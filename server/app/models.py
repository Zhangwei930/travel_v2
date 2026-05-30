"""数据库模型 — 对应方案文档第 9 章核心表结构。

数组类字段在 SQLite(本地) 用 JSON，在 PostgreSQL(生产) 用原生 ARRAY/JSONB。
这样同一份模型可兼容本地开发库和生产 schema。
"""
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


TEXT_LIST = JSON().with_variant(ARRAY(String), "postgresql")
INT_LIST = JSON().with_variant(ARRAY(Integer), "postgresql")
JSON_VALUE = JSON().with_variant(JSONB, "postgresql")


def _now() -> datetime:
    return datetime.utcnow()


class PoiIndex(Base):
    """地图 API 地点索引与缓存引用 — 只存必要字段，不永久沉淀完整地图数据。"""

    __tablename__ = "poi_index"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(20), default="stub")  # amap / tencent / stub
    provider_poi_id: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    category: Mapped[str | None] = mapped_column(String(100))
    image: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(50))
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class TravelKnowledge(Base):
    """出游知识 — 标签、推荐理由、避坑提醒，系统的核心资产。"""

    __tablename__ = "travel_knowledge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    poi_id: Mapped[int | None] = mapped_column(ForeignKey("poi_index.id"))
    scene_ids: Mapped[list] = mapped_column(TEXT_LIST, default=list)        # 过滤用：family/couple/rainy...
    scene_tags: Mapped[list] = mapped_column(TEXT_LIST, default=list)       # 展示用：亲子/雨天/文化
    suitable_people: Mapped[list] = mapped_column(TEXT_LIST, default=list)
    suitable_weather: Mapped[list] = mapped_column(TEXT_LIST, default=list)
    recommend_reason: Mapped[str | None] = mapped_column(Text)
    play_duration: Mapped[str | None] = mapped_column(String(50))
    budget_level: Mapped[str | None] = mapped_column(String(50))
    best_time: Mapped[str | None] = mapped_column(String(100))
    avoid_tips: Mapped[str | None] = mapped_column(Text)
    route_suggestion: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(Text)
    display_no: Mapped[str | None] = mapped_column(String(20))         # 索引风角标 NO.001
    content_source: Mapped[str] = mapped_column(String(50), default="人工")  # 人工/AI/WebSearch/用户反馈
    review_status: Mapped[str] = mapped_column(String(20), default="approved")  # pending/approved/rejected
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class TravelRoute(Base):
    """路线模板与线路组合。"""

    __tablename__ = "travel_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str | None] = mapped_column(String(50))
    scene: Mapped[str | None] = mapped_column(String(50))             # 场景 id
    scene_label: Mapped[str | None] = mapped_column(String(50))       # 场景中文标签
    duration: Mapped[str | None] = mapped_column(String(50))
    budget_level: Mapped[str | None] = mapped_column(String(50))
    poi_ids: Mapped[list] = mapped_column(INT_LIST, default=list)
    route_text: Mapped[str | None] = mapped_column(Text)
    tips: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(Text)
    display_no: Mapped[str | None] = mapped_column(String(20))        # R-01
    color: Mapped[str | None] = mapped_column(String(20))
    review_status: Mapped[str] = mapped_column(String(20), default="approved")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class FaqKnowledge(Base):
    """客服 FAQ 与常见问题。"""

    __tablename__ = "faq_knowledge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))          # 门票/停车/天气/会员/推荐逻辑
    city: Mapped[str | None] = mapped_column(String(50))
    keywords: Mapped[list] = mapped_column(TEXT_LIST, default=list)
    review_status: Mapped[str] = mapped_column(String(20), default="approved")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class SearchCache(Base):
    """联网搜索结果缓存 — 短期缓存，设置过期时间。"""

    __tablename__ = "search_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    results: Mapped[list] = mapped_column(JSON_VALUE, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)


class KbPending(Base):
    """待审核知识 — 联网搜索/AI 生成内容必须先入此表，人工审核后再入正式库。"""

    __tablename__ = "kb_pending"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str | None] = mapped_column(Text)
    generated_answer: Mapped[str | None] = mapped_column(Text)
    source_urls: Mapped[list] = mapped_column(TEXT_LIST, default=list)
    city: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[str | None] = mapped_column(String(50))
    risk_level: Mapped[str] = mapped_column(String(20), default="低")  # 低/中/高
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/approved/rejected/needs_update
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)


class UserRequest(Base):
    """用户生成攻略请求记录。"""

    __tablename__ = "user_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str | None] = mapped_column(String(50))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    params: Mapped[dict] = mapped_column(JSON_VALUE, default=dict)
    result: Mapped[dict | None] = mapped_column(JSON_VALUE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class UserFeedback(Base):
    """用户反馈、纠错、评分 — 必须沉淀，形成数据壁垒。"""

    __tablename__ = "user_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_type: Mapped[str | None] = mapped_column(String(30))       # plan/poi/route/answer
    target_id: Mapped[str | None] = mapped_column(String(80))
    useful: Mapped[bool | None] = mapped_column(Boolean)
    rating: Mapped[int | None] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    images: Mapped[str | None] = mapped_column(Text)                  # JSON 列表：截图 base64 data URL
    handled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class EmbeddingChunk(Base):
    """知识库切片与向量索引 — 本地用 JSON 存向量，生产用 pgvector/Qdrant。"""

    __tablename__ = "embedding_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ref_type: Mapped[str | None] = mapped_column(String(30))          # knowledge/route/faq
    ref_id: Mapped[int | None] = mapped_column(Integer)
    content: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list | None] = mapped_column(JSON_VALUE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class SceneGear(Base):
    """场景装备清单 — 运营可在 admin 编辑；trip_service 和 /api/gear/list 共用。

    DB 里没有/空时降级回 app.taxonomy.GEAR_BY_SCENE 兜底常量，保证接口永远有响应。
    """

    __tablename__ = "scene_gear"

    scene_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    items: Mapped[list] = mapped_column(TEXT_LIST, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)
