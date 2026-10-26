"""Versiones .xlsx de los archivos de revisión de la seudonimización (para abrirlos en Excel sin
problemas de separador). Agrega una columna "revision" vacía. Todo queda en datos/raw/ (fuera de Git:
contiene nombres reales).

    .venv/Scripts/python.exe src/hojas_revision.py
"""
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font

RAW = Path(__file__).resolve().parents[1] / "datos" / "raw"


def guardar(df, ruta, anchos, revision=True):
    df = df.assign(revision="") if revision else df
    with pd.ExcelWriter(ruta, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="revision")
        hoja = w.sheets["revision"]
        hoja.freeze_panes = "A2"
        for i, col in enumerate(df.columns, start=1):
            letra = hoja.cell(row=1, column=i).column_letter
            hoja.column_dimensions[letra].width = anchos.get(col, 14)
            hoja.cell(row=1, column=i).font = Font(bold=True)
            for celda in hoja[letra][1:]:
                celda.alignment = Alignment(wrap_text=True, vertical="top")
    print(ruta.name, len(df), "filas")


def main():
    det = pd.read_csv(RAW / "revision_seudonimizacion.csv")
    det = det[~det["id"].str.endswith("_plano")]  # el texto plano usa el mismo mapeo: no se revisa dos veces
    seud = pd.read_csv(RAW / "seudonimos.csv").drop_duplicates("nombre")
    det = det.merge(seud, left_on="entidad", right_on="nombre", how="left").drop(columns="nombre")
    guardar(det, RAW / "revision_seudonimizacion.xlsx", {"entidad": 40, "seudonimo": 16, "revision": 18})

    ocr = pd.read_csv(RAW / "documentos" / "ocr_seudonimizado.csv")[["id", "tipo", "texto_ocr"]]
    guardar(ocr, RAW / "documentos" / "ocr_seudonimizado.xlsx", {"texto_ocr": 120, "revision": 40})

    asr = pd.read_csv(RAW / "audio" / "asr_seudonimizado.csv")[["id", "condicion", "texto_asr_seud"]]
    guardar(asr, RAW / "audio" / "asr_seudonimizado.xlsx", {"texto_asr_seud": 120, "revision": 40})


if __name__ == "__main__":
    main()
