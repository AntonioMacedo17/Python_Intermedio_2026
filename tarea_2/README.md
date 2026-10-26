# Tarea 2 – Voces y documentos peruanos: del archivo escaneado al texto buscable

**Diplomado QLAB · Python Intermedio 2026 · Trabajo individual**
Estudiante: Antonio Macedo

**Pregunta guía:** ¿pueden convertirse documentos escaneados y entrevistas en audio peruanas en un archivo de
texto estructurado y buscable?

**Dashboard:** _(enlace de Streamlit Community Cloud: se agrega al publicar)_

| Etapa | Archivo | Salida |
|---|---|---|
| Parte 1 · Corpus, OCR, ASR, limpieza, seudonimización, EDA | `01_extraccion.ipynb` | `datos/documentos.csv`, `datos/transcripciones.csv`, `datos/fuentes.csv` |
| Parte 2 · Referencias manuales, CER/WER, modelos alternativos, LLM y auditoría | `02_evaluacion.ipynb` | `datos/metricas.csv`, `datos/comparacion_modelos.csv`, `datos/extraccion_llm.csv` |
| Parte 3 · Dashboard | `app.py` | — |

## 1. Corpus

| | Cantidad | Fuente | Licencias |
|---|---|---|---|
| Documentos | **19** (8 impresos, 5 fotos, 6 manuscritos) | Wikimedia Commons | dominio público, CC0, CC BY 2.0, CC BY 4.0, CC BY-SA 4.0 |
| Audio en español | **35 clips, 36,7 min** (15 entrevistas y grabaciones peruanas + 20 frases leídas) | Wikimedia Commons y OpenSLR 73 (español peruano, Google) | CC BY-SA 4.0 |
| Audio en quechua (extra) | 1 clip, 130 s | Wikimedia Commons | CC BY-SA 4.0 |

- 14 clips tienen 2 o más hablantes según la diarización.
- La limpieza descartó 2 clips: eran la misma grabación que otro clip, en otro formato (se detectaron por la envolvente de energía, con correlación 1,00).
- La URL, la licencia y la fecha de extracción de cada archivo están en `datos/fuentes.csv`.
- Los audios crudos, las imágenes originales y los pesos de los modelos **no se versionan**: viven en `datos/raw/`, que está en `.gitignore`.

## 2. Modelos y configuración

Todas las configuraciones y la regla de muestra se fijaron **antes** de ver resultados, en `modelos/config_evaluacion.json` (commit `4045a71`).

| Tarea | Base | Alternativo | Licencia |
|---|---|---|---|
| OCR | PaddleOCR 3.7.0, `lang='es'` | Tesseract 5.4.0, `spa` | Apache-2.0 / Apache-2.0 |
| ASR | faster-whisper small (CPU, int8, VAD Silero) | Parakeet TDT 0.6B v3 (CPU) | MIT / CC-BY-4.0 |
| Diarización | WeSpeaker ResNet34 + clustering aglomerativo (umbral 0,7) | — | — |
| Seudonimización | lista de nombres conocidos (difusa) + NER `mrm8488/bert-spanish-cased-finetuned-ner` + expresiones regulares (DNI, RUC, celular, correo) | — | NER sin licencia declarada: solo se usa localmente |
| Extracción | Gemini `gemini-3.8-flash`, temperature 0, JSON con esquema | — | API propietaria |

Todo corrió en una laptop **sin GPU** (Windows 11, 8 GB de RAM).

## 3. Privacidad

- Ningún nombre real se publica. Las personas se reemplazan por `[PERSONA_###]`: 119 cadenas distintas, 136 reemplazos en total (34 de la lista y 102 del NER).
- Después del proceso automático hubo una **revisión humana** (`src/hojas_revision.py` genera las hojas de revisión).
- A Gemini solo se envió **texto ya seudonimizado**. El script bloquea el envío si encuentra un nombre de la lista.
- Solo se muestran imágenes o audios de ejemplo en el dashboard si su licencia lo permite y no tienen datos personales.

## 4. Resultados

Las métricas se calcularon sobre los **10 clips de la muestra** (14,9 min) frente a la transcripción manual del estudiante. Se usó la misma normalización para los dos modelos (minúsculas, sin puntuación, con tildes). El valor agregado es el total de errores dividido entre el total de palabras.

