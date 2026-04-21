from fastapi import FastAPI
from app.core.database import Base, engine
from app.routes.kyc_routes import router as kyc_router
from app.routes.kyc_admin_routes import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="KYC Verification Service")

app.include_router(kyc_router)
app.include_router(admin_router)
