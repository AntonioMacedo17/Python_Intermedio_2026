"""Paso 5: reportaje HTML autocontenido (scroll), contado desde las personas.

Todas las cifras se leen de datos/procesados (nada escrito a mano salvo citas de fuentes oficiales,
verificadas el 21 oct 2026 y marcadas según su nivel de verificación en la plantilla).
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import shapes
from rasterio.windows import from_bounds
from shapely.geometry import box, shape

BASE = Path(__file__).resolve().parents[1]
RAW, PROC = BASE / "datos" / "raw", BASE / "datos" / "procesados"
OUT = BASE / "dashboard"
OUT.mkdir(exist_ok=True)
ELEGIDO = 190
CRS_M = "EPSG:32718"

conteos = json.loads((PROC / "conteos_focos.json").read_text(encoding="utf-8"))
res = json.loads((PROC / "resumen_poblacion.json").read_text(encoding="utf-8"))
dn = json.loads((PROC / f"dnbr_incendio_{ELEGIDO}.json").read_text(encoding="utf-8"))
sens = pd.read_csv(PROC / f"sensibilidad_dnbr_incendio_{ELEGIDO}.csv")
escenas = pd.read_csv(PROC / f"escenas_s2_incendio_{ELEGIDO}.csv")
grad = pd.read_csv(PROC / "gradiente_definiciones.csv")
anillos = pd.read_csv(PROC / "anillos_distancia.csv")
pdist = pd.read_csv(PROC / "poblacion_5km_por_distrito.csv", dtype={"IDDIST": str})
pdep = pd.read_csv(PROC / "poblacion_5km_por_departamento.csv")
act = pd.read_csv(PROC / "incendios_activos_poblacion.csv")
focos = pd.read_csv(PROC / "focos_peru.csv")
el = act[act.incendio_id == ELEGIDO].iloc[0]

# ---------- Capas del mapa de Mazamari ----------
f = focos[focos.incendio_id == ELEGIDO]
gf = gpd.GeoDataFrame(f, geometry=gpd.points_from_xy(f.longitude, f.latitude), crs="EPSG:4326").to_crs(CRS_M)
aros = gpd.GeoDataFrame(
    {"radio_km": [5, 3, 1]},
    geometry=[gf.buffer(r * 1000).union_all() for r in (5, 3, 1)], crs=CRS_M,
).to_crs("EPSG:4326")
aros["geometry"] = aros.geometry.simplify(0.0003)

with rasterio.open(PROC / f"dnbr_incendio_{ELEGIDO}.tif") as src:
    d = src.read(1)
    clase = np.zeros(d.shape, "uint8")
    for i, lo in enumerate([0.10, 0.27, 0.44, 0.66], start=1):
        clase[np.nan_to_num(d, nan=-9) >= lo] = i
    pol = [(shape(g), int(v)) for g, v in shapes(clase, mask=clase > 0, transform=src.transform)]
    sev = gpd.GeoDataFrame({"clase": [v for _, v in pol]}, geometry=[g for g, _ in pol], crs=src.crs)
sev = sev.dissolve("clase").reset_index().to_crs("EPSG:4326")

x0, y0, x1, y1 = aros.total_bounds
x0, y0, x1, y1 = x0 - 0.03, y0 - 0.03, x1 + 0.03, y1 + 0.03
with rasterio.open(RAW / "per_ppp_2020_1km_Aggregated.tif") as src:
    w = from_bounds(x0, y0, x1, y1, src.transform).round_offsets().round_lengths()
    pop = src.read(1, window=w)
    tw = rasterio.windows.transform(w, src.transform)
celdas = []
for r in range(pop.shape[0]):
    for c in range(pop.shape[1]):
        v = float(pop[r, c])
        if v > 0:
            lx, ty = tw * (c, r)
            rx, by = tw * (c + 1, r + 1)
            celdas.append((round(v, 1), box(lx, by, rx, ty)))
pobl = gpd.GeoDataFrame({"v": [v for v, _ in celdas]}, geometry=[g for _, g in celdas], crs="EPSG:4326")

datos = {
    "aros": json.loads(aros.to_json()),
    "sev": json.loads(sev.to_json()),
    "pob": json.loads(pobl.to_json()),
    "focos": f[["latitude", "longitude", "fecha_hora", "sensor", "frp"]].round(5).to_dict("records"),
    "anillos": anillos.to_dict("records"),
}


def n(x, dec=0):
    """Número en formato peruano: espacio de miles, coma decimal."""
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


def pct(x, dec=1):
    return n(x, dec) + " %"


# Comparaciones exactas, dentro del mismo dataset (WorldPop 2020)
pob_mz = float(pdist.loc[pdist.NOMBDIST == "MAZAMARI", "poblacion"].iat[0])
veces_mz = res["personas_5km_vegetacion"] / pob_mz
uno_de = res["poblacion_peru_worldpop2020"] / res["personas_5km_vegetacion"]
junin = pdep.iloc[0]
pct_junin = 100 * junin.expuesta_5km / res["personas_5km_vegetacion"]
a = anillos.set_index("radio_km")

top = pdist[pdist.expuesta_5km > 0].head(15)
maxv = top.expuesta_5km.max()
ranking = "".join(
    f"""<li><span class="rk-n">{i}</span><div class="rk-body"><div class="rk-top"><b>{r.NOMBDIST.title()}</b>
