"""Aplica la regla de modelos/config_evaluacion.json y guarda datos/muestra_evaluacion.csv.

    .venv/Scripts/python.exe src/elegir_muestra.py audio
    .venv/Scripts/python.exe src/elegir_muestra.py documentos

Solo usa metadatos (tipo, condición, duración del archivo, descartes de la limpieza):
nunca salidas de OCR o ASR. Se corre una sola vez, cuando el corpus de 25+ documentos
esté completo, y su resultado se commitea ANTES de escribir las referencias manuales.
"""
import json
import sys
from pathlib import Path

import pandas as pd
import soundfile as sf

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"


def sortear(elegibles, n, semilla):
    return elegibles.sort_values("id").sample(n=n, random_state=semilla)


def muestra_documentos(cfg, semilla):
    docs = pd.read_csv(RAW / "documentos" / "corpus_documentos.csv")  # incluye capturas propias
    docs = docs[~docs["titulo_original"].isin(cfg["excluir_por_titulo"]) & ~docs["descartado"]]
    partes = [sortear(docs[docs["tipo"] == t], n, semilla) for t, n in cfg["cuotas_por_tipo"].items()]
    return pd.concat(partes).assign(modalidad="documento")[["id", "modalidad", "tipo"]]


def muestra_audio(cfg, semilla):
    clips = pd.read_csv(RAW / "audio" / "limpieza.csv").merge(
        pd.read_csv(RAW / "audio" / "descargas.csv")[["titulo_original", "condicion", "idioma"]], on="titulo_original")
    clips["duracion_archivo"] = [sf.info(RAW / "audio" / "clips" / f"{i}.wav").duration for i in clips["id"]]
    clips = clips[(clips["idioma"] == "es") & ~clips["descartado"]]
    obligatorios = clips[clips["titulo_original"].isin(cfg["obligatorios"])]
    elegibles = clips[(clips["duracion_archivo"] <= cfg["duracion_maxima_seg"]) & ~clips["id"].isin(obligatorios["id"])]
    partes = [obligatorios]
    for cond, n in cfg["cuotas_por_condicion"].items():
        n_restante = n - (obligatorios["condicion"] == cond).sum()
        partes.append(sortear(elegibles[elegibles["condicion"] == cond], n_restante, semilla))
    m = pd.concat(partes).assign(modalidad="audio").rename(columns={"condicion": "tipo"})
    return m[["id", "modalidad", "tipo"]]


def main():
    """Uso: `elegir_muestra.py audio` o `elegir_muestra.py documentos`. Cada modalidad se sortea
    una sola vez y se guarda en su propio archivo; la de audio no depende de las fotos propias."""
    cfg = json.loads((RAIZ / "modelos" / "config_evaluacion.json").read_text(encoding="utf-8"))
    modalidad = sys.argv[1]
    salida = RAIZ / "datos" / f"muestra_evaluacion_{modalidad}.csv"
    if salida.exists():
        raise SystemExit(f"{salida.name} ya existe: la muestra se sortea una sola vez y no se rehace.")
    if modalidad == "audio":
        muestra = muestra_audio(cfg["muestra_audio"], cfg["semilla"])
    else:
        muestra = muestra_documentos(cfg["muestra_documentos"], cfg["semilla"])
    assert len(muestra) == 10, len(muestra)
    muestra.to_csv(salida, index=False)
    print(muestra.to_string(index=False))


if __name__ == "__main__":
    main()
