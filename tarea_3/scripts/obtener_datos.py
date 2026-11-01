"""Descarga las series originales de la Tarea 3 (estructura tributaria, desigualdad y gasto social).

Uso:  python scripts/obtener_datos.py      (desde la carpeta tarea_3/)

Fuentes (todas públicas, consultadas el 01/11/2026):
- OCDE, Global Revenue Statistics (incluye la base OCDE/CEPAL/CIAT/BID de América Latina y el Caribe)
- OCDE, Social Expenditure Database (SOCX), gasto social público total en % del PIB (incluye al Perú)
- CEPALSTAT, gasto público social por funciones (indicador 3127) y gasto social metodología SOCX (4407)
- Banco Mundial, WDI: Gini, ingreso tributario, PIB per cápita PPA y población
- WID.world (World Inequality Database): solo los archivos de los países analizados, leídos desde el
  ZIP oficial con descargas parciales (el ZIP completo pesa ~887 MB). Esos CSV no se versionan.
"""
from pathlib import Path

import requests
from remotezip import RemoteZip

RAIZ = Path(__file__).resolve().parents[1]
ORIG = RAIZ / "datos" / "originales"

OCDE = "https://sdmx.oecd.org/public/rest/data/"
CSV = {"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"}

# Códigos de la clasificación OCDE de impuestos que se usan en el análisis
CODIGOS_IMPUESTOS = "_T+T_1000+T_1100+T_1200+T_1300+T_2000+T_3000+T_4000+T_5000+T_5110+T_5111+T_5120+T_6000"

WB_INDICADORES = ["SI.POV.GINI", "GC.TAX.TOTL.GD.ZS", "NY.GDP.PCAP.PP.KD", "SP.POP.TOTL"]
CEPAL_INDICADORES = [3127, 4407]
WID_PAISES = ["PE", "AR", "BO", "BR", "CL", "CO", "EC", "MX", "PY", "UY", "DK", "FI", "NO", "SE", "IS"]


def bajar(url, destino, headers=None):
    destino.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=headers, timeout=300)
    r.raise_for_status()
    destino.write_bytes(r.content)
    print(f"{destino.relative_to(RAIZ)}  ({len(r.content) / 1e6:.1f} MB)")


def main():
    bajar(
        OCDE + "OECD.CTP.TPS,DSD_REV_COMP_GLOBAL@DF_RSGLOBAL,2.1/"
        f".TAX_REV.S13.{CODIGOS_IMPUESTOS}._T.PT_B1GQ+PT_OTR_REV_CAT.A"
        "?startPeriod=2000&dimensionAtObservation=AllDimensions",
        ORIG / "ocde_global_revenue_statistics.csv", CSV,
    )
    bajar(
        OCDE + "OECD.ELS.SPD,DSD_SOCX_AGG@DF_SOCX_AGG,1.0/.A.SOCX.PT_B1GQ.ES10._T._T."
        "?startPeriod=2000&dimensionAtObservation=AllDimensions",
        ORIG / "ocde_socx" / "socx_publico_total_pib.csv", CSV,
    )
    for ind in WB_INDICADORES:
        bajar(
            f"https://api.worldbank.org/v2/country/all/indicator/{ind}?format=json&per_page=20000&date=2000:2024",
            ORIG / "banco_mundial" / f"{ind}.json",
        )
    for ind in CEPAL_INDICADORES:
        bajar(
            f"https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{ind}/data?lang=es&format=json&in=1",
            ORIG / "cepalstat" / f"ind_{ind}.json",
        )
    destino = ORIG / "wid"
    destino.mkdir(parents=True, exist_ok=True)
    with RemoteZip("https://wid.world/bulk_download/wid_all_data.zip") as z:
        z.extract("WID_countries.csv", destino)
        for p in WID_PAISES:
            for nombre in (f"WID_data_{p}.csv", f"WID_metadata_{p}.csv"):
                z.extract(nombre, destino)
                print(f"datos/originales/wid/{nombre}")


if __name__ == "__main__":
    main()
