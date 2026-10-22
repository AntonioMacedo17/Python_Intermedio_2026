"""Paso 0: descarga de datos abiertos (sin clave): focos VIIRS 7 días, límites INEI, WorldPop 2020."""
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[1] / "datos" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

FIRMS = "https://firms.modaps.eosdis.nasa.gov/data/active_fire"
GEOJSON = "https://raw.githubusercontent.com/juaneladio/peru-geojson/master"
URLS = {
    "SUOMI_VIIRS_C2_South_America_7d.csv": f"{FIRMS}/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_America_7d.csv",
    "J1_VIIRS_C2_South_America_7d.csv": f"{FIRMS}/noaa-20-viirs-c2/csv/J1_VIIRS_C2_South_America_7d.csv",
    "J2_VIIRS_C2_South_America_7d.csv": f"{FIRMS}/noaa-21-viirs-c2/csv/J2_VIIRS_C2_South_America_7d.csv",
    "peru_departamental_simple.geojson": f"{GEOJSON}/peru_departamental_simple.geojson",
    "peru_distrital_simple.geojson": f"{GEOJSON}/peru_distrital_simple.geojson",
    "per_ppp_2020_1km_Aggregated.tif": "https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/PER/per_ppp_2020_1km_Aggregated.tif",
}

for nombre, url in URLS.items():
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    (RAW / nombre).write_bytes(r.content)
    print(f"{nombre}: {len(r.content) / 1e6:.1f} MB")
