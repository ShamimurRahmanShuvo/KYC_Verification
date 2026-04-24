# Enums / Shared constants
from enum import Enum


class DecisionState(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    MANUAL_REVIEW = "manual_review"


class ReasonCodes(Enum):
    SELFIE_BLURRY = "selfie_blurry"
    FACE_MISMATCH = "face_mismatch"
    DOC_EXPIRED = "doc_expired"
    LIVENESS_FAILURE = "liveness_failure"
    OTHER = "other"


class Roles(Enum):
    ADMIN = "admin"
    USER = "user"
    REVIEWER = "reviewer"
    AUDITOR = "auditor"
