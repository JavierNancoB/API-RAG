"""
Aplicación FastAPI para gestionar un chatbot con conexión a bases de datos
MongoDB y Weaviate, y servir un frontend estático.

Características:
- Inicializa conexiones a Mongo y Weaviate en el evento startup.
- Expone un endpoint POST /chat para procesar mensajes del usuario.
- Configura middleware CORS para permitir acceso desde cualquier origen.
- Sirve archivos estáticos del directorio FrontEnd.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from api.chat_logic import procesar_chat_simple
from db.mongo import conectar_mongo
from retriever.weaviate_client import conectar_weaviate

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio de la aplicación.
    Conecta a las bases de datos MongoDB y Weaviate.
    """
    conectar_mongo()
    conectar_weaviate()

# Configuración middleware para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    """
    Modelo Pydantic para validar el cuerpo de la petición POST /chat.

    Atributos:
        input (str): Mensaje de entrada del usuario.
        id_conversacion (Optional[str]): Identificador opcional de la conversación.
    """
    input: str
    id_conversacion: Optional[str] = None

@app.post("/chat")
def chat(request: ChatRequest):
    """
    Endpoint para recibir un mensaje del usuario y retornar la respuesta generada.

    Args:
        request (ChatRequest): Objeto con los datos de entrada del usuario.

    Returns:
        dict: Diccionario con la respuesta del chatbot, id de conversación y flag de nueva conversación.
    """
    return procesar_chat_simple(
        query=request.input,
        id_conversacion=request.id_conversacion
    )

# Montar carpeta con frontend estático (HTML, JS, CSS)
app.mount(
    "/",
    StaticFiles(directory="FrontEnd", html=True),
    name="frontend",
)
