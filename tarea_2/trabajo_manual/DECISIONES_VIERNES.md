# Decisiones tomadas el viernes 23/10 (trabajo autónomo)

Cada decisión eligió la opción más conservadora. Todas se pueden revertir el sábado.

| # | Hora | Decisión | Motivo | Cómo revertir |
|---|---|---|---|---|
| 1 | 18:42 | No subo `15_juev.png` ni `16_juev.png` y no los borro. | Son copias exactas (mismo SHA-256) de `13_juev.png` y `14_juev.png`; tú pediste no borrar archivos tuyos. | Bórralas tú, o pídeme que las suba si eran otras pantallas. |
| 2 | 18:46 | Seudonimizo a **todas** las personas, incluidos personajes históricos o públicos (Miguel Grau, Ramón Castilla, etc.). | El enunciado dice "ningún nombre ... real puede publicarse" sin excepciones; tapar de más es lo conservador. | Quitar esos nombres de `datos/raw/nombres_conocidos.txt` y volver a correr `src/seudonimizar.py`. |
| 3 | 18:47 | Muestra de audio sorteada hoy con `src/elegir_muestra.py audio` (regla del commit 4045a71, sin cambios). | Tú lo pediste; solo usa metadatos, no salidas de modelos. | No se rehace: el script se niega a sortear dos veces. |
| 4 | 18:48 | La plantilla de referencias va vacía y fuera de Git (`datos/raw/referencias/`). | Darte el texto de Whisper como borrador sesgaría la referencia; y al transcribir escribirás nombres reales. | — |
| 5 | 18:48 | Convención: números en palabras, sin marcas de hablante, ininteligibles se omiten y se anotan. | Hay que fijarla antes de escribir; "en palabras" es lo que se oye (no se adapta al formato de ningún modelo). | Cambiar la guía antes de empezar a transcribir. |
| 6 | 18:49 | Modelo NER sin licencia declarada en Hugging Face: lo uso solo para inferencia local, sin redistribuirlo. | Es el modelo que sugiere el enunciado; no se sube ni se publica. | Reemplazar por otro NER con licencia explícita. |
