"""
Módulo para gestionar la conexión al servidor local Weaviate,
incluyendo conexión, cierre y acceso al cliente.
"""

import weaviate

client = None

def conectar_weaviate(port=8080, grpc_port=50051):
    """
    Establece la conexión al servidor Weaviate local y asigna el cliente global.

    Args:
        port (int, opcional): Puerto HTTP para la conexión (por defecto 8080).
        grpc_port (int, opcional): Puerto gRPC para la conexión (por defecto 50051).

    Efectos secundarios:
        Inicializa la variable global `client` con el cliente Weaviate conectado.
        Imprime mensaje de confirmación.
    """
    global client
    client = weaviate.connect_to_local(port=port, grpc_port=grpc_port)
    print("🔌 Conectado a Weaviate")


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
