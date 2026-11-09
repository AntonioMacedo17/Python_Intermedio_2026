# Resumen de la orquestación · Parte 3 (sesión del 2026-11-08, noche)

Una sola sesión de Claude Code (Opus 5.5) abierta en `tarea_4/`, con el servidor MCP `bcrp` conectado por
`.mcp.json` y las skills del proyecto en `.claude/skills/`. Lista en orden de las herramientas MCP y skills usadas,
con lo que devolvió cada una. Las cifras completas están en `salidas/bcrp_contexto.json`, `salidas/indicadores.csv`
y `salidas/validacion.txt`.

## Antes de empezar
- Commit `cf15bf8` (evidencia de la Parte 4) y push.
- Se borró `salidas/personas_2024.parquet` para que la cadena de la ENAHO corra desde los microdatos.

## Servidor MCP `bcrp` (llamadas directas desde Claude Code)

| # | Herramienta | Argumentos | Qué devolvió |
|---|---|---|---|
| 1 | `buscar_series` | "ipc lima 12 meses", Mensual | `PN01273PM` (IPC Lima, var% 12 meses) primero, más 4 variantes (importado, subyacente, transables, no transables) |
| 2 | `buscar_series` | "pbi variacion", Mensual | solo series sectoriales (agropecuaria, pesca…): **no** encontró el PBI global |
| 3 | `buscar_series` | "pbi variacion porcentual", Anual | `PM04863AA` (PBI, variación porcentual), entre otras |
| 4 | `buscar_series` | "ingresos tributarios gobierno general pbi" | `PM05876FA` (anual) y `PN03251FQ` (trimestral), ingresos tributarios % del PBI |
| 5 | `buscar_series` | "producto bruto interno interanual", Mensual | `PN01728AM` (PBI, var. % interanual) primero |
| 6 | `resumen` | PN01273PM, 2020-01 a 2024-12 | n = 60; pico 8.8126 (2022-06); mínimo 1.5987 (2020-06); promedio 4.4664; último 1.9663 (2024-12) |
| 7 | `resumen` | PN01728AM, 2020-01 a 2024-12 | n = 60; máximo 59.8948 (2021-04); mínimo −39.277 (2020-04); promedio 2.247; último 5.0662 |
| 8 | `serie` | PM04863AA, 2020 a 2024 | 2020 −10.93; 2021 13.42; 2022 2.82; 2023 −0.35; 2024 3.52 |
| 9 | `serie` | PM05876FA, 2020 a 2024 | 13.01; 16.04; 16.93; 14.83; 14.41 (% del PBI) |
| 10 | `serie` | PN01273PM, 2020-01 a 2024-12 | los 60 valores mensuales (dic-2020 1.97, dic-2021 6.43, dic-2022 8.46, dic-2023 3.24, dic-2024 1.97) |
| 11 | `correlacion` | PN01273PM vs PN01728AM, 2020-2024, niveles | n = 60; Pearson 0.0508; Spearman 0.1604; «positiva débil» |
| 12 | `correlacion` | ídem, en diferencias | n = 59; Pearson −0.1669; Spearman −0.2249; «negativa débil» |
| 13 | `correlacion` | 2022-2024, niveles | n = 36; Pearson −0.3194; Spearman −0.3351; «negativa moderada» |
| 14 | `correlacion` | 2022-2024, en diferencias | n = 35; Pearson −0.1608; Spearman −0.1227; «negativa débil» |

Ninguna llamada falló. Ninguna excluyó periodos por falta de dato.

## Skills de la ENAHO (invocadas con la herramienta Skill)

| # | Skill | Comando que corrió | Qué devolvió |
|---|---|---|---|
| 15 | `limpiando-enaho` | `uv run .claude/skills/limpiando-enaho/scripts/limpiar.py` | exit 0; 12/12 validaciones esenciales PASAN; pobreza 27.53 % (facpob07) y 27.58 % (sumaria); 108,664 residentes; 2 informativas FALLA con facpob07 (rural 39.44, Lima Met. 28.03), PASAN con la sumaria. Base y `indicadores.csv` (35 filas) reescritos |
| 16 | `graficando-enaho` | `graficar.py --por area`, `--por edad`, `--por departamento` | 3 figuras; urbana 24.74 / rural 39.44; 0-14 años 37.52 (la más alta); departamentos de 5.91 (Ica) a 44.99 (Cajamarca). Figuras idénticas a las ya versionadas |
| 17 | `mapeando-enaho` | `uv run .claude/skills/mapeando-enaho/scripts/mapear.py` | 25/25 departamentos unidos por código; diferencia máxima vs referencia +0.52 pp (Puno) con facpob07 y +0.05 pp con la sumaria |

## Scripts propios de esta parte

| # | Script | Qué hizo |
|---|---|---|
| 18 | `informes/scripts/grafico_bcrp.py` | Repite las llamadas 6-14 con `fastmcp.Client` en memoria (sin buscar_series), guarda `salidas/bcrp_contexto.json` y `figuras/bcrp_inflacion_pbi_2020_2024.png`. Sus cifras coinciden exactamente con las llamadas directas |
| 19 | `informes/scripts/verificacion.py` | Lee las salidas guardadas y escribe `salidas/verificacion.csv` y `salidas/brechas_enaho.csv` (rural − urbana 14.70 pp; 0-14 − nacional 9.99 pp; rango departamental 39.08 pp; 10 de 25 sobre el promedio) |

## Consultas web (subagente `web-fetch`)

| # | Qué | Resultado |
|---|---|---|
| 20 | Meta de inflación en 3 páginas de `www.bcrp.gob.pe` | **Falló**: las 3 devolvieron una página anti-bot («Pardon Our Interruption»). La banda meta no se dibujó |
| 21 | Páginas BCRPData de `PN01273PM` y `PM04863AA` | Cargaron: Dic.2024 1.97, Jun.2022 8.81; PBI 2020 −10,9 … 2024 3,5. Coinciden con el MCP (lectura automática: falta la revisión manual de Antonio) |

## Problemas y correcciones
- La búsqueda #2 no encontró el PBI global: se reformuló (#5).
- Primera versión de la figura del BCRP con el título cortado y la etiqueta del pico encima de la línea: corregida.
- En el borrador del informe se escribió a mano una diferencia (0.18 pp para Lima Met.) que era 0.17: se reemplazó por
  los valores que imprime `validacion.txt`.
