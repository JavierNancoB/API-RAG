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
* [📂 Estructura del Proyecto](#-estructura-del-proyecto)
* [🧹 Cleaner: Limpieza de Conversaciones Inactivas](#-cleaner-limpieza-de-conversaciones-inactivas)

## ⚙️ Requisitos Previos

### 🐍 Python

* Python 3.11.9 o superior.

### 🧠 Weaviate (local)

Debes tener **Weaviate corriendo de forma local**, ya sea con Docker o instalado directamente.
Para más informacion respecto a la base de datos Vectorial visitar la [documentación de weaviate](../weaviate_local/Readme.md) de este proyecto.

### 🔑 ENV

Crea un archivo `.env` en la carpeta [LangChain](../LangChain/), en caso de dudas se encuentra el archivo [ejemplo.env](./ejemplo.env):

### Variables definidas en `.env`

| Variable             | Descripción                                        | Ejemplo                      |
| -------------------- | -------------------------------------------------- | ---------------------------- |
| `GROQ_API_KEY`       | Clave API para autenticar con el modelo Groq LLM   | `sk-abcdef1234567890`        |
| `MONGO_URI`          | URI de conexión a la base MongoDB                  | `mongodb://localhost:27017/` |
| `WEAVIATE_PORT`      | Puerto HTTP donde corre el servidor Weaviate local | `8080`                       |
| `WEAVIATE_GRPC_PORT` | Puerto gRPC para comunicación con Weaviate         | `50051`                      |

---

### Cómo crear y usar tu archivo `.env`

1. Copia el archivo de ejemplo `ejemplo.env` en la carpeta `LangChain/` y renómbralo a `.env`.
2. Rellena cada variable con los valores correspondientes a tu entorno.
3. El proyecto carga estas variables automáticamente al iniciar (usando `python-dotenv` o similar).
4. NUNCA subair archivo `.env` a repositorios públicos.
5. Puedes conseguir una clave en [https://console.groq.com](https://console.groq.com).

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

## 🧹 Cleaner: Limpieza de Conversaciones Inactivas

El script `cleaner.py` se encarga de **mover automáticamente las conversaciones inactivas** (que no han sido modificadas en los últimos 30 minutos) desde la colección principal a una colección de respaldo (`finalizadas`) en MongoDB.

Esto permite mantener la base de datos liviana, mejorar el rendimiento del sistema y facilitar la escalabilidad a largo plazo.

---

## ⚙️ Ejecución Manual

Puedes ejecutar el script de forma manual con:

```bash
python cleaner.py
```

---

## 🕒 Automatización en Producción

### 🐧 Linux (con `cron`)

`cron` es el método más común y confiable para programar tareas en entornos Linux.

1. Abre el archivo `crontab` del usuario actual:

   ```bash
   crontab -e
   ```

2. Agrega la siguiente línea para ejecutar el script cada 30 minutos:

   ```bash
   */30 * * * * /ruta/a/tu/entorno/.venv/bin/python /ruta/completa/a/LangChain/cleaner.py
   ```

   > Asegúrate de:
   >
   > * Usar rutas absolutas tanto para el intérprete Python como para el archivo.
   > * Que el entorno virtual esté activado correctamente si lo usas.
   > * Dar permisos de ejecución si es necesario.

---

### 🪟 Windows (con el Programador de tareas)

Windows no tiene `cron`, pero puedes usar el **Programador de tareas** de forma equivalente.

1. Abre el **Programador de tareas**.
2. Crea una nueva **tarea básica**:

   * **Nombre:** `Cleaner LangChain`
   * **Desencadenador:** Cada 30 minutos
   * **Acción:** Iniciar un programa

     * **Programa/script:** `python` (o la ruta completa: `C:\Ruta\a\Python\python.exe`)
     * **Argumentos:** `C:\Ruta\al\proyecto\LangChain\cleaner.py`
3. Guarda y activa la tarea.

> Asegúrate de que:
>
> * Python está correctamente instalado y en el `PATH`, o usa la ruta completa.
> * El script se ejecuta correctamente desde PowerShell o CMD con el mismo comando.
