from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )


class KYC(Base):
    __tablename__ = "kyc"

    id = Column(Integer, primary_key=True, index=True)

    # OCR extracted identity info
    full_name = Column(String)
    dob = Column(String)
    id_number = Column(String)
    document_type = Column(String, default="government_id")
    country = Column(String, default="unknown")

    # Upload files
    selfie_path = Column(String)
    id_path = Column(String)

    # Cropped face from id path
    cropped_face_path = Column(String)

    # Verification metrics
    match_score = Column(Float)

    # Flags
    verified = Column(Boolean, default=False)
    liveness_passed = Column(Boolean, default=False)
    review_required = Column(Boolean, default=False)

    # Status tracking
    status = Column(String, default="pending")
    failure_reason = Column(String, nullable=True)

    # Admin review
    admin_notes = Column(String)
    reviewed_by = Column(String)
    reviewed_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
