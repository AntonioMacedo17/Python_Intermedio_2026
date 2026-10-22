"""Paso 3: ¿A quién afecta? Personas a <= 5 km de los incendios activos (WorldPop 2020, 1 km).

- Buffer de 5 km alrededor de cada foco de los incendios activos (UTM 18S), unidos (sin doble conteo).
- Se suman los píxeles WorldPop cuyo centro cae dentro del área.
- Filtro urbano: un "incendio" cuya mayoría de focos cae en píxeles con >= 500 hab/km² se trata como
  fuente urbana/industrial (siderúrgica, fábricas, quema de basura), no como incendio de vegetación.
- Totales por departamento y distrito (límites INEI, juaneladio/peru-geojson) y por incendio.
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask, rasterize
from rasterio.windows import Window, from_bounds

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "datos" / "raw"
PROC = BASE / "datos" / "procesados"
CRS_M = "EPSG:32718"
RADIO_M = 5000
DENS_URBANA = 500  # hab/km² en el píxel del foco
INCENDIO_ELEGIDO = 190

focos = pd.read_csv(PROC / "focos_peru.csv")
inc = pd.read_csv(PROC / "incendios_peru.csv", index_col="incendio_id")

with rasterio.open(RAW / "per_ppp_2020_1km_Aggregated.tif") as src:
    pop = src.read(1).astype("float64")
    pop[(pop == src.nodata) | (pop < 0)] = 0
    T, shape = src.transform, src.shape
    focos["dens_pixel"] = [v[0] for v in src.sample(zip(focos.longitude, focos.latitude))]
focos["dens_pixel"] = focos.dens_pixel.clip(lower=0)

inc["pct_focos_urbanos"] = (focos.assign(u=focos.dens_pixel >= DENS_URBANA)
                            .groupby("incendio_id").u.mean() * 100).round(1)
inc["urbano"] = inc.pct_focos_urbanos > 50
activos = inc[inc.activo].copy()

dist = gpd.read_file(RAW / "peru_distrital_simple.geojson")
ids = rasterize([(g, i + 1) for i, g in enumerate(dist.geometry)], out_shape=shape, transform=T, fill=0)
pop_dist = np.bincount(ids.ravel(), weights=pop.ravel(), minlength=len(dist) + 1)[1:]


def buffers(ids_inc, radio=RADIO_M):
    f = focos[focos.incendio_id.isin(ids_inc)]
    g = gpd.GeoDataFrame(f, geometry=gpd.points_from_xy(f.longitude, f.latitude), crs="EPSG:4326").to_crs(CRS_M)
    g["geometry"] = g.buffer(radio)
    return g.dissolve("incendio_id")[["geometry"]]


def exposicion(ids_inc, radio=RADIO_M):
    """Personas a <= radio de la unión de buffers + desglose por distrito."""
    b = buffers(ids_inc, radio)
    union = gpd.GeoSeries([b.union_all()], crs=CRS_M)
    dentro = ~geometry_mask(union.to_crs("EPSG:4326"), out_shape=shape, transform=T)
    pe = np.where(dentro, pop, 0)
    exp = np.bincount(ids.ravel(), weights=pe.ravel(), minlength=len(dist) + 1)[1:]
    return b, float(pe.sum()), float(union.area.iat[0] / 1e6), exp


def pob_por_incendio(b):
    """Personas en el buffer de cada incendio por separado (se solapan: NO sumables)."""
    out = {}
    for iid, geom in b.to_crs("EPSG:4326").geometry.items():
        w = from_bounds(*geom.bounds, transform=T).round_offsets().round_lengths()
        w = Window(w.col_off - 2, w.row_off - 2, w.width + 4, w.height + 4)  # margen: no cortar píxeles del borde
        w = w.intersection(Window(0, 0, shape[1], shape[0]))
        sub = pop[w.row_off:w.row_off + w.height, w.col_off:w.col_off + w.width]
        m = ~geometry_mask([geom], out_shape=sub.shape, transform=rasterio.windows.transform(w, T))
        out[iid] = float(sub[m].sum())
    return pd.Series(out)


veg = activos.index[~activos.urbano]
b_todos, p_todos, a_todos, exp_todos = exposicion(activos.index)
b_veg, p_veg, a_veg, exp_veg = exposicion(veg)
activos["pob_5km"] = pob_por_incendio(b_todos).round()

por_dist = dist[["IDDIST", "NOMBDIST", "NOMBPROV", "NOMBDEP"]].assign(
    poblacion=pop_dist.round(), expuesta_5km=exp_veg.round(), expuesta_5km_sin_filtro=exp_todos.round())
por_dist["pct_expuesta"] = (100 * por_dist.expuesta_5km / por_dist.poblacion.replace(0, np.nan)).round(1)
cuenta = activos[~activos.urbano].iddist.astype(str).str.zfill(6).value_counts()
por_dist["incendios_activos"] = por_dist.IDDIST.map(cuenta).fillna(0).astype(int)
por_dist = por_dist.sort_values("expuesta_5km", ascending=False)
por_dep = por_dist.groupby("NOMBDEP")[["poblacion", "expuesta_5km", "expuesta_5km_sin_filtro", "incendios_activos"]].sum()
por_dep["pct_expuesta"] = (100 * por_dep.expuesta_5km / por_dep.poblacion).round(2)
por_dep = por_dep.sort_values("expuesta_5km", ascending=False)

av = activos[~activos.urbano]
el = activos.loc[INCENDIO_ELEGIDO]

# Gradiente: ¿cuánta gente queda expuesta según qué tan estricta es la definición de "incendio"?
definiciones = {
    "Todos los focos activos": activos.index,
    "Sin fuentes urbanas/industriales": veg,
    "Y con >= 3 focos": av.index[av.n_focos >= 3],
    "Y con huella > 100 ha": av.index[av.huella_ha > 100],
}
gradiente = pd.DataFrame([
    {"definicion": k, "incendios": len(v), "personas_5km": round(exposicion(v)[1])}
    for k, v in definiciones.items()
])
print(gradiente.to_string(index=False))
gradiente.to_csv(PROC / "gradiente_definiciones.csv", index=False)

# Anillos de distancia (acumulados): personas a <= 1, 3 y 5 km. A 1 km la resolución de WorldPop (1 km) es gruesa.
anillos = pd.DataFrame([
    {"radio_km": r, "personas_veg": round(exposicion(veg, r * 1000)[1]),
     "personas_mazamari": round(exposicion([INCENDIO_ELEGIDO], r * 1000)[1])}
    for r in (1, 3, 5)
])
print(anillos.to_string(index=False))
anillos.to_csv(PROC / "anillos_distancia.csv", index=False)
resumen = {
    "corte_focos_utc": f"{focos.fecha_hora.min()} a {focos.fecha_hora.max()}",
    "incendios_activos_total": int(len(activos)),
    "incendios_activos_urbanos_excluidos": int(activos.urbano.sum()),
    "incendios_activos_vegetacion": int(len(av)),
    "poblacion_peru_worldpop2020": round(float(pop.sum())),
    "personas_5km_sin_filtro": round(p_todos),
    "personas_5km_vegetacion": round(p_veg),
    "pct_peru_vegetacion": round(100 * p_veg / float(pop.sum()), 2),
    "area_5km_vegetacion_km2": round(a_veg),
    "distritos_con_expuestos": int((por_dist.expuesta_5km > 0).sum()),
    "incendios_veg_con_mas_de_1000_personas": int((av.pob_5km > 1000).sum()),
    "mediana_personas_por_incendio_veg": round(float(av.pob_5km.median())),
    "elegido": {"incendio_id": INCENDIO_ELEGIDO, "distrito": el.distrito, "provincia": el.provincia,
                "departamento": el.departamento, "personas_5km": round(float(el.pob_5km)),
                "n_focos": int(el.n_focos)},
}
print(json.dumps(resumen, indent=2, ensure_ascii=False))
print(activos[activos.urbano][["n_focos", "pob_5km", "pct_focos_urbanos", "distrito", "departamento"]].to_string())
print(por_dep.head(10).to_string())
print(por_dist.head(15).to_string(index=False))
print(av.sort_values("pob_5km", ascending=False).head(15)[
    ["n_focos", "huella_ha", "pob_5km", "departamento", "provincia", "distrito"]].to_string())

(PROC / "resumen_poblacion.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
por_dist.to_csv(PROC / "poblacion_5km_por_distrito.csv", index=False)
por_dep.to_csv(PROC / "poblacion_5km_por_departamento.csv")
activos.to_csv(PROC / "incendios_activos_poblacion.csv")
focos[focos.incendio_id.isin(activos.index)].to_csv(PROC / "focos_incendios_activos.csv", index=False)
b_todos.to_crs("EPSG:4326").join(activos[["urbano", "pob_5km", "distrito", "departamento", "n_focos"]]) \
    .reset_index().to_file(PROC / "buffers_5km_incendios_activos.geojson", driver="GeoJSON")
