"""
Módulo que define una clase personalizada para generar embeddings de texto
usando el modelo preentrenado 'all-MiniLM-L6-v2' de SentenceTransformers.
"""

from sentence_transformers import SentenceTransformer

class CustomEmbedding:
    """
    Clase que encapsula el modelo de SentenceTransformers para generar embeddings
    de texto. Ideal para tareas de búsqueda semántica, recuperación de información
    y sistemas de recomendación.
    """

    def __init__(self):
        """
        Inicializa la clase cargando el modelo 'all-MiniLM-L6-v2'.
        Este modelo balancea velocidad y precisión para tareas de similaridad semántica.
        """
        model = SentenceTransformer('all-MiniLM-L6-v2')
        self.model = model

    def embed_query(self, text):
        """
        Genera el embedding vectorial de una consulta textual.

        Args:
            text (str): Texto o consulta a convertir en embedding.

        Returns:
            list[float]: Vector de características representando el texto.
        """
        return self.model.encode(text).tolist()
