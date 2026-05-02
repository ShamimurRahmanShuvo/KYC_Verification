from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.kyc_model import User, Role, UserRole
from app.schemas.kyc_schema import (RegisterRequest, LoginRequest, CurrentUserResponse,
                                    TokenResponse, RoleRequest)
from app.core.auth import get_current_user, hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=CurrentUserResponse)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    for role_name in request.roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.commit()
            db.refresh(role)

        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [user_role.roles.name for user_role in user.roles]
    }


@router.post("/login", response_model=TokenResponse)
def login_user(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")

    stored_hash = getattr(user, "hashed_password", None) or getattr(user, "password_hash")

    if not verify_password(request.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_info(current_user=Depends(get_current_user)):
    roles = [
        x.roles.name for x in current_user.roles
    ]

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "roles": roles
    }


@router.post("/create-role", response_model=RoleRequest)
def create_role(request: RoleRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if "admin" not in [x.roles.name for x in current_user.roles]:
        raise HTTPException(status_code=403, detail="Only admins can create roles")

    existing_role = db.query(Role).filter(Role.name == request.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")

    role = Role(name=request.name)
    db.add(role)
    db.commit()
    db.refresh(role)

    return {"name": role.name}


@router.get("/roles")
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [{"name": role.name} for role in roles]
