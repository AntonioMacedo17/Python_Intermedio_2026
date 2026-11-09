"""Gráfico del contexto macro 2020-2024 con datos del BCRP obtenidos del servidor MCP (Tarea 4, Parte 3).

    uv run informes/scripts/grafico_bcrp.py        # desde tarea_4/

Llama al servidor MCP en memoria (fastmcp Client, igual que mcp/test_server.py): ninguna cifra se escribe a mano.
Guarda:
  - figuras/bcrp_inflacion_pbi_2020_2024.png
  - salidas/bcrp_contexto.json  (todo lo que devolvieron las herramientas: resúmenes, series anuales y correlaciones)

Series: PN01273PM (IPC Lima Metropolitana, var. % 12 meses), PN01728AM (PBI, var. % interanual, mensual),
PM04863AA (PBI, var. % anual) y PM05876FA (ingresos tributarios del gobierno general, % del PBI).
La banda meta de inflación NO se dibuja: no se pudo confirmar en una página oficial del BCRP (ver informe).
"""
import asyncio
import json
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from fastmcp import Client

RAIZ = Path(__file__).resolve().parents[2]          # tarea_4/
sys.path.insert(0, str(RAIZ / "mcp"))
from server import mcp                               # noqa: E402

INFL, PBI_M, PBI_A, TRIB = "PN01273PM", "PN01728AM", "PM04863AA", "PM05876FA"
DESDE, HASTA = "2020-01", "2024-12"
FIG = RAIZ / "figuras" / "bcrp_inflacion_pbi_2020_2024.png"
SALIDA = RAIZ / "salidas" / "bcrp_contexto.json"

# Delimitación propia (no oficial) del periodo de pandemia para sombrear: desde el primer mes con caída del PBI
# en los datos de 2020 (mar-2020) hasta dic-2021. Se declara así en la figura y en el informe.
PANDEMIA = ("2020-03-01", "2021-12-31")

CREMA, CARBON, VERDE, MORADO, GRIS = "#F7F3EA", "#2B2B2B", "#1F5F4A", "#6A4C93", "#8A8578"


async def consultar():
    async with Client(mcp) as c:
        async def h(nombre, **args):
            return (await c.call_tool(nombre, args)).data
        r = {
            "resumen_inflacion": await h("resumen", codigo=INFL, desde=DESDE, hasta=HASTA),
            "resumen_pbi_mensual": await h("resumen", codigo=PBI_M, desde=DESDE, hasta=HASTA),
            "serie_inflacion": await h("serie", codigo=INFL, desde=DESDE, hasta=HASTA),
            "serie_pbi_mensual": await h("serie", codigo=PBI_M, desde=DESDE, hasta=HASTA),
            "serie_pbi_anual": await h("serie", codigo=PBI_A, desde="2020", hasta="2024"),
            "serie_tributarios_pct_pbi": await h("serie", codigo=TRIB, desde="2020", hasta="2024"),
            "correlaciones": [],
        }
        for desde in ("2020-01", "2022-01"):
            for dif in (False, True):
                k = await h("correlacion", codigo_a=INFL, codigo_b=PBI_M, desde=desde, hasta=HASTA,
                            en_diferencias=dif)
                k.pop("pares")       # los pares son las mismas series ya guardadas
                r["correlaciones"].append(k)
        return r


def a_serie(s):
    return pd.Series([x["valor"] for x in s["datos"]],
                     index=pd.to_datetime([x["periodo"] for x in s["datos"]]))


