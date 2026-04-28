from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# Common / Base Schemas
class MessageResponse(BaseModel):
    message: str


class PaginationResponse(BaseModel):
    total: int
    page: int
    size: int
    total_pages: int


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
    email: Optional[EmailStr] = None
    roles: List[str]


# Role Schemas
class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class RoleRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)


# KYC Application Schemas
class CreateKYCCaseRequest(BaseModel):
    country: Optional[str] = None
    document_type: Optional[str] = None


class KYCCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_reference: str
    status: str
    retry_count: int
    created_at: datetime


class KYCDetailResponse(KYCCaseResponse):
    model_config = ConfigDict(from_attributes=True)

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


# Document Schemas
class DocumentUploadResponse(BaseModel):
    document_id: int
    message: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    side: str
    document_type: Optional[str] = None
    country: Optional[str] = None

    extracted_name: Optional[str] = None
    extracted_dob: Optional[datetime] = None
    extracted_id_number: Optional[str] = None
    extracted_expiry_date: Optional[datetime] = None


# Biometric / Selfie / Video Schemas
class SelfieUploadResponse(BaseModel):
    session_id: int
    message: str


class VideoUploadResponse(BaseModel):
    session_id: int
    message: str


class BiometricSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_reference: str
    capture_type: str

    passive_liveness_score: float
    active_liveness_score: float
    combined_liveness_score: float
    face_match_score: float

    challenge_result: Optional[str] = None

    created_at: datetime


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_reference: str
    username: Optional[str]
    status: str
    overall_score: float
    created_at: datetime


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
    model_config = ConfigDict(from_attributes=True)

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


# Audit Logs
class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: str
    ip_address: Optional[str]
    details: Optional[str]
    created_at: datetime


# Fraud Detection Schemas
class FraudEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    risk_score: float
    description: Optional[str]
    created_at: datetime


# Health Check Schemas
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
