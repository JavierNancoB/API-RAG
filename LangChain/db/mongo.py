from pymongo import MongoClient
from datetime import datetime

client = None
db = None
coleccion_usuarios = None
coleccion_conversaciones = None
coleccion_finalizadas = None

def conectar_mongo(uri="mongodb://localhost:27017/", db_name="alloxentric"):
    global client, db, coleccion_usuarios, coleccion_conversaciones, coleccion_finalizadas
    client = MongoClient(uri)
    db = client[db_name]
    coleccion_usuarios = db["usuarios"]
    coleccion_conversaciones = db["conversaciones"]
    coleccion_finalizadas = db["finalizadas"]
    print("🔌 Conectado a MongoDB")

def cerrar_mongo():
    global client
    if client:
        client.close()
        print("🔒 Conexión a MongoDB cerrada")

def guardar_usuario(datos_usuario: dict):
    if coleccion_usuarios is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    
    # Guardar si al menos un campo está presente
    campos_clave = ["nombre", "correo", "empresa", "necesidad"]
    if any(datos_usuario.get(campo) for campo in campos_clave):
        # Solo actualizar los campos que no sean None ni vacíos
        datos_a_guardar = {k: v for k, v in datos_usuario.items() if v not in [None, ""]}

        resultado = coleccion_usuarios.update_one(
            {"id_conversacion": datos_usuario["id_conversacion"]},  # clave única
            {"$set": datos_a_guardar},
            upsert=True
        )
        # Imprimir el documento actualizado/inserto para debug
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
    if coleccion_conversaciones is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    doc = coleccion_conversaciones.find_one({"id_conversacion": id_conversacion})
    if doc:
        historial = doc.get("historial", [])
        return [tuple(turno) for turno in historial]
    return []

def guardar_conversacion(historial: list, id_conversacion: str):
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
    if coleccion_conversaciones is None or coleccion_finalizadas is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    doc = coleccion_conversaciones.find_one({"id_conversacion": id_conversacion})
    if doc:
        coleccion_finalizadas.insert_one(doc)
        coleccion_conversaciones.delete_one({"id_conversacion": id_conversacion})
        print(f"📦 Conversación {id_conversacion} movida a finalizadas")

def existe_conversacion_finalizada(id_conversacion: str):
    if coleccion_finalizadas is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    return coleccion_finalizadas.find_one({"id_conversacion": id_conversacion})

def cargar_datos_usuario(id_conversacion: str):
    if coleccion_usuarios is None:
        raise RuntimeError("No hay conexión a MongoDB. Llama a conectar_mongo() primero.")
    return coleccion_usuarios.find_one({"id_conversacion": id_conversacion})
