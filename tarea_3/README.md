# ¿Quién financia al Estado peruano?

**Estructura tributaria, desigualdad y gasto social en el Perú frente a América Latina, la OCDE y los países nórdicos**

Tarea 3 · Diplomado QLAB, Python Intermedio 2026 · Antonio Macedo

- **Dashboard:** https://antoniomacedo17.github.io/Python_Intermedio_2026/
- **Post de LinkedIn (con el reel):** _pendiente: se agrega al publicarlo_
- **Reel:** subtítulos en [`reel/reel_tarea3.srt`](reel/reel_tarea3.srt), guion en `reel/guion_reel.py`; el video se publica en LinkedIn

---

## 1. Tema y pregunta

**Pregunta:** ¿cómo se compara la estructura tributaria del Perú (cuánto recauda, de quién y con qué impuestos) con la
de América Latina y el Caribe, la OCDE y los países nórdicos entre 2000 y 2024, y cómo se asocia con la desigualdad
y el gasto social?

Tiene tres ejes: (a) presión tributaria e impuestos indirectos (IGV) frente a directos; (b) desigualdad de
ingreso y de riqueza (Gini, 10 % y 1 % más ricos, 50 % de menores ingresos); (c) gasto social público. El enfoque
se inspira en la CEPAL: la forma de recaudar y gastar también es una forma de distribuir. Las conclusiones son
**asociaciones entre países, no efectos causales**.

## 2. Descripción del proyecto

- **Dashboard estático** (HTML + Plotly.js) publicado en GitHub Pages:
  - 4 KPIs que cambian con el año y el grupo de comparación.
  - Mapa por país, serie 2000–2024, composición de la recaudación, ranking, dispersión fiscal–desigualdad y comparación de WID.
  - Controles: año, grupo de comparación, indicador, países de la composición (también con clic en el mapa) y ejes de la dispersión.
  - Hallazgos, una sección sobre lo que el Estado deja de recaudar, metodología, fuentes, limitaciones y tabla descargable en CSV.
- **Reel** de ~60 s (1080×1920), en 7 escenas:
  - Narrado con mi voz clonada por IA (Qwen3-TTS) a partir de una grabación mía de 20 s.
  - Lleva subtítulos .srt, música con licencia CC BY y el aviso «voz generada con IA».

```
tarea_3/
├── scripts/      obtener_datos.py → procesar_datos.py → analizar_datos.py
├── datos/        originales/ (descargas y LEEME.md) y procesados/ (panel.csv, indicadores.json)
├── web/          index.html, assets/ y data/ (lo que publica GitHub Pages)
├── reel/         guion_reel.py, hacer_voz.py, hacer_video.py, curso_s15/ (código MIT del curso)
└── referencias.md   todas las fuentes, verificadas o marcadas como no verificadas
```

## 3. Fuentes y metodología

**Datos** (descargados el 01/11/2026 con `scripts/obtener_datos.py`):

| Fuente | Qué se usó |
|---|---|
| OCDE, Global Revenue Statistics (con CEPAL, CIAT y BID para ALC) | Recaudación por tipo de impuesto, % del PIB, 2000–2024 |
| OCDE, SOCX | Gasto social público, % del PIB (Perú desde 2012) |
| WID.world | Participación del 10 % y el 1 % más ricos en el ingreso y la riqueza; 50 % de menores ingresos |
| Banco Mundial, WDI | Gini, PIB per cápita PPA, población |
| CEPALSTAT (3127, 4407) | Gasto social (respaldo) |

**Indicadores:**
- **Presión tributaria:** recaudación total del gobierno general, con contribuciones sociales, en % del PIB.
- **Composición:** recaudación de cada impuesto ÷ recaudación total × 100. Los códigos OCDE son 1100 renta de personas, 1200 empresas, 4000 propiedad y 5111 IVA/IGV.
- **Ratio directos/indirectos:** (1000 + 4000) ÷ 5000.
- **Desigualdad:** promedio 2019–2023 de cada país.

