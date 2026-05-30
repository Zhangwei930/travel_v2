"""Build route cards from nearby scored POIs and approved route templates."""
from sqlalchemy.orm import Session

from app.models import PoiIndex, TravelRoute
from app.schemas import RecommendPoiOut, RouteCardOut, RouteStopOut
from app.services import map_provider
from app.taxonomy import SCENE_LABELS

MAX_ROUTE_STOP_KM = 15.0


def _city_matches(row_city: str | None, requested_city: str | None) -> bool:
    if not requested_city:
        return True
    return map_provider.normalize_city(row_city) == map_provider.normalize_city(requested_city)


def _stop_from_poi(poi: PoiIndex, origin: tuple[float, float]) -> RouteStopOut | None:
    if poi.lat is None or poi.lng is None:
        return None
    km = map_provider.haversine_km(origin[0], origin[1], poi.lat, poi.lng)
    if km > MAX_ROUTE_STOP_KM:
        return None
    return RouteStopOut(
        id=poi.id,
        name=poi.name,
        distance=map_provider.format_distance(km),
        reason=poi.category or "",
        lat=poi.lat,
        lng=poi.lng,
    )


def _stop_from_card(card: RecommendPoiOut) -> RouteStopOut | None:
    if card.lat is None or card.lng is None:
        return None
    return RouteStopOut(
        id=card.id,
        name=card.name,
        distance=card.distance,
        reason=card.reason,
        lat=card.lat,
        lng=card.lng,
    )


def _template_routes(
    db: Session,
    city: str,
    scene: str | None,
    origin: tuple[float, float],
    limit: int,
) -> list[RouteCardOut]:
    rows = db.query(TravelRoute).filter(TravelRoute.review_status == "approved").all()
    rows = [r for r in rows if _city_matches(r.city, city)]
    if scene:
        scene_rows = [r for r in rows if r.scene == scene]
        rows = scene_rows or rows

    cards: list[RouteCardOut] = []
    for route in rows[:limit]:
        stops: list[RouteStopOut] = []
        for poi_id in route.poi_ids or []:
            poi = db.get(PoiIndex, poi_id)
            if not poi:
                continue
            stop = _stop_from_poi(poi, origin)
            if stop:
                stops.append(stop)
        if not stops:
            continue
        cards.append(RouteCardOut(
            id=route.id,
            title=route.title,
            duration=route.duration or "半日",
            budget=route.budget_level,
            scene=route.scene,
            summary=route.route_text or "",
            stops=stops,
            nav_ready=bool(stops),
        ))
    return cards


AVG_SPEED_KMH = 25.0   # 车程估算速度，与 recommend_service 的 drive_time 一致

# 每个时长：站点数 + 预算等级 + 往返车程上限(分钟)。
# 2小时=2站/≤60min、半日=3站/≤120min、一日=5站/≤240min。
# 往返车程超上限即"光路上就超时"，不出该路线。
_DURATION_SPECS = [
    ("2h", "2小时", 2, "低", 60),
    ("half", "半日", 3, "低", 120),
    ("day", "一日", 5, "中", 240),
]


def _route_travel_min(origin: tuple[float, float], stops: list[RouteStopOut]) -> float:
    """估算 当前位置→各站→返回 的总车程分钟（直线距离 / 平均车速）。"""
    pts = [origin] + [(s.lat, s.lng) for s in stops] + [origin]
    km = sum(
        map_provider.haversine_km(a[0], a[1], b[0], b[1])
        for a, b in zip(pts, pts[1:])
    )
    return km / AVG_SPEED_KMH * 60


def _dynamic_routes(
    recommended: list[RecommendPoiOut],
    scene: str | None,
    origin: tuple[float, float],
    max_per_dur: int,
) -> list[RouteCardOut]:
    """把附近 POI 池切成每个时长多条路线，标题用「首站-末站」。
    按距离由近到远成行，并跳过往返车程超出该时长预算的路线。"""
    label = SCENE_LABELS.get(scene or "", "附近")
    pool = [s for s in (_stop_from_card(card) for card in recommended) if s]
    pool.sort(key=lambda s: map_provider.haversine_km(origin[0], origin[1], s.lat, s.lng))
    cards: list[RouteCardOut] = []
    for key, duration, size, budget, max_travel in _DURATION_SPECS:
        cnt = 0
        for i in range(0, len(pool), size):
            chunk = pool[i:i + size]
            if len(chunk) < 2:          # 至少 2 站才算一条路线
                break
            if _route_travel_min(origin, chunk) > max_travel:
                break                   # 距离升序，后续路线更远，必然也超时
            title = f"{chunk[0].name}-{chunk[-1].name}"
            cards.append(RouteCardOut(
                id=f"dynamic_{scene or 'nearby'}_{key}_{i}",
                title=title,
                duration=duration,
                budget=budget,
                scene=scene,
                summary=f"{label}·{len(chunk)}站，就近成行，从当前位置出发。",
                stops=chunk,
                nav_ready=True,
            ))
            cnt += 1
            if cnt >= max_per_dur:
                break
    return cards


def build_home_routes(
    db: Session,
    city: str,
    scene: str | None,
    origin: tuple[float, float],
    recommended: list[RecommendPoiOut],
    limit: int = 3,
    max_per_dur: int = 1,
) -> list[RouteCardOut]:
    cards = _dynamic_routes(recommended, scene, origin, max_per_dur)
    if len(cards) < limit:
        existing_ids = {str(card.id) for card in cards}
        for card in _template_routes(db, city, scene, origin, limit):
            if str(card.id) not in existing_ids:
                cards.append(card)
            if len(cards) >= limit:
                break
    return cards[:limit]
