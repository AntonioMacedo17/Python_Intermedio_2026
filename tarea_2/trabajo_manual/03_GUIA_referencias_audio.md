# Guía: referencias manuales de los 10 clips (sábado)

La muestra ya está sorteada con la regla commiteada (`datos/muestra_evaluacion_audio.csv`):
10 clips, **14,9 minutos** en total. Calcula unas 2 horas.

## Dónde escribir

Abre `tarea_2/datos/raw/referencias/referencias_audio.csv` (con Excel o VS Code).
Está **fuera de Git** a propósito: al transcribir vas a escribir nombres reales; la versión que
se publica se seudonimiza después con el mismo procedimiento que el resto del corpus.

Para escuchar cada clip, abre el `.wav` de la columna `archivo_para_escuchar`
(doble clic lo abre en el reproductor de Windows; puedes pausar y retroceder).

**No mires la transcripción de Whisper antes ni durante**: te "anclaría" y la referencia dejaría
de ser independiente (es una de las fallas que el profe menciona).

## Convenciones (iguales para los 10 clips)

1. **Escribe lo que se dice, no lo que "debería" decirse.** Si alguien dice "pa' que", escribe
   "pa que". No corrijas gramática.
2. **Números en palabras**, como se pronuncian: "dos mil veintidós", "quince soles".
3. **Puntuación y mayúsculas: no importan** (la evaluación las quita). Pon puntos si te ayudan.
4. **No escribas marcas de hablante** en `texto_referencia`. Escribe todo seguido, en orden.
5. **Muletillas** ("eh", "este", "ajá"): escríbelas si se oyen claramente.
6. **Partes ininteligibles**: no las inventes. Sáltalas y anota en `notas` el segundo aproximado
   (por ejemplo, "ininteligible 0:42-0:45").
7. **Música o ruido sin voz**: no escribas nada.
8. **`n_voces_distintas`**: cuántas personas distintas hablan en el clip (cuenta también a quien
   entrevista). Sirve para evaluar la diarización.

## Al terminar

Guarda el archivo (si Excel pregunta, mantén el formato CSV UTF-8) y avísame. Yo verifico que no
falte ninguno, seudonimizo, copio la columna a `datos/transcripciones.csv` y calculo el WER.
En los 3 clips de OpenSLR (`leido_estudio`) además comparo tu referencia con el texto oficial del
dataset, como control de calidad de la transcripción manual.
