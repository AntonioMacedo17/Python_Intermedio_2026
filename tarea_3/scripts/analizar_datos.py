"""Calcula los indicadores y hallazgos, y exporta los datos que usa el dashboard (web/data/).

Uso:  python scripts/analizar_datos.py      (desde tarea_3/, después de procesar_datos.py)

Año de referencia: 2023, el último con datos para el Perú, el promedio ALC y el promedio OCDE en
Global Revenue Statistics. Para la desigualdad se usa el promedio 2019-2023 de cada país para no depender
de un solo año (las encuestas no son anuales en todos los países y WID extrapola los últimos años).
Las correlaciones son de Spearman (por rangos), entre países: describen asociación, no causalidad.
"""
import json
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "datos" / "procesados"
WEB = RAIZ / "web" / "data"

ANIO = 2023
VENTANA = (2019, 2023)
NORDICOS = ["DNK", "FIN", "NOR", "SWE", "ISL"]


def promedio_nordico(p, col, anio=ANIO):
    return p[(p.iso3.isin(NORDICOS)) & (p.anio == anio)][col].mean()


def valor(p, iso, col, anio=ANIO):
    s = p[(p.iso3 == iso) & (p.anio == anio)][col]
    return float(s.iloc[0]) if len(s) and pd.notna(s.iloc[0]) else None


def corte_transversal(p):
    """Un valor por país: impuestos y gasto en 2023 (o el último año disponible), desigualdad promedio 2019-2023."""
    v = p[p.anio.between(*VENTANA) & ~p.iso3.isin(["A9", "OECD_REP"])]
    desig = v.groupby("iso3")[["gini_bm", "top10_ingreso", "top1_ingreso", "top10_riqueza", "top1_riqueza",
                               "bottom50_ingreso"]].mean()
    fiscal_cols = ["presion_tributaria", "renta_personas_pib", "renta_personas_pct", "iva_pct",
                   "ratio_directos_indirectos", "propiedad_pib", "gasto_social_pib", "pib_pc_ppa"]
    ult = (v.sort_values("anio").groupby("iso3")[fiscal_cols].last())
    cx = ult.join(desig)
    meta = p.drop_duplicates("iso3").set_index("iso3")[["pais", "grupo"]]
    return meta.join(cx, how="inner").reset_index()


def main():
    p = pd.read_csv(PROC / "panel.csv")
    WEB.mkdir(parents=True, exist_ok=True)
    cx = corte_transversal(p)
    cx.to_csv(PROC / "corte_transversal_2019_2023.csv", index=False)

    res = {"anio_referencia": ANIO}
    for col in ["presion_tributaria", "iva_pct", "iva_pib", "renta_personas_pct", "renta_personas_pib",
                "renta_empresas_pct", "propiedad_pib", "bienes_servicios_pct", "directos_pct",
                "ratio_directos_indirectos", "gasto_social_pib"]:
        res[col] = {"PER": valor(p, "PER", col), "ALC": valor(p, "A9", col), "OCDE": valor(p, "OECD_REP", col),
                    "Nordicos": round(promedio_nordico(p, col), 3)}
    # Ranking del Perú en presión tributaria dentro de ALC (países con dato en 2023)
    alc = p[(p.grupo.isin(["Perú", "América Latina y el Caribe"])) & (p.anio == ANIO)].dropna(
        subset=["presion_tributaria"]).sort_values("presion_tributaria", ascending=False)
    res["ranking_presion_alc"] = {"puesto": int(alc.iso3.tolist().index("PER") + 1), "de": len(alc)}
    # IGV frente a renta de personas en el Perú
    res["igv_sobre_renta_personas_PER"] = round(valor(p, "PER", "iva_pib") / valor(p, "PER", "renta_personas_pib"), 2)
    # Evolución del Perú 2000 -> 2023
    res["evolucion_PER"] = {c: {"2000": valor(p, "PER", c, 2000), "2023": valor(p, "PER", c)}
                            for c in ["presion_tributaria", "iva_pct", "renta_personas_pct", "renta_empresas_pct"]}
    res["gasto_social_PER_serie"] = p[(p.iso3 == "PER")].dropna(subset=["gasto_social_pib"])[
        ["anio", "gasto_social_pib"]].values.tolist()
    # Desigualdad del Perú (promedio 2019-2023)
    per = cx[cx.iso3 == "PER"].iloc[0]
    res["desigualdad_PER_2019_2023"] = {c: round(float(per[c]), 2) for c in
                                        ["gini_bm", "top10_ingreso", "top1_ingreso", "top10_riqueza",
                                         "top1_riqueza", "bottom50_ingreso"]}
    res["desigualdad_nordicos_2019_2023"] = {
        c: round(float(cx[cx.iso3.isin(NORDICOS)][c].mean()), 2) for c in
        ["gini_bm", "top10_ingreso", "top1_ingreso", "top10_riqueza", "top1_riqueza", "bottom50_ingreso"]}

    # Asociaciones entre países (Spearman)
    corr = {}
    pares = [("presion_tributaria", "gini_bm"), ("renta_personas_pib", "gini_bm"),
             ("gasto_social_pib", "gini_bm"), ("ratio_directos_indirectos", "gini_bm"),
             ("renta_personas_pib", "top10_ingreso"), ("gasto_social_pib", "top10_ingreso")]
    for x, y in pares:
        d = cx[[x, y]].dropna()
        rho, pval = spearmanr(d[x], d[y])
        corr[f"{x}~{y}"] = {"rho": round(float(rho), 3), "p": round(float(pval), 4), "n": int(len(d))}
    res["correlaciones_spearman"] = corr

    (PROC / "indicadores.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    # Datos para la web
    cols_web = ["iso3", "pais", "grupo", "anio", "presion_tributaria", "renta_pib", "renta_personas_pib",
                "renta_empresas_pib", "contrib_seg_social_pib", "propiedad_pib", "bienes_servicios_pib", "iva_pib",
                "renta_pct", "renta_personas_pct", "renta_empresas_pct", "contrib_seg_social_pct", "propiedad_pct",
                "bienes_servicios_pct", "iva_pct", "otros_pct", "nomina_pct", "ratio_directos_indirectos",
                "gasto_social_pib", "gini_bm", "top10_ingreso", "top1_ingreso", "top10_riqueza", "top1_riqueza",
                "bottom50_ingreso", "pib_pc_ppa"]
    panel_web = p[cols_web].astype(object).where(p[cols_web].notna(), None)
    (WEB / "panel.json").write_text(json.dumps(panel_web.to_dict("records"), ensure_ascii=False), encoding="utf-8")
    cx_web = cx.astype(object).where(cx.notna(), None)
    (WEB / "corte_transversal.json").write_text(json.dumps(cx_web.to_dict("records"), ensure_ascii=False),
                                                encoding="utf-8")
    (WEB / "indicadores.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
