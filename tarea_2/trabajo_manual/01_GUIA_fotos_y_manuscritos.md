# Guía para las capturas propias (viernes en la noche, ~40 min)

Commons ya aporta 8 impresos, 5 fotos y 6 manuscritos con licencia verificada.
**Faltan 3 fotos y 3 manuscritos.** Haz **4 de cada uno** (1 de reserva por si alguno se descarta
por ilegible, como pide el enunciado).

## Reglas (no negociables)

- **Nada de datos personales**: ni tu nombre, DNI, dirección, firma, teléfono, correo, placas
  ni caras. Si algo aparece por accidente, repite la foto.
- **Texto real, no inventado por una IA** (el enunciado prohíbe "texto sintético").
- **Sin filtros ni "modo escáner"** del celular: ese modo endereza y limpia la imagen y
  borraría justo las dificultades que queremos medir.
- Ubicación del celular: **apaga la ubicación de la cámara** antes de empezar (las fotos guardan
  el GPS en sus metadatos). De todos modos, el pipeline borra los metadatos antes de publicar.

## A. 4 manuscritos (≈20 min)

Escribe a mano, en hojas distintas, **entre 40 y 80 palabras** cada uno (más largo = más trabajo
el sábado, cuando tengas que transcribirlo). Copia el texto de una fuente impresa o web que
tengas delante; no importa si te equivocas al copiar: la referencia será **lo que escribiste**.

| Archivo | Texto real a copiar | Cómo escribirlo |
|---|---|---|
| `manuscrito_01.jpg` | Artículos 1 y 2 (inciso 1) de la Constitución Política del Perú de 1993 | letra cursiva, lapicero azul, hoja rayada |
| `manuscrito_02.jpg` | Coro y primera estrofa del Himno Nacional del Perú | letra de imprenta (separada), lápiz, hoja blanca |
| `manuscrito_03.jpg` | Primeros versos de "Los heraldos negros" de César Vallejo (1918) | cursiva rápida, lapicero negro, hoja cuadriculada |
| `manuscrito_04.jpg` (reserva) | Una receta tuya real (p. ej., ingredientes y pasos de un plato) | tu letra normal, cualquier lapicero |

- Los textos legales y el himno son textos oficiales de uso público; los poemas de Vallejo
  (fallecido en 1938) están en dominio público en el Perú. *Esto último es mi lectura de la
  ley peruana de derecho de autor (vida del autor + 70 años); si quieres total seguridad,
  reemplaza el 03 por otro texto oficial.*
- Si alguien de tu familia quiere escribir uno (letra distinta = mejor prueba), que no ponga
  su nombre ni firme.

**Foto de los manuscritos:** de frente, buena luz, sin sombra fuerte. (La dificultad aquí es la
letra, no la foto.)

## B. 4 fotos de impresos con problemas (≈15 min)

Fotografía **texto impreso de uso público**, en este orden de preferencia (por licencia):

1. Páginas impresas de la Constitución, una ley o una norma (textos oficiales).
2. Afiches o comunicados públicos de una entidad del Estado o municipalidad.
3. Si tienes impresora: imprime 1-2 páginas de las constituciones de 1856 o 1860 de Commons
   (dominio público) y fotografíalas.

No uses periódicos ni libros con derechos de autor, ni boletas o recibos (tienen RUC/DNI).

| Archivo | Problema que debe tener la foto |
|---|---|
| `foto_01.jpg` | **sombra** de tu mano o del celular sobre parte del texto |
| `foto_02.jpg` | **inclinación** fuerte (cámara a unos 30-45° del papel) |
| `foto_03.jpg` | **luz amarilla de noche** (foco o lámpara), sin flash |
| `foto_04.jpg` (reserva) | **papel curvado** (libro abierto o página arrugada) |

El texto tiene que seguir siendo **legible para una persona**: si tú no lo puedes leer, el
sábado tampoco podrás transcribirlo.

## C. Dónde dejarlas

1. Copia las 8 imágenes (JPG originales, sin recortar) a
   `tarea_2/datos/raw/documentos/propias/` con los nombres de las tablas.
2. Llena `trabajo_manual/02_capturas_propias.csv` (una fila por imagen): de dónde copiaste el
   texto o qué fotografiaste, y la fecha.
3. Avísame: yo borro los metadatos, corro el OCR, fijo la muestra 10+10 y hago commit
   **antes** de que empieces las referencias del sábado.
