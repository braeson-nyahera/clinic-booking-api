from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db

from app.routers.doctors import router as doctors_router
from app.routers.appointments import router as appointments_router
from app.routers.patients import router as patients_router

app = FastAPI(
    title="Clinic Booking API",
    description="REST API for managing clinic appointments.",
    version="0.1.0",
)

app.include_router(doctors_router)
app.include_router(appointments_router)
app.include_router(patients_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Clinic Booking API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable",
        )
