import weaviate

client = None

def conectar_weaviate(port=8080, grpc_port=50051):
    global client
    client = weaviate.connect_to_local(port=port, grpc_port=grpc_port)
    print("🔌 Conectado a Weaviate")

def cerrar_weaviate():
    global client
    if client:
        client.close()
        print("🔒 Conexión a Weaviate cerrada")

def get_client():
    if not client:
        raise RuntimeError("Cliente Weaviate no conectado. Llama a conectar_weaviate() primero.")
    return client
