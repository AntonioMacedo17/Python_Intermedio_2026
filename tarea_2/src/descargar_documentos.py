"""Descarga los documentos de Wikimedia Commons de la tarea 2 y registra fuente y licencia.

    .venv/Scripts/python.exe src/descargar_documentos.py

Guarda en datos/raw/documentos/originales/ (no se versiona) y escribe
datos/raw/documentos/descargas.csv con autor, licencia, URL, fecha y SHA-1 de cada archivo.

Cada candidato se revisó a ojo (miniatura) y su licencia se leyó con la API de Commons
(LicenseShortName) el 22/10/2026. Criterio de tipo (decidido antes del OCR):
- impreso: texto impreso escaneado o digital, de frente y sin sombras.
- foto: documento fotografiado con cámara (reflejos, sombra, inclinación, vitrina).
- manuscrito: la información principal está escrita a mano (aunque esté fotografiada).
En los PDF se toman las páginas 5 y 10, fijadas antes de verlas (no se eligen "las que salen bien").
Las capturas propias del estudiante se agregan aparte (ver trabajo_manual/).
"""
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "datos" / "raw" / "documentos"
UA = {"User-Agent": "QLAB-tarea2/0.1 (https://github.com/AntonioMacedo17/Python_Intermedio_2026; proyecto academico)"}
PAUSA = 2.0
ANCHO_MAX = 2500  # las fotos de 6000 px se bajan a 2500 px de ancho (miniatura oficial de Commons)

# (título en Commons, tipo, página del PDF o None, nota)
DOCUMENTOS = [
    ("Acta de Creación de los Símbolos para el Distrito de Mache.jpg", "impreso", None, "resolución municipal 2016"),
    ("Carta de agradecimiento del secretario de la Presidencia de la República Nazario Chávez Aliaga al pintor "
     "Segundo Ciro Gallardo Gallo en nombre del presidente Manuel Prado Ugarteche.jpg", "impreso", None, "carta 1956"),
    ("Constitución Política de la República Peruana (1828).pdf", "impreso", 5, ""),
    ("Constitución Política de la República Peruana (1828).pdf", "impreso", 10, ""),
    ("Constitución Política del Perú (1856).pdf", "impreso", 5, ""),
    ("Constitución Política del Perú (1856).pdf", "impreso", 10, ""),
    ("Constitución política del Perú reformada por el Congreso de 1860.pdf", "impreso", 5, ""),
    ("Constitución política del Perú reformada por el Congreso de 1860.pdf", "impreso", 10, ""),
    ("Canciller inaugura exposición del centenario del retorno de Tarata al Perú.jpg", "foto", None, "vitrina, reflejos"),
    ("Canciller inaugura exposición del centenario del retorno de Tarata al Perú - 54778280176.jpg", "foto", None,
     "vitrina, reflejos"),
    ("Estado General de Miguel Grau.jpg", "foto", None, "marco con vidrio; formulario impreso con llenado a mano"),
    ("Libro de Bautismos en la Gran Villa de Lampa 1655-1722.jpg", "foto", None, "portada impresa, reflejo de flash"),
    ("Carta de Grau a viuda de Prat en monumento chileno.JPG", "foto", None, "placa grabada (monumento en Chile)"),
    ("Libro de Bautismos en la Gran Villa de Lampa 1871.jpg", "manuscrito", None, "sombra del fotógrafo"),
    ("Libro de Bautismos en la Gran Villa de Lampa 1832.jpg", "manuscrito", None, "caligrafía antigua"),
    ("Miguel Grau - Brev.jpg", "manuscrito", None, "carta de 1879"),
    ("Asiento de la partida de bautismo de Raúl Porras Barrenechea.jpg", "manuscrito", None, "fotocopia certificada"),
    ("Peruvian Telephone Company receipt Lima 1895.JPG", "manuscrito", None, "formulario impreso, llenado a mano"),
    ("Targheta.jpg", "manuscrito", None, "tarjeta de circulación 1921, llenado a mano"),
]


def _get(url, intentos=4):
    for i in range(intentos):
        time.sleep(PAUSA)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == intentos - 1:
                raise
            time.sleep(int(e.headers.get("Retry-After", 30)))


def main():
    (DESTINO / "originales").mkdir(parents=True, exist_ok=True)
    filas = []
    for titulo, tipo, pagina, nota in DOCUMENTOS:
        params = dict(action="query", format="json", titles="File:" + titulo, prop="imageinfo",
                      iiprop="url|sha1|size|extmetadata", iiextmetadatafilter="LicenseShortName|Artist|DateTimeOriginal")
        if pagina:
            params |= dict(iiurlwidth=1800, iiurlparam=f"page{pagina}-1800px")
        else:
            params |= dict(iiurlwidth=ANCHO_MAX)
        p = next(iter(json.loads(_get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)))
                      ["query"]["pages"].values()))
        ii = p["imageinfo"][0]
        meta = {k: v.get("value", "") for k, v in ii["extmetadata"].items()}
        # si la imagen es más chica que ANCHO_MAX, Commons devuelve el original como "thumburl"
        url = ii.get("thumburl") or ii["url"]
        clave = hashlib.md5(f"{titulo}|{pagina}".encode()).hexdigest()[:10]
        local = DESTINO / "originales" / f"{clave}.{'png' if url.endswith('.png') else 'jpg'}"
        if not local.exists():
            local.write_bytes(_get(url))
        filas.append({
            "origen": "Wikimedia Commons", "titulo_original": titulo, "pagina_pdf": pagina, "tipo": tipo,
            "archivo_original": str(local.relative_to(RAIZ)).replace("\\", "/"), "fuente_url": ii["descriptionurl"],
            "url_descarga": url, "licencia": meta.get("LicenseShortName", ""),
            "autor": pd.Series([meta.get("Artist", "")]).str.replace(r"<[^>]+>", "", regex=True)[0].strip(),
            "fecha_documento": meta.get("DateTimeOriginal", "")[:10], "ancho_original": ii["width"],
            "alto_original": ii["height"], "sha1_local": hashlib.sha1(local.read_bytes()).hexdigest(), "nota": nota,
        })
        print(f"ok  {tipo:10s} {titulo[:70]} {'p.' + str(pagina) if pagina else ''}")
    tabla = pd.DataFrame(filas)
    tabla["fecha_extraccion"] = date.today().isoformat()
    tabla.to_csv(DESTINO / "descargas.csv", index=False)
    print(tabla.groupby(["tipo", "licencia"]).size())


if __name__ == "__main__":
    main()
