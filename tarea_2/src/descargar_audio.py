"""Descarga el corpus de audio de la tarea 2 y registra fuente y licencia de cada archivo.

    .venv/Scripts/python.exe src/descargar_audio.py

Qué baja a datos/raw/audio/ (no se versiona en Git):

- originales/: los archivos tal como están en Wikimedia Commons (ogg, wav, opus, webm).
- openslr73/: frases de español peruano leído de OpenSLR 73 (Google, CC BY-SA 4.0).
  Se leen por partes (HTTP Range) para no bajar los zips de ~1 GB completos.
- descargas.csv: una fila por archivo con autor, licencia, URL, fecha y SHA-1.

Todas las licencias se verificaron el 22/10/2026 con la API de Commons (campo
LicenseShortName) y en https://www.openslr.org/73/. Entre solicitudes se espera 2 s.

La clase ZipRemoto y la idea de leer OpenSLR por partes vienen de `datos.py` de la
Sesión 13 del curso (https://github.com/d2cml-ai/Data-Science-Python, MIT License,
Copyright (c) 2025 d2cml-ai).
"""
import hashlib
import io
import random
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "datos" / "raw" / "audio"
UA = {"User-Agent": "QLAB-tarea2/0.1 (https://github.com/AntonioMacedo17/Python_Intermedio_2026; proyecto academico)"}
PAUSA = 2.0
API = "https://commons.wikimedia.org/w/api.php?"

# (título en Commons, condición de grabación, idioma, nota)
# Condición: sirve después para elegir la muestra de evaluación por estratos.
COMMONS = [
    ("Entrevista 1 en la Av. Rivagüero - El Agustino.ogg", "calle", "es", ""),
    ("Entrevista 2 en la Av. Rivagüero - El Agustino.ogg", "calle", "es", "2 entrevistadas: multihablante"),
    ("Entrevista en el medio tiempo.opus", "calle", "es", ""),
    ("Entrevista-Aurora Coronado-organización de mujeres indígenas-fiestas patrias.ogg", "evento_publico", "es", ""),
    ("Entrevista a Luz Merida-Organización de mujeres indígenas-fiestas patrias-protesta.ogg", "evento_publico", "es", ""),
    ("Entrevista 1,.wav", "evento_publico", "es", ""),
    ("Entrevista 2.wav", "evento_publico", "es", ""),
    ("Entrevista 3.wav", "evento_publico", "es", ""),
    ("Entrevista 4.wav", "evento_publico", "es", ""),
    ("Entrevista a la señora Aurelia, mujer shuyasina.ogg", "fiesta_patronal", "es", ""),
    ("Entrevista a la señora Dina Espinoza, mujer pomabambina.ogg", "fiesta_patronal", "es", ""),
    ("Entrevista a María Romero, organizadora de la fiesta patronal de Tayta Palli de Chuyas.ogg",
     "fiesta_patronal", "es", ""),
    ("UNMSM Entrevista realizada en la marcha por Cristopher Serrano Pérez.wav", "marcha", "es", ""),
    ("UNMSM Entrevistas en la marcha 1 por Cristopher Serrano Pérez.wav", "marcha", "es", ""),
    ("Audio de la entrevista a una chica que participaba de la marcha.ogg", "marcha", "es", ""),
    # Mismas grabaciones subidas en otro formato: se bajan A PROPÓSITO para probar la limpieza
    # (el hash no las detecta porque los bytes son distintos; la duración y el contenido sí).
    ("UNMSM Entrevistas en la marcha 1 VIDEO por Cristopher Serrano Pérez.ogg", "marcha", "es",
     "posible duplicado en otro formato"),
    ("UNMSM Entrevistas en la marcha 2 VIDEO por Cristopher Serrano Pérez.ogg", "marcha", "es",
     "posible duplicado en otro formato"),
    # Quechua de Huaylas: solo para la bonificación con MMS, NO cuenta para los 30 min en español.
    ("Elena Figueroa - Entrevista sobre Españolada, Shansha, Áncash, Perú.ogg", "quechua", "qwh",
     "bonificación MMS; fuera del corpus en español"),
]

OPENSLR73 = "https://www.openslr.org/resources/73/es_pe_{sexo}.zip"


def _get(url, rango=None, intentos=4):
    cab = dict(UA)
    if rango:
        cab["Range"] = f"bytes={rango[0]}-{rango[1]}"
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == intentos - 1:
                raise
            time.sleep(int(e.headers.get("Retry-After", 30)))


def _api(**params):
    time.sleep(PAUSA)
    import json
    return json.loads(_get(API + urllib.parse.urlencode({"format": "json", **params})))


