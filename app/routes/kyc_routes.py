from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.core.database import SessionLocal
from app.models.kyc_model import KYC
from app.services.storage_services import save_upload
from app.services.face_services import crop_face_from_image, compare_faces
from app.services.liveness_services import check_liveness
from app.services.ocr_services import extract_kyc_data

router = APIRouter(prefix="/kyc", tags=["KYC"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_upload(file):
    path = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


@router.post("/verify")
def verify_kyc(
        selfie: UploadFile = File(...),
        id_card: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    selfie_path = save_upload(selfie)
    id_path = save_upload(id_card)

    # Liveness check
    is_live = check_liveness(selfie_path)

    # OCR
    ocr_data = extract_kyc_data(id_path)

    # Crop face from ID
    cropped_face_path = f"uploads/{uuid.uuid4()}_id_face.jpg"
    crop_face_from_image(id_path, cropped_face_path)

    # Compare selfie vs cropped face
    result = compare_faces(selfie_path, cropped_face_path)

    if not is_live:
        status = "rejected"
        verified = False
        review_required = False
        failure_reason = "Liveness failed"

    elif result["score"] >= 80:
        status = "verified"
        verified = True
        review_required = False
        failure_reason = None

    elif result["score"] >= 70:
        status = "manual_review"
        verified = False
        review_required = True
        failure_reason = "Low confidence match"

    else:
        status = "rejected"
        verified = False
        review_required = False
        failure_reason = "Face mismatch"

    # verified = result["score"] >= 75

    row = KYC(
        full_name=ocr_data["name"],
        dob=ocr_data["dob"],
        id_number=ocr_data["idn"],
        selfie_path=selfie_path,
        id_path=id_path,
        cropped_face_path=cropped_face_path,
        match_score=result["score"],
        verified=verified,
        liveness_passed=is_live,
        review_required=review_required,
        status=status,
        failure_reason=failure_reason
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "kyc_id": row.id,
        "verified": verified,
        "match_score": result["score"],
        "liveness": True,
        "review_required": review_required,
        "status": status,
        "failure_reason": failure_reason,
        "data": ocr_data
    }


@router.get("/{kyc_id}")
def get_kyc_by_id(kyc_id: int, db: Session=Depends(get_db)):
    row = db.query(KYC).filter(KYC.id == kyc_id).first()

    if not row:
        return {"error": f"{kyc_id} not found"}

    return row


@router.get("/queue/manual-review")
def manual_review_queue(db: Session=Depends(get_db)):
    rows = db.query(KYC).filter(
        KYC.status == "manual_review"
    ).all()

    return rows
