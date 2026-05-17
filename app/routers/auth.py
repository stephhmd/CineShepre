import os
from datetime import datetime, timedelta
import hashlib

from fastapi import APIRouter, HTTPException
from jose import jwt

from app.db.database import SessionLocal
from app.db.models import User

router = APIRouter()

# 🔐 SECRET KEY desde .env (Render o local)
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
ALGORITHM = "HS256"


# -----------------------
# HASH SIMPLE (SIN BCRYPT)
# -----------------------
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str):
    return hashlib.sha256(password.encode()).hexdigest() == hashed


# -----------------------
# DB CONNECTION
# -----------------------
def get_db():
    return SessionLocal()


# -----------------------
# REGISTER
# -----------------------
@router.post("/register")
def register(username: str, password: str):
    db = get_db()

    try:
        existing_user = db.query(User).filter(User.username == username).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Usuario ya existe")

        new_user = User(
            username=username,
            password=hash_password(password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "Usuario registrado correctamente"}

    finally:
        db.close()


# -----------------------
# LOGIN
# -----------------------
@router.post("/login")
def login(username: str, password: str):
    db = get_db()

    try:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")

        token = jwt.encode(
            {
                "sub": username,
                "exp": datetime.utcnow() + timedelta(hours=2)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return {"access_token": token}

    finally:
        db.close()