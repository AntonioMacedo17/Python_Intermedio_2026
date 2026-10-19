"""Dashboard de la Tarea 1: clasificador de titulares peruanos (La República).

Ejecutar en local:  streamlit run app.py
"""
import json
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).parent
CATEGORIAS = ["politica", "economia", "deportes", "ciencia_tecnologia"]
NOMBRES = {"politica": "Política", "economia": "Economía", "deportes": "Deportes",
           "ciencia_tecnologia": "Ciencia y tecnología"}
COLORES = {"politica": "#2E5EAA", "economia": "#E0A100", "deportes": "#2A9D5B", "ciencia_tecnologia": "#8E44AD"}

st.set_page_config(page_title="Clasificador de titulares peruanos", page_icon="🗞️", layout="wide")


# ---------- Carga de datos, métricas y modelo ----------
@st.cache_data
def cargar_noticias():
    return pd.read_csv(BASE / "datos" / "noticias.csv")


@st.cache_data
def cargar_metricas():
    ruta = BASE / "modelo" / "metricas.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


def origen_modelo():
    """Modelo local en modelo/ o, si no existe (p. ej. en Streamlit Cloud), un repositorio de Hugging Face."""
    local = BASE / "modelo"
    if (local / "config.json").exists() and any(local.glob("*.safetensors")):
        return str(local)
    try:
        return st.secrets.get("HF_MODEL_ID") or os.environ.get("HF_MODEL_ID")
    except Exception:
        return os.environ.get("HF_MODEL_ID")


@st.cache_resource(show_spinner="Cargando el modelo DistilBERT…")
def cargar_clasificador(origen):
    from transformers import pipeline
    return pipeline("text-classification", model=origen, tokenizer=origen, device=-1)


df = cargar_noticias()
metricas = cargar_metricas()

# ---------- Encabezado ----------
st.title("🗞️ ¿Pueden convertir titulares peruanos en un clasificador de noticias?")
st.markdown(
    f"Clasificador de titulares de **La República** en 4 categorías: "
    f"{', '.join(NOMBRES[c] for c in CATEGORIAS)}."
)
with st.expander("Resumen metodológico", expanded=False):
    st.markdown(
        f"""
1. **Recolección:** {len(df)} noticias de larepublica.pe obtenidas de sus RSS oficiales, sitemaps de noticias y
   páginas de noticia, respetando `robots.txt` (pausa de 1.5 s, 1 reintento máximo).
2. **Normalización:** la sección del diario se mapea a 4 categorías; las demás secciones se descartan.
3. **Supervisión débil:** un LLM (`{metricas.get('modelo_llm', 'LLM')}`) etiqueta todo el dataset y una auditoría humana
   de 20 casos mide su calidad.
4. **Modelo:** `{metricas.get('modelo_base', 'distilbert-base-multilingual-cased')}` afinado 3 épocas con las etiquetas
   del LLM; partición estratificada 70/15/15 (`random_state=42`).
5. **Evaluación:** F1 macro sobre el conjunto de **test** reservado, comparado con una línea base zero-shot.
"""
    )

# ---------- Filtros ----------
st.sidebar.header("Filtros")
medios = sorted(df["medio"].dropna().unique())
sel_medios = st.sidebar.multiselect("Medio", medios, default=medios)
sel_cats = st.sidebar.multiselect("Categoría", CATEGORIAS, default=CATEGORIAS, format_func=NOMBRES.get)
filtrado = df[df["medio"].isin(sel_medios) & df["etiqueta"].isin(sel_cats)]
st.sidebar.caption(f"{len(filtrado)} de {len(df)} noticias seleccionadas")

# ---------- Indicadores ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Noticias recolectadas", f"{len(df)}", delta=f"{len(filtrado)} con los filtros", delta_color="off")
f1 = metricas.get("f1_macro_test")
f1_zs = metricas.get("f1_macro_zero_shot")
c2.metric("F1 macro en test", f"{f1:.2f}" if f1 is not None else "—",
          delta=f"{f1 - f1_zs:+.2f} vs. zero-shot" if f1 is not None and f1_zs is not None else None)
