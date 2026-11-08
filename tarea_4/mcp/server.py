"""Servidor MCP del BCRP (Tarea 4). Basado en el proyecto de la Sesión 04; buscar_series viene de la sesión.

    uv run pytest -q                                        # desde tarea_4/: 8 pruebas originales + 2 propias
    uv run mcp/server.py                                    # el servidor, por stdio
    claude mcp add --scope project bcrp -- uv run mcp/server.py   # o usar el .mcp.json de tarea_4/

Herramientas: buscar_series, serie, resumen y correlacion (propia). Recurso: bcrp://serie/{codigo}.
Prompt: informe(tema).

Las cuentas las hace Python, no el modelo: así cada cifra sale de una llamada que se puede repetir.
Las descargas tienen reintentos con espera creciente y una caché en disco (datos/cache_api/, ignorada por git).
"""
import calendar
import hashlib
import json
import math
import re
import time
import unicodedata
from functools import cache
from pathlib import Path

import httpx
import pandas as pd
from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError, ToolError

AQUI = Path(__file__).parent
CATALOGO = AQUI / "datos" / "catalogo_bcrp.csv"
CACHE_API = AQUI / "datos" / "cache_api"
URL_CATALOGO = "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata"
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series"
SOLO_LECTURA = {"readOnlyHint": True, "openWorldHint": True}

REINTENTOS = 4          # intentos por pedido a la API
ESPERA_BASE = 1.5       # segundos; se duplica en cada reintento (1.5, 3, 6)
CACHE_HORAS = 12        # una respuesta guardada se reutiliza durante 12 h (los datos recientes se revisan)

MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8,
         "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12}
WEB_FRECUENCIA = {"diaria": "diarias", "mensual": "mensuales", "trimestral": "trimestrales", "anual": "anuales"}

mcp = FastMCP("bcrp", instructions=(
    "Series oficiales del Banco Central de Reserva del Perú (BCRP). Primero busca el código con buscar_series; "
    "luego usa resumen para variaciones, promedios y extremos, serie para los datos y correlacion para medir "
    "la asociación entre dos series en los mismos periodos. No calcules a mano: cita siempre el código de la "
    "serie, el periodo y la fuente (URL). Si una herramienta falla o no hay datos, dilo en vez de estimar."))


def _sin_tildes(s):
    return unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()


@cache
def catalogo():
    """El catálogo oficial: 17 mil series en unos 7 MB. Se baja una vez y queda en datos/."""
    if not CATALOGO.exists():
        CATALOGO.parent.mkdir(exist_ok=True)
        r = httpx.get(URL_CATALOGO, timeout=120)
        r.raise_for_status()
        CATALOGO.write_text(r.content.decode("latin-1"), encoding="utf-8")
    df = pd.read_csv(CATALOGO, sep=";", dtype=str).fillna("")
    df = df.rename(columns={"Código de serie": "codigo", "Categoría de serie": "categoria", "Grupo de serie": "grupo",
                            "Nombre de serie": "nombre", "Frecuencia": "frecuencia",
                            "Fecha de actualización": "actualizada", "Fecha de inicio": "inicio"})
    df["texto"] = (df.categoria + " " + df.grupo + " " + df.nombre).map(_sin_tildes)
    return df


def _ficha(codigo):
    fila = catalogo().query("codigo == @codigo")
    if fila.empty:
        raise ToolError(f"No existe el código de serie {codigo!r}. Búsquenlo con buscar_series.")
    f = fila.iloc[0]
    return {"codigo": f.codigo, "nombre": f"{f.grupo} - {f.nombre}", "categoria": f.categoria,
            "frecuencia": f.frecuencia, "inicio": f.inicio, "actualizada": f.actualizada}


