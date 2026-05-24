"""Build route cards from nearby scored POIs and approved route templates."""
from sqlalchemy.orm import Session

from app.models import PoiIndex, TravelRoute
from app.schemas import RecommendPoiOut, RouteCardOut, RouteStopOut
from app.services import map_provider
from app.taxonomy import SCENE_LABELS


def _city_matches(row_city: str | None, requested_city: str | None) -> bool:
    if not requested_city:
        return True
    return map_provider.normalize_city(row_city) == map_provider.normalize_city(requested_city)


def _stop_from_poi(poi: PoiIndex, origin: tuple[float, float]) -> RouteStopOut | None:
    if poi.lat is None or poi.lng is None:
        return None
    return RouteStopOut(
        id=poi.id,
        name=poi.name,
        distance=map_provider.distance_text(origin, poi.lat, poi.lng),
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


def _dynamic_routes(
    recommended: list[RecommendPoiOut],
    scene: str | None,
    limit: int,
) -> list[RouteCardOut]:
    label = SCENE_LABELS.get(scene or "", "附近")
    specs = [
        ("dynamic_2h", f"2小时{label}轻松路线", "2小时", "低", recommended[:2]),
        ("dynamic_half_day", f"半日{label}路线", "半日", "低", recommended[:3]),
        ("dynamic_day", f"一日{label}路线", "一日", "中", recommended[:5]),
    ]
    cards: list[RouteCardOut] = []
    for route_id, title, duration, budget, stops_src in specs:
        stops = [s for s in (_stop_from_card(card) for card in stops_src) if s]
        if not stops:
            continue
        cards.append(RouteCardOut(
            id=f"{route_id}_{scene or 'nearby'}",
            title=title,
            duration=duration,
            budget=budget,
            scene=scene,
            summary="距离近，强度低，适合从当前位置直接出发。",
            stops=stops,
            nav_ready=True,
        ))
    return cards[:limit]


def build_home_routes(
    db: Session,
    city: str,
    scene: str | None,
    origin: tuple[float, float],
    recommended: list[RecommendPoiOut],
    limit: int = 3,
) -> list[RouteCardOut]:
    cards = _template_routes(db, city, scene, origin, limit)
    if len(cards) < limit:
        existing_ids = {str(card.id) for card in cards}
        for card in _dynamic_routes(recommended, scene, limit):
            if str(card.id) not in existing_ids:
                cards.append(card)
            if len(cards) >= limit:
                break
    return cards[:limit]
