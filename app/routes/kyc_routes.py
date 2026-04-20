from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.kyc_model import KYC
from app.services.storage_services import save_upload
from app.services.face_services import compare_faces
from app.services.ocr_services import extract_kyc_data

router = APIRouter(prefix="/kyc", tags=["KYC"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/verify")
def verify_kyc(
        selfie: UploadFile = File(...),
        id_card: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    selfie_path = save_upload(selfie)
    id_path = save_upload(id_card)

    ocr_data = extract_kyc_data(id_path)

    score = compare_faces(selfie_path, id_path)

    verified = score >= 70

    row = KYC(
        full_name=ocr_data["name"],
        dob=ocr_data["dob"],
        id_number=ocr_data["idn"],
        selfie_path=selfie_path,
        id_path=id_path,
        match_score=score,
        verified=verified
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "kyc_id": row.id,
        "verified": verified,
        "match_score": score,
        "data": ocr_data
    }


@router.get("/records")
def list_records(db: Session = Depends(get_db)):
    return db.query(KYC).all()
