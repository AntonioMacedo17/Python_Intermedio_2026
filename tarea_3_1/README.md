# Incendios en el Perú · D: ¿A quién afecta?

**Tarea 3.1 · Ciencia de Datos con Python · 21 de octubre de 2026 · Antonio Macedo**

**Dashboard interactivo:** [`dashboard/index.html`](dashboard/index.html). Descárgalo y ábrelo con doble clic, o míralo en línea en [raw.githack](https://raw.githack.com/AntonioMacedo17/Python_Intermedio_2026/main/tarea_3_1/dashboard/index.html). Tiene un mapa de distritos e incendios con un deslizador de "mínimo de focos", gráficos por departamento y por definición, una tabla de incendios y la sección de Mazamari.

## La pregunta

¿Cuántas personas viven a **5 km o menos** de los incendios activos del Perú esta semana, dónde están, y cuánto se quemó en un incendio concreto (Mazamari, Satipo)?

## Tres hallazgos

1. **Unas 828 mil personas (2,3 % del país) viven a ≤ 5 km de alguno de los 327 incendios de vegetación activos.** Junín encabeza la lista con **148 mil personas (9,2 % de su población)**, concentradas en la selva central: en el distrito de Satipo queda expuesto el **75 %** de los habitantes, y en Pangoa hay **14 incendios activos**. Le siguen San Martín (100 mil · 9,6 %) y Lambayeque (85 mil).
2. **La respuesta depende de lo que llamemos «incendio».** Con todos los focos salen **1,15 millones** de personas, y quitando 4 fuentes urbanas o industriales (Chimbote, Chincha, Pisco y Mollendo) bajan a **828 mil**. Si solo cuento los incendios con ≥ 3 focos quedan **213 mil**, y con los que superan las 100 ha, **72 mil**. Más de la mitad de los incendios activos (172 de 327) son de un solo foco, y suelen estar cerca de pueblos: probablemente quemas agrícolas pequeñas que exponen a mucha gente al humo.
3. **Mazamari (Satipo, Junín): 112 ha quemadas con severidad moderada (dNBR ≥ 0,27) y 507 ha con algún daño (dNBR ≥ 0,1), con 2 529 personas a ≤ 5 km.** Afecta a una población rural dispersa de 10 a 100 hab/km², no a una ciudad. El número cambia según la imagen "antes" que elija: entre **69 y 152 ha**.

![Mapa nacional de población expuesta](figuras/mapa_poblacion_5km_peru.png)

![Barras por departamento y por definición](figuras/barras_departamento_y_definiciones.png)

![Mazamari: población, radio de 5 km y área quemada](figuras/mapa_mazamari_poblacion.png)

![dNBR de Mazamari](figuras/mapa_dnbr_incendio_190.png)

## Los datos y sus fechas

| Dato | Fuente | Fecha / versión | Tipo |
|---|---|---|---|
| Focos de calor | NASA FIRMS, VIIRS 375 m (S-NPP, NOAA-20, NOAA-21), «South America 7d» | 14 oct 05:14 – 21 oct 19:19 UTC, 2026 | Puntos (CSV) |
| Imágenes | Sentinel-2 L2A, Microsoft Planetary Computer | antes **28 sep 2026**, después **20 oct 2026** (órbita R082, tiles 18LWM/LWN/LXM/LXN) | Raster 20 m |
| Población | WorldPop 2020, 1 km, Perú (`per_ppp_2020_1km_Aggregated`) | 2020 | Raster 1 km |
| Límites | INEI con UBIGEO, `juaneladio/peru-geojson` | — | Polígonos |

**Nubes de las imágenes Sentinel-2 en la zona del incendio de Mazamari** (todas las imágenes en [`escenas_s2_incendio_190.csv`](datos/procesados/escenas_s2_incendio_190.csv)):

| Fecha | % nube en la zona | % nube escena | Uso |
|---|---|---|---|
| 2026-08-31 | 0,0 | 40,3 | sensibilidad |
| **2026-09-28** | **0,0** | 44,3 | **antes** |
| 2026-10-08 | 0,0 | 33,8 | sensibilidad |
| 2026-10-13 | 51,0 | 36,6 | descartada |
| 2026-10-18 | 43,3 | 81,0 | descartada |
| **2026-10-20** | **1,2** | 62,9 | **después** |

## Método

Cada paso es un script de `src/` y corre en CPU en unos minutos.

0. **`00_descargar.py`**: baja los focos, los límites y WorldPop (nada pide clave).
1. **`01_focos_incendios.py`**: de focos a incendios.
   - Une los 3 satélites VIIRS, se queda con los focos dentro del Perú y descarta los de confianza baja (9 949 → 8 613 focos).
   - Excluye los focos a ≤ 5 km de volcanes activos (Sabancaya, Ubinas, Misti).
   - Agrupa como un mismo incendio los focos a **≤ 1 km y ≤ 48 h** entre sí, usando componentes conexas de un grafo.
   - Saca las **fuentes fijas**, que arden ≥ 6 días sin moverse más de ~220 m. Así cayó la planta de gas de Pisco (Paracas).
   - Resultado: **2 585 incendios**, de los cuales **331 están activos** (con algún foco en las últimas 48 h).
2. **`02_dnbr.py`**: área quemada de Mazamari.
   - Primero lista las fechas y el % de nubes **dentro de la zona del incendio**.
   - Calcula NBR = (B8A − B12)/(B8A + B12) a 20 m, y dNBR = NBR antes − NBR después.
   - Enmascara con la capa SCL las clases 0, 1, 3, 6, 8, 9, 10 y 11 (sin dato, saturado, sombra, agua, nubes, cirros y nieve), en cualquiera de las dos fechas. Queda enmascarado el 1,2 % de la zona.
   - Solo cuenta píxeles a ≤ 1 km de los focos del incendio. Las clases de severidad siguen al USGS (0,10 / 0,27 / 0,44 / 0,66).
3. **`03_poblacion.py`**: ¿a quién afecta?
   - Traza un buffer de 5 km alrededor de cada foco activo (en UTM 18S) y **une** todos los buffers, para no contar dos veces a la misma persona.
   - Suma los píxeles de WorldPop cuyo centro cae dentro y reparte el total por distrito y departamento.
   - Excluye como **urbano/industrial** todo incendio cuya mayoría de focos cae en píxeles con ≥ 500 hab/km².
4. **`04_figuras.py`**: genera los mapas y gráficos. **`05_dashboard.py`** arma el dashboard HTML (Leaflet + Plotly) con los datos incrustados.

### Decisiones que cambiaron el resultado

- **Incendio elegido.** Primero probé **Cayna (Ambo, Huánuco)**, pero empezó el 18 de octubre y la única imagen posterior (21 oct) estaba 100 % nublada: no se podía medir. Entre los incendios activos, solo Curahuasi y Mazamari habían quemado antes de una imagen limpia. Elegí Mazamari porque Curahuasi era el ejemplo de la clase.
- **Fecha "antes".** En la imagen del 8 de octubre ya se veía una parte quemada, así que el incendio empezó antes de que FIRMS registrara sus 7 días. Por eso usé el 28 de septiembre:

  | Imagen antes | dNBR ≥ 0,27 | dNBR ≥ 0,10 |
  |---|---|---|
  | 8 oct | 69 ha | 405 ha |
  | **28 sep** | **112 ha** | **507 ha** |
  | 31 ago | 152 ha | 637 ha |

  Una fecha más temprana capta más del incendio, pero también mezcla más cambios ajenos a él, como quemas agrícolas anteriores o el cambio estacional de la vegetación.

## Limitaciones

- **Un foco de calor no es un incendio.** Los focos de un solo píxel pueden ser quemas agrícolas, basurales o industrias. Excluí 4 fuentes urbanas y 2 fijas, pero quedan dudas. Por ejemplo, varios "incendios" en la costa de Moquegua, Ilo y Arequipa aparecen todos en la misma pasada del 20 oct (18:36 UTC) y podrían ser falsos positivos sobre el desierto.
- **Las nubes esconden el fuego.** En la selva, un incendio puede quedar oculto a VIIRS y a Sentinel-2 durante días. Cayna no se pudo medir por eso.
- **Exposición no es daño.** Vivir a ≤ 5 km de un incendio no significa haber perdido algo; es una medida de *quién está cerca* (humo, riesgo, evacuación). Además, el radio de 5 km es una convención.
- **WorldPop es de 2020** y modela la población: no es un censo. A 1 km, un píxel parcialmente dentro del buffer se cuenta entero o no se cuenta, según dónde caiga su centro.
- **FIRMS de 7 días** no ve el inicio de incendios más antiguos. Las cifras por incendio se solapan y no se pueden sumar; el total nacional sí usa la unión de los buffers.
- La herramienta es independiente y no reemplaza los reportes de COEN, INDECI, SERFOR ni SERNANP.

## Cómo reproducir

```bash
cd tarea_3_1
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
cd src
python 00_descargar.py
python 01_focos_incendios.py
python 02_dnbr.py listar 190 2026-08-25 2026-10-21
python 02_dnbr.py calcular 190 2026-09-28 2026-10-20
python 03_poblacion.py
python 04_figuras.py
python 05_dashboard.py
```

> FIRMS «7d» cambia todos los días. Los focos de este análisis quedaron guardados en `datos/procesados/focos_peru.csv`. Los ID de incendio pueden cambiar si se re-descargan los datos.
