"""Plantilla vacía para las referencias manuales de los 10 documentos de la muestra.

    .venv/Scripts/python.exe src/plantilla_referencias_documentos.py

No muestra ninguna salida de OCR (para no anclar la transcripción). Queda en
datos/raw/referencias/referencias_documentos.xlsx (fuera de Git). No sobrescribe una plantilla existente.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hojas_revision import guardar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"


def main():
    salida = RAW / "referencias" / "referencias_documentos.xlsx"
    if salida.exists():
        raise SystemExit("La plantilla ya existe: no se sobrescribe.")
    m = pd.read_csv(RAIZ / "datos" / "muestra_evaluacion_documentos.csv")
    corpus = pd.read_csv(RAW / "documentos" / "corpus_documentos.csv")[["id", "archivo_original"]]
    m = m.merge(corpus, on="id")
    m["imagen_para_mirar"] = m["archivo_original"].map(lambda p: str((RAIZ / p).resolve()))
    m["que_transcribir"] = "primeras 15 líneas en orden de lectura (o todo, si tiene 15 o menos)"
    m["texto_referencia"] = ""
    m["notas"] = ""
    guardar(m[["id", "tipo", "imagen_para_mirar", "que_transcribir", "texto_referencia", "notas"]], salida,
            {"imagen_para_mirar": 60, "que_transcribir": 30, "texto_referencia": 100, "notas": 40}, revision=False)


if __name__ == "__main__":
    main()
