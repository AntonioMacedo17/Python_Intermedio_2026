"""Voces y documentos peruanos: del archivo escaneado al texto buscable (Tarea 2, QLAB).

    streamlit run app.py

La app solo LEE los CSV generados en los notebooks (no carga modelos de OCR, ASR ni LLM).
Todo el texto que muestra ya está seudonimizado. Imágenes y audios solo se muestran si están en
datos/ejemplos/ y en datos/ejemplos/ejemplos.csv (archivos con licencia que permite publicarlos y
sin datos personales).
"""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATOS = Path(__file__).parent / "datos"
CREMA, CARBON, VERDE_TITULO, VERDE, MORADO = "#F7F3EA", "#2B2B2B", "#1F5F4A", "#0F7A55", "#6A4C93"

st.set_page_config(page_title="Voces y documentos peruanos", page_icon="📜", layout="wide")
st.markdown(f"""
<style>
  .stApp {{ background: {CREMA}; color: {CARBON}; }}
  h1, h2, h3 {{ color: {VERDE_TITULO}; }}
  [data-testid="stMetricValue"] {{ color: {MORADO}; }}
  .marca-hablante {{ color: {MORADO}; font-weight: 600; }}
</style>""", unsafe_allow_html=True)


@st.cache_data
def leer(nombre):
    ruta = DATOS / nombre
    return pd.read_csv(ruta) if ruta.exists() else None


def grafico(fig, alto=380):
    fig.update_layout(height=alto, paper_bgcolor=CREMA, plot_bgcolor=CREMA, font_color=CARBON,
                      title_font_color=VERDE_TITULO, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig, width="stretch")


docs, trans = leer("documentos.csv"), leer("transcripciones.csv")
llm, metricas, ejemplos = leer("extraccion_llm.csv"), leer("metricas.csv"), leer("ejemplos/ejemplos.csv")
comparacion_asr, comparacion = leer("comparacion_asr.csv"), leer("comparacion_modelos.csv")
campos = {} if llm is None else {r.id: json.loads(r.campos_json) for r in llm.itertuples()}
publicables = set() if ejemplos is None else set(ejemplos["id"])

# ── encabezado ─────────────────────────────────────────────────────────────────────────
st.title("¿Se pueden volver buscables los documentos y las voces del Perú?")
st.markdown(
    "Documentos peruanos (impresos, fotos y manuscritos) leídos con **OCR** y entrevistas en español peruano "
    "transcritas con **ASR**, con nombres reemplazados por seudónimos, campos extraídos por un **LLM** y "
    "una evaluación contra transcripciones hechas a mano. Los modelos corrieron en los notebooks; "
    "aquí se exploran sus resultados.")
if docs is None or trans is None:
    st.warning("Todavía no hay datos exportados: ejecuta los notebooks 01 y 02.")
    st.stop()

# ── indicadores ─────────────────────────────────────────────────────────────────────────
c = st.columns(5)
c[0].metric("Documentos procesados", len(docs))
c[1].metric("Minutos de audio transcritos", f"{trans['duracion_seg'].sum() / 60:.1f}")
if metricas is not None:
    elegidos = metricas[metricas["elegido"]]
    for i, (_, m) in enumerate(elegidos.iterrows()):
        c[2 + i].metric(f"{m['metrica']} · {m['modelo']}", f"{m['valor']:.2f}",
                        help="Sobre la muestra de 10 casos con referencia manual (menor es mejor).")
if llm is not None and "acuerdo_auditoria" in llm:
    ok = llm["acuerdo_auditoria"].dropna()
    c[4].metric("Acuerdo LLM vs. auditoría humana", f"{ok.mean():.0%}", help=f"{int(ok.sum())}/{len(ok)} extracciones")

# ── filtros (actualizan tablas y gráficos) ──────────────────────────────────────────────
with st.sidebar:
    st.header("Filtros")
    buscar = st.text_input("Buscar palabra en los textos", "")
    tipos = st.multiselect("Tipo de documento", ["impreso", "foto", "manuscrito"], ["impreso", "foto", "manuscrito"])
    modelos_ocr = st.multiselect("Modelo OCR", sorted(docs["modelo_ocr"].unique()), sorted(docs["modelo_ocr"].unique()))
    dmin, dmax = float(trans["duracion_seg"].min()), float(trans["duracion_seg"].max())
    rango = st.slider("Duración del clip (s)", dmin, dmax, (dmin, dmax))

d = docs[docs["tipo"].isin(tipos) & docs["modelo_ocr"].isin(modelos_ocr)]
t = trans[trans["duracion_seg"].between(*rango)]
if buscar:
    d = d[d["texto_ocr"].fillna("").str.contains(buscar, case=False, regex=False)]
    t = t[t["texto_asr"].fillna("").str.contains(buscar, case=False, regex=False)]

tab_res, tab_doc, tab_aud, tab_eval = st.tabs(["Resumen", "Documentos", "Audios", "Evaluación de modelos"])

