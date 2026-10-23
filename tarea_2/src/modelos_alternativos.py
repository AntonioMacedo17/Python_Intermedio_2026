"""Modelos alternativos de la Parte 2, sobre todo el corpus (configuración de modelos/config_evaluacion.json).

    .venv/Scripts/python.exe src/modelos_alternativos.py tesseract
    .venv/Scripts/python.exe src/modelos_alternativos.py parakeet

- tesseract: Tesseract 5.4.0, lang='spa' (tessdata oficial en modelos/tessdata), --oem 3 --psm 3, sin preproceso.
- parakeet: Parakeet TDT 0.6B v3 vía voz.Transcriptor, CPU, tramos de voz por VAD (0,3 s, máx. 12 s).
  Primero procesa los clips de la muestra de evaluación y luego el resto.

Los dos reanudan: un archivo ya procesado no se repite. Salidas en datos/raw/alternativos/ (fuera de Git:
sin seudonimizar). Se mide el tiempo de proceso de cada archivo sin contar la carga del modelo.
"""
import json
import sys
import time
from pathlib import Path

import torch  # noqa: F401  (antes que cualquier librería que cargue paddle)
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"
SALIDA = RAW / "alternativos"
TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
CONFIG_TESS = "--oem 3 --psm 3"


def tesseract():
    import pytesseract
    from PIL import Image
    pytesseract.pytesseract.tesseract_cmd = TESSERACT
    version = str(pytesseract.get_tesseract_version())
    carpeta = SALIDA / "tesseract"
    carpeta.mkdir(parents=True, exist_ok=True)
    docs = pd.read_csv(RAW / "documentos" / "descargas.csv").reset_index(drop=True)
    docs["id"] = [f"doc_{i:03d}" for i in range(1, len(docs) + 1)]
    for f in docs.itertuples():
        destino = carpeta / f"{f.id}.json"
        if destino.exists():
            continue
        img = Image.open(RAIZ / f.archivo_original).convert("RGB")
        t0 = time.perf_counter()
        texto = pytesseract.image_to_string(
            img, lang="spa", config=f'{CONFIG_TESS} --tessdata-dir "{RAIZ / "modelos" / "tessdata"}"')
        seg = time.perf_counter() - t0
        destino.write_text(json.dumps({"id": f.id, "texto": texto, "segundos": round(seg, 2),
                                       "modelo": f"Tesseract {version} (spa, {CONFIG_TESS})"}, ensure_ascii=False),
                           encoding="utf-8")
        print(f"{f.id} {f.tipo:10s} {len(texto):5d} caracteres  {seg:5.1f}s", flush=True)


def parakeet():
    import voz
    carpeta = SALIDA / "parakeet"
    carpeta.mkdir(parents=True, exist_ok=True)
    clips = pd.read_csv(RAW / "audio" / "limpieza.csv")
    clips = clips[clips["id"].str.startswith("clip_") & ~clips["descartado"]]
    muestra = pd.read_csv(RAIZ / "datos" / "muestra_evaluacion_audio.csv")["id"].tolist()
    orden = muestra + [i for i in clips["id"] if i not in muestra]
    t = None
    for cid in orden:
        destino = carpeta / f"{cid}.json"
        if destino.exists():
            continue
        if t is None:
            t = voz.Transcriptor("parakeet-v3", device="cpu")
            print(f"{t} cargado en {t.segundos_carga:.1f} s", flush=True)
        x = voz.cargar_audio(RAW / "audio" / "clips" / f"{cid}.wav")
        t0 = time.perf_counter()
        segs = t.segmentos(x)
        seg = time.perf_counter() - t0
        dur = len(x) / voz.SR
        destino.write_text(json.dumps({"id": cid, "texto": " ".join(s.texto for s in segs),
                                       "segmentos": [[s.inicio, s.fin, s.texto] for s in segs],
                                       "segundos": round(seg, 2), "duracion_seg": round(dur, 2),
                                       "rtf": round(seg / dur, 3), "modelo": "Parakeet TDT 0.6B v3 (CPU, VAD 0,3 s)",
                                       "en_muestra": cid in muestra}, ensure_ascii=False), encoding="utf-8")
        print(f"{cid} {'[muestra]' if cid in muestra else '         '} {dur:6.1f}s  RTF {seg / dur:.2f}", flush=True)


if __name__ == "__main__":
    {"tesseract": tesseract, "parakeet": parakeet}[sys.argv[1]]()
