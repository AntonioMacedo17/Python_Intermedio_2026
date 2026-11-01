# Guion del reel (borrador para aprobar) — 01/11/2026

Formato 1080×1920, ~65 s, 7 escenas. La **voz** lleva los números en palabras; el **texto en pantalla** y los
subtítulos (.srt), en cifras. Todas las cifras salen de `web/data/indicadores.json` (año 2023, salvo que se indique otra cosa).

| # | Voz (lo que dice la voz clonada) | En pantalla | Cifra y fuente |
|---|---|---|---|
| 1 | Cada vez que compras algo en el Perú, pagas IGV. Pero ¿quién sostiene realmente al Estado? | «¿Quién sostiene el fisco peruano?» + boleta con IGV | — |
| 2 | En dos mil veintitrés, el Perú recaudó dieciséis coma siete por ciento de su PIB. América Latina, veintiuno coma cinco. La OCDE, treinta y tres coma siete. Y los países nórdicos, más de cuarenta y uno. | Barras: 16.7 / 21.5 / 33.7 / 41.2 % del PIB | presion_tributaria (OCDE, Global Revenue Statistics) |
| 3 | El IGV recauda tres coma seis veces lo que el impuesto a la renta de las personas. Los impuestos directos pesan casi como en la OCDE, pero los pagan sobre todo las empresas, y suben o bajan con la minería y el precio de los metales. | «3.6×» · renta de personas 1.8 % del PIB vs 14.4 % en los nórdicos | igv_sobre_renta_personas_PER; renta_personas_pib; directos_pct (41.7 vs 41.2) |
| 4 | Mientras tanto, la mitad de peruanos con menores ingresos recibe apenas ocho coma tres por ciento del ingreso nacional. Y los impuestos a la propiedad recaudan menos de uno por ciento del PIB. | 50 % inferior: 8.3 % del ingreso (nórdicos 23.5 %) · propiedad 0.9 % del PIB | bottom50_ingreso (WID, prom. 2019–2023); propiedad_pib |
| 5 | El gasto social público llega a siete coma cinco por ciento del PIB, frente a casi veintiuno en la OCDE. Entre cincuenta países, los que recaudan y gastan más tienden a ser menos desiguales, incluso con un ingreso por persona parecido. Es una asociación, no una prueba de causa. | Gasto social 7.5 vs 20.8 % · dispersión del dashboard | gasto_social_pib (SOCX); correlación parcial −0.53 (n = 50) |
| 6 | Y el Estado deja de recaudar algo más de dos por ciento del PIB en exoneraciones y otros beneficios, según la estimación oficial para dos mil veintiséis. | «2.16 % del PIB en gasto tributario (2026)» | MMM 2026-2029 (MEF, estimación SUNAT), vía El Comercio |
| 7 | Explora los datos en el dashboard; el enlace está en la descripción. | URL del dashboard · «Voz generada con IA (clon de mi voz)» · «Fuentes: OCDE, WID.world, Banco Mundial, MEF» | — |

**Extensión:** 166 palabras; a unas 2.5 palabras por segundo da ~65 s. La generación en CPU tomaría ~40 min.

**Aviso fijo en pantalla durante todo el reel:** «Voz generada con IA» (esquina superior) y «Datos: OCDE, WID.world, Banco Mundial» (inferior).

## Música (licencia verificada en Wikimedia Commons; volumen muy por debajo de la voz)

1. **Kevin MacLeod – «Clean Soul»** (5:07, tranquila). CC BY 3.0. https://commons.wikimedia.org/wiki/File:Kevin_MacLeod_-_Clean_Soul.ogg
2. **Kevin MacLeod – «Living Voyage»** (3:29). CC BY 3.0 US. https://commons.wikimedia.org/wiki/File:Living_Voyage_(MacLeod,_Kevin)_(ISRC_USUAN1100594).oga
3. **Kevin MacLeod – «Dream Catcher»** (6:17). CC BY 3.0. https://commons.wikimedia.org/wiki/File:Kevin_MacLeod_-_Dream_Catcher_(cc-by)_(incompetech).ogg

Crédito obligatorio (CC BY), en el último cuadro y en el post: «Música: "<título>" – Kevin MacLeod (incompetech.com), CC BY 3.0».
