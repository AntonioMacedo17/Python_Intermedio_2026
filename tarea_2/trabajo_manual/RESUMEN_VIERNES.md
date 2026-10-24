# Resumen del viernes 23/10 (sesión autónoma, 18:40–20:55)

## Hecho (las 8 tareas)
| # | Tarea | Estado |
|---|---|---|
| 1 | OCR de los 19 documentos de Commons (PaddleOCR) | ✅ `datos/raw/documentos/ocr_crudo.csv` |
| 2 | Revisión del ASR (descartes y alucinaciones) | ✅ dentro del notebook 01 (2 duplicados de formato descartados; clip_010 casi sin voz por la música) |
| 3 | Seudonimización con conteo | ✅ lista 34 + NER 102 reemplazos; 0 nombres de la lista visibles (decisiones 2, 12, 13) |
| 4 | Notebook 01 ejecutado con 3 gráficos Plotly | ✅ ejecutado sin errores; subido **sin salidas** hasta tu revisión (decisión 7) |
| 5 | Tesseract y Parakeet | ⚠️ Tesseract ✅ (19 docs); Parakeet ⏳ sábado por RAM (decisión 14) |
| 6 | Muestra de 10 clips + plantilla | ✅ `datos/muestra_evaluacion_audio.csv` (14,9 min) y plantilla vacía en `datos/raw/referencias/` |
| 7 | Extracción con Gemini | ⚠️ 16/19 documentos, 0/35 audios (límite 429 + RAM; decisión 17) |
| 8 | Borrador de `app.py` | ✅ solo lee CSV; probado con AppTest; no publicado |

## Pendiente
- Gemini: 3 documentos y 35 audios (el script reanuda solo).
- Parakeet sobre la muestra y luego el resto.
- Capturas propias (fotos y manuscritos) → OCR → sorteo de la muestra de documentos → plantilla.
- Tus referencias manuales (10 clips + 10 documentos), auditoría de 20 casos, notebook 02, README, despliegue.
- Notar: en `doc_012` y `doc_016` Gemini dejó vacíos tema y resumen (texto OCR muy ruidoso); lo verás en la auditoría.

## Decisiones
Ver `DECISIONES_VIERNES.md` (1–18). Las que más te tocan: 1 (capturas 15 y 16 duplicadas, no subidas), 2 (se tapan también personajes históricos), 7 (textos no se suben hasta tu revisión).

## Tus tareas del sábado, en orden
1. Revisar `datos/raw/revision_seudonimizacion.csv` (¿quedó algún nombre?, ¿se tapó algo que no era nombre?).
2. Hacer las fotos y manuscritos según `01_GUIA_fotos_y_manuscritos.md` (~40 min) y avisarme: yo corro OCR, Tesseract y sorteo la muestra de documentos (commit **antes** de que escribas sus referencias).
3. Mientras corre lo pesado: transcribir los 10 clips en `referencias_audio.csv` siguiendo `03_GUIA_referencias_audio.md` (con la columna `n_voces_distintas`).
4. Transcribir los 10 documentos de la muestra cuando esté la plantilla.
5. Cerrar Stata un rato si puedes: Parakeet necesita ~2,5 GB libres.
6. Revisar y subir capturas de `evidencias_ia/` (archivo por archivo) y comentar el Issue.
