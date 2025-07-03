from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from api.chat_logic import procesar_chat_simple
from db.mongo import conectar_mongo
from retriever.weaviate_client import conectar_weaviate

app = FastAPI()

# Conectar bases de datos al iniciar la app
@app.on_event("startup")
async def startup_event():
    conectar_mongo()
    conectar_weaviate()

# No necesitas shutdown explícito para cerrar conexiones Mongo/Weaviate si no quieres

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API /chat
class ChatRequest(BaseModel):
    input: str
    id_conversacion: Optional[str] = None

@app.post("/chat")
def chat(request: ChatRequest):
    return procesar_chat_simple(
        query=request.input,
        id_conversacion=request.id_conversacion
    )

# Servir frontend estático
app.mount(
    "/",
    StaticFiles(directory="FrontEnd", html=True),
    name="frontend",
)