**Asociación:** correlación de Spearman entre países y **correlación parcial** controlando por el logaritmo del PIB per
cápita. En simple: se quita a cada variable la parte que explica el nivel de desarrollo y se correlaciona lo que
queda. Si la relación sigue, no se debe solo a que los países ricos recauden más; aun así no prueba causalidad.

Referencias académicas y oficiales (Francke 2017; Alarco, Castillo y Leiva 2019; Jaramillo 2013; OCDE 2018;
Observatorio Fiscal Internacional 2026; SUNAT 2025; Lahura y Segovia 2021; Durand 2016; CEPAL 2016; Lustig 2018) en [`referencias.md`](referencias.md), con link y estado de verificación.

## 4. Tres hallazgos (año 2023, salvo que se indique)

1. **Impuestos directos como en la OCDE, pero los pagan las empresas.**
   - Los directos pesan 41.7 % de la recaudación en el Perú frente a 41.2 % en la OCDE.
   - La renta de empresas aporta 24.3 % del total (OCDE: 11.1 %) y depende de la minería y del precio de los metales.
   - La renta de personas recauda solo 1.76 % del PIB (OCDE: 8.2 %; nórdicos: 14.4 %).
   - El IGV recauda **3.6 veces** lo que la renta de personas.
   - La presión tributaria es 16.7 % del PIB (ALC: 21.5 %; OCDE: 33.7 %; nórdicos: 41.2 %), puesto 23 de 28 en ALC.
   - La base es estrecha: en los registros de la SUNAT de 2014–2015, solo alrededor de 25 % de 5.49 millones de trabajadores formales pagó impuesto a la renta, y la rebaja de tasas de 2015 (Ley 30296) hizo más desigual su ingreso después de impuestos (Lahura y Segovia, 2021, pp. 13, 16 y 22).
2. **La mitad de menores ingresos recibe muy poco y la propiedad casi no tributa.**
   - El 50 % de menores ingresos recibe 8.3 % del ingreso nacional (nórdicos: 23.5 %; WID, promedio 2019–2023).
   - Los impuestos a la propiedad recaudan 0.90 % del PIB (OCDE: 1.69 %).
   - WID estima que el 1 % más rico tiene 39 % de la riqueza neta, pero es una estimación con pocos datos directos para el Perú.
   - Cómo medir mejor: con registros anónimos de la SUNAT, Lahura y Segovia (2021) encuentran impuestos directos progresivos (Kakwani ≈ 0.36) que bajan el Gini 2.3–2.5 puntos entre trabajadores formales; con la ENAHO, Jaramillo halla 0.6 puntos (citado en su p. 4). No son comparables: cubren poblaciones distintas.
3. **Recaudar y gastar más se asocia con menos desigualdad; la mezcla de impuestos, por sí sola, no.**
   - Entre 50 países, la presión tributaria se asocia con un menor Gini aun controlando por PIB per cápita (ρ parcial = −0.53, p < 0.001).
   - El gasto social muestra lo mismo (−0.37, p = 0.025, 37 países).
   - La renta de personas deja de ser significativa, y una mayor proporción de directos/indirectos se asocia con *más* desigualdad (+0.39).
   - El Perú gasta 7.5 % del PIB en lo social (OCDE: 20.8 %).
   - Coincide con Jaramillo (2013): el Perú redistribuye poco porque recauda y gasta poco.

**Contexto (no es resultado propio):** según la SUNAT, el gasto tributario potencial de 2026 es S/ 26 350 millones,
2.16 % del PBI y 12.68 % de la recaudación (Informe N.º 000045-2025-SUNAT/1V3000). La SUNAT advierte que la suma es
«una gruesa referencia» y «podría estar sobrestimada». Como ejemplo de cómo se decide lo que no se recauda, Durand (2016,
pp. 8 y 62) estudia la Ley 30230 (2014) como caso de captura del Estado: en lo tributario condona deudas, limita la
fiscalización de la SUNAT, amplía los convenios de estabilidad tributaria y suspende por tres años la norma antielusión.