def bajar_commons():
    carpeta = DESTINO / "originales"
    carpeta.mkdir(parents=True, exist_ok=True)
    filas = []
    for titulo, condicion, idioma, nota in COMMONS:
        info = _api(action="query", titles="File:" + titulo, prop="imageinfo",
                    iiprop="url|sha1|size|extmetadata",
                    iiextmetadatafilter="LicenseShortName|Artist|DateTimeOriginal")
        pagina = next(iter(info["query"]["pages"].values()))
        ii = pagina["imageinfo"][0]
        meta = {k: v.get("value", "") for k, v in ii["extmetadata"].items()}
        local = carpeta / (hashlib.md5(titulo.encode()).hexdigest()[:10] + Path(titulo).suffix)
        if not local.exists():
            time.sleep(PAUSA)
            local.write_bytes(_get(ii["url"]))
        sha1 = hashlib.sha1(local.read_bytes()).hexdigest()
        if sha1 != ii["sha1"]:
            raise ValueError(f"SHA-1 distinto al de Commons: {titulo}")
        filas.append({
            "origen": "Wikimedia Commons", "titulo_original": titulo, "archivo_original": str(local.relative_to(RAIZ)),
            "fuente_url": ii["descriptionurl"], "licencia": meta.get("LicenseShortName", ""),
            "autor": pd.Series([meta.get("Artist", "")]).str.replace(r"<[^>]+>", "", regex=True)[0].strip(),
            "fecha_grabacion": meta.get("DateTimeOriginal", "")[:10], "condicion": condicion, "idioma": idioma,
            "duracion_commons_seg": ii.get("duration"), "sha1": sha1, "nota": nota,
            "texto_oficial": "",
        })
        print(f"ok  {titulo[:70]}")
    return filas


class ZipRemoto(io.RawIOBase):
    """Archivo remoto que se lee por partes (HTTP Range): zipfile solo pide los bytes que necesita.
    Adaptado de datos.py (Sesión 13, MIT)."""

    BLOQUE = 1 << 20

    def __init__(self, url):
        self.url, self.pos, self.buf_ini, self.buf = url, 0, 0, b""
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA, method="HEAD"), timeout=60) as r:
            self.size = int(r.headers["Content-Length"])

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = {0: offset, 1: self.pos + offset, 2: self.size + offset}[whence]
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        fin = self.pos + n
        if not (self.buf_ini <= self.pos and fin <= self.buf_ini + len(self.buf)):
            self.buf_ini = self.pos
            self.buf = _get(self.url, (self.pos, min(self.pos + max(n, self.BLOQUE), self.size) - 1))
        datos = self.buf[self.pos - self.buf_ini:fin - self.buf_ini]
        self.pos += len(datos)
        return datos


def bajar_openslr73(n_por_sexo=10, semilla=2026):
    """Una frase por hablante (6 a 20 palabras), hablantes elegidos al azar con semilla fija.
    Se guarda también la transcripción oficial del dataset (texto_oficial): NO es la referencia
    manual de la tarea; solo sirve para contrastar la referencia que escribe el estudiante."""
    carpeta = DESTINO / "openslr73"
    carpeta.mkdir(parents=True, exist_ok=True)
    filas = []
    for sexo in ["female", "male"]:
        url = OPENSLR73.format(sexo=sexo)
        z = zipfile.ZipFile(ZipRemoto(url))
        lineas = z.read("line_index.tsv").decode("utf-8").strip().splitlines()
        tabla = pd.DataFrame([l.split("\t") for l in lineas], columns=["id", "texto"])
        tabla["hablante"] = tabla["id"].str.rsplit("_", n=1).str[0]
        tabla = tabla[tabla["texto"].str.split().str.len().between(6, 20)]
        hablantes = sorted(tabla["hablante"].unique())
        random.Random(semilla).shuffle(hablantes)
        for h in hablantes[:n_por_sexo]:
            fila = tabla[tabla["hablante"] == h].sample(1, random_state=semilla).iloc[0]
            local = carpeta / f"{fila['id']}.wav"
            if not local.exists():
                local.write_bytes(z.read(f"{fila['id']}.wav"))
            filas.append({
                "origen": "OpenSLR 73", "titulo_original": f"{fila['id']}.wav (es_pe_{sexo}.zip)",
                "archivo_original": str(local.relative_to(RAIZ)), "fuente_url": "https://www.openslr.org/73/",
                "licencia": "CC BY-SA 4.0", "autor": "Google (Guevara-Rukoz et al., 2020)",
                "fecha_grabacion": "", "condicion": "leido_estudio", "idioma": "es",
                "duracion_commons_seg": None, "sha1": hashlib.sha1(local.read_bytes()).hexdigest(),
                "nota": f"hablante {h}", "texto_oficial": fila["texto"].strip(),
            })
        print(f"ok  OpenSLR 73 {sexo}: {n_por_sexo} frases")
    return filas


if __name__ == "__main__":
    DESTINO.mkdir(parents=True, exist_ok=True)
    tabla = pd.DataFrame(bajar_commons() + bajar_openslr73())
    tabla["fecha_extraccion"] = date.today().isoformat()
    tabla.to_csv(DESTINO / "descargas.csv", index=False)
    print(tabla.groupby("origen").size())
