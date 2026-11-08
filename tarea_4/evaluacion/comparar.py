"""Resume evaluacion/resultados.csv: tablas en Markdown (para comparacion.md) y figuras/evaluacion_aciertos.png.

    uv run evaluacion/comparar.py        # desde tarea_4/
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

AQUI = Path(__file__).parent
FIGURA = AQUI.parent / "figuras" / "evaluacion_aciertos.png"
CREMA, CARBON, VERDE, MORADO, GRIS = "#F7F3EA", "#2B2B2B", "#1F5F4A", "#6A4C93", "#A8A29A"
COLORES = {"correcta": VERDE, "incorrecta": MORADO, "sin respuesta": GRIS, "error": "#D9D2C3"}
NOMBRE_MODO = {"A": "A · sin MCP ni skills", "B": "B · con MCP y skills"}


def md(df):
    cols = list(df.columns)
    filas = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    filas += ["| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(filas)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    res = pd.read_csv(AQUI / "resultados.csv", dtype={"id": str})
    n = res.groupby("modo").size()

    # 1. Resumen por modo
    conteo = res.groupby("modo").resultado.value_counts().unstack(fill_value=0).reindex(columns=list(COLORES),
                                                                                       fill_value=0)
    resumen = conteo.assign(total=n, segundos_promedio=res.groupby("modo").segundos.mean().round(1),
                            segundos_mediana=res.groupby("modo").segundos.median().round(1),
                            usaron_mcp=res.groupby("modo").uso_mcp.sum(),
                            usaron_skill=res.groupby("modo").skills_usadas.apply(lambda s: s.notna().sum()))
    print("## Resumen por modo\n\n" + md(resumen.reset_index()) + "\n")
    print("## Por tipo de pregunta (correctas / total)\n")
    tipo = res.groupby(["tipo", "modo"]).resultado.apply(lambda s: f"{(s == 'correcta').sum()}/{len(s)}").unstack()
    print(md(tipo.reset_index()) + "\n")

    # 2. Por pregunta
    ancho = res.pivot(index="id", columns="modo", values="resultado")
    cambio = []
    for i, r in ancho.iterrows():
        a, b = r.get("A"), r.get("B")
        cambio.append("mejora" if a != "correcta" and b == "correcta" else
                      "empeora" if a == "correcta" and b != "correcta" else "igual")
    ancho["cambio_A_a_B"] = cambio
    print("## Por pregunta\n\n" + md(ancho.reset_index()) + "\n")
    det = res[["id", "modo", "verdad", "valor", "verdad_2", "valor_2", "resultado", "coherente_auto", "herramientas",
               "segundos", "acceso_fuera_copia", "error"]].copy()
    det["herramientas"] = det.herramientas.fillna("").str.slice(0, 90)
    print("## Detalle\n\n" + md(det) + "\n")

    # 3. Figura: barras apiladas por modo + matriz por pregunta
    plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": CARBON, "axes.labelcolor": CARBON,
                         "xtick.color": CARBON, "ytick.color": CARBON})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.15, 1]},
                                   facecolor=CREMA)
    modos = [m for m in ("A", "B") if m in conteo.index]
    izq = pd.Series(0, index=modos)
    for cat, color in COLORES.items():
        v = conteo.loc[modos, cat]
        if v.sum() == 0:
            continue
        ax1.barh([NOMBRE_MODO[m] for m in modos], v, left=izq, color=color, label=cat, height=0.55)
        for m in modos:
            if v[m]:
                ax1.text(izq[m] + v[m] / 2, NOMBRE_MODO[m], str(v[m]), ha="center", va="center",
                         color="white" if cat in ("correcta", "incorrecta") else CARBON, fontsize=11, weight="bold")
        izq += v
    ax1.set_xlim(0, int(n.max()))
    ax1.set_xlabel("Preguntas (de 10)")
    ax1.invert_yaxis()
    ax1.set_title("Resultado por modo", loc="left", fontsize=12, weight="bold")
    ax1.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False, fontsize=9)

    ids = list(ancho.index)
    for j, m in enumerate(modos):
        for i, q in enumerate(ids):
            ax2.scatter(i, j, s=260, marker="s", color=COLORES.get(ancho.loc[q, m], "white"), edgecolor=CARBON,
                        linewidth=0.4)
    ax2.set_xticks(range(len(ids)), ids)
    ax2.set_yticks(range(len(modos)), [NOMBRE_MODO[m] for m in modos])
    ax2.set_ylim(len(modos) - 0.5, -0.5)
    ax2.set_title("Resultado por pregunta", loc="left", fontsize=12, weight="bold")
    for ax in (ax1, ax2):
        ax.set_facecolor(CREMA)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    ax2.tick_params(length=0)
    modelo = ", ".join(res.modelo.unique())
    fig.text(0.01, 0.01, f"Fuente: evaluacion/resultados.csv (claude -p, modelo {modelo}, una corrida por pregunta y "
             "modo). B = BCRP, E = ENAHO 2024, C = combinadas.", fontsize=8, color=CARBON)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    FIGURA.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURA, dpi=150, facecolor=CREMA)
    print(f"Figura: {FIGURA}")


if __name__ == "__main__":
    main()
