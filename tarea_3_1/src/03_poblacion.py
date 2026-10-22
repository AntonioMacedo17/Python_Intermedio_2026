"""Paso 3: ¿A quién afecta? Personas a <= 5 km de los incendios activos (WorldPop 2020, 1 km).

- Buffer de 5 km alrededor de cada foco de los incendios activos (UTM 18S), unidos (sin doble conteo).
- Se suman los píxeles WorldPop cuyo centro cae dentro del área.
- Totales por departamento y distrito (límites INEI, juaneladio/peru-geojson) y por incendio.
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask, rasterize
from rasterio.windows import from_bounds

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "datos" / "raw"
PROC = BASE / "datos" / "procesados"
CRS_M = "EPSG:32718"
RADIO_M = 5000

focos = pd.read_csv(PROC / "focos_peru.csv")
inc = pd.read_csv(PROC / "incendios_peru.csv", index_col="incendio_id")
activos = inc[inc.activo]
fa = focos[focos.incendio_id.isin(activos.index)]
gfa = gpd.GeoDataFrame(fa, geometry=gpd.points_from_xy(fa.longitude, fa.latitude), crs="EPSG:4326").to_crs(CRS_M)
gfa["geometry"] = gfa.buffer(RADIO_M)
buf_inc = gfa.dissolve("incendio_id")[["geometry"]]                     # un buffer por incendio
area_total = gpd.GeoSeries([buf_inc.union_all()], crs=CRS_M).to_crs("EPSG:4326")

with rasterio.open(RAW / "per_ppp_2020_1km_Aggregated.tif") as src:
    pop = src.read(1).astype("float64")
    pop[pop == src.nodata] = 0
    pop[pop < 0] = 0
    T, shape = src.transform, src.shape

dentro = ~geometry_mask(area_total, out_shape=shape, transform=T)      # centro del píxel dentro
pop_expuesta = np.where(dentro, pop, 0)

# Por distrito / departamento
dist = gpd.read_file(RAW / "peru_distrital_simple.geojson")
ids = rasterize([(g, i + 1) for i, g in enumerate(dist.geometry)], out_shape=shape, transform=T, fill=0)
tot = np.bincount(ids.ravel(), weights=pop.ravel(), minlength=len(dist) + 1)[1:]
exp = np.bincount(ids.ravel(), weights=pop_expuesta.ravel(), minlength=len(dist) + 1)[1:]
por_dist = dist[["IDDIST", "NOMBDIST", "NOMBPROV", "NOMBDEP"]].assign(
    poblacion=tot.round(), expuesta_5km=exp.round()
)
por_dist["pct_expuesta"] = (100 * por_dist.expuesta_5km / por_dist.poblacion.replace(0, np.nan)).round(1)
n_inc = activos.groupby("iddist").size()
por_dist["incendios_activos"] = por_dist.IDDIST.astype(str).str.zfill(6).map(
    n_inc.rename(lambda x: str(x).zfill(6))).fillna(0).astype(int)
por_dist = por_dist.sort_values("expuesta_5km", ascending=False)
por_dep = por_dist.groupby("NOMBDEP")[["poblacion", "expuesta_5km", "incendios_activos"]].sum()
por_dep["pct_expuesta"] = (100 * por_dep.expuesta_5km / por_dep.poblacion).round(2)
por_dep = por_dep.sort_values("expuesta_5km", ascending=False)

# Por incendio (cada buffer por separado: NO son sumables, se solapan)
buf4326 = buf_inc.to_crs("EPSG:4326")
pop_inc = {}
for iid, geom in buf4326.geometry.items():
    w = from_bounds(*geom.bounds, transform=T).round_offsets().round_lengths()
    w = w.intersection(rasterio.windows.Window(0, 0, shape[1], shape[0]))
    sub = pop[w.row_off:w.row_off + w.height, w.col_off:w.col_off + w.width]
    m = ~geometry_mask([geom], out_shape=sub.shape, transform=rasterio.windows.transform(w, T))
    pop_inc[iid] = float(sub[m].sum())
activos = activos.assign(pob_5km=pd.Series(pop_inc).round()).sort_values("pob_5km", ascending=False)

resumen = {
    "incendios_activos": int(len(activos)),
    "focos_de_incendios_activos": int(len(fa)),
    "poblacion_peru_worldpop": round(float(pop.sum())),
    "personas_a_5km": round(float(pop_expuesta.sum())),
    "pct_peru": round(100 * float(pop_expuesta.sum() / pop.sum()), 2),
    "area_5km_km2": round(float(buf_inc.union_all().area / 1e6)),
    "distritos_con_expuestos": int((por_dist.expuesta_5km > 0).sum()),
    "incendios_con_mas_de_1000_personas": int((activos.pob_5km > 1000).sum()),
    "incendios_sin_personas": int((activos.pob_5km < 1).sum()),
}
print(json.dumps(resumen, indent=2, ensure_ascii=False))
print(por_dep.head(10).to_string())
print(por_dist.head(15).to_string(index=False))
print(activos.head(15)[["n_focos", "huella_ha", "pob_5km", "departamento", "provincia", "distrito"]].to_string())

(PROC / "resumen_poblacion.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
por_dist.to_csv(PROC / "poblacion_5km_por_distrito.csv", index=False)
por_dep.to_csv(PROC / "poblacion_5km_por_departamento.csv")
activos.to_csv(PROC / "incendios_activos_poblacion.csv")
buf4326.reset_index().to_file(PROC / "buffers_5km_incendios_activos.geojson", driver="GeoJSON")
