"""Location-first home feed."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PoiIndex, TravelKnowledge
from app.schemas import HomeEntryOut, HomeFeedOut, LocationOut
from app.services import map_provider
from app.services.recommend_service import recommend_pois
from app.services.route_builder import build_home_routes
from app.services.weather_provider import get_weather
from app.taxonomy import SCENES

router = APIRouter(prefix="/api/home", tags=["home"])

HOME_ENTRIES = [
    HomeEntryOut(id="place_index", title="按场所索引"),
    HomeEntryOut(id="nearby_now", title="附近现在适合去"),
    HomeEntryOut(id="hot_routes", title="精选路线"),
    HomeEntryOut(id="assistant", title="问出游助手"),
]

ASSISTANT_CHIPS = ["2小时内去哪", "带孩子去哪", "雨天室内去哪", "低预算去哪"]


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
        radius_km=5.0,
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


@router.get("/feed", response_model=HomeFeedOut)
def home_feed(
    lat: float = Query(...),
    lng: float = Query(...),
    city: str | None = Query(default=None),
    intent: str | None = Query(default=None),
    scene: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    resolved_city = (
        map_provider.normalize_city(city)
        or map_provider.amap_reverse_city(lat, lng)
        or map_provider.nearest_city(lat, lng)
    )
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
        location=LocationOut(city=resolved_city, lat=lat, lng=lng),
        weather=weather,
        entries=HOME_ENTRIES,
        scene_index=SCENES,
        nearby_now=nearby,
        routes=routes,
        assistant_chips=ASSISTANT_CHIPS,
    )
