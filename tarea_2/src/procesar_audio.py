"""Pipeline de audio de la tarea 2: limpieza -> VAD + transcripción -> diarización -> CSV/SRT/TXT.

    .venv/Scripts/python.exe src/procesar_audio.py

Entrada: datos/raw/audio/descargas.csv (de descargar_audio.py).
Salidas (todas en datos/raw/audio/, fuera de Git porque aún NO están seudonimizadas):
- clips/<id>.wav           audio mono 16 kHz de cada clip
- salidas/<id>.srt|.txt|.csv  transcripción por segmentos, con hablante
- limpieza.csv             qué se descartó y por qué
- asr_crudo.csv            una fila por clip, insumo del notebook 01

Configuración (fijada ANTES de ver métricas; es también la línea base de la Parte 2):
faster-whisper small, CPU int8, idioma 'es', beam_size=5, VAD Silero con silencios de 0,3 s.
"""
import hashlib
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import voz  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
AUDIO = RAIZ / "datos" / "raw" / "audio"
MODELO = "faster-whisper-small"
CONFIG_ASR = "faster-whisper small (CPU int8, lang=es, beam=5, VAD Silero 0.3 s)"
MIN_PROPORCION_VOZ = 0.10      # menos de 10 % del audio con voz -> "audio sin voz"
UMBRAL_DUPLICADO = 0.95         # correlación de envolventes para considerar dos audios iguales
TOLERANCIA_DURACION = 1.0       # segundos

# Frases que Whisper suele "inventar" en silencios o música (vistas en la clase y en la literatura
# de Whisper); se marcan para revisión manual, no se borran.
FRASES_SOSPECHOSAS = ["amara.org", "subtítulos realizados", "gracias por ver", "suscríbete",
                      "no olvides suscribirte", "gracias por su atención"]


def envolvente(x, sr=voz.SR, hz=50):
    """Energía del audio 50 veces por segundo: un 'resumen' que no cambia con el formato del archivo."""
    paso = sr // hz
    n = len(x) // paso
    e = np.sqrt((x[:n * paso].reshape(n, paso) ** 2).mean(axis=1))
    return (e - e.mean()) / (e.std() + 1e-9)


def parecido(a, b, max_desfase=100):
    """Máxima correlación entre dos envolventes, permitiendo un desfase de hasta 2 s."""
    mejor = 0.0
    for d in range(-max_desfase, max_desfase + 1, 2):
        x, y = (a[d:], b) if d >= 0 else (a, b[-d:])
        n = min(len(x), len(y))
        if n > 200:
            mejor = max(mejor, float(np.corrcoef(x[:n], y[:n])[0, 1]))
    return mejor


def sospechas(segmentos):
    """Marca segmentos con frases típicas de alucinación o con una palabra repetida 4+ veces seguidas."""
    marcas = []
    for s in segmentos:
        t = s.texto.lower()
        if any(f in t for f in FRASES_SOSPECHOSAS) or re.search(r"\b(\w+)(?:\W+\1\b){3,}", t):
            marcas.append(f"{s.inicio:.1f}-{s.fin:.1f}s: {s.texto[:80]}")
    return marcas


def fila_de(f, segs, seg_asr, seg_diar):
    """Una fila de asr_crudo.csv a partir de los segmentos de un clip."""
    n_hab = len({s.hablante for s in segs})
    plano = " ".join(s.texto for s in segs)
    # marcas de hablante solo si hay más de uno, como pide el enunciado
    texto_asr = " ".join(f"[HABLANTE_{s.hablante[1:]}] {s.texto}" for s in segs) if n_hab >= 2 else plano
    return {"id": f.id, "texto_asr": texto_asr, "texto_plano": plano, "modelo_asr": CONFIG_ASR,
            "n_hablantes": n_hab, "n_segmentos": len(segs),
            "segundos_asr": round(seg_asr, 1) if seg_asr is not None else None,
            "segundos_diarizacion": round(seg_diar, 1) if seg_diar is not None else None,
            "rtf": round(seg_asr / f.duracion_seg, 3) if seg_asr is not None else None,
            "sospechas_alucinacion": " | ".join(sospechas(segs))}


