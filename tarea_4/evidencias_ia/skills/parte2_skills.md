 ▐▛███▛█   Claude Code v2.1.319
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~\repos\Python_Intermedio_2026\tarea_4


> /clear                                                                        

> Hola ccode. Seguimos con la Tarea 4 (Issue #201:                              
  https://github.com/d2cml-ai/Data-Science-Python/issues/201). Lee primero      
  CLAUDE.md, README.md y mcp/ para tener contexto: la Parte 1 (MCP del BCRP, 10 
  passed) ya está hecha y probada en Claude Code. El repo del curso está        
  clonado como referencia de solo lectura en C:\Users\Antonio                   
  Macedo\repos\Data-Science-Python. Trabaja con rigor y avísame al terminar     
  cada skill. Si algo te bloquea, pregúntame.                                   
                                                                                
  PARTE 2 · TRES SKILLS DE LA ENAHO 2024 (en .claude/skills/, con la            
  metodología de la sesión 16)                                                  
                                                                                
  0. Lee completo sessions/16-skills-enaho/README.md (pipeline, reglas y        
  valores de validación) y copia                                                
  sessions/16-skills-enaho/referencias/pobreza_departamento_2024.csv a          
  tarea_4/referencias/.                                                         
                                                                                
  1. SKILL limpiando-enaho (SKILL.md, reference.md, scripts/limpiar.py)         
  - Lee los .dta directamente desde datos/966-Modulo34.zip y                    
  datos/966-Modulo02.zip con pd.read_stata(convert_categoricals=False), con las 
  llaves (conglome, vivienda, hogar, codperso, ubigeo) como texto y sin perder  
  ceros iniciales.                                                              
  - Normaliza los nombres de columna a minúscula (ojo con aÑo).                 
  - Filtra residentes habituales: ((p204 == 1) & (p205 == 2)) | ((p204 == 2) &  
  (p206 == 1)).                                                                 
  - Une personas con sumaria: merge(on=[conglome, vivienda, hogar],             
  validate="m:1", indicator=True), comprobando que no se pierdan ni dupliquen   
  filas.                                                                        
  - Construye: departamento = ubigeo[:2]; area (urbana si estrato <= 5, rural   
  si no); pobre = pobreza <= 2; pobre_extremo = pobreza == 1; sexo (p207); edad 
  (p208a) y grupos de edad.                                                     
  - Pondera SIEMPRE con facpob07 a nivel de personas. Calcula también la        
  pobreza nacional con la sumaria y factor07 × mieperho, y explica en           
  validacion.txt por qué difieren levemente.                                    
  - salidas/validacion.txt con PASA/FALLA en cada chequeo: pobreza nacional     
  27.6 % ± 0.1 pp; 108,664 residentes habituales; 25 códigos de departamento    
  (01 a 25); llaves únicas en sumaria y en personas; la unión no pierde ni      
  duplica filas; factores sin nulos y positivos; urbana ~24.8 % y rural ~39.3 % 
  (informativas). Si falla una validación esencial, el script termina con       
  error (sys.exit(1)) y no escribe la base. Nunca ajustes resultados para que   
  coincidan con la referencia.                                                  
  - Salidas: salidas/personas_2024.parquet (ponlo en .gitignore: es microdato), 
  salidas/validacion.txt y salidas/indicadores.csv (pobreza ponderada           
  nacional, por área, sexo, grupo de edad y departamento, con n de              
  observaciones y población expandida).                                         
  - reference.md: diccionario de las variables usadas (códigos de pobreza,      
  estrato, p204 a p208a, factores) y las trampas de la ENAHO.                   
                                                                                
  2. SKILL graficando-enaho (SKILL.md, scripts/graficar.py)                     
  - Gráficos desde salidas/personas_2024.parquet, ponderados con facpob07: (a)  
  pobreza urbana y rural; (b) por sexo y por grupo de edad; (c) por             
  departamento, ordenado y con línea del promedio nacional.                     
  - Reglas: barras desde cero, valor escrito en cada barra, título analítico    
  que diga qué y cuándo, unidad (% de personas), nota «Fuente: INEI, ENAHO 2024 
  (módulos 34 y 02). Elaboración propia, ponderado con facpob07.», PNG a 200    
  dpi en figuras/.                                                              
  - Argumento --por area|sexo|edad|departamento, para pedirlos en lenguaje      
  natural.                                                                      
  - En SKILL.md: «Si no existe salidas/personas_2024.parquet, usa primero la    
  skill limpiando-enaho».                                                       
                                                                                
  3. SKILL mapeando-enaho (SKILL.md, scripts/mapear.py)                         
  - GeoJSON: si no está en datos/, el script lo descarga de                     
  https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/ 
  06-geoespacial/lab/Data/peru_departamental_simple.geojson                     
  - Une por código, nunca por nombre: ubigeo[:2] con FIRST_IDDP, ambos como     
  texto de 2 dígitos. Exige 25 unidades y ninguna sin dato; Lima (15) y Callao  
  (07) separados.                                                               
  - Escala secuencial de claro a oscuro que empiece en 0, leyenda con la unidad 
  (% de personas en pobreza monetaria), título y fuente; guarda                 
  mapas/pobreza_departamento.png.                                               
  - Compara cada departamento con referencias/pobreza_departamento_2024.csv,    
  guarda salidas/comparacion_mapa_referencia.csv con las diferencias y reporta  
  la diferencia máxima.                                                         
  - En SKILL.md: «Si no existe salidas/personas_2024.parquet, usa primero la    
  skill limpiando-enaho».                                                       
                                                                                
  4. PARA LAS TRES                                                              
  - SKILL.md con YAML válido: name y description en tercera persona, con las    
  palabras que usaría quien pide (ENAHO, INEI, pobreza, gráfico, mapa,          
  departamento), e instrucciones de menos de 500 líneas. Los scripts se corren  
  con uv run ${CLAUDE_SKILL_DIR}/scripts/... desde tarea_4/.                    
  - Prueba cada script: borra salidas/personas_2024.parquet y corre limpiar.py, 
  graficar.py (las 4 opciones) y mapear.py. Mira cada figura y el mapa antes    
  de darlos por buenos.                                                         
  - Un commit por skill, y push al final.                                       
  - Al terminar dime: el contenido de validacion.txt, la lista de figuras, la   
  diferencia máxima contra la referencia, si debo reiniciar Claude Code para    
  que detecte las skills, y cómo pruebo que se activan solas.                   

● Empiezo leyendo el contexto: CLAUDE.md, README.md, mcp/ y el README de la
  sesión 16.

  Ran 3 shell commands (ctrl+o to expand)

● Copio la referencia y reviso qué hay dentro de los zip (nombres de archivos y
  columnas) antes de escribir el script.

  Ran 1 shell command (ctrl+o to expand)

● Ojo: el módulo 34 trae dos .dta (sumaria-2024.dta y sumaria-2024-12g.dta).
  Reviso ambos para elegir bien.

  Ran 1 shell command (ctrl+o to expand)

● Las llaves y el año llegan mal decodificados, así que los normalizo; el módulo
  34 trae dos archivos y usaré el estándar; p204–p208a tienen 3,966 nulos que
  el filtro de residentes excluye. Ahora escribo la skill limpiando-enaho.

  Ran 1 shell command (ctrl+o to expand)

● Las dos sumarias dan la misma pobreza (27.58 %), así que elegir la estándar no
  cambia el resultado. Escribo el script.

● Write(.claude\skills\limpiando-enaho\scripts\limpiar.py)
  ⎿  Wrote 253 lines to .claude\skills\limpiando-enaho\scripts\limpiar.py
       1 """Limpia la ENAHO 2024 (INEI): módulos 34 (sumaria) y 02 (miemb
         ros) -> base de personas con pobreza.
       2 
       3 Se corre desde tarea_4/:
       4     uv run .claude/skills/limpiando-enaho/scripts/limpiar.py
       5 
       6 Pipeline (siempre en este orden): leer -> normalizar columnas ->
          filtrar residentes habituales ->
       7 unir personas con sumaria (m:1) -> construir variables -> valida
         r -> guardar.
     … +246 lines (ctrl+o to expand)

● Simplifico la regla del año (el � queda como ao al quitar caracteres no ASCII;
  aÑo queda como ano):

● Update(.claude\skills\limpiando-enaho\scripts\limpiar.py)
  ⎿  Added 1 line, removed 1 line
      52      nuevas = {}
      53      for c in df.columns:
      54          limpio = unicodedata.normalize("NFKD", str(c).lower()).
          encode("ascii", "ignore").decode()
      55 -        if c.lower().startswith("a") and c.lower().endswith("o"
         -) and len(c) == 3 and limpio != "ano" or limpio == "ano":      
      55 +        if limpio in ("ano", "ao"):   # 'aÑo' -> 'ano'; 'a�o' (
         +mal decodificada) -> 'ao'                                      
      56              limpio = "anio"
      57          nuevas[c] = limpio
      58      return df.rename(columns=nuevas)

  Ran 1 shell command (ctrl+o to expand)

● La consola de Windows no imprime Σ. Fuerzo UTF-8 en la salida (útil también
  para las otras dos skills):

● Update(.claude\skills\limpiando-enaho\scripts\limpiar.py)
  ⎿  Added 2 lines, removed 1 line
      84  
      85  
      86  def main():
      87 -    ap = argparse.ArgumentParser(description=__doc__, formatter
         -_class=argparse.RawDescriptionHelpFormatter)                   
      87 +    sys.stdout.reconfigure(encoding="utf-8")   # la consola de 
         +Windows usa cp1252 por defecto                                 
      88 +    ap =argparse.ArgumentParser(description=__doc__, formatter_
         +class=argparse.RawDescriptionHelpFormatter)                    
      89      ap.add_argument("--datos", default="datos", help="carpeta c
          on los zip del INEI (por defecto datos/)")
      90      ap.add_argument("--salidas", default="salidas", help="carpe
          ta de salida (por defecto salidas/)")
      91      args = ap.parse_args()

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4" && rm
      -f salidas/personas_2024.parquet && uv run
      .claude/skills/limpiando-enaho/scripts/limpia…)
  ⎿  VALIDACIÓN · ENAHO 2024 (INEI), módulos 34 (sumaria) y 02 (miembros)
     Generado: 2026-11-08 14:11 con .claude/skills/limpiando-enaho/scripts/
     limpiar.py
     … +83 lines (ctrl+o to expand)
  ⎿  Created salidas\indicadores.csv (+36 -0)
       1 +nivel,codigo,categoria,pobreza_pct,pobreza_extrema_pct,n_obs,po
         +blacion_expandida                                              
       2 +nacional,,Perú,27.53,5.5,108664,34147768                       
       3 +area,,rural,39.44,15.6,36071,6486385                           
       4 +area,,urbana,24.74,3.13,72593,27661382                         
       5 +sexo,,hombre,27.37,5.37,52587,16453003                         
       6 +sexo,,mujer,27.68,5.62,56077,17694764                          
       7 +grupo_edad,,0-14,37.52,8.59,26489,7941994                      
       8 +grupo_edad,,15-29,25.97,4.5,23122,7512400                      
       9 +grupo_edad,,30-44,27.87,5.59,20648,6689119                     
      10 +grupo_edad,,45-59,21.41,3.58,19408,6130223                     
      11 +grupo_edad,,60 y más,22.02,4.49,18997,5874030                  
      12 +departamento,01,Amazonas,26.08,6.15,3911,430252                
      13 +departamento,02,Áncash,22.88,5.76,4576,1199410                 
      14 +departamento,03,Apurímac,24.09,5.18,2500,474458                
      15 +departamento,04,Arequipa,15.77,1.62,4645,1415224               
      16 +departamento,05,Ayacucho,33.04,9.24,3308,755197                
      17 +departamento,06,Cajamarca,44.99,19.62,4468,1547849             
      18 +departamento,07,Callao,33.77,4.98,3457,1138852                 
      19 +departamento,08,Cusco,18.54,2.15,3777,1380357                  
      20 +departamento,09,Huancavelica,33.61,11.28,3244,525028           
      21 +departamento,10,Huánuco,39.47,12.4,3903,910900                 
      22 +departamento,11,Ica,5.91,0.15,4838,855183                      
      23 +departamento,12,Junín,18.61,3.81,4658,1436462                  
      24 +departamento,13,La Libertad,30.07,6.58,5028,2064878            
      25 +departamento,14,Lambayeque,14.05,0.5,4405,1348585              
      26 +departamento,15,Lima,26.89,3.12,14823,11233286                 
      27 +departamento,16,Loreto,42.61,15.01,5678,1121012                
      28 +departamento,17,Madre de Dios,11.14,1.53,2045,165829           
      29 +departamento,18,Moquegua,10.88,2.34,2511,196788                
      30 +departamento,19,Pasco,39.28,8.27,2746,323033                   
      31 +departamento,20,Piura,31.81,4.36,5876,1970217                  
      32 +departamento,21,Puno,40.42,12.63,3112,1535441                  
      33 +departamento,22,San Martín,21.99,4.45,4619,937167              
      34 +departamento,23,Tacna,23.88,2.58,3622,375607                   
      35 +departamento,24,Tumbes,26.6,1.06,2771,261973                   
      36 +departamento,25,Ucayali,27.12,3.33,4143,544778                 
  ⎿  Updated salidas\validacion.txt (+1 -1)
      1  VALIDACIÓN · ENAHO 2024 (INEI), módulos 34 (sumaria) y 02 (miemb
         ros)
      2 -Generado: 2026-11-08 14:10 con .claude/skills/limpiando-enaho/sc
        -ripts/limpiar.py                                                
      2 +Generado: 2026-11-08 14:11 con .claude/skills/limpiando-enaho/sc
        +ripts/limpiar.py                                                
      3  Archivos: datos\966-Modulo34.zip::sumaria-2024.dta y datos\966-M
         odulo02.zip::enaho01-2024-200.dta
      4  Referencias: Data-Science-Python, sessions/16-skills-enaho/READM
         E.md (sección Validación)
      5  
  ⎿  … 1 more file changed

● Todas las esenciales pasan; dos informativas quedan fuera de ±0.1 pp (rural y
  Lima Metropolitana), y no las ajusto hasta verificar si la referencia usó la
  sumaria en vez de personas y si mi hipótesis sobre trabajadores del hogar y
  pensionistas es correcta.

  Ran 1 shell command (ctrl+o to expand)

● Las cifras de urbana, rural y Lima Met. con el método de la sumaria dan
  exactas, y con personas y facpob07 difieren solo ligeramente; mostraré ambos
  métodos en las informativas. También corrijo mi explicación de los
  trabajadores del hogar y pensionistas, que era exagerada, para decir solo lo
  verificado.

● Update(.claude\skills\limpiando-enaho\scripts\limpiar.py)
  ⎿  Added 18 lines, removed 10 lines
      163      chequear(True, "sexo y edad sin nulos en residentes", base
           ["sexo"].notna().all() and base["edad"].notna().all(),
      164               f"{int(base['sexo'].isna().sum())} sexo nulos, {i
           nt(base['edad'].isna().sum())} edad nulos")
      165  
      166 -    # Informativas (no detienen el script)                    
      167 -    por_area = {a: 100 * media_ponderada(g["pobre"], g["facpob
          -07"]) for a, g in base.groupby("area")}                       
      168 -    extrema = 100 * media_ponderada(base["pobre_extremo"], w) 
      169 -    lima_met = base[base["dominio"] == 8]                     
      170 -    pob_lima_met = 100 * media_ponderada(lima_met["pobre"], li
          -ma_met["facpob07"])                                           
      171 -    for nombre, valor, ref in (("Pobreza urbana (estrato <= 5)
          -", por_area["urbana"], REF_URBANA),                           
      172 -                               ("Pobreza rural (estrato >= 6)"
          -, por_area["rural"], REF_RURAL),                              
      173 -                               ("Pobreza extrema nacional", ex
          -trema, REF_EXTREMA),                                          
      174 -                               ("Pobreza Lima Metropolitana (d
          -ominio == 8)", pob_lima_met, REF_LIMA_MET)):                  
      175 -        chequear(False, f"{nombre} ~ {ref} %", abs(valor - ref
          -) <= TOL_POBREZA, f"{valor:.2f} %")                           
      166 +    # Informativas (no detienen el script). Se calculan con lo
          +s dos métodos y se muestran ambos:                            
      167 +    # las referencias del README de la sesión 16 coinciden con
          + el método de la sumaria.                                     
      168 +    s_pobre, s_ext = (sumaria["pobreza"] <= 2).astype(int), (s
          +umaria["pobreza"] == 1).astype(int)                           
      169 +    informativas = (                                          
      170 +        ("Pobreza urbana (estrato <= 5)", base["estrato"] <= 5
          +, sumaria["estrato"] <= 5, "pobre", s_pobre, REF_URBANA),     
      171 +        ("Pobreza rural (estrato >= 6)", base["estrato"] > 5, 
          +sumaria["estrato"] > 5, "pobre", s_pobre, REF_RURAL),         
      172 +        ("Pobreza extrema nacional", base["estrato"] > 0, suma
          +ria["estrato"] > 0, "pobre_extremo", s_ext, REF_EXTREMA),     
      173 +        ("Pobreza Lima Metropolitana (dominio == 8)", base["do
          +minio"] == 8, sumaria["dominio"] == 8, "pobre", s_pobre,      
      174 +         REF_LIMA_MET),                                       
      175 +    )                                                         
      176 +    for nombre, m_p, m_s, var, s_var, ref in informativas:    
      177 +        v_p = 100 * media_ponderada(base.loc[m_p, var], w[m_p]
          +)                                                             
      178 +        v_s = 100 * media_ponderada(s_var[m_s], w_hog[m_s])   
      179 +        chequear(False, f"{nombre} ~ {ref} % · personas, facpo
          +b07", abs(v_p - ref) <= TOL_POBREZA, f"{v_p:.2f} %")          
      180 +        chequear(False, f"{nombre} ~ {ref} % · sumaria, factor
          +07 × mieperho", abs(v_s - ref) <= TOL_POBREZA,                
      181 +                 f"{v_s:.2f} %")                              
      182  
      183      # Por qué difieren las dos pobrezas nacionales (cifras cal
           culadas aquí, no escritas a mano)
      184      res_por_hogar = base.groupby(LLAVES_HOGAR).size().rename("
           residentes")
      185      comp = sumaria.set_index(LLAVES_HOGAR)[["mieperho"]].join(
           res_por_hogar, how="left").fillna({"residentes": 0})
      186      hogares_distintos = int((comp["mieperho"] != comp["residen
           tes"]).sum())
      187 +    trab_hogar = int((base["p203"] == 8).sum())               
      188 +    pensionistas = int((base["p203"] == 9).sum())             
      189      pob_exp_personas = float(w.sum())
      190      pob_exp_sumaria = float(w_hog.sum())
      191  

● Update(.claude\skills\limpiando-enaho\scripts\limpiar.py)
  ⎿  Added 12 lines, removed 11 lines
      206          "",
      207          "POR QUÉ DIFIEREN LAS DOS POBREZAS NACIONALES",
      208          f"  Personas con facpob07: {pob_personas:.2f} %  ·  Su
           maria con factor07 × mieperho: {pob_sumaria:.2f} %",
      209 -        "  1. Distinta población de referencia: en la sumaria 
          -cada hogar pesa factor07 × mieperho, y mieperho",             
      210 -        "     cuenta a los miembros del hogar según la definic
          -ión del INEI; en personas cada residente habitual",           
      211 -        "     pesa su propio facpob07. En "                   
      212 -        f"{hogares_distintos:,} de {len(sumaria):,} hogares mi
          -eperho no coincide con el número de",                         
      213 -        "     residentes habituales del módulo 02 (p. ej., tra
          -bajadores del hogar y pensionistas, que mieperho",            
      214 -        "     excluye y el filtro de residentes puede incluir)
          -.",                                                           
      215 -        "  2. Distintos factores: facpob07 (población) y facto
          -r07 (hogares) se calibran por separado a las",                
      216 -        "     proyecciones del CPV 2007, así que no son propor
          -cionales entre sí.",                                          
      217 -        f"     Población expandida: {pob_exp_personas:,.0f} (p
          -ersonas, Σ facpob07) vs "                                     
      218 -        f"{pob_exp_sumaria:,.0f} (sumaria, Σ factor07 × mieper
          -ho).",                                                        
      219 -        "  La cifra oficial del INEI (27.6 %) redondea ambas; 
          -esta base usa siempre facpob07 a nivel de personas.",         
      209 +        "  1. Distintos factores: en la sumaria cada hogar pes
          +a factor07 × mieperho (todos sus miembros con el",            
      210 +        "     mismo peso); en personas cada residente habitual
          + pesa su propio facpob07. Son factores distintos",            
      211 +        "     del INEI y no son proporcionales entre sí. Pobla
          +ción expandida:",                                             
      212 +        f"     {pob_exp_personas:,.0f} (personas, Σ facpob07) 
          +vs {pob_exp_sumaria:,.0f} (sumaria, Σ factor07 × mieperho).", 
      213 +        "  2. Distinto conteo de personas por hogar: en "     
      214 +        f"{hogares_distintos:,} de {len(sumaria):,} hogares mi
          +eperho no coincide con el",                                   
      215 +        "     número de residentes habituales del módulo 02. E
          +ntre los residentes hay "                                     
      216 +        f"{trab_hogar} trabajadores del hogar",               
      217 +        f"     (p203 == 8) y {pensionistas} pensionistas (p203
          + == 9), así que eso explica solo una parte; el resto",        
      218 +        "     depende de la definición de mieperho del INEI (v
          +er Diccionario2024.pdf del módulo 34), no verificada aquí.",  
      219 +        "  La cifra oficial del INEI (27.6 %) redondea ambas. 
          +Las referencias informativas (urbana, rural, extrema,",       
      220 +        "  Lima Met.) coinciden con el método de la sumaria; e
          +sta base usa siempre facpob07 a nivel de personas.",          
      221          "",
      222          f"RESULTADO: {'TODAS LAS VALIDACIONES ESENCIALES PASAN
           ' if esenciales_ok else 'FALLA AL MENOS UNA VALIDACIÓN ESENCIA
           L'}",
      223      ]

● Ahora corro de nuevo y además pruebo el camino de error: fuerzo una referencia
  falsa (en una carpeta temporal, sin tocar el script) para comprobar que
  termina con exit 1 y no escribe la base.

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4" && rm
      -f salidas/personas_2024.parquet && uv run
      .claude/skills/limpiando-enaho/scripts/limpia…)
  ⎿  ESENCIALES (si alguna falla, no se escribe la base)
       [PASA ] Pobreza nacional (personas, facpob07) = 27.6 % ± 0.1 pp: 27.
     53 %
     … +42 lines (ctrl+o to expand)
  ⎿  Updated salidas\validacion.txt (+18 -13)
      18    [PASA ] sexo y edad sin nulos en residentes: 0 sexo nulos, 0 
          edad nulos
      19  
      20  INFORMATIVAS (tolerancia ± 0.1 pp; no detienen el script)
      21 -  [PASA ] Pobreza urbana (estrato <= 5) ~ 24.8 %: 24.74 %      
      22 -  [FALLA] Pobreza rural (estrato >= 6) ~ 39.3 %: 39.44 %       
      23 -  [PASA ] Pobreza extrema nacional ~ 5.5 %: 5.50 %             
      24 -  [FALLA] Pobreza Lima Metropolitana (dominio == 8) ~ 28.2 %: 2
         -8.03 %                                                         
      21 +  [PASA ] Pobreza urbana (estrato <= 5) ~ 24.8 % · personas, fa
         +cpob07: 24.74 %                                                
      22 +  [PASA ] Pobreza urbana (estrato <= 5) ~ 24.8 % · sumaria, fac
         +tor07 × mieperho: 24.81 %                                      
      23 +  [FALLA] Pobreza rural (estrato >= 6) ~ 39.3 % · personas, fac
         +pob07: 39.44 %                                                 
      24 +  [PASA ] Pobreza rural (estrato >= 6) ~ 39.3 % · sumaria, fact
         +or07 × mieperho: 39.30 %                                       
      25 +  [PASA ] Pobreza extrema nacional ~ 5.5 % · personas, facpob07
         +: 5.50 %                                                       
      26 +  [PASA ] Pobreza extrema nacional ~ 5.5 % · sumaria, factor07 
         +× mieperho: 5.50 %                                             
      27 +  [FALLA] Pobreza Lima Metropolitana (dominio == 8) ~ 28.2 % · 
         +personas, facpob07: 28.03 %                                    
      28 +  [PASA ] Pobreza Lima Metropolitana (dominio == 8) ~ 28.2 % · 
         +sumaria, factor07 × mieperho: 28.21 %                          
      29  
      30  POR QUÉ DIFIEREN LAS DOS POBREZAS NACIONALES
      31    Personas con facpob07: 27.53 %  ·  Sumaria con factor07 × mie
          perho: 27.58 %
      28 -  1. Distinta población de referencia: en la sumaria cada hogar
         - pesa factor07 × mieperho, y mieperho                          
      29 -     cuenta a los miembros del hogar según la definición del IN
         -EI; en personas cada residente habitual                        
      30 -     pesa su propio facpob07. En 1,846 de 33,691 hogares mieper
         -ho no coincide con el número de                                
      31 -     residentes habituales del módulo 02 (p. ej., trabajadores 
         -del hogar y pensionistas, que mieperho                         
      32 -     excluye y el filtro de residentes puede incluir).         
      33 -  2. Distintos factores: facpob07 (población) y factor07 (hogar
         -es) se calibran por separado a las                             
      34 -     proyecciones del CPV 2007, así que no son proporcionales e
         -ntre sí.                                                       
      35 -     Población expandida: 34,147,768 (personas, Σ facpob07) vs 
         -34,482,700 (sumaria, Σ factor07 × mieperho).                   
      36 -  La cifra oficial del INEI (27.6 %) redondea ambas; esta base 
         -usa siempre facpob07 a nivel de personas.                      
      32 +  1. Distintos factores: en la sumaria cada hogar pesa factor07
         + × mieperho (todos sus miembros con el                         
      33 +     mismo peso); en personas cada residente habitual pesa su p
         +ropio facpob07. Son factores distintos                         
      34 +     del INEI y no son proporcionales entre sí. Población expan
         +dida:                                                          
      35 +     34,147,768 (personas, Σ facpob07) vs 34,482,700 (sumaria, 
         +Σ factor07 × mieperho).                                        
      36 +  2. Distinto conteo de personas por hogar: en 1,846 de 33,691 
         +hogares mieperho no coincide con el                            
      37 +     número de residentes habituales del módulo 02. Entre los r
         +esidentes hay 44 trabajadores del hogar                        
      38 +     (p203 == 8) y 0 pensionistas (p203 == 9), así que eso expl
         +ica solo una parte; el resto                                   
      39 +     depende de la definición de mieperho del INEI (ver Diccion
         +ario2024.pdf del módulo 34), no verificada aquí.               
      40 +  La cifra oficial del INEI (27.6 %) redondea ambas. Las refere
         +ncias informativas (urbana, rural, extrema,                    
      41 +  Lima Met.) coinciden con el método de la sumaria; esta base u
         +sa siempre facpob07 a nivel de personas.                       
      42  
      43  RESULTADO: TODAS LAS VALIDACIONES ESENCIALES PASAN
      44  Base escrita: salidas\personas_2024.parquet (108,664 filas)

● Ambas pruebas salen bien: con datos reales todas las esenciales pasan, y con
  una referencia falsa el proceso termina con exit 1 sin escribir el parquet.
  Siguiente: SKILL.md, reference.md y .gitignore.

● Write(.claude\skills\limpiando-enaho\SKILL.md)
  ⎿  Wrote 57 lines to .claude\skills\limpiando-enaho\SKILL.md
      1 ---
      2 name: limpiando-enaho
      3 description: Limpia y une los módulos 34 (sumaria) y 02 (miembros
        ) de la ENAHO 2024 del INEI y arma una base de personas con pobre
        za monetaria y factor de expansión facpob07, validada contra la c
        ifra oficial (27.6 %). Úsala cuando pidan limpiar, unir o analiza
        r la ENAHO, o calcular la pobreza o pobreza extrema del Perú por 
        departamento, región, área urbana o rural, sexo o edad.
      4 ---
      5 
     … +52 lines (ctrl+o to expand)

● Write(.claude\skills\limpiando-enaho\reference.md)
  ⎿  Wrote 91 lines to .claude\skills\limpiando-enaho\reference.md
       1 # ENAHO 2024 · Diccionario de variables usadas y trampas
       2 
       3 Fuente de las etiquetas: las *value labels* y *variable labels* 
         de los propios `.dta` del INEI
       4 (`966-Modulo34/sumaria-2024.dta` y `966-Modulo02/enaho01-2024-20
         0.dta`), leídas con pandas. El diccionario
       5 oficial completo viene en el zip del módulo 34 (`Diccionario2024
         .pdf`).
       6 
       7 ## Archivos
     … +84 lines (ctrl+o to expand)
● Verifico en los datos la afirmación sobre Lima Metropolitana (trampa 9) y
  actualizo .gitignore:

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4" && uv
      run python -c "
      import pandas as pd; b=pd.read_parquet('salidas/personas_2024.parquet');…)
  ⎿  departamento
     07     3457
     15    10106
     … +30 lines (ctrl+o to expand)
  ⎿  Updated .gitignore (+4 -0)
      20  # Archivos temporales del sistema
      21  .DS_Store
      22  Thumbs.db
      23 +                                                               
      24 +# Base limpia de la ENAHO: es microdato, no se versiona        
      25 +salidas/personas_2024.parquet                                  
      26 +*.parquet                                                      
  ⎿  1 skill available

● Comprobado: dominio == 8 junta Callao (07) y parte de Lima (15). Lo dejo
  preciso en la trampa 9 y hago el commit de la skill 1 (sin tocar tus archivos
  de evidencias_ia/, que son tuyos).

● Update(.claude\skills\limpiando-enaho\reference.md)
  ⎿  Added 2 lines, removed 1 line
      86     coinciden con el método de la sumaria; con personas dan 24.7
          4, 39.44 y 28.03 (ver `salidas/validacion.txt`).
      87  8. **`ubigeo` y `estrato` están en ambos módulos.** En la unión
           se comprobó que coinciden en todas las filas.
      88  9. **Lima y Callao.** El departamento 15 (Lima) y la Provincia 
          Constitucional del Callao (07) son unidades
      89 -   distintas. `dominio == 8` (Lima Metropolitana) es otro recor
         -te: no es igual al departamento 15.                            
      89 +   distintas. `dominio == 8` (Lima Metropolitana) es otro recor
         +te: en la base incluye todo Callao (07) y                      
      90 +   parte de Lima (15), así que no es igual al departamento 15. 
      91  10. **Muestra, no censo.** Las estimaciones por departamento o 
          grupos chicos tienen error muestral; esta base
      92      no calcula intervalos de confianza (requeriría el diseño mu
          estral: estrato y conglomerado).

  Ran 1 shell command (ctrl+o to expand)
  ⎿  PostToolUse:Bash says: Tip: Run /ultrareview before you push to catch bugs 
     with a cloud-based multi-agent review — 3 free reviews left.

● Skill 1 (limpiando-enaho) quedó lista en el commit 6dda9fa, con validaciones
  pasando y Claude Code ya la detectó sin reiniciar. Sigo con graficando-enaho y
  cargo la guía de visualización antes de escribir el código de gráficos.

● Skill(dataviz)
  ⎿  Successfully loaded skill

● Usaré la paleta del CLAUDE.md, con barras en verde selva y la línea del
  promedio en morado, y como las figuras son PNG estáticas no aplica la capa de
  hover. Los títulos se generarán desde los datos para no escribir cifras a
  mano.

● Write(.claude\skills\graficando-enaho\scripts\graficar.py)
  ⎿  Wrote 151 lines to .claude\skills\graficando-enaho\scripts\graficar.py
       1 """Gráficos de pobreza monetaria (ENAHO 2024, INEI), ponderados 
         con facpob07.
       2 
       3 Se corre desde tarea_4/:
       4     uv run .claude/skills/graficando-enaho/scripts/graficar.py -
         -por area
       5     uv run .claude/skills/graficando-enaho/scripts/graficar.py -
         -por sexo
       6     uv run .claude/skills/graficando-enaho/scripts/graficar.py -
         -por edad
     … +145 lines (ctrl+o to expand)

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4" && for
      p in area sexo edad departamento; do uv run
      .claude/skills/graficando-enaho/scripts/gra…)
  ⎿  Figura: figuras\pobreza_area.png
     Pobreza nacional (facpob07): 27.53 %
             pobreza_pct  n_obs
     … +44 lines (ctrl+o to expand)
  ⎿  4 files changed (binary, mode only or too large to show)

