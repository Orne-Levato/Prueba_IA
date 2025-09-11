# orchestrator.py (Versión Final del MVP)
import os
import time
import json
from moviepy.editor import VideoFileClip
import google.generativeai as genai
from dotenv import load_dotenv

# Agentes
from agents.transcriber import transcribe_clip_detailed
from agents.strategist import get_edit_plan_from_gemini

# --- CONFIGURACIÓN ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No se encontró la API Key de Gemini.")
genai.configure(api_key=GEMINI_API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
CLIPS_DIR = os.path.join(WORKSPACE_DIR, "clips")
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports")

# --- FUNCIONES AUXILIARES ---

def simplify_transcription_report(transcription_data: dict) -> dict:
    """Toma el reporte crudo de Whisper y lo limpia para Gemini."""
    simplified_dialogues = []
    for segment in transcription_data.get("dialogue_segments", []):
        simplified_dialogues.append({
            "start": segment.get("start"),
            "end": segment.get("end"),
            "text": segment.get("text", "").strip()
        })
    
    clean_report = {
        "duration": transcription_data.get("clip_duration"),
        "dialogues": simplified_dialogues
    }
    return clean_report

# --- Bloque principal ---
if __name__ == '__main__':

    # Buscar el único archivo en input/
    input_files = [f for f in os.listdir(INPUT_DIR) if os.path.isfile(os.path.join(INPUT_DIR, f))]
    
    if len(input_files) == 0:
        print(f"¡ERROR! No se encontró ningún archivo en {INPUT_DIR}")
        exit()
    elif len(input_files) > 1:
        print(f"¡ERROR! Hay más de un archivo en {INPUT_DIR}. Deja solo uno.")
        exit()

    input_filename = input_files[0]
    source_path = source_path = os.path.abspath(os.path.join(INPUT_DIR, input_filename)).replace("\\", "/") #modificación hehca por Orne L.
    # Esto convierte la ruta relativa en ruta absoluta, que FFmpeg entiende sin problemas.
    # y no hay problema para que lo encuentre.


    # 1. Transcripción Global
    print("--- [Orquestador] Iniciando transcripción del video completo... ---")
    full_transcription_report_path = transcribe_clip_detailed(source_path, REPORTS_DIR)
    with open(full_transcription_report_path, 'r', encoding='utf-8') as f:
        full_transcription_data = json.load(f)

    # 2. Limpieza y Preparación del Dossier/Reporte
    print("--- [Orquestador] Limpiando el reporte de transcripción... ---")

    clean_report = simplify_transcription_report(full_transcription_data)
    clean_report["input_name"] = input_filename
    
    # Guardar el reporte limpio para depuración
    report_path = os.path.join(REPORTS_DIR, f"{os.path.splitext(input_filename)[0]}_dossier_limpio.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(clean_report, f, ensure_ascii=False, indent=4)
    print(f"Dossier limpio para Gemini guardado en: {report_path}")

    # 3. Análisis y subida del archivo a Gemini (sea audio o video)
    final_edit_plan = {"plan_de_edicion": []}
    uploaded_files = {}
   
    try:
        print(f"Subiendo {input_filename} a la API de Gemini...")
        file_response = genai.upload_file(path=source_path, display_name=input_filename)
        print(f"Archivo subido. ID: {file_response.name}. Esperando a que esté ACTIVO...")

        while file_response.state.name == "PROCESSING":
            time.sleep(5)
            file_response = genai.get_file(name=file_response.name)
            print(f"Estado actual de {input_filename}: {file_response.state.name}")

        if file_response.state.name != "ACTIVE":
            raise Exception(f"La subida del archivo {input_filename} falló. Estado final: {file_response.state.name}")

        print(f"{input_filename} está ACTIVO y listo para ser analizado.")
        uploaded_files[input_filename] = file_response

        # Llamar al Estratega para el análisis
        clip_analysis = get_edit_plan_from_gemini(clean_report, file_response)
        final_edit_plan["plan_de_edicion"].append(clip_analysis)

    except Exception as e:
        print(f"No se pudo procesar el archivo. Error: {e}")

    finally:
         if file_response:
            print("\n--- [Orquestador] Limpiando el archivo subido del servidor... ---")
            print(f"Borrando {file_response.display_name} (ID: {file_response.name})...")
            genai.delete_file(file_response.name)
            print("Limpieza completada.")

    # 4. Guardar el Plan de Edición Final
    plan_path = os.path.join(REPORTS_DIR, f"{os.path.splitext(input_filename)[0]}_edit_plan.json")
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(final_edit_plan, f, ensure_ascii=False, indent=4)
        
    print(f"\n--- PROCESO COMPLETADO ---")
    print(f"El plan de edición multimodal ha sido guardado en: {plan_path}")