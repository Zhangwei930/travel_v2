"""出游助手问答接口 — POST /api/kb/ask。"""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AskIn, AskOut
from app.services import kb_service

router = APIRouter(prefix="/api", tags=["kb"])


@router.post("/kb/ask", response_model=AskOut)
def ask(payload: AskIn, db: Session = Depends(get_db)):
    return kb_service.ask(payload, db)


@router.post("/kb/ask_stream")
def ask_stream(payload: AskIn, db: Session = Depends(get_db)):
    result = kb_service.ask(payload, db)

    def line(event: dict) -> str:
        return json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"

    def events():
        yield line({
            "event": "meta",
            "sources": [s.model_dump() for s in result.sources],
            "chips": result.chips,
            "from_kb": result.from_kb,
        })
        yield line({"event": "text", "text": result.text})
        yield line({"event": "done"})

    return StreamingResponse(events(), media_type="application/x-ndjson")
