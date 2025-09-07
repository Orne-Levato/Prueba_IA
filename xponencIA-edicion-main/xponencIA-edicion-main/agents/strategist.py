# agents/strategist.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
# Cargar variables de entorno
load_dotenv()

# API de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No se encontró la API Key de Gemini")
genai.configure(api_key=GEMINI_API_KEY)

# Definimos el modelo
MODEL_NAME = "gemini-2.5-pro"

# --- LA PLANTILLA DEL PROMPT ---

PROMPT_TEMPLATE_VANTA = """ Quiero que analices el siguiente material compuesto por un video y su transcripción textual.

Instrucciones:

Divide el video en bloques de 5 a 10 segundos.

Para cada bloque, indica el rango de tiempo con marcas [inicio - fin].

En cada bloque escribe un único apartado:
Analisis: debe ser un análisis integral que combine los tres niveles:

Verbal: interpreta el contenido de lo dicho, tono discursivo, elección de palabras, pausas, silencios y la intención comunicativa aparente. Considera si hay congruencia o incongruencia entre lo que se dice y cómo se dice.

No verbal: describe expresiones faciales, microexpresiones, contacto visual, lenguaje corporal, posturas, distancia interpersonal, gesticulación, tono y modulación de la voz. Señala cambios en la energía o sincronía entre participantes.

Estratégico: analiza la interacción desde la psicología evolutiva y social. Observa señales de poder, dominancia o sumisión, empatía, cooperación, manipulación, atracción, rechazo, construcción de estatus, liderazgo, vulnerabilidad o intentos de persuasión. Interpreta cómo estas conductas afectan la dinámica grupal o individual.

Cada bloque debe escribirse como un análisis narrativo y contextualizado, no como una lista.

Al terminar todos los bloques, haz un Meta-análisis final, resumiendo la evolución de las dinámicas sociales, los roles de los participantes y patrones clave.

# DATOS (GUION DEL VIDEO)
Aquí tienes el guion completo de la conversación:

{dossier_json}

Formato de salida esperado:
[00:00 - 00:07]
Analisis: ...

[00:07 - 00:15]
Analisis: ...

...

Meta-analisis final:
...

"""

def get_edit_plan_from_gemini(dossier_data: dict, uploaded_video_file) -> dict:

    print("--- [Estratega] Iniciando análisis holístico del video completo ---")

    # 1. Convertir el diccionario de datos a una cadena de texto JSON
    dossier_json_string = json.dumps(dossier_data, indent=2, ensure_ascii=False)

    # 2. Insertar el JSON en nuestra plantilla de prompt
    full_prompt = PROMPT_TEMPLATE_VANTA.format(dossier_json=dossier_json_string)

    # 3. Llamar a la API de Gemini con el prompt de texto y el archivo de video
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # Enviamos una lista que contiene tanto el texto como el video
        response = model.generate_content(
            [full_prompt, uploaded_video_file],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        # 4. Cargar la respuesta de texto JSON en un diccionario de Python
        plan_json = json.loads(response.text)
        print("--- [Estratega] Plan de corte recibido exitosamente de Gemini. ---")
        return plan_json

    except Exception as e:
        print(f"¡ERROR! Ocurrió un error en el análisis holístico: {e}")
        # En caso de error, devolvemos un plan vacío
        return {"plan_de_corte": []}