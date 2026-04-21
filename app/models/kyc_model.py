from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


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
