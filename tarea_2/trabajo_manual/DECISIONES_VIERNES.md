# Decisiones tomadas el viernes 23/10 (trabajo autónomo)

Cada decisión eligió la opción más conservadora. Todas se pueden revertir el sábado.

| # | Hora | Decisión | Motivo | Cómo revertir |
|---|---|---|---|---|
| 1 | 18:42 | No subo `15_juev.png` ni `16_juev.png` y no los borro. | Son copias exactas (mismo SHA-256) de `13_juev.png` y `14_juev.png`; tú pediste no borrar archivos tuyos. | Bórralas tú, o pídeme que las suba si eran otras pantallas. |
| 2 | 18:45 | Seudonimizo a **todas** las personas, incluidos personajes históricos o públicos (Miguel Grau, Ramón Castilla, etc.). | El enunciado dice "ningún nombre ... real puede publicarse" sin excepciones; tapar de más es lo conservador. | Quitar esos nombres de `datos/raw/nombres_conocidos.txt` y volver a correr `src/seudonimizar.py`. |
| 3 | 18:45 | Muestra de audio sorteada hoy con `src/elegir_muestra.py audio` (regla del commit 4045a71, sin cambios). | Tú lo pediste; solo usa metadatos, no salidas de modelos. | No se rehace: el script se niega a sortear dos veces. |
| 4 | 18:45 | La plantilla de referencias va vacía y fuera de Git (`datos/raw/referencias/`). | Darte el texto de Whisper como borrador sesgaría la referencia; y al transcribir escribirás nombres reales. | — |
| 5 | 18:45 | Convención: números en palabras, sin marcas de hablante, ininteligibles se omiten y se anotan. | Hay que fijarla antes de escribir; "en palabras" es lo que se oye (no se adapta al formato de ningún modelo). | Cambiar la guía antes de empezar a transcribir. |
| 6 | 18:45 | Modelo NER sin licencia declarada en Hugging Face: lo uso solo para inferencia local, sin redistribuirlo. | Es el modelo que sugiere el enunciado; no se sube ni se publica. | Reemplazar por otro NER con licencia explícita. |
| 7 | 18:50 | Los textos (`documentos.csv`, `transcripciones.csv`, `extraccion_llm.csv` y el notebook 01 **con salidas**) NO se suben hasta tu revisión humana de la seudonimización. Hoy subo solo código y el notebook sin salidas. | El enunciado: "el procedimiento automático no sustituye la revisión humana" y publicar datos personales anula la parte. | Tras tu revisión (sábado/domingo) se suben con un commit. |
| 8 | 18:50 | Uso `#0F7A55` (verde más saturado) para barras de datos; `#1F5F4A` queda para títulos. | `#1F5F4A` falla el piso de croma del validador de paletas (0,074 < 0,10: se lee gris); `#0F7A55` pasa los 5 chequeos con el morado sobre el fondo crema. | Cambiar `VERDE` en la celda de estilo del notebook. |
| 9 | 18:50 | Agrego `kaleido` (grupo tarea2) para guardar cada gráfico Plotly también como imagen. | GitHub no muestra gráficos Plotly interactivos dentro de un .ipynb; el enunciado pide gráficos visibles en GitHub. | `uv remove --group tarea2 kaleido`. |
| 10 | 18:50 | Parakeet procesa primero los 10 clips de la muestra y luego el resto del corpus. | Pesa 2,5 GB y la RAM está justa: lo indispensable para la Parte 2 primero. | — |
| 11 | 18:50 | Gemini con el "thinking" en su valor por defecto de la API (no lo toqué), temperature=0, JSON con esquema; se verifica que ningún nombre de la lista conocida esté en el texto antes de enviarlo. | Reproducibilidad y privacidad. | Cambiar en `src/extraccion_llm.py`. |
