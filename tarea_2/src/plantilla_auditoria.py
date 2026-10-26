"""Sortea las 20 extracciones del LLM a auditar (10 documentos + 10 audios) y arma la plantilla.

    .venv/Scripts/python.exe src/plantilla_auditoria.py

Se corre una sola vez. Sorteo: pandas.sample(random_state=2026) dentro de cada modalidad, entre las
extracciones que existen (el 25/10 la cuota diaria gratuita de Gemini dejó 19 documentos y 13 audios: el
sorteo es entre esos; la disponibilidad no depende de la calidad de la extracción). La plantilla queda en
datos/raw/referencias/auditoria_llm.xlsx (fuera de Git: contiene textos aún no revisados) y los criterios
en trabajo_manual/04_GUIA_auditoria_llm.md.
"""
import json
from pathlib import Path

import pandas as pd

from hojas_revision import guardar

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"
SEMILLA = 2026


def main():
    salida = RAW / "referencias" / "auditoria_llm.xlsx"
    if salida.exists():
        raise SystemExit("auditoria_llm.xlsx ya existe: el sorteo se hace una sola vez.")
    ext = pd.DataFrame([json.loads(p.read_text(encoding="utf-8")) for p in (RAW / "llm").glob("*.json")])
    ext["campos_json"] = ext["campos"].map(lambda c: json.dumps(c, ensure_ascii=False))
    ext = ext.sort_values("id").reset_index(drop=True)
    print(ext["modalidad"].value_counts().to_string())
    textos = pd.concat([
        pd.read_csv(RAW / "documentos" / "ocr_seudonimizado.csv")[["id", "texto_ocr"]].rename(columns={"texto_ocr": "texto"}),
        pd.read_csv(RAW / "audio" / "asr_seudonimizado.csv")[["id", "texto_asr_seud"]].rename(columns={"texto_asr_seud": "texto"})])
    muestra = pd.concat([ext[ext["modalidad"] == m].sample(n=10, random_state=SEMILLA) for m in ["documento", "audio"]])
    muestra = muestra.merge(textos, on="id", how="left")
    for col in ["tema_ok", "resumen_ok", "campos_especificos_ok", "sin_inventos", "completamente_correcta", "error_observado"]:
        muestra[col] = ""
    muestra["texto"] = muestra["texto"].fillna("").str.slice(0, 32000)  # límite de celda de Excel
    muestra["campos_legibles"] = muestra["campos_json"].map(
        lambda s: " | ".join(f"{k}: {v}" for k, v in json.loads(s).items() if not k.startswith("_")))
    muestra[["id", "modalidad", "texto", "campos_legibles", "tema_ok", "resumen_ok", "campos_especificos_ok",
             "sin_inventos", "completamente_correcta", "error_observado"]].pipe(
        lambda d: guardar(d, salida, {"texto": 90, "campos_legibles": 70, "error_observado": 40}, revision=False))
    print(muestra[["id", "modalidad"]].to_string(index=False))


if __name__ == "__main__":
    main()
