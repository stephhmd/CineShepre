"""
CineSphere API: Fase 1 (health, CORS, logging), Fase 2 (TMDB búsqueda), Fase 3 (persistencia).
"""
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import TMDB_API_KEY
from app.db.database import init_db
from app.routers import recursos
from app.services.tmdb import search_movie_first

# Cargar variables de entorno
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cliente HTTP para TMDB y creación de tablas en arranque."""
    init_db()
    async with httpx.AsyncClient(timeout=10.0) as client:
        app.state.http_client = client
        yield


app = FastAPI(
    title="CineSphere API - Fase 3",
    lifespan=lifespan,
)

# --- CORS SEGURO ---
ORIGEN = os.getenv("ORIGEN_PERMITIDO", "http://127.0.0.1:5500")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGEN],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Logging middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    print(
        f"DEBUG: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"{process_time:.2f}ms"
    )
    return response


# --- Rutas ---
app.include_router(recursos.router)


@app.get("/")
async def root():
    """Health check (Fase 1)."""
    return {
        "status": "online",
        "message": "Servidor Arriba",
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/config")
async def config():
    """Verifica variables de entorno (sin exponer datos sensibles)."""
    return {
        "status": "Running in Staging",
        "port": os.getenv("PORT"),
        "tmdb_key_loaded": bool(TMDB_API_KEY),
        "origen_permitido": ORIGEN,
    }


@app.get("/pelicula/{criterio}")
async def pelicula(criterio: str, request: Request):
    """Búsqueda en TMDB."""
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="TMDB_API_KEY no configurada en .env",
        )
    client = request.app.state.http_client
    result = await search_movie_first(client, criterio)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró ninguna película para: {criterio}",
        )
    return result
