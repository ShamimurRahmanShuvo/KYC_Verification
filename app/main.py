from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, get_engine
from app.core.auth import create_demo_admin

from app.routes.kyc_auth_routes import router as auth_router
from app.routes.kyc_routes import router as kyc_router
from app.routes.kyc_admin_routes import router as admin_router
from app.routes.kyc_health_routes import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="KYC API",
        version="2.0.0",
        description="A simple KYC API built with FastAPI and SQLAlchemy",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    origins = [
        "http://localhost:5137",  # Your current port
        "http://127.0.0.1:5137",  # IP equivalent
        "http://localhost:5173",  # Vite default (just in case)
        "http://localhost:5174",  # Previous Vite port
        "http://127.0.0.1:5174",  # IP equivalent
        "http://localhost:5175",  # Current Vite port
        "http://127.0.0.1:5175",  # IP equivalent
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(kyc_router)
    app.include_router(admin_router)

    @app.on_event("startup")
    def on_startup():
        # Create database tables
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        # Seed default admin user
        create_demo_admin()

    @app.get("/")
    def read_root():
        return {"message": "Welcome to the KYC API!",
                "version": "2.0.0",
                "description": "This API allows you to manage KYC records, authenticate users, "
                               "and perform admin operations.",
                "docs_url": "/docs"}

    return app


app = create_app()
