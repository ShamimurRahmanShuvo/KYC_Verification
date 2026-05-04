from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.kyc_model import User, Role, UserRole, UserProfile
from app.schemas.kyc_schema import (RegisterRequest, LoginRequest, CurrentUserResponse,
                                    TokenResponse, RoleRequest, UserCreateProfileRequest, UserResponse)
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


@router.post("/create-profile", response_model=UserCreateProfileRequest)
def create_user_profile(request: UserCreateProfileRequest,
                        db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    if current_user.id != request.id:
        raise HTTPException(status_code=403, detail="You can only create a profile for yourself")

    existing_user_profile = db.query(UserProfile).filter(UserProfile.id == request.id).first()

    if existing_user_profile:
        existing_user_profile.first_name = request.first_name
        existing_user_profile.last_name = request.last_name
        existing_user_profile.phone_number = request.phone_number
        existing_user_profile.date_of_birth = request.date_of_birth
        existing_user_profile.address = request.address
        existing_user_profile.city = request.city
        existing_user_profile.state = request.state
        existing_user_profile.country = request.country
        existing_user_profile.postal_code = request.postal_code
        db.add(existing_user_profile)
        db.commit()
        db.refresh(existing_user_profile)
        user_profile = existing_user_profile
    else:
        user_profile = UserProfile(
            id=request.id,
            first_name=request.first_name,
            last_name=request.last_name,
            phone_number=request.phone_number,
            date_of_birth=request.date_of_birth,
            address=request.address,
            city=request.city,
            state=request.state,
            country=request.country,
            postal_code=request.postal_code
        )
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)

    return {"message": "Profile created/updated successfully",
            "profile_id": user_profile.id,
            "details": {
                "first_name": user_profile.first_name,
                "last_name": user_profile.last_name,
                "phone_number": user_profile.phone_number,
                "date_of_birth": user_profile.date_of_birth,
                "address": user_profile.address,
                "city": user_profile.city,
                "state": user_profile.state,
                "country": user_profile.country,
                "postal_code": user_profile.postal_code
            }}


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
