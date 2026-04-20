from fastapi import FastAPI
from app.core.database import Base, engine
from app.routes.kyc_routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="KYC Verification Service")

app.include_router(router)
