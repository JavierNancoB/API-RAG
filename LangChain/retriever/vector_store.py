"""
Módulo para crear una instancia de WeaviateVectorStore configurada
para almacenamiento y búsqueda de vectores de texto.
"""

from langchain_weaviate import WeaviateVectorStore

def create_vectorstore(client, embedding):
    """
    Crea y retorna un objeto WeaviateVectorStore para realizar búsquedas
    vectoriales en el índice 'PdfPage'.

    Args:
        client: Cliente Weaviate previamente inicializado para conexión.
        embedding: Objeto de embeddings que provee vectores para textos.

    Returns:
        WeaviateVectorStore: Instancia configurada para búsqueda vectorial.
    """
    return WeaviateVectorStore(
        client=client,
        index_name="PdfPage",
        text_key="content",
        embedding=embedding,
    )
