"""目录类接口：天气、场景、地点列表/详情、路线推荐（GET）。"""
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
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


def _dist_km(item: PoiOut) -> float:
    d = item.dist or ""
    if d.endswith("km"):
        try: return float(d[:-2])
        except ValueError: pass
    if d.endswith("m"):
        try: return float(d[:-1]) / 1000
        except ValueError: pass
    return 9999.0


def _city_matches(row_city: str | None, requested_city: str | None) -> bool:
    if not requested_city:
        return True
    return map_provider.normalize_city(row_city) == map_provider.normalize_city(requested_city)


def _poi_out(poi: PoiIndex, kn: TravelKnowledge | None, origin, dist_text: str | None = None) -> PoiOut:
    # 仅下发真实照片；无照片时留空，前端走 /api/poi/map-thumb 代理（不暴露 key）
    img_url = (kn.cover_image if kn else None) or poi.image or ""

    return PoiOut(
        id=poi.id,
        no=(kn.display_no if kn else None) or f"NO.{poi.id:03d}",
        name=poi.name,
        cat=poi.category or "地点",
        dist=dist_text if dist_text is not None else map_provider.distance_text(origin, poi.lat, poi.lng),
        time=(kn.play_duration if kn else None) or "1-2h",
        budget=(kn.budget_level if kn else None) or "以官方为准",
        tags=(kn.scene_tags if kn else None) or [],
        img=img_url,
        reason=(kn.recommend_reason if kn else None) or "",
        lat=poi.lat,
        lng=poi.lng,
    )


def _parse_amap_to_poiout(raw: list, lat: float, lng: float, city: str | None, db: Session) -> list[PoiOut]:
    """将高德原始 POI 列表解析入库并返回 PoiOut。"""
    parsed = [p for p in (map_provider.parse_amap_poi(x) for x in raw) if p and p["name"]]
    if not parsed:
        return []

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
        # 用请求坐标到 POI 的直线距离，缓存按网格命中时距离仍准确
        if p["lat"] is not None and p["lng"] is not None:
            dist = map_provider.format_distance(map_provider.haversine_km(lat, lng, p["lat"], p["lng"]))
        elif p["distance_m"] is not None:
            dist = map_provider.format_distance(p["distance_m"] / 1000)
        else:
            dist = "—"
        img_url = (kn.cover_image if kn else None) or row.image or ""
        out.append(PoiOut(
            id=row.id,
            no=(kn.display_no if kn else None) or f"NO.{row.id:03d}",
            name=row.name,
            cat=row.category or "地点",
            dist=dist,
            time=(kn.play_duration if kn else None) or "—",
            budget=(kn.budget_level if kn else None) or "以官方为准",
            tags=(kn.scene_tags if kn else None) or p["type_tags"],
            img=img_url,
            reason=(kn.recommend_reason if kn else None) or (row.address or ""),
            lat=row.lat,
            lng=row.lng,
        ))
    db.commit()
    return out


def _amap_nearby(lat: float, lng: float, city: str | None, db: Session) -> list[PoiOut] | None:
    """高德实时附近搜索（无场景，默认类型）。"""
    raw = map_provider.amap_search_around(lat, lng)
    result = _parse_amap_to_poiout(raw, lat, lng, city, db)
    return result if result else None


@router.get("/weather", response_model=WeatherOut)
def weather(city: str | None = None):
    return get_weather(city or settings.default_city)


@router.get("/capability")
def capability():
    return {
        "map_amap": map_provider.provider_name() == "amap",
        "websearch": bool(settings.searxng_base),
        "ai": ai_provider.is_live(),
        "consult": settings.consult_enabled,   # 在线咨询入口是否对外开放
    }


@router.get("/city/list")
def city_list(db: Session = Depends(get_db)):
    cities = {settings.default_city, *map_provider.CITY_CENTER.keys()}
    rows = db.query(PoiIndex.city).filter(PoiIndex.city.isnot(None)).distinct().all()
    cities.update(row[0] for row in rows if row[0])
    return sorted(cities)


@router.get("/geo/city")
def geo_city(lat: float = Query(...), lng: float = Query(...)):
    geo = map_provider.amap_reverse_geocode(lat, lng)
    city = geo["city"] or map_provider.nearest_city(lat, lng)
    return {"city": city, "landmark": geo.get("landmark")}


