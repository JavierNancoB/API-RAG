"""
Script para limpiar y mover conversaciones inactivas de la colección 'conversaciones'
a la colección 'finalizadas' en MongoDB.

Funciones principales:
- Conectar a la base de datos MongoDB usando variable de entorno.
- Buscar conversaciones activas que no han sido modificadas en los últimos 30 minutos.
- Mover esos documentos a la colección de finalizadas.
- Imprimir el progreso y resumen de la operación.
"""

import os
from pymongo import MongoClient
from datetime import datetime, timedelta

# Leer URI de conexión desde variable de entorno
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ La variable de entorno MONGO_URI no está configurada.")

# Conexión a MongoDB usando variable de entorno
client = MongoClient(MONGO_URI)
db = client["alloxentric"]
coleccion_activas = db["conversaciones"]
coleccion_finalizadas = db["finalizadas"]

# Definición del tiempo límite de inactividad en minutos
LIMITE_MINUTOS = 30

now = datetime.utcnow()
limite = now - timedelta(minutes=LIMITE_MINUTOS)

# Buscar documentos con última_modificacion anterior o igual al límite (inactivos)
inactivas = coleccion_activas.find({
    "ultima_modificacion": {"$lte": limite}
})

count = inactivas.count() if hasattr(inactivas, 'count') else coleccion_activas.count_documents({
    "ultima_modificacion": {"$lte": limite}
})

print(f"🔍 Encontradas {count} conversaciones inactivas para mover...")

for doc in inactivas:
    id_conversacion = doc.get("id_conversacion", "<sin id>")
    doc["movido_en"] = now
    coleccion_finalizadas.insert_one(doc)
    coleccion_activas.delete_one({"_id": doc["_id"]})
    print(f"✅ Movida a finalizadas: {id_conversacion}")

print("🧹 Limpieza completada.")
