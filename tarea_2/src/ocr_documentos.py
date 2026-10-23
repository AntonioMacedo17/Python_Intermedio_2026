"""OCR de los documentos de la tarea 2 con PaddleOCR (configuración fijada antes de ver métricas).

    .venv/Scripts/python.exe src/ocr_documentos.py

Entrada: datos/raw/documentos/descargas.csv (+ capturas propias cuando existan).
Salidas en datos/raw/documentos/ (fuera de Git: aún sin seudonimizar):
- ocr/<id>.json        respaldo crudo de PaddleOCR (cajas, textos y confianzas)
- ocr/<id>_cajas.jpg   la imagen con las cajas detectadas (para revisar a ojo)
- recortes/<id>/       un recorte por línea detectada
- ocr_crudo.csv        una fila por documento, insumo del notebook 01

Configuración (igual a la Sesión 10 del curso, solo se agrega el idioma):
PaddleOCR 3.7, lang='es', sin clasificar orientación, sin "planchar" la hoja y sin girar
líneas; sin preprocesamiento de la imagen. Es también la línea base de la Parte 2.
"""
import json
import os
import time
from pathlib import Path

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"  # como en la Sesión 10
import torch  # noqa: F401,E402  en Windows torch debe importarse ANTES que paddle (WinError 127)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import paddleocr  # noqa: E402
from paddleocr import PaddleOCR  # noqa: E402
from PIL import Image  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "datos" / "raw" / "documentos"
OPCIONES = dict(lang="es", use_doc_orientation_classify=False, use_doc_unwarping=False,
                use_textline_orientation=False,
                # Arreglo técnico (23/10, antes de cualquier métrica): PaddlePaddle 3.3 en CPU/Windows
                # falla con oneDNN ("ConvertPirAttribute2RuntimeAttribute not support"). Sin oneDNN
                # funciona igual, solo más lento. No cambia el modelo ni sus parámetros.
                enable_mkldnn=False)
CONFIG_OCR = f"PaddleOCR {paddleocr.__version__} (lang=es, sin orientación/unwarping, sin preproceso, oneDNN off)"


def main():
    tabla = pd.read_csv(DOCS / "descargas.csv").reset_index(drop=True)
    tabla["id"] = [f"doc_{i:03d}" for i in range(1, len(tabla) + 1)]
    (DOCS / "ocr").mkdir(exist_ok=True)
    ocr = None  # el modelo se carga solo si falta algún documento
    filas = []
    for f in tabla.itertuples():
        salida_json = DOCS / "ocr" / f"{f.id}.json"
        if salida_json.exists():  # reanudar: el JSON se escribe al final de cada documento
            prev = json.loads(salida_json.read_text(encoding="utf-8"))
            filas.append({"id": f.id, "texto_ocr_crudo": "\n".join(prev["textos"]), "modelo_ocr": prev["config"],
                          "n_lineas": len(prev["textos"]),
                          "confianza_media": round(float(np.mean(prev["confianzas"])), 3) if prev["confianzas"] else None,
                          "segundos_ocr": prev.get("segundos")})
            print(f"{f.id} ya estaba hecho: se reutiliza", flush=True)
            continue
        if ocr is None:
            ocr = PaddleOCR(**OPCIONES)
        t0 = time.perf_counter()
        r = ocr.predict(str(RAIZ / f.archivo_original))[0]
        segundos = time.perf_counter() - t0
        textos, confs = list(r["rec_texts"]), [float(c) for c in r["rec_scores"]]
        cajas = np.asarray(r["rec_boxes"]).reshape(-1, 4).astype(int).tolist()
        r.save_to_img(str(DOCS / "ocr" / f"{f.id}_cajas.jpg"))
        img = Image.open(RAIZ / f.archivo_original).convert("RGB")
        (DOCS / "recortes" / f.id).mkdir(parents=True, exist_ok=True)
        for k, (x0, y0, x1, y1) in enumerate(cajas):
            img.crop((x0, y0, x1, y1)).save(DOCS / "recortes" / f.id / f"linea_{k:03d}.png")
        # el JSON va al final: si existe, el documento quedó completo
        salida_json.write_text(json.dumps({"id": f.id, "config": CONFIG_OCR, "textos": textos, "confianzas": confs,
                                           "cajas_xyxy": cajas, "segundos": round(segundos, 1)}, ensure_ascii=False),
                               encoding="utf-8")
        filas.append({"id": f.id, "texto_ocr_crudo": "\n".join(textos), "modelo_ocr": CONFIG_OCR,
                      "n_lineas": len(textos), "confianza_media": round(float(np.mean(confs)), 3) if confs else None,
                      "segundos_ocr": round(segundos, 1)})
        print(f"{f.id} {f.tipo:10s} {len(textos):4d} líneas  conf {np.mean(confs) if confs else 0:.2f}  "
              f"{segundos:5.1f}s", flush=True)
    tabla.merge(pd.DataFrame(filas), on="id").to_csv(DOCS / "ocr_crudo.csv", index=False)
    print("listo:", DOCS / "ocr_crudo.csv")


if __name__ == "__main__":
    main()
