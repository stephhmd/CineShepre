"""
Configuración central: variables de entorno y rutas.
La raíz del proyecto es el directorio que contiene la carpeta 'app'.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Cargar .env
_env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_env_path)

# TMDB (SIN valores hardcodeados)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL")
TMDB_IMAGE_BASE = os.getenv("TMDB_IMAGE_BASE")

# Validación (opcional pero pro)
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY no está configurada en el archivo .env")

# Base de datos
DATABASE_PATH = PROJECT_ROOT / "cinesphere.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"