"""Paso 4: figuras estáticas para el README (paleta propia; escalas de datos estándar)."""
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap, LogNorm
from rasterio.windows import from_bounds

import estilo

estilo.aplicar()
BASE = Path(__file__).resolve().parents[1]
RAW, PROC, FIG = BASE / "datos" / "raw", BASE / "datos" / "procesados", BASE / "figuras"
ELEGIDO = 190

dist = gpd.read_file(RAW / "peru_distrital_simple.geojson")
dep = gpd.read_file(RAW / "peru_departamental_simple.geojson")
pdist = pd.read_csv(PROC / "poblacion_5km_por_distrito.csv", dtype={"IDDIST": str})
pdep = pd.read_csv(PROC / "poblacion_5km_por_departamento.csv")
act = pd.read_csv(PROC / "incendios_activos_poblacion.csv")
grad = pd.read_csv(PROC / "gradiente_definiciones.csv")
d = dist.merge(pdist[["IDDIST", "expuesta_5km"]], on="IDDIST")

# 1. Mapa nacional
fig, ax = plt.subplots(figsize=(9, 10.5))
d.plot(ax=ax, color="#ffffff", edgecolor="#e2ddd2", lw=0.2)
d[d.expuesta_5km > 0].plot(ax=ax, column="expuesta_5km", cmap="YlOrRd", norm=LogNorm(100, 2e5),
                           edgecolor="#bbb", lw=0.2, legend=True,
                           legend_kwds={"label": "Personas a ≤ 5 km de un incendio activo (escala log)",
                                        "shrink": 0.5, "orientation": "horizontal", "pad": 0.0, "fraction": 0.035})
dep.boundary.plot(ax=ax, color=estilo.CARBON, lw=0.5)
veg, urb = act[~act.urbano], act[act.urbano]
ax.scatter(veg.lon, veg.lat, s=4 + veg.n_focos.clip(upper=100), facecolor="none", edgecolor=estilo.VERDE,
           lw=0.8, label=f"Incendio activo de vegetación ({len(veg)})")
ax.scatter(urb.lon, urb.lat, s=40, marker="x", color=estilo.MORADO, label=f"Foco urbano/industrial excluido ({len(urb)})")
e = act[act.incendio_id == ELEGIDO].iloc[0]
ax.annotate("Mazamari\n(incendio elegido)", (e.lon, e.lat), xytext=(e.lon + 2.2, e.lat + 1.2), color=estilo.MORADO,
            fontweight="bold", arrowprops={"arrowstyle": "->", "color": estilo.MORADO})
ax.legend(loc="lower left", frameon=False)
ax.set_title("¿A quién afectan los incendios activos?\nPersonas a ≤ 5 km por distrito · focos VIIRS 14–21 oct 2026",
             loc="left")
ax.set_axis_off()
fig.text(0.02, 0.01, "Fuentes: NASA FIRMS VIIRS, WorldPop 2020 (1 km), INEI (juaneladio/peru-geojson)", fontsize=8)
fig.savefig(FIG / "mapa_poblacion_5km_peru.png", dpi=140, bbox_inches="tight")

# 2. Barras por departamento + gradiente de definiciones
fig, ax = plt.subplots(1, 2, figsize=(15, 6), constrained_layout=True)
top = pdep.head(12).iloc[::-1]
ax[0].barh(top.NOMBDEP.str.title(), top.expuesta_5km / 1e3, color=estilo.VERDE)
for y, (v, p) in enumerate(zip(top.expuesta_5km, top.pct_expuesta)):
    ax[0].text(v / 1e3 + 2, y, f"{v / 1e3:,.0f} mil · {p:.1f} %", va="center", fontsize=9)
ax[0].set_xlabel("Miles de personas a ≤ 5 km (sin focos urbanos)")
ax[0].set_title("Por departamento (y % de su población)", loc="left")
ax[0].spines[["top", "right"]].set_visible(False)
ax[1].bar(range(len(grad)), grad.personas_5km / 1e3, color=[estilo.MORADO] + [estilo.VERDE] * 3)
for i, r in grad.iterrows():
    ax[1].text(i, r.personas_5km / 1e3 + 15, f"{r.personas_5km / 1e3:,.0f} mil\n({r.incendios} incendios)",
               ha="center", fontsize=9)
ax[1].set_xticks(range(len(grad)), ["Todos los\nfocos activos", "Sin fuentes\nurbanas", "Y con\n≥ 3 focos", "Y con huella\n> 100 ha"], fontsize=9)
ax[1].set_ylabel("Miles de personas"); ax[1].set_ylim(0, 1350)
ax[1].set_title("El número depende de qué llamamos «incendio»", loc="left")
ax[1].spines[["top", "right"]].set_visible(False)
fig.savefig(FIG / "barras_departamento_y_definiciones.png", dpi=140)

# 3. Zoom al incendio elegido: población WorldPop + buffer 5 km + dNBR >= 0,27
buf = gpd.read_file(PROC / "buffers_5km_incendios_activos.geojson")
b = buf[buf.incendio_id == ELEGIDO]
x0, y0, x1, y1 = b.total_bounds
x0, y0, x1, y1 = x0 - 0.08, y0 - 0.08, x1 + 0.08, y1 + 0.08
with rasterio.open(RAW / "per_ppp_2020_1km_Aggregated.tif") as src:
    w = from_bounds(x0, y0, x1, y1, src.transform).round_offsets().round_lengths()
    sub = src.read(1, window=w)
    sub = np.where(sub < 0, np.nan, sub)
    ext = rasterio.windows.bounds(w, src.transform)
fig, ax = plt.subplots(figsize=(9, 8))
im = ax.imshow(sub, extent=[ext[0], ext[2], ext[1], ext[3]], cmap="YlOrRd", norm=LogNorm(1, 2000))
fig.colorbar(im, ax=ax, label="Personas por km² (WorldPop 2020)", shrink=0.75)
dist.boundary.plot(ax=ax, color="#888", lw=0.6)
b.boundary.plot(ax=ax, color=estilo.VERDE, lw=2.2)
with rasterio.open(PROC / f"dnbr_incendio_{ELEGIDO}.tif") as src:
    dn = src.read(1)
    q = gpd.GeoSeries([], crs=src.crs)
    from rasterio.features import shapes
    from shapely.geometry import shape
    geoms = [shape(g) for g, v in shapes((dn >= 0.27).astype("uint8"), transform=src.transform) if v == 1]
    q = gpd.GeoSeries(geoms, crs=src.crs).to_crs("EPSG:4326")
q.plot(ax=ax, color="#7f0000", edgecolor="#7f0000")
f = pd.read_csv(PROC / "focos_incendios_activos.csv")
f = f[f.incendio_id == ELEGIDO]
ax.scatter(f.longitude, f.latitude, s=8, color=estilo.CARBON, label="Focos VIIRS")
for _, r in dist.cx[x0:x1, y0:y1].iterrows():
    c = r.geometry.representative_point()
    if x0 < c.x < x1 and y0 < c.y < y1:
        ax.text(c.x, c.y, r.NOMBDIST.title(), fontsize=8, ha="center", color=estilo.CARBON)
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
el = act[act.incendio_id == ELEGIDO].iloc[0]
ax.set_title(f"Incendio de Mazamari: {el.pob_5km:,.0f} personas a ≤ 5 km\n"
             "verde = radio de 5 km · rojo oscuro = dNBR ≥ 0,27 · puntos = focos VIIRS", loc="left")
fig.savefig(FIG / "mapa_mazamari_poblacion.png", dpi=140, bbox_inches="tight")
print("Figuras listas")
