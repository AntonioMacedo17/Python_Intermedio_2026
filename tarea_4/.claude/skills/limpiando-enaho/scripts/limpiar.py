"""Limpia la ENAHO 2024 (INEI): módulos 34 (sumaria) y 02 (miembros) -> base de personas con pobreza.

Se corre desde tarea_4/:
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py

Pipeline (siempre en este orden): leer -> normalizar columnas -> filtrar residentes habituales ->
unir personas con sumaria (m:1) -> construir variables -> validar -> guardar.

Salidas (en salidas/):
    personas_2024.parquet  base de residentes habituales (microdato: no se versiona)
    validacion.txt         PASA/FALLA de cada chequeo
    indicadores.csv        pobreza ponderada con facpob07 por nivel, con n y población expandida

Si falla una validación esencial, el script termina con sys.exit(1) y NO escribe la base.
Nunca se ajustan resultados para que coincidan con la referencia.
"""
import argparse
import sys
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

ZIP_SUMARIA = "966-Modulo34.zip"     # 966 = código de la ENAHO 2024 en el portal del INEI
ZIP_PERSONAS = "966-Modulo02.zip"
DTA_SUMARIA = "sumaria-2024.dta"     # el zip trae también sumaria-2024-12g.dta (12 grupos de gasto); no se usa
DTA_PERSONAS = "enaho01-2024-200.dta"
LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_TEXTO = LLAVES_HOGAR + ["codperso", "ubigeo"]

# Valores publicados en sessions/16-skills-enaho/README.md (calculados con los archivos 2024 del INEI)
REF_POBREZA = 27.6        # % nacional
TOL_POBREZA = 0.1         # puntos porcentuales
REF_RESIDENTES = 108_664
REF_URBANA, REF_RURAL = 24.8, 39.3        # informativas
REF_EXTREMA, REF_LIMA_MET = 5.5, 28.2     # informativas

DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
    "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
GRUPOS_EDAD = [(0, 14, "0-14"), (15, 29, "15-29"), (30, 44, "30-44"), (45, 59, "45-59"), (60, 200, "60 y más")]


def normalizar_columnas(df):
    """Minúsculas y sin tildes. La columna del año llega como 'aÑo' (o mal decodificada): se llama 'anio'."""
    nuevas = {}
    for c in df.columns:
        limpio = unicodedata.normalize("NFKD", str(c).lower()).encode("ascii", "ignore").decode()
        if limpio in ("ano", "ao"):   # 'aÑo' -> 'ano'; 'a�o' (mal decodificada) -> 'ao'
            limpio = "anio"
        nuevas[c] = limpio
    return df.rename(columns=nuevas)


def leer_dta(ruta_zip, nombre_dta):
    """Lee un .dta directo desde el zip, sin convertir etiquetas, con las llaves como texto."""
    with zipfile.ZipFile(ruta_zip) as zf:
        candidatos = [n for n in zf.namelist() if n.lower().endswith("/" + nombre_dta.lower()) or n.lower() == nombre_dta.lower()]
        if len(candidatos) != 1:
            sys.exit(f"ERROR: no encontré un único {nombre_dta} dentro de {ruta_zip}: {candidatos}")
        with zf.open(candidatos[0]) as f:
            df = pd.read_stata(f, convert_categoricals=False)
    df = normalizar_columnas(df)
    for c in LLAVES_TEXTO:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df


def media_ponderada(valores, pesos):
    return float((valores * pesos).sum() / pesos.sum())


def grupo_edad(edad):
    cortes = [g[0] for g in GRUPOS_EDAD] + [GRUPOS_EDAD[-1][1] + 1]
    etiquetas = [g[2] for g in GRUPOS_EDAD]
    return pd.cut(edad, bins=cortes, right=False, labels=etiquetas)


