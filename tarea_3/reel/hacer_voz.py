r"""Paso 2: narración con la voz clonada de Antonio (Qwen3-TTS 0.6B Base, en CPU) y control con Whisper.

Uso (desde tarea_3/reel):  ..\.venv-tts\Scripts\python.exe hacer_voz.py
Genera una escena por vez y la guarda en salidas/escena_k.wav, así un corte no hace perder lo ya generado
(si el archivo existe, la escena se salta). Al final transcribe cada escena con Whisper para revisar que se entienda.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "curso_s15"))
import reel  # noqa: E402  (código de la sesión 15, licencia MIT)

MODELOS = AQUI.parent / "modelos"
SALIDAS = AQUI / "salidas"
# Transcripción de referencia: la que dio Antonio (Whisper coincidió salvo "recaudo" e "IGB", errores de Whisper).
# "IGV" se escribe como se pronunció, para que el texto calce con el audio.
TEXTO_REF = ("Hola, soy Antonio y estudio economía. En el Perú, buena parte de lo que recauda el Estado viene de "
             "impuestos que pagamos todos al comprar, como el i ge be. Hoy quiero mostrarte, con datos, quién financia "
             "realmente al Estado peruano y cómo nos comparamos con América Latina y con los países nórdicos.")


def main():
    import torch
    from qwen_tts import Qwen3TTSModel

    SALIDAS.mkdir(exist_ok=True)
    guion = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
    t0 = time.time()
    ref = reel.cargar_audio(AQUI / "voz" / "mi_voz.m4a")
    tts = Qwen3TTSModel.from_pretrained(str(MODELOS / "qwen3-tts-0.6b-base"), device_map="cpu", dtype=torch.float32)
    prompt = tts.create_voice_clone_prompt(ref_audio=(ref, 16000), ref_text=TEXTO_REF)
    print(f"modelo cargado en {time.time() - t0:.0f} s", flush=True)

    for k, e in enumerate(guion["escenas"], 1):
        ruta = SALIDAS / f"escena_{k}.wav"
        if ruta.exists():
            continue
        t = time.time()
        wavs, sr = tts.generate_voice_clone(text=[e["frase"]], language=["Spanish"], voice_clone_prompt=prompt)
        w = np.asarray(wavs[0], np.float32)
        sf.write(ruta, w, sr)
        print(f"escena {k}: {len(w) / sr:.1f} s de audio en {time.time() - t:.0f} s", flush=True)
    del tts

    # Control: ¿Whisper entiende lo que dice la voz?
    from faster_whisper import WhisperModel
    modelo = WhisperModel(str(MODELOS / "faster-whisper-large-v3-turbo"), device="cpu", compute_type="int8")
    lineas, total = [], 0.0
    for k, e in enumerate(guion["escenas"], 1):
        w, sr = sf.read(SALIDAS / f"escena_{k}.wav", dtype="float32")
        total += len(w) / sr
        oido = " ".join(s.text.strip() for s in modelo.transcribe(reel._a16k(w, sr), language="es")[0])
        lineas += [f"Escena {k} ({len(w) / sr:.1f} s)", f"  guion:   {e['sub']}", f"  whisper: {oido}", ""]
    lineas.append(f"Duración total de la voz: {total:.1f} s (sin pausas)")
    (SALIDAS / "revision_voz.txt").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas), flush=True)
    print(f"listo en {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
