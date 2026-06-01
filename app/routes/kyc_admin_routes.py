from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.kyc_model import User, Role, UserRole, KYCApplication, Document, AdminReview, AuditLog
from app.schemas.kyc_schema import (
    ReviewRequest,
    ReviewResponse,
    AuditLogResponse,
    KYCDetailResponse,
    PaginatedKYCApplicationsResponse,
    AdminKYCItemResponse,
    AdminUserResponse,
    UserRoleUpdateRequest,
    RoleRequest,
)
from app.core.auth import get_current_user, require_role
from app.services.audit_seervices import log_audit_event
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


@router.post("create-role", response_model=RoleRequest)
def create_role(payload: RoleRequest,
                db: Session = Depends(get_db),
                current_user=Depends(require_role("admin"))):
    existing_role = db.query(Role).filter(Role.name == payload.name).first()
    if existing_role:
        raise HTTPException(400, "Role already exists")

    new_role = Role(name=payload.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return new_role


@router.get("/users", response_model=List[AdminUserResponse])
def list_users(db: Session = Depends(get_db), current_user=Depends(require_role("admin"))):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email if user.email else None,
            "roles": [user_role.roles.name for user_role in user.roles if user_role.roles],
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        for user in users
    ]


@router.patch("/users/{user_id}/roles", response_model=AdminUserResponse)
def update_user_roles(user_id: int,
                      payload: UserRoleUpdateRequest,
                      db: Session = Depends(get_db),
                      current_user=Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.id == current_user.id and "admin" not in payload.roles:
        raise HTTPException(400, "You cannot remove your own admin role")

    desired_roles = set(payload.roles)
    if not desired_roles:
        raise HTTPException(400, "At least one role must be assigned")

    existing_user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    existing_role_names = {user_role.roles.name for user_role in existing_user_roles if user_role.roles}

    role_objects = []
    for role_name in desired_roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.commit()
            db.refresh(role)
        role_objects.append(role)

    current_role_ids = {user_role.role_id for user_role in existing_user_roles}
    desired_role_ids = {role.id for role in role_objects}

    for user_role in existing_user_roles:
        if user_role.role_id not in desired_role_ids:
            db.delete(user_role)

    for role in role_objects:
        if role.id not in current_role_ids:
            db.add(UserRole(user_id=user_id, role_id=role.id))

    db.commit()
    db.refresh(user)

    log_audit_event(
        db,
        action="admin_user_role_update",
        entity_type="User",
        entity_id=str(user_id),
        user_id=current_user.id,
        details={
            "previous_roles": list(existing_role_names),
            "updated_roles": list(desired_roles),
        }
    )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [user_role.roles.name for user_role in user.roles if user_role.roles],
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


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

    if payload.action != "approve":
        raise HTTPException(400, "Invalid action")

    previous_status = kyc.status
    kyc.status = "verified"
    kyc.verified = True
    kyc.review_required = False
    kyc.failure_reason = None
    kyc.reviewed_at = datetime.utcnow()

    review = AdminReview(
        application_id=kyc_id,
        reviewer_id=current_user.id,
        action=payload.action,
        notes=payload.notes,
        previous_status=previous_status,
        new_status=kyc.status,
        # reviewed_by=current_user.username,
        created_at=datetime.utcnow()
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    log_audit_event(
        db,
        action="admin_approve",
        entity_type="KYCApplication",
        entity_id=str(kyc_id),
        user_id=current_user.id,
        details={
            "previous_status": previous_status,
            "new_status": kyc.status,
            "notes": payload.notes,
        }
    )

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

    previous_status = kyc.status

    if payload.action != "reject":
        raise HTTPException(400, "Invalid action")

    kyc.status = "rejected"
    kyc.verified = False
    kyc.review_required = False
    kyc.failure_reason = "Face mismatch"

    kyc.reviewed_at = datetime.utcnow()

    review = AdminReview(
        kyc_application_id=kyc_id,
        reviewer_id=current_user.id,
        action=payload.action,
        notes=payload.notes,
        previous_status=previous_status,
        new_status=kyc.status,
        reviewed_by=current_user.username,
        created_at=datetime.utcnow()
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    log_audit_event(
        db,
        action="admin_reject",
        entity_type="KYCApplication",
        entity_id=str(kyc_id),
        user_id=current_user.id,
        details={
            "previous_status": previous_status,
            "new_status": kyc.status,
            "notes": payload.notes,
        }
    )

    return review


@router.get("/kyc-review-queue", response_model=List[AdminKYCItemResponse])
def get_review_queue(db: Session = Depends(get_db),
                     current_user=Depends(require_role("admin", "reviewer"))):
    queue = db.query(KYCApplication).filter(
        KYCApplication.status == "manual_review"
    ).order_by(KYCApplication.created_at.asc()).all()

    return queue


@router.get("/kyc-applications/{kyc_id}/reviews", response_model=List[ReviewResponse])
def get_kyc_reviews(kyc_id: int,
                    db: Session = Depends(get_db),
                    current_user=Depends(require_role("admin", "reviewer"))):
    reviews = db.query(AdminReview).filter(
        AdminReview.application_id == kyc_id
    ).order_by(AdminReview.created_at.desc()).all()

    return reviews


@router.get("/kyc-applications/{kyc_id}/audit-logs", response_model=List[AuditLogResponse])
def get_kyc_audit_logs(kyc_id: int,
                       db: Session = Depends(get_db),
                       current_user=Depends(require_role("admin", "reviewer"))):
    logs = db.query(AuditLog).filter(
        AuditLog.application_id == kyc_id
    ).order_by(AuditLog.created_at.desc()).all()

    return logs
