# Parte 4 · Evaluación: ¿mejoran el MCP y las skills las respuestas de Claude Code?

Este archivo fija el diseño **antes de la primera corrida**: las preguntas, las respuestas esperadas, las
tolerancias y las reglas de calificación. Si después cambia algo, se anota abajo, en «Cambios después de fijar»,
con la fecha y el motivo. Las tolerancias no se cambian después de ver los resultados.

## Preguntas (`preguntas.csv`)

10 preguntas con respuesta numérica verificable: 4 del BCRP (B1–B4), 4 de la ENAHO 2024 (E1–E4) y 2 combinadas
(C1–C2). Las combinadas piden una cifra de cada fuente y una interpretación.

| id | Pide | Respuesta esperada sale de |
|---|---|---|
| B1 | Tasa de referencia de política monetaria, dic. 2024 | BCRP PD04722MM |
| B2 | Inflación Lima Met. (IPC, var. % 12 meses), set. 2026 | BCRP PN01273PM |
| B3 | Tipo de cambio bancario promedio (S/ por US$), set. 2026 | BCRP PN01210PM |
| B4 | Reservas internacionales netas (millones US$), dic. 2025 | BCRP PN00027MM |
| E1 | Pobreza monetaria nacional 2024 | README de la sesión 16 |
| E2 | Pobreza monetaria rural 2024 | README de la sesión 16 |
| E3 | Pobreza monetaria en Cusco 2024 | `referencias/pobreza_departamento_2024.csv` |
| E4 | Pobreza extrema nacional 2024 | README de la sesión 16 |
| C1 | (a) Pobreza en Cajamarca 2024 + (b) crecimiento del PBI real 2024 | CSV de la sesión 16 + BCRP PM04863AA |
| C2 | (a) Pobreza urbana 2024 + (b) inflación Lima Met. dic. 2024 | README de la sesión 16 + BCRP PN01273PM |

Mezclé periodos a propósito: B1 y C2 (b) son de 2024, cifras que un modelo podría recordar. B2, B3 y B4 son de
2025–2026, cifras que un modelo no puede conocer sin consultar una fuente.

## De dónde salen las respuestas esperadas (nunca del MCP, las skills ni el agente)

- **BCRP**: `verdades_bcrp.py` llama directo a la API del BCRP con `httpx`, sin importar `mcp/server.py` y sin
  caché. Guarda en `verdades_bcrp.csv` el valor crudo de la API, los decimales que declara la API (campo `dec`), la
  URL de la API (JSON) y la URL de la página web, para revisarlas a mano. La respuesta esperada es el valor
  redondeado a esos decimales, que es lo que muestra la web.
- **ENAHO**: la respuesta esperada es siempre la **cifra de referencia del curso**: el README de la sesión 16
  (sección «Validación») para nacional, extrema, urbana y rural, y `referencias/pobreza_departamento_2024.csv` para
  los departamentos. `verdades_enaho.py` (escrito aparte, sin importar los scripts de las skills) las recalcula desde
  los microdatos por dos métodos y deja la comparación en `verdades_enaho.csv`. En los 25 departamentos, la mayor
  diferencia con la referencia es 0.518 pp con personas y `facpob07` (Puno) y 0.049 pp con hogares y
  `factor07 × mieperho` (Amazonas); en urbana y rural, 0.065 y 0.142 pp con `facpob07` (salida impresa de
  `verdades_enaho.py`, corrida del 2026-11-08). Con el método de hogares todas las referencias se reproducen con ±0.05 pp (redondeo). Eso confirma que las
  referencias son correctas y que fueron calculadas con la sumaria.
- `armar_preguntas.py` une el texto de cada pregunta con su valor esperado, leído de esos dos CSV. Ninguna
  respuesta esperada está escrita a mano en el CSV de preguntas.

## Tolerancias (fijadas antes de correr)

