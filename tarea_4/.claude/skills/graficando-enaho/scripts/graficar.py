"""Gráficos de pobreza monetaria (ENAHO 2024, INEI), ponderados con facpob07.

Se corre desde tarea_4/:
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por sexo
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por edad
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por departamento
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por todos

Lee salidas/personas_2024.parquet (lo crea la skill limpiando-enaho) y guarda figuras/pobreza_<por>.png a 200 dpi.
Imprime las cifras graficadas para que quien lo pida pueda citarlas.
"""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

BASE = Path("salidas/personas_2024.parquet")
FIGURAS = Path("figuras")
FUENTE = "Fuente: INEI, ENAHO 2024 (módulos 34 y 02). Elaboración propia, ponderado con facpob07."
UNIDAD = "% de personas en pobreza monetaria"

# Paleta del proyecto
CREMA, CARBON, VERDE, MORADO, GRIS = "#F7F3EA", "#2B2B2B", "#1F5F4A", "#6A4C93", "#8A8578"

COLUMNA = {"area": "area", "sexo": "sexo", "edad": "grupo_edad", "departamento": "departamento_nombre"}
ETIQUETAS = {"urbana": "Urbana", "rural": "Rural", "hombre": "Hombres", "mujer": "Mujeres"}
ORDEN_EDAD = ["0-14", "15-29", "30-44", "45-59", "60 y más"]


def pobreza_por(base, col):
    g = base.assign(_wp=base["pobre"] * base["facpob07"]).groupby(col, observed=True)
    t = pd.DataFrame({"pobreza_pct": 100 * g["_wp"].sum() / g["facpob07"].sum(), "n_obs": g.size()})
    return t


def estilo(ax):
    ax.set_facecolor(CREMA)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(GRIS)
    ax.tick_params(colors=CARBON, labelsize=10)


def cerrar(fig, ax, titulo, subtitulo, salida):
    fig.suptitle(titulo, x=0.02, ha="left", fontsize=13, fontweight="bold", color=CARBON)
    ax.set_title(subtitulo, loc="left", fontsize=10, color=GRIS, pad=8)
    fig.text(0.02, 0.012, FUENTE, fontsize=8, color=GRIS, ha="left")
    fig.get_layout_engine().set(rect=(0, 0.035, 1, 0.965))
    FIGURAS.mkdir(exist_ok=True)
    fig.savefig(salida, dpi=200, facecolor=CREMA)
    plt.close(fig)
    print(f"Figura: {salida}")


def barras_verticales(t, nacional, titulo, salida):
    fig, ax = plt.subplots(figsize=(8, 5.2), facecolor=CREMA, layout="constrained")
    estilo(ax)
    x = range(len(t))
    ax.bar(x, t["pobreza_pct"], color=VERDE, width=0.6, zorder=2)
    ax.axhline(nacional, color=MORADO, lw=1.5, ls="--", zorder=3, label=f"Promedio nacional: {nacional:.1f} %")
    for i, v in enumerate(t["pobreza_pct"]):   # el valor va dentro de la barra, lejos de la línea
        ax.text(i, v / 2, f"{v:.1f} %", ha="center", va="center", fontsize=12, fontweight="bold", color=CREMA,
                zorder=4)
    ley = ax.legend(loc="upper left", frameon=False, fontsize=9.5, borderaxespad=0.2)
    ley.get_texts()[0].set_color(MORADO)
    ax.set_xticks(list(x), [f"{c}\n(n = {n:,})" for c, n in zip(t.index, t["n_obs"])])
    ax.set_ylim(0, max(t["pobreza_pct"].max(), nacional) * 1.3)
    ax.set_ylabel(UNIDAD, color=CARBON)
    ax.yaxis.grid(True, color="#E2DCCF", lw=0.8, zorder=0)
    cerrar(fig, ax, titulo, f"Perú, 2024 · {UNIDAD}", salida)


