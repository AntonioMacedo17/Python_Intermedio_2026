# Tarea 4 · Agente de investigación socioeconómica (MCP del BCRP + Skills de ENAHO 2024)

Ricardo Antonio Macedo Villegas · Diplomado QLAB, Python Intermedio 2026 · Issue
[d2cml-ai/Data-Science-Python#201](https://github.com/d2cml-ai/Data-Science-Python/issues/201)

**Informe final:** [`informes/informe_final.md`](informes/informe_final.md) ·
**Evaluación:** [`evaluacion/comparacion.md`](evaluacion/comparacion.md) ·
**Evidencias de IA:** [`evidencias_ia/`](evidencias_ia/)

Todas las cifras de este README están copiadas de archivos del repo (se indica cuál junto a cada una).

---

## 1. Objetivo

Construir un agente de investigación con Claude Code que combine dos fuentes oficiales sin escribir cifras a mano:

- un **servidor MCP propio** (`bcrp`) que consulta la API de series estadísticas del Banco Central de Reserva del
  Perú (BCRP) y hace las cuentas (resúmenes, correlaciones) en el servidor;
- tres **skills** que limpian, grafican y mapean la pobreza monetaria de la **ENAHO 2024** del INEI, ponderada con
  `facpob07`, validada contra la cifra oficial.

Con ese agente se respondió la pregunta de investigación del [informe](informes/informe_final.md): *¿En qué
contexto macroeconómico llegó el Perú a 2024 y qué tan desigual era su pobreza monetaria?* (inflación y PBI
2020-2024 según el BCRP; brechas de pobreza por departamento, área y edad en 2024 según la ENAHO). Además se midió
si el MCP y las skills mejoran las respuestas de Claude Code (Parte 4). El alcance es descriptivo: se habla de
asociación, nunca de causalidad ([`CLAUDE.md`](CLAUDE.md), regla 3).

## 2. Arquitectura del agente

```text
                         ┌──────────────────────────────┐
                         │   Claude Code (agente)       │
                         │   abierto en tarea_4/        │
                         │   reglas: CLAUDE.md          │
                         └──────┬─────────────────┬─────┘
             .mcp.json (stdio)  │                 │  .claude/skills/ (herramienta Skill)
                                ▼                 ▼
          ┌──────────────────────────┐   ┌────────────────────────────────────────┐
          │ MCP bcrp (mcp/server.py) │   │ Skills de la ENAHO 2024                │
          │ 4 herramientas,          │   │ limpiando-enaho → graficando-enaho     │
          │ 1 recurso, 1 prompt      │   │                 → mapeando-enaho       │
          └────────────┬─────────────┘   └───────────────┬────────────────────────┘
                       │ httpx (reintentos + caché)      │ lee datos/*.zip (INEI) y el GeoJSON
                       ▼                                 ▼
          ┌──────────────────────────┐   ┌────────────────────────────────────────┐
          │ API del BCRP             │   │ salidas/  (validacion.txt, indicadores)│
          │ estadisticas.bcrp.gob.pe │   │ figuras/  (barras)   mapas/ (mapa)     │
          └────────────┬─────────────┘   └───────────────┬────────────────────────┘
                       │  salidas/bcrp_contexto.json     │
                       └───────────────┬─────────────────┘
                                       ▼
                     informes/informe_final.md (+ tabla de verificación)
```

Claude Code decide qué herramienta usar; el MCP trae y resume las series del BCRP; las skills procesan los
microdatos con scripts de Python; los scripts de `informes/scripts/` repiten las llamadas al MCP en memoria y
guardan todo en `salidas/` para que el informe cite archivos y no la conversación.

## 3. Servidor MCP `bcrp` ([`mcp/server.py`](mcp/server.py))

Hecho con FastMCP. Las 4 herramientas son de solo lectura y todas las cuentas se hacen con pandas en el servidor.

| Tipo | Nombre | Qué hace |
|---|---|---|
| Herramienta | `buscar_series(texto, frecuencia, limite)` | Busca códigos de serie en el catálogo de metadatos del BCRP por palabras |
| Herramienta | `serie(codigo, desde, hasta)` | Devuelve los valores oficiales periodo a periodo, con la URL de la API y de la página web |
| Herramienta | `resumen(codigo, desde, hasta)` | Primero, último, cambio, variación %, promedio, máximo y mínimo |
| Herramienta | `correlacion(codigo_a, codigo_b, desde, hasta, en_diferencias)` | Pearson y Spearman entre dos series alineadas por periodo, en niveles o en diferencias |
| Recurso | `bcrp://serie/{codigo}` | Ficha de una serie: nombre, categoría, frecuencia, desde cuándo hay datos, enlaces |
| Prompt | `informe(tema)` | Plantilla para un informe breve con cada cifra citada y verificable |

Detalles: reintentos con espera creciente si la API responde HTML (límite de pedidos) y caché en disco de 12 h en
`mcp/datos/cache_api/` (ignorada por Git). Pruebas en [`mcp/test_server.py`](mcp/test_server.py): **10 passed**
([`salidas/pytest_mcp.txt`](salidas/pytest_mcp.txt), corrida en vivo contra la API, sin caché, el 8 de noviembre de
2026).

## 4. Skills de la ENAHO ([`.claude/skills/`](.claude/skills/))

| Skill | Script | Qué hace |
|---|---|---|
| [`limpiando-enaho`](.claude/skills/limpiando-enaho/SKILL.md) | `scripts/limpiar.py` | Lee los módulos 34 y 02 desde los zip, filtra residentes habituales, une persona-hogar (`m:1`), valida contra la cifra oficial y escribe la base de personas, [`salidas/validacion.txt`](salidas/validacion.txt) e [`salidas/indicadores.csv`](salidas/indicadores.csv). Detalle del método en [`reference.md`](.claude/skills/limpiando-enaho/reference.md) |
| [`graficando-enaho`](.claude/skills/graficando-enaho/SKILL.md) | `scripts/graficar.py --por {area,sexo,edad,departamento}` | Barras de pobreza ponderada con `facpob07` en [`figuras/`](figuras/) |
| [`mapeando-enaho`](.claude/skills/mapeando-enaho/SKILL.md) | `scripts/mapear.py` | Mapa coroplético de los 25 departamentos en [`mapas/`](mapas/) y comparación con la referencia del curso en [`salidas/comparacion_mapa_referencia.csv`](salidas/comparacion_mapa_referencia.csv) |

Validación ([`salidas/validacion.txt`](salidas/validacion.txt)): pobreza nacional **27.53 %** (personas,
`facpob07`) y **27.58 %** (sumaria, `factor07 × mieperho`), ambas dentro de 27.6 ± 0.1 pp; **108,664** residentes
habituales de 117,721 filas del módulo 02; 25 códigos de departamento; todas las validaciones esenciales pasan. El
mapa une **25/25** departamentos (25 filas en `comparacion_mapa_referencia.csv`).

## 5. Fuentes y links de descarga

| Fuente | Link | Dónde va |
|---|---|---|
| INEI, ENAHO 2024, módulo 34 (sumaria) | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip | `datos/` (sin descomprimir) |
| INEI, ENAHO 2024, módulo 02 (miembros del hogar) | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip | `datos/` (sin descomprimir) |
| GeoJSON de departamentos (repositorio del curso) | https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson | `datos/` (`mapear.py` lo baja solo si falta) |
| BCRP, API de series | `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/<código>/json/<desde>/<hasta>` | consultada por el MCP |
| BCRP, catálogo de metadatos | https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata | usado por `buscar_series` |
| Referencias de validación del curso | [sesión 16 (`16-skills-enaho`)](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho) y [`referencias/pobreza_departamento_2024.csv`](referencias/pobreza_departamento_2024.csv) | validación |

Series del BCRP usadas en el informe: `PN01273PM` (IPC Lima, var. % 12 meses), `PN01728AM` (PBI, var. %
interanual), `PM04863AA` (PBI, var. % anual) y `PM05876FA` (ingresos tributarios, % del PBI).

## 6. Instalación con uv

```bash
# 1. Instalar uv: https://docs.astral.sh/uv/getting-started/installation/
# 2. Desde la raíz del repo:
cd tarea_4
uv sync            # crea .venv con las dependencias de pyproject.toml (incluye pytest)
```

Dependencias ([`pyproject.toml`](pyproject.toml)): `fastmcp>=4,<5`, `httpx`, `pandas`, `pyarrow`, `geopandas`,
`matplotlib`; `pytest` en el grupo `dev`. Python ≥ 3.11. Funciona en CPU (probado en Windows 11 con ~8 GB de RAM).

## 7. Conectar el MCP a Claude Code

El servidor se declara a nivel de proyecto en [`.mcp.json`](.mcp.json):

```json
{
  "mcpServers": {
    "bcrp": { "type": "stdio", "command": "uv", "args": ["run", "mcp/server.py"], "env": {} }
  }
}
```

1. Abrir Claude Code **dentro de `tarea_4/`** (`cd tarea_4` y luego `claude`).
2. Aceptar el servidor del proyecto cuando Claude Code lo pregunte.
3. Escribir `/mcp`: debe aparecer `bcrp` con ✓ y **4 tools**
   ([captura](evidencias_ia/mcp/captura_mcp_conectado.png)).
4. Las skills se cargan solas desde `.claude/skills/`; `/skills` las lista como `project`
   ([captura](evidencias_ia/skills/captura_skills.png)).

No necesita claves: la API del BCRP es pública.

## 8. Reproducir el procesamiento y las pruebas

Desde `tarea_4/`, con los dos zip de la ENAHO en `datos/`:

```bash
uv run pytest -q                                                     # contrato del MCP (10 pruebas)
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py             # base validada + indicadores
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por edad
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por departamento
uv run .claude/skills/mapeando-enaho/scripts/mapear.py               # mapa + comparación con la referencia
uv run informes/scripts/grafico_bcrp.py                              # BCRP vía MCP en memoria + Figura 1
uv run informes/scripts/verificacion.py                              # tabla de verificación y brechas
```

Evaluación de la Parte 4 (necesita el CLI `claude` con sesión iniciada; consume uso del plan):

```bash
uv run evaluacion/verdades_bcrp.py && uv run evaluacion/verdades_enaho.py && uv run evaluacion/armar_preguntas.py
uv run evaluacion/evaluar.py         # 10 preguntas × modos A y B, modelo sonnet
uv run evaluacion/comparar.py        # resultados.csv → comparacion.md y figura
```

## 9. Resultados de la evaluación (Parte 4)

Diseño fijado antes de correr en [`evaluacion/README_evaluacion.md`](evaluacion/README_evaluacion.md): 10 preguntas
(4 BCRP, 4 ENAHO, 2 combinadas), mismo modelo (sonnet) en los dos modos, una sesión independiente por pregunta.

| Modo | Correctas | Incorrectas | Sin respuesta | Tiempo promedio |
|---|---|---|---|---|
| A · sin MCP ni skills | **2/10** | 3 | 5 | 5.6 s |
| B · con MCP y skills | **9/10** | 1 | 0 | 15.0 s |

| Tipo | A | B |
|---|---|---|
| BCRP (B1–B4) | 1/4 | 4/4 |
| ENAHO (E1–E4) | 1/4 | 3/4 |
| Combinadas (C1–C2) | 0/2 | 2/2 |

Mejoraron 7 preguntas y ninguna empeoró. El MCP se usó en las 6 preguntas que pedían una cifra del BCRP y acertó en
todas. La única incorrecta del modo B fue E4 (pobreza extrema), respondida de memoria. Datos completos:
[`evaluacion/resultados.csv`](evaluacion/resultados.csv) · análisis: [`evaluacion/comparacion.md`](evaluacion/comparacion.md)
· registros de herramientas: [`evaluacion/registros/`](evaluacion/registros/) · figura:
[`figuras/evaluacion_aciertos.png`](figuras/evaluacion_aciertos.png). Son 10 preguntas y una sola corrida: el
resultado es indicativo.

## 10. Limitaciones y problemas encontrados

1. **Dos métodos de ponderación dan cifras algo distintas.** Con personas y `facpob07` la pobreza nacional es
   27.53 %; con la sumaria (`factor07 × mieperho`), 27.58 %. Las referencias del curso de rural (39.3) y Lima
   Metropolitana (28.2) coinciden con la sumaria (39.30 y 28.21 %); con `facpob07` dan 39.44 y 28.03 % y quedan
   marcadas FALLA informativa (± 0.1 pp). En el mapa, la diferencia máxima con la referencia es +0.52 pp (Puno) con
   `facpob07` y ±0.05 pp con la sumaria. Es una diferencia de método, no un error; no se ajustó nada
   ([`salidas/validacion.txt`](salidas/validacion.txt)).
2. **Banda meta de inflación no confirmada.** Las tres páginas de `www.bcrp.gob.pe` sobre la meta devolvieron una
   página anti-bot («Pardon Our Interruption»), así que la banda no se dibujó en la Figura 1 ni se usa como cifra.
   La franja de la pandemia (mar-2020 a dic-2021) es una delimitación propia, no oficial.
3. **Las skills no siempre se activan solas.** En el modo B, el script de la skill corrió en 3 de las 6 preguntas
   con ENAHO (E3, C1, C2). En E2 el agente calculó con su propio código, en E1 citó la `description` y en E4
   respondió de memoria (y falló).
4. **El 27.6 escrito en la `description` de `limpiando-enaho`.** Por eso E1 del modo B acertó sin correr la skill:
   cuenta como correcta según la regla, pero no prueba que la skill procese datos.
5. **Falsos positivos de la regla automática de coherencia.** Marcó como causales 2 de 4 interpretaciones (C1-A y
   C2-A) que en realidad niegan la causalidad (disparadores: «explique» y «general»). No cambió ningún resultado;
   la calificación final de coherencia fue la revisión manual de Antonio (4/4 coherentes).
6. **`ls ~` en el modo B.** En B-E3 el agente corrió `ls ~ | head` y vio las 10 primeras entradas de la carpeta
   personal (sin `repos`); en B-E2 descomprimió la sumaria en `/tmp`. Ninguna lectura del modo B tocó la ruta del
   repo (columna `acceso_fuera_copia` vacía en las 20 filas de `resultados.csv`).
7. **Otras.** Sin intervalos de confianza para la ENAHO (diferencias chicas pueden no ser significativas); inflación
   de Lima frente a PBI nacional; fuentes de distinto nivel de agregación y periodo (2020-2024 frente a 2024); las
   series del BCRP se revisan (valores al 8 de noviembre de 2026). Detalle en la sección 6 del
   [informe](informes/informe_final.md#6-limitaciones).

## 11. Ejemplo de una ejecución completa (Parte 3)

Una sola sesión de Claude Code en `tarea_4/` produjo el informe. Orden de llamadas completo en
[`evidencias_ia/integracion/resumen_orquestacion.md`](evidencias_ia/integracion/resumen_orquestacion.md):

1. **MCP `bcrp`, 14 llamadas:** 5 `buscar_series` para elegir los códigos (una no encontró el PBI global y se
   reformuló), 2 `resumen`, 3 `serie` y 4 `correlacion` (niveles y diferencias, 2020-2024 y 2022-2024). Ninguna
   falló.
2. **Skills:** `limpiando-enaho` desde los microdatos (12/12 validaciones esenciales pasan), `graficando-enaho`
   (área, edad, departamento) y `mapeando-enaho` (25/25 departamentos).
3. **Scripts propios:** `grafico_bcrp.py` repite las llamadas al MCP en memoria y guarda
   [`salidas/bcrp_contexto.json`](salidas/bcrp_contexto.json) y la Figura 1; `verificacion.py` escribe
   [`salidas/verificacion.csv`](salidas/verificacion.csv) y [`salidas/brechas_enaho.csv`](salidas/brechas_enaho.csv).
4. **Verificación:** tabla de 8 afirmaciones al final del [informe](informes/informe_final.md#verificación); Antonio
   revisó a mano en BCRPData la inflación de dic-2024 (1.97) y el PBI 2024 (3,5) y 2020 (−10,9)
   ([captura IPC](evidencias_ia/integracion/verificacion_ipc.png), [captura PBI](evidencias_ia/integracion/verificacion_pbi.png)).

Algunos resultados (del informe): inflación de Lima con pico de 8.81 % en jun-2022 y 1.97 % en dic-2024; PBI 2024
+3.5 %; pobreza rural 39.44 % frente a urbana 24.74 % (brecha de 14.70 pp); pobreza de 0 a 14 años 37.52 %;
departamentos de 5.91 % (Ica) a 44.99 % (Cajamarca).

## 12. Evidencias del uso de IA ([`evidencias_ia/`](evidencias_ia/))

| Parte | Archivo | Qué es |
|---|---|---|
| 1 · MCP | [`mcp/parte1_servidor.md`](evidencias_ia/mcp/parte1_servidor.md) | Conversación con Claude Code al construir el servidor |
| 1 · MCP | [`mcp/demo_mcp.md`](evidencias_ia/mcp/demo_mcp.md) | Demo del MCP conectado respondiendo preguntas |
| 1 · MCP | [`mcp/captura_mcp_conectado.png`](evidencias_ia/mcp/captura_mcp_conectado.png) | Captura de `/mcp` con `bcrp` y 4 tools |
| 2 · Skills | [`skills/parte2_skills.md`](evidencias_ia/skills/parte2_skills.md) | Conversación al construir las tres skills |
| 2 · Skills | [`skills/demo_skills.md`](evidencias_ia/skills/demo_skills.md) | Demo de activación de las skills |
| 2 · Skills | [`skills/captura_skills.png`](evidencias_ia/skills/captura_skills.png) | Captura de `/skills` con las tres skills del proyecto |
| 3 · Integración | [`integracion/parte3_agente.md`](evidencias_ia/integracion/parte3_agente.md) | Conversación completa de la sesión que hizo el informe |
| 3 · Integración | [`integracion/resumen_orquestacion.md`](evidencias_ia/integracion/resumen_orquestacion.md) | Orden de las herramientas MCP y skills usadas |
| 3 · Integración | [`integracion/verificacion_ipc.png`](evidencias_ia/integracion/verificacion_ipc.png), [`integracion/verificacion_pbi.png`](evidencias_ia/integracion/verificacion_pbi.png) | Capturas de la verificación manual en BCRPData |
| 4 · Evaluación | [`evaluacion/parte4_evaluacion.md`](evidencias_ia/evaluacion/parte4_evaluacion.md) | Conversación de la evaluación con y sin MCP/skills |

**Revisión de datos sensibles.** Antes de versionarlos se revisaron todos los archivos de `evidencias_ia/` y los
registros de `evaluacion/registros/`: no contienen claves de API, tokens ni correos; solo aparece el nombre de
Antonio en las rutas de Windows. Las capturas muestran la ruta del proyecto, la barra de tareas y, en las de
BCRPData, pestañas y marcadores del navegador sin datos personales. La verificación manual la hizo Antonio; no se
generó con un modelo.

## Estructura

| Carpeta / archivo | Qué contiene |
|---|---|
| `mcp/` | Servidor MCP del BCRP (`server.py`) y sus pruebas (`test_server.py`) |
| `.claude/skills/` | Skills `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho` |
| `datos/` | Microdatos ENAHO 2024 y GeoJSON (ignorados por Git; ver sección 5) |
| `salidas/`, `figuras/`, `mapas/` | Resultados generados por código |
| `referencias/` | Pobreza por departamento de referencia (sesión 16 del curso) |
| `evaluacion/` | Experimento con y sin MCP/Skills |
| `informes/` | Informe final y scripts que lo alimentan |
| `evidencias_ia/` | Conversaciones y capturas del uso de IA (mcp, skills, integracion, evaluacion) |
| `trabajo_manual/` | Resúmenes de cada sesión |
| `CLAUDE.md` | Reglas del proyecto para el agente |

No se versionan: `datos/`, `.venv/`, cachés, `.env` ni la base de personas (`*.parquet`), según
[`.gitignore`](.gitignore).
