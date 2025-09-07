## Arquitectura del Sistema

### XPONENCIA-EDICION/

* ├── agents/         # Contiene los scripts o módulos de agentes
* ├── input/          # Carpeta para archivos de entrada
* ├── output/         # Carpeta para archivos de salida/resultados
* ├── venv/           # Entorno virtual de Python
* ├── workspace/      # Carpeta para trabajo temporal o intermedio
* ├── .env            # Variables de entorno del proyecto
* ├── config.py       # Archivo de configuración principal
* ├── orchestrator.py # Script principal de orquestación
* ├── requirements.txt# Dependencias del proyecto

1.  **Orchestrator (`venv` principal):** Es el director del proyecto. Se encarga de coordinar a los demás agentes, gestionar el flujo de datos y la lógica principal.
2.  **Agente Transcriptor (Whisper):** Reside en el `venv` principal. Su única misión es convertir el audio de los videos en texto estructurado.
3.  **Agente Estratega (Gemini):** Reside en el `venv` principal. Es el "cerebro" del sistema. Recibe los datos de los otros agentes y utiliza la API de Google Gemini para tomar decisiones editoriales.

## 🚀 Guía de Instalación y Configuración

Sigue estos pasos cuidadosamente para configurar el entorno del proyecto.

### 1. Clonar el Repositorio

Abre una terminal y clona este repositorio en tu máquina local:
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DE_LA_CARPETA>
```

### 2. Configurar las Claves de API

El proyecto necesita una clave de API para comunicarse con Google Gemini.

1.  En la raíz del proyecto, crea un archivo llamado `.env`.
2.  Abre el archivo `.env` y añade tu clave de API de la siguiente manera:

    ```env
    # Obtenida desde Google AI Studio
    GEMINI_API_KEY="AIzaSy...tu_clave_de_api_aqui"
    ```
    Asegúrate de que no haya espacios extra.

### 3. Configurar el Entorno Virtual Principal

Este entorno contendrá la lógica principal y los agentes de transcripción y estrategia.

1.  Crea el entorno virtual usando:
    ```bash
    py -m venv venv
    ```
2.  Activa el entorno virtual:
    *   **Windows:** `.\venv\Scripts\activate`
    *   **macOS / Linux:** `source venv/bin/activate`
    
    Aparece `(venv)` al principio de la línea de la terminal.

3.  Instala las dependencias desde el archivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

### Uso
* Asegurate de que tu entorno principal `(venv)` esté activado en la terminal.
* Coloca los archivos de entrada en la carpeta **input/**.
* Ejecuta el orquestador principal:
    ```
    python orchestrator.py
    ```
## Salida del Programa

El script ejecutará el pipeline completo de análisis. Al finalizar, encontrarás los siguientes archivos en la carpeta `workspace/reports/`:

*   `_transcription.json`: La transcripción cruda generada por Whisper para cada clip.
*   `_dossier_limpio.json`: El informe consolidado y limpio que se envía a Gemini.
*   `_edit_plan.json` o `_edit_plan_multimodal.json`: **Este es el resultado principal.** Contiene el plan de edición en formato JSON, con los timestamps de las escenas seleccionadas, el análisis de la IA y el texto sugerido.

