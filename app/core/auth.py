# Authentication and Authorization utilities for the application.
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.kyc_model import User, Role, UserRole


SECRET = "superSecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def normalize_password(password: str) -> str:
    """
    Convert any length password into fixed-length hex string using SHA-256.
    Prevents bcrypt 72-byte limit issues and ensures consistent hashing regardless of input length.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    normalized = normalize_password(password)
    return pwd_context.hash(normalized)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized = normalize_password(plain_password)
    return pwd_context.verify(normalized, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_role(*allowed_roles: str):
    """
    Usages:
    depends(require_role("admin")) - Only allows users with "admin" role
    depends(require_role("admin", "reviewer")) - Allows users with either "admin" or "reviewer" role
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        user_role = getattr(
            current_user,
            "role",
            None
        )

        if user_role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        return current_user

    return role_checker


def create_demo_admin():
    db = next(get_db())

    existing_admin = db.query(User).filter(User.username == "admin").first()

    if existing_admin:
        db.close()
        return

    admin_user = User(
        username="admin",
        email="admin@local.test",
        hashed_password=hash_password("admin123"),
        is_active=True
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    role = db.query(Role).filter(Role.name == "admin").first()

    if not role:
        role = Role(name="admin")
        db.add(role)
        db.commit()
        db.refresh(role)

    mapping = UserRole(
        user_id=admin_user.id,
        role_id=role.id
    )

    db.add(mapping)
    db.commit()
    db.close()