@mcp.tool(annotations=SOLO_LECTURA)
def buscar_series(texto: str, frecuencia: str | None = None, limite: int = 10) -> list[dict]:
    """Busca series del BCRP por palabras: todas deben aparecer en la categoría, el grupo o el nombre.

    Ejemplos: "ipc 12 meses", "tipo de cambio interbancario venta", "reservas internacionales netas",
    "tasa de referencia", "cobre precio". frecuencia: "Diaria", "Mensual", "Trimestral" o "Anual".
    Devuelve el código, el nombre completo, la frecuencia y desde cuándo hay datos. Si no hay resultados,
    prueben con menos palabras.
    """
    df = catalogo()
    m = pd.Series(True, index=df.index)
    for palabra in _sin_tildes(texto).split():
        m &= df.texto.str.contains(re.escape(palabra))
    if frecuencia:
        m &= df.frecuencia.str.lower() == frecuencia.lower()
    # primero las series vigentes y, entre ellas, las de nombre más corto (las más generales)
    sel = df[m]
    orden = sel.assign(vieja=sel.actualizada < "2025", largo=(sel.grupo + sel.nombre).str.len())
    return [_ficha(c) for c in orden.sort_values(["vieja", "largo"]).head(limite).codigo]


# ---------------------------------------------------------------------------------------------------------------
# Fechas: lo que escribe el usuario -> lo que pide la API; lo que devuelve la API -> periodo normalizado
# ---------------------------------------------------------------------------------------------------------------

def _fecha_api(fecha: str, frecuencia: str, fin: bool = False) -> str:
    """Convierte "2025", "2025-03", "2025-T1" o "2025-03-15" al formato que pide la API según la frecuencia.

    Mensual y trimestral: "2025-3" (mes o trimestre); diaria: "2025-03-15"; anual: "2025".
    Si falta precisión, `fin` decide si se toma el inicio o el final del periodo (p. ej. "2025" -> dic. o 31-dic).
    """
    m = re.fullmatch(r"\s*(\d{4})(?:-(T)?(\d{1,2}))?(?:-(\d{1,2}))?\s*", str(fecha), flags=re.IGNORECASE)
    if not m:
        raise ToolError(f"Fecha {fecha!r} no válida. Usen 2025, 2025-03, 2025-T1 o 2025-03-15.")
    anio, es_trim, parte, dia = int(m[1]), bool(m[2]), m[3], m[4]
    parte = int(parte) if parte else None
    if es_trim and not (parte and 1 <= parte <= 4):
        raise ToolError(f"Trimestre no válido en {fecha!r}: va de T1 a T4.")
    if not es_trim and parte is not None and not 1 <= parte <= 12:
        raise ToolError(f"Mes no válido en {fecha!r}: va de 01 a 12.")
    # mes de referencia (para mensual y diaria)
    if parte is None:
        mes = 12 if fin else 1
    elif es_trim:
        mes = 3 * parte if fin else 3 * parte - 2
    else:
        mes = parte

    f = frecuencia.lower()
    if f == "anual":
        return f"{anio}"
    if f == "mensual":
        return f"{anio}-{mes}"
    if f == "trimestral":
        trim = parte if es_trim else (mes - 1) // 3 + 1
        return f"{anio}-{trim}"
    if f == "diaria":
        ultimo = calendar.monthrange(anio, mes)[1]
        d = int(dia) if dia else (ultimo if fin else 1)
        if not 1 <= d <= ultimo:
            raise ToolError(f"Día no válido en {fecha!r}.")
        return f"{anio}-{mes:02d}-{d:02d}"
    raise ToolError(f"Frecuencia {frecuencia!r} no soportada.")


def _anio_dos_cifras(aa: str) -> int:
    a = int(aa)
    return 2000 + a if a < 50 else 1900 + a


def _periodo(nombre: str, frecuencia: str) -> str:
    """"Ene.2025" -> "2025-01"; "01.Oct.26" -> "2026-10-01"; "T1.25" -> "2025-T1"; "2025" -> "2025"."""
    f = frecuencia.lower()
    try:
        if f == "mensual":
            mes, anio = nombre.split(".")
            return f"{int(anio)}-{MESES[mes.lower()[:3]]:02d}"
        if f == "diaria":
            dia, mes, aa = nombre.split(".")
            return f"{_anio_dos_cifras(aa)}-{MESES[mes.lower()[:3]]:02d}-{int(dia):02d}"
        if f == "trimestral":
            trim, aa = nombre.split(".")
            return f"{_anio_dos_cifras(aa)}-T{int(trim.upper().lstrip('T'))}"
        if f == "anual":
            return str(int(nombre))
    except (ValueError, KeyError):
        pass
    raise ToolError(f"No pude interpretar el periodo {nombre!r} que devolvió el BCRP ({frecuencia}).")


