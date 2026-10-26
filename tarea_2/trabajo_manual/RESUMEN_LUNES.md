# Resumen de cierre – Tarea 2 (domingo 25 y madrugada del lunes 26/10/2026)

## Qué se hizo
- Entrega publicada en el Issue #190 y actualizada con el CER de OCR.
- Referencias manuales de los 10 documentos (hechas por el estudiante), seudonimizadas antes de publicarlas.
- CER/WER de OCR calculados con la regla del fragmento fijo (primeras 15 líneas) y con las referencias parciales marcadas.
- README, dashboard y notebooks 01 y 02 actualizados; capturas 01–27 en `evidencias_ia/`.

## Cifras clave
| | Base | Alternativo |
|---|---|---|
| ASR, WER (10 clips) | faster-whisper small 0,302 | Parakeet 0,286 |
| OCR, CER (10 documentos) | PaddleOCR 0,236 | Tesseract 0,430 |
| OCR, CER sin las 2 referencias parciales | 0,228 | 0,423 |
| OCR, CER impresos / fotos / manuscritos | 0,024 / 0,348 / 0,364 | 0,158 / 0,580 / 0,582 |
| LLM (Gemini), acuerdo con la auditoría humana | 17/20 (85 %) | — |

## Decisiones de esta sesión
- Referencias de documentos clasificadas según las notas del estudiante: completas (4), con omisiones (4) y parciales (2: doc_012 y doc_017). El CER se calcula solo sobre la parte transcrita.
- "Prat" se agregó a la lista de nombres, con el mismo criterio que a los personajes históricos. Se había filtrado en `documentos.csv`.

## Pendientes (opcionales, fuera de plazo)
- 6 documentos propios (3 fotos y 3 manuscritos) para llegar a 25.
- 22 extracciones de Gemini que faltan, cuando se renueve la cuota.

## Próximo paso
La Tarea 2 está cerrada. Siguen la Tarea 1 (retomarla en `repos/Python_Intermedio_2026/tarea_1`, no en OneDrive) y la Tarea 3.
