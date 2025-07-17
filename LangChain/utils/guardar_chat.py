"""
Módulo para guardar el historial de conversaciones en archivos de texto
locales organizados por carpeta y nombre de archivo.
"""

import os
from datetime import datetime

def guardar_conversacion(chat_history, carpeta=None, id_conversacion=None):
    """
    Guarda el historial de chat en un archivo de texto.

    Args:
        chat_history (list[tuple[str, str]]): Lista de tuplas (pregunta, respuesta).
        carpeta (str, opcional): Directorio donde se guardará la conversación.
                                 Si no se especifica, se usa 'conversaciones' en la raíz del proyecto.
        id_conversacion (str, opcional): Identificador único para el nombre del archivo.
                                         Si no se proporciona, se genera un timestamp.

    Efectos secundarios:
        Crea el directorio si no existe.
        Escribe el archivo con el formato:
            Turno X:
            Tú: pregunta
            Bot: respuesta

        Imprime la ruta donde se guardó la conversación.
    """
    if carpeta is None:
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        langchain_dir = os.path.abspath(os.path.join(dir_actual, ".."))
        carpeta = os.path.join(langchain_dir, "conversaciones")

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    nombre_archivo = f"{id_conversacion or datetime.now().strftime('conversacion_%Y%m%d_%H%M%S')}.txt"
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        for i, (pregunta, respuesta) in enumerate(chat_history, start=1):
            f.write(f"Turno {i}:\n")
            f.write(f"Tú: {pregunta}\n")
            f.write(f"Bot: {respuesta}\n\n")

    print(f"Conversación guardada en: {ruta_archivo}")
