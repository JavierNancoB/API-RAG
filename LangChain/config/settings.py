"""
Módulo de configuración para cargar variables de entorno.

Este módulo carga automáticamente las variables de entorno definidas
en un archivo `.env` y expone la clave API para el servicio GROQ.

Variables expuestas:
- GROQ_API_KEY (str | None): Clave API para acceder al servicio GROQ,
  obtenida de la variable de entorno "GROQ_API_KEY".

Requiere:
- python-dotenv para cargar variables desde archivo `.env`.
"""

import os
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env al entorno del sistema
load_dotenv()

# Clave API para el servicio GROQ, debe estar definida en las variables de entorno
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