# ---------------------------------------------------------------------------------------------------------------
# Descarga con reintentos y caché
# ---------------------------------------------------------------------------------------------------------------

def _pedir_api(url: str) -> dict:
    """GET a la API del BCRP. Si responde HTML (límite de pedidos o sin datos) reintenta con espera creciente.

    Las respuestas válidas se guardan en datos/cache_api/ y se reutilizan durante CACHE_HORAS.
    """
    archivo = CACHE_API / (hashlib.sha1(url.encode()).hexdigest() + ".json")
    if archivo.exists() and time.time() - archivo.stat().st_mtime < CACHE_HORAS * 3600:
        return json.loads(archivo.read_text(encoding="utf-8"))

    error = None
    for intento in range(REINTENTOS):
        try:
            r = httpx.get(url, timeout=60)
            r.raise_for_status()
            datos = r.json()                      # la API responde text/html incluso con JSON: se intenta leer
            if not isinstance(datos, dict) or "periods" not in datos:
                raise ValueError("respuesta sin 'periods'")
            break
        except (httpx.HTTPError, ValueError) as e:   # ValueError incluye JSONDecodeError (llegó una página HTML)
            error = e
            if intento < REINTENTOS - 1:
                time.sleep(ESPERA_BASE * 2 ** intento)
    else:
        raise ToolError(f"El BCRP no respondió con datos tras {REINTENTOS} intentos ({type(error).__name__}). "
                        f"Puede ser el límite de pedidos o que no haya datos en ese periodo. URL: {url}")

    CACHE_API.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return datos


def _url_web(codigo: str, frecuencia: str) -> str:
    return f"{WEB}/{WEB_FRECUENCIA.get(frecuencia.lower(), 'mensuales')}/resultados/{codigo}/html"


def _serie(codigo: str, desde: str, hasta: str) -> dict:
    codigo = str(codigo).strip().upper()
    ficha = _ficha(codigo)
    fr = ficha["frecuencia"]
    d, h = _fecha_api(desde, fr), _fecha_api(hasta, fr, fin=True)
    url = f"{API}/{codigo}/json/{d}/{h}"
    datos = []
    for p in _pedir_api(url).get("periods", []):
        bruto = (p.get("values") or ["n.d."])[0]
        try:
            valor = float(bruto)
        except (TypeError, ValueError):          # "n.d." y similares: sin dato
            continue
        if math.isnan(valor):
            continue
        datos.append({"periodo": _periodo(p["name"], fr), "valor": round(valor, 6)})
    if not datos:
        raise ToolError(f"La serie {codigo} no tiene datos entre {desde} y {hasta}. "
                        f"Hay datos desde {ficha['inicio']} (actualizada {ficha['actualizada']}).")
    return {"codigo": codigo, "nombre": ficha["nombre"], "frecuencia": fr, "desde": desde, "hasta": hasta,
            "datos": datos, "fuente": url, "consulta_web": _url_web(codigo, fr)}


# ---------------------------------------------------------------------------------------------------------------
# Herramientas
# ---------------------------------------------------------------------------------------------------------------

@mcp.tool(annotations=SOLO_LECTURA)
def serie(codigo: str, desde: str, hasta: str) -> dict:
    """Descarga los datos oficiales de una serie del BCRP entre dos fechas (ambas incluidas).

    Úsala cuando necesiten los valores periodo a periodo. Fechas: "2025-01" (mensual), "2025-T1" o "2025-01"
    (trimestral), "2026-10-01" (diaria), "2025" (anual o todo el año). Ejemplo: codigo="PN01273PM",
    desde="2024-01", hasta="2024-12". Devuelve código, nombre, frecuencia, datos [{periodo, valor}] y la URL
    de la fuente. Los valores "n.d." del BCRP se omiten. Para promedios o variaciones usen resumen.
    """
    return _serie(codigo, desde, hasta)


