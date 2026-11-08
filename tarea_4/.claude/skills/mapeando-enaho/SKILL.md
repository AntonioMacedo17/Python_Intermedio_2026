---
name: mapeando-enaho
description: Hace un mapa coroplético de la pobreza monetaria por departamento del Perú con la ENAHO 2024 del INEI (25 departamentos, Lima y Callao separados), ponderado con facpob07, y lo compara con la referencia oficial. Úsala cuando pidan un mapa de la pobreza, un mapa por departamento o región, o ver geográficamente dónde hay más pobreza en el Perú con la ENAHO.
---

# Mapear la pobreza de la ENAHO 2024

Todas las rutas son relativas a `tarea_4/`.

**Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.**

## Pasos

1. Corre exactamente:

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py
   ```

   Si falta `datos/peru_departamental_simple.geojson`, el script lo descarga de
   https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson
2. Si termina con `ERROR`, detente y explica qué falló (departamento sin dato, códigos que no cruzan, etc.).
   No unas por nombre ni rellenes valores para que el mapa salga completo.
3. Abre `mapas/pobreza_departamento.png` y míralo antes de entregarlo.
4. Reporta la **diferencia máxima** que imprime el script contra `referencias/pobreza_departamento_2024.csv`
   y la ruta de `salidas/comparacion_mapa_referencia.csv`.

## Reglas que el script ya cumple

- **Une por código, nunca por nombre**: `ubigeo[:2]` con `FIRST_IDDP`, ambos texto de 2 dígitos
  («APURIMAC» no es «Apurímac»; `1` no es `01`).
- Exige 25 unidades, ninguna sin dato, sin códigos repetidos; Lima (15) y Callao (07) separados.
- Escala secuencial de un solo tono (`Greens`), de claro a oscuro, que empieza en 0. Nunca arcoíris.
- Leyenda con la unidad «% de personas en pobreza monetaria», título con qué y cuándo, y fuente.
- PNG a 200 dpi en `mapas/`.

## Cómo leer la comparación con la referencia

`salidas/comparacion_mapa_referencia.csv` trae, por departamento: la referencia, lo calculado con `facpob07`
(lo que muestra el mapa), la diferencia, y lo calculado con el método de la sumaria (`factor07 × mieperho`).
La referencia de la sesión 16 se hizo con el método de la sumaria, por eso con ese método las diferencias son
solo de redondeo y con `facpob07` son algo mayores. Es una diferencia de método, no un error: dilo así.

## Cuidado

- Callao es muy pequeño en el mapa: si preguntan por él, da la cifra del CSV.
- Son estimaciones muestrales sin intervalos de confianza; describe patrones, no causas.
