# Authentication and Authorization utilities for the application.
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.kyc_model import User

SECRET = "supersecret"


# Hashes password using bcrypt algorithm.
def hash_password(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


# Check raw password against the hashed password.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


# Creates a JWT token with the given data and an expiration time of 24 hours.
def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(payload, SECRET, algorithm="HS256")


# Validates JWT and extacts claims. Returns the claims if valid, otherwise raises an exception.
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload
    except jwt.JWTError:
        raise Exception("Invalid token")


# Get logged in user with bearer token.
def get_current_user(token: str):
    try:
        payload = decode_access_token(token)
        return payload.get("sub")
    except Exception:
        raise Exception("Could not validate credentials")


# Restricts route access to users with specific roles.
def require_role(token: str, required_role: str):
    user_role = get_current_user(token)
    if user_role != required_role:
        raise Exception("Unauthorized")


# Seeds default admin user if no users exist in the system.
def create_demo_admin():
    db = get_db()
    if db.query(User).count() == 0:
        admin_user = User(
            username="admin",
            password=hash_password("admin123"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
