# Guion del reel (borrador para aprobar) — 01/11/2026

Formato 1080×1920, ~65 s, 7 escenas. La **voz** lleva los números en palabras; el **texto en pantalla** y los
subtítulos (.srt), en cifras. Todas las cifras salen de `web/data/indicadores.json` (año 2023, salvo que se indique otra cosa).

| # | Voz (lo que dice la voz clonada) | En pantalla | Cifra y fuente |
|---|---|---|---|
| 1 | Cada vez que compras algo, pagas IGV. Pero ¿quién sostiene realmente al Estado peruano? | «¿Quién sostiene el fisco peruano?» + boleta con IGV | — |
| 2 | En dos mil veintitrés, el Perú recaudó dieciséis coma siete por ciento de su PIB. La OCDE, treinta y tres coma siete. Los nórdicos, más de cuarenta y uno. | Barras: Perú 16.7 · ALC 21.5 · OCDE 33.7 · nórdicos 41.2 % del PIB | presion_tributaria (OCDE, Global Revenue Statistics) |
| 3 | El IGV recauda tres coma seis veces lo que la renta de las personas. Lo directo lo pagan sobre todo las empresas, y sube y baja con la minería. | «3.6×» · renta de personas 1.8 % del PIB vs 14.4 % en los nórdicos | igv_sobre_renta_personas_PER; renta_personas_pib; directos_pct (41.7 vs 41.2) |
| 4 | La mitad de peruanos con menores ingresos recibe apenas ocho coma tres por ciento del ingreso nacional. Y la propiedad casi no tributa. | 50 % inferior: 8.3 % del ingreso (nórdicos 23.5 %) · propiedad 0.9 % del PIB | bottom50_ingreso (WID, prom. 2019–2023); propiedad_pib |
| 5 | El gasto social es siete coma cinco por ciento del PIB; en la OCDE, casi veintiuno. Entre cincuenta países, recaudar y gastar más se asocia con menos desigualdad. Asociación, no causa. | Gasto social 7.5 vs 20.8 % · dispersión del dashboard | gasto_social_pib (SOCX); correlación parcial −0.53 (n = 50) |
| 6 | Además, el Estado deja de recaudar más de dos por ciento del PIB en exoneraciones y otros beneficios. | «2.16 % del PIB en gasto tributario (2026)» | SUNAT, Informe N.º 000045-2025-SUNAT/1V3000 (27/06/2025) |
| 7 | Explora los datos en el dashboard. El enlace está en la descripción. | URL del dashboard · «Voz generada con IA (clon de mi voz)» · «Fuentes: OCDE, WID.world, Banco Mundial, MEF» | — |

**Extensión:** 156 palabras; a unas 2.5 palabras por segundo da ~62 s. La generación en CPU tomaría ~40 min.

**Aviso fijo en pantalla durante todo el reel:** «Voz generada con IA» (esquina superior) y «Datos: OCDE, WID.world, Banco Mundial» (inferior).

## Música (licencia verificada en Wikimedia Commons; volumen muy por debajo de la voz)

1. **Kevin MacLeod – «Clean Soul»** (5:07, tranquila). CC BY 3.0. https://commons.wikimedia.org/wiki/File:Kevin_MacLeod_-_Clean_Soul.ogg
2. **Kevin MacLeod – «Living Voyage»** (3:29). CC BY 3.0 US. https://commons.wikimedia.org/wiki/File:Living_Voyage_(MacLeod,_Kevin)_(ISRC_USUAN1100594).oga
3. **Kevin MacLeod – «Dream Catcher»** (6:17). CC BY 3.0. https://commons.wikimedia.org/wiki/File:Kevin_MacLeod_-_Dream_Catcher_(cc-by)_(incompetech).ogg

Crédito obligatorio (CC BY), en el último cuadro y en el post: «Música: "<título>" – Kevin MacLeod (incompetech.com), CC BY 3.0».
