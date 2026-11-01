r"""Paso 3: video 1080×1920 con la narración (salidas/escena_k.wav), gráficos simples, subtítulos y música.

Uso (desde tarea_3/reel, después de hacer_voz.py):  ..\.venv-tts\Scripts\python.exe hacer_video.py
Salidas: salidas/reel_tarea3.mp4, reel_tarea3.srt (subtítulos con cifras y siglas normales) y portada.png.
Se apoya en las funciones de dibujo y en ffmpeg del código de la sesión 15 (curso_s15/reel.py, licencia MIT).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from num2words import num2words
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "curso_s15"))
import reel  # noqa: E402
from reel import ANCHO, ALTO, FPS, MARGEN, _fuente, _envolver, _ajustar  # noqa: E402

SALIDAS = AQUI / "salidas"
MUSICA = AQUI / "musica" / "clean_soul.ogg"
URL = "antoniomacedo17.github.io/Python_Intermedio_2026"
AUTOR = "Antonio Macedo · Diplomado QLAB"
CREDITOS = ["Voz: clon de mi voz con IA (Qwen3-TTS)",
            "Música: «Clean Soul», Kevin MacLeod (incompetech.com), CC BY 3.0",
            "Datos: OCDE, WID.world, Banco Mundial, MEF"]

# Paleta 3 del dashboard, variante oscura
FONDO, TEXTO, SUAVE, CAJA = "#1F2328", "#FFFFFF", "#B9BFC6", "#2D333B"
PERU, ALC, OCDE, NOR = "#FF8C9B", "#F2BE5C", "#3FB8C6", "#B4C6FF"
PAUSA, INICIO, FINAL = 0.35, 0.4, 1.2

# Gráfico de barras de cada escena: (etiqueta, valor, color); None = sin gráfico
BARRAS = {
    2: [("Perú", 16.7, PERU), ("América Latina", 21.5, ALC), ("OCDE", 33.7, OCDE), ("Nórdicos", 41.2, NOR)],
    3: [("Perú", 1.8, PERU), ("OCDE", 8.2, OCDE), ("Nórdicos", 14.4, NOR)],
    4: [("Perú", 8.3, PERU), ("Nórdicos", 23.5, NOR)],
    5: [("Perú", 7.5, PERU), ("OCDE", 20.8, OCDE), ("Nórdicos", 24.8, NOR)],
}
TITULO_BARRAS = {2: "Recaudación, % del PIB (2023)", 3: "Renta de personas, % del PIB (2023)",
                 4: "Ingreso del 50 % de menores ingresos, % (WID, 2019–2023)",
                 5: "Gasto social público, % del PIB (2023)"}


# ---------- Narración y tiempos de cada palabra ----------

def narracion(guion):
    partes, escenas, t, sr = [], [], INICIO, None
    for k in range(1, len(guion["escenas"]) + 1):
        w, sr = sf.read(SALIDAS / f"escena_{k}.wav", dtype="float32")
        partes.append(w)
    silencio = lambda s: np.zeros(int(s * sr), np.float32)
    audio = [silencio(INICIO)]
    for w in partes:
        escenas.append((t, t + len(w) / sr))
        audio += [w, silencio(PAUSA)]
        t += len(w) / sr + PAUSA
    audio.append(silencio(FINAL))
    return reel.Narracion(np.concatenate(audio), sr, escenas), partes


def hablado(palabra):
    """Cuántas letras «suena» una palabra escrita: sirve para repartir el tiempo de los subtítulos."""
    p = palabra.replace("IGV", "i ge be").replace("PIB", "pib").replace("OCDE", "o ce de e").replace("%", "por ciento")
    p = re.sub(r"\d+", lambda m: num2words(int(m.group()), lang="es"), p.replace(".", " coma "))
    return max(1, len(re.sub(r"[^\w]", "", p)))


def tiempos(guion, nar, partes):
    """Palabras del subtítulo (con cifras) alineadas al habla: Whisper da cuándo suena cada palabra de la voz y
    el texto con cifras se reparte sobre esa curva según lo que tarda en decirse cada palabra."""
    from faster_whisper import WhisperModel
    asr = WhisperModel(str(AQUI.parent / "modelos" / "faster-whisper-large-v3-turbo"), device="cpu", compute_type="int8")
    palabras = []
    for e, w, (ini, _) in zip(guion["escenas"], partes, nar.escenas):
        segs, _ = asr.transcribe(reel._a16k(w, nar.sr), language="es", word_timestamps=True)
        ws = [x for s in segs for x in s.words if x.word.strip()]
        largos = np.array([max(1, len(re.sub(r"[^\w]", "", x.word))) for x in ws], float)
        f_voz = np.concatenate([[0], np.cumsum(largos) / largos.sum()])
        t_voz = np.array([ws[0].start] + [x.end for x in ws])
        subs = e["sub"].split()
        pesos = np.array([hablado(s) for s in subs], float)
        f_sub = np.concatenate([[0], np.cumsum(pesos) / pesos.sum()])
        t_sub = np.interp(f_sub, f_voz, t_voz) + ini
        palabras += [(t_sub[i], t_sub[i + 1], s) for i, s in enumerate(subs)]
    nar.palabras = palabras
    return palabras


# ---------- Dibujo ----------

def base(guion):
    img = Image.new("RGB", (ANCHO, ALTO), FONDO)
    d = ImageDraw.Draw(img)
    d.text((MARGEN, 235), "FISCO Y DESIGUALDAD · PERÚ", font=_fuente("PublicSans", 34, 800), fill=PERU)
    aviso, f = "VOZ GENERADA CON IA", _fuente("PublicSans", 28, 700)
    x1 = MARGEN + d.textlength(aviso, font=f) + 36
    d.rounded_rectangle((MARGEN, 300, x1, 350), radius=25, outline=SUAVE, width=2)
    d.text((MARGEN + 18, 325), aviso, font=f, fill=SUAVE, anchor="lm")
    pie = _fuente("PublicSans", 30, 500)
    for i, linea in enumerate(_envolver(d, f"{AUTOR} · Fuente: {guion['fuente']}", pie, ANCHO - 2 * MARGEN)):
        d.text((MARGEN, 1560 + i * 42), linea, font=pie, fill=SUAVE)
    return img


def capa(k, e, avance):
    """Capa de la escena k; avance (0-1) anima el crecimiento de las barras."""
    c = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    ancho = ANCHO - 2 * MARGEN
    y = 430
    if k == 1:
        f = _fuente("Oswald", 132, 700)
        for linea in _envolver(d, e["etiqueta"], f, ancho):
            y += 150
            d.text((MARGEN, y), linea, font=f, fill=TEXTO, anchor="ls")
        fs = _fuente("PublicSans", 42, 500)
        y += 40
        for linea in _envolver(d, guion_global["subtitulo"], fs, ancho):
            y += 56
            d.text((MARGEN, y), linea, font=fs, fill=SUAVE, anchor="ls")
        return c
    if k == 7:
        f = _fuente("Oswald", 110, 700)
        for linea in _envolver(d, "Explora el dashboard", f, ancho):
            y += 125
            d.text((MARGEN, y), linea, font=f, fill=TEXTO, anchor="ls")
        fu = _ajustar(d, URL, "PublicSans", 700, ancho, 50, 30)
        y += 80
        d.text((MARGEN, y), URL, font=fu, fill=PERU, anchor="ls")
        fc = _fuente("PublicSans", 34, 500)
        y += 50
        for cr in CREDITOS:
            for linea in _envolver(d, cr, fc, ancho):
                y += 48
                d.text((MARGEN, y), linea, font=fc, fill=SUAVE, anchor="ls")
            y += 12
        return c
    # Cifra grande + etiqueta + barras
    color_cifra = PERU if k in (2, 3, 4, 5) else ALC
    f = _ajustar(d, e["cifra"], "Oswald", 700, ancho, 230)
    y += 210
    d.text((MARGEN, y), e["cifra"], font=f, fill=color_cifra, anchor="ls")
    fe = _fuente("PublicSans", 44, 600)
    y += 20
    for linea in _envolver(d, e["etiqueta"], fe, ancho):
        y += 56
        d.text((MARGEN, y), linea, font=fe, fill=TEXTO, anchor="ls")
    barras = BARRAS.get(k)
    if barras:
        y += 60
        d.text((MARGEN, y), TITULO_BARRAS[k], font=_fuente("PublicSans", 30, 600), fill=SUAVE, anchor="ls")
        y += 24
        maximo = max(v for _, v, _ in barras)
        fl, fv = _fuente("PublicSans", 32, 600), _fuente("PublicSans", 34, 800)
        etiqueta_ancho, alto_barra = 250, 44
        largo = ancho - etiqueta_ancho - 110
        for nombre, v, col in barras:
            d.text((MARGEN, y + alto_barra / 2), nombre, font=fl, fill=TEXTO, anchor="lm")
            x0 = MARGEN + etiqueta_ancho
            w = max(8, largo * v / maximo * avance)
            d.rounded_rectangle((x0, y, x0 + w, y + alto_barra), radius=6, fill=col)
            d.text((x0 + w + 14, y + alto_barra / 2), f"{v:.1f}", font=fv, fill=TEXTO, anchor="lm")
            y += alto_barra + 18
    return c


def cuadro(fondo, guion, nar, t, bloques, fuente_sub):
    img = fondo.copy()
    i = max([k for k, (ini, _) in enumerate(nar.escenas) if ini - PAUSA <= t] or [0])
    dt = t - nar.escenas[i][0] + PAUSA
    a = min(1.0, max(0.0, dt / 0.35))
    avance = min(1.0, max(0.0, dt / 0.9)) ** 0.6
    c = capa(i + 1, guion["escenas"][i], avance)
    if a < 1:
        c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
    img.paste(c, (0, int(40 * (1 - a))), c)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((MARGEN, 170, ANCHO - MARGEN, 178), radius=4, fill=CAJA)
    d.rounded_rectangle((MARGEN, 170, MARGEN + (ANCHO - 2 * MARGEN) * t / nar.duracion, 178), radius=4, fill=PERU)
    b = next((b for b in bloques if b[0][0] - 0.1 <= t <= b[-1][1] + 0.25), None)
    if b:
        texto = " ".join(p[2] for p in b)
        w = d.textlength(texto, font=fuente_sub)
        x, y = (ANCHO - w) / 2, 1360
        d.rounded_rectangle((x - 36, y - 26, x + w + 36, y + fuente_sub.size + 34), radius=28, fill=CAJA)
        for ini, fin, palabra in b:
            d.text((x, y), palabra, font=fuente_sub, fill=ALC if ini <= t <= fin + 0.05 else TEXTO)
            x += d.textlength(palabra + " ", font=fuente_sub)
    return img


def video(guion, nar, ruta):
    wav = ruta.with_suffix(".voz.wav")
    sf.write(wav, nar.audio, nar.sr)
    fondo, bloques, fuente_sub = base(guion), reel._bloques(nar.palabras), _fuente("PublicSans", 60, 800)
    dur = nar.duracion
    # Voz a -14 LUFS; música unos 20 dB por debajo, con entrada y salida suaves
    filtro = (f"[1:a]loudnorm=I=-14:TP=-2:LRA=11,aresample=48000[v];"
              f"[2:a]atrim=0:{dur:.2f},loudnorm=I=-34:TP=-10,afade=t=in:d=1.5,afade=t=out:st={dur - 2.5:.2f}:d=2.5,"
              f"aresample=48000[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]")
    cmd = [reel.FFMPEG, "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ANCHO}x{ALTO}", "-r", str(FPS), "-i", "-",
           "-i", str(wav), "-i", str(MUSICA), "-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(ruta)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(dur * FPS)):
        proc.stdin.write(cuadro(fondo, guion, nar, k / FPS, bloques, fuente_sub).tobytes())
    proc.stdin.close()
    proc.wait()
    wav.unlink()
    return ruta


guion_global = {}

if __name__ == "__main__":
    guion = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
    guion_global.update(guion)
    nar, partes = narracion(guion)
    tiempos(guion, nar, partes)
    reel.a_srt(nar, SALIDAS / "reel_tarea3.srt")
    for k, (ini, _) in enumerate(nar.escenas, 1):   # una imagen por escena para revisar el diseño
        cuadro(base(guion), guion, nar, ini + 1.5, reel._bloques(nar.palabras),
               _fuente("PublicSans", 60, 800)).save(SALIDAS / f"cuadro_{k}.png")
    if "--solo-cuadros" not in sys.argv:
        video(guion, nar, SALIDAS / "reel_tarea3.mp4")
        print(f"listo: {nar.duracion:.1f} s")
