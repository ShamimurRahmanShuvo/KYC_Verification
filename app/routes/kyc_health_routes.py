from fastapi import APIRouter, Depends

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "KYC Service"}


@router.get("/ready")
def readiness_check():
    # Here you can add checks for database connectivity, external services, etc.
    return {"status": "ready", "service": "KYC Service"}
