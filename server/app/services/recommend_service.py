"""Simple scoring for nearby destination cards."""
import re
from datetime import datetime

from app.models import PoiIndex, TravelKnowledge
from app.schemas import RecommendPoiOut, WeatherOut
from app.services import map_provider
from app.services.kb_resolver import resolve_kb_status
from app.taxonomy import SCENE_LABELS


SCENE_KEYWORDS: dict[str, list[str]] = {
    "family": ["亲子", "公园", "科技馆", "博物馆", "儿童", "乐园"],
    "couple": ["情侣", "咖啡", "夜景", "公园", "商圈"],
    "rainy": ["室内", "商场", "博物馆", "美术馆", "科技馆", "购物"],
    "budget": ["免费", "公园", "街区", "Citywalk", "低预算"],
    "fish": ["钓鱼", "水库", "河边", "垂钓"],
    "photo": ["拍照", "地标", "老街", "公园", "夜景"],
    "night": ["夜游", "夜市", "商圈", "步行街", "灯光"],
    "walk": ["Citywalk", "步行", "老街", "街区", "公园"],
    "old": ["适老", "公园", "平路", "休闲", "轻量"],
    "hike": ["登山", "山", "徒步", "爬山", "景区", "森林"],
    "food": ["美食", "火锅", "餐厅", "小吃", "川菜", "馆子"],
    "cycle": ["绿道", "骑行", "自行车", "环湖", "江滩", "郊野"],
    "camp": ["露营", "营地", "帐篷", "野餐", "草坪", "户外"],
}

INDOOR_KEYWORDS = ["室内", "商场", "博物馆", "美术馆", "科技馆", "购物"]
OUTDOOR_KEYWORDS = ["公园", "水库", "河边", "登高", "露营", "户外"]
NIGHT_KEYWORDS = ["夜游", "夜市", "夜景", "商圈", "步行街", "灯光"]


def _join_text(poi: PoiIndex, kn: TravelKnowledge | None) -> str:
    parts = [
        poi.name,
        poi.category or "",
        " ".join(poi.category.split("·")) if poi.category else "",
        " ".join(kn.scene_tags or []) if kn else "",
        kn.recommend_reason or "" if kn else "",
    ]
    return " ".join(parts)


def _distance_score(km: float) -> int:
    if km <= 1:
        return 30
    if km <= 3:
        return 25
    if km <= 5:
        return 15
    if km <= 10:
        return 5
    return -10


def _time_slot(now: datetime | None = None) -> str:
    hour = (now or datetime.now()).hour
    if 5 <= hour < 11:
        return "上午"
    if 11 <= hour < 17:
        return "下午"
    if 17 <= hour < 22:
        return "晚上"
    return "夜间"


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(k in text for k in keywords)


def score_poi(
    poi: PoiIndex,
    kn: TravelKnowledge | None,
    origin: tuple[float, float],
    scene: str | None = None,
    weather: WeatherOut | None = None,
    now: datetime | None = None,
) -> RecommendPoiOut | None:
    if poi.lat is None or poi.lng is None:
        return None

    km = map_provider.haversine_km(origin[0], origin[1], poi.lat, poi.lng)
    score = _distance_score(km)
    text = _join_text(poi, kn)
    tags: list[str] = []

    if scene:
        scene_keywords = SCENE_KEYWORDS.get(scene, [])
        if _contains_any(text, scene_keywords) or (kn and scene in (kn.scene_ids or [])):
            score += 25
            tags.append(SCENE_LABELS.get(scene, scene))

    for tag in (kn.scene_tags if kn else []) or []:
        if tag not in tags:
            tags.append(tag)

    slot = _time_slot(now)
    if slot in ("晚上", "夜间"):
        if _contains_any(text, NIGHT_KEYWORDS):
            score += 30
            tags.append("夜间适合")
        elif _contains_any(text, ["博物馆", "科技馆"]):
            score -= 10
    elif kn and kn.best_time and slot in kn.best_time:
        score += 10
        tags.append(f"{slot}适合")

    if weather and weather.cond in ("雨", "雪"):
        if _contains_any(text, INDOOR_KEYWORDS):
            score += 30
            tags.append("雨天友好")
        elif _contains_any(text, OUTDOOR_KEYWORDS):
            score -= 30
    elif weather:
        tags.append(weather.advice)

    if kn and (kn.budget_level or "") in ("免费", "低", "低预算"):
        score += 10
        tags.append(kn.budget_level)

    kb_status = resolve_kb_status(kn)
    score += {"hit": 15, "unchanged": 15, "partial": 5, "stale": 0, "miss": -5}.get(kb_status, 0)

    if km <= 1 and "近距离" not in tags:
        tags.insert(0, "近距离")

    reason = (kn.recommend_reason if kn else None) or poi.address or "附近可导航地点"
    if scene and SCENE_LABELS.get(scene) and SCENE_LABELS[scene] not in reason:
        reason = f"{reason}，匹配{SCENE_LABELS[scene]}需求"

    # 仅下发真实照片；无照片时留空，前端走 /api/poi/map-thumb 代理（不暴露 key）
    img_url = (kn.cover_image if kn else None) or poi.image or ""

    return RecommendPoiOut(
        id=poi.id,
        name=poi.name,
        category=poi.category or "地点",
        address=poi.address,
        distance=map_provider.format_distance(km),
        drive_time=f"{max(3, round(km / 25 * 60))}分钟",
        score=max(0, min(100, score)),
        reason=reason,
        tags=tags[:5],
        kb_status=kb_status,
        source="kb" if kb_status in ("hit", "partial", "stale", "unchanged") else (poi.source or poi.provider),
        lat=poi.lat,
        lng=poi.lng,
        nav_ready=True,
        img=img_url,
    )


def _core_name(name: str | None) -> str:
    """主名：取分隔符前的主体（"大槐树寻根祭祖园-财神殿"→"大槐树寻根祭祖园"），
    用于同一景区子点位去重；主名太短时退回整名，避免误并。"""
    if not name:
        return ""
    core = re.split(r"[-（(·•|/]", name)[0].strip()
    return core if len(core) >= 3 else name.strip()


def dedup_by_core(cards):
    """同一主名只保留第一个（列表已排序时即最优那个），去掉景区子点位重复。"""
    seen: set[str] = set()
    out = []
    for c in cards:
        key = _core_name(getattr(c, "name", None))
        if key and key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def recommend_pois(
    poi_rows: list[tuple[PoiIndex, TravelKnowledge | None]],
    origin: tuple[float, float],
    scene: str | None = None,
    weather: WeatherOut | None = None,
    limit: int = 8,
    preserve_order: bool = False,
    max_km: float | None = None,
) -> list[RecommendPoiOut]:
    scored = [
        card for card in (
            score_poi(poi, kn, origin=origin, scene=scene, weather=weather)
            for poi, kn in poi_rows
        )
        if card and card.nav_ready
        and (max_km is None or _distance_value(card.distance) <= max_km)
    ]
    # preserve_order：保留输入(高德 weight=热度)顺序，优先推热门点而非最近的冷门点
    if not preserve_order:
        scored.sort(key=lambda item: (-item.score, _distance_value(item.distance)))
    return dedup_by_core(scored)[:limit]


def _distance_value(distance: str) -> float:
    if distance.endswith("km"):
        return float(distance[:-2] or 0)
    if distance.endswith("m"):
        return float(distance[:-1] or 0) / 1000
    return 999.0
