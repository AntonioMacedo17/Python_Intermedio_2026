"""Arma datos/fuentes.csv (fuente, licencia y forma de recuperar cada archivo del corpus).

    .venv/Scripts/python.exe src/armar_fuentes.py

Los ids siguen el mismo orden que procesar_audio.py (clip_###, qwh_###) y que el OCR (doc_###).
Atribución: la licencia CC BY-SA 4.0 permite atribuir con un enlace a la página que reúne autor
y licencia (sección 3(a)(2)); por eso aquí va la URL de Commons y no se repiten nombres de personas.
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"


def main():
    audio = pd.read_csv(RAW / "audio" / "descargas.csv")
    es = audio[audio["idioma"] == "es"].reset_index(drop=True)
    es["id"] = [f"clip_{i:03d}" for i in range(1, len(es) + 1)]
    qu = audio[audio["idioma"] != "es"].reset_index(drop=True)
    qu["id"] = [f"qwh_{i:03d}" for i in range(1, len(qu) + 1)]
    audio = pd.concat([es, qu], ignore_index=True)
    audio["modalidad"] = "audio"
    audio["acceso"] = audio["origen"].map({
        "Wikimedia Commons": "Descarga directa desde Commons con src/descargar_audio.py (verifica SHA-1)",
        "OpenSLR 73": "Lectura parcial (HTTP Range) del zip de OpenSLR 73 con src/descargar_audio.py"})

    docs = pd.read_csv(RAW / "documentos" / "descargas.csv").reset_index(drop=True)
    docs["id"] = [f"doc_{i:03d}" for i in range(1, len(docs) + 1)]
    docs["modalidad"] = "documento"
    docs["acceso"] = [
        "Miniatura oficial de Commons con src/descargar_documentos.py"
        + (f" (página {int(p)} del PDF)" if pd.notna(p) else "") for p in docs["pagina_pdf"]]

    cols = ["id", "modalidad", "fuente_url", "licencia", "acceso", "origen", "fecha_extraccion", "nota"]
    fuentes = pd.concat([docs[cols], audio[cols]], ignore_index=True)
    fuentes.to_csv(RAIZ / "datos" / "fuentes.csv", index=False)
    print(fuentes.groupby(["modalidad", "licencia"]).size())


if __name__ == "__main__":
    main()
