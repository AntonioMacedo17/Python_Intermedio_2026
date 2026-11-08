"""Arma evaluacion/preguntas.csv: une el texto de cada pregunta con su respuesta esperada.

    uv run evaluacion/verdades_bcrp.py && uv run evaluacion/verdades_enaho.py && uv run evaluacion/armar_preguntas.py

Ninguna respuesta esperada se escribe aquí: se leen de verdades_bcrp.csv y verdades_enaho.csv. Aquí solo van el
texto de la pregunta, la unidad y la tolerancia (justificada en README_evaluacion.md, fijada antes de evaluar).
"""
import csv
import sys
from pathlib import Path

AQUI = Path(__file__).parent

# Tolerancias (ver README_evaluacion.md): fijadas antes de la primera corrida.
TOL_TASA_BCRP = 0.05     # tasas y variaciones % del BCRP: redondeo
TOL_TC = 0.005           # tipo de cambio S/ por US$: redondeo a 2 decimales
TOL_MILLONES = 1         # montos en millones de US$ (la serie no tiene decimales)
TOL_POBREZA_NAC = 0.1    # pobreza nacional: ±0.1 pp, como pide el Issue
TOL_POBREZA_SUB = 0.6    # departamentos y subgrupos: redondeo (0.05) + máx. |facpob07 − referencia| (0.518)

ENAHO = "según la ENAHO 2024 del INEI"
P = [
    # id, tipo, pregunta, clave verdad, unidad, tolerancia, [clave verdad 2, unidad 2, tolerancia 2]
    ("B1", "bcrp", "¿Cuál era la tasa de referencia de la política monetaria del BCRP en diciembre de 2024? "
     "Responde en porcentaje.", "tasa_ref_2024_12", "%", TOL_TASA_BCRP),
    ("B2", "bcrp", "¿Cuál fue la inflación de Lima Metropolitana (IPC, variación porcentual en 12 meses) en "
     "setiembre de 2026, según el BCRP? Responde en porcentaje.", "ipc12m_2026_09", "%", TOL_TASA_BCRP),
    ("B3", "bcrp", "¿Cuál fue el tipo de cambio bancario promedio del periodo (soles por dólar) en setiembre de "
     "2026, según el BCRP?", "tc_bancario_2026_09", "S/ por US$", TOL_TC),
    ("B4", "bcrp", "¿A cuánto ascendían las reservas internacionales netas del Perú al cierre de diciembre de 2025, "
     "según el BCRP? Responde en millones de US$.", "rin_usd_2025_12", "millones de US$", TOL_MILLONES),
    ("E1", "enaho", f"¿Qué porcentaje de la población del Perú estaba en situación de pobreza monetaria en 2024, "
     f"{ENAHO}?", "nacional", "% de personas", TOL_POBREZA_NAC),
    ("E2", "enaho", f"¿Qué porcentaje de la población del área rural del Perú estaba en situación de pobreza "
     f"monetaria en 2024, {ENAHO}?", "rural", "% de personas", TOL_POBREZA_SUB),
    ("E3", "enaho", f"¿Qué porcentaje de la población del departamento de Cusco estaba en situación de pobreza "
     f"monetaria en 2024, {ENAHO}?", "cusco", "% de personas", TOL_POBREZA_SUB),
    ("E4", "enaho", f"¿Qué porcentaje de la población del Perú estaba en situación de pobreza monetaria extrema en "
     f"2024, {ENAHO}?", "extrema_nacional", "% de personas", TOL_POBREZA_NAC),
    ("C1", "combinada", "Para un informe necesito dos cifras: (a) el porcentaje de la población del departamento de "
     f"Cajamarca en situación de pobreza monetaria en 2024, {ENAHO}, y (b) el crecimiento del PBI real del Perú en "
     "2024 (variación porcentual anual), según el BCRP. Pon (a) en «valor» y (b) en «valor_2». En «interpretacion» "
     "explica en 2 o 3 oraciones qué se puede y qué no se puede concluir al poner ambas cifras juntas.",
     "cajamarca", "% de personas", TOL_POBREZA_SUB, "pbi_var_2024", "%", TOL_TASA_BCRP),
    ("C2", "combinada", "Para un informe necesito dos cifras: (a) el porcentaje de la población del área urbana del "
     f"Perú en situación de pobreza monetaria en 2024, {ENAHO}, y (b) la inflación de Lima Metropolitana (IPC, "
     "variación porcentual en 12 meses) en diciembre de 2024, según el BCRP. Pon (a) en «valor» y (b) en "
     "«valor_2». En «interpretacion» explica en 2 o 3 oraciones qué se puede y qué no se puede concluir al poner "
     "ambas cifras juntas.", "urbana", "% de personas", TOL_POBREZA_SUB, "ipc12m_2024_12", "%", TOL_TASA_BCRP),
]


def leer(nombre):
    with (AQUI / nombre).open(encoding="utf-8") as f:
        return {r["clave"]: r for r in csv.DictReader(f)}


def describir(v):
    """Fuente y forma de verificar una respuesta esperada."""
    if "url_api" in v:
        return (f"BCRP, serie {v['codigo']} ({v['nombre_serie']}), {v['periodo']}; API: {v['url_api']} ; "
                f"web: {v['url_web']}",
                f"verdades_bcrp.py: llamada directa a la API con httpx (sin el MCP); valor de la API {v['valor_api']} "
                f"redondeado a {v['decimales_api']} decimales (los que declara la API); consultado {v['consultado']}")
    return (v["fuente"],
            f"Referencia del curso. Recalculada en verdades_enaho.py sin las skills: personas/facpob07 = "
            f"{v['calc_facpob07']} ({float(v['dif_facpob07_pp']):+.3f} pp), sumaria/factor07×mieperho = "
            f"{v['calc_sumaria']} ({float(v['dif_sumaria_pp']):+.3f} pp)")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    verdades = {**leer("verdades_bcrp.csv"), **leer("verdades_enaho.csv")}
    filas = []
    for id_, tipo, pregunta, clave, unidad, tol, *segunda in P:
        v = verdades[clave]
        fuente, como = describir(v)
        fila = {"id": id_, "tipo": tipo, "pregunta": pregunta, "verdad": float(v["valor"]), "unidad": unidad,
                "tolerancia": tol, "verdad_2": "", "unidad_2": "", "tolerancia_2": "",
                "fuente_verdad": fuente, "como_se_verifico": como}
        if segunda:
            clave2, unidad2, tol2 = segunda
            v2 = verdades[clave2]
            f2, c2 = describir(v2)
            fila.update(verdad_2=float(v2["valor"]), unidad_2=unidad2, tolerancia_2=tol2,
                        fuente_verdad=f"(a) {fuente} || (b) {f2}", como_se_verifico=f"(a) {como} || (b) {c2}")
        filas.append(fila)
    with (AQUI / "preguntas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    for r in filas:
        extra = f"  verdad_2={r['verdad_2']} ±{r['tolerancia_2']}" if r["verdad_2"] != "" else ""
        print(f"{r['id']}  verdad={r['verdad']} ±{r['tolerancia']}{extra}")
    print(f"Escrito {AQUI / 'preguntas.csv'} ({len(filas)} preguntas)")


if __name__ == "__main__":
    main()