| Tipo de cifra | Tolerancia | Por qué |
|---|---|---|
| Tasas y variaciones % del BCRP (B1, B2, C1 b, C2 b) | ±0.05 | Redondeo: la API publica con 1 o 2 decimales; quien redondea a 1 decimal se aleja hasta 0.05 |
| Tipo de cambio (B3) | ±0.005 S/ | Redondeo a 2 decimales, la forma usual de reportar el tipo de cambio |
| Reservas en millones de US$ (B4) | ±1 millón | La serie es un entero; solo se admite redondeo |
| Pobreza nacional y extrema nacional (E1, E4) | ±0.1 pp | Lo que pide el Issue. Ambos métodos caen dentro (27.53 % y 27.58 % frente a 27.6 %) |
| Pobreza por departamento o subgrupo (E2, E3, C1 a, C2 a) | ±0.6 pp | 0.05 de redondeo + 0.518 pp, la mayor diferencia documentada entre `facpob07` (el método de nuestras skills, que es correcto) y la referencia, que se calculó con `factor07 × mieperho`. Así no se castiga elegir un método válido. Es una tolerancia amplia: un modelo que recuerde la cifra oficial redondeada también acierta |

## Los dos modos

Los dos modos usan el mismo modelo (`sonnet`), la misma instrucción, el mismo esquema JSON y sesiones independientes
(`claude -p --no-session-persistence`). Cada llamada corre en su propia carpeta temporal nueva.

- **Modo A (sin MCP ni skills)**: `--tools ""` (ninguna herramienta) y `--strict-mcp-config` sin `--mcp-config`, así
  que no hay MCP del BCRP ni conectores de claude.ai. Corre en una carpeta temporal vacía: no puede leer archivos.
- **Modo B (con MCP y skills)**: `--mcp-config .mcp.json --strict-mcp-config` (solo el MCP `bcrp`), las herramientas
  `Skill, Bash, Read, Write, Edit, Glob, Grep` y el MCP, permitidas con `--allowedTools`. Corre en una **copia
  temporal** del proyecto con `datos/` (zips de la ENAHO y GeoJSON), `mcp/` (sin la caché de la API), `.claude/`
  (skills y `settings.local.json`), `.mcp.json`, `pyproject.toml` y `uv.lock`. **No** se copian `evaluacion/`,
  `salidas/`, `referencias/`, `figuras/`, `mapas/`, `informes/`, `evidencias_ia/` ni los `CLAUDE.md`. Sin `salidas/`
  no hay base limpia ni `indicadores.csv`: el agente tiene que correr la skill y procesar los microdatos.
  Para no reinstalar las dependencias en cada copia, `UV_PROJECT_ENVIRONMENT` apunta al `.venv` del proyecto (solo
  contiene paquetes de Python, ninguna respuesta).

### Instrucción (idéntica en ambos modos)

> Responde la pregunta con datos. Pon el número en «valor» (y, si la pregunta pide dos cifras, la segunda en
> «valor_2») en la unidad que pide la pregunta, sin símbolos. Si no puedes saberlo con certeza, pon null: no estimes.
> En «fuente» di de dónde sale cada cifra (código de serie, periodo, archivo o URL). Si la pregunta pide una
> interpretación, escríbela en «interpretacion»; si no, déjala vacía.

## Cómo se califica (`evaluar.py`)

- **B y E**: `correcta` si `|valor − verdad| ≤ tolerancia`. Si `valor` es null es «sin respuesta»; si la llamada falla
  o no devuelve JSON, «error».
