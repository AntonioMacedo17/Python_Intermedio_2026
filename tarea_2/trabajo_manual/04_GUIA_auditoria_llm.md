# Guía: auditoría humana de 20 extracciones del LLM (domingo, ~45 min)

Plantilla: `tarea_2/datos/raw/referencias/auditoria_llm.xlsx` (fuera de Git). Son 10 documentos y 10 audios
sorteados con semilla 2026. Cada fila trae el **texto que recibió el LLM** (ya seudonimizado) y los **campos
que devolvió**. Juzgas contra ese texto, no contra la imagen o el audio original: así se evalúa al LLM y no
al OCR/ASR.

## Criterios (escribe `si` o `no` en cada columna)

| Columna | Es `si` cuando… |
|---|---|
| `tema_ok` | el tema describe de qué trata el texto (o es `null` y el texto de verdad es ilegible o vacío) |
| `resumen_ok` | el resumen solo dice cosas que están en el texto y no omite lo principal |
| `campos_especificos_ok` | documentos: `emisor`, `fecha` y `monto` están bien **o** son `null` porque no aparecen; audios: las `citas_clave` están literalmente en el texto y `numero_hablantes` se puede sustentar (o es `null`) |
| `sin_inventos` | no hay ningún dato que no esté en el texto (nombres adivinados, fechas convertidas, montos inventados) |
| `completamente_correcta` | **las cuatro anteriores son `si`** |
| `error_observado` | si algo falló, una frase corta: qué campo y por qué |

El resultado que se reporta es: **extracciones completamente correctas / 20** (por ejemplo, 17/20 = 85 %).
`[PERSONA_###]` en un campo es correcto: el LLM no debe adivinar el nombre real.
