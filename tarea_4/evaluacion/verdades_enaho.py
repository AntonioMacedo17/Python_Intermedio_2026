"""Respuestas esperadas de la ENAHO 2024 para la evaluación y su verificación independiente.

    uv run evaluacion/verdades_enaho.py       # desde tarea_4/; escribe evaluacion/verdades_enaho.csv

La RESPUESTA ESPERADA es siempre la cifra de referencia del curso (no un cálculo nuestro):
  - nacional, extrema, urbana y rural: Data-Science-Python, sessions/16-skills-enaho/README.md, sección «Validación»;
  - departamentos: referencias/pobreza_departamento_2024.csv (copia idéntica de la de la sesión 16).

Además, este script recalcula cada cifra desde los microdatos con código escrito aparte (NO importa los scripts
de .claude/skills/), por los dos métodos:
  - personas: módulo 02 (residentes habituales) unido a sumaria, ponderado con facpob07;
  - hogares: sumaria, ponderado con factor07 × mieperho.
Con eso documenta cuánto se aleja el método de personas (el que usan nuestras skills) de la referencia, que es
lo que justifica la tolerancia de departamentos y subgrupos (ver README_evaluacion.md).
"""
import csv
import sys
import zipfile
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
RAIZ = AQUI.parent
DATOS = RAIZ / "datos"
REF_DEPTOS = RAIZ / "referencias" / "pobreza_departamento_2024.csv"
FUENTE_README = ("Data-Science-Python, sessions/16-skills-enaho/README.md, sección «Validación» "
                 "(https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho)")
FUENTE_CSV = "referencias/pobreza_departamento_2024.csv (sesión 16 del curso)"

# Referencias del README de la sesión 16 (sección «Validación»), transcritas tal cual con su fuente.
REF_README = {"nacional": 27.6, "extrema_nacional": 5.5, "urbana": 24.8, "rural": 39.3}
DEPTOS = {"cusco": "08", "cajamarca": "06"}


def leer(zip_nombre, sufijo, columnas):
    with zipfile.ZipFile(DATOS / zip_nombre) as z:
        nombre = next(n for n in z.namelist() if n.lower().endswith(sufijo))
        with z.open(nombre) as f:
            df = pd.read_stata(f, convert_categoricals=False)
    df.columns = [c.lower() for c in df.columns]
    return df[columnas].copy()


def ponderada(df, var, peso):
    return 100 * (df[var] * df[peso]).sum() / df[peso].sum()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    llaves = ["conglome", "vivienda", "hogar"]
    hog = leer("966-Modulo34.zip", "sumaria-2024.dta",
               llaves + ["ubigeo", "estrato", "pobreza", "factor07", "mieperho"])
    per = leer("966-Modulo02.zip", "enaho01-2024-200.dta", llaves + ["codperso", "p204", "p205", "p206", "facpob07"])
    for df in (hog, per):
        for c in llaves:
            df[c] = df[c].astype(str).str.strip()
    hog["ubigeo"] = hog["ubigeo"].astype(str).str.strip().str.zfill(6)
    assert not hog.duplicated(llaves).any(), "sumaria con llaves duplicadas"

    residente = ((per.p204 == 1) & (per.p205 == 2)) | ((per.p204 == 2) & (per.p206 == 1))
    per = per[residente].merge(hog, on=llaves, how="left", validate="m:1", indicator=True)
    assert (per["_merge"] == "both").all(), "hay personas sin hogar en sumaria"
    print(f"Residentes habituales: {len(per):,} · hogares en sumaria: {len(hog):,}")

    for df in (hog, per):
        df["pobre"] = (df.pobreza <= 2).astype(float)
        df["extremo"] = (df.pobreza == 1).astype(float)
        df["urbano"] = df.estrato <= 5
        df["ccdd"] = df.ubigeo.str[:2]
    hog["peso_personas"] = hog.factor07 * hog.mieperho

    def dos_metodos(filtro_p, filtro_h, var="pobre"):
        return (ponderada(per[filtro_p(per)], var, "facpob07"),
                ponderada(hog[filtro_h(hog)], var, "peso_personas"))

    todos = lambda d: d.index == d.index  # noqa: E731
    calc = {
        "nacional": dos_metodos(todos, todos),
        "extrema_nacional": dos_metodos(todos, todos, "extremo"),
        "urbana": dos_metodos(lambda d: d.urbano, lambda d: d.urbano),
        "rural": dos_metodos(lambda d: ~d.urbano, lambda d: ~d.urbano),
    }
    ref = pd.read_csv(REF_DEPTOS, dtype={"ccdd": str})
    ref["ccdd"] = ref.ccdd.str.zfill(2)
    difs = []
    for _, r in ref.iterrows():
        p, h = dos_metodos(lambda d, c=r.ccdd: d.ccdd == c, lambda d, c=r.ccdd: d.ccdd == c)
        difs.append({"ccdd": r.ccdd, "departamento": r.departamento, "referencia": r.pobreza_pct,
                     "facpob07": p, "sumaria": h, "dif_facpob07": p - r.pobreza_pct, "dif_sumaria": h - r.pobreza_pct})
    difs = pd.DataFrame(difs)

    filas = []
    for clave, (p, h) in calc.items():
        filas.append({"clave": clave, "valor": REF_README[clave], "fuente": FUENTE_README,
                      "calc_facpob07": round(p, 3), "calc_sumaria": round(h, 3),
                      "dif_facpob07_pp": round(p - REF_README[clave], 3),
                      "dif_sumaria_pp": round(h - REF_README[clave], 3)})
    for clave, ccdd in DEPTOS.items():
        d = difs.set_index("ccdd").loc[ccdd]
        filas.append({"clave": clave, "valor": d.referencia, "fuente": FUENTE_CSV,
                      "calc_facpob07": round(d.facpob07, 3), "calc_sumaria": round(d.sumaria, 3),
                      "dif_facpob07_pp": round(d.dif_facpob07, 3), "dif_sumaria_pp": round(d.dif_sumaria, 3)})

    salida = AQUI / "verdades_enaho.csv"
    with salida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    print("\nclave              referencia  personas(facpob07)  hogares(factor07×mieperho)")
    for f_ in filas:
        print(f"{f_['clave']:18s} {f_['valor']:>9}   {f_['calc_facpob07']:>8.3f} ({f_['dif_facpob07_pp']:+.3f})"
              f"      {f_['calc_sumaria']:>8.3f} ({f_['dif_sumaria_pp']:+.3f})")
    i, j = difs.dif_facpob07.abs().idxmax(), difs.dif_sumaria.abs().idxmax()
    print(f"\n25 departamentos · máx |facpob07 − referencia| = {abs(difs.dif_facpob07[i]):.3f} pp "
          f"({difs.departamento[i]}); máx |sumaria − referencia| = {abs(difs.dif_sumaria[j]):.3f} pp "
          f"({difs.departamento[j]})")
    sub = [abs(calc[k][0] - REF_README[k]) for k in ("urbana", "rural")]
    print(f"Subgrupos urbana/rural · |facpob07 − referencia| = {sub[0]:.3f} / {sub[1]:.3f} pp")
    print(f"Escrito {salida}")


if __name__ == "__main__":
    main()
