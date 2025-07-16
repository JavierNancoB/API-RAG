from datetime import datetime
import json
from chains.qa_chains import build_qa_chain
from chains.extraction import build_extractor_chain
from config.respuestas_salida import RESPUESTAS_SALIDA
from utils.json import extraer_json_del_texto
from db.mongo import (
    cargar_datos_usuario,
    guardar_usuario,
    cargar_conversacion,
    guardar_conversacion as guardar_conversacion_mongo,
    mover_a_finalizadas,
    existe_conversacion_finalizada
)
from utils.guardar_chat import guardar_conversacion as guardar_conversacion_archivo
from retriever.weaviate_client import get_client
from embeddings.embedding_model import CustomEmbedding
from llm.groq_model import load_llm
from retriever.vector_store import create_vectorstore
import re


def extraer_json_del_texto(texto):
    # Buscar bloque JSON dentro de triples backticks
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", texto, re.DOTALL)
    if match:
        return match.group(1)
    else:
        # Si no encuentra, intenta buscar solo el primer bloque JSON simple
        match = re.search(r"({.*})", texto, re.DOTALL)
        if match:
            return match.group(1)
    return None


def convertir_objetos_para_json(obj):
    if isinstance(obj, dict):
        return {k: convertir_objetos_para_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convertir_objetos_para_json(i) for i in obj]
    elif 'ObjectId' in str(type(obj)):
        return str(obj)
    else:
        return obj


# Variables globales inicializadas en None
client = None
embedding_model = None
vectorstore = None
llm = None
qa_chain = None
extractor_chain = None


def inicializar_componentes():
    global client, embedding_model, vectorstore, llm, qa_chain, extractor_chain
    if client is None:
        client = get_client()
        embedding_model = CustomEmbedding()
        vectorstore = create_vectorstore(client, embedding_model)
        llm = load_llm()
        qa_chain = build_qa_chain(llm, vectorstore.as_retriever())
        extractor_chain = build_extractor_chain(llm)


def procesar_chat_simple(query, chat_history=None, id_conversacion=None):
    inicializar_componentes()  # Asegura que todo esté listo antes de usar

    nueva_conversacion = False

    if id_conversacion:
        doc_finalizada = existe_conversacion_finalizada(id_conversacion)
        if doc_finalizada:
            id_anterior = id_conversacion
            id_conversacion = datetime.now().strftime("conversacion_%Y%m%d_%H%M%S")
            chat_history = [("[Sistema]", f"Esta conversación continúa desde una cerrada: {id_anterior}")]
            nueva_conversacion = True
        else:
            if chat_history is None:
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
                    # Actualiza solo si el valor extraído no es None ni cadena vacía y es distinto
                    if valor_extraido not in [None, ""] and datos_usuario.get(key) != valor_extraido:
                        datos_usuario[key] = valor_extraido
                        datos_actualizados = True

            if datos_actualizados:
                guardar_usuario(datos_usuario)
                print("✅ Datos actualizados guardados en Mongo:")
                print(json.dumps(convertir_objetos_para_json(datos_usuario), indent=4))
            else:
                print("ℹ️ No hubo nuevos datos que guardar.")

            print("📌 Datos usuario después de fusión con lo extraído:")
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

    # Si la conversación es nueva, devolvemos un saludo inicial
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