def main():
    sys.stdout.reconfigure(encoding="utf-8")   # la consola de Windows usa cp1252 por defecto
    ap =argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", default="datos", help="carpeta con los zip del INEI (por defecto datos/)")
    ap.add_argument("--salidas", default="salidas", help="carpeta de salida (por defecto salidas/)")
    args = ap.parse_args()
    datos, salidas = Path(args.datos), Path(args.salidas)

    for z in (ZIP_SUMARIA, ZIP_PERSONAS):
        if not (datos / z).exists():
            sys.exit(f"ERROR: falta {datos / z}. Bájalo del INEI: "
                     f"https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{z}")

    # 1-2. Leer y normalizar
    sumaria = leer_dta(datos / ZIP_SUMARIA, DTA_SUMARIA)
    personas_todas = leer_dta(datos / ZIP_PERSONAS, DTA_PERSONAS)
    n_mod02 = len(personas_todas)

    # 3. Residentes habituales: miembros no ausentes 30+ días, o no miembros presentes 30+ días
    filtro = ((personas_todas.p204 == 1) & (personas_todas.p205 == 2)) | \
             ((personas_todas.p204 == 2) & (personas_todas.p206 == 1))
    personas = personas_todas.loc[filtro].copy()

    # 4. Unir personas (m) con sumaria (1). De sumaria solo se traen variables de hogar que personas no tiene.
    cols_sumaria = LLAVES_HOGAR + ["pobreza", "factor07", "mieperho", "ubigeo", "estrato"]
    suma = sumaria[cols_sumaria].rename(columns={"ubigeo": "ubigeo_sumaria", "estrato": "estrato_sumaria"})
    base = personas.merge(suma, on=LLAVES_HOGAR, how="left", validate="m:1", indicator=True)

    # 5. Construir
    base["departamento"] = base["ubigeo"].str[:2]
    base["departamento_nombre"] = base["departamento"].map(DEPARTAMENTOS)
    base["area"] = base["estrato"].le(5).map({True: "urbana", False: "rural"})
    base["pobre"] = (base["pobreza"] <= 2).astype("int8")
    base["pobre_extremo"] = (base["pobreza"] == 1).astype("int8")
    base["sexo"] = base["p207"].map({1: "hombre", 2: "mujer"})
    base["edad"] = base["p208a"].astype("Int16")
    base["grupo_edad"] = grupo_edad(base["p208a"])

    # 6. Validar
    chequeos = []   # (esencial, nombre, ok, detalle)

    def chequear(esencial, nombre, ok, detalle):
        chequeos.append((esencial, nombre, bool(ok), detalle))

    w = base["facpob07"]
    pob_personas = 100 * media_ponderada(base["pobre"], w)
    w_hog = sumaria["factor07"] * sumaria["mieperho"]
    pob_sumaria = 100 * media_ponderada((sumaria["pobreza"] <= 2).astype(int), w_hog)

    chequear(True, f"Pobreza nacional (personas, facpob07) = {REF_POBREZA} % ± {TOL_POBREZA} pp",
             abs(pob_personas - REF_POBREZA) <= TOL_POBREZA, f"{pob_personas:.2f} %")
    chequear(True, f"Pobreza nacional (sumaria, factor07 × mieperho) = {REF_POBREZA} % ± {TOL_POBREZA} pp",
             abs(pob_sumaria - REF_POBREZA) <= TOL_POBREZA, f"{pob_sumaria:.2f} %")
    chequear(True, f"Residentes habituales = {REF_RESIDENTES:,}", len(personas) == REF_RESIDENTES,
             f"{len(personas):,} de {n_mod02:,} filas del módulo 02")
    deps = sorted(base["departamento"].unique())
    chequear(True, "25 códigos de departamento (01 a 25)", deps == sorted(DEPARTAMENTOS),
             f"{len(deps)} códigos: {deps[0]} a {deps[-1]}")
    chequear(True, "Llaves únicas en sumaria (conglome, vivienda, hogar)",
             not sumaria.duplicated(LLAVES_HOGAR).any(), f"{len(sumaria):,} hogares, "
             f"{sumaria.duplicated(LLAVES_HOGAR).sum()} duplicados")
    llaves_p = LLAVES_HOGAR + ["codperso"]
    chequear(True, "Llaves únicas en personas (+ codperso)", not personas_todas.duplicated(llaves_p).any(),
             f"{personas_todas.duplicated(llaves_p).sum()} duplicados en {n_mod02:,} filas")
    sin_par = int((base["_merge"] != "both").sum())
    chequear(True, "La unión no pierde ni duplica filas",
             len(base) == len(personas) and sin_par == 0,
             f"{len(personas):,} personas antes, {len(base):,} después, {sin_par} sin hogar en sumaria")
    chequear(True, "ubigeo y estrato coinciden entre módulo 02 y sumaria",
             (base["ubigeo"] == base["ubigeo_sumaria"]).all() and (base["estrato"] == base["estrato_sumaria"]).all(),
             f"{int((base['ubigeo'] != base['ubigeo_sumaria']).sum())} ubigeo distintos, "
             f"{int((base['estrato'] != base['estrato_sumaria']).sum())} estrato distintos")
    for col, df in (("facpob07", base), ("factor07", sumaria)):
        chequear(True, f"{col} sin nulos y positivo", df[col].notna().all() and (df[col] > 0).all(),
                 f"{int(df[col].isna().sum())} nulos, {int((df[col] <= 0).sum())} no positivos")
    chequear(True, "pobreza sin nulos tras la unión", base["pobreza"].notna().all(),
             f"{int(base['pobreza'].isna().sum())} nulos")
    chequear(True, "sexo y edad sin nulos en residentes", base["sexo"].notna().all() and base["edad"].notna().all(),
             f"{int(base['sexo'].isna().sum())} sexo nulos, {int(base['edad'].isna().sum())} edad nulos")

    # Informativas (no detienen el script). Se calculan con los dos métodos y se muestran ambos:
    # las referencias del README de la sesión 16 coinciden con el método de la sumaria.
    s_pobre, s_ext = (sumaria["pobreza"] <= 2).astype(int), (sumaria["pobreza"] == 1).astype(int)
    informativas = (
        ("Pobreza urbana (estrato <= 5)", base["estrato"] <= 5, sumaria["estrato"] <= 5, "pobre", s_pobre, REF_URBANA),
        ("Pobreza rural (estrato >= 6)", base["estrato"] > 5, sumaria["estrato"] > 5, "pobre", s_pobre, REF_RURAL),
        ("Pobreza extrema nacional", base["estrato"] > 0, sumaria["estrato"] > 0, "pobre_extremo", s_ext, REF_EXTREMA),
        ("Pobreza Lima Metropolitana (dominio == 8)", base["dominio"] == 8, sumaria["dominio"] == 8, "pobre", s_pobre,
         REF_LIMA_MET),
    )
    for nombre, m_p, m_s, var, s_var, ref in informativas:
        v_p = 100 * media_ponderada(base.loc[m_p, var], w[m_p])
        v_s = 100 * media_ponderada(s_var[m_s], w_hog[m_s])
        chequear(False, f"{nombre} ~ {ref} % · personas, facpob07", abs(v_p - ref) <= TOL_POBREZA, f"{v_p:.2f} %")
        chequear(False, f"{nombre} ~ {ref} % · sumaria, factor07 × mieperho", abs(v_s - ref) <= TOL_POBREZA,
                 f"{v_s:.2f} %")

    # Por qué difieren las dos pobrezas nacionales (cifras calculadas aquí, no escritas a mano)
    res_por_hogar = base.groupby(LLAVES_HOGAR).size().rename("residentes")
    comp = sumaria.set_index(LLAVES_HOGAR)[["mieperho"]].join(res_por_hogar, how="left").fillna({"residentes": 0})
    hogares_distintos = int((comp["mieperho"] != comp["residentes"]).sum())
    trab_hogar = int((base["p203"] == 8).sum())
    pensionistas = int((base["p203"] == 9).sum())
    pob_exp_personas = float(w.sum())
    pob_exp_sumaria = float(w_hog.sum())

    esenciales_ok = all(ok for e, _, ok, _ in chequeos if e)
    salidas.mkdir(parents=True, exist_ok=True)
    lineas = [
        "VALIDACIÓN · ENAHO 2024 (INEI), módulos 34 (sumaria) y 02 (miembros)",
        f"Generado: {datetime.now():%Y-%m-%d %H:%M} con .claude/skills/limpiando-enaho/scripts/limpiar.py",
        f"Archivos: {datos / ZIP_SUMARIA}::{DTA_SUMARIA} y {datos / ZIP_PERSONAS}::{DTA_PERSONAS}",
        "Referencias: Data-Science-Python, sessions/16-skills-enaho/README.md (sección Validación)",
        "",
        "ESENCIALES (si alguna falla, no se escribe la base)",
    ]
    lineas += [f"  [{'PASA ' if ok else 'FALLA'}] {n}: {d}" for e, n, ok, d in chequeos if e]
    lineas += ["", "INFORMATIVAS (tolerancia ± 0.1 pp; no detienen el script)"]
    lineas += [f"  [{'PASA ' if ok else 'FALLA'}] {n}: {d}" for e, n, ok, d in chequeos if not e]
    lineas += [
        "",
        "POR QUÉ DIFIEREN LAS DOS POBREZAS NACIONALES",
        f"  Personas con facpob07: {pob_personas:.2f} %  ·  Sumaria con factor07 × mieperho: {pob_sumaria:.2f} %",
        "  1. Distintos factores: en la sumaria cada hogar pesa factor07 × mieperho (todos sus miembros con el",
        "     mismo peso); en personas cada residente habitual pesa su propio facpob07. Son factores distintos",
        "     del INEI y no son proporcionales entre sí. Población expandida:",
        f"     {pob_exp_personas:,.0f} (personas, Σ facpob07) vs {pob_exp_sumaria:,.0f} (sumaria, Σ factor07 × mieperho).",
        "  2. Distinto conteo de personas por hogar: en "
        f"{hogares_distintos:,} de {len(sumaria):,} hogares mieperho no coincide con el",
        "     número de residentes habituales del módulo 02. Entre los residentes hay "
        f"{trab_hogar} trabajadores del hogar",
        f"     (p203 == 8) y {pensionistas} pensionistas (p203 == 9), así que eso explica solo una parte; el resto",
        "     depende de la definición de mieperho del INEI (ver Diccionario2024.pdf del módulo 34), no verificada aquí.",
        "  La cifra oficial del INEI (27.6 %) redondea ambas. Las referencias informativas (urbana, rural, extrema,",
        "  Lima Met.) coinciden con el método de la sumaria; esta base usa siempre facpob07 a nivel de personas.",
        "",
        f"RESULTADO: {'TODAS LAS VALIDACIONES ESENCIALES PASAN' if esenciales_ok else 'FALLA AL MENOS UNA VALIDACIÓN ESENCIAL'}",
    ]
    if esenciales_ok:
        lineas.append(f"Base escrita: {salidas / 'personas_2024.parquet'} ({len(base):,} filas)")
    else:
        lineas.append("La base NO se escribió.")
    (salidas / "validacion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))

    if not esenciales_ok:
        sys.exit(1)

    # 7. Guardar la base y los indicadores
    columnas = ["anio", "mes", "conglome", "vivienda", "hogar", "codperso", "ubigeo", "departamento",
                "departamento_nombre", "dominio", "estrato", "area", "sexo", "edad", "grupo_edad",
                "pobreza", "pobre", "pobre_extremo", "facpob07", "factor07", "mieperho"]
    base[columnas].to_parquet(salidas / "personas_2024.parquet", index=False)

    filas = []

    def agregar(nivel, categoria, g, codigo=""):
        filas.append({
            "nivel": nivel, "codigo": codigo, "categoria": categoria,
            "pobreza_pct": round(100 * media_ponderada(g["pobre"], g["facpob07"]), 2),
            "pobreza_extrema_pct": round(100 * media_ponderada(g["pobre_extremo"], g["facpob07"]), 2),
            "n_obs": len(g), "poblacion_expandida": round(float(g["facpob07"].sum())),
        })

    agregar("nacional", "Perú", base)
    for nivel, col in (("area", "area"), ("sexo", "sexo"), ("grupo_edad", "grupo_edad")):
        for cat, g in base.groupby(col, observed=True):
            agregar(nivel, str(cat), g)
    for cod, g in base.groupby("departamento"):
        agregar("departamento", DEPARTAMENTOS[cod], g, codigo=cod)
    ind = pd.DataFrame(filas)
    ind.to_csv(salidas / "indicadores.csv", index=False, encoding="utf-8")
    print(f"\nIndicadores: {salidas / 'indicadores.csv'} ({len(ind)} filas). "
          "Fuente: INEI, ENAHO 2024 (módulos 34 y 02), ponderado con facpob07.")


if __name__ == "__main__":
    main()
