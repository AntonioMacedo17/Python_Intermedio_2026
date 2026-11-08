# Tarea 4 · Agente de investigación socioeconómica (MCP del BCRP + Skills de ENAHO 2024)

> En construcción. Este README se completa al cierre de la tarea con arquitectura, instalación,
> reproducción, evaluación, limitaciones y evidencias del uso de IA.

## Estructura

| Carpeta / archivo | Qué contiene |
|---|---|
| `mcp/` | Servidor MCP del BCRP (`server.py`) y sus pruebas (`test_server.py`) |
| `.claude/skills/` | Skills `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho` |
| `datos/` | Microdatos ENAHO 2024 (ignorados por Git; ver abajo cómo bajarlos) |
| `salidas/`, `figuras/`, `mapas/` | Resultados generados por código |
| `evaluacion/` | Experimento con y sin MCP/Skills |
| `informes/` | Informe final |
| `evidencias_ia/` | Conversaciones con asistentes de IA (mcp, skills, integracion, evaluacion) |

## Instalación rápida

```bash
# 1. Instalar uv: https://docs.astral.sh/uv/getting-started/installation/
cd tarea_4
uv sync                      # crea .venv con las dependencias de pyproject.toml
```

## Datos

Bajar desde el portal del INEI y dejar los zip, sin descomprimir, en `tarea_4/datos/`:

- ENAHO 2024, módulo 34 (sumaria): https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip
- ENAHO 2024, módulo 02 (miembros): https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip
