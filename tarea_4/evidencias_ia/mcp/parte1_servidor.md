 ▐▛███▛█   Claude Code v2.1.318
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~\repos\Python_Intermedio_2026


> Hola ccode. Hoy hacemos la Tarea 4 completa (Issue #201:                      
  https://github.com/d2cml-ai/Data-Science-Python/issues/201). La entrega es    
  HOY domingo 08/11 a las 23:59. Trabaja con mucho rigor y por partes, y        
  avísame al terminar cada una, y explicame brevemente siempre.                 
                                                                                
  CONTEXTO: lee el enunciado completo del Issue #201 (si no puedes abrirlo,     
  avísame y te pego el texto). Clona el repo del curso como referencia de solo  
  lectura en C:\Users\Antonio Macedo\repos\Data-Science-Python (o haz git pull  
  si ya existe) y lee sessions/04-mcp-claude-code/proyecto (README, server.py,  
  test_server.py, evaluar.py, preguntas.csv) y sessions/16-skills-enaho (README 
  y referencias/).                                                              
                                                                                
  PARTE 0 · PREPARAR                                                            
  1. En tarea_4/ crea la estructura del Issue: README.md, pyproject.toml,       
  .mcp.json, .gitignore, mcp/, .claude/skills/, datos/, salidas/, figuras/,     
  mapas/, evaluacion/, informes/ y evidencias_ia/ con las subcarpetas mcp,      
  skills, integracion y evaluacion.                                             
  2. Un solo entorno uv en tarea_4/ con fastmcp>=4,<5, httpx, pandas, pyarrow,  
  geopandas, matplotlib, y pytest en el grupo dev. Verifica que uv esté         
  instalado.                                                                    
  3. .gitignore: datos/ (en cualquier carpeta), .venv/ y cachés. Nada de claves 
  y ningún microdato en el repo.                                                
  4. Crea tarea_4/CLAUDE.md con estas reglas: ninguna cifra escrita a mano ni   
  inventada (todo sale de código y se valida); ponderar siempre con el factor   
  correcto; asociación, no causalidad; citar código de serie, periodo y fuente; 
  commits descriptivos por avance; si algo falla, decirlo en vez de inventar.   
  5. Datos ENAHO: ya dejé 966-Modulo34.zip y 966-Modulo02.zip en                
  tarea_4/datos/. Verifica que estén completos y se puedan leer.                
  6. Prueba que la API del BCRP responda desde esta computadora (por ejemplo    
  PN01273PM de 2025-1 a 2025-3). Si no responde, avísame.                       
  7. Commit: "Tarea 4: estructura inicial".                                     
                                                                                
  PARTE 1 · SERVIDOR MCP DEL BCRP (meta: 10 passed)                             
  1. Copia server.py y test_server.py de la sesión 04 a tarea_4/mcp/. No        
  modifiques las 8 pruebas originales (solo los imports si hace falta). No      
  crees mcp/__init__.py: la carpeta se llama igual que el paquete mcp que usa   
  FastMCP.                                                                      
  2. Completa los TODO: serie, resumen, una herramienta propia útil (por        
  ejemplo comparar_periodos o correlacion entre dos series; elige la más útil   
  para analizar inflación y actividad económica y explícame por qué), un        
  recurso bcrp://serie/{codigo} y un prompt informe(tema). Todas las cuentas en 
  Python, con reintentos y caché para la API.                                   
  3. Escribe 2 pruebas nuevas para la herramienta propia, sin tocar las 8       
  originales. Meta: uv run pytest -q → 10 passed. Guarda la salida en           
  salidas/pytest_mcp.txt.                                                       
  4. Crea tarea_4/.mcp.json con el servidor bcrp (uv run mcp/server.py, con la  
  ruta correcta), sin claves.                                                   
  5. Commit: "Parte 1: servidor MCP del BCRP con 10 pruebas".                   
  6. Al terminar dime: el resultado de pytest, qué hace la herramienta propia y 
  cómo pruebo el MCP en Claude Code.                                            

● Empiezo por leer el Issue y preparar el repo de referencia.

  Ran 2 shell commands (ctrl+o to expand)

● uv no está instalado y gh tampoco. Mientras tanto leo el Issue por la API
  pública y clono el repo.

  Read 1 file, ran 3 shell commands (ctrl+o to expand)

● Issue leído y repo clonado. Ahora los archivos de referencia.

  Ran 3 shell commands (ctrl+o to expand)

● Todo leído. Mientras tanto avanzo con lo que no requiere uv: estructura,
  verificación de los zips y prueba de la API del BCRP.

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4"
      mkdir -p mcp .claude/skills salidas figuras mapas evaluacion informes
      evidencias_ia/{mcp,skill…)
  ⎿  datos/966-Modulo34.zip integridad: OK
         966-Modulo34/ 0
         966-Modulo34/ConstVarGasto-Metodologia actualizada.zip 24486
     … +45 lines (ctrl+o to expand)
  ⎿  Created tarea_4\.claude\skills\.gitkeep (+0 -0)
  ⎿  Created tarea_4\evaluacion\.gitkeep (+0 -0)
  ⎿  Created tarea_4\evidencias_ia\evaluacion\.gitkeep (+0 -0)
  ⎿  Created tarea_4\evidencias_ia\integracion\.gitkeep (+0 -0)
  ⎿  Created tarea_4\evidencias_ia\mcp\.gitkeep (+0 -0)
  ⎿  … 5 more files changed

● Los zips están íntegros y la API del BCRP responde. Falta uv para crear el
  entorno, y tu CLAUDE.md dice que te consulte antes de instalar cosas.

● User answered Claude's questions:
  ⎿  · uv no está instalado en esta computadora y la tarea lo exige (entorno, 
     pytest y el MCP en .mcp.json). ¿Lo instalo con el instalador oficial de 
     Astral? Es un ejecutable chico (~30 MB) que se guarda en tu carpeta de 
     usuario (%USERPROFILE%\.local\bin), sin permisos de administrador. → Sí, 
     instálalo (Recomendado)

  Ran 1 shell command (ctrl+o to expand)

● uv 0.13.7 instalado. Ahora creo los archivos de configuración.

● Write(tarea_4\pyproject.toml)
  ⎿  Wrote 22 lines to tarea_4\pyproject.toml
       1 [project]
       2 name = "tarea-4-agente-socioeconomico"
       3 version = "0.1.0"
       4 description = "Agente de investigación socioeconómica: MCP del B
         CRP + Skills de ENAHO 2024 (Tarea 4, Python Intermedio)"
       5 requires-python = ">=3.11"
       6 dependencies = [
       7     "fastmcp>=4,<5",
       8     "httpx",
       9     "pandas",
     … +13 lines (ctrl+o to expand)

● Write(tarea_4\.gitignore)
  ⎿  Wrote 22 lines to tarea_4\.gitignore
       1 # Microdatos y descargas: nunca al repo (en cualquier carpeta, p
         . ej. datos/ y mcp/datos/)
       2 datos/
       3 **/datos/
       4 
       5 # Entorno y cachés
       6 .venv/
       7 __pycache__/
       8 *.py[cod]
       9 .pytest_cache/
     … +13 lines (ctrl+o to expand)