- **Combinadas (C1, C2)**: se califican tres cosas y la pregunta es `correcta` solo si pasan las tres:
  1. `valor` dentro de la tolerancia de (a);
  2. `valor_2` dentro de la tolerancia de (b);
  3. **coherencia interpretativa**, con una regla automática sobre el texto de `interpretacion`:
     - *no afirma causalidad*: no aparece ningún verbo causal (`causa…`, `provoc…`, `explic…`, `gener…`, `debe a`,
       `debido a`, `impuls…`, `determin…`, `contribuy…`, `efecto`, `impacto`) salvo que, en los 40 caracteres
       anteriores, haya una negación (`no`, `ni`, `sin`, `nunca`, `tampoco`);
     - *reconoce el distinto nivel de agregación o cobertura*: aparece alguna mención como «agregación», «distinto(s)
       nivel(es)/fuente(s)/escala/cobertura/ámbito», «macro», «microdatos», «encuesta de hogares»,
       «departamental … nacional», «Lima Metropolitana … urbano/nacional», «Cajamarca … nacional/país» o «falacia
       ecológica».
  La regla automática es aproximada (puede fallar con negaciones raras o sinónimos). Por eso `resultados.csv` trae
  el texto completo y una columna vacía `revision_manual_coherencia` para que Antonio la revise a mano; la revisión
  manual no la hace un modelo.
- También se registra: la fuente que declara el agente, las herramientas que usó de verdad (del registro
  `stream-json` de cada sesión: llamadas al MCP, skills cargadas, comandos), el tiempo en segundos y si hubo error o
  respuesta vacía. En el modo B se marca si algún comando o lectura tocó rutas fuera de su copia temporal.

## Limitaciones conocidas antes de correr

1. **Las cifras nacionales están dentro de la skill.** La `description` de `limpiando-enaho` dice «27.6 %» y
   `limpiar.py` trae como referencias de validación 27.6, 24.8 (urbana), 39.3 (rural) y 5.5 (extrema). En el modo B el
   agente puede citarlas sin calcular. Eso es parte del diseño de la skill (valida contra la cifra oficial), pero
   hace que E1, E2, E4 y C2 (a) sean más fáciles en el modo B. E3 (Cusco) y C1 (a) (Cajamarca) no tienen esa ayuda:
   son la prueba más limpia de que la skill procesa los datos.
2. **Sin `referencias/` en la copia**, `mapeando-enaho` no puede hacer su comparación final con la referencia
   (`mapear.py` la lee). Las preguntas no piden mapas, así que no debería afectar.
3. El modo B tiene `Bash`, así que en teoría podría leer archivos fuera de su copia. No se le dice dónde está el
   proyecto original; se revisa en el registro de herramientas si lo hizo.
4. Una sola corrida por pregunta y modo: los modelos no son deterministas y otra corrida puede dar otro resultado.
5. Las cifras recientes del BCRP pueden revisarse después. Las respuestas esperadas se consultaron en la fecha que
   indica `verdades_bcrp.csv`.

## Cambios después de fijar

Ninguno cambia las preguntas, las respuestas esperadas ni las tolerancias. Todos se hicieron después de las
pruebas con 1 pregunta y **antes de la corrida completa**:

1. **2026-11-08 · Entorno de Python del modo B.** En la prueba con E3, el PATH del agente incluía el `.venv` del
   repo (porque el evaluador se lanza con `uv run`), y un error de Python le mostró la ruta real del proyecto. No la
   usó, pero podría haber leído `evaluacion/`. Ahora el evaluador crea un entorno aparte con `uv sync --frozen` en la
   carpeta temporal del sistema (`tarea4_eval_venv`), le quita al agente el `.venv` del repo del PATH y la variable
   `VIRTUAL_ENV`, y marca en `acceso_fuera_copia` si la ruta del repo aparece en alguna salida de herramienta. Esto
   reemplaza lo dicho arriba sobre `UV_PROJECT_ENVIRONMENT` apuntando al `.venv` del proyecto.
2. **2026-11-08 · Caso no previsto en combinadas.** Si el agente da una sola de las dos cifras (la otra en null), la
   pregunta cuenta como «incorrecta» (no como «sin respuesta»). Solo es «sin respuesta» si las dos cifras son null.
3. **Observación de la prueba (no es un cambio):** en la prueba con E3, el modo B acertó (18.5) sin cargar ninguna
   skill: descomprimió la sumaria y calculó con `factor07 × mieperho`. Las skills y el MCP sí estaban disponibles
   (el evento de inicio las lista). No se cambió la instrucción para empujarlo a usarlas: si las activa o no es parte
   de lo que se mide.
