"""Paso 2: dNBR con Sentinel-2 L2A (Planetary Computer) para UN incendio.

Uso:
  python 02_dnbr.py listar <incendio_id> <desde> <hasta>   -> fechas y % de nubes en la zona
  python 02_dnbr.py calcular <incendio_id> <fecha_pre> <fecha_post>

NBR = (B8A - B12) / (B8A + B12), a 20 m. dNBR = NBR_pre - NBR_post.
Nubes: se descartan píxeles SCL 0,1,3,6,8,9,10,11 en cualquiera de las dos fechas.
Solo se cuentan píxeles a <= 1 km de los focos VIIRS del incendio.
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import planetary_computer
import pystac_client
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from odc.stac import load
from rasterio.features import rasterize

import estilo

estilo.aplicar()
BASE = Path(__file__).resolve().parents[1]
PROC = BASE / "datos" / "procesados"
FIG = BASE / "figuras"
FIG.mkdir(exist_ok=True)

SCL_MALOS = [0, 1, 3, 6, 8, 9, 10, 11]
SCL_NUBE = [3, 8, 9, 10]
CLASES = [  # USGS / Key & Benson
    ("No quemado", -np.inf, 0.10),
    ("Severidad baja", 0.10, 0.27),
    ("Moderada-baja", 0.27, 0.44),
    ("Moderada-alta", 0.44, 0.66),
    ("Alta", 0.66, np.inf),
]
PIXEL_HA = 20 * 20 / 1e4
CRS = "EPSG:32718"


def zona_incendio(inc_id):
    focos = pd.read_csv(PROC / "focos_peru.csv")
    f = focos[focos.incendio_id == inc_id]
    g = gpd.GeoDataFrame(f, geometry=gpd.points_from_xy(f.longitude, f.latitude), crs="EPSG:4326").to_crs(CRS)
    zona = g.buffer(1000).union_all()  # 1 km alrededor de cada foco
    return g, zona


def items_s2(zona, desde, hasta):
    cat = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace
    )
    bbox = gpd.GeoSeries([zona], crs=CRS).to_crs("EPSG:4326").total_bounds.tolist()
    items = cat.search(collections=["sentinel-2-l2a"], bbox=bbox, datetime=f"{desde}/{hasta}").item_collection()
    return items, bbox


def cargar(items, bbox, bandas):
    return load(items, bands=bandas, bbox=bbox, crs=CRS, resolution=20, groupby="solar_day", chunks={})


def mascara_zona(ds, zona):
    return rasterize([(zona, 1)], out_shape=(ds.sizes["y"], ds.sizes["x"]),
                     transform=ds.odc.geobox.transform, fill=0).astype(bool)


def listar(inc_id, desde, hasta):
    _, zona = zona_incendio(inc_id)
    items, bbox = items_s2(zona, desde, hasta)
    ds = cargar(items, bbox, ["SCL"]).compute()
    m = mascara_zona(ds, zona)
    filas = []
    for t in ds.time.values:
        scl = ds.SCL.sel(time=t).values[m]
        filas.append({
            "fecha": str(t)[:10],
            "pct_nube_zona": round(100 * np.isin(scl, SCL_NUBE).mean(), 1),
            "pct_sin_dato": round(100 * (scl == 0).mean(), 1),
            "pct_valido": round(100 * (~np.isin(scl, SCL_MALOS)).mean(), 1),
            "nube_escena": round(np.mean([i.properties["eo:cloud_cover"] for i in items
                                          if i.datetime.date().isoformat() == str(t)[:10]]), 1),
        })
    tabla = pd.DataFrame(filas)
    print(tabla.to_string(index=False))
    tabla.to_csv(PROC / f"escenas_s2_incendio_{inc_id}.csv", index=False)


def calcular(inc_id, f_pre, f_post):
    g, zona = zona_incendio(inc_id)
    resultado = {"incendio_id": inc_id}
    nbr, scl, rgb = {}, {}, {}
    for etiqueta, fecha in [("pre", f_pre), ("post", f_post)]:
        items, bbox = items_s2(zona, fecha, fecha)
        ds = cargar(items, bbox, ["B04", "B03", "B02", "B8A", "B12", "SCL"]).isel(time=0).compute()
        b8a, b12 = ds.B8A.astype("float32"), ds.B12.astype("float32")
        nbr[etiqueta] = ((b8a - b12) / (b8a + b12)).values
        scl[etiqueta] = ds.SCL.values
        rgb[etiqueta] = np.clip(np.dstack([ds.B12, ds.B8A, ds.B04]).astype("float32") / 4000, 0, 1)  # falso color
        resultado[f"fecha_{etiqueta}"] = fecha
        resultado[f"escenas_{etiqueta}"] = [i.id for i in items]
    geobox = ds.odc.geobox
    en_zona = mascara_zona(ds, zona)
    valido = ~np.isin(scl["pre"], SCL_MALOS) & ~np.isin(scl["post"], SCL_MALOS) & en_zona
    dnbr = np.where(valido, nbr["pre"] - nbr["post"], np.nan)

    resultado["pct_zona_enmascarada"] = round(100 * (1 - valido.sum() / en_zona.sum()), 1)
    resultado["zona_ha"] = round(en_zona.sum() * PIXEL_HA, 1)
    resultado["ha_por_clase"] = {n: round(float(((dnbr >= lo) & (dnbr < hi)).sum() * PIXEL_HA), 1)
                                 for n, lo, hi in CLASES}
    resultado["ha_quemadas_dnbr_027"] = round(float((dnbr >= 0.27).sum() * PIXEL_HA), 1)
    resultado["ha_quemadas_dnbr_010"] = round(float((dnbr >= 0.10).sum() * PIXEL_HA), 1)

    # Hectáreas quemadas (dNBR >= 0,27) por distrito
    dist = gpd.read_file(BASE / "datos" / "raw" / "peru_distrital_simple.geojson").to_crs(CRS)
    dist = dist[dist.intersects(zona)].reset_index(drop=True)
    ids = rasterize([(geom, i + 1) for i, geom in enumerate(dist.geometry)],
                    out_shape=dnbr.shape, transform=geobox.transform, fill=0)
    quemado = dnbr >= 0.27
    resultado["ha_quemadas_por_distrito"] = {
        f"{r.NOMBDIST} ({r.NOMBPROV}, {r.NOMBDEP})": round(float((quemado & (ids == i + 1)).sum() * PIXEL_HA), 1)
        for i, r in dist.iterrows()
    }
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    (PROC / f"dnbr_incendio_{inc_id}.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")

    # GeoTIFF del dNBR (para el dashboard)
    with rasterio.open(PROC / f"dnbr_incendio_{inc_id}.tif", "w", driver="GTiff", height=dnbr.shape[0],
                       width=dnbr.shape[1], count=1, dtype="float32", crs=CRS,
                       transform=geobox.transform, nodata=np.nan, compress="deflate") as dst:
        dst.write(dnbr.astype("float32"), 1)

    # Mapa: falso color antes / después / dNBR por clases
    ext = [geobox.extent.boundingbox.left, geobox.extent.boundingbox.right,
           geobox.extent.boundingbox.bottom, geobox.extent.boundingbox.top]
    fig, ax = plt.subplots(1, 3, figsize=(18, 6.5), constrained_layout=True)
    for a, et in zip(ax[:2], ["pre", "post"]):
        a.imshow(rgb[et], extent=ext)
        a.set_title(f"{'Antes' if et == 'pre' else 'Después'}: {resultado['fecha_' + et]} (B12-B8A-B4)")
    cmap = ListedColormap(["#d9d9d9", "#fee391", "#fe9929", "#d7301f", "#7f0000"])
    norm = BoundaryNorm([-1, 0.1, 0.27, 0.44, 0.66, 2], cmap.N)
    im = ax[2].imshow(dnbr, extent=ext, cmap=cmap, norm=norm)
    ax[2].set_title(f"dNBR · {resultado['ha_quemadas_dnbr_027']:,.0f} ha con dNBR ≥ 0,27")
    cb = fig.colorbar(im, ax=ax[2], shrink=0.8, ticks=[-0.45, 0.185, 0.355, 0.55, 1.33])
    cb.ax.set_yticklabels([c[0] for c in CLASES])
    for a in ax:
        gpd.GeoSeries([zona], crs=CRS).boundary.plot(ax=a, color="cyan", lw=0.8)
        g.plot(ax=a, color="yellow", markersize=2)
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle(f"Incendio {inc_id}: Sentinel-2 L2A · focos VIIRS (amarillo) · zona de 1 km (celeste)",
                 color=estilo.MORADO, fontweight="bold", fontsize=14)
    fig.savefig(FIG / f"mapa_dnbr_incendio_{inc_id}.png", dpi=130)
    print("Mapa guardado")


if __name__ == "__main__":
    modo, inc = sys.argv[1], int(sys.argv[2])
    (listar if modo == "listar" else calcular)(inc, sys.argv[3], sys.argv[4])