● Write(tarea_4\CLAUDE.md)
  ⎿  Wrote 19 lines to tarea_4\CLAUDE.md
       1 # Reglas del proyecto · Tarea 4 (agente de investigación socioec
         onómica)
       2 
       3 Estas reglas valen para cualquier sesión de Claude Code abierta 
         en `tarea_4/`.
       4 
       5 1. **Ninguna cifra escrita a mano ni inventada.** Todo número sa
         le de código (herramientas MCP del BCRP o
       6    scripts de las Skills de ENAHO) y se valida antes de usarlo. 
         Si una cifra no viene de una salida
     … +13 lines (ctrl+o to expand)

● Bash(export PATH="$HOME/.local/bin:$PATH"; cd "/c/Users/Antonio
      Macedo/repos/Python_Intermedio_2026/tarea_4"; uv sync 2>&1 | tail -15; uv
      run python -c "import fastm…)
  ⎿   + referencing==0.37.0
      + rich==15.0.0
      + rich-rst==2.2.0
     … +13 lines (ctrl+o to expand)
  ⎿  1 file changed (binary, mode only or too large to show)
  ⎿  (timeout 10m)

● Entorno listo (fastmcp 4.1.6). Ahora verifico que los .dta se lean bien, con
  las llaves como texto.

  Ran 1 shell command (ctrl+o to expand)

● Las dos bases cargan bien, con 33,691 hogares y 117,721 personas que coinciden
  con la sesión 16, y las llaves conservan sus ceros iniciales. Ahora escribo
  el README inicial y .mcp.json, y después hago el commit.

● Write(tarea_4\README.md)
  ⎿  Wrote 31 lines to tarea_4\README.md
       1 # Tarea 4 · Agente de investigación socioeconómica (MCP del BCRP
          + Skills de ENAHO 2024)
       2 
       3 > En construcción. Este README se completa al cierre de la tarea
          con arquitectura, instalación,
       4 > reproducción, evaluación, limitaciones y evidencias del uso de
          IA.
       5 
       6 ## Estructura
       7 
     … +24 lines (ctrl+o to expand)

● Write(tarea_4\.mcp.json)
  ⎿  Wrote 10 lines to tarea_4\.mcp.json
       1 {
       2   "mcpServers": {
       3     "bcrp": {
       4       "type": "stdio",
       5       "command": "uv",
       6       "args": ["run", "mcp/server.py"],
       7       "env": {}
       8     }
       9   }
      10 }

  Ran 2 shell commands (ctrl+o to expand)

● Parte 0 está lista (commit 4b0e012): instalé uv 0.13.7 con las dependencias
  fijadas, verifiqué los zips y la API del BCRP, y confirmé que datos/ queda
  fuera de git. Ahora reviso cómo FastMCP 4 declara recursos y prompts antes de
  empezar la Parte 1.

  Ran 2 shell commands (ctrl+o to expand)

● La API de FastMCP 4 es la esperada: @mcp.resource(uri) y @mcp.prompt. Copio
  los dos archivos sin cambios y corro las pruebas como punto de partida.
  Debería dar 1 passed y 7 failed.

● Bash(export PATH="$HOME/.local/bin:$PATH"; cd "/c/Users/Antonio
      Macedo/repos/Python_Intermedio_2026/tarea_4";
      SRC="../../Data-Science-Python/sessions/04-mcp-claude-c…)
  ⎿  E        +      and   <coroutine object _con_cliente at 0x000001F373C7
     B4C0> = _con_cliente(<function test_un_prompt.<locals>.<lambda> at 0x0
     00001F373C762A0>)
     … +21 lines (ctrl+o to expand)
  ⎿  Created tarea_4\mcp\server.py (+107 -0)
        1 +"""Servidor MCP del BCRP. Empiecen aquí: buscar_series ya func
          +iona; completen los TODO hasta que pasen las pruebas.         
        2 +                                                              
        3 +    uv run pytest                                           # 
          +el contrato: las 8 pruebas deben pasar                        
        4 +    uv run server.py                                        # 
          +el servidor, por stdio                                        
        5 +    claude mcp add --scope project bcrp -- uv run server.py # 
          +conectarlo a Claude Code                                      
        6 +                                                              
        7 +Las cuentas las hace Python, no el modelo: así cada cifra sale
          + de una llamada que se puede repetir.                         
        8 +"""                                                           
        9 +import re                                                     
       10 +import unicodedata                                            
       11 +from functools import cache                                   
       12 +from pathlib import Path                                      
       13 +                                                              
       14 +import httpx                                                  
       15 +import pandas as pd                                           
       16 +from fastmcp import FastMCP                                   
       17 +from fastmcp.exceptions import ToolError                      
       18 +                                                              
       19 +AQUI = Path(__file__).parent                                  
       20 +CATALOGO = AQUI / "datos" / "catalogo_bcrp.csv"               
       21 +URL_CATALOGO = "https://estadisticas.bcrp.gob.pe/estadisticas/
          +series/metadata"                                              
       22 +API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/ap
          +i"                                                            
       23 +SOLO_LECTURA = {"readOnlyHint": True, "openWorldHint": True}  
       24 +                                                              
       25 +mcp = FastMCP("bcrp", instructions=(                          
       26 +    "Series oficiales del Banco Central de Reserva del Perú (B
          +CRP). Primero busca el código con buscar_series; "            
       27 +    "luego usa resumen para variaciones, promedios y extremos,
          + y serie para los datos. No calcules a mano: "                
       28 +    "cita siempre el código de la serie y el periodo."))      
       29 +                                                              
       30 +                                                              
       31 +def _sin_tildes(s):                                           
       32 +    return unicodedata.normalize("NFD", str(s).lower()).encode
          +("ascii", "ignore").decode()                                  
       33 +                                                              
       34 +                                                              
       35 +@cache                                                        
       36 +def catalogo():                                               
       37 +    """El catálogo oficial: 17 mil series en unos 7 MB. Se baj
          +a una vez y queda en datos/."""                               
       38 +    if not CATALOGO.exists():                                 
       39 +        CATALOGO.parent.mkdir(exist_ok=True)                  
       40 +        r = httpx.get(URL_CATALOGO, timeout=120)              
     … 67 more lines (ctrl+o to expand)
  ⎿  Created tarea_4\mcp\test_server.py (+71 -0)
       1 +"""El contrato del servidor: si estas pruebas pasan, Claude Cod
         +e y evaluar.py pueden usarlo.                                  
       2 +                                                               
       3 +    uv run pytest -q                                           
       4 +                                                               
       5 +Llaman al servidor en memoria, igual que lo haría Claude Code, 
         +y piden datos reales al BCRP.                                  
       6 +"""                                                            
       7 +import asyncio                                                 
       8 +                                                               
       9 +import pytest                                                  
      10 +from fastmcp import Client                                     
      11 +from fastmcp.exceptions import ToolError                       
      12 +                                                               
      13 +from server import mcp                                         
      14 +                                                               
      15 +                                                               
      16 +async def _con_cliente(f):                                     
      17 +    async with Client(mcp) as c:                               
      18 +        return await f(c)                                      
      19 +                                                               
      20 +                                                               
      21 +def llamar(herramienta, **args):                               
      22 +    return asyncio.run(_con_cliente(lambda c: c.call_tool(herra
         +mienta, args))).data                                           
      23 +                                                               
      24 +                                                               
      25 +def test_buscar_encuentra_el_ipc():                            
      26 +    r = llamar("buscar_series", texto="ipc 12 meses", limite=5)
      27 +    assert "PN01273PM" in [x["codigo"] for x in r]             
      28 +    assert {"codigo", "nombre", "frecuencia"} <= r[0].keys()   
      29 +                                                               
      30 +                                                               
      31 +def test_cuatro_herramientas_como_minimo():                    
      32 +    nombres = {t.name for t in asyncio.run(_con_cliente(lambda 
         +c: c.list_tools()))}                                           
      33 +    assert {"buscar_series", "serie", "resumen"} <= nombres    
      34 +    assert len(nombres) >= 4, "falta su herramienta propia"    
      35 +                                                               
      36 +                                                               
      37 +def test_serie_mensual():                                      
      38 +    r = llamar("serie", codigo="PN01271PM", desde="2025-01", ha
         +sta="2025-12")                                                 
      39 +    assert len(r["datos"]) == 12                               
      40 +    assert r["datos"][0]["periodo"] == "2025-01"               
     … 31 more lines (ctrl+o to expand)
  ⎿  (timeout 5m)

