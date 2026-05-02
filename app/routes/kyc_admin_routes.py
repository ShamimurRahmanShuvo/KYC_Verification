from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.kyc_model import KYCApplication, Document, AdminReview
from app.schemas.kyc_schema import (
    ReviewRequest,
    ReviewResponse,
    KYCDetailResponse,
    PaginatedKYCApplicationsResponse,
    AdminKYCItemResponse,
)
from app.core.auth import get_current_user, require_role
from app.utils.pagination import paginate_query

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/kyc-applications", response_model=PaginatedKYCApplicationsResponse)
def list_kyc_applications(page: int = Query(1, ge=1),
                          size: int = Query(10, ge=1, le=100),
                          db: Session = Depends(get_db),
                          current_user=Depends(require_role("admin", "reviewer"))):
    query = db.query(KYCApplication).order_by(KYCApplication.created_at.desc())

    items, meta = paginate_query(query, page, size)

    return {
        **meta,
        "items": items
    }


@router.get("/kyc-applications/search", response_model=List[AdminKYCItemResponse])
def search_kyc_applications(status: str = None, id_number: str = None,
                            db: Session = Depends(get_db),
                            current_user=Depends(require_role("admin", "reviewer"))):
    query = db.query(KYCApplication)

    if status:
        query = query.filter(KYCApplication.status == status)

    results = query.all()

    if id_number:
        filtered = []

        for item in results:
            docs = db.query(Document).filter(
                Document.kyc_application_id == item.id
            ).all()

            for doc in docs:
                if doc.id_number == id_number:
                    filtered.append(item)
                    break
        return filtered

    return results


@router.get("/kyc-applications/{kyc_id}", response_model=KYCDetailResponse)
def get_kyc_detail(kyc_id: int,
                   db: Session = Depends(get_db),
                   current_user=Depends(require_role("admin", "reviewer"))):
    kyc = db.query(KYCApplication).filter(
        KYCApplication.id == kyc_id
    ).first()

    if not kyc:
        raise HTTPException(404, "KYC application not found")

    return kyc


@router.post("/kyc-applications/{kyc_id}/approve", response_model=ReviewResponse)
def approve_kyc(kyc_id: int,
                payload: ReviewRequest,
                db: Session = Depends(get_db),
                current_user=Depends(require_role("admin", "reviewer"))):
    kyc = db.query(KYCApplication).filter(
        KYCApplication.id == kyc_id
    ).first()

    if not kyc:
        raise HTTPException(404, "KYC application not found")

    if payload.action == "approve":
        kyc.status = "verified"
        kyc.verified = True
        kyc.review_required = False
        kyc.failure_reason = None

    elif payload.action == "reject":
        kyc.status = "rejected"
        kyc.verified = False
        kyc.review_required = False
        kyc.failure_reason = "Face mismatch"

    else:
        raise HTTPException(400, "Invalid action")

    review = AdminReview(
        kyc_application_id=kyc_id,
        action=payload.action,
        notes=payload.notes,
        reviewed_by=current_user.username,
        reviewed_at=datetime.utcnow()
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.post("/kyc-applications/{kyc_id}/reject", response_model=ReviewResponse)
def reject_kyc(kyc_id: int,
               payload: ReviewRequest,
               db: Session = Depends(get_db),
               current_user=Depends(require_role("admin", "reviewer"))):
    kyc = db.query(KYCApplication).filter(
        KYCApplication.id == kyc_id
    ).first()

    if not kyc:
        raise HTTPException(404, "KYC application not found")

    if payload.action == "approve":
        kyc.status = "verified"
        kyc.verified = True
        kyc.review_required = False
        kyc.failure_reason = None

    elif payload.action == "reject":
        kyc.status = "rejected"
        kyc.verified = False
        kyc.review_required = False
        kyc.failure_reason = "Face mismatch"

    else:
        raise HTTPException(400, "Invalid action")

    review = AdminReview(
        kyc_application_id=kyc_id,
        action=payload.action,
        notes=payload.notes,
        reviewed_by=current_user.username,
        reviewed_at=datetime.utcnow()
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.get("/kyc-review-queue", response_model=List[AdminKYCItemResponse])
def get_review_queue(db: Session = Depends(get_db),
                     current_user=Depends(require_role("admin", "reviewer"))):
    queue = db.query(KYCApplication).filter(
        KYCApplication.status == "manual_review"
    ).order_by(KYCApplication.created_at.asc()).all()

    return queue
