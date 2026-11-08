---
name: graficando-enaho
description: Hace gráficos de barras de la pobreza monetaria del Perú con la ENAHO 2024 del INEI, ponderados con facpob07, por área urbana y rural, por sexo, por grupo de edad o por departamento (con el promedio nacional). Úsala cuando pidan un gráfico, gráfica, figura o barras de la pobreza, o comparar la pobreza entre zonas, mujeres y hombres, edades o departamentos con la ENAHO.
---

# Graficar la pobreza de la ENAHO 2024

Todas las rutas son relativas a `tarea_4/`.

**Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.**

## Pasos

1. Traduce el pedido a un corte:

   | El usuario dice… | `--por` |
   |---|---|
   | urbana y rural, zona, ámbito, campo y ciudad | `area` |
   | mujeres y hombres, sexo, género | `sexo` |
   | edad, niños, jóvenes, adultos mayores, grupos de edad | `edad` |
   | departamento, región, regiones del Perú, ranking | `departamento` |
   | todos los gráficos | `todos` |

2. Corre exactamente (uno por corte):

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --por area
   ```

3. Abre el PNG (`figuras/pobreza_<por>.png`) y míralo antes de entregarlo: textos sin choques, barras desde
   cero, valor en cada barra.
4. Responde con la ruta de la figura y las cifras que **imprime el script** (no las recalcules a mano).
   Cita: «INEI, ENAHO 2024 (módulos 34 y 02), ponderado con facpob07».

## Reglas que el script ya cumple (no las rompas si lo modificas)

- Pondera siempre con `facpob07`: `(pobre * facpob07).sum() / facpob07.sum()`.
- Barras desde cero, un solo color (verde `#1F5F4A`) y el valor escrito en cada barra.
- Línea punteada morada (`#6A4C93`) con el promedio nacional.
- Título analítico calculado desde los datos (qué y cuándo), subtítulo con «Perú, 2024» y la unidad
  «% de personas en pobreza monetaria».
- Nota: «Fuente: INEI, ENAHO 2024 (módulos 34 y 02). Elaboración propia, ponderado con facpob07.»
- Debajo de cada barra, el número de observaciones (n). Departamentos ordenados de mayor a menor.
- PNG a 200 dpi en `figuras/`, fondo crema `#F7F3EA`.

## Cuidado al interpretar

- Son estimaciones de una muestra, sin intervalos de confianza. Diferencias chicas (p. ej., menos de un punto
  entre mujeres y hombres) no deben presentarse como brechas reales.
- Describe asociaciones, no causas («la pobreza es mayor en…», no «ser rural causa…»).
