from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import SessionLocal
from app.models.kyc_model import KYC
from app.schemas.kyc_schema import AdminReviewRequest

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/review/{kyc_id}")
def review_kyc(kyc_id: int, payload: AdminReviewRequest, db: Session = Depends(get_db)):
    row = db.query(KYC).filter(KYC.id == kyc_id).first()

    if not row:
        raise HTTPException(404, "Record not found")

    if payload.action == "approve":
        row.status = "verified"
        row.verified = True
        row.review_required = False
        row.failure_reason = None

    elif payload.action == "rejected":
        row.status = "rejected"
        row.verified = False
        row.review_required = False
        row.failure_reason = "Face mismatch"

    else:
        raise HTTPException(400, "Invalid action")

    row.admin_notes = payload.notes
    row.reviewed_by = payload.reviewer
    row.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(row)

    return {
        "id": row.id,
        "status": row.status,
        "reviewer": row.reviewed_by
    }


@router.get("/records")
def list_records(db: Session = Depends(get_db)):
    return db.query(KYC).all()
