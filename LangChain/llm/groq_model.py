"""
Módulo para cargar y configurar el modelo de lenguaje LLM ChatGroq
con parámetros específicos y clave API desde configuración.
"""

from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY

def load_llm():
    """
    Inicializa y retorna una instancia del modelo ChatGroq configurado.

    Configuraciones:
        - api_key: Clave API para autenticación.
        - model: Nombre del modelo específico a usar.
        - temperature: Control de aleatoriedad en la generación (0.0 = determinista).

    Returns:
        ChatGroq: Instancia configurada del modelo LLM para uso en cadenas.
    """
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0.0,
    )
