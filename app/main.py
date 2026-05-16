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
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import TMDB_API_KEY
from app.db.database import init_db
from app.routers import recursos, auth
from app.services.tmdb import search_movie_first

# --- CARGAR VARIABLES ---
load_dotenv()


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


# 🔥 CORS CORRECTO PARA DESARROLLO
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


# --- RUTAS ---
app.include_router(recursos.router)
app.include_router(auth.router)


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