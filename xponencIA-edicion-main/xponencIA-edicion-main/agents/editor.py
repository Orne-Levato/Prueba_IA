# editor.py = Automatización de edición en Resolve

#--------------------------------------
# Objetivos:
# - Conectar al proyecto y la timeline.
# - Agregar marcadores en base a timestamps.
# - Hacer cortes en base a pares inicio/fin.


import DaVinciResolveScript as dvr

def conectar_resolve():
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        raise Exception("❌ No se pudo conectar a DaVinci Resolve.")
    return resolve

def agregar_marcadores(timestamps, color="Blue"):
    resolve = conectar_resolve()
    proyecto = resolve.GetProjectManager().GetCurrentProject()
    timeline = proyecto.GetCurrentTimeline()
    
    for ts in timestamps:
        tiempo_seg = ts["time"]  # en segundos
        nombre = ts.get("label", f"Marcador {ts['time']}")
        timeline.AddMarker(tiempo_seg, color, nombre, "", 1)
    print(f"✅ {len(timestamps)} marcadores creados.")

def hacer_cortes(segments):
    resolve = conectar_resolve()
    proyecto = resolve.GetProjectManager().GetCurrentProject()
    timeline = proyecto.GetCurrentTimeline()
    
    for seg in segments:
        inicio = seg["start"]
        fin = seg["end"]
        timeline.AddMarker(inicio, "Green", "Inicio corte", "", 1)
        timeline.AddMarker(fin, "Red", "Fin corte", "", 1)
        timeline.Cut(inicio)  
        timeline.Cut(fin)
    print(f"✂️ {len(segments)} cortes aplicados.")



