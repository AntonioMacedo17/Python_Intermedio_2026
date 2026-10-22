"""Paso 1: focos VIIRS (NASA FIRMS, últimos 7 días) -> incendios en Perú.

Regla: focos a <= 1 km y <= 48 h pertenecen al mismo incendio (componentes conexas).
Incendio activo: tiene al menos un foco en las últimas 48 h del archivo.
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.neighbors import BallTree

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "datos" / "raw"
OUT = BASE / "datos" / "procesados"
OUT.mkdir(parents=True, exist_ok=True)

R_TIERRA_KM = 6371.0
DIST_KM = 1.0
HORAS = 48
VOLCANES = {  # lat, lon de volcanes activos (generan "focos" que no son incendios)
    "Sabancaya": (-15.787, -71.857),
    "Ubinas": (-16.355, -70.903),
    "Misti": (-16.294, -71.409),
}

# 1. Unir los tres sensores VIIRS
archivos = {
    "S-NPP": "SUOMI_VIIRS_C2_South_America_7d.csv",
    "NOAA-20": "J1_VIIRS_C2_South_America_7d.csv",
    "NOAA-21": "J2_VIIRS_C2_South_America_7d.csv",
}
df = pd.concat(
    [pd.read_csv(RAW / f).assign(sensor=s) for s, f in archivos.items()], ignore_index=True
)
df["fecha_hora"] = pd.to_datetime(
    df["acq_date"] + " " + df["acq_time"].astype(str).str.zfill(4), format="%Y-%m-%d %H%M"
)
print(f"Focos Sudamérica: {len(df):,}")

# 2. Solo Perú (puntos dentro de los distritos INEI)
dist = gpd.read_file(RAW / "peru_distrital_simple.geojson")[
    ["IDDIST", "NOMBDIST", "NOMBPROV", "NOMBDEP", "geometry"]
]
peru_bbox = dist.total_bounds
df = df[df.longitude.between(peru_bbox[0], peru_bbox[2]) & df.latitude.between(peru_bbox[1], peru_bbox[3])]
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
gdf = gpd.sjoin(gdf, dist, predicate="within", how="inner").drop(columns="index_right")
n_peru = len(gdf)

# 3. Limpieza: confianza baja y volcanes
gdf = gdf[gdf.confidence != "l"] if "l" in set(gdf.confidence) else gdf[gdf.confidence != "low"]
n_conf = len(gdf)
lat_r, lon_r = np.radians(gdf.latitude.values), np.radians(gdf.longitude.values)
lejos = np.ones(len(gdf), bool)
for lat, lon in VOLCANES.values():
    d = R_TIERRA_KM * 2 * np.arcsin(np.sqrt(
        np.sin((lat_r - np.radians(lat)) / 2) ** 2
        + np.cos(lat_r) * np.cos(np.radians(lat)) * np.sin((lon_r - np.radians(lon)) / 2) ** 2
    ))
    lejos &= d > 5
gdf = gdf[lejos].reset_index(drop=True)
print(f"Perú: {n_peru:,} focos | sin confianza baja: {n_conf:,} | sin volcanes: {len(gdf):,}")

# 4. Agrupar: vecinos a <= 1 km (BallTree haversine) y <= 48 h
coords = np.radians(gdf[["latitude", "longitude"]].values)
tree = BallTree(coords, metric="haversine")
vecinos = tree.query_radius(coords, r=DIST_KM / R_TIERRA_KM)
t = gdf.fecha_hora.values.astype("datetime64[h]").astype(np.int64)
filas, cols = [], []
for i, js in enumerate(vecinos):
    js = js[np.abs(t[js] - t[i]) <= HORAS]
    filas.extend([i] * len(js))
    cols.extend(js)
grafo = coo_matrix((np.ones(len(filas)), (filas, cols)), shape=(len(gdf), len(gdf)))
_, gdf["incendio_id"] = connected_components(grafo, directed=False)

# 5. Resumen por incendio (huella = envolvente de píxeles VIIRS de 375 m)
t_max = gdf.fecha_hora.max()
gdf_m = gdf.to_crs("EPSG:32718")  # UTM 18S, metros
gdf_m["geometry"] = gdf_m.buffer(187.5, cap_style=3)
huellas = gdf_m.dissolve("incendio_id").convex_hull
agg = gdf.groupby("incendio_id").agg(
    n_focos=("latitude", "size"),
    lat=("latitude", "mean"),
    lon=("longitude", "mean"),
    inicio=("fecha_hora", "min"),
    ultimo=("fecha_hora", "max"),
    frp_total=("frp", "sum"),
    departamento=("NOMBDEP", lambda s: s.mode().iat[0]),
    provincia=("NOMBPROV", lambda s: s.mode().iat[0]),
    distrito=("NOMBDIST", lambda s: s.mode().iat[0]),
    iddist=("IDDIST", lambda s: s.mode().iat[0]),
)
agg["huella_ha"] = (huellas.area / 1e4).reindex(agg.index).round(1)

# Fuentes fijas (antorchas de gas, industrias): arden >= 6 días distintos sin moverse (< 0,002° ~ 220 m)
disp = gdf.assign(dia=gdf.fecha_hora.dt.date).groupby("incendio_id").agg(
    dias=("dia", "nunique"), sd_lat=("latitude", "std"), sd_lon=("longitude", "std"))
fijas = disp[(disp.dias >= 6) & (disp.sd_lat < 0.002) & (disp.sd_lon < 0.002)].index
print("Fuentes fijas excluidas:", agg.loc[fijas, ["n_focos", "distrito", "departamento"]].to_dict("index"))
agg = agg.drop(fijas)
gdf = gdf[~gdf.incendio_id.isin(fijas)]
agg["activo"] = agg.ultimo >= t_max - pd.Timedelta(hours=HORAS)
agg = agg.sort_values("n_focos", ascending=False)

print(f"Corte de datos: {gdf.fecha_hora.min()} a {t_max} UTC")
print(f"Incendios: {len(agg):,} | activos (foco en últimas 48 h): {agg.activo.sum():,}")
print(f"Activos con huella > 100 ha: {(agg.activo & (agg.huella_ha > 100)).sum()}")
print(agg.head(20)[["n_focos", "huella_ha", "frp_total", "activo", "departamento", "provincia", "distrito", "inicio", "ultimo"]].to_string())

gdf.drop(columns="geometry").to_csv(OUT / "focos_peru.csv", index=False)
agg.to_csv(OUT / "incendios_peru.csv")
