"""Paleta propia del proyecto (las escalas de dNBR y población se mantienen estándar)."""
import matplotlib as mpl

CREMA, CARBON, VERDE, MORADO = "#F7F3EA", "#2B2B2B", "#1F5F4A", "#6A4C93"


def aplicar():
    mpl.rcParams.update({
        "figure.facecolor": CREMA, "axes.facecolor": CREMA, "savefig.facecolor": CREMA,
        "text.color": CARBON, "axes.labelcolor": CARBON, "xtick.color": CARBON, "ytick.color": CARBON,
        "axes.edgecolor": CARBON, "axes.titlecolor": MORADO, "axes.titleweight": "bold",
        "font.size": 11,
    })
