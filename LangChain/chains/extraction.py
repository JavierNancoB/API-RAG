"""
Módulo para construir la cadena (chain) de extracción de datos del usuario
a partir del historial de chat usando LangChain y un modelo LLM.
"""

from langchain.prompts import PromptTemplate

def build_extractor_chain(llm):
    """
    Construye una cadena de extracción que utiliza un LLM para extraer
    datos del usuario desde el historial de chat.

    Args:
        llm: Instancia del modelo de lenguaje (Large Language Model) compatible con LangChain.

    Returns:
        Chain: Objeto cadena que al invocarse con el historial devuelve un JSON con los campos:
               nombre, empresa, necesidad, correo, idioma, agenda.

    Detalles:
        - Usa un PromptTemplate con formato específico que solicita estrictamente
          la extracción de los campos mencionados en formato JSON.
        - Incluye instrucciones claras para evitar confusiones, por ejemplo,
          que el usuario no se llame "Agustin" (nombre del asistente).
        - La cadena resultante es la composición del prompt y el LLM, lista para usarse.
    """
    prompt = PromptTemplate(
        input_variables=["chat_history"],
        template="""\nExtrae del siguiente historial los datos del usuario si están disponibles (EL USUARIO NO SE LLAMA AGUSTIN, ESE ES TÚ NOMBRE, pero si se repite mucho quizas si sea asi. Idioma es el idioma del input del usuario de la pregunta, si buscas la empresa Alloxentric NUNCA será la empresa).\nDevuelve en JSON estrictamente este formato:\n\n{{\n  "nombre": "",\n  "empresa": "",\n  "necesidad": "",\n  "correo": "",\n  "idioma": "",\n  "agenda": ""\n}}\n\nHistorial:\n{chat_history}\n"""
    )
    return prompt | llm
