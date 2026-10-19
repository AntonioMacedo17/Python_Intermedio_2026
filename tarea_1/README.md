# Tarea 1 – Noticias peruanas: del titular al clasificador

**Diplomado QLAB · Trabajo individual · Opción A: La República**
Estudiante: Antonio Macedo

## 1. Pregunta del proyecto

**¿Pueden convertir titulares peruanos en un clasificador de noticias?**

Se recolectaron titulares reales de La República, se etiquetaron con un LLM (supervisión débil), se afinó un modelo
DistilBERT multilingüe y se publicó un dashboard en Streamlit donde cualquiera puede escribir un titular y ver la
categoría predicha (`politica`, `economia`, `deportes`, `ciencia_tecnologia`) con su probabilidad.

| Etapa | Archivo |
|---|---|
| Recolección, limpieza y EDA | `01_recoleccion.ipynb` → `datos/noticias.csv` |
| Zero-shot, LLM, fine-tuning y evaluación | `02_clasificacion.ipynb` → `datos/etiquetas_llm.csv`, `modelo/` |
| Dashboard | `app.py` |

## 2. Medio y fechas de extracción

- **Medio:** La República (https://larepublica.pe).
- **Fuentes:** RSS oficiales por sección (`/rss/politica.xml`, `/rss/economia.xml`, `/rss/deportes.xml`,
  `/rss/ciencia.xml`, `/rss/home.xml`), sitemaps de noticias declarados en `robots.txt` y páginas de noticia.
- **Fecha de descarga:** `AAAA-MM-DD` ✍️ *(cópiala de la salida `FECHA_DESCARGA` del notebook 01)*.
- **Rango de fechas de publicación:** `DD/MM/AAAA – DD/MM/AAAA` ✍️ *(sale en el título del gráfico 2 del notebook 01)*.
- **Volumen final:** `N` noticias ✍️ (máx. 100 por categoría).
- Se respetó `robots.txt` (sin paginación `/pag/`, sin `/tag/`), con User-Agent descriptivo, pausa de 1.5 s y
  máximo 1 reintento.

## 3. Resultados

| Modelo | F1 macro | Dónde |
|---|---|---|
| Zero-shot (`Recognai/bert-base-spanish-wwm-cased-xnli`) | `0.xx` ✍️ | 40 titulares del test |
| LLM débil (`gemini-2.5-flash`) | `0.xx` ✍️ | test completo |
| **DistilBERT fine-tuned** | **`0.xx`** ✍️ | test completo |

Acuerdo LLM–humano en la auditoría: `xx/20` ✍️.

## 4. Hallazgos analíticos

> ✍️ Reemplaza con lo que muestren TUS gráficos y la matriz de confusión. Ejemplos de cómo redactarlos:

1. **La confusión principal está entre política y economía.** *(Ej.: "De los N errores en test, M fueron entre
   `politica` y `economia`: titulares sobre presupuesto, AFP o impuestos tienen tema económico pero actores políticos.")*
2. **Deportes es la categoría más fácil de reconocer.** *(Ej.: "Deportes logró F1 de 0.9x gracias a un vocabulario
   exclusivo —clubes, Liga 1, Selección— mientras que los titulares de ciencia son X caracteres más largos en mediana.")*

## 5. Limitaciones técnicas

1. **Etiquetas ruidosas:** el modelo se entrena con etiquetas del LLM, no con etiquetas humanas; los errores del LLM
   se heredan. Además, la sección del diario (la referencia) no siempre coincide con el tema real del titular.
2. **Datos pequeños y de pocas semanas:** ~400 titulares de un solo medio y de un periodo corto; el modelo aprende la
   coyuntura (nombres propios del momento) y puede perder precisión con noticias de otros meses u otros diarios.
   El modelo pesa ~540 MB, por lo que no se sube a GitHub (para desplegarlo en la nube hay que publicarlo en
   Hugging Face Hub).

## 6. Cómo ejecutarlo en local (Windows / PowerShell)

```powershell
cd tarea_1
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

1. Abre la carpeta en VS Code y elige el kernel `.venv` en cada notebook.
2. Ejecuta `01_recoleccion.ipynb` completo (*Run All*).
3. Crea el archivo `.env` (copia `.env.example`) con tu `GEMINI_API_KEY` y ejecuta `02_clasificacion.ipynb`.
   Completa `datos/auditoria_llm.csv` cuando el notebook lo pida y vuelve a ejecutar desde esa celda.
4. Lanza el dashboard:

```powershell
streamlit run app.py
```

En macOS/Linux, activa el entorno con `source .venv/bin/activate`.

### Despliegue opcional en Streamlit Community Cloud

Como los pesos del modelo no están en GitHub, súbelos a Hugging Face Hub (gratis) tras `hf auth login`:

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
repo = "tu_usuario_hf/clasificador-titulares-lr"
AutoModelForSequenceClassification.from_pretrained("modelo").push_to_hub(repo)
AutoTokenizer.from_pretrained("modelo").push_to_hub(repo)
```

En share.streamlit.io, en *Secrets*, agrega `HF_MODEL_ID = "tu_usuario_hf/clasificador-titulares-lr"`.
