"""攻略生成接口 — POST /api/trip/generate。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TripGenerateIn, TripPlanOut
from app.services import trip_service

router = APIRouter(prefix="/api", tags=["trip"])


@router.post("/trip/generate", response_model=TripPlanOut)
def generate_trip(payload: TripGenerateIn, db: Session = Depends(get_db)):
    return trip_service.generate_plan(payload, db)
