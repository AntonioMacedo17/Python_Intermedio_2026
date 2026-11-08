"""Mapa de la pobreza monetaria por departamento (ENAHO 2024, INEI), ponderado con facpob07.

Se corre desde tarea_4/:
    uv run .claude/skills/mapeando-enaho/scripts/mapear.py

Entra:  salidas/personas_2024.parquet (lo crea la skill limpiando-enaho)
        datos/peru_departamental_simple.geojson (si no está, se descarga del repositorio del curso)
        referencias/pobreza_departamento_2024.csv (para comparar)
Sale:   mapas/pobreza_departamento.png (200 dpi)
        salidas/comparacion_mapa_referencia.csv (diferencias por departamento)

La unión es por código, nunca por nombre: ubigeo[:2] con FIRST_IDDP, ambos texto de 2 dígitos.
Exige 25 departamentos con dato (Lima 15 y Callao 07 separados); si no, termina con error.
"""
import math
import sys
from pathlib import Path

import geopandas as gpd
import httpx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402

BASE = Path("salidas/personas_2024.parquet")
GEOJSON = Path("datos/peru_departamental_simple.geojson")
URL_GEOJSON = ("https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/"
               "lab/Data/peru_departamental_simple.geojson")
REFERENCIA = Path("referencias/pobreza_departamento_2024.csv")
MAPA = Path("mapas/pobreza_departamento.png")
COMPARACION = Path("salidas/comparacion_mapa_referencia.csv")

FUENTE = ("Fuente: INEI, ENAHO 2024 (módulos 34 y 02). Elaboración propia, ponderado con facpob07.\n"
          "Límites departamentales: repositorio d2cml-ai/Data-Science-Python (sesión 06).")
UNIDAD = "% de personas en pobreza monetaria"
CREMA, CARBON, GRIS = "#F7F3EA", "#2B2B2B", "#8A8578"
ESCALA = "Greens"   # secuencial de un solo tono, de claro a oscuro (matplotlib)
LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]


def error(msg):
    sys.exit(f"ERROR: {msg}")


def cargar_geojson():
    if not GEOJSON.exists():
        print(f"No está {GEOJSON}; lo descargo de {URL_GEOJSON}")
        r = httpx.get(URL_GEOJSON, timeout=60, follow_redirects=True)
        r.raise_for_status()
        GEOJSON.parent.mkdir(parents=True, exist_ok=True)
        GEOJSON.write_bytes(r.content)
    geo = gpd.read_file(GEOJSON)
    if "FIRST_IDDP" not in geo.columns:
        error(f"el GeoJSON no tiene la columna FIRST_IDDP (columnas: {list(geo.columns)})")
    geo["FIRST_IDDP"] = geo["FIRST_IDDP"].astype(str).str.strip().str.zfill(2)
    return geo