● Las cuatro corren. Ahora miro cada figura antes de darlas por buenas:

  Read 2 files (ctrl+o to expand)

● Tres cosas fallan en los gráficos: la etiqueta del promedio y el "24.7 %"
  chocan con las barras y la línea punteada, algunos valores quedan tachados por
  esa línea, y sobra espacio entre título y subtítulo. Voy a mover los valores
  dentro de las barras, poner fondo a los de las horizontales y usar un diseño
  constrained para cerrar el hueco.

  Ran 2 shell commands (ctrl+o to expand)

● La última línea de mi reemplazo no existía y por eso no se aplicó nada. La
  quito y lo repito:

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4/.claude/
      skills/graficando-enaho/scripts" && uv run --project ../../../.. python -
      <<'EOF'
      from…)
  ⎿  aplicado
     ok
  ⎿  Updated .claude\skills\graficando-enaho\scripts\graficar.py (+154 
     -151)
        1 -"""Gráficos de pobreza monetaria (ENAHO 2024, INEI), ponderado
          -s con facpob07.                                               
        2 -                                                              
        3 -Se corre desde tarea_4/:                                      
        4 -    uv run .claude/skills/graficando-enaho/scripts/graficar.py
          - --por area                                                   
        5 -    uv run .claude/skills/graficando-enaho/scripts/graficar.py
          - --por sexo                                                   
        6 -    uv run .claude/skills/graficando-enaho/scripts/graficar.py
          - --por edad                                                   
        7 -    uv run .claude/skills/graficando-enaho/scripts/graficar.py
          - --por departamento                                           
        8 -    uv run .claude/skills/graficando-enaho/scripts/graficar.py
          - --por todos                                                  
        9 -                                                              
       10 -Lee salidas/personas_2024.parquet (lo crea la skill limpiando-
          -enaho) y guarda figuras/pobreza_<por>.png a 200 dpi.          
       11 -Imprime las cifras graficadas para que quien lo pida pueda cit
          -arlas.                                                        
       12 -"""                                                           
       13 -import argparse                                               
       14 -import sys                                                    
       15 -from pathlib import Path                                      
       16 -                                                              
       17 -import matplotlib                                             
       18 -                                                              
       19 -matplotlib.use("Agg")                                         
       20 -import matplotlib.pyplot as plt  # noqa: E402                 
       21 -import pandas as pd  # noqa: E402                             
       22 -                                                              
       23 -BASE = Path("salidas/personas_2024.parquet")                  
       24 -FIGURAS = Path("figuras")                                     
       25 -FUENTE = "Fuente: INEI, ENAHO 2024 (módulos 34 y 02). Elaborac
          -ión propia, ponderado con facpob07."                          
       26 -UNIDAD = "% de personas en pobreza monetaria"                 
       27 -                                                              
       28 -# Paleta del proyecto                                         
       29 -CREMA, CARBON, VERDE, MORADO, GRIS = "#F7F3EA", "#2B2B2B", "#1
          -F5F4A", "#6A4C93", "#8A8578"                                  
       30 -                                                              
       31 -COLUMNA = {"area": "area", "sexo": "sexo", "edad": "grupo_edad
          -", "departamento": "departamento_nombre"}                     
       32 -ETIQUETAS = {"urbana": "Urbana", "rural": "Rural", "hombre": "
          -Hombres", "mujer": "Mujeres"}                                 
       33 -ORDEN_EDAD = ["0-14", "15-29", "30-44", "45-59", "60 y más"]  
       34 -                                                              
       35 -                                                              
       36 -def pobreza_por(base, col):                                   
       37 -    g = base.assign(_wp=base["pobre"] * base["facpob07"]).grou
          -pby(col, observed=True)                                       
       38 -    t = pd.DataFrame({"pobreza_pct": 100 * g["_wp"].sum() / g[
          -"facpob07"].sum(), "n_obs": g.size()})                        
       39 -    return t                                                  
       40 -                                                              
     … 265 more lines (ctrl+o to expand)
  ⎿  … 4 more files changed

  Read 4 files (ctrl+o to expand)

● Mejoraron, pero el promedio de área y edad todavía tapa títulos y barras, y en
  sexo casi no hay espacio arriba. Voy a pasar el promedio a una leyenda en un
  espacio libre y poner el valor dentro de la barra en los departamentos
  cercanos al promedio.

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4/.claude/
      skills/graficando-enaho/scripts" && uv run --project ../../../.. python -
      <<'EOF'
      from…)
  ⎿  aplicado
     ok
  ⎿  Updated .claude\skills\graficando-enaho\scripts\graficar.py (+8 -6)
      64      estilo(ax)
      65      x = range(len(t))
      66      ax.bar(x, t["pobreza_pct"], color=VERDE, width=0.6, zorder=
          2)
      67 -    ax.axhline(nacional, color=MORADO, lw=1.5, ls="--", zorder=
         -3)                                                             
      67 +    ax.axhline(nacional, color=MORADO, lw=1.5, ls="--", zorder=
         +3, label=f"Promedio nacional: {nacional:.1f} %")               
      68      for i, v in enumerate(t["pobreza_pct"]):   # el valor va de
          ntro de la barra, lejos de la línea
      69          ax.text(i, v / 2, f"{v:.1f} %", ha="center", va="center
          ", fontsize=12, fontweight="bold", color=CREMA,
      70                  zorder=4)
      71 -    ax.text(-0.5, nacional + 0.6, f"Promedio nacional: {naciona
         -l:.1f} %", ha="left", va="bottom", fontsize=9,                 
      72 -            color=MORADO, zorder=4, bbox=dict(facecolor=CREMA, 
         -edgecolor="none", pad=1.5))                                    
      71 +    ley = ax.legend(loc="upper left", frameon=False, fontsize=9
         +.5, borderaxespad=0.2)                                         
      72 +    ley.get_texts()[0].set_color(MORADO)                       
      73      ax.set_xticks(list(x), [f"{c}\n(n = {n:,})" for c, n in zip
          (t.index, t["n_obs"])])
      74 -    ax.set_ylim(0, max(t["pobreza_pct"].max(), nacional) * 1.18
         -)                                                              
      74 +    ax.set_ylim(0, max(t["pobreza_pct"].max(), nacional) * 1.3)
      75      ax.set_ylabel(UNIDAD, color=CARBON)
      76      ax.yaxis.grid(True, color="#E2DCCF", lw=0.8, zorder=0)
      77      cerrar(fig, ax, titulo, f"Perú, 2024 · {UNIDAD}", salida)
     ...
      84      y = range(len(t))
      85      ax.barh(y, t["pobreza_pct"], color=VERDE, height=0.7, zorde
          r=2)
      86      for i, v in enumerate(t["pobreza_pct"]):
      87 -        ax.text(v + 0.4, i, f"{v:.1f}", va="center", fontsize=8
         -.5, color=CARBON, zorder=4,                                    
      88 -                bbox=dict(facecolor=CREMA, edgecolor="none", pa
         -d=1))                                                          
      87 +        if 0 < nacional - v < 3:   # la etiqueta chocaría con l
         +a línea del promedio: va dentro de la barra                    
      88 +            ax.text(v - 0.4, i, f"{v:.1f}", va="center", ha="ri
         +ght", fontsize=8.5, color=CREMA, zorder=4)                     
      89 +        else:                                                  
      90 +            ax.text(v + 0.4, i, f"{v:.1f}", va="center", fontsi
         +ze=8.5, color=CARBON, zorder=4)                                
      91      ax.axvline(nacional, color=MORADO, lw=1.5, ls="--", zorder=
          3)
      92      ax.text(nacional + 0.4, len(t) - 0.45, f"Promedio nacional:
           {nacional:.1f} %", fontsize=9, color=MORADO,
      93              va="bottom", zorder=4)
  ⎿  … 4 more files changed

  Read 4 files (ctrl+o to expand)

● Las cuatro figuras ya se leen bien. Dejé una advertencia en SKILL.md: la
  diferencia de 0.3 puntos en sexo puede no ser significativa, porque no
  calculamos intervalos.

● Write(.claude\skills\graficando-enaho\SKILL.md)
  ⎿  Wrote 50 lines to .claude\skills\graficando-enaho\SKILL.md
       1 ---
       2 name: graficando-enaho
       3 description: Hace gráficos de barras de la pobreza monetaria del
          Perú con la ENAHO 2024 del INEI, ponderados con facpob07, por á
         rea urbana y rural, por sexo, por grupo de edad o por departamen
         to (con el promedio nacional). Úsala cuando pidan un gráfico, gr
         áfica, figura o barras de la pobreza, o comparar la pobreza entr
         e zonas, mujeres y hombres, edades o departamentos con la ENAHO.
       4 ---
       5 
     … +45 lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

● Skill 2 quedó lista (graficando-enaho, commit 17e0a64). Ahora sigo con
  mapeando-enaho, revisando el mapa de referencia y la estructura del GeoJSON.

  Read 1 file, ran 1 shell command (ctrl+o to expand)
  ⎿  1 skill available

● El mapa de referencia usa el método de la sumaria (factor07 × mieperho), no
  facpob07, así que parte de las diferencias por departamento vendrán del
  método. Incluiré ese valor en la comparación para que se vea de dónde sale
  cada diferencia.

● Write(.claude\skills\mapeando-enaho\scripts\mapear.py)
  ⎿  Wrote 156 lines to .claude\skills\mapeando-enaho\scripts\mapear.py
       1 """Mapa de la pobreza monetaria por departamento (ENAHO 2024, IN
         EI), ponderado con facpob07.
       2 
       3 Se corre desde tarea_4/:
       4     uv run .claude/skills/mapeando-enaho/scripts/mapear.py
       5 
       6 Entra:  salidas/personas_2024.parquet (lo crea la skill limpiand
         o-enaho)
       7         datos/peru_departamental_simple.geojson (si no está, se 
         descarga del repositorio del curso)
     … +149 lines (ctrl+o to expand)

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4" && uv
      run .claude/skills/mapeando-enaho/scripts/mapear.py; echo "exit=$?"; uv
      run python -c "…)  ⎿  No está datos\peru_departamental_simple.geojson; lo descargo de https:
     //raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions
     /06-geoespacial/lab/Data/peru_departamental_simple.geojson
     … +70 lines (ctrl+o to expand)
  ⎿  Created salidas\comparacion_mapa_referencia.csv (+26 -0)
       1 +ccdd,departamento,referencia_pct,calculado_facpob07_pct,diferen
         +cia_pp,pobreza_metodo_sumaria_pct,diferencia_metodo_sumaria_pp,
         +n_obs,poblacion_expandida                                      
       2 +01,AMAZONAS,25.7,26.08,0.38,25.75,0.05,3911,430252.0           
       3 +02,ANCASH,22.8,22.88,0.08,22.77,-0.03,4576,1.19941e+06         
       4 +03,APURIMAC,24.0,24.09,0.09,23.96,-0.04,2500,474458.0          
       5 +04,AREQUIPA,15.8,15.77,-0.03,15.78,-0.02,4645,1.415224e+06     
       6 +05,AYACUCHO,32.8,33.04,0.24,32.76,-0.04,3308,755197.0          
       7 +06,CAJAMARCA,45.0,44.99,-0.01,45.01,0.01,4468,1.547849e+06     
       8 +07,CALLAO,33.9,33.77,-0.13,33.86,-0.04,3457,1.138852e+06       
       9 +08,CUSCO,18.5,18.54,0.04,18.54,0.04,3777,1.380357e+06          
      10 +09,HUANCAVELICA,33.4,33.61,0.21,33.4,0.0,3244,525028.0         
      11 +10,HUANUCO,39.0,39.47,0.47,38.96,-0.04,3903,910900.0           
      12 +11,ICA,6.0,5.91,-0.09,6.01,0.01,4838,855183.0                  
      13 +12,JUNIN,18.5,18.61,0.11,18.5,-0.0,4658,1.436462e+06           
      14 +13,LA LIBERTAD,30.2,30.07,-0.13,30.19,-0.01,5028,2.064878e+06  
      15 +14,LAMBAYEQUE,14.0,14.05,0.05,14.04,0.04,4405,1.348585e+06     
      16 +15,LIMA,27.1,26.89,-0.21,27.07,-0.03,14823,1.1233286e+07       
      17 +16,LORETO,43.0,42.61,-0.39,42.97,-0.03,5678,1.121012e+06       
      18 +17,MADRE DE DIOS,11.1,11.14,0.04,11.15,0.05,2045,165829.0      
      19 +18,MOQUEGUA,11.0,10.88,-0.12,10.97,-0.03,2511,196788.0         
      20 +19,PASCO,39.0,39.28,0.28,38.97,-0.03,2746,323033.0             
      21 +20,PIURA,31.9,31.81,-0.09,31.86,-0.04,5876,1.970217e+06        
      22 +21,PUNO,39.9,40.42,0.52,39.94,0.04,3112,1.535441e+06           
      23 +22,SAN MARTIN,22.0,21.99,-0.01,22.02,0.02,4619,937167.0        
      24 +23,TACNA,24.0,23.88,-0.12,23.99,-0.01,3622,375607.0            
      25 +24,TUMBES,26.9,26.6,-0.3,26.9,0.0,2771,261973.0                
      26 +25,UCAYALI,27.1,27.12,0.02,27.07,-0.03,4143,544778.0           
  ⎿  … 1 more file changed

● Con el método de la sumaria, los 25 departamentos coinciden con la referencia
  salvo redondeo, mientras que con facpob07, la regla del curso, Puno queda
  +0.52 pp arriba. No ajusto nada y lo dejo documentado en el CSV; ahora reviso
  el mapa.

● Update(.claude\skills\mapeando-enaho\scripts\mapear.py)
  ⎿  Added 1 line
      81          error(f"no existe {BASE}. Usa primero la skill limpiand
          o-enaho "
      82                "(uv run .claude/skills/limpiando-enaho/scripts/l
          impiar.py).")
      83      base = pd.read_parquet(BASE)
      84 +    base[["facpob07", "factor07"]] = base[["facpob07", "factor0
         +7"]].astype("float64")   # evita ruido de float32              
      85      base["departamento"] = base["ubigeo"].astype(str).str[:2]
      86      t, n_hogares = pobreza_departamental(base)
      87  

  Read 1 file (ctrl+o to expand)

● El mapa coincide con la referencia, con Cajamarca como el tono más oscuro y
  Callao casi invisible a esta escala. Ahora escribo el SKILL.md.

● Write(.claude\skills\mapeando-enaho\SKILL.md)
  ⎿  Wrote 47 lines to .claude\skills\mapeando-enaho\SKILL.md
       1 ---
       2 name: mapeando-enaho
       3 description: Hace un mapa coroplético de la pobreza monetaria po
         r departamento del Perú con la ENAHO 2024 del INEI (25 departame
         ntos, Lima y Callao separados), ponderado con facpob07, y lo com
         para con la referencia oficial. Úsala cuando pidan un mapa de la
          pobreza, un mapa por departamento o región, o ver geográficamen
         te dónde hay más pobreza en el Perú con la ENAHO.
       4 ---
       5 
     … +42 lines (ctrl+o to expand)

● Bash(cd "/c/Users/Antonio Macedo/repos/Python_Intermedio_2026/tarea_4" && echo
      "== sin base: graficar y mapear deben pedir limpiando-enaho ==" && rm -f
      salidas/perso…)
  ⎿  == sin base: graficar y mapear deben pedir limpiando-enaho ==
     ERROR: no existe salidas\personas_2024.parquet. Usa primero la skill l
     impiando-enaho (uv run .claude/skills/limpiando-enaho/scripts/limpiar.
     … +41 lines (ctrl+o to expand)
  ⎿  Updated salidas\comparacion_mapa_referencia.csv (+12 -12)
       1  ccdd,departamento,referencia_pct,calculado_facpob07_pct,diferen
          cia_pp,pobreza_metodo_sumaria_pct,diferencia_metodo_sumaria_pp,
          n_obs,poblacion_expandida
       2  01,AMAZONAS,25.7,26.08,0.38,25.75,0.05,3911,430252.0
       3 -02,ANCASH,22.8,22.88,0.08,22.77,-0.03,4576,1.19941e+06         
       3 +02,ANCASH,22.8,22.88,0.08,22.77,-0.03,4576,1199410.0           
       4  03,APURIMAC,24.0,24.09,0.09,23.96,-0.04,2500,474458.0
       5 -04,AREQUIPA,15.8,15.77,-0.03,15.78,-0.02,4645,1.415224e+06     
       5 +04,AREQUIPA,15.8,15.77,-0.03,15.78,-0.02,4645,1415224.0        
       6  05,AYACUCHO,32.8,33.04,0.24,32.76,-0.04,3308,755197.0
       7 -06,CAJAMARCA,45.0,44.99,-0.01,45.01,0.01,4468,1.547849e+06     
       8 -07,CALLAO,33.9,33.77,-0.13,33.86,-0.04,3457,1.138852e+06       
       9 -08,CUSCO,18.5,18.54,0.04,18.54,0.04,3777,1.380357e+06          
       7 +06,CAJAMARCA,45.0,44.99,-0.01,45.01,0.01,4468,1547849.0        
       8 +07,CALLAO,33.9,33.77,-0.13,33.86,-0.04,3457,1138852.0          
       9 +08,CUSCO,18.5,18.54,0.04,18.54,0.04,3777,1380357.0             
      10  09,HUANCAVELICA,33.4,33.61,0.21,33.4,0.0,3244,525028.0
      11  10,HUANUCO,39.0,39.47,0.47,38.96,-0.04,3903,910900.0
      12  11,ICA,6.0,5.91,-0.09,6.01,0.01,4838,855183.0
      13 -12,JUNIN,18.5,18.61,0.11,18.5,-0.0,4658,1.436462e+06           
      14 -13,LA LIBERTAD,30.2,30.07,-0.13,30.19,-0.01,5028,2.064878e+06  
      15 -14,LAMBAYEQUE,14.0,14.05,0.05,14.04,0.04,4405,1.348585e+06     
      16 -15,LIMA,27.1,26.89,-0.21,27.07,-0.03,14823,1.1233286e+07       
      17 -16,LORETO,43.0,42.61,-0.39,42.97,-0.03,5678,1.121012e+06       
      13 +12,JUNIN,18.5,18.61,0.11,18.5,-0.0,4658,1436462.0              
      14 +13,LA LIBERTAD,30.2,30.07,-0.13,30.19,-0.01,5028,2064878.0     
      15 +14,LAMBAYEQUE,14.0,14.05,0.05,14.04,0.04,4405,1348585.0        
      16 +15,LIMA,27.1,26.89,-0.21,27.07,-0.03,14823,11233286.0          
      17 +16,LORETO,43.0,42.61,-0.39,42.97,-0.03,5678,1121012.0          
      18  17,MADRE DE DIOS,11.1,11.14,0.04,11.15,0.05,2045,165829.0
      19  18,MOQUEGUA,11.0,10.88,-0.12,10.97,-0.03,2511,196788.0
      20  19,PASCO,39.0,39.28,0.28,38.97,-0.03,2746,323033.0
      21 -20,PIURA,31.9,31.81,-0.09,31.86,-0.04,5876,1.970217e+06        
      22 -21,PUNO,39.9,40.42,0.52,39.94,0.04,3112,1.535441e+06           
      21 +20,PIURA,31.9,31.81,-0.09,31.86,-0.04,5876,1970217.0           
      22 +21,PUNO,39.9,40.42,0.52,39.94,0.04,3112,1535441.0              
      23  22,SAN MARTIN,22.0,21.99,-0.01,22.02,0.02,4619,937167.0
      24  23,TACNA,24.0,23.88,-0.12,23.99,-0.01,3622,375607.0
      25  24,TUMBES,26.9,26.6,-0.3,26.9,0.0,2771,261973.0
  ⎿  Updated salidas\validacion.txt (+1 -1)
      1  VALIDACIÓN · ENAHO 2024 (INEI), módulos 34 (sumaria) y 02 (miemb
         ros)
      2 -Generado: 2026-11-08 14:11 con .claude/skills/limpiando-enaho/sc
        -ripts/limpiar.py                                                
      2 +Generado: 2026-11-08 14:46 con .claude/skills/limpiando-enaho/sc
        +ripts/limpiar.py                                                
      3  Archivos: datos\966-Modulo34.zip::sumaria-2024.dta y datos\966-M
         odulo02.zip::enaho01-2024-200.dta
      4  Referencias: Data-Science-Python, sessions/16-skills-enaho/READM
         E.md (sección Validación)
      5  

● La prueba completa desde cero pasa en ambos casos: sin la base fallan graficar
  y mapear con un aviso para usar limpiando-enaho, y con ella todo termina
  bien. Las figuras son idénticas byte a byte, el parquet está ignorado por git,
  y ahora hago el commit de la skill 3 y el push.

  Pushed to main (ctrl+o to expand)
  ⎿  1 skill available

● Todo subido. Por último dejo el resumen de la sesión que pide tu CLAUDE.md:

  Ran 1 shell command (ctrl+o to expand)

● Write(trabajo_manual\RESUMEN_2026-11-08.md)
  ⎿  Wrote 26 lines to trabajo_manual\RESUMEN_2026-11-08.md
       1 # Resumen · 08/11/2026 · Tarea 4, Parte 2 (Skills de la ENAHO 20
         24)
       2 
       3 ## Qué se hizo
       4 - Tres skills en `.claude/skills/`: `limpiando-enaho` (SKILL.md,
          reference.md, scripts/limpiar.py),
       5   `graficando-enaho` (SKILL.md, scripts/graficar.py) y `mapeando
         -enaho` (SKILL.md, scripts/mapear.py).
       6 - Copiada `referencias/pobreza_departamento_2024.csv` (sesión 16
         ).
     … +20 lines (ctrl+o to expand)

● Terminé la Parte 2: las tres skills están hechas, probadas desde cero y
  subidas a GitHub. Todas las validaciones esenciales pasan.

  1. salidas/validacion.txt

  Esenciales: las 12 PASAN.
  - Pobreza nacional: 27.53 % con personas y facpob07, y 27.58 % con la sumaria
    y factor07 × mieperho. Ambas están dentro de 27.6 ± 0.1.
  - Residentes habituales: 108,664 de 117,721 filas del módulo 02.
  - Departamentos: 25 códigos, del 01 al 25.
  - Llaves: únicas en la sumaria y en personas.
  - Unión: no pierde ni duplica filas (108,664 antes y después).
  - Factores, pobreza, sexo y edad: sin nulos, y los factores son positivos.

  Informativas: 2 salen FALLA a propósito, no por un error. Las calculé con los
  dos métodos y descubrí que las referencias del curso usan el de la sumaria:

  ┌───────────────────┬───────────────────────┬───────────────┬────────────┐
  │       Cifra       │    Con personas y     │    Con la     │ Referencia │
  │                   │       facpob07        │    sumaria    │            │
  ├───────────────────┼───────────────────────┼───────────────┼────────────┤
  │ Urbana            │ 24.74                 │ 24.81         │ 24.8       │
  ├───────────────────┼───────────────────────┼───────────────┼────────────┤
  │ Rural             │ 39.44 (FALLA)         │ 39.30         │ 39.3       │
  ├───────────────────┼───────────────────────┼───────────────┼────────────┤
  │ Extrema           │ 5.50                  │ 5.50          │ 5.5        │
  ├───────────────────┼───────────────────────┼───────────────┼────────────┤
  │ Lima              │ 28.03 (FALLA)         │ 28.21         │ 28.2       │
  │ Metropolitana     │                       │               │            │
  └───────────────────┴───────────────────────┴───────────────┴────────────┘

  No ajusté nada; el archivo explica la diferencia. Al revisarla corregí una
  explicación mía que no estaba verificada: yo había dicho que los trabajadores
  del hogar explicaban la diferencia, pero solo hay 44 entre los residentes.
  Ahora el archivo dice solo lo comprobado y marca como "no verificada" la parte
  que depende de cómo define el INEI mieperho.

  2. Figuras (revisé cada una y corregí textos que chocaban antes de darlas por 
  buenas)

  - figuras/pobreza_area.png
  - figuras/pobreza_sexo.png
  - figuras/pobreza_edad.png
  - figuras/pobreza_departamento.png
  - mapas/pobreza_departamento.png

  3. Diferencia máxima contra la referencia

  - +0.52 pp en Puno (40.42 % calculado frente a 39.9 % de referencia), con
    facpob07, que es lo que muestra el mapa.
  - Con el método de la sumaria, los 25 departamentos coinciden en ±0.05 pp. El
    propio mapa de referencia dice en su pie que usó factor07 × mieperho, así
    que es una diferencia de método, no un error. Todo queda en
    salidas/comparacion_mapa_referencia.csv.

  4. ¿Hay que reiniciar Claude Code?

  No hizo falta: esta sesión detectó las tres skills apenas creé cada SKILL.md.
  En una sesión nueva aparecen solas. Si /skills no las muestra, reinicia.

  5. Cómo probar que se activan solas

  Abre una sesión nueva en tarea_4/ y escribe los pedidos de la sesión 16, sin
  nombrar ninguna skill:
  ¿Cuál fue la pobreza en Cusco en 2024?            → limpiando-enaho (debe dar 
  ~18.5 %)
  Grafica la pobreza urbana y rural                 → graficando-enaho
  Haz un mapa de la pobreza por departamento        → mapeando-enaho
  Claude Code muestra en la conversación qué skill usó. Para probar que se
  activan dos seguidas, borra antes salidas/personas_2024.parquet: el pedido del
  mapa debería usar primero limpiando-enaho. Para comparar sin skills: claude 
  -p --disallowedTools Skill "...". Esas corridas y capturas te tocan a ti,
  porque son evidencia.

  Decisiones de método que conviene que revises

  - Sumaria: el zip trae dos versiones (sumaria-2024.dta y -12g). Usé la
    estándar; ambas dan la misma pobreza.
  - Grupos de edad: 0-14, 15-29, 30-44, 45-59 y 60 y más (60 es el umbral de
    adulto mayor en Perú).
  - Diferencia por sexo: son 0.3 puntos y no calculamos intervalos de confianza.
    El SKILL.md advierte que no se presente como una brecha real.

  Commits: 6dda9fa (limpiando), 17e0a64 (graficando) y ddf17a4 (mapeando), con
  push a main.

  Lo que creé sin subir: tarea_4/trabajo_manual/RESUMEN_2026-11-08.md (el
  resumen de la sesión). No toqué tus archivos de evidencias_ia/mcp/. Ojo:
  captura_mcp_conectado.png.png tiene la extensión repetida.

  Comentario para el Issue #201 (T4 – Parte 2):

  ▎ Parte 2 lista: skills limpiando-enaho, graficando-enaho y mapeando-enaho en 
  ▎ .claude/skills/, probadas desde cero. Validación: pobreza 27.53 % (facpob07)
  ▎ / 27.58 % (sumaria), 108,664 residentes, 25 departamentos; mapa a +0.52 pp 
  ▎ máx. de la referencia (Puno), por diferencia de método. Commits 6dda9fa, 
  ▎ 17e0a64, ddf17a4.

✻ Cogitated for 8m 44s · done 2:47 p.m.