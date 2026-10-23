"""Métricas de la Parte 2, tal como se fijaron en modelos/config_evaluacion.json.

- Normalización: voz.normalizar() (minúsculas, NFC, sin puntuación, espacios simples; tildes se quedan),
  igual para la referencia y para la salida del modelo.
- Las marcas de hablante [HABLANTE_n] se quitan antes del WER (no son palabras habladas).
- CER/WER agregado: errores totales / caracteres (o palabras) totales de la referencia, sobre los 10 casos
  (jiwer con listas). También se da el valor por caso.
- RTF = segundos de procesamiento / duración del audio.
"""
import re
import sys
from pathlib import Path

import jiwer
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voz import normalizar  # noqa: E402

MARCA = re.compile(r"\[HABLANTE_\d+\]")


def limpiar(texto):
    return normalizar(MARCA.sub(" ", texto if isinstance(texto, str) else ""))


def tasa(refs, hips, metrica):
    """CER o WER agregado sobre listas. Una salida vacía cuenta como todo borrado."""
    r = [limpiar(x) for x in refs]
    h = [limpiar(x) or "∅" for x in hips]
    return (jiwer.cer if metrica == "CER" else jiwer.wer)(r, h)


def por_caso(df, col_ref, col_hip, metrica):
    """Devuelve una Serie con la métrica de cada fila (misma normalización)."""
    return pd.Series([tasa([a], [b], metrica) for a, b in zip(df[col_ref], df[col_hip])], index=df.index)
