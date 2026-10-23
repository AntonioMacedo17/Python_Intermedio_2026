"""Sortea las 20 extracciones del LLM a auditar (10 documentos + 10 audios) y arma la plantilla.

    .venv/Scripts/python.exe src/plantilla_auditoria.py

Se corre una sola vez, con el corpus completo ya extraído. Sorteo: pandas.sample(random_state=2026)
dentro de cada modalidad. La plantilla queda en datos/raw/referencias/auditoria_llm.csv (fuera de Git:
contiene textos aún no revisados) y los criterios en trabajo_manual/04_GUIA_auditoria_llm.md.
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"
SEMILLA = 2026


def main():
    salida = RAW / "referencias" / "auditoria_llm.csv"
    if salida.exists():
        raise SystemExit("auditoria_llm.csv ya existe: el sorteo se hace una sola vez.")
    ext = pd.read_csv(RAW / "llm" / "extraccion_llm_borrador.csv").sort_values("id")
    textos = pd.concat([
        pd.read_csv(RAW / "documentos" / "ocr_seudonimizado.csv")[["id", "texto_ocr"]].rename(columns={"texto_ocr": "texto"}),
        pd.read_csv(RAW / "audio" / "asr_seudonimizado.csv")[["id", "texto_asr_seud"]].rename(columns={"texto_asr_seud": "texto"})])
    muestra = pd.concat([ext[ext["modalidad"] == m].sample(n=10, random_state=SEMILLA) for m in ["documento", "audio"]])
    muestra = muestra.merge(textos, on="id", how="left")
    for col in ["tema_ok", "resumen_ok", "campos_especificos_ok", "sin_inventos", "completamente_correcta", "error_observado"]:
        muestra[col] = ""
    muestra["campos_legibles"] = muestra["campos_json"].map(
        lambda s: " | ".join(f"{k}: {v}" for k, v in json.loads(s).items() if not k.startswith("_")))
    muestra[["id", "modalidad", "texto", "campos_legibles", "tema_ok", "resumen_ok", "campos_especificos_ok",
             "sin_inventos", "completamente_correcta", "error_observado"]].to_csv(salida, index=False, encoding="utf-8-sig")
    print(muestra[["id", "modalidad"]].to_string(index=False))


if __name__ == "__main__":
    main()
