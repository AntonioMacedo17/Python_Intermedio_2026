"""Tabla de verificación y brechas del informe final (Tarea 4, Parte 3). Sin cuentas a mano.

    uv run informes/scripts/verificacion.py        # desde tarea_4/, después de grafico_bcrp.py y de las skills

Lee salidas guardadas (salidas/bcrp_contexto.json, salidas/indicadores.csv, salidas/comparacion_mapa_referencia.csv)
y las referencias del curso / del BCRP, y escribe:
  - salidas/verificacion.csv  (afirmación, valor calculado, referencia, fuente, diferencia)
  - salidas/brechas_enaho.csv (brechas de pobreza calculadas desde indicadores.csv)

Los valores de referencia de la web del BCRP son los que muestran las páginas BCRPData leídas el 2026-11-08
(lectura automática): Antonio debe confirmarlos a mano (columna "verificado por Antonio" del informe).
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
S = RAIZ / "salidas"
WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series"
CURSO = "https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho"

bcrp = json.loads((S / "bcrp_contexto.json").read_text(encoding="utf-8"))
ind = pd.read_csv(S / "indicadores.csv", dtype={"codigo": str})
comp = pd.read_csv(S / "comparacion_mapa_referencia.csv", dtype={"ccdd": str})
ref_dep = pd.read_csv(RAIZ / "referencias" / "pobreza_departamento_2024.csv", dtype={"ccdd": str})

ri = bcrp["resumen_inflacion"]
pbi_a = {x["periodo"]: x["valor"] for x in bcrp["serie_pbi_anual"]["datos"]}


def fila(cat, valor, pct):
    return float(ind.query("nivel == @cat and categoria == @valor")[pct].iloc[0])


nac = fila("nacional", "Perú", "pobreza_pct")
urb, rur = fila("area", "urbana", "pobreza_pct"), fila("area", "rural", "pobreza_pct")
caj = comp.query("ccdd == '06'").iloc[0]

filas = [
    ("BCRP", "Inflación de Lima a 12 meses, dic-2024 (PN01273PM)", ri["ultimo"]["valor"], 1.97,
     f"Página BCRPData {WEB}/mensuales/resultados/PN01273PM/html, fila Dic.2024 (2 decimales)"),
    ("BCRP", "Pico de la inflación de Lima 2020-2024, jun-2022 (PN01273PM)", ri["maximo"]["valor"], 8.81,
     f"Página BCRPData {WEB}/mensuales/resultados/PN01273PM/html, fila Jun.2022 (2 decimales)"),
    ("BCRP", "Crecimiento del PBI 2024, var. % anual (PM04863AA)", pbi_a["2024"], 3.5,
     f"Página BCRPData {WEB}/anuales/resultados/PM04863AA/html, columna 2024 (1 decimal)"),
    ("BCRP", "Caída del PBI 2020, var. % anual (PM04863AA)", pbi_a["2020"], -10.9,
     f"Página BCRPData {WEB}/anuales/resultados/PM04863AA/html, columna 2020 (1 decimal)"),
    ("ENAHO", "Pobreza monetaria nacional 2024 (facpob07)", nac, 27.6,
     f"Referencia del curso, sesión 16, sección Validación ({CURSO}); cifra oficial INEI 27.6 %"),
    ("ENAHO", "Pobreza rural 2024 (facpob07)", rur, 39.3, f"Referencia del curso, sesión 16 ({CURSO})"),
    ("ENAHO", "Pobreza urbana 2024 (facpob07)", urb, 24.8, f"Referencia del curso, sesión 16 ({CURSO})"),
    ("ENAHO", "Pobreza de Cajamarca 2024, la más alta (facpob07)", float(caj.calculado_facpob07_pct),
     float(caj.referencia_pct), "referencias/pobreza_departamento_2024.csv (sesión 16 del curso)"),
]
ver = pd.DataFrame(filas, columns=["fuente_dato", "afirmacion", "valor_calculado", "valor_referencia", "verificacion"])
ver["diferencia"] = (ver.valor_calculado - ver.valor_referencia).round(3)
ver.to_csv(S / "verificacion.csv", index=False, encoding="utf-8")

dep = ind.query("nivel == 'departamento'")
edad = ind.query("nivel == 'grupo_edad'").set_index("categoria")
brechas = pd.DataFrame([
    ("rural menos urbana (pp)", round(rur - urb, 2)),
    ("rural / urbana (veces)", round(rur / urb, 2)),
    ("0-14 años menos nacional (pp)", round(edad.loc["0-14", "pobreza_pct"] - nac, 2)),
    ("0-14 años menos 45-59 años (pp)", round(edad.loc["0-14", "pobreza_pct"] - edad.loc["45-59", "pobreza_pct"], 2)),
    ("departamento máximo menos mínimo (pp)", round(dep.pobreza_pct.max() - dep.pobreza_pct.min(), 2)),
    ("departamentos sobre el promedio nacional (n de 25)", int((dep.pobreza_pct > nac).sum())),
    ("pobreza extrema rural menos urbana (pp)",
     round(fila("area", "rural", "pobreza_extrema_pct") - fila("area", "urbana", "pobreza_extrema_pct"), 2)),
    ("población rural en pobreza (personas expandidas)",
     int(round(rur / 100 * ind.query("categoria == 'rural'").poblacion_expandida.iloc[0]))),
    ("población urbana en pobreza (personas expandidas)",
     int(round(urb / 100 * ind.query("categoria == 'urbana'").poblacion_expandida.iloc[0]))),
], columns=["brecha", "valor"])
brechas.to_csv(S / "brechas_enaho.csv", index=False, encoding="utf-8")

pd.set_option("display.width", 200, "display.max_colwidth", 70)
print(ver.drop(columns="verificacion"))
print(brechas)
print("Escritos: salidas/verificacion.csv y salidas/brechas_enaho.csv")