| Modelo | WER | CER | Latencia (RTF mediano, CPU) | Licencia | Privacidad |
|---|---|---|---|---|---|
| faster-whisper small (base) | **0,302** | 0,219 | 0,54 | MIT | local |
| Parakeet TDT 0.6B v3 (alternativo) | **0,286** | 0,213 | 0,21 | CC-BY-4.0 | local |
| PaddleOCR (base) | pendiente | pendiente | 103 s/página | Apache-2.0 | local |
| Tesseract (alternativo) | pendiente | pendiente | 1 s/página | Apache-2.0 | local |
| Gemini 3.8 Flash (extracción) | — | — | — | API propietaria | nube, solo texto seudonimizado |

**WER por tipo de audio** (Whisper / Parakeet):

| Tipo de audio | WER |
|---|---|
| Lectura en estudio | 0,17 / 0,13 |
| Evento público | 0,18 / 0,13 |
| Calle | 0,24 / 0,25 |
| Marcha | 0,39 / 0,39 |
| Fiesta patronal | **0,74 / 0,73** |

La música de banda encima de la voz es el caso más difícil para los dos modelos.

**Conclusión:**
- Parakeet es algo más preciso que Whisper small (WER 0,286 contra 0,302) y unas 2,5 veces más rápido en CPU.
- La diferencia es pequeña para solo 10 clips, así que la conclusión es prudente: ambos sirven para volver buscable el habla clara, y ninguno sirve con música fuerte.

**Pendiente:**
- El CER de OCR: la muestra de 10 documentos ya está sorteada y la regla del fragmento fijo de 15 líneas está fijada, pero faltan las referencias manuales.
- El acuerdo LLM-humano: la auditoría de 20 casos ya está sorteada, pero falta llenarla.

## 5. Limitaciones (honestas)

1. **Corpus de documentos incompleto: 19 de 25.**
   - Faltan 3 fotos y 3 manuscritos propios (capturas tomadas por el estudiante).
   - Con licencia libre abundan los impresos peruanos, pero casi no hay manuscritos.
   - Las capturas propias se agregarán después de la entrega, con el mismo pipeline (`src/corpus_documentos.py`).
2. **Sin CER/WER de OCR todavía.**
   - La muestra de 10 documentos (3 impresos / 3 fotos / 4 manuscritos) ya está sorteada con la regla fijada, sobre los 19 documentos actuales.
   - Cada referencia cubrirá solo las primeras 15 líneas del documento (regla fijada antes de escribirlas).
   - Faltan las referencias manuales. Sí se reporta la latencia de los dos OCR.
3. **Gemini parcial: 32 de 54 extracciones** (19 documentos y 13 de 35 audios).
   - El nivel gratuito permite 20 pedidos por día y por modelo, y el límite cortó la corrida.
   - No se cambió de modelo para completar, para no mezclar dos modelos en el corpus.
   - La auditoría de 20 casos se sorteó entre las 32 extracciones existentes. La disponibilidad no depende de la calidad de la extracción.
4. **Diarización poco confiable con muchas voces cortas.** En una marcha detectó hasta 15 "hablantes".
5. **Música encima de la voz.** En un clip de fiesta patronal, el VAD solo encontró voz en ~11 % del audio.
6. **Orden de lectura.** En un manuscrito con 3 columnas, PaddleOCR mezcla las columnas. Por eso se excluyó de la muestra con una regla fijada antes.
7. **Sesgo de la muestra de audio.** Para que la transcripción manual fuera factible se tomaron clips de 200 s o menos, así que las entrevistas largas no se evalúan.

## 6. Cómo reproducir

```bash
cd tarea_2
uv sync --group docai --group audio --group tarea2      # entorno de los notebooks
.venv/Scripts/python.exe src/descargar_audio.py          # y src/descargar_documentos.py
.venv/Scripts/python.exe src/procesar_audio.py           # limpieza + ASR + diarización
.venv/Scripts/python.exe src/ocr_documentos.py
.venv/Scripts/python.exe src/seudonimizar.py
.venv/Scripts/python.exe src/modelos_alternativos.py tesseract   # y parakeet
.venv/Scripts/python.exe src/extraccion_llm.py           # necesita GEMINI_API_KEY en tarea_2/.env (no versionado)
# luego ejecutar 01_extraccion.ipynb y 02_evaluacion.ipynb
pip install -r requirements.txt && streamlit run app.py  # el dashboard solo lee los CSV
```

Los scripts son reanudables: si se interrumpen, siguen desde donde quedaron.

## 7. Uso de IA

- Se trabajó con Claude Code como asistente. Las capturas del proceso están en `evidencias_ia/` y la bitácora está en los Issues del repositorio.
- Las **transcripciones de referencia y la auditoría las hizo el estudiante a mano**: no se generaron con ningún modelo.
- Las decisiones tomadas durante el trabajo están en `trabajo_manual/DECISIONES_VIERNES.md`.
