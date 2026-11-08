---
name: limpiando-enaho
description: Limpia y une los módulos 34 (sumaria) y 02 (miembros) de la ENAHO 2024 del INEI y arma una base de personas con pobreza monetaria y factor de expansión facpob07, validada contra la cifra oficial (27.6 %). Úsala cuando pidan limpiar, unir o analizar la ENAHO, o calcular la pobreza o pobreza extrema del Perú por departamento, región, área urbana o rural, sexo o edad.
---

# Limpiar la ENAHO 2024

Todas las rutas son relativas a `tarea_4/` (la carpeta del proyecto). Ninguna cifra se escribe a mano:
todas salen de `salidas/validacion.txt` o `salidas/indicadores.csv`.

## Pasos

1. Comprueba que existan `datos/966-Modulo34.zip` y `datos/966-Modulo02.zip` (sin descomprimir).
   Si faltan, pide al usuario bajarlos del INEI (966 = ENAHO 2024):
   - https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip
   - https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip
2. Si `salidas/personas_2024.parquet` ya existe y `salidas/validacion.txt` dice
   «TODAS LAS VALIDACIONES ESENCIALES PASAN», puedes reutilizarla. Si no, corre exactamente:

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py
   ```

3. Lee `salidas/validacion.txt`. Si el script termina con error (exit 1) o alguna validación esencial dice
   FALLA, **detente y dile al usuario qué falló**. No corrijas ni ajustes nada para que coincida con la referencia.
4. Para responder cifras usa `salidas/indicadores.csv` (nacional, área, sexo, grupo de edad y departamento,
   con `n_obs` y `poblacion_expandida`). Para otros cortes, calcula desde `salidas/personas_2024.parquet`
   con media ponderada por `facpob07`: `(pobre * facpob07).sum() / facpob07.sum()`. Nunca promedios simples.
5. Al dar una cifra, cita: «INEI, ENAHO 2024 (módulos 34 y 02), personas residentes habituales, ponderado con
   facpob07». Reporta con un decimal (p. ej., 27.5 %) y, si importa, el n de observaciones.
6. Antes de usar una variable que no esté en la base o de interpretar un código, lee
   [reference.md](reference.md) (diccionario y trampas).

## Qué hace el script (no lo reescribas; córrelo)

1. Lee `sumaria-2024.dta` y `enaho01-2024-200.dta` directo desde los zip, con
   `convert_categoricals=False` y las llaves (`conglome`, `vivienda`, `hogar`, `codperso`, `ubigeo`) como texto.
2. Pasa las columnas a minúscula sin tildes (`aÑo` → `anio`).
3. Filtra residentes habituales: `((p204 == 1) & (p205 == 2)) | ((p204 == 2) & (p206 == 1))`.
4. Une personas con sumaria: `merge(on=[conglome, vivienda, hogar], validate="m:1", indicator=True)`.
5. Construye `departamento = ubigeo[:2]`, `area` (urbana si `estrato <= 5`), `pobre = pobreza <= 2`,
   `pobre_extremo = pobreza == 1`, `sexo` (p207), `edad` (p208a) y `grupo_edad` (0-14, 15-29, 30-44, 45-59, 60 y más).
6. Valida (PASA/FALLA) y solo si todo lo esencial pasa escribe la base y los indicadores.

## Salidas

| Archivo | Contenido | ¿Se versiona? |
|---|---|---|
| `salidas/personas_2024.parquet` | 108,664 residentes habituales con pobreza y factores | No (microdato) |
| `salidas/validacion.txt` | PASA/FALLA de cada chequeo y por qué difieren los dos métodos | Sí |
| `salidas/indicadores.csv` | Pobreza y pobreza extrema ponderadas, con n y población expandida | Sí |

## Reglas

- Pondera siempre con `facpob07` a nivel de personas. `factor07` es de hogares (solo para la sumaria).
- Las relaciones con otras variables son asociaciones, no causas.
- Si un departamento o grupo tiene pocas observaciones, dilo: la ENAHO es una muestra.
