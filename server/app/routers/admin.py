"""后台审核接口 — 待审核知识列表与审核入库。

方案文档 11.2 审核状态：pending/approved/rejected/needs_update。
请求头需带 X-Admin-Token。
"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import FaqKnowledge, KbPending, SceneGear
from app.schemas import (
    KbAnalyzeIn,
    KbAnalyzeOut,
    KbApproveIn,
    KbPendingOut,
    OkOut,
    SceneGearOut,
    SceneGearUpdateIn,
)
from app.services import ai_provider
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
    if payload.generated_answer:
        pending.generated_answer = payload.generated_answer.strip()
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


def _heuristic_review(pending: KbPending) -> KbAnalyzeOut:
    answer = (pending.generated_answer or "").strip()
    question = (pending.question or "").strip()
    issues: list[str] = []

    if not answer:
        issues.append("答案为空，需要补充内容")
    if len(answer) < 20:
        issues.append("答案过短，建议补充可执行信息")
    if len(answer) > 180:
        issues.append("答案偏长，建议压缩到 150 字左右")
    if any(word in question + answer for word in ["门票", "票价", "营业", "开放", "限行", "停车费"]) and not any(
        hint in answer for hint in ["以实时", "以官方", "以景区", "以地图"]
    ):
        issues.append("涉及价格、营业或实时信息，需提示以官方或地图实时信息为准")
    if pending.risk_level == "高":
        issues.append("高风险内容不建议自动通过")

    revised = answer
    if revised and "以实时" not in revised and any(word in question + answer for word in ["门票", "票价", "营业", "开放", "限行", "停车费"]):
        revised = revised.rstrip("。") + "，具体以官方或地图实时信息为准。"

    if not answer:
        suggested = "needs_update"
    elif pending.risk_level == "高":
        suggested = "needs_update"
    elif issues:
        suggested = "needs_update"
    else:
        suggested = "approved"

    return KbAnalyzeOut(
        id=pending.id,
        suggested_status=suggested,
        confidence="中" if issues else "高",
        issues=issues or ["未发现明显风险，可进入人工确认"],
        revised_answer=revised or answer,
        provider="rules",
    )


@router.post("/kb/analyze", response_model=KbAnalyzeOut, dependencies=[Depends(_check_token)])
def analyze(payload: KbAnalyzeIn, db: Session = Depends(get_db)):
    pending = db.get(KbPending, payload.id)
    if not pending:
        raise HTTPException(status_code=404, detail="待审核记录不存在")

    analysis = _heuristic_review(pending)
    if not ai_provider.is_live():
        return analysis

    prompt = (
        "你是周密出游知识库审核员。请审核候选问答是否可入库。\n"
        "必须检查：是否编造实时信息、是否需要注明以官方/地图实时信息为准、是否答非所问、是否过长。\n"
        "只输出 JSON，字段：suggested_status(approved/needs_update/rejected), confidence(高/中/低), "
        "issues(字符串数组), revised_answer(修订后答案)。\n\n"
        f"问题：{pending.question or ''}\n"
        f"候选答案：{pending.generated_answer or ''}\n"
        f"城市：{pending.city or ''}\n"
        f"分类：{pending.category or ''}\n"
        f"来源：{', '.join(pending.source_urls or [])}"
    )
    text = ai_provider.generate_text(prompt, fallback="")
    if not text:
        return analysis

    try:
        data = json.loads(text)
    except ValueError:
        return analysis

    suggested = data.get("suggested_status") or analysis.suggested_status
    if suggested not in {"approved", "needs_update", "rejected"}:
        suggested = analysis.suggested_status

    issues = data.get("issues")
    if not isinstance(issues, list) or not issues:
        issues = analysis.issues

    revised = str(data.get("revised_answer") or analysis.revised_answer or "").strip()
    return KbAnalyzeOut(
        id=pending.id,
        suggested_status=suggested,
        confidence=str(data.get("confidence") or analysis.confidence),
        issues=[str(item) for item in issues],
        revised_answer=revised,
        provider="ai",
    )


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
