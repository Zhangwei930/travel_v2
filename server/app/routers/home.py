"""Location-first home feed."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PoiIndex, TravelKnowledge
from app.schemas import HomeEntryOut, HomeFeedOut, LocationOut, RecommendPoiOut, RouteCardOut
from app.services import map_provider
from app.services.recommend_service import recommend_pois
from app.services.route_builder import build_home_routes
from app.services.weather_provider import get_weather
from app.taxonomy import SCENES

router = APIRouter(prefix="/api/home", tags=["home"])
compat_router = APIRouter(prefix="/api", tags=["home"])

HOME_ENTRIES = [
    HomeEntryOut(id="place_index", title="按场所索引"),
    HomeEntryOut(id="nearby_now", title="附近现在适合去"),
    HomeEntryOut(id="hot_routes", title="精选路线"),
    HomeEntryOut(id="assistant", title="问出游助手"),
]

ASSISTANT_CHIPS = ["2小时内去哪", "带孩子去哪", "雨天室内去哪", "低预算去哪"]
NEARBY_RADIUS_KM = 15.0


def _city_matches(row_city: str | None, requested_city: str | None) -> bool:
    if not requested_city:
        return True
    return map_provider.normalize_city(row_city) == map_provider.normalize_city(requested_city)


def _knowledge_maps(db: Session) -> tuple[dict[int, TravelKnowledge], dict[str, TravelKnowledge]]:
    approved = db.query(TravelKnowledge).filter(TravelKnowledge.review_status == "approved").all()
    by_id = {kn.poi_id: kn for kn in approved if kn.poi_id}
    by_name: dict[str, TravelKnowledge] = {}
    for kn in approved:
        if not kn.poi_id:
            continue
        poi = db.get(PoiIndex, kn.poi_id)
        if poi:
            by_name[poi.name] = kn
    return by_id, by_name


def _amap_rows(db: Session, lat: float, lng: float, city: str, scene: str | None) -> list[tuple[PoiIndex, TravelKnowledge | None]]:
    raw = map_provider.amap_search_around(
        lat,
        lng,
        radius_km=NEARBY_RADIUS_KM,
        types=map_provider.amap_types_for_scene(scene),
    )
    parsed = [p for p in (map_provider.parse_amap_poi(item) for item in raw) if p and p["name"]]
    if not parsed:
        return []

    _, kn_by_name = _knowledge_maps(db)
    now = datetime.utcnow()
    expires = now + timedelta(days=1)
    rows: list[tuple[PoiIndex, TravelKnowledge | None]] = []

    for item in parsed:
        provider_poi_id = item["provider_poi_id"]
        row = None
        if provider_poi_id:
            row = (
                db.query(PoiIndex)
                .filter(PoiIndex.provider == "amap", PoiIndex.provider_poi_id == provider_poi_id)
                .first()
            )
        if row:
            row.name = item["name"]
            row.city = city
            row.address = item["address"]
            row.lat = item["lat"]
            row.lng = item["lng"]
            row.category = item["category"]
            row.image = item.get("image")
            row.source = "amap"
            row.fetched_at = now
            row.expires_at = expires
        else:
            row = PoiIndex(
                provider="amap",
                provider_poi_id=provider_poi_id,
                name=item["name"],
                city=city,
                address=item["address"],
                lat=item["lat"],
                lng=item["lng"],
                category=item["category"],
                image=item.get("image"),
                source="amap",
                fetched_at=now,
                expires_at=expires,
            )
            db.add(row)
            db.flush()
        rows.append((row, kn_by_name.get(row.name)))

    db.commit()
    return rows


def _local_rows(db: Session, city: str, scene: str | None) -> list[tuple[PoiIndex, TravelKnowledge | None]]:
    kn_by_id, _ = _knowledge_maps(db)
    pois = db.query(PoiIndex).filter(PoiIndex.provider != "amap").all()
    rows: list[tuple[PoiIndex, TravelKnowledge | None]] = []
    for poi in pois:
        if not _city_matches(poi.city, city):
            continue
        kn = kn_by_id.get(poi.id)
        if scene and not (kn and scene in (kn.scene_ids or [])):
            continue
        rows.append((poi, kn))
    return rows


def _distance_value(distance: str) -> float:
    if distance.endswith("km"):
        return float(distance[:-2] or 0)
    if distance.endswith("m"):
        return float(distance[:-1] or 0) / 1000
    return 999.0


def _filter_nearby(items: list[RecommendPoiOut], filter_id: str | None) -> list[RecommendPoiOut]:
    if filter_id == "nearest":
        return sorted(items, key=lambda item: _distance_value(item.distance))
    if filter_id == "free":
        return [item for item in items if any("免费" in tag or "免门票" in tag for tag in item.tags)]
    if filter_id == "indoor":
        return [
            item for item in items
            if "室内" in (item.category or "") or any("室内" in tag for tag in item.tags)
        ]
    return items


def _filter_routes(items: list[RouteCardOut], duration: str | None) -> list[RouteCardOut]:
    if not duration:
        return items
    duration_map = {
        "2h": ("2小时", "2h", "两小时"),
        "half": ("半日", "半天", "3小时", "4小时"),
        "day": ("一日", "全天", "一天"),
    }
    needles = duration_map.get(duration, (duration,))
    return [item for item in items if any(needle in (item.duration or "") for needle in needles)]


def _build_home_feed(
    lat: float,
    lng: float,
    city: str | None,
    scene: str | None,
    db: Session,
) -> HomeFeedOut:
    _regeo = map_provider.amap_reverse_geocode(lat, lng)
    resolved_city = (
        _regeo["city"]
        or map_provider.normalize_city(city)
        or map_provider.nearest_city(lat, lng)
    )
    landmark = _regeo["landmark"]
    origin = (lat, lng)
    weather = get_weather(resolved_city)

    poi_rows = _amap_rows(db, lat, lng, resolved_city, scene)
    if not poi_rows:
        poi_rows = _local_rows(db, resolved_city, scene)

    nearby = recommend_pois(
        poi_rows,
        origin=origin,
        scene=scene,
        weather=weather,
        limit=8,
    )
    routes = build_home_routes(
        db,
        city=resolved_city,
        scene=scene,
        origin=origin,
        recommended=nearby,
        limit=3,
    )

    return HomeFeedOut(
        location=LocationOut(city=resolved_city, lat=lat, lng=lng, landmark=landmark),
        weather=weather,
        entries=HOME_ENTRIES,
        scene_index=SCENES,
        nearby_now=nearby,
        routes=routes,
        assistant_chips=ASSISTANT_CHIPS,
    )


@router.get("/feed", response_model=HomeFeedOut)
def home_feed(
    lat: float = Query(...),
    lng: float = Query(...),
    city: str | None = Query(default=None),
    intent: str | None = Query(default=None),
    scene: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return _build_home_feed(lat=lat, lng=lng, city=city, scene=scene, db=db)


@router.get("/bootstrap", response_model=HomeFeedOut)
def home_bootstrap(
    lat: float = Query(...),
    lng: float = Query(...),
    city: str | None = Query(default=None),
    intent: str | None = Query(default=None),
    scene: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return _build_home_feed(lat=lat, lng=lng, city=city, scene=scene, db=db)


@compat_router.get("/nearby/recommend", response_model=list[RecommendPoiOut])
def nearby_recommend(
    lat: float = Query(...),
    lng: float = Query(...),
    city: str | None = Query(default=None),
    scene: str | None = Query(default=None),
    filter: str | None = Query(default=None),
    time_slot: str | None = Query(default=None),
    weather: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    feed = _build_home_feed(lat=lat, lng=lng, city=city, scene=scene, db=db)
    return _filter_nearby(feed.nearby_now, filter)


@compat_router.get("/routes/featured", response_model=list[RouteCardOut])
def routes_featured(
    lat: float = Query(...),
    lng: float = Query(...),
    city: str | None = Query(default=None),
    scene: str | None = Query(default=None),
    duration: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    feed = _build_home_feed(lat=lat, lng=lng, city=city, scene=scene, db=db)
    return _filter_routes(feed.routes, duration)
