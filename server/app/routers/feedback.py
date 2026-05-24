"""用户反馈接口 — POST /api/feedback。

方案文档合规约束 5：用户反馈必须回流，沉淀为数据资产。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import KbPending, UserFeedback
from app.schemas import FeedbackIn, OkOut

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post("/feedback", response_model=OkOut)
def submit_feedback(payload: FeedbackIn, db: Session = Depends(get_db)):
    fb = UserFeedback(
        target_type=payload.target_type,
        target_id=payload.target_id,
        useful=payload.useful,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(fb)
    if payload.comment:
        db.add(KbPending(
            question=f"用户反馈：{payload.target_type or 'unknown'} {payload.target_id or ''}".strip(),
            generated_answer=payload.comment,
            source_urls=[],
            category="用户反馈",
            risk_level="低",
            status="pending",
        ))
    db.commit()
    db.refresh(fb)
    return OkOut(message="感谢反馈，已回流至知识库审核队列", id=fb.id)


@router.get("/feedback/list")
def list_feedback(db: Session = Depends(get_db)):
    rows = db.query(UserFeedback).order_by(UserFeedback.created_at.desc()).limit(50).all()
    return [
        {
            "id": row.id,
            "target_type": row.target_type,
            "target_id": row.target_id,
            "target_label": _target_label(row.target_type, row.target_id),
            "useful": row.useful,
            "rating": row.rating,
            "content": row.comment or "",
            "status": "accepted" if row.handled else "pending",
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


def _target_label(target_type: str | None, target_id: str | None) -> str:
    if target_type == "plan" and target_id:
        return f"攻略方案 · {target_id}"
    if target_type == "answer":
        return "出游助手"
    if target_type == "poi" and target_id:
        return f"地点 · {target_id}"
    return "出游反馈"