## 5. Limitaciones

- **Asociación, no causalidad:** con un corte transversal de países no se aísla el efecto de los impuestos; influyen la historia, las instituciones y la informalidad.
- **El Gini mide cosas distintas:** en ALC suele medirse sobre ingreso per cápita y en Europa sobre ingreso disponible.
- **WID.world:** combina encuestas, registros tributarios y cuentas nacionales; los últimos años son extrapolados y difieren de las cifras del INEI. El top 1 % del Perú cae de 35.8 % (2022) a 27.6 % (2023), lo que sugiere un cambio de método y no un cambio real.
- **Gasto social del Perú en SOCX:** solo desde 2012; no hay promedio ALC con esa metodología.
- **Lo que no se mide:** evasión ni incidencia por deciles. No se verificó el costo fiscal del régimen agrario ni el de los convenios de estabilidad minera.
- **Gasto tributario:** la SUNAT advierte que su suma «solamente debe ser considerada como una gruesa referencia» y «podría estar sobrestimada».
- **Lahura y Segovia (2021):** su estudio cubre solo a trabajadores formales y advierte que los ingresos declarados pueden no ser los reales por la evasión (p. 22).
- **Fuentes que no se pudieron abrir:** algunas (CEPAL, BCRP) bloquean las descargas automáticas; las que Antonio no verificó en el navegador están marcadas como «no verificadas» en `referencias.md` y no se citan en el dashboard.

## 6. Links

- Dashboard: https://antoniomacedo17.github.io/Python_Intermedio_2026/
- LinkedIn (post con el reel): _pendiente_
- Repositorio: https://github.com/AntonioMacedo17/Python_Intermedio_2026/tree/main/tarea_3

## 7. Cómo reproducir

```bash
cd tarea_3
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python scripts/obtener_datos.py      # descarga (WID: solo 15 países, vía HTTP range)
python scripts/procesar_datos.py     # panel país-año: datos/procesados/panel.csv
python scripts/analizar_datos.py     # indicadores.json y los JSON de web/data/
python -m http.server 8765 --directory web   # abrir http://localhost:8765
```

**Reel:** usa un entorno aparte, `.venv-tts`, con qwen-tts, faster-whisper, imageio-ffmpeg, jiwer, num2words y pillow. Los modelos van en `modelos/` y no se versionan.

```bash
cd reel
python guion_reel.py                 # verifica las cifras del guion contra indicadores.json
python transcribir_referencia.py     # Whisper sobre mi grabación (voz/mi_voz.m4a, no versionada)
python hacer_voz.py                  # voz clonada, escena por escena (~40 min en CPU)
python hacer_video.py                # video 1080×1920 + .srt + música
```

La publicación la hace `.github/workflows/pages-tarea3.yml` en cada push que cambia `tarea_3/web/`.

## 8. Declaración de uso de IA

- **Asistente de programación y redacción:** usé Claude (Anthropic), mediante Claude Code. Me ayudó a escribir los scripts de descarga, limpieza y análisis, el dashboard, el guion y los textos, y a buscar y verificar referencias.
- **Qué decidí y revisé yo:** el tema, la pregunta, la paleta, el enfoque y el guion. Cada cifra del dashboard y del reel se lee de `indicadores.json`, que se calcula con los scripts; el guion se verifica con `guion_reel.py`. Las referencias que no se pudieron abrir están marcadas y no se citan.
- **Voz del reel:** generada con IA (Qwen3-TTS 0.6B, Alibaba Qwen, licencia Apache 2.0) a partir de una grabación de mi propia voz. La transcripción de referencia la di yo y se comparó con Whisper large-v3-turbo.
- **Código del reel:** se basa en el de la sesión 15 del curso (`reel/curso_s15/`, licencia MIT).
- **Música:** «Clean Soul», de Kevin MacLeod (incompetech.com), licencia CC BY 3.0, descargada de Wikimedia Commons.
