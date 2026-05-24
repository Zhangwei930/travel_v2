"""按场景返回装备清单。

数据源优先级：
1. `scene_gear` 表（运营可编辑，立即生效）
2. `app.taxonomy.GEAR_BY_SCENE` 兜底常量（保证 DB 空 / 新场景不报错）

合规约束：装备清单是知识库内容（人工维护），不属于实时数据，可放心返回。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SceneGear
from app.taxonomy import GEAR_BY_SCENE

router = APIRouter(prefix="/api", tags=["gear"])


@router.get("/gear/list", response_model=list[str])
def gear_list(
    scene: str = Query(default="", description="场景 id，如 fish/family"),
    db: Session = Depends(get_db),
):
    if scene:
        row = db.query(SceneGear).filter(SceneGear.scene_id == scene).first()
        if row and row.items:
            return list(row.items)
    return GEAR_BY_SCENE.get(scene, [])
