# SQLAlchemy ORM models for KYC data
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


# Application User Account
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("UserRole", back_populates="users")
    kyc_cases = relationship("KYCApplication", back_populates="user")


# Role definition for access control
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), unique=True, nullable=False)

    users = relationship("UserRole", back_populates="roles")


# Join table for many-to-many relationship between users and roles
class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))

    assigned_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="roles")
    roles = relationship("Role", back_populates="users")

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uix_user_role"),
    )

# KYC Application model
class KYCApplication(Base):
    __tablename__ = "kyc_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    case_reference = Column(String(100), unique=True, index=True, nullable=False)
    # Workflow state
    status = Column(String(50), default="pending") # pending / processing / approve/ retry / manual_review / reject
    reason_codes = Column(Text, nullable=True)

    # scores
    face_score = Column(Float, default=0.0)
    liveness_score = Column(Float, default=0.0)
    document_score = Column(Float, default=0.0)
    fraud_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    # Decision metadata
    decision_source = Column(String(50), default="system")  # e.g., "system", "reviewer", "admin"

    model_version = Column(String, nullable=True)

    # Network Signals
    ip_address = Column(String(100), nullable=True)
    device_fingerprint = Column(String(255), nullable=True)

    retry_count = Column(Integer, default=0)

    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="kyc_cases")
    documents = relationship("Document", back_populates="application")
    frauds = relationship("FraudEvent", back_populates="application")
    biometric_sessions = relationship("BiometricSession", back_populates="application")
    decisions = relationship("DecisionLog", back_populates="application")
    reviews = relationship("AdminReview", back_populates="application")


# Document model for storing KYC documents
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("kyc_applications.id"))

    side = Column(String(20), nullable=False)  # e.g., "front", "back"
    document_type = Column(String(50), nullable=False)  # e.g., "passport", "driver_license", "id_card"
    file_path = Column(String(255), nullable=False)  # URL to the stored document
    encrypted_path = Column(String(255), nullable=True)  # URL to the encrypted document (if applicable)

    # extracted_data
    extracted_name = Column(String(255), nullable=True)
    extracted_dob = Column(String(50), nullable=True)
    extracted_id_number = Column(String(100), nullable=True)
    extracted_expiry_date = Column(String(50), nullable=True)

    barcode_data = Column(Text, nullable=True)

    oce_confidence = Column(Float, default=0.0)  # Confidence score for OCR extraction
    authenticity_score = Column(Float, default=0.0)  # Score indicating document authenticity

    is_expired = Column(Boolean, default=False)
    is_tampered = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("KYCApplication", back_populates="documents")


# Biometric session model for storing facial recognition data
class BiometricSession(Base):
    __tablename__ = "biometric_sessions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("kyc_applications.id"))

    session_reference = Column(String(100), unique=True, index=True)
    capture_type = Column(String(50), nullable=False)  # e.g., "selfie", "video", "active_challenge

    selfie_path = Column(String(255), nullable=True) # URL to the stored selfie
    video_path = Column(String(255), nullable=True) # URL to the stored video (if applicable)
    cropped_face_path = Column(String(255), nullable=True)  # URL to the cropped face image (if applicable)

    passive_liveness_score = Column(Float, default=0.0)
    active_liveness_score = Column(Float, default=0.0)
    combined_liveness_score = Column(Float, default=0.0)

    face_match_score = Column(Float, default=0.0)
    challenge_result = Column(Float, default=0.0, nullable=True)  # Score for active challenge performance

    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("KYCApplication", back_populates="biometric_sessions")


# Fraud signal model for storing network and device information
class FraudEvent(Base):
    __tablename__ = "fraud_events"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("kyc_applications.id"), nullable=True)

    ip_address = Column(String(100), nullable=True)
    device_fingerprint = Column(String(255), nullable=True)

    event_type = Column(String(50), nullable=False)  # e.g., "velocity", "device_reuse", "geo_risk", "proxy_detected"
    risk_score = Column(Float, default=0.0)
    event_details = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    application = relationship("KYCApplication", back_populates="fraud_events")


# Decision log model for storing the history of decisions made on a KYC application
class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("kyc_applications.id"))

    decision = Column(String(50))  # e.g., "approve", "reject", "manual_review", "retry"
    reason_codes = Column(Text, nullable=True)

    face_score = Column(Float, default=0.0)
    liveness_score = Column(Float, default=0.0)
    document_score = Column(Float, default=0.0)
    fraud_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    model_version = Column(String(50), nullable=True)  # Version of the model that made the decision

    decided_by = Column(String(50), default="system")  # e.g., "system", "reviewer", "admin"

    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("KYCApplication", back_populates="decisions")


# Admin review model for storing manual reviews of KYC applications
class AdminReview(Base):
    __tablename__ = "admin_reviews"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("kyc_applications.id"))

    reviewer_id = Column(Integer, ForeignKey("users.id"))  # ID of the admin reviewer
    action = Column(String(50))  # e.g., "approve", "reject", "request_more_info"
    notes = Column(Text, nullable=True)

    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("KYCApplication", back_populates="reviews")
    reviewer = relationship("User")


# Audit log model for tracking all actions taken on KYC applications
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, nullable=True)

    action = Column(String(50))  # e.g., "login", "submit_case", "approve_case", "decision_made", "review_performed"

    entity_type = Column(String(50))  # e.g., "KYCApplication", "Document", "BiometricSession", "DecisionLog", "AdminReview"
    entity_id = Column(String, nullable=True)

    ip_address = Column(String(100), nullable=True)

    details = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("KYCApplication", back_populates="audit_logs")
