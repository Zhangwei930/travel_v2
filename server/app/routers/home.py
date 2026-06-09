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


def _amap_rows(db: Session, lat: float, lng: float, city: str, scene: str | None,
               radius_km: float = NEARBY_RADIUS_KM, pages: int = 1,
               sortrule: str = "distance", spread: bool = False,
               keyword: str = "") -> list[tuple[PoiIndex, TravelKnowledge | None]]:
    types = map_provider.amap_types_for_scene(scene)
    if spread:
        # 距离分段采样：偏移中心一圈，把远处郊区点也召回（附近页大半径避免只堆市中心 2-4km）
        # （amap_search_spread 不支持 keyword；spread 调用方=附近页本就不传 keyword）
        raw = map_provider.amap_search_spread(lat, lng, radius_km=radius_km, types=types,
                                              pages=pages, sortrule=sortrule)
    else:
        raw = map_provider.amap_search_around(lat, lng, radius_km=radius_km, types=types,
                                              keyword=keyword, pages=pages, sortrule=sortrule)
    parsed = [p for p in (map_provider.parse_amap_poi(item) for item in raw) if p and p["name"]]
    # 通用过滤：附近召回会混进餐馆/酒吧/美容养生/商务住宅等非出游点，与场景索引口径一致剔除
    parsed = [
        p for p in parsed
        if map_provider.is_outing_destination(p["name"], p.get("category"), None,
                                              p.get("address"), allow_food=(scene == "food"))
    ]
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
    radius: float | None = None,
    route_limit: int = 3,
    route_per_duration: int = 1,
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

    # 附近页传 radius → 用该半径抓多页、返回更多（供下拉加载）；首页不传则保持 15km/精简
    # 带半径时按热度横跨全半径召回（与场景页一致）：distance 排序只返回最近一圈，
    # 且页数随半径放大，否则大半径（15/30/50km）列表会卡在最近几公里（如选 15km 却只拉到 ~4.2km）。
    eff_radius = radius or NEARBY_RADIUS_KM
    pages = map_provider.pages_for_radius(eff_radius) if radius else 1
    nearby_limit = pages * 25 if radius else 8
    sortrule = "weight" if radius else "distance"
    poi_rows = _amap_rows(db, lat, lng, resolved_city, scene, radius_km=eff_radius,
                          pages=pages, sortrule=sortrule, spread=bool(radius))
    if not poi_rows:
        poi_rows = _local_rows(db, resolved_city, scene)

    nearby = recommend_pois(
        poi_rows,
        origin=origin,
        scene=scene,
        weather=weather,
        limit=nearby_limit,
    )
    routes = build_home_routes(
        db,
        city=resolved_city,
        scene=scene,
        origin=origin,
        recommended=nearby,
        limit=route_limit,
        max_per_dur=route_per_duration,
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
    radius: float | None = Query(default=None, ge=1, le=100),
    route_limit: int = Query(default=3, ge=1, le=90),
    route_per_duration: int = Query(default=1, ge=1, le=30),
    db: Session = Depends(get_db),
):
    return _build_home_feed(
        lat=lat,
        lng=lng,
        city=city,
        scene=scene,
        db=db,
        radius=radius,
        route_limit=route_limit,
        route_per_duration=route_per_duration,
    )


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
    radius: float | None = Query(default=None, ge=1, le=100),
    route_limit: int | None = Query(default=None, ge=1, le=90),
    route_per_duration: int = Query(default=1, ge=1, le=30),
    db: Session = Depends(get_db),
):
    response_limit = route_limit or (route_per_duration if duration else 3)
    build_limit = max(response_limit, route_per_duration * 3) if duration else response_limit
    feed = _build_home_feed(
        lat=lat,
        lng=lng,
        city=city,
        scene=scene,
        db=db,
        radius=radius,
        route_limit=build_limit,
        route_per_duration=route_per_duration,
    )
    return _filter_routes(feed.routes, duration)[:response_limit]
