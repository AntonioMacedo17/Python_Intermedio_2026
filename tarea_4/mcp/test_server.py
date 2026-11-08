"""El contrato del servidor: si estas pruebas pasan, Claude Code y evaluar.py pueden usarlo.

    uv run pytest -q

Llaman al servidor en memoria, igual que lo haría Claude Code, y piden datos reales al BCRP.
"""
import asyncio

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from server import mcp


async def _con_cliente(f):
    async with Client(mcp) as c:
        return await f(c)


def llamar(herramienta, **args):
    return asyncio.run(_con_cliente(lambda c: c.call_tool(herramienta, args))).data


def test_buscar_encuentra_el_ipc():
    r = llamar("buscar_series", texto="ipc 12 meses", limite=5)
    assert "PN01273PM" in [x["codigo"] for x in r]
    assert {"codigo", "nombre", "frecuencia"} <= r[0].keys()


def test_cuatro_herramientas_como_minimo():
    nombres = {t.name for t in asyncio.run(_con_cliente(lambda c: c.list_tools()))}
    assert {"buscar_series", "serie", "resumen"} <= nombres
    assert len(nombres) >= 4, "falta su herramienta propia"


def test_serie_mensual():
    r = llamar("serie", codigo="PN01271PM", desde="2025-01", hasta="2025-12")
    assert len(r["datos"]) == 12
    assert r["datos"][0]["periodo"] == "2025-01"
    assert r["datos"][2]["valor"] == pytest.approx(0.81, abs=0.01)   # IPC de Lima, marzo de 2025
    assert r["fuente"].startswith("https://estadisticas.bcrp.gob.pe")


def test_serie_diaria():
    r = llamar("serie", codigo="PD04638PD", desde="2026-10-01", hasta="2026-10-15")
    assert r["datos"][0]["periodo"] == "2026-10-01"
    assert r["datos"][-1] == {"periodo": "2026-10-15", "valor": pytest.approx(3.428, abs=0.001)}


def test_resumen_sin_cuentas_a_mano():
    r = llamar("resumen", codigo="PN01273PM", desde="2025-12", hasta="2026-09")
    assert r["primero"]["valor"] == pytest.approx(1.51, abs=0.01)
    assert r["ultimo"]["valor"] == pytest.approx(4.55, abs=0.01)
    assert r["maximo"]["periodo"] == "2026-09"
    assert {"cambio", "variacion_pct", "promedio", "minimo"} <= r.keys()


def test_codigo_inexistente_da_un_error_claro():
    with pytest.raises(ToolError, match="XX999"):
        llamar("serie", codigo="XX999", desde="2025-01", hasta="2025-02")


def test_un_recurso():
    async def contar(c):
        return len(await c.list_resources()) + len(await c.list_resource_templates())
    assert asyncio.run(_con_cliente(contar)) >= 1


def test_un_prompt():
    assert len(asyncio.run(_con_cliente(lambda c: c.list_prompts()))) >= 1


# --- Pruebas propias (Tarea 4): herramienta correlacion. Las 8 de arriba son las originales, sin cambios. ---

def test_correlacion_coincide_con_calculo_independiente():
    """Inflación de Lima (12 meses) contra PBI (var. % interanual), 2020-2024: la herramienta debe dar lo mismo
    que un cálculo hecho aparte con numpy sobre los datos que devuelve `serie`."""
    import numpy as np
    args = dict(desde="2020-01", hasta="2024-12")
    a = {x["periodo"]: x["valor"] for x in llamar("serie", codigo="PN01273PM", **args)["datos"]}
    b = {x["periodo"]: x["valor"] for x in llamar("serie", codigo="PN01728AM", **args)["datos"]}
    comunes = sorted(set(a) & set(b))
    esperado = np.corrcoef([a[p] for p in comunes], [b[p] for p in comunes])[0, 1]

    r = llamar("correlacion", codigo_a="PN01273PM", codigo_b="PN01728AM", **args)
    assert r["n_periodos"] == len(comunes) == 60
    assert r["periodo_comun"] == {"desde": "2020-01", "hasta": "2024-12"}
    assert r["pearson"] == pytest.approx(esperado, abs=1e-4)
    assert -1 <= r["spearman"] <= 1
    assert r["serie_a"]["fuente"].startswith("https://estadisticas.bcrp.gob.pe")
    assert "causalidad" in r["advertencia"]


def test_correlacion_casos_limite():
    """Una serie consigo misma da r = 1; en diferencias se pierde el primer periodo; frecuencias distintas
    dan un error claro en vez de un número sin sentido."""
    r = llamar("correlacion", codigo_a="PN01271PM", codigo_b="PN01271PM", desde="2025-01", hasta="2025-12")
    assert r["pearson"] == pytest.approx(1.0) and r["spearman"] == pytest.approx(1.0)
    assert r["n_periodos"] == 12

    d = llamar("correlacion", codigo_a="PN01271PM", codigo_b="PN01273PM", desde="2025-01", hasta="2025-12",
               en_diferencias=True)
    assert d["n_periodos"] == 11 and d["periodo_comun"]["desde"] == "2025-02"

    with pytest.raises(ToolError, match="frecuencias distintas"):
        llamar("correlacion", codigo_a="PN01273PM", codigo_b="PD04638PD", desde="2025-01", hasta="2025-03")
