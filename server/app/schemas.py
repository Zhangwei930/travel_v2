"""请求/响应模型。响应结构与前端 API 客户端契约保持一致。"""
from pydantic import BaseModel, Field


# ---------- 天气 / 场景 ----------
class WeatherOut(BaseModel):
    temp: int
    cond: str
    icon: str
    advice: str
    wind: str
    source: str = "stub"


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
    lat: float | None = None      # 供前端无照片时拼 /api/poi/map-thumb 定位图
    lng: float | None = None


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


# ---------- 定位首页 ----------
class LocationOut(BaseModel):
    city: str
    lat: float
    lng: float
    landmark: str | None = None


class HomeEntryOut(BaseModel):
    id: str
    title: str


class RecommendPoiOut(BaseModel):
    id: int | str
    name: str
    category: str | None = None
    address: str | None = None
    distance: str
    drive_time: str | None = None
    score: int = 0
    reason: str = ""
    tags: list[str] = Field(default_factory=list)
    kb_status: str = "miss"
    source: str = "amap"
    lat: float | None = None
    lng: float | None = None
    nav_ready: bool = False
    img: str | None = None


class RouteStopOut(BaseModel):
    id: int | str | None = None
    name: str
    distance: str | None = None
    reason: str = ""
    lat: float | None = None
    lng: float | None = None


class RouteCardOut(BaseModel):
    id: str | int
    title: str
    duration: str
    budget: str | None = None
    scene: str | None = None
    summary: str = ""
    stops: list[RouteStopOut] = Field(default_factory=list)
    nav_ready: bool = False


class HomeFeedOut(BaseModel):
    location: LocationOut
    weather: WeatherOut | None = None
    entries: list[HomeEntryOut]
    scene_index: list[SceneOut]
    nearby_now: list[RecommendPoiOut]
    routes: list[RouteCardOut]
    assistant_chips: list[str]


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
class ChatTurn(BaseModel):
    role: str = Field(description="user / bot")
    text: str


class AskIn(BaseModel):
    question: str
    city: str | None = None
    lat: float | None = None
    lng: float | None = None
    scene: str | None = None
    intent: str | None = None
    weather: str | None = None
    context: str | None = Field(default=None, description="（兼容旧字段）上一条用户问题")
    history: list[ChatTurn] = Field(default_factory=list, description="最近 N 轮对话，建议传 4-6 条")


class VisionAskIn(BaseModel):
    image_base64: str
    city: str | None = None
    lat: float | None = None
    lng: float | None = None


class AskSource(BaseModel):
    k: str
    v: str


class AskOut(BaseModel):
    text: str
    sources: list[AskSource]
    chips: list[str] = []
    from_kb: bool = True
    destinations: list[RecommendPoiOut] = Field(default_factory=list)
    routes: list[RouteCardOut] = Field(default_factory=list)
    kb_status: str = "hit"


# ---------- 反馈 ----------
class FeedbackIn(BaseModel):
    target_type: str | None = None
    target_id: str | None = None
    useful: bool | None = None
    rating: int | None = None
    comment: str | None = None
    images: list[str] | None = None      # 截图 base64 data URL 列表


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
    generated_answer: str | None = None


class KbAnalyzeIn(BaseModel):
    id: int


class KbAnalyzeOut(BaseModel):
    id: int
    suggested_status: str
    confidence: str
    issues: list[str]
    revised_answer: str
    provider: str


class SceneGearOut(BaseModel):
    scene_id: str
    label: str       # 场景中文名 from taxonomy
    icon: str
    items: list[str]


class SceneGearUpdateIn(BaseModel):
    items: list[str] = Field(default_factory=list, description="完整覆盖该场景的装备清单")
