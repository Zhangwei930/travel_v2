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


def _ask_stream_response(payload: AskIn, db: Session):
    result = kb_service.ask(payload, db)

    def line(event: dict) -> str:
        return json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"

    def events():
        yield line({
            "event": "meta",
            "sources": [s.model_dump() for s in result.sources],
            "chips": result.chips,
            "from_kb": result.from_kb,
            "destinations": [d.model_dump() for d in result.destinations],
            "routes": [r.model_dump() for r in result.routes],
            "kb_status": result.kb_status,
        })
        yield line({"event": "text", "text": result.text})
        yield line({"event": "done"})

    return StreamingResponse(events(), media_type="application/x-ndjson")


@router.post("/kb/ask_stream")
def ask_stream(payload: AskIn, db: Session = Depends(get_db)):
    return _ask_stream_response(payload, db)


@router.post("/consult/ask", response_model=AskOut)
def consult_ask(payload: AskIn, db: Session = Depends(get_db)):
    return ask(payload, db)


@router.post("/consult/ask_stream")
def consult_ask_stream(payload: AskIn, db: Session = Depends(get_db)):
    return _ask_stream_response(payload, db)
