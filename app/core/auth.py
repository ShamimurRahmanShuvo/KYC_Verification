from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET = "supersecret"
pwd=CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd.verify(plain_password, hashed_password)


def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(payload, SECRET, algorithm="HS256")