def graficar_departamento(t, nacional, salida):
    t = t.sort_values("pobreza_pct")
    fig, ax = plt.subplots(figsize=(8.5, 9.5), facecolor=CREMA, layout="constrained")
    estilo(ax)
    y = range(len(t))
    ax.barh(y, t["pobreza_pct"], color=VERDE, height=0.7, zorder=2)
    for i, v in enumerate(t["pobreza_pct"]):
        if 0 < nacional - v < 3:   # la etiqueta chocaría con la línea del promedio: va dentro de la barra
            ax.text(v - 0.4, i, f"{v:.1f}", va="center", ha="right", fontsize=8.5, color=CREMA, zorder=4)
        else:
            ax.text(v + 0.4, i, f"{v:.1f}", va="center", fontsize=8.5, color=CARBON, zorder=4)
    ax.axvline(nacional, color=MORADO, lw=1.5, ls="--", zorder=3)
    ax.text(nacional + 0.4, len(t) - 0.45, f"Promedio nacional: {nacional:.1f} %", fontsize=9, color=MORADO,
            va="bottom", zorder=4)
    ax.set_yticks(list(y), t.index)
    ax.set_xlim(0, t["pobreza_pct"].max() * 1.12)
    ax.set_ylim(-0.7, len(t) + 0.3)
    ax.set_xlabel(UNIDAD, color=CARBON)
    ax.xaxis.grid(True, color="#E2DCCF", lw=0.8, zorder=0)
    alto, bajo = t.iloc[-1], t.iloc[0]
    titulo = (f"La pobreza va de {bajo['pobreza_pct']:.1f} % en {t.index[0]} "
              f"a {alto['pobreza_pct']:.1f} % en {t.index[-1]}")
    cerrar(fig, ax, titulo, f"Pobreza monetaria por departamento, Perú, 2024 · {UNIDAD}", salida)


def comparar(a_nom, a, b_nom, b):
    """Frase para el título a partir de los datos (sin juicios de significancia)."""
    if a >= b:
        return f"La pobreza {a_nom} ({a:.1f} %) supera a la {b_nom} ({b:.1f} %) en {a - b:.1f} puntos"
    return f"La pobreza {a_nom} ({a:.1f} %) es menor que la {b_nom} ({b:.1f} %) en {b - a:.1f} puntos"


def graficar(base, por):
    nacional = 100 * (base["pobre"] * base["facpob07"]).sum() / base["facpob07"].sum()
    t = pobreza_por(base, COLUMNA[por])
    salida = FIGURAS / f"pobreza_{por}.png"
    if por == "area":
        t = t.loc[["urbana", "rural"]]
        titulo = comparar("rural", t.loc["rural", "pobreza_pct"], "urbana", t.loc["urbana", "pobreza_pct"])
        t.index = [ETIQUETAS[i] for i in t.index]
        barras_verticales(t, nacional, titulo, salida)
    elif por == "sexo":
        t = t.loc[["mujer", "hombre"]]
        m, h = t.loc["mujer", "pobreza_pct"], t.loc["hombre", "pobreza_pct"]
        titulo = f"Pobreza de mujeres ({m:.1f} %) y hombres ({h:.1f} %): diferencia de {abs(m - h):.1f} puntos"
        t.index = [ETIQUETAS[i] for i in t.index]
        barras_verticales(t, nacional, titulo, salida)
    elif por == "edad":
        t = t.loc[ORDEN_EDAD]
        mayor = t["pobreza_pct"].idxmax()
        titulo = f"El grupo de {mayor} años tiene la mayor pobreza: {t.loc[mayor, 'pobreza_pct']:.1f} %"
        t.index = [f"{i} años" for i in t.index]
        barras_verticales(t, nacional, titulo, salida)
    else:
        graficar_departamento(t, nacional, salida)
    print(f"Pobreza nacional (facpob07): {nacional:.2f} %")
    print(t.sort_values("pobreza_pct", ascending=False).round(2).to_string() if por == "departamento"
          else t.round(2).to_string())


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--por", required=True, choices=[*COLUMNA, "todos"], help="corte del gráfico")
    args = ap.parse_args()
    if not BASE.exists():
        sys.exit(f"ERROR: no existe {BASE}. Usa primero la skill limpiando-enaho "
                 "(uv run .claude/skills/limpiando-enaho/scripts/limpiar.py).")
    base = pd.read_parquet(BASE)
    if base["facpob07"].isna().any() or (base["facpob07"] <= 0).any():
        sys.exit("ERROR: facpob07 tiene nulos o valores no positivos; vuelve a correr limpiando-enaho.")
    for por in (list(COLUMNA) if args.por == "todos" else [args.por]):
        graficar(base, por)


if __name__ == "__main__":
    main()