@mcp.tool(annotations=SOLO_LECTURA)
def resumen(codigo: str, desde: str, hasta: str) -> dict:
    """Resume una serie del BCRP en un periodo: primero, último, cambio, variación %, promedio, máximo y mínimo.

    Úsala siempre que pidan un valor puntual, una variación o un promedio, para no hacer cuentas a mano.
    Ejemplo: codigo="PN01273PM", desde="2025-12", hasta="2026-09". "cambio" está en las unidades de la serie
    (si la serie ya es una tasa en %, el cambio es en puntos porcentuales); "variacion_pct" es la variación
    relativa entre el primer y el último valor (null si el primero es 0).
    """
    s = _serie(codigo, desde, hasta)
    v = pd.Series([x["valor"] for x in s["datos"]], index=[x["periodo"] for x in s["datos"]])
    primero, ultimo = float(v.iloc[0]), float(v.iloc[-1])
    return {
        "codigo": s["codigo"], "nombre": s["nombre"], "frecuencia": s["frecuencia"],
        "periodo": {"desde": v.index[0], "hasta": v.index[-1]}, "n": int(v.size),
        "primero": {"periodo": v.index[0], "valor": round(primero, 4)},
        "ultimo": {"periodo": v.index[-1], "valor": round(ultimo, 4)},
        "cambio": round(ultimo - primero, 4),
        "variacion_pct": round((ultimo / primero - 1) * 100, 4) if primero != 0 else None,
        "promedio": round(float(v.mean()), 4),
        "maximo": {"periodo": v.idxmax(), "valor": round(float(v.max()), 4)},
        "minimo": {"periodo": v.idxmin(), "valor": round(float(v.min()), 4)},
        "fuente": s["fuente"], "consulta_web": s["consulta_web"],
    }


def _lectura(r: float) -> str:
    fuerza = "débil" if abs(r) < 0.3 else "moderada" if abs(r) < 0.7 else "fuerte"
    signo = "positiva" if r > 0 else "negativa" if r < 0 else "nula"
    return f"asociación lineal {signo} {fuerza} (r = {r:.3f})"


@mcp.tool(annotations=SOLO_LECTURA)
def correlacion(codigo_a: str, codigo_b: str, desde: str, hasta: str, en_diferencias: bool = False) -> dict:
    """Mide la asociación entre dos series del BCRP de la misma frecuencia, alineando sus periodos.

    Úsala para preguntas como «¿la inflación se movió junto con la actividad económica entre 2020 y 2024?»:
    por ejemplo codigo_a="PN01273PM" (IPC Lima, var. % 12 meses) y codigo_b="PN01728AM" (PBI, var. %
    interanual), desde="2020-01", hasta="2024-12". Descarga ambas, conserva solo los periodos con dato en las
    dos (informa cuáles se excluyeron) y calcula Pearson y Spearman (Pearson sobre rangos) con pandas. Con en_diferencias=True
    correlaciona los cambios de un periodo al siguiente, útil cuando ambas series tienen tendencia.
    Exige al menos 3 periodos comunes. Es una medida descriptiva: no demuestra causalidad.
    """
    a, b = _serie(codigo_a, desde, hasta), _serie(codigo_b, desde, hasta)
    if a["frecuencia"] != b["frecuencia"]:
        raise ToolError(f"Las series tienen frecuencias distintas: {a['codigo']} es {a['frecuencia']} y "
                        f"{b['codigo']} es {b['frecuencia']}. Elijan dos series de la misma frecuencia "
                        "(búsquenlas con buscar_series y el filtro frecuencia).")
    sa = pd.Series({x["periodo"]: x["valor"] for x in a["datos"]}, name="a")
    sb = pd.Series({x["periodo"]: x["valor"] for x in b["datos"]}, name="b")
    tabla = pd.concat([sa, sb], axis=1).sort_index()
    solo_a = tabla.index[tabla.a.notna() & tabla.b.isna()].tolist()
    solo_b = tabla.index[tabla.b.notna() & tabla.a.isna()].tolist()
    if en_diferencias:              # la diferencia se toma sobre la tabla completa: un hueco no se salta
        tabla = tabla.diff()
    comunes = tabla.dropna()
    if len(comunes) < 3:
        raise ToolError(f"Solo hay {len(comunes)} periodos comunes con dato entre {a['codigo']} y {b['codigo']} "
                        f"de {desde} a {hasta}; se necesitan al menos 3.")
    if comunes.a.std() == 0 or comunes.b.std() == 0:
        constante = a["codigo"] if comunes.a.std() == 0 else b["codigo"]
        raise ToolError(f"La serie {constante} no varía en los periodos comunes: la correlación no está definida.")
    pearson = float(comunes.a.corr(comunes.b))
    rangos = comunes.rank()         # Spearman = Pearson sobre rangos (empates con rango promedio); sin scipy
    spearman = float(rangos.a.corr(rangos.b))
    return {
        "serie_a": {"codigo": a["codigo"], "nombre": a["nombre"], "fuente": a["fuente"]},
        "serie_b": {"codigo": b["codigo"], "nombre": b["nombre"], "fuente": b["fuente"]},
        "frecuencia": a["frecuencia"], "en_diferencias": en_diferencias,
        "periodo_comun": {"desde": comunes.index[0], "hasta": comunes.index[-1]},
        "n_periodos": int(len(comunes)),
        "excluidos": {"solo_en_a": solo_a, "solo_en_b": solo_b},
        "pearson": round(pearson, 4), "spearman": round(spearman, 4),
        "lectura": _lectura(pearson),
        "advertencia": ("Correlación descriptiva entre series agregadas: no implica causalidad. Si ambas series "
                        "tienen tendencia, la correlación en niveles puede ser espuria; comparen con "
                        "en_diferencias=True."),
        "pares": [{"periodo": p, "a": round(float(f.a), 6), "b": round(float(f.b), 6)}
                  for p, f in comunes.iterrows()],
    }


