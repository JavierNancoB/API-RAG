# 🐳 Uso local con Docker Compose

Este proyecto utiliza **Docker Desktop** para levantar un entorno local con **Weaviate**, una base de datos vectorial que almacena y permite hacer búsquedas semánticas de contenido procesado.

El entorno se compone de dos servicios:

* `weaviate`: la base de datos vectorial.
* `loader` *(opcional)*: servicio encargado de cargar datos en Weaviate.

> ⚠️ **Requisitos**: tener instalado [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## 📁 1. Navegar al directorio del entorno

```bash
cd weaviate_local
```

Cargar los .PDF necesarios en la carpeta [PDF](./PDF/), estos archivos seran directamente cargados en la base de datos vectorial. Es importante comprobar que la carpeta tenga los archivos antes de correr la imagen de loader.

---

## 🚀 2. Levantar el stack

1. **Levantar Weaviate:**

```bash
docker-compose -f docker-compose-weaviate.yml up --build -d
```

1. **Levantar el loader (si aplica):**

```bash
docker-compose -f docker-compose-loader.yml up --build -d
```

---

## 🔌 3. Conexión desde LangChain

Dentro de la aplicación principal en Python, la conexión a Weaviate se realiza a través del cliente oficial y del módulo `langchain_weaviate`.

Ejemplo:

```python
from langchain_weaviate import WeaviateVectorStore
import weaviate

client = weaviate.connect_to_local(port=8080, grpc_port=50051)

vectorstore = WeaviateVectorStore(
    client=client,
    index_name="PdfPage",
    text_key="content",
    embedding=mi_embedding
)
```

Esto permite almacenar y consultar vectores desde LangChain directamente sobre Weaviate.

> Las funciones como `conectar_weaviate()` y `get_client()` están disponibles en los módulos auxiliares del proyecto para facilitar esta conexión.

---

## ❗ Problemas conocidos

Si Weaviate queda atascado intentando conectarse a otros nodos o no responde en `http://localhost:8080`, puede deberse a un estado inconsistente del volumen persistente.

Solución:

```bash
docker volume rm weaviate_local_weaviate_data
```

Luego, vuelve a levantar el stack como se explicó arriba.

---

## 🧹 4. Detener y limpiar todo

Para detener y borrar todos los contenedores y volúmenes:

```bash
docker-compose -f docker-compose-weaviate.yml down -v
docker-compose -f docker-compose-loader.yml down -v
```
