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
MARCADOR = re.compile(r"\[PERSONA_\d{3}\]")
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
    def __init__(self, conocidos, no_son_nombres=()):
        from transformers import pipeline
        self.ner = pipeline("ner", model=MODELO_NER, aggregation_strategy="simple", device="cpu")
        self.tabla = {}  # clave(nombre) -> (nombre visto, seudónimo)
        self.conocidos = sorted(conocidos, key=len, reverse=True)
        self.detecciones = []
        self.no_son_nombres = {clave(x) for x in no_son_nombres}

    def seudonimo(self, nombre):
        k = clave(nombre)
        if k not in self.tabla:
            self.tabla[k] = (nombre, f"[PERSONA_{len(self.tabla) + 1:03d}]")
        return self.tabla[k][1]

    def tramos_ner(self, texto):
        """Posiciones (inicio, fin) de personas en el texto ORIGINAL. Se usan los offsets del modelo,
        no la palabra reconstruida (que puede diferir del original en espacios o tildes)."""
        partes = [(a, b, texto[a:b]) for a, b in pedazos(texto)]
        # Líneas TODO EN MAYÚSCULAS (títulos de OCR): el NER distingue mayúsculas y casi no las reconoce;
        # se le pasan además en "Tipo Título" (misma longitud, así las posiciones siguen valiendo).
        for m in re.finditer(r"[^\n]+", texto):
            letras = [c for c in m.group() if c.isalpha()]
            if len(m.group().split()) >= 2 and letras and sum(c.isupper() for c in letras) / len(letras) > 0.6:
                titulo = m.group().title()
                if len(titulo) == len(m.group()):
                    partes.append((m.start(), m.end(), titulo))
        marcas = [m.span() for m in MARCADOR.finditer(texto)]
        tramos = []
        for a, b, trozo in partes:
            for e in self.ner(trozo):
                ini, fin = a + e["start"], a + e["end"]
                if e["entity_group"] != "PER" or e["score"] < UMBRAL_NER:
                    continue
                # El NER trabaja con pedazos de palabra: se extiende el tramo a palabras completas
                # (si no, "Micaela" queda como "Mic[PERSONA_001]" y se filtran pedazos del nombre).
                while ini > 0 and texto[ini - 1].isalnum():
                    ini -= 1
                while fin < len(texto) and texto[fin].isalnum():
                    fin += 1
                if any(ini < mb and ma < fin for ma, mb in marcas):  # tocaría un seudónimo ya puesto
                    continue
                w = texto[ini:fin].strip(" .,;:")
                if len(w) >= 3 and re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", w) and clave(w) not in NO_PERSONAS \
                        and clave(w) not in self.no_son_nombres:  # revisión humana, sobre la palabra completa
                    tramos.append((ini, fin))
        return tramos

    @staticmethod
    def tramos_difusos(texto, nombre, parecido=None):
        """Como voz.seudonimizar pero sin distinguir tildes ni mayúsculas, y devolviendo posiciones.
        Umbral: 75 para nombres de 2+ palabras (más letras, menos coincidencias por azar) y 80 para
        nombres de una palabra. Ej.: 'BANON GASTILLA' (error de OCR) vs 'Ramón Castilla' = 78,6."""
        from rapidfuzz import fuzz
        palabras = [m.span() for m in re.finditer(r"\w+", texto)]
        n = len(re.findall(r"\w+", nombre))
        parecido = parecido or (75 if n >= 2 else 80)
        objetivo = clave(" ".join(re.findall(r"\w+", nombre)))
        hallados = []
        for j in range(len(palabras) - n + 1):
            ini, fin = palabras[j][0], palabras[j + n - 1][1]
            ventana = clave(" ".join(re.findall(r"\w+", texto[ini:fin])))
            if fuzz.ratio(ventana, objetivo) >= parecido:
                hallados.append((ini, fin))
        return hallados

    def aplicar(self, id_, texto):
        if not isinstance(texto, str) or not texto.strip():
            return texto, {"n_reemplazos_lista": 0, "n_reemplazos_ner": 0, "n_reemplazos_regex": 0}
        conteo = {"n_reemplazos_lista": 0, "n_reemplazos_ner": 0, "n_reemplazos_regex": 0}
        salida = texto
        # 1. lista conocida, difusa
        for nombre in self.conocidos:  # de los más largos a los más cortos
            n, limite = 0, len(salida) + 1
            for ini, fin in sorted(self.tramos_difusos(salida, nombre), reverse=True):
                if fin > limite or any(ini < mb and ma < fin for ma, mb in
                                       (m.span() for m in MARCADOR.finditer(salida))):
                    continue
                limite = ini
                salida = salida[:ini] + self.seudonimo(nombre) + salida[fin:]
                n += 1
            if n:
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
    # Revisión humana (25/10): lo marcado "no_es_nombre" deja de taparse; "duda" se sigue tapando.
    ruta_no = RAW / "no_son_nombres.txt"
    no_son = [l.strip() for l in ruta_no.read_text(encoding="utf-8").splitlines()] if ruta_no.exists() else []
    s = Seudonimizador(conocidos, [x for x in no_son if x])

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

    # Referencias manuales: el estudiante escribió los nombres tal como se oyen. Se publican solo seudonimizadas
    # (mismo mapeo); las métricas usan la versión original (decisión 16).
    for modalidad in ["audio", "documentos"]:
        ruta = RAW / "referencias" / f"referencias_{modalidad}.xlsx"
        if ruta.exists():
            ref = pd.read_excel(ruta)
            ref["texto_referencia"] = [s.aplicar(f"ref_{i}", t)[0] for i, t in zip(ref["id"], ref["texto_referencia"])]
            ref.drop(columns=[c for c in ["archivo_para_escuchar", "notas"] if c in ref]).to_csv(
                RAW / "referencias" / f"referencias_{modalidad}_seud.csv", index=False)

    # Campos que devolvió el LLM: recibió texto seudonimizado, pero de una versión anterior de este proceso
    # (antes de la revisión humana); se pasan otra vez por el mismo procedimiento antes de publicarlos.
    ruta = RAW / "llm" / "extraccion_llm_borrador.csv"
    if ruta.exists():
        ext = pd.read_csv(ruta)
        ext["campos_json"] = [s.aplicar(f"llm_{i}", t)[0] for i, t in zip(ext["id"], ext["campos_json"])]
        ext.to_csv(RAW / "llm" / "extraccion_llm_seud.csv", index=False)

    pd.DataFrame([{"nombre": v[0], "seudonimo": v[1]} for v in s.tabla.values()]).to_csv(
        RAW / "seudonimos.csv", index=False)
    pd.DataFrame(s.detecciones).to_csv(RAW / "revision_seudonimizacion.csv", index=False)
    print("cadenas distintas reemplazadas:", len(s.tabla))
    det = pd.DataFrame(s.detecciones)
    det = det[~det["id"].str.endswith("_plano") & ~det["id"].str.match(r"(ref|llm)_")]
    print(det.groupby("capa")["veces"].sum().to_string())


if __name__ == "__main__":
    main()
