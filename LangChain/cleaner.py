"""
Script para limpiar y mover conversaciones inactivas y usuarios antiguos
de las colecciones 'conversaciones' y 'usuarios' a 'finalizadas' y 'usuarios_finalizados'.
"""

import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ La variable de entorno MONGO_URI no está configurada.")

client = MongoClient(MONGO_URI)
db = client["alloxentric"]

coleccion_conversaciones = db["conversaciones"]
coleccion_finalizadas = db["finalizadas"]

coleccion_usuarios = db["usuarios"]
coleccion_usuarios_finalizados = db["usuarios_finalizados"]

LIMITE_MINUTOS = 30
now = datetime.utcnow()
limite_conversaciones = now - timedelta(minutes=LIMITE_MINUTOS)
limite_usuarios = now - timedelta(days=1)  # 1 día para usuarios

# --- Procesar conversaciones inactivas ---
conversaciones_inactivas = coleccion_conversaciones.find({
    "ultima_modificacion": {"$lte": limite_conversaciones}
})

count_conv = coleccion_conversaciones.count_documents({
    "ultima_modificacion": {"$lte": limite_conversaciones}
})

print(f"🔍 Encontradas {count_conv} conversaciones inactivas para mover...")

for doc in conversaciones_inactivas:
    id_conversacion = doc.get("id_conversacion", "<sin id>")
    doc["movido_en"] = now
    coleccion_finalizadas.insert_one(doc)
    coleccion_conversaciones.delete_one({"_id": doc["_id"]})
    print(f"✅ Conversación movida a finalizadas: {id_conversacion}")

# --- Procesar usuarios antiguos (creados hace más de 1 día) ---
usuarios_inactivos = coleccion_usuarios.find({
    "_id": {"$lt": ObjectId.from_datetime(limite_usuarios)}
})

count_usuarios = coleccion_usuarios.count_documents({
    "_id": {"$lt": ObjectId.from_datetime(limite_usuarios)}
})

print(f"🔍 Encontrados {count_usuarios} usuarios antiguos para mover...")

for doc in usuarios_inactivos:
    id_usuario = doc.get("nombre", "<sin nombre>")
    doc["movido_en"] = now
    coleccion_usuarios_finalizados.insert_one(doc)
    coleccion_usuarios.delete_one({"_id": doc["_id"]})
    print(f"✅ Usuario movido a usuarios_finalizados: {id_usuario}")

print("🧹 Limpieza completada.")
