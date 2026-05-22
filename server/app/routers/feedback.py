"""用户反馈接口 — POST /api/feedback。

方案文档合规约束 5：用户反馈必须回流，沉淀为数据资产。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserFeedback
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
    db.commit()
    db.refresh(fb)
    return OkOut(message="感谢反馈，已回流至知识库审核队列", id=fb.id)