<span class="rk-lugar">{r.NOMBPROV.title()}, {r.NOMBDEP.title()}</span><em>{n(r.expuesta_5km)}</em></div>
<div class="rk-bar"><i style="width:{100 * r.expuesta_5km / maxv:.1f}%"></i></div>
<div class="rk-sub">{pct(r.pct_expuesta)} de sus {n(r.poblacion)} habitantes · {r.incendios_activos} incendio(s) activo(s) dentro del distrito</div></div></li>"""
    for i, r in enumerate(top.itertuples(), start=1)
)


def uso(r):
    if r.fecha == dn["fecha_pre"]:
        return "<b>antes</b>"
    if r.fecha == dn["fecha_post"]:
        return "<b>después</b>"
    if r.fecha in set(sens.fecha_pre):
        return "sensibilidad"
    return "descartada (nubes)" if r.pct_valido < 90 else "no usada"


filas_esc = "".join(
    f"<tr{' class=sel' if r.fecha in (dn['fecha_pre'], dn['fecha_post']) else ''}><td>{r.fecha}</td>"
    f"<td class=n>{pct(r.pct_nube_zona)}</td><td class=n>{pct(r.pct_valido)}</td><td class=n>{pct(r.nube_escena)}</td><td>{uso(r)}</td></tr>"
    for r in escenas.itertuples()
)
filas_sens = "".join(
    f"<tr{' class=sel' if r.fecha_pre == dn['fecha_pre'] else ''}><td>{r.fecha_pre}</td><td>{r.fecha_post}</td>"
    f"<td class=n>{n(r.ha_dnbr_027)}</td><td class=n>{n(r.ha_dnbr_010)}</td></tr>" for r in sens.itertuples()
)
filas_grad = "".join(
    f"<tr><td>{r.definicion.replace('>=', '≥')}</td><td class=n>{r.incendios}</td><td class=n>{n(r.personas_5km)}</td></tr>"
    for r in grad.itertuples()
)

MESES = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def fecha(t):
    return f"{t.day} {MESES[t.month]} {t.year}, {t:%H:%M}"


fin = pd.Timestamp(conteos["corte_fin_utc"])
reemplazos = {
    "__CORTE_UTC__": fecha(fin) + " UTC",
    "__CORTE_LIMA__": f"{(fin - pd.Timedelta(hours=5)):%H:%M} h de Lima",
    "__VENTANA__": f"{fecha(pd.Timestamp(conteos['corte_inicio_utc']))} – {fecha(fin)} UTC",
    "__ACTIVO_DESDE__": fecha(fin - pd.Timedelta(hours=48)) + " UTC",
    "__P5__": n(res["personas_5km_vegetacion"]),
    "__P5_MIL__": n(round(res["personas_5km_vegetacion"] / 1000)),
    "__PCT_PERU__": pct(res["pct_peru_vegetacion"], 2),
    "__INC_VEG__": str(res["incendios_activos_vegetacion"]),
    "__INC_URB__": str(res["incendios_activos_urbanos_excluidos"]),
    "__F_SA__": n(conteos["focos_sudamerica"]), "__F_PE__": n(conteos["focos_peru"]),
    "__F_CONF__": n(conteos["focos_sin_conf_baja"]), "__F_LIM__": n(conteos["focos_limpios"]),
    "__N_FIJAS__": str(conteos["fuentes_fijas"]),
    "__INC__": n(conteos["incendios"]), "__INC_ACT__": str(conteos["incendios_activos"]),
    "__MZ_FOCOS__": str(int(el.n_focos)),
    "__MZ_HA27__": n(dn["ha_quemadas_dnbr_027"]), "__MZ_HA10__": n(dn["ha_quemadas_dnbr_010"]),
    "__MZ_P5__": n(a.loc[5, "personas_mazamari"]), "__MZ_P3__": n(a.loc[3, "personas_mazamari"]),
    "__MZ_P1__": n(a.loc[1, "personas_mazamari"]),
    "__MZ_PRE__": dn["fecha_pre"], "__MZ_POST__": dn["fecha_post"],
    "__MZ_MASK__": pct(dn["pct_zona_enmascarada"]), "__MZ_ZONA__": n(dn["zona_ha"]),
    "__MZ_RANGO__": f"{n(sens.ha_dnbr_027.min())} a {n(sens.ha_dnbr_027.max())} ha",
    "__MZ_INICIO__": el.inicio[:16], "__MZ_ULTIMO__": el.ultimo[:16],
    "__P1__": n(a.loc[1, "personas_veg"]), "__P3__": n(a.loc[3, "personas_veg"]),
    "__G0__": n(grad.personas_5km.iat[0]), "__G3__": n(grad.personas_5km.iat[-1]),
    "__G3_INC__": str(grad.incendios.iat[-1]),
    "__UNFOCO__": str(int((act[~act.urbano].n_focos == 1).sum())),
    "__VECES_MZ__": n(veces_mz, 1), "__VECES_MZ_EXACTO__": n(veces_mz, 2), "__POB_MZ__": n(pob_mz),
    "__UNO_DE__": n(uno_de, 0), "__UNO_DE_EXACTO__": n(uno_de, 2),
    "__POB_PERU__": n(res["poblacion_peru_worldpop2020"]),
    "__JUNIN_P__": n(junin.expuesta_5km), "__JUNIN_PCT__": pct(pct_junin),
    "__JUNIN_PCTDEP__": pct(junin.pct_expuesta, 2),
    "__RANKING__": ranking,
    "__FILAS_ESC__": filas_esc, "__FILAS_SENS__": filas_sens, "__FILAS_GRAD__": filas_grad,
    "__DATOS__": json.dumps(datos, ensure_ascii=False, separators=(",", ":")),
}

html = (BASE / "src" / "plantilla_reportaje.html").read_text(encoding="utf-8")
for k, v in reemplazos.items():
    html = html.replace(k, v)
faltan = sorted(set(t for t in __import__("re").findall(r"__[A-Z0-9_]+__", html)))
assert not faltan, faltan
(OUT / "index.html").write_text(html, encoding="utf-8")
print(f"Reportaje: {OUT / 'index.html'} ({len(html) / 1e6:.2f} MB)")
