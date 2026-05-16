from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.user import User

router = APIRouter()

SECRET_KEY = "mi_clave_super_secreta"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    return db


@router.post("/register")
def register(username: str, password: str):
    db: Session = get_db()

    existing_user = db.query(User).filter(User.username == username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    hashed_password = pwd_context.hash(password)

    new_user = User(
        username=username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()

    return {"message": "Usuario registrado correctamente"}


@router.post("/login")
def login(username: str, password: str):
    db: Session = get_db()

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(hours=2)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"token": token}