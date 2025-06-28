# main.py  (o el archivo donde creas la app)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from api.chat_logic import procesar_chat_simple

app = FastAPI()

# ---  CORS  -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # cámbialo si quieres restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---  API /chat  -------------------------------------------
class ChatRequest(BaseModel):
    input: str
    id_conversacion: Optional[str] = None

@app.post("/chat")
def chat(request: ChatRequest):
    return procesar_chat_simple(
        query=request.input,
        id_conversacion=request.id_conversacion
    )

# ---  SERVIR EL FRONTEND  ----------------------------------
# Monta la carpeta FrontEnd en la raíz (“/”)
app.mount(
    "/",  # sirve en la raíz
    StaticFiles(directory="FrontEnd", html=True),
    name="frontend",
)