acuerdo = metricas.get("acuerdo_llm_humano")
n_aud = metricas.get("auditoria_n", 20)
c3.metric("Concordancia LLM vs. auditoría humana", f"{acuerdo / n_aud:.0%}" if acuerdo is not None else "—",
          delta=f"{acuerdo}/{n_aud} casos" if acuerdo is not None else None, delta_color="off")
c4.metric("F1 macro zero-shot (piso)", f"{f1_zs:.2f}" if f1_zs is not None else "—")
if not metricas:
    st.info("Aún no existe `modelo/metricas.json`. Ejecuta el notebook 02_clasificacion.ipynb para generarlo.")

# ---------- Gráfico y tabla ----------
col_graf, col_tabla = st.columns([2, 3])
with col_graf:
    conteo = filtrado["etiqueta"].value_counts().reindex(sel_cats, fill_value=0).reset_index()
    conteo.columns = ["etiqueta", "noticias"]
    conteo["categoria"] = conteo["etiqueta"].map(NOMBRES)
    fig = px.bar(conteo, x="categoria", y="noticias", color="etiqueta", text="noticias",
                 color_discrete_map=COLORES, title="Noticias por categoría (según filtros)",
                 labels={"categoria": "Categoría", "noticias": "Noticias"})
    fig.update_layout(showlegend=False, margin=dict(t=50, b=10))
    st.plotly_chart(fig, width="stretch")
with col_tabla:
    st.dataframe(
        filtrado[["fecha", "etiqueta", "titular", "bajada", "seccion_original", "url"]],
        width="stretch", hide_index=True, height=380,
        column_config={"url": st.column_config.LinkColumn("url", display_text="abrir"),
                       "titular": st.column_config.TextColumn("titular", width="large")},
    )
    st.download_button("⬇️ Descargar CSV filtrado", filtrado.to_csv(index=False).encode("utf-8"),
                       file_name="noticias_filtradas.csv", mime="text/csv")

# ---------- Probador en vivo ----------
st.divider()
st.subheader("🔎 Probador en vivo")
titular = st.text_area("Escribe o pega un titular nuevo",
                       placeholder="Ej.: Congreso aprueba nuevo retiro de fondos de AFP", height=80)
if st.button("Clasificar titular", type="primary"):
    origen = origen_modelo()
    if not titular.strip():
        st.warning("Escribe un titular primero.")
    elif not origen:
        st.error("No se encontró el modelo. Ejecuta el notebook 02 para crear `modelo/` "
                 "o define `HF_MODEL_ID` en los secrets de Streamlit.")
    else:
        clasificador = cargar_clasificador(origen)
        salida = clasificador(titular.strip(), top_k=None, truncation=True)
        if salida and isinstance(salida[0], list):
            salida = salida[0]
        probs = pd.DataFrame(salida).sort_values("score", ascending=False)
        mejor = probs.iloc[0]
        r1, r2 = st.columns([1, 2])
        r1.metric("Categoría predicha", NOMBRES.get(mejor["label"], mejor["label"]))
        r1.metric("Probabilidad", f"{mejor['score']:.1%}")
        probs["categoria"] = probs["label"].map(NOMBRES)
        fig_p = px.bar(probs, x="score", y="categoria", orientation="h", color="label",
                       color_discrete_map=COLORES, range_x=[0, 1], text=probs["score"].map("{:.1%}".format),
                       labels={"score": "Probabilidad", "categoria": ""})
        fig_p.update_layout(showlegend=False, height=240, margin=dict(t=10, b=10),
                            yaxis={"categoryorder": "total ascending"})
        r2.plotly_chart(fig_p, width="stretch")

st.caption("Tarea 1 · Diplomado QLAB · Datos: larepublica.pe · Modelo: DistilBERT multilingüe afinado con supervisión débil")
