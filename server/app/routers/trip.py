"""攻略生成接口 — POST /api/trip/generate。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserRequest
from app.schemas import TripGenerateIn, TripPlanOut
from app.services import trip_service

router = APIRouter(prefix="/api", tags=["trip"])


@router.post("/trip/generate", response_model=TripPlanOut)
def generate_trip(payload: TripGenerateIn, db: Session = Depends(get_db)):
    return trip_service.generate_plan(payload, db)


@router.get("/trip/plan", response_model=TripPlanOut)
def get_trip_plan(no: str = Query(...), db: Session = Depends(get_db)):
    rows = db.query(UserRequest).order_by(UserRequest.created_at.desc()).limit(100).all()
    for row in rows:
        result = row.result or {}
        if result.get("no") == no:
            return TripPlanOut(**result)
    raise HTTPException(status_code=404, detail="攻略不存在")
