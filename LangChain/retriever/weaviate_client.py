"""
Módulo para gestionar la conexión al servidor local Weaviate,
incluyendo conexión, cierre y acceso al cliente.
"""

import os
from dotenv import load_dotenv
import weaviate

# Cargar variables de entorno
load_dotenv()

client = None

def conectar_weaviate():
    """
    Establece la conexión al servidor Weaviate local y asigna el cliente global.

    Usa los puertos definidos en el archivo .env:
        - WEAVIATE_PORT (default: 8080)
        - WEAVIATE_GRPC_PORT (default: 50051)

    Efectos secundarios:
        Inicializa la variable global `client` con el cliente Weaviate conectado.
        Imprime mensaje de confirmación.
    """
    global client

    port = int(os.getenv("WEAVIATE_PORT", 8080))
    grpc_port = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))

    client = weaviate.connect_to_local(port=port, grpc_port=grpc_port)
    print(f"🔌 Conectado a Weaviate en puerto HTTP {port} y gRPC {grpc_port}")


def cerrar_weaviate():
    """
    Cierra la conexión con el cliente Weaviate si está activo.

    Efectos secundarios:
        Cierra el cliente global `client` y lo limpia.
        Imprime mensaje de confirmación.
    """
    global client
    if client:
        client.close()
        print("🔒 Conexión a Weaviate cerrada")


def get_client():
    """
    Retorna el cliente Weaviate previamente conectado.

    Returns:
        weaviate.Client: Cliente activo para interactuar con Weaviate.

    Raises:
        RuntimeError: Si no se ha establecido la conexión previamente.
    """
    if not client:
        raise RuntimeError("Cliente Weaviate no conectado. Llama a conectar_weaviate() primero.")
    return client
