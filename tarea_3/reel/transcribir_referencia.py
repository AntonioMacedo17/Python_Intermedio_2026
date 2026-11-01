r"""Transcribe la grabación de referencia con Whisper (large-v3-turbo, local) y la compara con la transcripción
que dio Antonio. Uso: ..\.venv-tts\Scripts\python.exe transcribir_referencia.py  (desde tarea_3/reel)"""
import sys
from pathlib import Path

import jiwer
from faster_whisper import WhisperModel

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "curso_s15"))
import reel  # noqa: E402

DADA = ("Hola, soy Antonio y estudio economía. En el Perú, buena parte de lo que recauda el Estado viene de impuestos "
        "que pagamos todos al comprar, como el IGV. Hoy quiero mostrarte, con datos, quién financia realmente al "
        "Estado peruano y cómo nos comparamos con América Latina y con los países nórdicos.")

audio = reel.cargar_audio(AQUI / "voz" / "mi_voz.m4a")
print(f"duración: {len(audio) / 16000:.1f} s; pico: {abs(audio).max():.2f}")
asr = WhisperModel(str(AQUI.parent / "modelos" / "faster-whisper-large-v3-turbo"), device="cpu", compute_type="int8")
oido = " ".join(s.text.strip() for s in asr.transcribe(audio, language="es")[0])
print("WHISPER:", oido)
print("DADA:   ", DADA)
print(f"WER (normalizado): {jiwer.wer(reel._normalizar(DADA), reel._normalizar(oido)):.3f}")
