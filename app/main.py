"""
CineSphere API: Fase 1 (health, CORS, logging),
Fase 2 (TMDB búsqueda),
Fase 3 (persistencia + seguridad).
"""

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import TMDB_API_KEY
from app.db.database import init_db
from app.routers import recursos
from app.services.tmdb import search_movie_first

# --- CARGAR VARIABLES ---
load_dotenv()

API_KEY = os.getenv("API_SECRET_KEY")
ORIGEN = os.getenv("ORIGEN_PERMITIDO", "http://localhost")


# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cliente HTTP para TMDB y creación de tablas en arranque."""
    init_db()
    async with httpx.AsyncClient(timeout=10.0) as client:
        app.state.http_client = client
        yield


# --- APP PRINCIPAL ---
app = FastAPI(
    title="CineSphere API - Fase 4",
    lifespan=lifespan,
)


# --- CORS CONFIGURADO ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- LOGGING ---
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


# --- ENDPOINT PROTEGIDO ---
@app.post("/favoritos")
async def guardar_favorito(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Firma no válida")

    return {"mensaje": "Guardado correctamente"}


# --- RUTAS ---
app.include_router(recursos.router)


# --- HEALTH CHECK ---
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Servidor Arriba",
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


# --- CONFIG ---
@app.get("/config")
async def config():
    return {
        "status": "Running",
        "port": os.getenv("PORT"),
        "tmdb_key_loaded": bool(TMDB_API_KEY),
        "origen_permitido": ORIGEN,
    }


# --- TMDB ---
@app.get("/pelicula/{criterio}")
async def pelicula(criterio: str, request: Request):
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

    from app.routers import auth
    app.include_router(auth.router)