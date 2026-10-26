"""Lógica de la Parte 2 (la usa 02_evaluacion.ipynb). Solo lee resultados ya calculados y referencias.

Decisión de método: CER/WER se calculan sobre el texto SIN seudonimizar de ambos lados (referencia manual y
salida del modelo), que vive en datos/raw/. Si se compararan textos seudonimizados, un seudónimo "acertado"
escondería errores reales de reconocimiento en los nombres. Lo que se publica son las métricas y, en los CSV,
las referencias ya seudonimizadas.
"""
import json
from pathlib import Path

import pandas as pd

from evaluacion import por_caso, tasa

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"


def muestra(modalidad):
    """10 ids sorteados con la regla commiteada (datos/muestra_evaluacion_<modalidad>.csv)."""
    return pd.read_csv(RAIZ / "datos" / f"muestra_evaluacion_{modalidad}.csv")


def referencias(modalidad):
    """Referencias manuales del estudiante (el .xlsx si existe; si no, el .csv).
    Devuelve (referencias completas, ids que faltan). Si falta la muestra o la plantilla, (None, todos)."""
    base = RAW / "referencias" / f"referencias_{modalidad}"
    ruta = next((p for p in [base.with_suffix(".xlsx"), base.with_suffix(".csv")] if p.exists()), None)
    try:
        m = muestra(modalidad)
    except FileNotFoundError:
        return None, ["(muestra aún no sorteada)"]
    if ruta is None:
        return None, sorted(m["id"])
    ref = pd.read_excel(ruta) if ruta.suffix == ".xlsx" else pd.read_csv(ruta, encoding="utf-8-sig")
    hechos = set(ref.loc[ref["texto_referencia"].fillna("").astype(str).str.strip() != "", "id"])
    falta = sorted(set(m["id"]) - hechos)
    ref = m.merge(ref.drop(columns=[c for c in ["tipo"] if c in ref]), on="id")
    return ref[ref["id"].isin(hechos)], falta


def salidas_documentos():
    """Texto y segundos por documento de cada OCR (base y alternativo)."""
    base = pd.read_csv(RAW / "documentos" / "ocr_crudo.csv")[["id", "texto_ocr_crudo", "segundos_ocr", "modelo_ocr"]]
    base.columns = ["id", "texto", "segundos", "modelo"]
    tess = pd.DataFrame([json.loads(p.read_text(encoding="utf-8")) for p in (RAW / "alternativos" / "tesseract").glob("*.json")])
    return {"PaddleOCR (base)": base, "Tesseract (alternativo)": tess[["id", "texto", "segundos", "modelo"]]}


def salidas_audio():
    """Texto, segundos y RTF por clip de cada ASR (base y alternativo, si ya corrió)."""
    base = pd.read_csv(RAW / "audio" / "asr_crudo.csv")
    base = base[base["id"].str.startswith("clip_")][["id", "texto_plano", "segundos_asr", "rtf", "modelo_asr"]]
    base.columns = ["id", "texto", "segundos", "rtf", "modelo"]
    salidas = {"faster-whisper small (base)": base}
    pk = list((RAW / "alternativos" / "parakeet").glob("*.json"))
    if pk:
        par = pd.DataFrame([json.loads(p.read_text(encoding="utf-8")) for p in pk])
        salidas["Parakeet TDT 0.6B v3 (alternativo)"] = par[["id", "texto", "segundos", "rtf", "modelo"]]
    return salidas


def evaluar(ref, salidas, metrica, por="tipo"):
    """Métrica agregada por modelo (y por grupo) sobre los MISMOS casos de la muestra.
    Devuelve (resumen, detalle por caso). Un modelo al que le falta algún caso no se evalúa."""
    filas, detalle = [], []
    for modelo, s in salidas.items():
        d = ref.merge(s, on="id", how="left")
        if d["texto"].isna().any():
            filas.append({"modelo": modelo, "grupo": "TODOS", "metrica": metrica, "valor": None,
                          "nota": f"faltan {d['texto'].isna().sum()} casos: no se evalúa"})
            continue
        d[metrica] = por_caso(d, "texto_referencia", "texto", metrica)
        d["modelo"] = modelo
        detalle.append(d)
        filas.append({"modelo": modelo, "grupo": "TODOS", "metrica": metrica,
                      "valor": tasa(d["texto_referencia"], d["texto"], metrica), "nota": ""})
        for g, dg in d.groupby(por):
            filas.append({"modelo": modelo, "grupo": g, "metrica": metrica,
                          "valor": tasa(dg["texto_referencia"], dg["texto"], metrica), "nota": f"{len(dg)} casos"})
    return pd.DataFrame(filas), (pd.concat(detalle) if detalle else pd.DataFrame())
