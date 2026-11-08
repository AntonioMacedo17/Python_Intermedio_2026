"""¿Mejoran el MCP del BCRP y las skills de la ENAHO las respuestas de Claude Code? Mismas preguntas en dos modos.

    uv run evaluacion/evaluar.py                          # desde tarea_4/: 10 preguntas × modos A y B, sonnet
    uv run evaluacion/evaluar.py --ids B1 --salida /tmp/prueba.csv     # prueba con una pregunta

Adaptado de Data-Science-Python, sessions/04-mcp-claude-code/proyecto/evaluar.py. Cambios principales:
  - Modo A: sin herramientas ni MCP, en una carpeta temporal vacía.
  - Modo B: MCP bcrp + skills + herramientas para correrlas, en una COPIA temporal del proyecto sin evaluacion/,
    salidas/ ni referencias/ (no puede leer las respuestas esperadas ni resultados previos).
  - Se lee el registro stream-json de cada sesión para saber qué herramientas usó de verdad.
  - Combinadas: dos cifras + coherencia interpretativa (regla automática; revisión manual aparte).
Las reglas de calificación y las tolerancias están fijadas en README_evaluacion.md.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
RAIZ = AQUI.parent
CLAUDE = shutil.which("claude") or "claude"

ESQUEMA = {"type": "object", "required": ["valor", "fuente"],
           "properties": {"valor": {"type": ["number", "null"]}, "valor_2": {"type": ["number", "null"]},
                          "unidad": {"type": "string"}, "fuente": {"type": "string"},
                          "interpretacion": {"type": "string"}}}
INSTRUCCION = ("Responde la pregunta con datos. Pon el número en «valor» (y, si la pregunta pide dos cifras, la "
               "segunda en «valor_2») en la unidad que pide la pregunta, sin símbolos. Si no puedes saberlo con "
               "certeza, pon null: no estimes. En «fuente» di de dónde sale cada cifra (código de serie, periodo, "
               "archivo o URL). Si la pregunta pide una interpretación, escríbela en «interpretacion»; si no, déjala "
               "vacía.\n\nPregunta: ")

HERRAMIENTAS_B = "Skill,Bash,Read,Write,Edit,Glob,Grep"
MODOS = {
    "A": ["--tools", "", "--strict-mcp-config"],
    "B": ["--tools", HERRAMIENTAS_B, "--allowedTools", HERRAMIENTAS_B + ",mcp__bcrp",
          "--mcp-config", ".mcp.json", "--strict-mcp-config"],
}
# Lo que se copia al modo B (todo lo demás queda fuera: evaluacion/, salidas/, referencias/, figuras/, CLAUDE.md...)
COPIAR_DIRS = ["datos", "mcp", ".claude"]
COPIAR_ARCHIVOS = [".mcp.json", "pyproject.toml", "uv.lock"]
IGNORAR = shutil.ignore_patterns("__pycache__", "cache_api", ".pytest_cache")
RUTAS_PROHIBIDAS = re.compile(r"Python_Intermedio_2026|Data-Science-Python|[\\/]evaluacion[\\/]|[\\/]referencias[\\/]",
                              re.IGNORECASE)

# Coherencia interpretativa (README_evaluacion.md)
CAUSAL = re.compile(r"\b(caus\w*|provoc\w*|explic\w*|gener[aóoe]\w*|deb(e|ido)\s+a|impuls\w*|determin\w*|"
                    r"contribuy\w*|efecto\w*|impacto\w*)\b", re.IGNORECASE)
NEGACION = re.compile(r"\b(no|ni|sin|nunca|tampoco)\b", re.IGNORECASE)
AGREGACION = re.compile(
    r"agregaci|distint[oa]s?\s+(nivel|fuente|escala|cobertura|[áa]mbito|unidad)|diferentes?\s+(nivel|fuente|escala|"
    r"cobertura|[áa]mbito|unidad)|macro|microdato|encuesta\s+de\s+hogares|departamental.*nacional|"
    r"nacional.*departamental|lima\s+metropolitana.*(urban|nacional)|(urban|nacional).*lima\s+metropolitana|"
    r"cajamarca.*(nacional|pa[íi]s)|(nacional|pa[íi]s).*cajamarca|falacia\s+ecol", re.IGNORECASE | re.DOTALL)


def afirma_causalidad(texto):
    for m in CAUSAL.finditer(texto):
        if not NEGACION.search(texto[max(0, m.start() - 40):m.start()]):
            return True
    return False


def preparar_carpeta(modo, id_):
    carpeta = Path(tempfile.mkdtemp(prefix=f"eval_{modo}_{id_}_"))
    if modo == "B":
        for d in COPIAR_DIRS:
            shutil.copytree(RAIZ / d, carpeta / d, ignore=IGNORAR)
        for a in COPIAR_ARCHIVOS:
            shutil.copy2(RAIZ / a, carpeta / a)
    return carpeta


def resumir_herramientas(eventos):
    """Lista de herramientas usadas, desde los bloques tool_use del registro stream-json."""
    usos, fuera, bcrp_fallo = [], [], False
    for e in eventos:
        if e.get("type") == "assistant":
            for b in e["message"].get("content", []):
                if b.get("type") != "tool_use" or b["name"] == "StructuredOutput":
                    continue
                n, inp = b["name"], b.get("input", {})
                if n.startswith("mcp__bcrp__"):
                    usos.append(f"mcp:{n.removeprefix('mcp__bcrp__')}")
                elif n == "Skill":
                    usos.append(f"skill:{inp.get('skill', inp.get('name', '?'))}")
                else:
                    usos.append(n)
                texto = json.dumps(inp, ensure_ascii=False)
                if RUTAS_PROHIBIDAS.search(texto):
                    fuera.append(f"{n}: {texto[:200]}")
        if e.get("type") == "user":
            for b in e["message"].get("content", []) if isinstance(e["message"].get("content"), list) else []:
                if b.get("type") != "tool_result":
                    continue
                texto = json.dumps(b, ensure_ascii=False)
                bcrp_fallo |= "BCRP no respondió" in texto
                if "Python_Intermedio_2026" in texto and "ruta del repo visible en una salida" not in fuera:
                    fuera.append("ruta del repo visible en una salida")
    return usos, fuera, bcrp_fallo


def compactar(eventos):
    """Registro corto para guardar: llamadas a herramientas, resultados recortados y el resultado final."""
    out = []
    for e in eventos:
        t = e.get("type")
        if t == "system" and e.get("subtype") == "init":
            out.append({"inicio": {"model": e.get("model"), "tools": e.get("tools"),
                                   "mcp_servers": e.get("mcp_servers"),
                                   "skills_enaho": [s for s in e.get("skills", []) if s.endswith("-enaho")]}})
        elif t == "assistant":
            for b in e["message"].get("content", []):
                if b.get("type") == "tool_use":
                    out.append({"tool_use": b["name"], "input": b.get("input")})
                elif b.get("type") == "text" and b.get("text"):
                    out.append({"texto": b["text"][:1500]})
        elif t == "user" and isinstance(e["message"].get("content"), list):
            for b in e["message"]["content"]:
                if b.get("type") == "tool_result":
                    c = b.get("content")
                    c = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
                    out.append({"tool_result": c[:1500]})
        elif t == "result":
            out.append({"result": {k: e.get(k) for k in ("subtype", "is_error", "num_turns", "duration_ms",
                                                          "structured_output", "result")}})
        elif t == "rate_limit_event":
            out.append({"rate_limit": e.get("rate_limit_info", {}).get("unifiedWindows")})
    return out


def entorno_python():
    """Entorno de Python para el modo B FUERA del repo (en la carpeta temporal del sistema).

    Si se usara el .venv del proyecto, cualquier error de Python le mostraría al agente la ruta real del repo
    (y con ella dónde están evaluacion/ y salidas/). Se sincroniza una vez con uv.lock (--frozen).
    """
    venv = Path(tempfile.gettempdir()) / "tarea4_eval_venv"
    env = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(venv)}
    subprocess.run(["uv", "sync", "--frozen", "--quiet"], cwd=RAIZ, env=env, check=True)
    return venv


def env_limpio(venv):
    """Variables de entorno para claude -p sin rastros del repo: sin su .venv en el PATH ni VIRTUAL_ENV."""
    env = {k: v for k, v in os.environ.items() if k not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")}
    raiz = str(RAIZ).lower()
    env["PATH"] = os.pathsep.join(p for p in env.get("PATH", "").split(os.pathsep) if not p.lower().startswith(raiz))
    if venv:
        env["UV_PROJECT_ENVIRONMENT"] = str(venv)
    return env


def preguntar(q, modo, modelo, registros, venv):
    intentos, ultimo = 0, None
    while intentos < 2:
        intentos += 1
        carpeta = preparar_carpeta(modo, q.id)
        env = env_limpio(venv if modo == "B" else None)
        cmd = [CLAUDE, "-p", "--output-format", "stream-json", "--verbose", "--json-schema", json.dumps(ESQUEMA),
               "--no-session-persistence", "--model", modelo, *MODOS[modo]]
        t = time.time()
        try:
            proc = subprocess.run(cmd, input=INSTRUCCION + q.pregunta, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=1500, cwd=carpeta, env=env)
            salida, err = proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as e:
            salida, err = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), "timeout"
        segundos = round(time.time() - t, 1)
        shutil.rmtree(carpeta, ignore_errors=True)

        eventos = []
        for linea in salida.splitlines():
            try:
                eventos.append(json.loads(linea))
            except json.JSONDecodeError:
                pass
        res = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
        so = res.get("structured_output") or {}
        usos, fuera, bcrp_fallo = resumir_herramientas(eventos)
        limite = next((e["rate_limit_info"].get("unifiedWindows", {}).get("five_hour", {}).get("utilization")
                       for e in reversed(eventos) if e.get("type") == "rate_limit_event"), None)
        error = ""
        if not res:
            error = f"sin resultado: {(err or salida)[-300:]}"
        elif res.get("is_error") or not so:
            error = f"{res.get('subtype')}: {str(res.get('result'))[:300]}"
        ultimo = {"valor": so.get("valor"), "valor_2": so.get("valor_2"), "fuente_declarada": so.get("fuente", ""),
                  "interpretacion": so.get("interpretacion", ""), "herramientas": "; ".join(usos),
                  "uso_mcp": any(u.startswith("mcp:") for u in usos),
                  "skills_usadas": "; ".join(dict.fromkeys(u[6:] for u in usos if u.startswith("skill:"))),
                  "acceso_fuera_copia": " | ".join(fuera), "segundos": segundos, "turnos": res.get("num_turns"),
                  "intentos": intentos, "error": error, "uso_limite_5h": limite}
        (registros / f"{modo}_{q.id}.json").write_text(
            json.dumps({"id": q.id, "modo": modo, "modelo": modelo, "intento": intentos, "segundos": segundos,
                        "eventos": compactar(eventos)}, ensure_ascii=False, indent=1), encoding="utf-8")
        reintentar = bool(error) or (modo == "B" and bcrp_fallo and so.get("valor") is None)
        if not reintentar:
            break
        print(f"  {modo} {q.id}: reintento ({error or 'el BCRP limitó los pedidos'})", flush=True)
        time.sleep(30)
    print(f"  {modo} {q.id}: valor={ultimo['valor']} valor_2={ultimo['valor_2']} ({ultimo['segundos']} s) "
          f"[{ultimo['herramientas'][:80]}]", flush=True)
    return ultimo


def dentro(valor, verdad, tol):
    return valor is not None and abs(float(valor) - float(verdad)) <= float(tol) + 1e-9


def calificar(q, r):
    f = {"ok_valor": dentro(r["valor"], q.verdad, q.tolerancia), "ok_valor_2": None, "no_afirma_causalidad": None,
         "reconoce_agregacion": None, "coherente_auto": None}
    if r["error"] and r["valor"] is None:
        return {**f, "resultado": "error"}
    if q.tipo != "combinada":
        return {**f, "resultado": "sin respuesta" if r["valor"] is None else
                ("correcta" if f["ok_valor"] else "incorrecta")}
    texto = r["interpretacion"] or ""
    f["ok_valor_2"] = dentro(r["valor_2"], q.verdad_2, q.tolerancia_2)
    f["no_afirma_causalidad"] = not afirma_causalidad(texto)
    f["reconoce_agregacion"] = bool(AGREGACION.search(texto))
    f["coherente_auto"] = f["no_afirma_causalidad"] and f["reconoce_agregacion"]
    if r["valor"] is None and r["valor_2"] is None:
        return {**f, "resultado": "sin respuesta"}
    return {**f, "resultado": "correcta" if f["ok_valor"] and f["ok_valor_2"] and f["coherente_auto"] else "incorrecta"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--modos", nargs="+", default=["A", "B"], choices=list(MODOS))
    p.add_argument("--modelo", default="sonnet")
    p.add_argument("--ids", nargs="+", help="solo estas preguntas (p. ej. B1 E3)")
    p.add_argument("--paralelo", type=int, default=2)
    p.add_argument("--salida", default=str(AQUI / "resultados.csv"))
    p.add_argument("--registros", default=str(AQUI / "registros"))
    a = p.parse_args()

    preguntas = pd.read_csv(AQUI / "preguntas.csv", dtype={"id": str})
    if a.ids:
        preguntas = preguntas[preguntas.id.isin(a.ids)]
    registros = Path(a.registros)
    registros.mkdir(parents=True, exist_ok=True)
    venv = entorno_python() if "B" in a.modos else None
    casos = [(q, m) for q in preguntas.itertuples() for m in a.modos]
    print(f"{len(casos)} llamadas a claude -p con {a.modelo}, {a.paralelo} en paralelo...", flush=True)
    with ThreadPoolExecutor(a.paralelo) as ex:
        respuestas = list(ex.map(lambda c: preguntar(c[0], c[1], a.modelo, registros, venv), casos))

    filas = []
    for (q, m), r in zip(casos, respuestas):
        filas.append({"id": q.id, "tipo": q.tipo, "modo": m, "modelo": a.modelo, "pregunta": q.pregunta,
                      "verdad": q.verdad, "tolerancia": q.tolerancia,
                      "verdad_2": q.verdad_2 if q.tipo == "combinada" else None,
                      "tolerancia_2": q.tolerancia_2 if q.tipo == "combinada" else None,
                      **{k: r[k] for k in ("valor", "valor_2")}, **calificar(q, r),
                      **{k: v for k, v in r.items() if k not in ("valor", "valor_2")},
                      "revision_manual_coherencia": ""})
    res = pd.DataFrame(filas).sort_values(["id", "modo"])
    res.to_csv(a.salida, index=False, encoding="utf-8")
    print("\n" + res[["id", "modo", "verdad", "valor", "verdad_2", "valor_2", "resultado", "segundos"]].to_string(index=False))
    tabla = res.groupby("modo").resultado.value_counts().unstack(fill_value=0)
    tabla["segundos_prom"] = res.groupby("modo").segundos.mean().round(1)
    print("\n" + tabla.to_string())
    print(f"\nEscrito {a.salida}")


if __name__ == "__main__":
    main()
