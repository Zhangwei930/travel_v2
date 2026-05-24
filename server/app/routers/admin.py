"""后台审核接口 — 待审核知识列表与审核入库。

方案文档 11.2 审核状态：pending/approved/rejected/needs_update。
请求头需带 X-Admin-Token。
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import FaqKnowledge, KbPending, SceneGear
from app.schemas import (
    KbApproveIn,
    KbPendingOut,
    OkOut,
    SceneGearOut,
    SceneGearUpdateIn,
)
from app.taxonomy import GEAR_BY_SCENE, SCENES

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


# ─── 场景装备清单（运营可编辑）─────────────────────────────────────

@router.get("/gear", response_model=list[SceneGearOut], dependencies=[Depends(_check_token)])
def list_gear(db: Session = Depends(get_db)):
    """列出所有场景的装备清单，按 SCENES 顺序返回（含 DB 空 → taxonomy 兜底）。"""
    db_rows = {r.scene_id: r for r in db.query(SceneGear).all()}
    out: list[SceneGearOut] = []
    for s in SCENES:
        row = db_rows.get(s["id"])
        items = list(row.items) if (row and row.items) else GEAR_BY_SCENE.get(s["id"], [])
        out.append(SceneGearOut(
            scene_id=s["id"],
            label=s["label"],
            icon=s["icon"],
            items=items,
        ))
    return out


@router.put("/gear/{scene_id}", response_model=OkOut, dependencies=[Depends(_check_token)])
def update_gear(scene_id: str, payload: SceneGearUpdateIn, db: Session = Depends(get_db)):
    """整组覆盖某场景的装备清单。空列表 = 该场景无特定装备。"""
    valid_ids = {s["id"] for s in SCENES}
    if scene_id not in valid_ids:
        raise HTTPException(status_code=400, detail=f"未知场景 id: {scene_id}")

    items = [str(x).strip() for x in payload.items if str(x).strip()]

    row = db.get(SceneGear, scene_id)
    if row:
        row.items = items
        row.updated_at = datetime.utcnow()
    else:
        db.add(SceneGear(scene_id=scene_id, items=items))
    db.commit()
    return OkOut(message=f"{scene_id} 装备清单已更新（{len(items)} 件）")