# ---------------------------------------------------------------------------------------------------------------
# Recurso y prompt
# ---------------------------------------------------------------------------------------------------------------

@mcp.resource("bcrp://serie/{codigo}", mime_type="application/json",
              description="Ficha descriptiva de una serie del BCRP: nombre, categoría, frecuencia, desde cuándo "
                          "hay datos, última actualización y enlaces a la API y a la página oficial.")
def ficha_serie(codigo: str) -> str:
    codigo = str(codigo).strip().upper()
    try:
        f = _ficha(codigo)
    except ToolError as e:
        raise ResourceError(str(e)) from e
    ficha = {**f, "api": f"{API}/{codigo}/json/<desde>/<hasta>", "consulta_web": _url_web(codigo, f["frecuencia"]),
             "fuente": "Banco Central de Reserva del Perú, catálogo de series estadísticas " + URL_CATALOGO}
    return json.dumps(ficha, ensure_ascii=False, indent=2)


@mcp.prompt
def informe(tema: str) -> str:
    """Plantilla para un informe breve sobre un indicador del BCRP, con cada cifra citada y verificable."""
    return (
        f"Prepara un informe breve sobre «{tema}» con datos oficiales del BCRP, usando solo el servidor MCP bcrp.\n\n"
        "1. Usa buscar_series para identificar la o las series pertinentes y explica por qué elegiste cada código.\n"
        "2. Usa resumen para el valor más reciente, el cambio, el promedio y los extremos del periodo; usa serie "
        "solo si necesitas los datos periodo a periodo; usa correlacion si el tema relaciona dos indicadores.\n"
        "3. No hagas cuentas a mano: toda cifra debe venir de una herramienta.\n"
        "4. Junto a cada cifra cita el código de serie, el periodo y la fuente (URL de la API o consulta_web).\n"
        "5. Describe asociaciones, no causas. Señala limitaciones (frecuencia, revisiones, periodo cubierto).\n"
        "6. Si una herramienta falla o no hay datos, dilo explícitamente; no estimes ni completes cifras.\n\n"
        "Estructura: (a) pregunta y series usadas, (b) cifras clave en una tabla, (c) interpretación en 3-5 "
        "líneas, (d) fuentes."
    )


if __name__ == "__main__":
    mcp.run()
