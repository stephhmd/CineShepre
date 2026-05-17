"""
Modelos de datos: Usuarios + MisFavoritos
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint

from app.db.database import Base


# 🔐 MODELO DE USUARIO (LOGIN)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)


# 🎬 MODELO DE FAVORITOS (EL TUYO)
class MisFavoritos(Base):
    """
    Recurso guardado en la lista de favoritos del usuario.
    UNIQUE (id_usuario, external_id, media_type) evita duplicados.
    """
    __tablename__ = "mis_favoritos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(String(255), nullable=False, index=True)
    external_id = Column(Integer, nullable=False)  # TMDB id
    media_type = Column(String(50), nullable=False, default="movie")
    fecha_creacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    notas_personales = Column(String(2000), nullable=True)
    title = Column(String(500), nullable=False)
    rating = Column(Float, nullable=True)
    release_date = Column(String(20), nullable=True)
    image = Column(String(1000), nullable=True)
    user_rating = Column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("id_usuario", "external_id", "media_type", name="uq_usuario_external_media"),
    )
    