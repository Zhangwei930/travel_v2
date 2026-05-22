"""后台审核接口 — 待审核知识列表与审核入库。

方案文档 11.2 审核状态：pending/approved/rejected/needs_update。
请求头需带 X-Admin-Token。
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import FaqKnowledge, KbPending
from app.schemas import KbApproveIn, KbPendingOut, OkOut

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _check_token(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="无效的管理令牌")


@router.get("/kb/pending", response_model=list[KbPendingOut], dependencies=[Depends(_check_token)])
def list_pending(
    status: str = Query(default="pending"),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(KbPending)
        .filter(KbPending.status == status)
        .order_by(KbPending.created_at.desc())
        .all()
    )
    return [
        KbPendingOut(
            id=r.id,
            question=r.question,
            generated_answer=r.generated_answer,
            source_urls=r.source_urls or [],
            city=r.city,
            category=r.category,
            risk_level=r.risk_level,
            status=r.status,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]


@router.post("/kb/approve", response_model=OkOut, dependencies=[Depends(_check_token)])
def approve(payload: KbApproveIn, db: Session = Depends(get_db)):
    pending = db.get(KbPending, payload.id)
    if not pending:
        raise HTTPException(status_code=404, detail="待审核记录不存在")

    pending.status = payload.status
    pending.reviewed_at = datetime.utcnow()

    # 审核通过：同步进正式 FAQ 知识库
    if payload.status == "approved" and pending.question and pending.generated_answer:
        db.add(FaqKnowledge(
            question=pending.question,
            answer=pending.generated_answer,
            category=pending.category or "出游助手",
            city=pending.city,
            keywords=[w for w in pending.question.replace("？", "").split() if w],
            review_status="approved",
        ))

    db.commit()
    return OkOut(message=f"已更新为 {payload.status}", id=pending.id)
