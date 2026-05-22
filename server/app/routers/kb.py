"""出游助手问答接口 — POST /api/kb/ask。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AskIn, AskOut
from app.services import kb_service

router = APIRouter(prefix="/api", tags=["kb"])


@router.post("/kb/ask", response_model=AskOut)
def ask(payload: AskIn, db: Session = Depends(get_db)):
    return kb_service.ask(payload, db)
