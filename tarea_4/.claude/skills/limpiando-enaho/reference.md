# ENAHO 2024 · Diccionario de variables usadas y trampas

Fuente de las etiquetas: las *value labels* y *variable labels* de los propios `.dta` del INEI
(`966-Modulo34/sumaria-2024.dta` y `966-Modulo02/enaho01-2024-200.dta`), leídas con pandas. El diccionario
oficial completo viene en el zip del módulo 34 (`Diccionario2024.pdf`).

## Archivos

| Archivo (dentro del zip) | Una fila por | Filas | Llaves | Factor |
|---|---|---|---|---|
| `966-Modulo34/sumaria-2024.dta` | hogar | 33,691 | `conglome`, `vivienda`, `hogar` | `factor07` |
| `966-Modulo02/enaho01-2024-200.dta` | persona | 117,721 | las tres + `codperso` | `facpob07` |

## Llaves y ubicación

| Variable | Etiqueta INEI | Tipo | Nota |
|---|---|---|---|
| `conglome` | número de conglomerado | texto, 6 dígitos | conservar ceros iniciales (`'017330'`) |
| `vivienda` | número de selección de vivienda | texto, 3 dígitos | |
| `hogar` | número secuencial del hogar | texto, 2 dígitos | |
| `codperso` | número de orden de la persona | texto, 2 dígitos | solo en módulo 02 |
| `ubigeo` | ubicación geográfica | texto, 6 dígitos | `ubigeo[:2]` = departamento (01 a 25) |
| `dominio` | dominio geográfico | entero | 1 costa norte, 2 costa centro, 3 costa sur, 4 sierra norte, 5 sierra centro, 6 sierra sur, 7 selva, 8 Lima Metropolitana |
| `estrato` | estrato geográfico (tamaño del centro poblado) | entero | ver abajo |

### `estrato`

| Código | Etiqueta | Área (regla del curso) |
|---|---|---|
| 1 | de 500 000 a más habitantes | urbana |
| 2 | de 100 000 a 499 999 habitantes | urbana |
| 3 | de 50 000 a 99 999 habitantes | urbana |
| 4 | de 20 000 a 49 999 habitantes | urbana |
| 5 | de 2 000 a 19 999 habitantes | urbana |
| 6 | de 500 a 1 999 habitantes | rural |
| 7 | área de empadronamiento rural (AER) compuesto | rural |
| 8 | área de empadronamiento rural (AER) simple | rural |

## Pobreza (sumaria, nivel hogar)

| Variable | Etiqueta | Códigos |
|---|---|---|
| `pobreza` | pobreza | 1 pobre extremo · 2 pobre no extremo · 3 no pobre |
| `mieperho` | total de miembros del hogar | entero |
| `factor07` | factor de expansión anual, proyecciones CPV-2007 (hogares) | real > 0 |

Derivadas: `pobre = pobreza <= 2` (pobreza monetaria total); `pobre_extremo = pobreza == 1`.
Todos los miembros de un hogar comparten su condición de pobreza.

## Personas (módulo 02)

| Variable | Etiqueta | Códigos |
|---|---|---|
| `p203` | relación de parentesco con el jefe | 0 panel, 1 jefe/jefa, 2 esposo(a), 3 hijo(a), 4 yerno/nuera, 5 nieto(a), 6 padres/suegros, 7 otros parientes, 8 trabajador del hogar, 9 pensionista, 10 otros no parientes, 11 hermano(a) |
| `p204` | ¿es miembro del hogar? | 1 sí · 2 no |
| `p205` | ¿se encuentra ausente del hogar 30 días o más? | 1 sí · 2 no |
| `p206` | ¿está presente en el hogar 30 días o más? (para no miembros) | 1 sí · 2 no |
| `p207` | sexo | 1 hombre · 2 mujer |
| `p208a` | ¿qué edad tiene en años cumplidos? | años |
| `facpob07` | factor de expansión anual de población, proyecciones CPV-2007 | real > 0 |

**Residente habitual** = miembro no ausente 30+ días, o no miembro presente 30+ días:
`((p204 == 1) & (p205 == 2)) | ((p204 == 2) & (p206 == 1))` → 108,664 de 117,721 filas.

## Variables de la base limpia (`salidas/personas_2024.parquet`)

`anio, mes, conglome, vivienda, hogar, codperso, ubigeo, departamento, departamento_nombre, dominio, estrato,
area, sexo, edad, grupo_edad, pobreza, pobre, pobre_extremo, facpob07, factor07, mieperho`.
Grupos de edad: 0-14, 15-29, 30-44, 45-59, 60 y más (60 es el umbral de persona adulta mayor en el Perú).

## Trampas de la ENAHO

1. **Ceros iniciales.** `ubigeo`, `conglome`, `codperso` son texto. Si se leen como número, `010101` se vuelve
   `10101` y Amazonas (01) desaparece o se confunde. Nunca convertir llaves a entero.
2. **La columna del año** llega como `aÑo` (y según la codificación, como `a�o`). El script la renombra `anio`.
3. **Dos sumarias en el zip.** `sumaria-2024.dta` (estándar) y `sumaria-2024-12g.dta` (12 grupos de gasto).
   Se usa la estándar; ambas dan la misma pobreza nacional.
4. **Etiquetas de Stata.** Con `convert_categoricals=True` los códigos se vuelven texto y `pobreza <= 2` falla.
   Leer siempre con `convert_categoricals=False`.
5. **No filtrar residentes** sobrestima la población: el módulo 02 incluye visitas y ausentes (117,721 filas).
   Además, 3,966 filas tienen `p204` a `p208a` nulos; el filtro las excluye.
6. **Factor equivocado.** `facpob07` es para personas; `factor07` es para hogares. Para llevar la sumaria a
   personas, usar `factor07 × mieperho`. Nunca promedios simples.
7. **Dos métodos, dos cifras.** Personas con `facpob07` da 27.53 % y sumaria con `factor07 × mieperho` da
   27.58 %; ambos redondean a 27.6 %. Las referencias de urbana (24.8), rural (39.3) y Lima Met. (28.2)
   coinciden con el método de la sumaria; con personas dan 24.74, 39.44 y 28.03 (ver `salidas/validacion.txt`).
8. **`ubigeo` y `estrato` están en ambos módulos.** En la unión se comprobó que coinciden en todas las filas.
9. **Lima y Callao.** El departamento 15 (Lima) y la Provincia Constitucional del Callao (07) son unidades
   distintas. `dominio == 8` (Lima Metropolitana) es otro recorte: en la base incluye todo Callao (07) y
   parte de Lima (15), así que no es igual al departamento 15.
10. **Muestra, no censo.** Las estimaciones por departamento o grupos chicos tienen error muestral; esta base
    no calcula intervalos de confianza (requeriría el diseño muestral: estrato y conglomerado).
