"""Arma datos/raw/documentos/corpus_documentos.csv: los documentos de Commons + las capturas propias.

    .venv/Scripts/python.exe src/corpus_documentos.py

- Commons: filas de descargas.csv, con ids doc_001... en el mismo orden (no cambian nunca).
- Capturas propias: las imágenes de datos/raw/documentos/propias/ listadas en
  trabajo_manual/02_capturas_propias.csv. Se copian a originales/ re-guardando SOLO los píxeles,
  así se eliminan los metadatos EXIF (fecha, modelo del celular y ubicación GPS).
  Reciben ids a continuación (doc_020, ...), en el orden de la plantilla.
Los demás scripts (OCR, Tesseract, fuentes, muestra) leen este archivo.
"""
from pathlib import Path

import pandas as pd
from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "datos" / "raw" / "documentos"


def main():
    commons = pd.read_csv(DOCS / "descargas.csv").reset_index(drop=True)
    commons["id"] = [f"doc_{i:03d}" for i in range(1, len(commons) + 1)]
    commons["descartado"] = False
    filas = [commons]

    plantilla = RAIZ / "trabajo_manual" / "02_capturas_propias.csv"
    propias = pd.read_csv(plantilla) if plantilla.exists() else pd.DataFrame()
    nuevas = []
    for f in propias.itertuples():
        origen = DOCS / "propias" / f.archivo
        if not origen.exists():
            continue
        destino = DOCS / "originales" / f"propia_{Path(f.archivo).stem}.jpg"
        img = ImageOps.exif_transpose(Image.open(origen)).convert("RGB")  # respeta la orientación de la foto
        Image.frombytes(img.mode, img.size, img.tobytes()).save(destino, quality=95)  # sin EXIF
        nuevas.append({"origen": "Captura propia", "titulo_original": f.archivo, "pagina_pdf": None, "tipo": f.tipo,
                       "archivo_original": str(destino.relative_to(RAIZ)).replace("\\", "/"),
                       "fuente_url": "captura propia (sin URL pública)",
                       "licencia": "Captura propia del estudiante (uso académico)",
                       "fecha_documento": f.fecha_captura, "nota": f"{f.que_es} | {f.fuente_del_texto}",
                       "fecha_extraccion": f.fecha_captura, "descartado": False})
    if nuevas:
        n0 = len(commons)
        nuevas = pd.DataFrame(nuevas)
        nuevas["id"] = [f"doc_{n0 + i:03d}" for i in range(1, len(nuevas) + 1)]
        filas.append(nuevas)
    corpus = pd.concat(filas, ignore_index=True)
    corpus.to_csv(DOCS / "corpus_documentos.csv", index=False)
    print(corpus.groupby(["origen", "tipo"]).size().to_string())


if __name__ == "__main__":
    main()
