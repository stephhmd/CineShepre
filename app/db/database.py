"""
Conexión a base de datos usando SQLAlchemy.
Compatible con SQLite (local) y PostgreSQL (producción).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- URL DE BASE DE DATOS ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cinesphere.db")

# --- CONFIGURACIÓN ESPECIAL PARA SQLITE ---
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# --- ENGINE ---
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

# --- SESIÓN ---
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# --- BASE ---
Base = declarative_base()


# --- DEPENDENCIA FASTAPI ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- INICIALIZAR DB ---
def init_db():
    from app.db import models  # evita import circular
    Base.metadata.create_all(bind=engine)