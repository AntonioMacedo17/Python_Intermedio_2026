"""Respuestas esperadas del BCRP para la evaluación, sacadas DIRECTO de la API oficial (sin usar mcp/server.py).

    uv run evaluacion/verdades_bcrp.py        # desde tarea_4/; escribe evaluacion/verdades_bcrp.csv

Cada cifra guarda la URL de la API (JSON) y la URL de la página web del BCRP donde se puede revisar a mano.
El valor esperado se redondea a los decimales que la propia API declara para la serie (campo "dec"), que son
los que muestra la web. No hay caché: cada corrida vuelve a pedir los datos.
"""
import csv
import sys
import time
from pathlib import Path

import httpx

AQUI = Path(__file__).parent
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series"

# clave, código, frecuencia (para la URL web), periodo en la API, periodo como lo escribe la API, descripción
PEDIDOS = [
    ("tasa_ref_2024_12", "PD04722MM", "mensuales", "2024-12", "Dic.2024",
     "Tasa de referencia de la política monetaria (%), diciembre 2024"),
    ("ipc12m_2026_09", "PN01273PM", "mensuales", "2026-9", "Sep.2026",
     "IPC Lima Metropolitana, variación % 12 meses, setiembre 2026"),
    ("tc_bancario_2026_09", "PN01210PM", "mensuales", "2026-9", "Sep.2026",
     "Tipo de cambio bancario promedio del periodo (S/ por US$), setiembre 2026"),
    ("rin_usd_2025_12", "PN00027MM", "mensuales", "2025-12", "Dic.2025",
     "Reservas internacionales netas (millones US$), diciembre 2025"),
    ("pbi_var_2024", "PM04863AA", "anuales", "2024", "2024",
     "PBI, variación porcentual anual (real), 2024"),
    ("ipc12m_2024_12", "PN01273PM", "mensuales", "2024-12", "Dic.2024",
     "IPC Lima Metropolitana, variación % 12 meses, diciembre 2024"),
]


def pedir(url, intentos=5, espera=2.0):
    """GET con reintentos: la API a veces responde HTML (límite de pedidos) en vez de JSON."""
    ultimo = None
    for i in range(intentos):
        try:
            r = httpx.get(url, timeout=60, headers={"User-Agent": "evaluacion-tarea4/1.0"})
            r.raise_for_status()
            datos = r.json()
            if "periods" in datos:
                return datos
            ultimo = "respuesta sin 'periods'"
        except (httpx.HTTPError, ValueError) as e:
            ultimo = f"{type(e).__name__}: {e}"
        time.sleep(espera * 2 ** i)
    sys.exit(f"ERROR: el BCRP no respondió con datos tras {intentos} intentos ({ultimo}). URL: {url}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    filas = []
    for clave, codigo, frec, periodo, nombre_api, descripcion in PEDIDOS:
        url = f"{API}/{codigo}/json/{periodo}/{periodo}"
        datos = pedir(url)
        periodos = datos["periods"]
        if len(periodos) != 1 or periodos[0]["name"] != nombre_api:
            sys.exit(f"ERROR: {codigo} devolvió periodos inesperados {[p['name'] for p in periodos]} (URL: {url})")
        bruto = periodos[0]["values"][0]
        try:
            valor = float(bruto)
        except ValueError:
            sys.exit(f"ERROR: {codigo} {nombre_api} no tiene dato numérico ({bruto!r}). URL: {url}")
        dec = int(datos["config"]["series"][0].get("dec", 2))
        filas.append({
            "clave": clave, "codigo": codigo, "periodo": nombre_api, "descripcion": descripcion,
            "valor_api": bruto, "decimales_api": dec, "valor": round(valor, dec),
            "nombre_serie": datos["config"]["series"][0]["name"],
            "url_api": url, "url_web": f"{WEB}/{frec}/resultados/{codigo}/html",
            "consultado": time.strftime("%Y-%m-%d %H:%M"),
        })
        print(f"{clave:22s} {codigo} {nombre_api:9s} = {round(valor, dec)}  ({url})")
        time.sleep(1.5)   # pedidos espaciados para no chocar con el límite de la API

    salida = AQUI / "verdades_bcrp.csv"
    with salida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito {salida} ({len(filas)} cifras)")


if __name__ == "__main__":
    main()
