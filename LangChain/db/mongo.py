"""
Módulo para gestionar la conexión y operaciones básicas con MongoDB
para almacenamiento de usuarios, conversaciones activas y finalizadas.

Funciones:
- conectar_mongo: Inicializa la conexión y colecciones.
- cerrar_mongo: Cierra la conexión activa.
- guardar_usuario: Inserta o actualiza datos del usuario.
- cargar_conversacion: Obtiene el historial de una conversación.
- guardar_conversacion: Actualiza o inserta el historial de conversación.
- mover_a_finalizadas: Mueve una conversación activa a finalizada.
- existe_conversacion_finalizada: Verifica si una conversación está finalizada.
- cargar_datos_usuario: Carga datos del usuario por ID de conversación.
"""

from pymongo import MongoClient
from datetime import datetime
import os

client = None
db = None
coleccion_usuarios = None
coleccion_conversaciones = None
coleccion_finalizadas = None

def conectar_mongo(uri=None, db_name="alloxentric"):
    """
    Conecta a MongoDB y asigna las colecciones globales.

    Args:
        uri (str): URI de conexión a MongoDB.
        db_name (str): Nombre de la base de datos.

    Efectos:
        Inicializa las variables globales client, db y colecciones.
        Imprime mensaje de conexión exitosa.
    """
    global client, db, coleccion_usuarios, coleccion_conversaciones, coleccion_finalizadas
    if uri is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(uri)
    db = client[db_name]
    coleccion_usuarios = db["usuarios"]
    coleccion_conversaciones = db["conversaciones"]
    coleccion_finalizadas = db["finalizadas"]
    print(f"🔌 Conectado a MongoDB en {uri}")


def cerrar_mongo():
    """
    Cierra la conexión activa con MongoDB.

    Efectos:
        Cierra el cliente Mongo si está activo y imprime mensaje.
    """
    global client
    if client:
        client.close()
        print("🔒 Conexión a MongoDB cerrada")


def guardar_usuario(datos_usuario: dict):
    """
    Inserta o actualiza la información del usuario en la colección 'usuarios'.

    Args:
        datos_usuario (dict): Diccionario con datos del usuario, debe incluir 'id_conversacion'.

    Condiciones:
        Solo guarda si alguno de los campos clave ('nombre', 'correo', 'empresa', 'necesidad') tiene valor.

    Efectos:
        Actualiza o inserta el documento según 'id_conversacion'.
        Imprime el documento guardado y estado (insertado o actualizado).
    
    Raises:
        RuntimeError: Si la conexión a MongoDB no está inicializada.
    """
    if coleccion_usuarios is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")

    campos_clave = ["nombre", "correo", "empresa", "necesidad"]
    if any(datos_usuario.get(campo) for campo in campos_clave):
        datos_a_guardar = {k: v for k, v in datos_usuario.items() if v not in [None, ""]}

        resultado = coleccion_usuarios.update_one(
            {"id_conversacion": datos_usuario["id_conversacion"]},
            {"$set": datos_a_guardar},
            upsert=True
        )
        doc_guardado = coleccion_usuarios.find_one({"id_conversacion": datos_usuario["id_conversacion"]})

        from bson import ObjectId
        import json

        def convertir_objetos_para_json(obj):
            if isinstance(obj, dict):
                return {k: convertir_objetos_para_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convertir_objetos_para_json(i) for i in obj]
            elif isinstance(obj, ObjectId):
                return str(obj)
            else:
                return obj

        print("📌 Documento guardado en MongoDB (actualizado o insertado):")
        print(json.dumps(convertir_objetos_para_json(doc_guardado), indent=4))

        if resultado.upserted_id:
            print(f"✅ Usuario insertado con _id: {resultado.upserted_id}")
        else:
            print(f"🔄 Usuario ya existía, datos actualizados.")
    else:
        print("⚠️ No se guardó en MongoDB: no hay campos clave con valor.")


def cargar_conversacion(id_conversacion: str):
    """
    Obtiene el historial de una conversación activa.

    Args:
        id_conversacion (str): Identificador único de la conversación.

    Returns:
        list[tuple]: Lista de tuplas (pregunta, respuesta) del historial.
                     Retorna lista vacía si no se encuentra la conversación.

    Raises:
        RuntimeError: Si la conexión a MongoDB no está inicializada.
    """
    if coleccion_conversaciones is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    doc = coleccion_conversaciones.find_one({"id_conversacion": id_conversacion})
    if doc:
        historial = doc.get("historial", [])
        return [tuple(turno) for turno in historial]
    return []


def guardar_conversacion(historial: list, id_conversacion: str):
    """
    Guarda o actualiza el historial de una conversación activa.

    Args:
        historial (list): Lista de tuplas (pregunta, respuesta).
        id_conversacion (str): Identificador único de la conversación.

    Efectos:
        Actualiza o inserta el documento con historial y última modificación.
        Imprime confirmación de guardado.

    Raises:
        RuntimeError: Si la conexión a MongoDB no está inicializada.
    """
    if coleccion_conversaciones is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    historial_serializable = [list(turno) for turno in historial]
    coleccion_conversaciones.update_one(
        {"id_conversacion": id_conversacion},
        {"$set": {
            "historial": historial_serializable,
            "ultima_modificacion": datetime.utcnow()
        }},
        upsert=True
    )
    print(f"💾 Conversación guardada en Mongo con ID: {id_conversacion}")


def mover_a_finalizadas(id_conversacion: str):
    """
    Mueve una conversación de la colección activa a la colección finalizada.

    Args:
        id_conversacion (str): Identificador único de la conversación a mover.

    Efectos:
        Inserta el documento en 'finalizadas' y elimina de 'conversaciones'.
        Imprime confirmación de movimiento.

    Raises:
        RuntimeError: Si la conexión a MongoDB no está inicializada.
    """
    if coleccion_conversaciones is None or coleccion_finalizadas is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    doc = coleccion_conversaciones.find_one({"id_conversacion": id_conversacion})
    if doc:
        coleccion_finalizadas.insert_one(doc)
        coleccion_conversaciones.delete_one({"id_conversacion": id_conversacion})
        print(f"📦 Conversación {id_conversacion} movida a finalizadas")


def existe_conversacion_finalizada(id_conversacion: str):
    """
    Verifica si una conversación ya existe en la colección de finalizadas.

    Args:
        id_conversacion (str): Identificador único de la conversación.

    Returns:
        dict | None: Documento de la conversación si existe, None si no.

    Raises:
        RuntimeError: Si la conexión a MongoDB no está inicializada.
    """
    if coleccion_finalizadas is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    return coleccion_finalizadas.find_one({"id_conversacion": id_conversacion})


def cargar_datos_usuario(id_conversacion: str):
    """
    Carga los datos del usuario asociados a una conversación.

    Args:
        id_conversacion (str): Identificador único de la conversación.

    Returns:
        dict | None: Documento con datos del usuario, o None si no existe.

    Raises:
        RuntimeError: Si la conexión a MongoDB no está inicializada.
    """
    if coleccion_usuarios is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    return coleccion_usuarios.find_one({"id_conversacion": id_conversacion})