def pobreza_departamental(base):
    """Pobreza por departamento con facpob07 (método del mapa) y, para comparar, con el método de la sumaria."""
    g = base.assign(_wp=base["pobre"] * base["facpob07"]).groupby("departamento")
    t = pd.DataFrame({
        "departamento_nombre": g["departamento_nombre"].first(),
        "pobreza_pct": 100 * g["_wp"].sum() / g["facpob07"].sum(),
        "n_obs": g.size(),
        "poblacion_expandida": g["facpob07"].sum().round(),
    })
    hog = base.drop_duplicates(LLAVES_HOGAR)   # un registro por hogar: factor07 × mieperho
    w = hog["factor07"] * hog["mieperho"]
    hs = hog.assign(_w=w, _wp=w * hog["pobre"]).groupby("departamento")
    t["pobreza_metodo_sumaria_pct"] = 100 * hs["_wp"].sum() / hs["_w"].sum()
    return t, len(hog)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not BASE.exists():
        error(f"no existe {BASE}. Usa primero la skill limpiando-enaho "
              "(uv run .claude/skills/limpiando-enaho/scripts/limpiar.py).")
    base = pd.read_parquet(BASE)
    base[["facpob07", "factor07"]] = base[["facpob07", "factor07"]].astype("float64")   # evita ruido de float32
    base["departamento"] = base["ubigeo"].astype(str).str[:2]
    t, n_hogares = pobreza_departamental(base)

    geo = cargar_geojson()
    # Chequeos de la unión por código
    if geo["FIRST_IDDP"].duplicated().any():
        error(f"códigos repetidos en el GeoJSON: {geo.loc[geo['FIRST_IDDP'].duplicated(), 'FIRST_IDDP'].tolist()}")
    if len(geo) != 25:
        error(f"el GeoJSON tiene {len(geo)} unidades, se esperaban 25")
    mapa = geo.merge(t, left_on="FIRST_IDDP", right_index=True, how="left", validate="1:1")
    sin_dato = mapa.loc[mapa["pobreza_pct"].isna(), "FIRST_IDDP"].tolist()
    if sin_dato:
        error(f"departamentos del mapa sin dato: {sin_dato}")
    sobran = sorted(set(t.index) - set(geo["FIRST_IDDP"]))
    if sobran:
        error(f"departamentos de la ENAHO que no están en el mapa: {sobran}")
    if not {"07", "15"} <= set(mapa["FIRST_IDDP"]):
        error("Lima (15) y Callao (07) deben estar como unidades separadas")
    print(f"Unión por código: {len(mapa)} de 25 departamentos con dato (Lima 15 y Callao 07 separados).")

    # Mapa
    vmax = math.ceil(mapa["pobreza_pct"].max() / 10) * 10
    norm = Normalize(vmin=0, vmax=vmax)
    fig, ax = plt.subplots(figsize=(7.5, 9.5), facecolor=CREMA, layout="constrained")
    ax.set_facecolor(CREMA)
    mapa.plot(column="pobreza_pct", cmap=ESCALA, norm=norm, edgecolor="white", linewidth=0.6, ax=ax)
    ax.set_axis_off()
    ax.set_aspect("equal")
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=ESCALA), ax=ax, shrink=0.45, pad=0.01, aspect=22)
    cb.set_label(UNIDAD, color=CARBON, fontsize=10)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=CARBON, labelsize=9)

    alto = t["pobreza_pct"].idxmax()
    bajo = t["pobreza_pct"].idxmin()
    titulo = (f"Pobreza monetaria por departamento, Perú 2024: de {t.loc[bajo, 'pobreza_pct']:.1f} % en "
              f"{t.loc[bajo, 'departamento_nombre']}\na {t.loc[alto, 'pobreza_pct']:.1f} % en "
              f"{t.loc[alto, 'departamento_nombre']}")
    fig.suptitle(titulo, x=0.03, ha="left", fontsize=12.5, fontweight="bold", color=CARBON)
    fig.text(0.03, 0.01, FUENTE, fontsize=7.5, color=GRIS, ha="left", va="bottom")
    fig.get_layout_engine().set(rect=(0, 0.045, 1, 0.96))
    MAPA.parent.mkdir(exist_ok=True)
    fig.savefig(MAPA, dpi=200, facecolor=CREMA)
    plt.close(fig)
    print(f"Mapa: {MAPA} (escala {ESCALA} de 0 a {vmax} %)")

    # Comparación con la referencia (no se ajusta nada: solo se reporta)
    ref = pd.read_csv(REFERENCIA, dtype={"ccdd": str})
    ref["ccdd"] = ref["ccdd"].str.zfill(2)
    comp = ref.merge(t, left_on="ccdd", right_index=True, how="outer", validate="1:1", indicator=True)
    if (comp["_merge"] != "both").any():
        error(f"códigos que no cruzan con la referencia: {comp.loc[comp['_merge'] != 'both', 'ccdd'].tolist()}")
    comp = comp.rename(columns={"pobreza_pct_x": "referencia_pct", "pobreza_pct_y": "calculado_facpob07_pct"})
    comp["diferencia_pp"] = comp["calculado_facpob07_pct"] - comp["referencia_pct"]
    comp["diferencia_metodo_sumaria_pp"] = comp["pobreza_metodo_sumaria_pct"] - comp["referencia_pct"]
    comp = comp[["ccdd", "departamento", "referencia_pct", "calculado_facpob07_pct", "diferencia_pp",
                 "pobreza_metodo_sumaria_pct", "diferencia_metodo_sumaria_pp", "n_obs", "poblacion_expandida"]]
    comp = comp.round({"calculado_facpob07_pct": 2, "diferencia_pp": 2, "pobreza_metodo_sumaria_pct": 2,
                       "diferencia_metodo_sumaria_pp": 2})
    comp.to_csv(COMPARACION, index=False, encoding="utf-8")

    i = comp["diferencia_pp"].abs().idxmax()
    j = comp["diferencia_metodo_sumaria_pp"].abs().idxmax()
    print(f"Comparación: {COMPARACION} (25 departamentos; referencia: {REFERENCIA})")
    print(f"Diferencia máxima (facpob07 vs referencia): {comp.loc[i, 'diferencia_pp']:+.2f} pp en "
          f"{comp.loc[i, 'departamento']} ({comp.loc[i, 'calculado_facpob07_pct']:.2f} vs {comp.loc[i, 'referencia_pct']})")
    print(f"Diferencia máxima con el método de la sumaria (factor07 × mieperho, {n_hogares:,} hogares): "
          f"{comp.loc[j, 'diferencia_metodo_sumaria_pp']:+.2f} pp en {comp.loc[j, 'departamento']}")
    print(comp.to_string(index=False))


if __name__ == "__main__":
    main()