with tab_res:
    a, b = st.columns(2)
    with a:
        n = d["tipo"].value_counts().reindex(["impreso", "foto", "manuscrito"]).fillna(0).rename_axis("tipo").reset_index(name="n")
        grafico(px.bar(n, x="tipo", y="n", text="n", color_discrete_sequence=[VERDE],
                       title=f"{len(d)} documentos con los filtros actuales", labels={"n": "documentos", "tipo": ""}))
    with b:
        grafico(px.histogram(t, x="duracion_seg", nbins=20, color_discrete_sequence=[MORADO],
                             title=f"{len(t)} clips: {(t['duracion_seg'] < 60).mean():.0%} dura menos de un minuto",
                             labels={"duracion_seg": "duración (s)", "count": "clips"}))
    st.subheader("Tabla filtrada")
    tabla = pd.concat([d.assign(modalidad="documento").rename(columns={"texto_ocr": "texto"})[["id", "modalidad", "tipo", "texto"]],
                       t.assign(modalidad="audio", tipo="clip").rename(columns={"texto_asr": "texto"})[["id", "modalidad", "tipo", "texto"]]])
    st.dataframe(tabla, width="stretch", hide_index=True)
    st.download_button("Descargar CSV (textos seudonimizados)", tabla.to_csv(index=False).encode("utf-8"),
                       "textos_filtrados.csv", "text/csv")

with tab_doc:
    if d.empty:
        st.info("Ningún documento coincide con los filtros.")
    else:
        sel = st.selectbox("Documento", d["id"], format_func=lambda i: f"{i} · {d.set_index('id').loc[i, 'tipo']}")
        fila = d.set_index("id").loc[sel]
        izq, der = st.columns([3, 2])
        with izq:
            st.markdown(f"**Fuente:** {fila['fuente']} · **Modelo:** {fila['modelo_ocr']}")
            st.text_area("Texto OCR (seudonimizado)", fila["texto_ocr"], height=280)
            if isinstance(fila.get("texto_referencia"), str) and fila["texto_referencia"].strip():
                st.text_area("Transcripción manual de referencia", fila["texto_referencia"], height=160)
                if metricas is not None and "cer_por_caso" in metricas:
                    pass  # se completa con la Parte 2
        with der:
            st.markdown("**Campos extraídos por el LLM**")
            st.json(campos.get(sel, {"aviso": "sin extracción"}))
            img = DATOS / "ejemplos" / f"{sel}.jpg"
            if sel in publicables and img.exists():
                st.image(str(img), caption="Imagen con licencia que permite publicarla")
            else:
                st.caption("La imagen no se publica (licencia o datos personales); se muestran texto y metadatos.")

with tab_aud:
    if t.empty:
        st.info("Ningún clip coincide con los filtros.")
    else:
        sel = st.selectbox("Clip", t["id"], format_func=lambda i: f"{i} · {t.set_index('id').loc[i, 'duracion_seg']:.0f} s")
        fila = t.set_index("id").loc[sel]
        st.markdown(f"**Modelo:** {fila['modelo_asr']} · **Hablantes detectados:** {fila['n_hablantes']}")
        texto = str(fila["texto_asr"]).replace("[HABLANTE_", "\n\n<span class='marca-hablante'>[HABLANTE_")
        st.markdown(texto.replace("] ", "]</span> "), unsafe_allow_html=True)
        audio = DATOS / "ejemplos" / f"{sel}.wav"
        if sel in publicables and audio.exists():
            st.audio(str(audio))
        else:
            st.caption("El audio de este clip no se publica; se muestra la transcripción.")
        if comparacion_asr is not None and sel in set(comparacion_asr["id"]):
            st.markdown("**Comparación de modelos en este clip**")
            st.dataframe(comparacion_asr[comparacion_asr["id"] == sel], hide_index=True, width="stretch")

with tab_eval:
    if metricas is None:
        st.info("Todavía no hay referencias manuales: las métricas de error se calculan en el notebook 02 "
                "cuando estén. Abajo, lo que no necesita referencias.")
    else:
        tot = metricas[metricas["grupo"] == "TODOS"]
        for modalidad, g in tot.groupby("modalidad"):
            grafico(px.bar(g, x="metrica", y="valor", color="modelo", barmode="group",
                           color_discrete_sequence=[VERDE, MORADO], text_auto=".2f",
                           title=f"{'ASR' if modalidad == 'audio' else 'OCR'}: error por modelo frente a la transcripción manual (menor es mejor)",
                           labels={"valor": "tasa de error", "metrica": "", "modelo": ""}))
        st.markdown("**Por tipo de clip o documento**")
        st.dataframe(metricas.drop(columns=["elegido"]).round(3), hide_index=True, width="stretch")
    if comparacion is not None:
        st.subheader("Comparación de modelos")
        st.caption("Latencia en una laptop sin GPU. Los modelos locales no envían nada fuera; a Gemini solo se "
                   "envió texto seudonimizado.")
        st.dataframe(comparacion.round(3), hide_index=True, width="stretch")
    st.subheader("Qué falta (y por qué)")
    st.markdown(
        "- **OCR sin CER/WER todavía:** la muestra de 10 documentos se sortea cuando estén las fotos y manuscritos "
        "propios (regla fijada antes de ver resultados).\n"
        "- **LLM parcial:** el nivel gratuito de Gemini (20 pedidos/día) dejó 32 de 54 extracciones.\n"
        "- **Parakeet parcial:** se cortó por tiempo; se compara solo en los clips que procesó.")

st.caption("Fuentes: Wikimedia Commons, OpenSLR 73 y capturas propias; licencias en datos/fuentes.csv. "
           "Nombres reales reemplazados por [PERSONA_###].")
