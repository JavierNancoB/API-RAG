# 🤖 ChatBot conversacional de ventas Alloxentric - Implementación con LangChain, Weaviate y MongoDB

## 📚 Introducción

Este proyecto implementa un chatbot interactivo para la empresa **Alloxentric**, diseñado para responder preguntas sobre sus servicios y agendar citas. Utiliza **LangChain** para la integración de un modelo de lenguaje, junto con una base de datos **MongoDB** para almacenar la información del usuario y de las conversaciones, y **Weaviate** como cliente de recuperación de información para consultas más detalladas.

La principal funcionalidad del chatbot es ofrecer asistencia en tiempo real, respondiendo a las preguntas de los usuarios y proporcionando la opción de agendar citas. Si el chatbot no tiene información específica sobre una consulta, ofrece la posibilidad de agendar una cita para una consulta más profunda.

### Integrantes del Proyecto

* **Javier Alonso Nanco Becerra**
* **Aranza Sue Díaz Tobar**
* **Nicolás Armando Pozo Villagrán**
* **Josefa Isadora González Rocha**

Este proyecto implementa un **asistente virtual inteligente para Alloxentric**, diseñado para resolver preguntas frecuentes, recuperar información técnica desde documentos PDF y orientar la atención para agendar reuniones.

Combina tecnologías modernas de procesamiento de lenguaje natural y recuperación semántica utilizando:

* **LangChain** como framework principal para construir cadenas conversacionales.
* **Weaviate**, una base de datos vectorial para búsqueda semántica sobre documentos.
* **MongoDB** como sistema de almacenamiento de usuarios y conversaciones.
* **Groq** como proveedor de LLM (modelo de lenguaje rápido y eficiente).

---

## 🧠 ¿Cómo Funciona?

El sistema sigue esta arquitectura general:

```bash
Usuario → Chatbot (LangChain + Groq) → Weaviate (busca info técnica) + MongoDB (almacena conversaciones)
```

1. **Weaviate** indexa contenido de archivos PDF internos, lo que permite al chatbot responder preguntas técnicas con precisión.
2. **LangChain** integra un modelo LLM de Groq para mantener conversaciones naturales.
3. **MongoDB** registra los datos del usuario y guarda el historial para fines de trazabilidad y mejoras futuras.
4. Si no se puede resolver una duda, se ofrece **agendar una cita comercial** de manera automatizada.

---

## 📦 Estructura del Proyecto

```bash
API_RAG/
├── LangChain/         # Lógica del bot, API y procesamiento LLM
├── weaviate_local/    # Archivos y entorno Docker para Weaviate
├── README.md          # ← (Este archivo principal)
```

---

## 📘 Guías de Uso

Este repositorio está dividido en **dos componentes principales**, cada uno con su propia guía:

1. ### 🐳 Entorno Local con Docker y Weaviate

   **Guía detallada para levantar la base vectorial localmente:**
   👉 [Ver documentación aquí](./weaviate_local/Readme.md)

2. ### 🧠 Funcionamiento del Sistema (LangChain, QA y LLM)

   **Guía para instalación, configuración y ejecución del sistema conversacional:**
   👉 [Ver documentación aquí](./LangChain/Readme.md)

---

## 🧪 Ejecución Rápida

Una vez configurado todo el entorno (ver guías anteriores), puedes iniciar la API con:

```bash
cd LangChain/
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## ❓ ¿Dudas o problemas?

Revisa las secciones de problemas conocidos y soluciones en cada README vinculado. Si persisten, asegúrate de:

* Tener Docker Desktop activo y configurado (modo WSL en Windows).
* Haber cargado los archivos PDF correctamente.
* Haber configurado tus variables de entorno en `.env`.
