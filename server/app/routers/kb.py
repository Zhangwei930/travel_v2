"""出游助手问答接口 — POST /api/kb/ask。"""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AskIn, AskOut, VisionAskIn
from app.services import kb_service
from app.services import vision_service

router = APIRouter(prefix="/api", tags=["kb"])


@router.post("/kb/ask", response_model=AskOut)
def ask(payload: AskIn, db: Session = Depends(get_db)):
    return kb_service.ask(payload, db)


def _ask_stream_response(payload: AskIn, db: Session):
    def line(event: dict) -> str:
        return json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"

    def events():
        for etype, data in kb_service.ask_stream_events(payload, db):
            if etype == "meta":
                yield line({
                    "event": "meta", "sources": [], "chips": [],
                    "from_kb": data.get("from_kb", False),
                    "destinations": [], "routes": [],
                    "kb_status": data.get("kb_status", ""),
                })
            elif etype == "chunk":
                yield line({"event": "chunk", "text": data})
            elif etype == "text":
                yield line({"event": "text", "text": data})
            elif etype == "done":
                yield line({"event": "done"})

    # X-Accel-Buffering=no：让 nginx 等反向代理不缓冲，逐块下发
    return StreamingResponse(
        events(), media_type="application/x-ndjson",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@router.post("/kb/ask_stream")
def ask_stream(payload: AskIn, db: Session = Depends(get_db)):
    return _ask_stream_response(payload, db)


@router.post("/kb/ask_vision", response_model=AskOut)
def ask_vision(payload: VisionAskIn, db: Session = Depends(get_db)):
    return vision_service.ask_vision(payload, db)


@router.post("/consult/ask", response_model=AskOut)
def consult_ask(payload: AskIn, db: Session = Depends(get_db)):
    return ask(payload, db)


@router.post("/consult/ask_stream")
def consult_ask_stream(payload: AskIn, db: Session = Depends(get_db)):
    return _ask_stream_response(payload, db)
