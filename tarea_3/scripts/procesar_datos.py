"""Limpia las series originales y arma un panel país-año en datos/procesados/panel.csv.

Uso:  python scripts/procesar_datos.py      (desde tarea_3/, después de obtener_datos.py)

Decisiones de método (ver README):
- Estructura tributaria: gobierno general (S13), clasificación OCDE. Se usan dos unidades: % del PIB y
  % de la recaudación total (PT_OTR_REV_CAT del código _T).
- "Impuestos directos" = renta (1000) + propiedad (4000). "Indirectos" = bienes y servicios (5000).
  Las contribuciones a la seguridad social (2000) se muestran aparte porque su incidencia es discutida.
- Desigualdad: Gini de encuestas (Banco Mundial) y participaciones de WID.world (ingreso nacional antes
  de impuestos y riqueza neta personal, adultos con reparto equitativo dentro de la pareja, código 992j).
- Gasto social: SOCX de la OCDE (gasto social público, % del PIB), que incluye al Perú con la misma
  metodología que a los países OCDE.
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ORIG = RAIZ / "datos" / "originales"
PROC = RAIZ / "datos" / "procesados"

NORDICOS = ["DNK", "FIN", "NOR", "SWE", "ISL"]
AGREGADOS = {"A9": "Promedio ALC", "OECD_REP": "Promedio OCDE"}

IMPUESTOS = {
    "_T": "total", "T_1000": "renta", "T_1100": "renta_personas", "T_1200": "renta_empresas",
    "T_1300": "renta_no_asignable", "T_2000": "contrib_seg_social", "T_3000": "nomina",
    "T_4000": "propiedad", "T_5000": "bienes_servicios", "T_5111": "iva", "T_5120": "selectivos_aduanas",
    "T_6000": "otros",
}

# ISO3 -> nombre en español, solo para los países que se muestran
NOMBRES = {
    "PER": "Perú", "ARG": "Argentina", "BOL": "Bolivia", "BRA": "Brasil", "CHL": "Chile", "COL": "Colombia",
    "CRI": "Costa Rica", "CUB": "Cuba", "DOM": "Rep. Dominicana", "ECU": "Ecuador", "GTM": "Guatemala",
    "HND": "Honduras", "JAM": "Jamaica", "MEX": "México", "NIC": "Nicaragua", "PAN": "Panamá",
    "PRY": "Paraguay", "SLV": "El Salvador", "URY": "Uruguay", "VEN": "Venezuela", "BHS": "Bahamas",
    "BLZ": "Belice", "BRB": "Barbados", "GUY": "Guyana", "TTO": "Trinidad y Tobago", "SUR": "Surinam",
    "ATG": "Antigua y Barbuda", "GRD": "Granada", "LCA": "Santa Lucía",
    "DNK": "Dinamarca", "FIN": "Finlandia", "NOR": "Noruega", "SWE": "Suecia", "ISL": "Islandia",
    "AUS": "Australia", "AUT": "Austria", "BEL": "Bélgica", "CAN": "Canadá", "CHE": "Suiza",
    "CZE": "Chequia", "DEU": "Alemania", "ESP": "España", "EST": "Estonia", "FRA": "Francia",
    "GBR": "Reino Unido", "GRC": "Grecia", "HUN": "Hungría", "IRL": "Irlanda", "ISR": "Israel",
    "ITA": "Italia", "JPN": "Japón", "KOR": "Corea", "LTU": "Lituania", "LUX": "Luxemburgo",
    "LVA": "Letonia", "NLD": "Países Bajos", "NZL": "Nueva Zelanda", "POL": "Polonia", "PRT": "Portugal",
    "SVK": "Eslovaquia", "SVN": "Eslovenia", "TUR": "Turquía", "USA": "Estados Unidos",
}
LAC = ["PER", "ARG", "BOL", "BRA", "CHL", "COL", "CRI", "CUB", "DOM", "ECU", "GTM", "HND", "JAM", "MEX",
       "NIC", "PAN", "PRY", "SLV", "URY", "VEN", "BHS", "BLZ", "BRB", "GUY", "TTO", "SUR", "ATG", "GRD", "LCA"]
WID_ISO = {"PE": "PER", "AR": "ARG", "BO": "BOL", "BR": "BRA", "CL": "CHL", "CO": "COL", "EC": "ECU",
           "MX": "MEX", "PY": "PRY", "UY": "URY", "DK": "DNK", "FI": "FIN", "NO": "NOR", "SE": "SWE", "IS": "ISL"}


def grupo(iso):
    if iso == "PER":
        return "Perú"
    if iso in AGREGADOS:
        return "Promedio"
    if iso in NORDICOS:
        return "Nórdicos"
    if iso in LAC:
        return "América Latina y el Caribe"
    return "OCDE (otros)"


def impuestos():
    d = pd.read_csv(ORIG / "ocde_global_revenue_statistics.csv")
    # Solo % del PIB: PT_OTR_REV_CAT es la participación dentro de la misma categoría, no en el total
    d = d[d.STANDARD_REVENUE.isin(IMPUESTOS) & (d.UNIT_MEASURE == "PT_B1GQ")
          & (d.REF_AREA.isin(NOMBRES) | d.REF_AREA.isin(AGREGADOS))]
    d = d.drop_duplicates(["REF_AREA", "STANDARD_REVENUE", "TIME_PERIOD"])
    d["var"] = d.STANDARD_REVENUE.map(IMPUESTOS) + "_pib"
    p = d.pivot_table(index=["REF_AREA", "TIME_PERIOD"], columns="var", values="OBS_VALUE").reset_index()
    p = p.rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "anio", "total_pib": "presion_tributaria"})
    # Participación en la recaudación total = (% del PIB del impuesto) / (presión tributaria) * 100
    for col in [c for c in p.columns if c.endswith("_pib")]:
        p[col.replace("_pib", "_pct")] = p[col] / p.presion_tributaria * 100
    return p


def banco_mundial():
    nombres = {"SI.POV.GINI": "gini_bm", "GC.TAX.TOTL.GD.ZS": "ingreso_trib_bm",
               "NY.GDP.PCAP.PP.KD": "pib_pc_ppa", "SP.POP.TOTL": "poblacion"}
    filas = []
    for cod, var in nombres.items():
        datos = json.loads((ORIG / "banco_mundial" / f"{cod}.json").read_text(encoding="utf-8"))[1]
        filas += [{"iso3": x["countryiso3code"], "anio": int(x["date"]), "var": var, "valor": x["value"]}
                  for x in datos if x["value"] is not None and x["countryiso3code"]]
    return pd.DataFrame(filas).pivot_table(index=["iso3", "anio"], columns="var", values="valor").reset_index()


def socx():
    d = pd.read_csv(ORIG / "ocde_socx" / "socx_publico_total_pib.csv").dropna(subset=["OBS_VALUE"])
    d = d.replace({"REF_AREA": {"OECD": "OECD_REP"}})
    return d.rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "anio", "OBS_VALUE": "gasto_social_pib"})[
        ["iso3", "anio", "gasto_social_pib"]]


def wid():
    series = {("sptinc992j", "p90p100"): "top10_ingreso", ("sptinc992j", "p99p100"): "top1_ingreso",
              ("sptinc992j", "p0p50"): "bottom50_ingreso", ("shweal992j", "p90p100"): "top10_riqueza",
              ("shweal992j", "p99p100"): "top1_riqueza"}
    partes = []
    for cod, iso in WID_ISO.items():
        d = pd.read_csv(ORIG / "wid" / f"WID_data_{cod}.csv", sep=";")
        d = d[(d.year >= 2000) & d.variable.isin({v for v, _ in series}) & d.percentile.isin({p for _, p in series})]
        d["var"] = [series.get((v, p)) for v, p in zip(d.variable, d.percentile)]
        d = d.dropna(subset=["var"]).assign(iso3=iso, value=lambda x: x.value * 100)
        partes.append(d.rename(columns={"year": "anio"})[["iso3", "anio", "var", "value"]])
    w = pd.concat(partes)
    return w.pivot_table(index=["iso3", "anio"], columns="var", values="value").reset_index()


def main():
    PROC.mkdir(parents=True, exist_ok=True)
    panel = impuestos()
    for extra in (banco_mundial(), socx(), wid()):
        panel = panel.merge(extra, on=["iso3", "anio"], how="left")
    panel = panel[(panel.anio >= 2000) & (panel.anio <= 2024)]
    panel.insert(1, "pais", panel.iso3.map(NOMBRES | AGREGADOS))
    panel.insert(2, "grupo", panel.iso3.map(grupo))

    # Indicadores derivados
    panel["directos_pct"] = panel.renta_pct + panel.propiedad_pct
    panel["indirectos_pct"] = panel.bienes_servicios_pct
    panel["ratio_directos_indirectos"] = panel.directos_pct / panel.indirectos_pct

    panel = panel.sort_values(["grupo", "pais", "anio"]).round(3)
    panel.to_csv(PROC / "panel.csv", index=False, encoding="utf-8")
    print(f"panel.csv: {panel.shape[0]} filas, {panel.iso3.nunique()} países/agregados, "
          f"{panel.anio.min()}-{panel.anio.max()}")
    return panel


if __name__ == "__main__":
    main()
