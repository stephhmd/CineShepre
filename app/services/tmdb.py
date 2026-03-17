"""
Servicio de integración con la API de TMDB.
"""
from typing import Any, Optional

import httpx
from fastapi import HTTPException

from app.core.config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE


def _build_image_url(poster_path: Optional[str]) -> Optional[str]:
    if not poster_path:
        return None
    return f"{TMDB_IMAGE_BASE}{poster_path}"


async def get_movie_by_id(client: httpx.AsyncClient, tmdb_id: int) -> Optional[dict[str, Any]]:
    """
    Obtiene los detalles de una película por ID desde TMDB.
    Devuelve un diccionario listo para guardar en DB o None si no existe/error.
    """
    if not TMDB_API_KEY:
        return None
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = await client.get(url, params=params)
    except (httpx.ConnectError, httpx.TimeoutException):
        return None
    if response.status_code != 200:
        return None
    data = response.json()
    if not data.get("id"):
        return None
    poster_path = data.get("poster_path")
    return {
        "external_id": data["id"],
        "title": data.get("title") or "",
        "media_type": "movie",
        "rating": data.get("vote_average"),
        "release_date": data.get("release_date") or "",
        "image": _build_image_url(poster_path),
        "notas_personales": None,
    }


async def search_movie_first(client: httpx.AsyncClient, criterio: str) -> Optional[dict[str, Any]]:
    """
    Busca una película por criterio y devuelve el primer resultado en formato limpio.
    Usado por GET /pelicula/{criterio}.
    - Devuelve dict si hay resultados.
    - Devuelve None si la respuesta es 200 pero no hay resultados (404).
    - Lanza HTTPException 503 si TMDB no responde; 502 si TMDB devuelve estado distinto de 200.
    """
    if not TMDB_API_KEY:
        return None  # El router devuelve 500
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": criterio}
    try:
        response = await client.get(url, params=params)
    except (httpx.ConnectError, httpx.TimeoutException):
        raise HTTPException(status_code=503, detail="TMDB no disponible o no responde.")
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"TMDB devolvió un estado inesperado: {response.status_code}",
        )
    results = (response.json() or {}).get("results") or []
    if not results:
        return None
    movie = results[0]
    poster_path = movie.get("poster_path")
    return {
        "id": movie.get("id"),
        "title": movie.get("title", ""),
        "media_type": "movie",
        "rating": movie.get("vote_average"),
        "release_date": movie.get("release_date") or "",
        "image": _build_image_url(poster_path),
    }
