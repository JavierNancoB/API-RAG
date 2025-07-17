"""
Módulo para construir la cadena de preguntas y respuestas (QA) basada en
un modelo LLM y un sistema de recuperación de documentos (retriever)
usando LangChain.
"""

from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

def build_qa_chain(llm, retriever):
    """
    Construye una cadena de ConversationalRetrievalChain que responde
    preguntas del usuario con contexto, siguiendo un prompt específico.

    Args:
        llm: Instancia del modelo de lenguaje (Large Language Model).
        retriever: Objeto responsable de recuperar documentos relevantes para el contexto.

    Returns:
        ConversationalRetrievalChain: Cadena que procesa preguntas con contexto y
        responde de forma profesional y directa según las reglas del prompt.

    Detalles del prompt:
        - El asistente es profesional y directo, representando la empresa Alloxentric.
        - Responde en el idioma del usuario.
        - Respuestas claras, precisas y breves (no más de 12 líneas).
        - No explica el proceso ni reformula preguntas.
        - Solicita datos del usuario (nombre, correo, empresa, necesidad, agenda) de forma amable si no están.
        - Controla el flujo de conversación para recolectar información de usuario.
        - No repite saludos innecesarios.
        - Usa el contexto de documentos relevantes para responder.

    Uso:
        La cadena puede ser invocada con inputs: question, user_data y context.
    """
    qa_prompt_template = """
        Eres un asistente profesional y directo de la empresa Alloxentric (siempre habla de nosotros).

        Tu único trabajo es brindar información útil, clara y precisa al usuario (No más de 12 lineas), sin explicar tu proceso de pensamiento, sin reformular sus preguntas, y sin dar clases.

        - Responde en el idioma que te responde el usuario.
        - Nunca empieces tus respuestas con frases como "La forma correcta de decirlo es..." o "La pregunta reformulada sería...".
        - No repitas la pregunta del usuario.
        - No expliques cómo interpretas lo que el usuario dice.
        - Responde de inmediato con la información más útil para el usuario.
        - Si el usuario aún no ha proporcionado su nombre o correo, pídelos de forma amable.
        - Si ya tienes el nombre y correo, no los vuelvas a pedir.
        - Si ya tienes nombre y correo, debes preguntar por el nombre de la empresa.
        - Si ya tienes nombre, correo y EL NOMBRE de la empresa, puedes preguntar por la necesidad y si desea ser agendado (RECUERDA QUE NECESITAS EL NOMBRE) si aún no ha sido mencionada.
        - Despues continuar con el flujo de informacion util y preguntas para el usuario.
        - No repitas tanto la palabra 'Hola' o 'Hola, soy Agustin', no es necesario.

        Datos del usuario conocidos hasta ahora:
        {user_data}

        Pregunta del usuario (debes responder en el idioma de la pregunta): {question}

        Documentos contextuales: {context}

        Respuesta:
        """

    qa_prompt = PromptTemplate(
        input_variables=["context", "question", "user_data"],
        template=qa_prompt_template,
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        combine_docs_chain_kwargs={"prompt": qa_prompt}
    )