@router.get("/poi/map-thumb")
def poi_map_thumb(lat: float = Query(...), lng: float = Query(...)):
    """POI 无照片时的定位地图缩略图：后端代理高德静态地图字节，key 不下发到客户端。"""
    if not (map_provider.provider_name() == "amap" and settings.amap_key):
        raise HTTPException(status_code=404, detail="map unavailable")
    url = (
        f"https://restapi.amap.com/v3/staticmap?location={lng},{lat}"
        f"&zoom=15&size=400*300&markers=mid,,A:{lng},{lat}&key={settings.amap_key}"
    )
    try:
        resp = httpx.get(url, timeout=8.0)
        resp.raise_for_status()
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="map fetch failed")
    return Response(
        content=resp.content,
        media_type=resp.headers.get("content-type", "image/png"),
        headers={"Cache-Control": "public, max-age=86400"},
    )


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
    radius: float | None = Query(default=None, ge=1, le=150),   # 前端可调距离（km）
    sort: str = Query(default="distance"),                      # distance=按距离 / hot=按热度
    db: Session = Depends(get_db),
):
    # 有坐标时走高德实时搜索（amap_search_around 内置 TTL 缓存，重复请求不再打高德）
    if lat is not None and lng is not None and not keyword:
        radius = radius or map_provider.SCENE_RADIUS_KM.get(scene or "", 15.0)
        types = map_provider.amap_types_for_scene(scene) if scene else map_provider.AMAP_DEFAULT_TYPES
        scene_kw = map_provider.SCENE_KEYWORDS.get(scene or "", "")
        # 场景浏览按热度抓多页：一次返回更多、覆盖近→远全半径（再按距离重排展示）
        # 页数随半径放大，否则大半径（15/30/50km）只铺到最近几公里就没有更多了
        sortrule = "weight" if scene else "distance"
        pages = map_provider.pages_for_radius(radius) if scene else 1
        around_radius = min(radius, map_provider.AMAP_AROUND_MAX_RADIUS_KM)

        def parsed_within_radius(raw_rows: list) -> list[PoiOut]:
            amap_rows = _parse_amap_to_poiout(raw_rows, lat, lng, city, db) if raw_rows else []
            rows = [p for p in amap_rows if _dist_km(p) <= radius]
            # 通用过滤：去类型搜索会混进餐馆/公司/汽修等，所有场景都剔除
            rows = [
                p for p in rows
                if map_provider.is_outing_destination(p.name, p.cat, p.tags, p.reason,
                                                      allow_food=(scene == "food"))
            ]
            if scene == "hike":
                rows = [
                    p for p in rows
                    if map_provider.is_hike_destination(p.name, p.cat, p.tags, p.reason)
                ]
            if scene == "food":
                rows = [p for p in rows if map_provider.is_food_destination(p.name, p.cat, p.tags)]
            if scene == "cycle":
                rows = [p for p in rows if map_provider.is_cycle_destination(p.name, p.cat, p.tags)]
            if scene == "camp":
                rows = [p for p in rows if map_provider.is_camp_destination(p.name, p.cat, p.tags)]
            return rows

        if scene == "hike" and radius > map_provider.AMAP_AROUND_MAX_RADIUS_KM:
            raw = map_provider.amap_search_text(
                city or map_provider.nearest_city(lat, lng),
                types=types,
                keyword=scene_kw,
                pages=pages,
            )
            amap_results = parsed_within_radius(raw)
            if amap_results:
                return amap_results if sort == "hot" else sorted(amap_results, key=lambda p: _dist_km(p))

        raw = []
        if scene_kw:
            raw = map_provider.amap_search_around(lat, lng, radius_km=around_radius, types=types,
                                                  keyword=scene_kw, sortrule="weight", pages=pages)
        if not raw:
            raw = map_provider.amap_search_around(lat, lng, radius_km=around_radius, types=types,
                                                  sortrule=sortrule, pages=pages)
        # 场景搜索无结果时，用默认类型兜底（避免只返回2条种子数据）
        if not raw and scene:
            raw = map_provider.amap_search_around(lat, lng, radius_km=around_radius,
                                                  types=map_provider.AMAP_DEFAULT_TYPES, pages=2)
        amap_results = parsed_within_radius(raw)
        if amap_results:
            return amap_results if sort == "hot" else sorted(amap_results, key=lambda p: _dist_km(p))

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

    if lat is not None and lng is not None and radius:
        out = [p for p in out if _dist_km(p) <= radius]
    if scene == "hike":
        out = [
            p for p in out
            if map_provider.is_hike_destination(p.name, p.cat, p.tags, p.reason)
        ]

    out.sort(key=_dist_km)   # 种子/无定位路径无热度信号，统一按距离（hot 仅在高德实时分支生效）
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
        FitItem(icon="people", label="人群", val="·".join(people) or "通用"),
        FitItem(icon="weather", label="天气", val="·".join(weather) or "晴天最佳"),
        FitItem(icon="time", label="时段", val=(kn.best_time if kn else None) or "全天"),
        FitItem(icon="strength", label="强度", val="轻量"),
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
        # 该场景无专属路线时回退到全部路线，保持前端列表可继续浏览。
        rows = matched or rows
    return [_route_out(r) for r in rows]
