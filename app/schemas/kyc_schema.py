from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Common / Base Schemas
class MessageResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    total: int
    page: int
    size: int
    total_pages: int


class AdminKYCItemResponse(BaseModel):
    id: int
    case_reference: str
    status: str
    face_score: float
    liveness_score: float
    document_score: float
    fraud_score: float
    overall_score: float
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class PaginatedKYCApplicationsResponse(PaginationResponse):
    items: List[AdminKYCItemResponse]


# AUTHENTICATION SCHEMAS
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    roles: Optional[List[str]] = ["user"]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    roles: List[str]

    class Config:
        from_attributes = True


# Role Schemas
class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class RoleRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# KYC Application Schemas
class CreateKYCCaseRequest(BaseModel):
    country: Optional[str] = None
    document_type: Optional[str] = None


class KYCCaseResponse(BaseModel):
    id: int
    case_reference: str
    status: str
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class KYCDetailResponse(KYCCaseResponse):
    id: int
    case_reference: str
    status: str

    face_score: float
    liveness_score: float
    document_score: float
    fraud_score: float
    overall_score: float

    reason_codes: Optional[str]
    decision_source: Optional[str]
    model_version: Optional[str]

    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    updated_at: datetime
    user: UserResponse
    documents: Optional[List[DocumentResponse]] = None
    biometric_sessions: Optional[List[BiometricSessionResponse]] = None


# Document Schemas
class DocumentUploadResponse(BaseModel):
    document_id: int
    message: str


class DocumentResponse(BaseModel):
    id: int
    side: str
    document_type: Optional[str] = None
    country: Optional[str] = None
    file_path: str

    extracted_name: Optional[str] = None
    extracted_dob: Optional[datetime] = None
    extracted_id_number: Optional[str] = None
    extracted_expiry_date: Optional[datetime] = None

    oce_confidence: float
    authenticity_score: float
    is_expired: bool
    is_tampered: bool

    class Config:
        from_attributes = True


# Biometric / Selfie / Video Schemas
class SelfieUploadResponse(BaseModel):
    session_id: int
    message: str


class VideoUploadResponse(BaseModel):
    session_id: int
    message: str


class BiometricSessionResponse(BaseModel):
    id: int
    session_reference: str
    capture_type: str

    passive_liveness_score: float
    active_liveness_score: float
    combined_liveness_score: float
    face_match_score: float

    challenge_result: Optional[float] = None

    created_at: datetime

    class Config:
        from_attributes = True


#  Verification / Review Schemas
class SubmitVerificationResponse(BaseModel):
    application_id: int
    case_reference: str

    decision: str
    status: str

    reason_codes: Optional[str] = None

    face_score: float
    liveness_score: float
    document_score: float
    fraud_score: float
    overall_score: float

    model_version: Optional[str] = None


class RetryCaseResponse(BaseModel):
    application_id: int
    status: str
    retry_count: int
    message: str


# Admin Review Schemas
class ReviewRequest(BaseModel):
    action: str = Field(..., description="approve / reject / request_retry")
    notes: Optional[str] = None


class ReviewResponse(BaseModel):
    application_id: int
    previous_status: str
    new_status: str
    reviewed_by: str
    notes: Optional[str]
    created_at: datetime


# Search / Filter Schemas
class SearchCasesRequest(BaseModel):
    id_number: Optional[str] = None
    case_reference: Optional[str] = None
    username: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None


class SearchCaseResponse(BaseModel):
    id: int
    case_reference: str
    username: Optional[str]
    status: str
    overall_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# Paginated List Schemas
class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int


class PaginatedKYCResponse(BaseModel):
    meta: PaginationMeta
    items: List[KYCCaseResponse]


class PaginatedSearchResponse(BaseModel):
    meta: PaginationMeta
    items: List[SearchCaseResponse]


# Decion History Schemas
class DecisionLogResponse(BaseModel):
    id: int
    decision: str
    reason_codes: Optional[str]

    face_score: float
    liveness_score: float
    document_score: float
    fraud_score: float
    overall_score: float

    model_version: Optional[str]
    decided_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# Audit Logs
class AuditLogResponse(BaseModel):
    id: int
    actor_user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: str
    ip_address: Optional[str]
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Fraud Detection Schemas
class FraudEventResponse(BaseModel):
    id: int
    event_type: str
    risk_score: float
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Health Check Schemas
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