def main():
    tabla = pd.read_csv(AUDIO / "descargas.csv")
    (AUDIO / "clips").mkdir(exist_ok=True)
    (AUDIO / "salidas").mkdir(exist_ok=True)

    # ── 1. ids estables y audio a 16 kHz ─────────────────────────────────────────────
    es = tabla[tabla["idioma"] == "es"].reset_index(drop=True)
    es["id"] = [f"clip_{i:03d}" for i in range(1, len(es) + 1)]
    qu = tabla[tabla["idioma"] != "es"].reset_index(drop=True)
    qu["id"] = [f"qwh_{i:03d}" for i in range(1, len(qu) + 1)]
    tabla = pd.concat([es, qu], ignore_index=True)

    audios, filas_limpieza = {}, []
    for f in tabla.itertuples():
        x = voz.cargar_audio(RAIZ / f.archivo_original)
        audios[f.id] = x
        destino = AUDIO / "clips" / f"{f.id}.wav"
        if not destino.exists():
            import soundfile as sf
            sf.write(destino, x, voz.SR)
    tabla["archivo_audio"] = [f"datos/raw/audio/clips/{i}.wav" for i in tabla["id"]]
    tabla["duracion_seg"] = [round(len(audios[i]) / voz.SR, 1) for i in tabla["id"]]

    # ── 2. limpieza ───────────────────────────────────────────────────────────────────
    tabla["descartado"], tabla["motivo_descarte"] = False, ""
    # 2a. duplicados exactos: mismo hash del archivo original
    hashes = {}
    for f in tabla.itertuples():
        h = hashlib.sha256((RAIZ / f.archivo_original).read_bytes()).hexdigest()
        if h in hashes:
            tabla.loc[f.Index, ["descartado", "motivo_descarte"]] = True, f"duplicado exacto (hash) de {hashes[h]}"
        hashes.setdefault(h, f.id)
    # 2b. misma grabación en otro formato: el hash NO la detecta (bytes distintos)
    env = {i: envolvente(audios[i]) for i in tabla["id"]}
    for j, b in tabla.iterrows():
        if b["descartado"]:
            continue
        for _, a in tabla.loc[:j - 1].iterrows():
            if a["descartado"] or abs(a["duracion_seg"] - b["duracion_seg"]) > TOLERANCIA_DURACION:
                continue
            r = parecido(env[a["id"]], env[b["id"]])
            filas_limpieza.append({"id_a": a["id"], "id_b": b["id"], "correlacion_envolvente": round(r, 3)})
            if r >= UMBRAL_DUPLICADO:
                tabla.loc[j, ["descartado", "motivo_descarte"]] = True, (
                    f"misma grabación que {a['id']} en otro formato (correlación {r:.2f})")
                break
    # 2c. audios sin voz
    tabla["proporcion_voz"] = 0.0
    for f in tabla.itertuples():
        tramos = voz.tramos_de_voz(audios[f.id])
        prop = sum(b - a for a, b in tramos) / max(f.duracion_seg, 1e-9)
        tabla.loc[f.Index, "proporcion_voz"] = round(prop, 3)
        if prop < MIN_PROPORCION_VOZ and not tabla.loc[f.Index, "descartado"]:
            tabla.loc[f.Index, ["descartado", "motivo_descarte"]] = True, f"sin voz ({prop:.0%} con voz)"
    pd.DataFrame(filas_limpieza).to_csv(AUDIO / "comparaciones_duplicados.csv", index=False)
    tabla[["id", "titulo_original", "descartado", "motivo_descarte", "proporcion_voz", "duracion_seg"]].to_csv(
        AUDIO / "limpieza.csv", index=False)
    print(tabla.loc[tabla["descartado"], ["id", "motivo_descarte"]].to_string(index=False) or "sin descartes")

    # ── 3-4. transcripción + diarización (solo español y no descartados) ─────────────────
    t = None  # el modelo se carga solo si falta algún clip
    filas = []
    for f in tabla[(tabla["idioma"] == "es") & ~tabla["descartado"]].itertuples():
        x = audios[f.id]
        hechos = [AUDIO / "salidas" / f"{f.id}.{ext}" for ext in ("csv", "srt", "txt")]
        if all(p.exists() for p in hechos):
            # Reanudar: este clip ya se procesó en una corrida anterior (el .txt se escribe al final).
            # Sus tiempos no se guardaron, así que quedan vacíos; el RTF oficial se mide en la Parte 2.
            prev = pd.read_csv(hechos[0]).fillna({"texto": "", "hablante": "H1"})
            segs = [voz.Segmento(r.inicio, r.fin, str(r.texto), r.hablante) for r in prev.itertuples()]
            filas.append(fila_de(f, segs, None, None))
            print(f"{f.id} ya estaba hecho: se reutiliza", flush=True)
            continue
        if t is None:
            t = voz.Transcriptor(MODELO)
            print(f"{t} cargado en {t.segundos_carga:.1f} s")
        t0 = time.perf_counter()
        segs = t.segmentos(x, idioma="es")
        seg_asr = time.perf_counter() - t0
        t0 = time.perf_counter()
        segs = voz.diarizar(x, segs) if segs else segs
        seg_diar = time.perf_counter() - t0
        voz.a_tabla(segs).to_csv(AUDIO / "salidas" / f"{f.id}.csv", index=False)
        (AUDIO / "salidas" / f"{f.id}.srt").write_text(voz.a_srt(segs), encoding="utf-8")
        (AUDIO / "salidas" / f"{f.id}.txt").write_text(voz.a_texto(segs), encoding="utf-8")
        filas.append(fila_de(f, segs, seg_asr, seg_diar))
        print(f"{f.id} {f.duracion_seg:6.1f}s  RTF {seg_asr / f.duracion_seg:.2f}  "
              f"hablantes {filas[-1]['n_hablantes']}", flush=True)
    salida = tabla.merge(pd.DataFrame(filas), on="id", how="left")
    salida.to_csv(AUDIO / "asr_crudo.csv", index=False)
    print("listo:", AUDIO / "asr_crudo.csv")


if __name__ == "__main__":
    main()
