"""目录类接口：天气、场景、地点列表/详情、路线推荐（GET）。"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import PoiIndex, TravelKnowledge, TravelRoute
from app.schemas import FitItem, PoiDetailOut, PoiOut, RouteOut, SceneOut, WeatherOut
from app.services import ai_provider, map_provider
from app.services.trip_service import GEAR_BY_SCENE
from app.services.weather_provider import get_weather
from app.taxonomy import SCENES

router = APIRouter(prefix="/api", tags=["catalog"])


def _city_matches(row_city: str | None, requested_city: str | None) -> bool:
    if not requested_city:
        return True
    return map_provider.normalize_city(row_city) == map_provider.normalize_city(requested_city)


def _poi_out(poi: PoiIndex, kn: TravelKnowledge | None, origin, dist_text: str | None = None) -> PoiOut:
    img_url = (kn.cover_image if kn else None) or poi.image or ""
    if not img_url and poi.lat and poi.lng and settings.amap_key:
        img_url = f"https://restapi.amap.com/v3/staticmap?location={poi.lng},{poi.lat}&zoom=15&size=400x400&markers=mid,,A:{poi.lng},{poi.lat}&key={settings.amap_key}"

    return PoiOut(
        id=poi.id,
        no=(kn.display_no if kn else None) or f"NO.{poi.id:03d}",
        name=poi.name,
        cat=poi.category or "地点",
        dist=dist_text if dist_text is not None else map_provider.distance_text(origin, poi.lat, poi.lng),
        time=(kn.play_duration if kn else None) or "1-2h",
        budget=(kn.budget_level if kn else None) or "免费",
        tags=(kn.scene_tags if kn else None) or [],
        img=img_url,
        reason=(kn.recommend_reason if kn else None) or "",
    )


def _amap_nearby(lat: float, lng: float, city: str | None, db: Session) -> list[PoiOut] | None:
    """高德实时附近搜索：查 POI → 写入 poi_index 短期缓存 → 组装返回（方案 4.3）。"""
    raw = map_provider.amap_search_around(lat, lng)
    parsed = [p for p in (map_provider.parse_amap_poi(x) for x in raw) if p and p["name"]]
    if not parsed:
        return None

    # 按名称匹配已有知识库内容，匹配上的用精编知识，否则用高德基础信息
    kn_by_name: dict[str, TravelKnowledge] = {}
    for kn in db.query(TravelKnowledge).all():
        poi = db.get(PoiIndex, kn.poi_id) if kn.poi_id else None
        if poi:
            kn_by_name[poi.name] = kn

    now = datetime.utcnow()
    expires = now + timedelta(days=1)
    cache_city = map_provider.normalize_city(city) or map_provider.nearest_city(lat, lng)
    out: list[PoiOut] = []
    for p in parsed:
        row = (
            db.query(PoiIndex)
            .filter(PoiIndex.provider == "amap", PoiIndex.provider_poi_id == p["provider_poi_id"])
            .first()
        )
        if row:
            row.name, row.lat, row.lng = p["name"], p["lat"], p["lng"]
            row.category, row.address = p["category"], p["address"]
            row.image = p.get("image") or row.image
            row.city = cache_city
            row.fetched_at, row.expires_at = now, expires
        else:
            row = PoiIndex(
                provider="amap", provider_poi_id=p["provider_poi_id"], name=p["name"],
                city=cache_city, address=p["address"], lat=p["lat"], lng=p["lng"],
                category=p["category"], image=p.get("image"), source="amap", fetched_at=now, expires_at=expires,
            )
            db.add(row)
            db.flush()
        kn = kn_by_name.get(p["name"])
        dist = map_provider.format_distance(p["distance_m"] / 1000) if p["distance_m"] is not None else "—"

        img_url = (kn.cover_image if kn else None) or row.image or ""
        if not img_url and row.lat and row.lng and settings.amap_key:
            img_url = f"https://restapi.amap.com/v3/staticmap?location={row.lng},{row.lat}&zoom=15&size=400x400&markers=mid,,A:{row.lng},{row.lat}&key={settings.amap_key}"

        out.append(PoiOut(
            id=row.id,
            no=(kn.display_no if kn else None) or f"NO.{row.id:03d}",
            name=row.name,
            cat=row.category or "地点",
            dist=dist,
            time=(kn.play_duration if kn else None) or "—",
            budget=(kn.budget_level if kn else None) or "—",
            tags=(kn.scene_tags if kn else None) or p["type_tags"],
            img=img_url,
            reason=(kn.recommend_reason if kn else None) or (row.address or ""),
        ))
    db.commit()
    return out


@router.get("/weather", response_model=WeatherOut)
def weather(city: str | None = None):
    return get_weather(city or settings.default_city)


@router.get("/capability")
def capability():
    return {
        "map_amap": map_provider.provider_name() == "amap",
        "websearch": bool(settings.searxng_base),
        "ai": ai_provider.is_live(),
    }


@router.get("/city/list")
def city_list(db: Session = Depends(get_db)):
    cities = {settings.default_city, *map_provider.CITY_CENTER.keys()}
    rows = db.query(PoiIndex.city).filter(PoiIndex.city.isnot(None)).distinct().all()
    cities.update(row[0] for row in rows if row[0])
    return sorted(cities)


@router.get("/geo/city")
def geo_city(lat: float = Query(...), lng: float = Query(...)):
    city = map_provider.amap_reverse_city(lat, lng) or map_provider.nearest_city(lat, lng)
    return {"city": city}


@router.get("/scene/list", response_model=list[SceneOut])
def scene_list():
    return SCENES


@router.get("/gear/list", response_model=list[str])
def gear_list(scene: str | None = Query(default=None)):
    return GEAR_BY_SCENE.get(scene or "", [])


@router.get("/poi/list", response_model=list[PoiOut])
def poi_list(
    scene: str | None = Query(default=None),
    city: str | None = Query(default=None),
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    # 带定位、无场景/关键词筛选时，走高德实时附近搜索
    if lat is not None and lng is not None and not scene and not keyword:
        nearby = _amap_nearby(lat, lng, city, db)
        if nearby is not None:
            return nearby

    # 知识库分支：仅取种子/精编 POI（不含高德实时缓存）
    origin = map_provider.resolve_origin(city or settings.default_city, lat, lng)
    pois = db.query(PoiIndex).filter(PoiIndex.provider != "amap").all()
    if city:
        pois = [p for p in pois if _city_matches(p.city, city)]
    kn_map = {k.poi_id: k for k in db.query(TravelKnowledge).all() if k.poi_id}

    # 带定位时用高德真实驾车路程替换直线估算
    real_dist: dict[int, str] = {}
    if origin and map_provider.provider_name() == "amap":
        located = [p for p in pois if p.lat is not None and p.lng is not None]
        meters = map_provider.amap_driving_distances(origin, [(p.lat, p.lng) for p in located])
        for poi, m in zip(located, meters):
            if m is not None:
                real_dist[poi.id] = map_provider.format_distance(m / 1000)

    out: list[PoiOut] = []
    for poi in pois:
        kn = kn_map.get(poi.id)
        if scene and not (kn and scene in (kn.scene_ids or [])):
            continue
        if keyword and keyword not in poi.name and keyword not in (poi.category or ""):
            continue
        out.append(_poi_out(poi, kn, origin, dist_text=real_dist.get(poi.id)))
    return out


@router.get("/poi/detail", response_model=PoiDetailOut)
def poi_detail(
    id: int = Query(...),
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    db: Session = Depends(get_db),
):
    poi = db.get(PoiIndex, id)
    if not poi:
        raise HTTPException(status_code=404, detail="地点不存在")
    kn = db.query(TravelKnowledge).filter(TravelKnowledge.poi_id == id).first()
    origin = map_provider.resolve_origin(poi.city or settings.default_city, lat, lng)
    base = _poi_out(poi, kn, origin)

    people = (kn.suitable_people if kn else None) or []
    weather = (kn.suitable_weather if kn else None) or []
    fit_items = [
        FitItem(icon="👨‍👩‍👧", label="人群", val="·".join(people) or "通用"),
        FitItem(icon="🌤", label="天气", val="·".join(weather) or "晴天最佳"),
        FitItem(icon="⏰", label="时段", val=(kn.best_time if kn else None) or "全天"),
        FitItem(icon="💪", label="强度", val="轻量"),
    ]
    tips_raw = (kn.avoid_tips if kn else None) or ""
    avoid_tips = [t.strip() for t in tips_raw.replace("；", "\n").splitlines() if t.strip()]

    return PoiDetailOut(
        **base.model_dump(),
        suitable_people=people,
        suitable_weather=weather,
        best_time=(kn.best_time if kn else None),
        fit_items=fit_items,
        avoid_tips=avoid_tips,
        lat=poi.lat,
        lng=poi.lng,
    )


def _route_out(route: TravelRoute) -> RouteOut:
    return RouteOut(
        id=route.id,
        no=route.display_no or f"R-{route.id:02d}",
        title=route.title,
        tag=route.scene_label or route.scene or "出游",
        color=route.color or "#0D4F4A",
        duration=route.duration or "半日",
        budget=route.budget_level or "低",
        poi=len(route.poi_ids or []),
        img=route.cover_image or "",
        summary=route.route_text or "",
    )


@router.get("/route/recommend", response_model=list[RouteOut])
def route_recommend(
    scene: str | None = Query(default=None),
    city: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    base = db.query(TravelRoute).filter(TravelRoute.review_status == "approved")
    rows = base.all()
    if city:
        rows = [r for r in rows if _city_matches(r.city, city)]
    if scene:
        matched = [r for r in rows if r.scene == scene]
        # 该场景无专属路线时回退到全部路线（与前端 mock 行为一致）
        rows = matched or rows
    return [_route_out(r) for r in rows]
