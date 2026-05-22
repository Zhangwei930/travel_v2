"""请求/响应模型。响应结构与前端 src/api/mock.js 对齐，前端可直接联调。"""
from pydantic import BaseModel, Field


# ---------- 天气 / 场景 ----------
class WeatherOut(BaseModel):
    temp: int
    cond: str
    icon: str
    advice: str
    wind: str


class SceneOut(BaseModel):
    id: str
    no: str
    label: str
    icon: str
    color: str
    desc: str


# ---------- POI ----------
class PoiOut(BaseModel):
    id: int
    no: str
    name: str
    cat: str
    dist: str
    time: str
    budget: str
    tags: list[str]
    img: str
    reason: str


class FitItem(BaseModel):
    icon: str
    label: str
    val: str


class PoiDetailOut(PoiOut):
    suitable_people: list[str] = []
    suitable_weather: list[str] = []
    best_time: str | None = None
    fit_items: list[FitItem] = []
    avoid_tips: list[str] = []
    lat: float | None = None
    lng: float | None = None


# ---------- 路线 ----------
class RouteOut(BaseModel):
    id: int
    no: str
    title: str
    tag: str
    color: str
    duration: str
    budget: str
    poi: int
    img: str
    summary: str


# ---------- 攻略生成 ----------
class TripGenerateIn(BaseModel):
    city: str | None = None
    lat: float | None = None
    lng: float | None = None
    time: str | None = None
    people_type: str | None = None
    budget: str | None = None
    transport: str | None = None
    preferences: list[str] = []
    scene: str | None = None


class PlanStop(BaseModel):
    idx: int
    name: str
    cat: str
    arrive: str
    stay: str
    budget: str
    reason: str
    tip: str
    transport: str
    lat: float | None = None
    lng: float | None = None


class PlanSource(BaseModel):
    kind: str
    t: str


class TripPlanOut(BaseModel):
    no: str
    title: str
    summary: str
    totalBudget: str
    totalTime: str
    people: str
    weather: str
    stops: list[PlanStop]
    gearList: list[str]
    backup: str
    disclaimer: str
    sources: list[PlanSource]


# ---------- 出游助手问答 ----------
class AskIn(BaseModel):
    question: str
    city: str | None = None


class AskSource(BaseModel):
    k: str
    v: str


class AskOut(BaseModel):
    text: str
    sources: list[AskSource]
    chips: list[str] = []
    from_kb: bool = True


# ---------- 反馈 ----------
class FeedbackIn(BaseModel):
    target_type: str | None = None
    target_id: str | None = None
    useful: bool | None = None
    rating: int | None = None
    comment: str | None = None


class OkOut(BaseModel):
    ok: bool = True
    message: str = "已收到"
    id: int | None = None


# ---------- 后台审核 ----------
class KbPendingOut(BaseModel):
    id: int
    question: str | None
    generated_answer: str | None
    source_urls: list[str]
    city: str | None
    category: str | None
    risk_level: str
    status: str
    created_at: str


class KbApproveIn(BaseModel):
    id: int
    status: str = Field(default="approved", description="approved/rejected/needs_update")
    review_note: str | None = None
