from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.kyc_model import KYCApplication, Document, BiometricSession
from app.schemas.kyc_schema import CreateKYCCaseRequest, KYCCaseResponse, DocumentUploadResponse
from app.services.storage_services import save_uploads
from app.services.capture_quality_services import validate_selfie_quality, validate_document_quality
from app.services.document_services import process_front_document, process_back_document
from app.services.face_services import generate_face_score
from app.services.liveness_services import combined_liveness_score
from app.services.fraud_services import calculate_fraud_score
from app.services.decision_services import evaluate_case
from app.utils.case_reference import generate_case_reference

router = APIRouter(prefix="/kyc", tags=["KYC"])


@router.post("/create-kyc", response_model=KYCCaseResponse)
def create_kyc_case(request: CreateKYCCaseRequest, current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    kyc_case = KYCApplication(
        user_id=current_user.id,
        status="pending",
        case_reference=generate_case_reference(),
        decision_source="system",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(kyc_case)
    db.commit()
    db.refresh(kyc_case)

    return kyc_case


@router.post("/{kyc_id}/upload-document/front-id", response_model=DocumentUploadResponse)
def upload_front_id(kyc_id: int, file: UploadFile = File(...), document_type: str = "front_id",
                    current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    path = save_uploads(file, f"kyc/{kyc_id}/front_id")

    ok, message = validate_document_quality(path)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Document quality issue: {message}")

    extracted_data = process_front_document(path)
    print(f"Extracted data from front ID: {extracted_data}")

    doc = Document(
        application_id=kyc_id,
        side="front_id",
        document_type=document_type,
        file_path=path,
        created_at=datetime.utcnow()
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return DocumentUploadResponse(document_id=doc.id,
                                  message="Front ID uploaded and processed successfully")


@router.post("/{kyc_id}/upload-document/back-id", response_model=DocumentUploadResponse)
def upload_back_id(kyc_id: int, file: UploadFile = File(...), document_type: str = "back_id",
                   current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    path = save_uploads(file, f"kyc/{kyc_id}/back_id")

    ok, message = validate_document_quality(path)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Document quality issue: {message}")

    extracted_data = process_back_document(path)
    print(f"Extracted data from back ID: {extracted_data}")

    doc = Document(
        application_id=kyc_id,
        side="back_id",
        document_type=document_type,
        file_path=path,
        created_at=datetime.utcnow()
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return DocumentUploadResponse(document_id=doc.id,
                                  message="Back ID uploaded and processed successfully")


@router.post("/{kyc_id}/upload-selfie", response_model=DocumentUploadResponse)
def upload_selfie(kyc_id: int, file: UploadFile = File(...),
                   current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    path = save_uploads(file, f"kyc/{kyc_id}/selfie")

    ok, message = validate_selfie_quality(path)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Selfie quality issue: {message}")

    bio = BiometricSession(
        application_id=kyc_id,
        session_reference=str(uuid4()),
        capture_type="selfie",
        selfie_path=path,
        created_at=datetime.utcnow()
    )

    db.add(bio)
    db.commit()
    db.refresh(bio)

    return DocumentUploadResponse(document_id=bio.id, message="Selfie uploaded and processed successfully")


@router.post("/{kyc_id}/evaluate")
def evaluate_kyc_case(kyc_id: int, request: Request, db: Session = Depends(get_db)):
    kyc_case = db.query(KYCApplication).filter(KYCApplication.id == kyc_id).first()

    if not kyc_case:
        raise HTTPException(status_code=404, detail="KYC case not found")

    document = db.query(Document).filter(
        Document.application_id == kyc_id,
        Document.document_type == "front_id").first()

    selfie = db.query(BiometricSession).filter(BiometricSession.application_id == kyc_id,
                                               BiometricSession.capture_type == "selfie"
                                               ).first()
    video = db.query(BiometricSession).filter(BiometricSession.application_id == kyc_id,
                                              BiometricSession.capture_type == "video").first()

    if not document or not selfie:
        raise HTTPException(status_code=400, detail="Missing required documents or selfie for evaluation")

    face = generate_face_score(selfie.selfie_path, document.file_path)
    liveness_score = combined_liveness_score(selfie.selfie_path, video.video_path if video else None)
    fraud_score = calculate_fraud_score(ip_address=request.client.host,
                                        device_id=request.headers.get("X-Device-ID", "unknown"),
                                        location=request.headers.get("X-Location", "unknown"))
    doc_score = 90.0  # Placeholder for document authenticity score

    result = evaluate_case(face, liveness_score, doc_score, fraud_score)

    kyc_case.face_score = face
    kyc_case.liveness_score = liveness_score
    kyc_case.document_score = doc_score
    kyc_case.fraud_score = fraud_score
    kyc_case.overall_score = result["overall_score"]
    kyc_case.status = result["decision_state"]
    kyc_case.reason_code = result["reason_codes"]
    kyc_case.submitted_at = datetime.utcnow()

    db.commit()

    return result


@router.get("/{kyc_id}")
def get_kyc_by_id(kyc_id: int, db: Session=Depends(get_db)):
    row = db.query(KYCApplication).filter(KYCApplication.id == kyc_id).first()

    if not row:
        raise HTTPException(status_code=404, detail=f"KYC case no {kyc_id} not found")

    return row


@router.post("/{kyc_id}/retry}")
def retry_kyc_evaluation(kyc_id: int, db: Session=Depends(get_db)):
    kyc_case = db.query(KYCApplication).filter(KYCApplication.id == kyc_id).first()

    if not kyc_case:
        raise HTTPException(status_code=404, detail=f"KYC case no {kyc_id} not found")

    kyc_case.retry_count += 1
    kyc_case.status = "pending"
    db.commit()

    return {"message": f"KYC case {kyc_id} marked for retry. Current retry count: {kyc_case.retry_count}"}


@router.get("/queue/manual-review")
def manual_review_queue(db: Session=Depends(get_db)):
    rows = db.query(KYCApplication).filter(
        KYCApplication.status == "manual_review"
    ).all()

    return rows
