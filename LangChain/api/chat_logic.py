"""
Módulo principal para procesar chats utilizando una cadena de extracción y una cadena de QA
basada en un modelo LLM, integrando almacenamiento en MongoDB y persistencia local.

Este módulo realiza:
- Inicialización perezosa de componentes (LLM, vector store, cliente Weaviate).
- Extracción de información desde el historial de conversación mediante un LLM.
- Fusión de datos extraídos con datos existentes del usuario.
- Generación de respuestas a través de una cadena de QA.
- Registro y persistencia del historial de conversación.

Dependencias: chains, config, db, utils, llm, retriever, embeddings
"""

import json
import re
from datetime import datetime

# Componentes internos del proyecto
from chains.qa_chains import build_qa_chain
from chains.extraction import build_extractor_chain
from utils.json import extraer_json_del_texto
from db.mongo import (
    cargar_datos_usuario,
    guardar_usuario,
    cargar_conversacion,
    guardar_conversacion as guardar_conversacion_mongo,
    existe_conversacion_finalizada
)
from utils.guardar_chat import guardar_conversacion as guardar_conversacion_archivo
from retriever.weaviate_client import get_client
from embeddings.embedding_model import CustomEmbedding
from llm.groq_model import load_llm
from retriever.vector_store import create_vectorstore


def extraer_json_del_texto(texto):
    """
    Intenta extraer un bloque JSON desde un texto, especialmente si está
    encerrado en triple backticks.

    Args:
        texto (str): Texto de entrada posiblemente con contenido JSON.

    Returns:
        str | None: Cadena JSON si se encuentra, de lo contrario None.
    """
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", texto, re.DOTALL)
    if match:
        return match.group(1)

    match = re.search(r"({.*})", texto, re.DOTALL)
    if match:
        return match.group(1)

    return None


def convertir_objetos_para_json(obj):
    """
    Convierte objetos especiales como ObjectId a formatos compatibles con JSON.

    Args:
        obj (Any): Objeto a convertir.

    Returns:
        Any: Objeto serializable en JSON.
    """
    if isinstance(obj, dict):
        return {k: convertir_objetos_para_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convertir_objetos_para_json(i) for i in obj]
    elif 'ObjectId' in str(type(obj)):
        return str(obj)
    return obj


# Variables globales para componentes del sistema
client = None
embedding_model = None
vectorstore = None
llm = None
qa_chain = None
extractor_chain = None


def inicializar_componentes():
    """
    Inicializa los componentes del sistema si no han sido inicializados previamente:
    - Cliente Weaviate
    - Modelo de embeddings
    - Vector store
    - Modelo LLM
    - Cadenas de QA y extracción
    """
    global client, embedding_model, vectorstore, llm, qa_chain, extractor_chain
    if client is None:
        client = get_client()
        embedding_model = CustomEmbedding()
        vectorstore = create_vectorstore(client, embedding_model)
        llm = load_llm()
        qa_chain = build_qa_chain(llm, vectorstore.as_retriever())
        extractor_chain = build_extractor_chain(llm)


def procesar_chat_simple(query, chat_history=None, id_conversacion=None):
    """
    Procesa una conversación con el usuario, integrando extracción de datos
    desde el texto con LLM y generando una respuesta basada en contexto.

    Args:
        query (str): Pregunta o entrada del usuario.
        chat_history (list[tuple[str, str]] | None): Historial de conversación.
        id_conversacion (str | None): ID de conversación previa.

    Returns:
        dict: Diccionario con la respuesta generada, ID de conversación
              y si fue una nueva conversación.
    """
    inicializar_componentes()

    nueva_conversacion = False

    if id_conversacion:
        if existe_conversacion_finalizada(id_conversacion):
            id_anterior = id_conversacion
            id_conversacion = datetime.now().strftime("conversacion_%Y%m%d_%H%M%S")
            chat_history = [("[Sistema]", f"Esta conversación continúa desde una cerrada: {id_anterior}")]
            nueva_conversacion = True
        elif chat_history is None:
            chat_history = cargar_conversacion(id_conversacion) or []
    else:
        id_conversacion = datetime.now().strftime("conversacion_%Y%m%d_%H%M%S")
        chat_history = []
        nueva_conversacion = True

    chat_history.append((query, ""))

    resultado = extractor_chain.invoke({"chat_history": str(chat_history)})
    print("🔍 Resultado bruto extractor_chain.invoke():")
    print(resultado.content)

    json_str = extraer_json_del_texto(resultado.content)
    datos_usuario = cargar_datos_usuario(id_conversacion) or {}

    for campo in ["nombre", "empresa", "necesidad", "correo", "idioma", "agenda"]:
        if campo not in datos_usuario:
            datos_usuario[campo] = None

    datos_usuario["id_conversacion"] = id_conversacion

    print("📦 Datos usuario cargados desde Mongo o por defecto:")
    print(json.dumps(convertir_objetos_para_json(datos_usuario), indent=4))

    if json_str:
        try:
            extraidos = json.loads(json_str)
            print("🧠 Datos extraídos desde LLM:")
            print(json.dumps(extraidos, indent=4))

            datos_actualizados = False
            for key in datos_usuario:
                if key != "id_conversacion":
                    valor_extraido = extraidos.get(key)
                    if valor_extraido not in [None, ""] and datos_usuario.get(key) != valor_extraido:
                        datos_usuario[key] = valor_extraido
                        datos_actualizados = True

            if datos_actualizados:
                guardar_usuario(datos_usuario)
                print("✅ Datos actualizados guardados en Mongo:")
            else:
                print("ℹ️ No hubo nuevos datos que guardar.")

            print(json.dumps(convertir_objetos_para_json(datos_usuario), indent=4))

        except json.JSONDecodeError:
            print("❌ Error al decodificar JSON extraído:")
            print(json_str)
    else:
        print("⚠️ No se encontró JSON válido en la respuesta del extractor.")

    resumen_usuario = f"""
        Idioma: {datos_usuario.get('idioma') or 'No proporcionado'}
        Nombre: {datos_usuario.get('nombre') or 'No proporcionado'}
        Correo: {datos_usuario.get('correo') or 'No proporcionado'}
        Empresa: {datos_usuario.get('empresa') or 'No proporcionado'}
        Necesidad: {datos_usuario.get('necesidad') or 'No proporcionado'}
        Agenda: {datos_usuario.get('agenda') or 'No proporcionado'}
    """.strip()

    respuesta = qa_chain.invoke({
        "question": query,
        "chat_history": chat_history,
        "user_data": resumen_usuario
    })

    if nueva_conversacion:
        saludo_inicial = "Hola soy un asistente automatizado, me llamo Agustin, ¿en qué te puedo ayudar?"
        chat_history[-1] = (query, saludo_inicial)
        guardar_conversacion_mongo(chat_history, id_conversacion=id_conversacion)
        guardar_conversacion_archivo(chat_history, id_conversacion=id_conversacion)
        return {
            "respuesta": saludo_inicial,
            "id_conversacion": id_conversacion,
            "nueva_conversacion": nueva_conversacion
        }

    chat_history[-1] = (query, respuesta["answer"])
    guardar_conversacion_mongo(chat_history, id_conversacion=id_conversacion)
    guardar_conversacion_archivo(chat_history, id_conversacion=id_conversacion)

    return {
        "respuesta": respuesta["answer"],
        "id_conversacion": id_conversacion,
        "nueva_conversacion": nueva_conversacion
    }
