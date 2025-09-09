#subtitulos.py se ejecuta dentro de la carpeta /agents

import re 
import os
import json 

# re es para buscar, reemplazar y validar texto
# os es para guardar los subtitulos generados en una carpeta asignada
# json guarda o lee subtitulos en estructuras de datos


#lectura del archivo SRT

def leer_srt(ruta_archivo): # Pongo input ya que es donde se almacena el video en el proyecto
    with open (ruta_archivo, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    
    #Y separo por bloques
    bloques = contenido.strip().split("\n\n") #strip() saca los espacios y saltos de línea
    return bloques

# saco el texto y cuento caracteres

def contar_caracteres(bloques):
    longitudes = [] #lista para guardar los numeros de caracteres
    for bloque in bloques: # ubico los bloques uno a uno
        lineas = bloque.split("\n")
        texto = lineas[2:] # Quiero contar los caracteres de dos lineas
        
        for linea in texto:
            longitudes.append(len(linea))
    return longitudes
    
# Importo a DaVinci Resolve
def Importo_a_Davinci(ruta_archivo):
    """Importa un archivo .srt al proyecto activo de DaVinci Resolve usando libDaVi"""
    try:
        try:
            import DaVinciResolveScript as libDaVi
        except ImportError:
            print("No se encontró DaVinciResolveScript, se omite la importación.")
            libDaVi = None

        if libDaVi is not None:
            ContDaVi = libDaVi.scriptapp("Resolve")
            proyecto = ContDaVi.GetProjectManager().GetCurrentProject()
            media_pool = proyecto.GetMediaPool()
            media_pool.ImportMedia([ruta_archivo])
            print("Subtítulos importados a DaVinci Resolve.")
        else:
            print("No se puede importar a DaVinci Resolve porque el módulo no está disponible.")

    except Exception as e:
        print("No pude conectar con DaVinci Resolve. Importalo a mano.")
        print("Error:", e)



 # Parte principal

if __name__ == "__main__": #__name__ es la variable que marca cómo se está ejecutando el archivo
    archivo = "ejemplo.srt"

    bloques = leer_srt(archivo)
    longitudes = contar_caracteres(bloques)
    Importo_a_Davinci(archivo)



# El estilo

TRACK_STYLE = { 
    "font": "Arial.ttf",
    "font_size": 36,
    "color": "#FFFFFF",
    "position": "bottom", # para que los subs aparezcan en la parte de abajo
    "use_track_style": True #le meto el estilo del track por defaul
}

# DEFAULT_MAX_CHARS_PER_LINE = 30 



#----------------------------
# Censura por bloques
#----------------------------


def separar_censurados(bloques):
    """
    Busca líneas con censura a partir de los dos numerales (#) o más y separa en 3 partes: 
    - Lo que está antes de la censura
    - La censura (####)
    - Lo que está después
    Devuelve una lista de nuevos bloques de texto
    """
    nuevos_bloques = []

    for bloque in bloques:

        lineas = bloque.split("\n")
        texto = lineas[2:]  # las líneas de subtítulo (después del índice y el timestamp)

        for linea in texto:
            match = re.search(r"(#+)", linea)
            if match and len(match.group(0)) >= 2:  # censura de 2 o más #
                antes = linea[:match.start()].strip() #len(...) en Python → devuelve la cantidad de caracteres de un string.
                censura = match.group(0)
                despues = linea[match.end():].strip()

                if antes:
                    nuevos_bloques.append(antes)
                nuevos_bloques.append(censura)
                if despues:
                    nuevos_bloques.append(despues)
            else:
                nuevos_bloques.append(linea)

    return nuevos_bloques
