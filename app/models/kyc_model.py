from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


class KYC(Base):
    __tablename__ = "kyc"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    dob = Column(String)
    id_number = Column(String)

    selfie_path = Column(String)
    id_path = Column(String)

    match_score = Column(Float)
    verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
