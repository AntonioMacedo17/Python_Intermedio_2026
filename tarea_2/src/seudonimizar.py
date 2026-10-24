"""Seudonimización de los textos de OCR y ASR, con conteo de reemplazos.

    .venv/Scripts/python.exe src/seudonimizar.py

Tres capas (de más segura a más amplia):
1. Lista de nombres conocidos (títulos y descripciones de Commons), con comparación difusa
   (voz.seudonimizar, rapidfuzz >= 80): atrapa nombres aunque el OCR/ASR los escriba mal.
   La lista vive en datos/raw/nombres_conocidos.txt (fuera de Git: contiene nombres reales).
2. NER: mrm8488/bert-spanish-cased-finetuned-ner, entidades PER con score >= 0,5
   (umbral bajo a propósito: preferimos tapar de más que dejar un nombre).
3. Expresiones regulares: DNI (8 dígitos), RUC (11 dígitos que empiezan en 10/20),
   celulares peruanos (9 dígitos que empiezan en 9) y correos.

Cada persona recibe un seudónimo estable [PERSONA_###]; la tabla nombre -> seudónimo se guarda
en datos/raw/seudonimos.csv (fuera de Git). El procedimiento automático NO reemplaza la revisión
humana: datos/raw/revision_seudonimizacion.csv lista cada detección con su contexto.

Salidas: datos/raw/documentos/ocr_seudonimizado.csv y datos/raw/audio/asr_seudonimizado.csv,
con las columnas de conteo n_reemplazos_* por documento/clip.
"""
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import torch  # noqa: F401,E402  (torch antes que cualquier cosa de paddle, por si acaso)
import voz  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "datos" / "raw"
MODELO_NER = "mrm8488/bert-spanish-cased-finetuned-ner"
UMBRAL_NER = 0.5
PATRONES = {
    "dni": r"\b\d{8}\b",
    "ruc": r"\b(?:10|20)\d{9}\b",
    "celular": r"\b9\d{2}[ -]?\d{3}[ -]?\d{3}\b",
    "correo": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
}
# Palabras que el NER suele confundir con personas en documentos legales antiguos.
NO_PERSONAS = {"art", "artículo", "congreso", "nación", "república", "constitución", "dios", "señor", "señora",
               "presidente", "lima", "perú", "estado", "título", "don", "doña", "sr", "sra", "dr"}


def clave(nombre):
    s = unicodedata.normalize("NFKD", nombre.lower())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def pedazos(texto, max_palabras=120):
    """Divide el texto en tramos (inicio, fin) de hasta max_palabras palabras, cortando en espacios,
    para no pasar del límite de 512 piezas de BERT. Devuelve posiciones del texto original."""
    palabras = [m.span() for m in re.finditer(r"\S+", texto)]
    for i in range(0, len(palabras), max_palabras):
        grupo = palabras[i:i + max_palabras]
        yield grupo[0][0], grupo[-1][1]


