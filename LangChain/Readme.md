# 🧠 Sistema de QA con LangChain, Weaviate y Groq

Este proyecto permite realizar preguntas sobre documentos cargados en una base vectorial usando:

* [LangChain](https://www.langchain.com/)
* [Weaviate](https://weaviate.io/) (base vectorial local)
* [Groq](https://groq.com/) (modelo LLM rápido y económico)
* [SentenceTransformers](https://www.sbert.net/) (para embeddings)

---

## 📚 Tabla de Contenidos

* [🔧 Requisitos Previos](#️-requisitos-previos)
* [📦 Instalación de Dependencias](#-instalación-de-dependencias)
* [📄 Descripción del Código](#-descripción-del-código)
* [🧪 Funcionamiento](#-funcionamiento)
* [📂 Estructura del Proyecto](#📁-estructura-del-desarrollo)
* [📝 Licencia](#-licencia)
* [🙋‍♂️ Contribuciones](#️-contribuciones)

## ⚙️ Requisitos Previos

### 🐍 Python

* Python 3.11.9 o superior.

### 🧠 Weaviate (local)

Debes tener **Weaviate corriendo de forma local**, ya sea con Docker o instalado directamente.
Para más informacion respecto a la base de datos Vectorial visitar la [documentación de weaviate](../weaviate_local/Readme.md) de este proyecto.

### 🔑 ENV

Crea un archivo `.env` en la carpeta [LangChain](../LangChain/), en caso de dudas se encuentra el archivo [ejemplo.env](./ejemplo.env):

```env
GROQ_API_KEY=tu_clave_api_de_groq
MONGO_URI=mongodb://localhost:27017/
WEAVIATE_PORT=8080
WEAVIATE_GRPC_PORT=50051
```

Puedes conseguir una clave en [https://console.groq.com](https://console.groq.com).

---

## 📦 Instalación de Dependencias

Crea un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## 📄 Descripción del Código

```python
# 1. Cargar variables de entorno
# 2. Definir clase custom para embeddings con SentenceTransformer
# 3. Conectar a cliente Weaviate local (puertos 8080 / 50051)
# 4. Crear VectorStore con LangChain y Weaviate
# 5. Cargar modelo LLM desde Groq (llama-3.1-8b-instant)
# 6. Crear cadena de QA con RetrievalQA
# 7. Hacer pregunta e imprimir respuesta
# 8. Cerrar cliente al final
```

---

## 🧪 Funcionamiento

```bash
cd .\LangChain\
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Salida esperada:

```bash
INFO:     Application startup complete.
🔌 Conectado a Weaviate en puerto HTTP 8080 y gRPC 50051
INFO:     Application startup complete.
```

## 📁 Estructura del Proyecto

A continuación se muestra la estructura principal del proyecto y el propósito de cada carpeta:

```bash
API_RAG/
├── LangChain/
│ ├── main.py
│ ├── cleaner.py
│ ├── chains/          # Cadenas de procesamiento (LLM + retriever)
│ ├── utils/           # Utilidades generales (guardar_chat.py + json.py)
│ ├── db/              # Conexión y lógica con MongoDB
│ ├── embeddings/      # Lógica de embeddings (SentenceTransformers)
│ ├── llm/             # Carga del modelo desde Groq
│ ├── retriever/       # Configuración del retriever (Weaviate)
│ ├── FrontEnd/        # Interfaz HTML/JS del chatbot
│ ├── config/          # Variables de entorno (ROQ_API_KEY)
│ ├── api/             # Lógica de la API
│ ├── ejemplo.env
├── weaviate_local/
│ ├── docker-compose-weaviate.yml
│ ├── docker-compose-loader.yml
│ ├── ...
└── ..
```

El archivo principal para levantar la API es main.py dentro de LangChain/, y Weaviate debe estar corriendo en Docker.