def main():
    r = asyncio.run(consultar())
    SALIDA.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")

    inf, pbi = a_serie(r["serie_inflacion"]), a_serie(r["serie_pbi_mensual"])
    ri, rp = r["resumen_inflacion"], r["resumen_pbi_mensual"]
    pbi_anual = {x["periodo"]: x["valor"] for x in r["serie_pbi_anual"]["datos"]}

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRIS, "axes.labelcolor": CARBON,
                         "xtick.color": CARBON, "ytick.color": CARBON, "text.color": CARBON})
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.2), sharex=True, facecolor=CREMA,
                                   gridspec_kw={"height_ratios": [1, 1.15], "hspace": 0.28})
    for ax in (ax1, ax2):
        ax.set_facecolor(CREMA)
        ax.axvspan(pd.Timestamp(PANDEMIA[0]), pd.Timestamp(PANDEMIA[1]), color=GRIS, alpha=0.15, lw=0)
        ax.grid(axis="y", color="#E2DDD0", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)

    # Panel 1: inflación
    ax1.plot(inf.index, inf.values, color=MORADO, lw=2.2)
    pico = pd.Timestamp(ri["maximo"]["periodo"])
    ax1.annotate(f"Pico: {ri['maximo']['valor']:.1f} % ({pico:%m-%Y})", (pico, ri["maximo"]["valor"]),
                 xytext=(0, 8), textcoords="offset points", fontsize=9.5, color=MORADO, ha="center")
    fin = pd.Timestamp(ri["ultimo"]["periodo"])
    ax1.annotate(f"{ri['ultimo']['valor']:.1f} %", (fin, ri["ultimo"]["valor"]), xytext=(4, 8),
                 textcoords="offset points", fontsize=9.5, color=MORADO, ha="right")
    ax1.set_ylim(0, ri["maximo"]["valor"] * 1.2)
    ax1.set_ylabel("Var. % 12 meses")
    ax1.set_title(f"Inflación de Lima Metropolitana (IPC, {INFL})", loc="left", fontsize=11.5, color=CARBON)
    ax1.text(pd.Timestamp(PANDEMIA[0]) + pd.Timedelta(days=20), ax1.get_ylim()[1] * 0.93,
             "Pandemia (delimitación propia:\nmar-2020 a dic-2021)", fontsize=8.5, color=GRIS, va="top")

    # Panel 2: PBI mensual + anual escrito
    ax2.axhline(0, color=GRIS, lw=1)
    ax2.plot(pbi.index, pbi.values, color=VERDE, lw=2.2)
    for clave in ("maximo", "minimo"):
        p = pd.Timestamp(rp[clave]["periodo"])
        ax2.annotate(f"{rp[clave]['valor']:.1f} % ({p:%m-%Y})", (p, rp[clave]["valor"]), xytext=(10, 0),
                     textcoords="offset points", fontsize=9.5, color=VERDE, va="center")
    for anio, v in pbi_anual.items():
        ax2.text(pd.Timestamp(f"{anio}-07-01"), 70, f"{anio}: {v:+.1f} %", ha="center", fontsize=9.5,
                 color=CARBON, fontweight="bold")
    ax2.text(pd.Timestamp("2020-01-20"), 84, f"Crecimiento anual del PBI ({PBI_A}):", fontsize=9, color=GRIS)
    ax2.set_ylim(-45, 95)
    ax2.set_ylabel("Var. % interanual")
    ax2.set_title(f"Producto bruto interno, variación respecto al mismo mes del año anterior ({PBI_M})",
                  loc="left", fontsize=11.5, color=CARBON)
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.set_xlim(pd.Timestamp("2020-01-01"), pd.Timestamp("2024-12-31"))

    fig.suptitle("Perú 2020-2024: la inflación subió hasta 2022 y luego bajó;\n"
                 "el PBI cayó en 2020 y rebotó en 2021", x=0.07, ha="left", fontsize=13.5, fontweight="bold",
                 color=CARBON)
    fig.text(0.07, 0.895, "Datos mensuales, enero 2020 - diciembre 2024 · porcentajes", fontsize=10.5, color=GRIS)
    fig.text(0.07, 0.015, f"Fuente: BCRP, series {INFL}, {PBI_M} y {PBI_A} (estadisticas.bcrp.gob.pe), vía el "
             "servidor MCP bcrp. Elaboración propia.\nLa banda meta de inflación no se dibuja: no se confirmó en "
             "una página oficial del BCRP en esta sesión.", fontsize=8.5, color=GRIS)
    fig.subplots_adjust(top=0.83, bottom=0.11, left=0.07, right=0.97)
    FIG.parent.mkdir(exist_ok=True)
    fig.savefig(FIG, dpi=200, facecolor=CREMA)

    print(f"Figura: {FIG.relative_to(RAIZ)}")
    print(f"Salida: {SALIDA.relative_to(RAIZ)}")
    print(f"Inflación {INFL}: pico {ri['maximo']}, mínimo {ri['minimo']}, promedio {ri['promedio']}, "
          f"último {ri['ultimo']}")
    print(f"PBI {PBI_M}: máximo {rp['maximo']}, mínimo {rp['minimo']}, promedio {rp['promedio']}")
    print(f"PBI anual {PBI_A}: {pbi_anual}")
    print("Tributarios % PBI", TRIB, {x['periodo']: x['valor'] for x in r['serie_tributarios_pct_pbi']['datos']})
    for k in r["correlaciones"]:
        print(f"Correlación {k['periodo_comun']} dif={k['en_diferencias']}: n={k['n_periodos']} "
              f"pearson={k['pearson']} spearman={k['spearman']}")


if __name__ == "__main__":
    main()