class Seudonimizador:
    def __init__(self, conocidos):
        from transformers import pipeline
        self.ner = pipeline("ner", model=MODELO_NER, aggregation_strategy="simple", device="cpu")
        self.tabla = {}  # clave(nombre) -> (nombre visto, seudónimo)
        self.conocidos = sorted(conocidos, key=len, reverse=True)
        self.detecciones = []

    def seudonimo(self, nombre):
        k = clave(nombre)
        if k not in self.tabla:
            self.tabla[k] = (nombre, f"[PERSONA_{len(self.tabla) + 1:03d}]")
        return self.tabla[k][1]

    def tramos_ner(self, texto):
        """Posiciones (inicio, fin) de personas en el texto ORIGINAL. Se usan los offsets del modelo,
        no la palabra reconstruida (que puede diferir del original en espacios o tildes)."""
        tramos = []
        for a, b in pedazos(texto):
            for e in self.ner(texto[a:b]):
                ini, fin = a + e["start"], a + e["end"]
                w = texto[ini:fin].strip(" .,;:")
                if e["entity_group"] == "PER" and e["score"] >= UMBRAL_NER and len(w) >= 3 \
                        and re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", w) and clave(w) not in NO_PERSONAS:
                    tramos.append((ini, fin))
        return tramos

    def aplicar(self, id_, texto):
        if not isinstance(texto, str) or not texto.strip():
            return texto, {"n_reemplazos_lista": 0, "n_reemplazos_ner": 0, "n_reemplazos_regex": 0}
        conteo = {"n_reemplazos_lista": 0, "n_reemplazos_ner": 0, "n_reemplazos_regex": 0}
        salida = texto
        # 1. lista conocida, difusa
        for nombre in self.conocidos:
            # marca provisoria: el seudónimo definitivo se crea solo si el nombre de verdad aparece
            salida = voz.seudonimizar(salida, {nombre: "[PROVISORIO]"})
            n = salida.count("[PROVISORIO]")
            if n:
                salida = salida.replace("[PROVISORIO]", self.seudonimo(nombre))
                conteo["n_reemplazos_lista"] += n
                self.detecciones.append({"id": id_, "capa": "lista", "entidad": nombre, "veces": n})
        # 2. NER sobre lo que queda (reemplazo por posiciones, de atrás hacia adelante)
        limite = len(salida) + 1
        for ini, fin in sorted(self.tramos_ner(salida), reverse=True):
            nombre = salida[ini:fin]
            if "[PERSONA_" in nombre or fin > limite:  # ya seudonimizado o se superpone con otro tramo
                continue
            limite = ini
            salida = salida[:ini] + self.seudonimo(nombre) + salida[fin:]
            conteo["n_reemplazos_ner"] += 1
            self.detecciones.append({"id": id_, "capa": "ner", "entidad": nombre, "veces": 1})
        # 3. números y correos
        for tipo, patron in PATRONES.items():
            salida, n = re.subn(patron, f"[{tipo.upper()}]", salida)
            if n:
                conteo["n_reemplazos_regex"] += n
                self.detecciones.append({"id": id_, "capa": f"regex_{tipo}", "entidad": "(número/correo)", "veces": n})
        return salida, conteo


def main():
    conocidos = [l.strip() for l in (RAW / "nombres_conocidos.txt").read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.startswith("#")]
    s = Seudonimizador(conocidos)

    ocr = pd.read_csv(RAW / "documentos" / "ocr_crudo.csv")
    filas = []
    for f in ocr.itertuples():
        texto, c = s.aplicar(f.id, f.texto_ocr_crudo)
        filas.append({"id": f.id, "texto_ocr": texto, **c})
    ocr.merge(pd.DataFrame(filas), on="id").to_csv(RAW / "documentos" / "ocr_seudonimizado.csv", index=False)

    asr = pd.read_csv(RAW / "audio" / "asr_crudo.csv")
    asr = asr[(asr["idioma"] == "es") & ~asr["descartado"]]
    filas = []
    for f in asr.itertuples():
        texto, c = s.aplicar(f.id, f.texto_asr)
        plano, _ = s.aplicar(f.id + "_plano", f.texto_plano)  # mismo mapeo; no se cuenta dos veces
        filas.append({"id": f.id, "texto_asr_seud": texto, "texto_plano_seud": plano, **c})
    asr.merge(pd.DataFrame(filas), on="id").to_csv(RAW / "audio" / "asr_seudonimizado.csv", index=False)

    pd.DataFrame([{"nombre": v[0], "seudonimo": v[1]} for v in s.tabla.values()]).to_csv(
        RAW / "seudonimos.csv", index=False)
    pd.DataFrame(s.detecciones).to_csv(RAW / "revision_seudonimizacion.csv", index=False)
    print("personas distintas:", len(s.tabla))
    det = pd.DataFrame(s.detecciones)
    det = det[~det["id"].str.endswith("_plano")]
    print(det.groupby("capa")["veces"].sum().to_string())


if __name__ == "__main__":
    main()
