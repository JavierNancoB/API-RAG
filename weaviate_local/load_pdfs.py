import fitz  # PyMuPDF
import os
import weaviate
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import Filter

# ----------- FUNCIONES -----------

def extract_texts_from_folder(folder_path):
    """
    Extrae texto de todos los PDFs en una carpeta dada.
    Retorna un diccionario: nombre_archivo -> lista de páginas (texto).
    """
    pdf_texts = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(folder_path, filename)
            try:
                doc = fitz.open(full_path)
                pages = [page.get_text().strip() for page in doc if page.get_text().strip()]
                pdf_texts[filename] = pages
            except Exception as e:
                print(f"❌ Error procesando {filename}: {e}", flush=True)
    return pdf_texts

# ----------- EJECUCIÓN PRINCIPAL -----------

def main():
    pdf_folder = "PDF"
    pdf_text_data = extract_texts_from_folder(pdf_folder)

    print("✅ Textos extraídos de los PDF:", flush=True)
    for nombre, paginas in pdf_text_data.items():
        print(f"{nombre} - {len(paginas)} páginas", flush=True)
        print(paginas[0][:300], flush=True)
        break

    # Lee host y puerto de variables de entorno, usa valores por defecto si no existen
    host = os.getenv("WEAVIATE_HOST", "weaviate")
    port = int(os.getenv("WEAVIATE_PORT", "8080"))

    with weaviate.connect_to_custom(
        http_host=host,
        http_port=port,
        grpc_host=host,
        grpc_port=50051,
        http_secure=False,
        grpc_secure=False,
    ) as client:

        # Verifica existencia antes de eliminar
        if "PdfPage" in [c.name for c in client.collections.list_all()]:
            client.collections.delete("PdfPage")

        client.collections.create(
            name="PdfPage",
            properties=[
                Property(name="content", data_type=DataType.TEXT),
                Property(name="source", data_type=DataType.TEXT),
                Property(name="page_number", data_type=DataType.INT)
            ]
        )
        print("✅ Colección 'PdfPage' creada correctamente.", flush=True)

        collection = client.collections.get("PdfPage")

        for nombre_archivo, paginas in pdf_text_data.items():
            for i, texto in enumerate(paginas):
                collection.data.insert({
                    "content": texto,
                    "source": nombre_archivo,
                    "page_number": i + 1
                })

        print("📚 Todos los PDFs fueron cargados correctamente.", flush=True)

        # Consultar con filtro
        palabra_clave = "cliente"
        filtro = Filter.by_property("content").like(f"*{palabra_clave}*")
        resultados = collection.query.fetch_objects(filters=filtro, limit=5)

        print("\n🔍 Resultados de la búsqueda:\n", flush=True)
        for obj in resultados.objects:
            print(f"{obj.properties['source']} (Página {obj.properties['page_number']}):", flush=True)
            print(obj.properties['content'][:1000], "\n---\n", flush=True)

if __name__ == "__main__":
    main()
