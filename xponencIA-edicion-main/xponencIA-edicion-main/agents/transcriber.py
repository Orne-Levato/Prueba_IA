# agents/transcriber.py
import os
import whisper
from moviepy.editor import VideoFileClip, AudioFileClip
import json
import time



MODEL_SIZE = "large-v3"




def transcribe_clip_detailed(clip_path: str, output_dir: str) -> str:
    
    print(f"--- [Transcriptor] Iniciando para: {os.path.basename(clip_path)} ---")

    if not os.path.exists(clip_path):
        raise FileNotFoundError(f"El archivo no se encontró en: {clip_path}")
    os.makedirs(output_dir, exist_ok=True)

    ext = os.path.splitext(clip_path)[1].lower()
    temp_audio_path = os.path.join(output_dir, f"temp_audio_{os.path.basename(clip_path)}.wav")

    video_duration = 0
    try:
        if ext in [".mp4", ".mov", ".avi", ".mkv"]:  # Archivos de video
            with VideoFileClip(clip_path) as video_clip:
                video_duration = video_clip.duration
                video_clip.audio.write_audiofile(temp_audio_path, codec="pcm_s16le", logger=None)
        elif ext in [".wav", ".mp3"]:  # Archivos de audio
            with AudioFileClip(clip_path) as audio_clip:
                video_duration = audio_clip.duration
                # Normalizamos a WAV 16-bit para Whisper
                audio_clip.write_audiofile(temp_audio_path, codec="pcm_s16le", logger=None)
        else:
            raise ValueError(f"Formato no soportado: {ext}")
    except Exception as e:
        print(f"Advertencia: No se pudo procesar {clip_path}. Error: {e}")
        result = {"text": "", "segments": []}
    else:
        model = whisper.load_model(MODEL_SIZE)
        result = model.transcribe(temp_audio_path, language="es")
    
    # Limpiar el archivo temporal
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)

    # Generar salida JSON
    final_output = {
        "clip_duration": video_duration,
        "full_text": result.get("text", "") if result else "",
        "dialogue_segments": result.get("segments", []) if result else []
    }

    clip_name = os.path.splitext(os.path.basename(clip_path))[0]
    output_json_path = os.path.join(output_dir, f"{clip_name}_transcription.json")

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)

    print(f"--- [Transcriptor] Finalizado para: {os.path.basename(clip_path)} ---")
    return output_json_path


