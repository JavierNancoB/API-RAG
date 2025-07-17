"""
Módulo para extraer un bloque JSON formateado dentro de texto delimitado
por triple backticks con especificador 'json'.
"""

import re

def extraer_json_del_texto(texto):
    """
    Extrae un bloque JSON delimitado por ```json ... ``` dentro de un texto.

    Args:
        texto (str): Texto que contiene un bloque JSON entre backticks.

    Returns:
        str | None: Cadena JSON extraída sin los backticks, o None si no se encuentra.
    """
    patron = r"```json\s*(\{.*?\})\s*```"
    match = re.search(patron, texto, re.DOTALL)
    return match.group(1) if match else None
