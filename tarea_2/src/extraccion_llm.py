"""Extracción de campos con Gemini sobre texto YA seudonimizado.

    .venv/Scripts/python.exe src/extraccion_llm.py

- Modelo: gemini-2.5-flash, temperature=0, salida JSON con esquema fijo (modelos/config_evaluacion.json).
- Prompt: modelos/prompt_extraccion.txt (fijado antes de la auditoría humana).
- Entrada: datos/raw/documentos/ocr_seudonimizado.csv y datos/raw/audio/asr_seudonimizado.csv.
  Antes de enviar cada texto se verifica que no contenga ningún nombre de la lista conocida.
- Salida: datos/extraccion_llm.csv (id, modalidad, campos_json, modelo_llm, fecha) y respuestas crudas en
  datos/raw/llm/. Reanuda: un id ya respondido no se vuelve a enviar.
- Control automático (no reemplaza la auditoría): cada "cita clave" se busca literalmente en el texto.
"""
import json
import time
import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"
MODELO = "gemini-2.5-flash"
PAUSA = 7.0  # segundos entre llamadas (límite gratuito por minuto)


class CamposDocumento(BaseModel):
    modalidad: str
    tema: str | None
    resumen: str | None
    emisor: str | None
    fecha: str | None
    monto: str | None


class CamposAudio(BaseModel):
    modalidad: str
    tema: str | None
    resumen: str | None
    citas_clave: list[str] | None
    numero_hablantes: int | None


def sin_tildes(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def main():
    load_dotenv(RAIZ / ".env")
    cliente = genai.Client()
    plantilla = (RAIZ / "modelos" / "prompt_extraccion.txt").read_text(encoding="utf-8")
    conocidos = [sin_tildes(l.strip()) for l in (RAW / "nombres_conocidos.txt").read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.startswith("#")]
    docs = pd.read_csv(RAW / "documentos" / "ocr_seudonimizado.csv")[["id", "texto_ocr"]].rename(columns={"texto_ocr": "texto"})
    docs["modalidad"] = "documento"
    aud = pd.read_csv(RAW / "audio" / "asr_seudonimizado.csv")[["id", "texto_asr_seud"]].rename(columns={"texto_asr_seud": "texto"})
    aud["modalidad"] = "audio"
    carpeta = RAW / "llm"
    carpeta.mkdir(exist_ok=True)

    for f in pd.concat([docs, aud]).itertuples():
        destino = carpeta / f"{f.id}.json"
        if destino.exists():
            continue
        texto = f.texto if isinstance(f.texto, str) else ""
        filtrado = [n for n in conocidos if n in sin_tildes(texto)]
        if filtrado:  # nunca debería pasar: la seudonimización ya los quitó
            print(f"{f.id}: NO SE ENVÍA, quedan nombres de la lista sin seudonimizar", flush=True)
            continue
        esquema = CamposDocumento if f.modalidad == "documento" else CamposAudio
        r = cliente.models.generate_content(
            model=MODELO, contents=plantilla.format(modalidad=f.modalidad, texto=texto),
            config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json",
                                               response_schema=esquema))
        campos = json.loads(r.text)
        if f.modalidad == "audio" and campos.get("citas_clave"):
            campos["_citas_literales"] = [c in texto for c in campos["citas_clave"]]
        destino.write_text(json.dumps({"id": f.id, "modalidad": f.modalidad, "campos": campos,
                                       "modelo": f"{MODELO} (temperature=0, JSON con esquema)",
                                       "fecha": date.today().isoformat()}, ensure_ascii=False), encoding="utf-8")
        print(f"{f.id} ok", flush=True)
        time.sleep(PAUSA)

    filas = []
    for p in sorted(carpeta.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        filas.append({"id": d["id"], "modalidad": d["modalidad"],
                      "campos_json": json.dumps(d["campos"], ensure_ascii=False),
                      "modelo_llm": d["modelo"], "fecha": d["fecha"]})
    pd.DataFrame(filas).to_csv(RAW / "llm" / "extraccion_llm_borrador.csv", index=False)
    print("respuestas:", len(filas))


if __name__ == "__main__":
    main()
