from jose import jwt
from datetime import datetime, timedelta

SECRET = "supersecret"


def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(payload, SECRET, algorithm="HS256")
