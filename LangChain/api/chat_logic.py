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

from datetime import datetime
import time


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
    inicializar_componentes()

    nueva_conversacion = False

    # --- Tiempo cargar conversación MongoDB ---
    start_db_load = time.perf_counter()

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

    end_db_load = time.perf_counter()
    print(f"⏱️ Tiempo carga conversación MongoDB: {(end_db_load - start_db_load)*1000:.2f} ms")

    chat_history.append((query, ""))

    # --- Tiempo llamada extractor_chain (API LLM) ---
    start_llm_extract = time.perf_counter()
    resultado = extractor_chain.invoke({"chat_history": str(chat_history)})
    end_llm_extract = time.perf_counter()
    print(f"⏱️ Tiempo extractor_chain.invoke(): {(end_llm_extract - start_llm_extract)*1000:.2f} ms")

    print("🔍 Resultado bruto extractor_chain.invoke():")
    print(resultado.content)

    json_str = extraer_json_del_texto(resultado.content)

    # --- Tiempo carga datos usuario MongoDB ---
    start_db_load_user = time.perf_counter()
    datos_usuario = cargar_datos_usuario(id_conversacion) or {}
    end_db_load_user = time.perf_counter()
    print(f"⏱️ Tiempo carga datos usuario MongoDB: {(end_db_load_user - start_db_load_user)*1000:.2f} ms")

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

            # --- Tiempo guardar datos usuario MongoDB (si hay cambios) ---
            if datos_actualizados:
                start_db_save_user = time.perf_counter()
                guardar_usuario(datos_usuario)
                end_db_save_user = time.perf_counter()
                print("✅ Datos actualizados guardados en Mongo:")
                print(json.dumps(convertir_objetos_para_json(datos_usuario), indent=4))
                print(f"⏱️ Tiempo guardar datos usuario MongoDB: {(end_db_save_user - start_db_save_user)*1000:.2f} ms")
            else:
                print("ℹ️ No hubo nuevos datos que guardar.")

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

    # --- Tiempo llamada qa_chain (API LLM) ---
    start_llm_qa = time.perf_counter()
    respuesta = qa_chain.invoke({
        "question": query,
        "chat_history": chat_history,
        "user_data": resumen_usuario
    })
    end_llm_qa = time.perf_counter()
    print(f"⏱️ Tiempo qa_chain.invoke(): {(end_llm_qa - start_llm_qa)*1000:.2f} ms")

    if nueva_conversacion:
        saludo_inicial = "Hola soy un asistente automatizado, me llamo Agustin, ¿en qué te puedo ayudar?"
        chat_history[-1] = (query, saludo_inicial)

        # --- Tiempo guardar conversación MongoDB y archivo ---
        start_db_save_conv = time.perf_counter()
        guardar_conversacion_mongo(chat_history, id_conversacion=id_conversacion)
        guardar_conversacion_archivo(chat_history, id_conversacion=id_conversacion)
        end_db_save_conv = time.perf_counter()
        print(f"⏱️ Tiempo guardar conversación MongoDB y archivo: {(end_db_save_conv - start_db_save_conv)*1000:.2f} ms")

        return {
            "respuesta": saludo_inicial,
            "id_conversacion": id_conversacion,
            "nueva_conversacion": nueva_conversacion
        }

    chat_history[-1] = (query, respuesta["answer"])

    # --- Tiempo guardar conversación MongoDB y archivo ---
    start_db_save_conv = time.perf_counter()
    guardar_conversacion_mongo(chat_history, id_conversacion=id_conversacion)
    guardar_conversacion_archivo(chat_history, id_conversacion=id_conversacion)
    end_db_save_conv = time.perf_counter()
    print(f"⏱️ Tiempo guardar conversación MongoDB y archivo: {(end_db_save_conv - start_db_save_conv)*1000:.2f} ms")

    return {
        "respuesta": respuesta["answer"],
        "id_conversacion": id_conversacion,
        "nueva_conversacion": nueva_conversacion
    }

