import re
import os
import json
from datetime import timedelta

# ==============================================================================
# CONFIGURACIÓN GLOBAL DESDE ARCHIVO EXTERNO
# ==============================================================================

CONFIG_PATH = "config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    CONFIG = {
        "subtitle_style": {"font": "Arial", "size": 50, "color": "white", "position": "bottom"},
        "max_characters_per_line": 40
    }
    print("⚠️ No se encontró config.json, usando configuración por defecto.")

# ==============================================================================
# LECTURA, PROCESAMIENTO Y ESCRITURA DE ARCHIVOS SRT
# ==============================================================================

def leer_srt(ruta_archivo):
    print(f"🔄 Leyendo archivo SRT desde: {ruta_archivo}")
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        print(f"❌ Error: El archivo {ruta_archivo} no fue encontrado.")
        return None
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return None

    bloques_raw = contenido.strip().split("\n\n")
    bloques = []

    for bloque in bloques_raw:
        lineas = bloque.split("\n")
        if len(lineas) >= 3:
            indice = lineas[0]
            timestamp = lineas[1]
            texto = lineas[2:]
            bloques.append({'indice': indice, 'timestamp': timestamp, 'texto': texto})
    
    print(f"✅ Se leyeron {len(bloques)} bloques de subtítulos.")
    return bloques

def _parse_time(time_str):
    parts = time_str.replace(',', '.').split(':')
    h = int(parts[0])
    m = int(parts[1])
    s, ms = map(int, parts[2].split('.'))
    return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)

def _format_time(td):
    total_seconds = int(td.total_seconds())
    milliseconds = td.microseconds // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# ==============================================================================
# NUEVO: Contar caracteres por línea
# ==============================================================================
def contar_caracteres_por_linea(bloques):
    max_chars = CONFIG["max_characters_per_line"]
    print(f"📏 Máximo permitido: {max_chars} caracteres por línea")
    for bloque in bloques:
        for linea in bloque['texto']:
            length = len(linea)
            if length > max_chars:
                print(f"⚠️ Bloque {bloque['indice']} excede ({length}/{max_chars}): {linea}")
            else:
                print(f"✅ Bloque {bloque['indice']} ({length}/{max_chars}): {linea}")

# ==============================================================================
# División de subtítulos censurados
# ==============================================================================
def dividir_y_reajustar_subtitulos(bloques):
    print(f"🔨 Buscando censuras para dividir los bloques.")
    
    nuevos_bloques = []
    nuevo_indice = 1
    
    for bloque in bloques:
        texto_lineas = " ".join(bloque['texto'])
        matches = list(re.finditer(r'(#{2,})', texto_lineas))
        
        if not matches:
            bloque['indice'] = str(nuevo_indice)
            nuevos_bloques.append(bloque)
            nuevo_indice += 1
            continue

        partes = []
        ultima_pos = 0
        for match in matches:
            partes.append(texto_lineas[ultima_pos:match.start()].strip())
            partes.append(match.group(0))
            ultima_pos = match.end()
        partes.append(texto_lineas[ultima_pos:].strip())
        partes = [p for p in partes if p]

        try:
            inicio_str, fin_str = bloque['timestamp'].split(' --> ')
            inicio = _parse_time(inicio_str)
            fin = _parse_time(fin_str)
            duracion_total = fin - inicio
            duracion_por_parte = duracion_total / len(partes)
        except (ValueError, IndexError) as e:
            print(f"❌ Error al parsear el timestamp '{bloque['timestamp']}'. Bloque omitido. Error: {e}")
            continue

        current_time = inicio
        for parte in partes:
            fin_parte = current_time + duracion_por_parte
            nuevo_bloque = {
                'indice': str(nuevo_indice),
                'timestamp': f"{_format_time(current_time)} --> {_format_time(fin_parte)}",
                'texto': [parte]
            }
            nuevos_bloques.append(nuevo_bloque)
            nuevo_indice += 1
            current_time = fin_parte
    
    print("✅ División y reajuste de subtítulos completado.")
    return nuevos_bloques

def guardar_srt(bloques, ruta_salida):
    print(f"💾 Guardando subtítulos censurados en: {ruta_salida}")
    try:
        with open(ruta_salida, "w", encoding="utf-8") as f:
            for bloque in bloques:
                f.write(f"{bloque['indice']}\n")
                f.write(f"{bloque['timestamp']}\n")
                for linea in bloque['texto']:
                    f.write(f"{linea}\n")
                f.write("\n")
        print("✅ Archivo SRT censurado y dividido guardado con éxito.")
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {e}")

# ==============================================================================
# INTEGRACIÓN CON DAVINCI RESOLVE
# ==============================================================================
def importar_a_davinci(ruta_archivo):
    try:
        import DaVinciResolveScript as libDaVi
        print("🔗 Conectando con DaVinci Resolve...")
        
        resolve_app = libDaVi.scriptapp("Resolve")
        if resolve_app is None:
            raise Exception("No se pudo conectar a DaVinci Resolve.")
            
        proyecto = resolve_app.GetProjectManager().GetCurrentProject()
        if proyecto is None:
            raise Exception("No hay un proyecto activo.")
            
        media_pool = proyecto.GetMediaPool()
        media_pool.ImportMedia([ruta_archivo])
        print("✅ Subtítulos importados a DaVinci Resolve.")

        # Aplicar estilos globales al track
        aplicar_estilos_globales(proyecto, CONFIG)

    except ImportError:
        print("⚠️ No se encontró 'DaVinciResolveScript'. Importa el SRT manualmente.")
    except Exception as e:
        print(f"❌ Error al importar: {e}")

# NUEVO: Aplicar estilos globales
def aplicar_estilos_globales(proyecto, config):
    timeline = proyecto.GetCurrentTimeline()
    if not timeline:
        raise Exception("No hay timeline activo.")

    estilo = config["subtitle_style"]
    ajustes = {
        "Font": estilo["font"],
        "Size": estilo["size"],
        "Color": estilo["color"],
        "Position": estilo["position"]
    }
    # Estos métodos son los que provee la API de Resolve (ejemplo)
    timeline.SetTrackName("subtitle", 1, "Subtítulos estilizados")
    timeline.SetSetting("subtitleTrackStyle", ajustes)
    print(f"🎨 Estilos aplicados al track: {ajustes}")

# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == "__main__":
    archivo_original = "ejemplo.srt"
    
    bloques_originales = leer_srt(archivo_original)
    
    if bloques_originales:
        contar_caracteres_por_linea(bloques_originales)
        bloques_modificados = dividir_y_reajustar_subtitulos(bloques_originales)
        
        archivo_salida = "ejemplo_dividido.srt"
        guardar_srt(bloques_modificados, archivo_salida)
        
        importar_a_davinci(archivo_salida)