● El punto de partida es 1 passed y 7 failed; el catálogo tiene cuatro
  frecuencias y elegí la serie mensual PN01728AM. Antes de escribir el código,
  confirmo cómo la API pide fechas para series trimestrales y anuales y qué
  responde ante un código inexistente.

  Ran 1 shell command (ctrl+o to expand)
● El trimestre se pide como 2025-1 pero llega como T1.25, y la API siempre
  responde text/html, así que el código intentará leer el JSON sin fiarse del
  tipo de contenido. Valido el código contra el catálogo antes de escribir el
  servidor.

  Read 2 files, ran 1 shell command (ctrl+o to expand)

● Verifiqué que las cuatro páginas del BCRP responden 200, así que pueden
  citarse como fuente comprobable. Ahora escribo server.py.

● Write(tarea_4\mcp\server.py)
  ⎿  Added 283 lines, removed 26 lines
       1 -"""Servidor MCP del BCRP. Empiecen aquí: buscar_series ya funci
         -ona; completen los TODO hasta que pasen las pruebas.           
       1 +"""Servidor MCP del BCRP (Tarea 4). Basado en el proyecto de la
         + Sesión 04; buscar_series viene de la sesión.                  
       2  
       3 -    uv run pytest                                           # e
         -l contrato: las 8 pruebas deben pasar                          
       4 -    uv run server.py                                        # e
         -l servidor, por stdio                                          
       5 -    claude mcp add --scope project bcrp -- uv run server.py # c
         -onectarlo a Claude Code                                        
       3 +    uv run pytest -q                                        # d
         +esde tarea_4/: 8 pruebas originales + 2 propias                
       4 +    uv run mcp/server.py                                    # e
         +l servidor, por stdio                                          
       5 +    claude mcp add --scope project bcrp -- uv run mcp/server.py
         +   # o usar el .mcp.json de tarea_4/                           
       6  
       7 +Herramientas: buscar_series, serie, resumen y correlacion (prop
         +ia). Recurso: bcrp://serie/{codigo}.                           
       8 +Prompt: informe(tema).                                         
       9 +                                                               
      10  Las cuentas las hace Python, no el modelo: así cada cifra sale 
          de una llamada que se puede repetir.
      11 +Las descargas tienen reintentos con espera creciente y una cach
         +é en disco (datos/cache_api/, ignorada por git).               
      12  """
      13 +import calendar                                                
      14 +import hashlib                                                 
      15 +import json                                                    
      16 +import math                                                    
      17  import re
      18 +import time                                                    
      19  import unicodedata
      20  from functools import cache
      21  from pathlib import Path
     ...
      23  import httpx
      24  import pandas as pd
      25  from fastmcp import FastMCP
      17 -from fastmcp.exceptions import ToolError                       
      26 +from fastmcp.exceptions import ResourceError, ToolError        
      27  
      28  AQUI = Path(__file__).parent
      29  CATALOGO = AQUI / "datos" / "catalogo_bcrp.csv"
      30 +CACHE_API = AQUI / "datos" / "cache_api"                       
      31  URL_CATALOGO = "https://estadisticas.bcrp.gob.pe/estadisticas/s
          eries/metadata"
      32  API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api
          "
      33 +WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series"   
      34  SOLO_LECTURA = {"readOnlyHint": True, "openWorldHint": True}
      35  
      36 +REINTENTOS = 4          # intentos por pedido a la API         
      37 +ESPERA_BASE = 1.5       # segundos; se duplica en cada reintent
         +o (1.5, 3, 6)                                                  
      38 +CACHE_HORAS = 12        # una respuesta guardada se reutiliza d
         +urante 12 h (los datos recientes se revisan)                   
      39 +                                                               
      40 +MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun
         +": 6, "jul": 7, "ago": 8,                                      
      41 +         "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12}  
      42 +WEB_FRECUENCIA = {"diaria": "diarias", "mensual": "mensuales", 
         +"trimestral": "trimestrales", "anual": "anuales"}              
      43 +                                                               
      44  mcp = FastMCP("bcrp", instructions=(
      45      "Series oficiales del Banco Central de Reserva del Perú (BC
          RP). Primero busca el código con buscar_series; "
      27 -    "luego usa resumen para variaciones, promedios y extremos, 
         -y serie para los datos. No calcules a mano: "                  
      28 -    "cita siempre el código de la serie y el periodo."))       
      46 +    "luego usa resumen para variaciones, promedios y extremos, 
         +serie para los datos y correlacion para medir "                
      47 +    "la asociación entre dos series en los mismos periodos. No 
         +calcules a mano: cita siempre el código de la "                
      48 +    "serie, el periodo y la fuente (URL). Si una herramienta fa
         +lla o no hay datos, dilo en vez de estimar."))                 
      49  
      50  
      51  def _sin_tildes(s):
     ...
       98      return [_ficha(c) for c in orden.sort_values(["vieja", "la
           rgo"]).head(limite).codigo]
       99  
      100  
       81 -# TODO 1 · serie(codigo, desde, hasta) -> {"codigo", "nombre",
          - "frecuencia", "datos": [{"periodo", "valor"}], "fuente"}     
       82 -#   La API se llama así: f"{API}/{codigo}/json/{desde}/{hasta}
          -" y responde                                                  
       83 -#   {"config": {...}, "periods": [{"name": "Ene.2025", "values
          -": ["0.81"]}, ...]}                                           
       84 -#   - Fechas que pide la API: 2025-1 (mensual y trimestral), 2
          -025-01-15 (diaria), 2025 (anual).                             
       85 -#   - Nombres que devuelve: "Ene.2025" (mensual), "01.Oct.26" 
          -(diaria), "T1.25" (trimestral), "2025" (anual).               
       86 -#     Setiembre viene como "Set". Devuelvan el periodo como "2
          -025-01", "2026-10-01", "2025-T1" o "2025".                    
       87 -#   - Salten los valores "n.d." y usen la frecuencia de _ficha
          -(codigo) para saber qué formato pedir.                        
       88 -#   - Si recibe muchos pedidos seguidos, la API responde una p
          -ágina HTML en vez de JSON: esperen unos segundos y            
       89 -#     reintenten (y guarden en caché lo que ya bajaron).      
       90 -#   - Un código que no existe debe dar un ToolError que diga e
          -l código.                                                     
      101 +# ------------------------------------------------------------
          +---------------------------------------------------           
      102 +# Fechas: lo que escribe el usuario -> lo que pide la API; lo 
          +que devuelve la API -> periodo normalizado                    
      103 +# ------------------------------------------------------------
          +---------------------------------------------------           
      104  
       92 -# TODO 2 · resumen(codigo, desde, hasta): primero, ultimo, cam
          -bio, variacion_pct, promedio, maximo y minimo                 
       93 -#   (los tres últimos con su periodo). Úsenla para que el mode
          -lo nunca haga cuentas a mano.                                 
      105 +def _fecha_api(fecha: str, frecuencia: str, fin: bool = False)
          + -> str:                                                      
      106 +    """Convierte "2025", "2025-03", "2025-T1" o "2025-03-15" a
          +l formato que pide la API según la frecuencia.                
      107  
       95 -# TODO 3 · Una herramienta suya, bien descrita. Ideas:        
       96 -#   - comparar_paises con la API del Banco Mundial, que tampoc
          -o pide clave:                                                 
       97 -#     https://api.worldbank.org/v2/country/PER;CHL;COL/indicat
          -or/NY.GDP.MKTP.KD.ZG?format=json&date=2015:2025               
       98 -#   - correlacion(codigo_a, codigo_b, desde, hasta)           
       99 -#   - grafico(codigo, desde, hasta) que guarde un PNG en salid
          -as/ y devuelva la ruta                                        
      108 +    Mensual y trimestral: "2025-3" (mes o trimestre); diaria: 
          +"2025-03-15"; anual: "2025".                                  
      109 +    Si falta precisión, `fin` decide si se toma el inicio o el
          + final del periodo (p. ej. "2025" -> dic. o 31-dic).          
      110 +    """                                                       
      111 +    m = re.fullmatch(r"\s*(\d{4})(?:-(T)?(\d{1,2}))?(?:-(\d{1,
          +2}))?\s*", str(fecha), flags=re.IGNORECASE)                   
      112 +    if not m:                                                 
      113 +        raise ToolError(f"Fecha {fecha!r} no válida. Usen 2025
          +, 2025-03, 2025-T1 o 2025-03-15.")                            
      114 +    anio, es_trim, parte, dia = int(m[1]), bool(m[2]), m[3], m
          +[4]                                                           
      115 +    parte = int(parte) if parte else None                     
      116 +    if es_trim and not (parte and 1 <= parte <= 4):           
      117 +        raise ToolError(f"Trimestre no válido en {fecha!r}: va
          + de T1 a T4.")                                                
      118 +    if not es_trim and parte is not None and not 1 <= parte <=
          + 12:                                                          
      119 +        raise ToolError(f"Mes no válido en {fecha!r}: va de 01
          + a 12.")                                                      
      120 +    # mes de referencia (para mensual y diaria)               
      121 +    if parte is None:                                         
      122 +        mes = 12 if fin else 1                                
      123 +    elif es_trim:                                             
      124 +        mes = 3 * parte if fin else 3 * parte - 2             
      125 +    else:                                                     
      126 +        mes = parte                                           
      127  
      101 -# TODO 4 · Un recurso, por ejemplo la plantilla bcrp://serie/{
          -codigo} con la ficha de la serie.                             
      128 +    f = frecuencia.lower()                                    
      129 +    if f == "anual":                                          
      130 +        return f"{anio}"                                      
      131 +    if f == "mensual":                                        
      132 +        return f"{anio}-{mes}"                                
      133 +    if f == "trimestral":                                     
      134 +        trim = parte if es_trim else (mes - 1) // 3 + 1       
      135 +        return f"{anio}-{trim}"                               
      136 +    if f == "diaria":                                         
      137 +        ultimo = calendar.monthrange(anio, mes)[1]            
      138 +        d = int(dia) if dia else (ultimo if fin else 1)       
      139 +        if not 1 <= d <= ultimo:                              
      140 +            raise ToolError(f"Día no válido en {fecha!r}.")   
      141 +        return f"{anio}-{mes:02d}-{d:02d}"                    
      142 +    raise ToolError(f"Frecuencia {frecuencia!r} no soportada."
          +)                                                             
      143  
      103 -# TODO 5 · Un prompt, por ejemplo informe(tema) que pida citar
          - el código y el periodo de cada cifra.                        
      144  
      145 +def _anio_dos_cifras(aa: str) -> int:                         
      146 +    a = int(aa)                                               
      147 +    return 2000 + a if a < 50 else 1900 + a                   
      148  
      149 +                                                              
      150 +def _periodo(nombre: str, frecuencia: str) -> str:            
      151 +    """"Ene.2025" -> "2025-01"; "01.Oct.26" -> "2026-10-01"; "
          +T1.25" -> "2025-T1"; "2025" -> "2025"."""                     
      152 +    f = frecuencia.lower()                                    
      153 +    try:                                                      
      154 +        if f == "mensual":                                    
      155 +            mes, anio = nombre.split(".")                     
      156 +            return f"{int(anio)}-{MESES[mes.lower()[:3]]:02d}"
      157 +        if f == "diaria":                                     
      158 +            dia, mes, aa = nombre.split(".")                  
      159 +            return f"{_anio_dos_cifras(aa)}-{MESES[mes.lower()
          +[:3]]:02d}-{int(dia):02d}"                                    
      160 +        if f == "trimestral":                                 
      161 +            trim, aa = nombre.split(".")                      
      162 +            return f"{_anio_dos_cifras(aa)}-T{int(trim.upper()
          +.lstrip('T'))}"                                               
      163 +        if f == "anual":                                      
      164 +            return str(int(nombre))                           
      165 +    except (ValueError, KeyError):                            
      166 +        pass                                                  
      167 +    raise ToolError(f"No pude interpretar el periodo {nombre!r
          +} que devolvió el BCRP ({frecuencia}).")                      
      168 +                                                              
      169 +                                                              
      170 +# ------------------------------------------------------------
          +---------------------------------------------------           
      171 +# Descarga con reintentos y caché                             
      172 +# ------------------------------------------------------------
          +---------------------------------------------------           
      173 +                                                              
      174 +def _pedir_api(url: str) -> dict:                             
      175 +    """GET a la API del BCRP. Si responde HTML (límite de pedi
          +dos o sin datos) reintenta con espera creciente.              
      176 +                                                              
      177 +    Las respuestas válidas se guardan en datos/cache_api/ y se
          + reutilizan durante CACHE_HORAS.                              
      178 +    """                                                       
      179 +    archivo = CACHE_API / (hashlib.sha1(url.encode()).hexdiges
          +t() + ".json")                                                
      180 +    if archivo.exists() and time.time() - archivo.stat().st_mt
          +ime < CACHE_HORAS * 3600:                                     
      181 +        return json.loads(archivo.read_text(encoding="utf-8"))
      182 +                                                              
      183 +    error = None                                              
      184 +    for intento in range(REINTENTOS):                         
      185 +        try:                                                  
      186 +            r = httpx.get(url, timeout=60)                    
      187 +            r.raise_for_status()                              
      188 +            datos = r.json()                      # la API res
          +ponde text/html incluso con JSON: se intenta leer             
      189 +            if not isinstance(datos, dict) or "periods" not in
          + datos:                                                       
      190 +                raise ValueError("respuesta sin 'periods'")   
      191 +            break                                             
      192 +        except (httpx.HTTPError, ValueError) as e:   # ValueEr
          +ror incluye JSONDecodeError (llegó una página HTML)           
      193 +            error = e                                         
      194 +            if intento < REINTENTOS - 1:                      
      195 +                time.sleep(ESPERA_BASE * 2 ** intento)        
      196 +    else:                                                     
      197 +        raise ToolError(f"El BCRP no respondió con datos tras 
          +{REINTENTOS} intentos ({type(error).__name__}). "             
      198 +                        f"Puede ser el límite de pedidos o que
          + no haya datos en ese periodo. URL: {url}")                   
      199 +                                                              
      200 +    CACHE_API.mkdir(parents=True, exist_ok=True)              
      201 +    archivo.write_text(json.dumps(datos, ensure_ascii=False), 
          +encoding="utf-8")                                             
      202 +    return datos                                              
      203 +                                                              
      204 +                                                              
      205 +def _url_web(codigo: str, frecuencia: str) -> str:            
      206 +    return f"{WEB}/{WEB_FRECUENCIA.get(frecuencia.lower(), 'me
          +nsuales')}/resultados/{codigo}/html"                          
      207 +                                                              
      208 +                                                              
      209 +def _serie(codigo: str, desde: str, hasta: str) -> dict:      
      210 +    codigo = str(codigo).strip().upper()                      
      211 +    ficha = _ficha(codigo)                                    
      212 +    fr = ficha["frecuencia"]                                  
      213 +    d, h = _fecha_api(desde, fr), _fecha_api(hasta, fr, fin=Tr
          +ue)                                                           
      214 +    url = f"{API}/{codigo}/json/{d}/{h}"                      
      215 +    datos = []                                                
      216 +    for p in _pedir_api(url).get("periods", []):              
      217 +        bruto = (p.get("values") or ["n.d."])[0]              
      218 +        try:                                                  
      219 +            valor = float(bruto)                              
      220 +        except (TypeError, ValueError):          # "n.d." y si
          +milares: sin dato                                             
      221 +            continue                                          
      222 +        if math.isnan(valor):                                 
      223 +            continue                                          
      224 +        datos.append({"periodo": _periodo(p["name"], fr), "val
          +or": round(valor, 6)})                                        
      225 +    if not datos:                                             
      226 +        raise ToolError(f"La serie {codigo} no tiene datos ent
          +re {desde} y {hasta}. "                                       
      227 +                        f"Hay datos desde {ficha['inicio']} (a
          +ctualizada {ficha['actualizada']}).")                         
      228 +    return {"codigo": codigo, "nombre": ficha["nombre"], "frec
          +uencia": fr, "desde": desde, "hasta": hasta,                  
      229 +            "datos": datos, "fuente": url, "consulta_web": _ur
          +l_web(codigo, fr)}                                            
      230 +                                                              
      231 +                                                              
      232 +# ------------------------------------------------------------
          +---------------------------------------------------           
      233 +# Herramientas                                                
      234 +# ------------------------------------------------------------
          +---------------------------------------------------           
      235 +                                                              
      236 +@mcp.tool(annotations=SOLO_LECTURA)                           
      237 +def serie(codigo: str, desde: str, hasta: str) -> dict:       
      238 +    """Descarga los datos oficiales de una serie del BCRP entr
          +e dos fechas (ambas incluidas).                               
      239 +                                                              
      240 +    Úsala cuando necesiten los valores periodo a periodo. Fech
          +as: "2025-01" (mensual), "2025-T1" o "2025-01"                
      241 +    (trimestral), "2026-10-01" (diaria), "2025" (anual o todo 
          +el año). Ejemplo: codigo="PN01273PM",                         
      242 +    desde="2024-01", hasta="2024-12". Devuelve código, nombre,
          + frecuencia, datos [{periodo, valor}] y la URL                
      243 +    de la fuente. Los valores "n.d." del BCRP se omiten. Para 
          +promedios o variaciones usen resumen.                         
      244 +    """                                                       
      245 +    return _serie(codigo, desde, hasta)                       
      246 +                                                              
      247 +                                                              
      248 +@mcp.tool(annotations=SOLO_LECTURA)                           
      249 +def resumen(codigo: str, desde: str, hasta: str) -> dict:     
      250 +    """Resume una serie del BCRP en un periodo: primero, últim
          +o, cambio, variación %, promedio, máximo y mínimo.            
      251 +                                                              
      252 +    Úsala siempre que pidan un valor puntual, una variación o 
          +un promedio, para no hacer cuentas a mano.                    
      253 +    Ejemplo: codigo="PN01273PM", desde="2025-12", hasta="2026-
          +09". "cambio" está en las unidades de la serie                
      254 +    (si la serie ya es una tasa en %, el cambio es en puntos p
          +orcentuales); "variacion_pct" es la variación                 
      255 +    relativa entre el primer y el último valor (null si el pri
          +mero es 0).                                                   
      256 +    """                                                       
      257 +    s = _serie(codigo, desde, hasta)                          
      258 +    v = pd.Series([x["valor"] for x in s["datos"]], index=[x["
          +periodo"] for x in s["datos"]])                               
      259 +    primero, ultimo = float(v.iloc[0]), float(v.iloc[-1])     
      260 +    return {                                                  
      261 +        "codigo": s["codigo"], "nombre": s["nombre"], "frecuen
          +cia": s["frecuencia"],                                        
      262 +        "periodo": {"desde": v.index[0], "hasta": v.index[-1]}
          +, "n": int(v.size),                                           
      263 +        "primero": {"periodo": v.index[0], "valor": round(prim
          +ero, 4)},                                                     
      264 +        "ultimo": {"periodo": v.index[-1], "valor": round(ulti
          +mo, 4)},                                                      
      265 +        "cambio": round(ultimo - primero, 4),                 
      266 +        "variacion_pct": round((ultimo / primero - 1) * 100, 4
          +) if primero != 0 else None,                                  
      267 +        "promedio": round(float(v.mean()), 4),                
      268 +        "maximo": {"periodo": v.idxmax(), "valor": round(float
          +(v.max()), 4)},                                               
      269 +        "minimo": {"periodo": v.idxmin(), "valor": round(float
          +(v.min()), 4)},                                               
      270 +        "fuente": s["fuente"], "consulta_web": s["consulta_web
          +"],                                                           
      271 +    }                                                         
      272 +                                                              
      273 +                                                              
      274 +def _lectura(r: float) -> str:                                
      275 +    fuerza = "débil" if abs(r) < 0.3 else "moderada" if abs(r)
          + < 0.7 else "fuerte"                                          
      276 +    signo = "positiva" if r > 0 else "negativa" if r < 0 else 
          +"nula"                                                        
      277 +    return f"asociación lineal {signo} {fuerza} (r = {r:.3f})"
      278 +                                                              
      279 +                                                              
      280 +@mcp.tool(annotations=SOLO_LECTURA)                           
      281 +def correlacion(codigo_a: str, codigo_b: str, desde: str, hast
          +a: str, en_diferencias: bool = False) -> dict:                
      282 +    """Mide la asociación entre dos series del BCRP de la mism
          +a frecuencia, alineando sus periodos.                         
      283 +                                                              
      284 +    Úsala para preguntas como «¿la inflación se movió junto co
          +n la actividad económica entre 2020 y 2024?»:                 
      285 +    por ejemplo codigo_a="PN01273PM" (IPC Lima, var. % 12 mese
          +s) y codigo_b="PN01728AM" (PBI, var. %                        
      286 +    interanual), desde="2020-01", hasta="2024-12". Descarga am
          +bas, conserva solo los periodos con dato en las               
      287 +    dos (informa cuáles se excluyeron) y calcula Pearson y Spe
          +arman con pandas. Con en_diferencias=True                     
      288 +    correlaciona los cambios de un periodo al siguiente, útil 
          +cuando ambas series tienen tendencia.                         
      289 +    Exige al menos 3 periodos comunes. Es una medida descripti
          +va: no demuestra causalidad.                                  
      290 +    """                                                       
      291 +    a, b = _serie(codigo_a, desde, hasta), _serie(codigo_b, de
          +sde, hasta)                                                   
      292 +    if a["frecuencia"] != b["frecuencia"]:                    
      293 +        raise ToolError(f"Las series tienen frecuencias distin
          +tas: {a['codigo']} es {a['frecuencia']} y "                   
      294 +                        f"{b['codigo']} es {b['frecuencia']}. 
          +Elijan dos series de la misma frecuencia "                    
      295 +                        "(búsquenlas con buscar_series y el fi
          +ltro frecuencia).")                                           
      296 +    sa = pd.Series({x["periodo"]: x["valor"] for x in a["datos
          +"]}, name="a")                                                
      297 +    sb = pd.Series({x["periodo"]: x["valor"] for x in b["datos
          +"]}, name="b")                                                
      298 +    tabla = pd.concat([sa, sb], axis=1).sort_index()          
      299 +    solo_a = tabla.index[tabla.a.notna() & tabla.b.isna()].tol
          +ist()                                                         
      300 +    solo_b = tabla.index[tabla.b.notna() & tabla.a.isna()].tol
          +ist()                                                         
      301 +    if en_diferencias:              # la diferencia se toma so
          +bre la tabla completa: un hueco no se salta                   
      302 +        tabla = tabla.diff()                                  
      303 +    comunes = tabla.dropna()                                  
      304 +    if len(comunes) < 3:                                      
      305 +        raise ToolError(f"Solo hay {len(comunes)} periodos com
          +unes con dato entre {a['codigo']} y {b['codigo']} "           
      306 +                        f"de {desde} a {hasta}; se necesitan a
          +l menos 3.")                                                  
      307 +    if comunes.a.std() == 0 or comunes.b.std() == 0:          
      308 +        constante = a["codigo"] if comunes.a.std() == 0 else b
          +["codigo"]                                                    
      309 +        raise ToolError(f"La serie {constante} no varía en los
          + periodos comunes: la correlación no está definida.")         
      310 +    pearson = float(comunes.a.corr(comunes.b))                
      311 +    spearman = float(comunes.a.corr(comunes.b, method="spearma
          +n"))                                                          
      312 +    return {                                                  
      313 +        "serie_a": {"codigo": a["codigo"], "nombre": a["nombre
          +"], "fuente": a["fuente"]},                                   
      314 +        "serie_b": {"codigo": b["codigo"], "nombre": b["nombre
          +"], "fuente": b["fuente"]},                                   
      315 +        "frecuencia": a["frecuencia"], "en_diferencias": en_di
          +ferencias,                                                    
      316 +        "periodo_comun": {"desde": comunes.index[0], "hasta": 
          +comunes.index[-1]},                                           
      317 +        "n_periodos": int(len(comunes)),                      
      318 +        "excluidos": {"solo_en_a": solo_a, "solo_en_b": solo_b
          +},                                                            
      319 +        "pearson": round(pearson, 4), "spearman": round(spearm
          +an, 4),                                                       
      320 +        "lectura": _lectura(pearson),                         
      321 +        "advertencia": ("Correlación descriptiva entre series 
          +agregadas: no implica causalidad. Si ambas series "           
      322 +                        "tienen tendencia, la correlación en n
          +iveles puede ser espuria; comparen con "                      
      323 +                        "en_diferencias=True."),              
      324 +        "pares": [{"periodo": p, "a": round(float(f.a), 6), "b
          +": round(float(f.b), 6)}                                      
      325 +                  for p, f in comunes.iterrows()],            
      326 +    }                                                         
      327 +                                                              
      328 +                                                              
      329 +# ------------------------------------------------------------
          +---------------------------------------------------           
      330 +# Recurso y prompt                                            
      331 +# ------------------------------------------------------------
          +---------------------------------------------------           
      332 +                                                              
      333 +@mcp.resource("bcrp://serie/{codigo}", mime_type="application/
          +json",                                                        
      334 +              description="Ficha descriptiva de una serie del 
          +BCRP: nombre, categoría, frecuencia, desde cuándo "           
      335 +                          "hay datos, última actualización y e
          +nlaces a la API y a la página oficial.")                      
      336 +def ficha_serie(codigo: str) -> dict:                         
      337 +    codigo = str(codigo).strip().upper()                      
      338 +    try:                                                      
      339 +        f = _ficha(codigo)                                    
      340 +    except ToolError as e:                                    
      341 +        raise ResourceError(str(e)) from e                    
      342 +    return {**f, "api": f"{API}/{codigo}/json/<desde>/<hasta>"
          +, "consulta_web": _url_web(codigo, f["frecuencia"]),          
      343 +            "fuente": "Banco Central de Reserva del Perú, catá
          +logo de series estadísticas " + URL_CATALOGO}                 
      344 +                                                              
      345 +                                                              
      346 +@mcp.prompt                                                   
      347 +def informe(tema: str) -> str:                                
      348 +    """Plantilla para un informe breve sobre un indicador del 
          +BCRP, con cada cifra citada y verificable."""                 
      349 +    return (                                                  
      350 +        f"Prepara un informe breve sobre «{tema}» con datos of
          +iciales del BCRP, usando solo el servidor MCP bcrp.\n\n"      
      351 +        "1. Usa buscar_series para identificar la o las series
          + pertinentes y explica por qué elegiste cada código.\n"       
      352 +        "2. Usa resumen para el valor más reciente, el cambio,
          + el promedio y los extremos del periodo; usa serie "          
      353 +        "solo si necesitas los datos periodo a periodo; usa co
          +rrelacion si el tema relaciona dos indicadores.\n"            
      354 +        "3. No hagas cuentas a mano: toda cifra debe venir de 
          +una herramienta.\n"                                           
      355 +        "4. Junto a cada cifra cita el código de serie, el per
          +iodo y la fuente (URL de la API o consulta_web).\n"           
      356 +        "5. Describe asociaciones, no causas. Señala limitacio
          +nes (frecuencia, revisiones, periodo cubierto).\n"            
      357 +        "6. Si una herramienta falla o no hay datos, dilo expl
          +ícitamente; no estimes ni completes cifras.\n\n"              
      358 +        "Estructura: (a) pregunta y series usadas, (b) cifras 
          +clave en una tabla, (c) interpretación en 3-5 "               
      359 +        "líneas, (d) fuentes."                                
      360 +    )                                                         
      361 +                                                              
      362 +                                                              
      363  if __name__ == "__main__":
      364      mcp.run()

● Corro las 8 pruebas originales:

  Ran 1 shell command (ctrl+o to expand)

● 8 de 8. Ahora pruebo correlacion con datos reales: inflación (PN01273PM)
  contra PBI (PN01728AM), 2020-2024.

  Ran 1 shell command (ctrl+o to expand)

● Spearman en pandas 3 requiere scipy, así que lo calculo como la correlación de
  Pearson sobre los rangos (con empates promediados), con el mismo resultado.

● Update(tarea_4\mcp\server.py)
  ⎿  Added 2 lines, removed 1 line
      308          constante = a["codigo"] if comunes.a.std() == 0 else b
           ["codigo"]
      309          raise ToolError(f"La serie {constante} no varía en los
            periodos comunes: la correlación no está definida.")
      310      pearson = float(comunes.a.corr(comunes.b))
      311 -    spearman = float(comunes.a.corr(comunes.b, method="spearma
          -n"))                                                          
      311 +    rangos = comunes.rank()         # Spearman = Pearson sobre
          + rangos (empates con rango promedio); sin scipy               
      312 +    spearman = float(rangos.a.corr(rangos.b))                 
      313      return {
      314          "serie_a": {"codigo": a["codigo"], "nombre": a["nombre
           "], "fuente": a["fuente"]},
      315          "serie_b": {"codigo": b["codigo"], "nombre": b["nombre
           "], "fuente": b["fuente"]},

● Update(tarea_4\mcp\server.py)
  ⎿  Added 1 line, removed 1 line
      284      Úsala para preguntas como «¿la inflación se movió junto co
           n la actividad económica entre 2020 y 2024?»:
      285      por ejemplo codigo_a="PN01273PM" (IPC Lima, var. % 12 mese
           s) y codigo_b="PN01728AM" (PBI, var. %
      286      interanual), desde="2020-01", hasta="2024-12". Descarga am
           bas, conserva solo los periodos con dato en las
      287 -    dos (informa cuáles se excluyeron) y calcula Pearson y Spe
          -arman con pandas. Con en_diferencias=True                     
      287 +    dos (informa cuáles se excluyeron) y calcula Pearson y Spe
          +arman (Pearson sobre rangos) con pandas. Con en_diferencias=Tr
          +ue                                                            
      288      correlaciona los cambios de un periodo al siguiente, útil 
           cuando ambas series tienen tendencia.
      289      Exige al menos 3 periodos comunes. Es una medida descripti
           va: no demuestra causalidad.
      290      """

  Ran 1 shell command (ctrl+o to expand)

● Todo funciona: la correlación inflación-PBI es débil en niveles y en
  diferencias, el error al cruzar frecuencias distintas es el esperado, y el
  recurso y el prompt responden bien. Ahora paso las tildes del recurso a texto
  legible y agrego las 2 pruebas nuevas a test_server.py sin tocar las 8
  originales.

● Update(tarea_4\mcp\server.py)
  ⎿  Added 4 lines, removed 3 lines
      334  @mcp.resource("bcrp://serie/{codigo}", mime_type="application/
           json",
      335                description="Ficha descriptiva de una serie del 
           BCRP: nombre, categoría, frecuencia, desde cuándo "
      336                            "hay datos, última actualización y e
           nlaces a la API y a la página oficial.")
      337 -def ficha_serie(codigo: str) -> dict:                         
      337 +def ficha_serie(codigo: str) -> str:                          
      338      codigo = str(codigo).strip().upper()
      339      try:
      340          f = _ficha(codigo)
      341      except ToolError as e:
      342          raise ResourceError(str(e)) from e
      343 -    return {**f, "api": f"{API}/{codigo}/json/<desde>/<hasta>"
          -, "consulta_web": _url_web(codigo, f["frecuencia"]),          
      344 -            "fuente": "Banco Central de Reserva del Perú, catá
          -logo de series estadísticas " + URL_CATALOGO}                 
      343 +    ficha = {**f, "api": f"{API}/{codigo}/json/<desde>/<hasta>
          +", "consulta_web": _url_web(codigo, f["frecuencia"]),         
      344 +             "fuente": "Banco Central de Reserva del Perú, cat
          +álogo de series estadísticas " + URL_CATALOGO}                
      345 +    return json.dumps(ficha, ensure_ascii=False, indent=2)    
      346  
      347  
      348  @mcp.prompt

● Update(tarea_4\mcp\test_server.py)
  ⎿  Added 36 lines
       69  
       70  def test_un_prompt():
       71      assert len(asyncio.run(_con_cliente(lambda c: c.list_promp
           ts()))) >= 1
       72 +                                                              
       73 +                                                              
       74 +# --- Pruebas propias (Tarea 4): herramienta correlacion. Las 
          +8 de arriba son las originales, sin cambios. ---              
       75 +                                                              
       76 +def test_correlacion_coincide_con_calculo_independiente():    
       77 +    """Inflación de Lima (12 meses) contra PBI (var. % interan
          +ual), 2020-2024: la herramienta debe dar lo mismo             
       78 +    que un cálculo hecho aparte con numpy sobre los datos que 
          +devuelve `serie`."""                                          
       79 +    import numpy as np                                        
       80 +    args = dict(desde="2020-01", hasta="2024-12")             
       81 +    a = {x["periodo"]: x["valor"] for x in llamar("serie", cod
          +igo="PN01273PM", **args)["datos"]}                            
       82 +    b = {x["periodo"]: x["valor"] for x in llamar("serie", cod
          +igo="PN01728AM", **args)["datos"]}                            
       83 +    comunes = sorted(set(a) & set(b))                         
       84 +    esperado = np.corrcoef([a[p] for p in comunes], [b[p] for 
          +p in comunes])[0, 1]                                          
       85 +                                                              
       86 +    r = llamar("correlacion", codigo_a="PN01273PM", codigo_b="
          +PN01728AM", **args)                                           
       87 +    assert r["n_periodos"] == len(comunes) == 60              
       88 +    assert r["periodo_comun"] == {"desde": "2020-01", "hasta":
          + "2024-12"}                                                   
       89 +    assert r["pearson"] == pytest.approx(esperado, abs=1e-4)  
       90 +    assert -1 <= r["spearman"] <= 1                           
       91 +    assert r["serie_a"]["fuente"].startswith("https://estadist
          +icas.bcrp.gob.pe")                                            
       92 +    assert "causalidad" in r["advertencia"]                   
       93 +                                                              
       94 +                                                              
       95 +def test_correlacion_casos_limite():                          
       96 +    """Una serie consigo misma da r = 1; en diferencias se pie
          +rde el primer periodo; frecuencias distintas                  
       97 +    dan un error claro en vez de un número sin sentido."""    
       98 +    r = llamar("correlacion", codigo_a="PN01271PM", codigo_b="
          +PN01271PM", desde="2025-01", hasta="2025-12")                 
       99 +    assert r["pearson"] == pytest.approx(1.0) and r["spearman"
          +] == pytest.approx(1.0)                                       
      100 +    assert r["n_periodos"] == 12                              
      101 +                                                              
      102 +    d = llamar("correlacion", codigo_a="PN01271PM", codigo_b="
          +PN01273PM", desde="2025-01", hasta="2025-12",                 
      103 +               en_diferencias=True)                           
      104 +    assert d["n_periodos"] == 11 and d["periodo_comun"]["desde
          +"] == "2025-02"                                               
      105 +                                                              
      106 +    with pytest.raises(ToolError, match="frecuencias distintas
          +"):                                                           
      107 +        llamar("correlacion", codigo_a="PN01273PM", codigo_b="
          +PD04638PD", desde="2025-01", hasta="2025-03")                 

● Corro la suite desde tarea_4/ sin caché para que todo se pida en vivo a la
  API, y luego comparo la salida con diff contra las 8 pruebas originales.

● Bash(export PATH="$HOME/.local/bin:$PATH"; cd "/c/Users/Antonio
      Macedo/repos/Python_Intermedio_2026/tarea_4"; rm -rf mcp/datos/cache_api;
      { echo "# uv run pytest -q…)
  ⎿  # uv run pytest -q  (desde tarea_4/, 2026-11-08 13:16 HPS, API del BCR
     P en vivo, sin caché)
     ..........
     … +4 lines (ctrl+o to expand)
  ⎿  Created tarea_4\salidas\pytest_mcp.txt (+3 -0)
      1 +# uv run pytest -q  (desde tarea_4/, 2026-11-08 13:16 HPS, API d
        +el BCRP en vivo, sin caché)                                     
      2 +..........                                                      
        +         [100%]                                                 
      3 +10 passed in 10.65s                                             
  ⎿  (timeout 5m)

● Las 10 pruebas pasan y las 8 originales no cambiaron; ahora compruebo que
  .mcp.json arranca el servidor con esa configuración.

● Bash(export PATH="$HOME/.local/bin:$PATH"; cd "/c/Users/Antonio
      Macedo/repos/Python_Intermedio_2026/tarea_4"; sed -i 's/ HPS,/ hora de
      Perú,/' salidas/pytest_mcp.txt…)
  ⎿  +---------------------------------------------------------------------
     --------+
     |
     … +29 lines (ctrl+o to expand)
  ⎿  Updated tarea_4\salidas\pytest_mcp.txt (+3 -3)
      1 -# uv run pytest -q  (desde tarea_4/, 2026-11-08 13:16 HPS, API d
        -el BCRP en vivo, sin caché)                                     
      2 -..........                                                      
        -         [100%]                                                 
      3 -10 passed in 10.65s                                             
      1 +# uv run pytest -q  (desde tarea_4/, 2026-11-08 13:16 hora de Pe
        +rú, API del BCRP en vivo, sin caché)                            
      2 +..........                                                      
        +         [100%]                                                 
      3 +10 passed in 10.65s                                             
  ⎿  (timeout 5m)

● El servidor ya arranca por stdio desde .mcp.json con sus 4 herramientas, el
  recurso y el prompt, y su último valor (1.2772) coincide con la respuesta de
  la API. Ahora hago el commit.

  Ran 1 shell command (ctrl+o to expand)

● Parte 1 lista: 10 passed (commit 73c692a)

  Pruebas: uv run pytest -q → 10 passed in 10.65s, con la API del BCRP en vivo y
  sin caché. La salida quedó en tarea_4/salidas/pytest_mcp.txt. Comprobé con
  diff que las 8 pruebas originales son idénticas a las de la sesión 04. No hizo
  falta cambiar ni los imports, porque pytest agrega la carpeta mcp/ al buscar
  módulos y from server import mcp funciona tal cual.

  Qué hice en mcp/server.py:
  - serie: convierte tus fechas al formato que pide la API, según la frecuencia
    de la serie. Devuelve los periodos normalizados (2025-01, 2026-10-01,
    2025-T1, 2025), omite los "n.d." e incluye la URL de la fuente.
  - resumen: devuelve el primer y el último valor, el cambio, la variación %, el
    promedio, el máximo y el mínimo. Aclara que si la serie ya es una tasa, el
    cambio está en puntos porcentuales.
  - Reintentos y caché: hasta 4 intentos con espera creciente, porque la API
    devuelve HTML cuando recibe muchos pedidos seguidos. Las respuestas se
    guardan 12 h en mcp/datos/cache_api/, que git ignora.
  - Recurso bcrp://serie/{codigo}: la ficha de la serie, con el link a la página
    oficial del BCRP. Verifiqué que ese formato de link responde.
  - Prompt informe(tema): pide citar código, periodo y fuente, no hacer cuentas
    a mano, no afirmar causas y decir cuando algo falla.

  Herramienta propia: correlacion(codigo_a, codigo_b, desde, hasta, 
  en_diferencias)
  - Qué hace: descarga dos series de la misma frecuencia y conserva solo los
    periodos que tienen dato en ambas. Te dice cuáles excluyó y calcula la
    correlación de Pearson y la de Spearman.
  - en_diferencias=True: compara los cambios de un mes al siguiente en vez de
    los niveles. Así se evita una correlación falsa cuando las dos series tienen
    tendencia.
  - Avisos y errores: siempre advierte que una correlación no demuestra
    causalidad. Con frecuencias distintas o menos de 3 periodos comunes, da un
    error claro en vez de un número.
  - Por qué la elegí: tu tema es inflación y actividad económica, y esta es la
    única opción que relaciona las dos variables. comparar_periodos sería
    básicamente resumen aplicado dos veces, y el Issue pide que la herramienta
    propia no duplique las otras.
  - Ejemplo real: inflación de Lima (PN01273PM) contra PBI (PN01728AM), de
    2020-01 a 2024-12. Con 60 meses, r = 0.051 en niveles y −0.167 en
    diferencias; en ambos casos la asociación es débil.
  - Las 2 pruebas nuevas:
    a. El resultado coincide con un cálculo independiente hecho con numpy sobre
       los datos de serie.
    b. Los casos límite: una serie contra sí misma da r = 1, en diferencias se
       pierde el primer mes y las frecuencias distintas dan error.

  Problema que apareció: pandas 3 necesita scipy para calcular Spearman. No
  agregué esa dependencia: lo calculo como Pearson sobre los rangos, que es la
  definición de Spearman.

  Cómo probar el MCP en Claude Code:
  1. Abre una terminal dentro de tarea_4/ (ahí está .mcp.json) y ejecuta claude.
     Si te pregunta si apruebas el servidor bcrp, acepta. Si uv no se reconoce,
     cierra y vuelve a abrir la terminal para que tome el PATH nuevo.
  2. Escribe /mcp: debe aparecer bcrp conectado, con 4 herramientas.
  3. Pregunta algo como: "¿Cuál fue la inflación de Lima a 12 meses en marzo de 
     2025?". En el detalle debería verse que llama a buscar_series y luego a
     resumen o serie.
  4. Para probar correlacion: "¿Se movieron juntas la inflación y el PBI entre 
     2020 y 2024?"
  5. Para el recurso: @bcrp:bcrp://serie/PN01273PM ¿desde cuándo hay datos?.
     Para el prompt: /mcp__bcrp__informe inflación.

  Te conviene sacar capturas de esos pasos para evidencias_ia/mcp/. No hice
  push: avísame cuando quieras subirlo. ¿Seguimos con la Parte 2 (las Skills de
  ENAHO)?

✻ Sautéed for 8m 59s · done 1:17 p.m.

※ recap: Estamos haciendo la Tarea 4, que se entrega hoy a las 23:59; ya terminamos la Parte 0 y el servidor MCP del BCRP, con 10 pruebas aprobadas y su commit. El siguiente paso es que me confirmes para empezar la Parte 2, las Skills de ENAHO. (disable recaps in /config)