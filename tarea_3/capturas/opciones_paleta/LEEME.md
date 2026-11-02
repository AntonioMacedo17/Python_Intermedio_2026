# Opciones de paleta (bloque C, 01/11/2026): todavía no se aplicó ninguna

Cada opción tiene dos imágenes: `*_portada.png` (modo claro arriba y oscuro abajo) y `*_grafico.png` (serie de presión
tributaria; claro a la izquierda y oscuro a la derecha). `actual_referencia_*` es la paleta publicada hoy, para comparar.

**Diagnóstico de la portada actual:** el color está fijo. `--hero-bg` vale #1F2328 en modo claro y #0B0D10 en modo
oscuro (`web/assets/style.css`), así que se ve casi negra en ambos.

| | Portada (claro / oscuro) | Perú | América Latina | OCDE | Nórdicos |
|---|---|---|---|---|---|
| 1 Marfil | marfil #FAF7F0, texto azul #0B3B6F, línea roja / azul profundo #1A2B45 | #C8102E | #B8862A | #1D3A66 | #4A90D9 |
| 2 Azul | azul medio #1F5FA6, texto blanco, línea roja / #1B4F8A | #D62839 | #E0B032 | #1A3E6E | #79B4E6 |
| 3 Granate | vino #6D1A36, texto crema #F5EBDD, cifra dorada / #5A1530 | #C8102E | #C9A13B | #24406F | #7FA7D6 |

Modo oscuro (las tres): Perú #FF6B6B o #FF7A85, ALC #F2C14E, OCDE #7FA8E8 o #6E9BE8, nórdicos #C9DCF5.

**Validación** (script propio en Python, separación OKLab ×100, con simulación de protanopia, deuteranopia y tritanopia):
el par más cercano entre los 4 grupos queda en 11.8 (opción 1), 15.4 (opción 2) y 13.2 (opción 3) en modo claro, y en
12.6–13.2 en modo oscuro. Todos superan el umbral de 8. Sobre fondo blanco, el amarillo y el celeste tienen contraste
menor que 3:1. Por eso los gráficos conservan leyenda, etiquetas y la tabla de datos.

Se evitaron el turquesa, el naranja y el morado. Las tres opciones usan rojo para el Perú, dorado para América
Latina y dos azules de distinta claridad para la OCDE y los nórdicos: con el rojo, un verde no pasaba la prueba
de deuteranopia.
