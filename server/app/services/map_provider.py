"""地图 API 适配器。

方案文档第 4 章：地图 API 负责真实地点、距离、路线，但不作为长期原始数据库。
默认 stub 模式用本地坐标做 haversine 距离计算，无需密钥即可运行；
配置 MAP_PROVIDER=amap 并填入 AMAP_KEY 后接入高德地图（周边搜索 + 真实路程）。
"""
from math import asin, cos, radians, sin, sqrt

import httpx

from app.config import settings

AMAP_BASE = "https://restapi.amap.com"
# 高德 POI 类型码：风景名胜大类(含公园/动植物园) / 博物馆 / 展览馆 / 美术馆 / 科技馆
AMAP_DEFAULT_TYPES = "110000|140100|140200|140400|140600"

# 各城市中心点（请求未带定位时的兜底原点）
CITY_CENTER: dict[str, tuple[float, float]] = {
    "成都": (30.5728, 104.0668),
    "乌鲁木齐": (43.8256, 87.6168),
}


def normalize_city(city: str | None) -> str:
    return (city or "").strip().removesuffix("市")


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """两点间球面距离，单位 km。"""
    r = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return 2 * r * asin(sqrt(a))


def format_distance(km: float) -> str:
    if km < 1:
        return f"{int(km * 1000)}m"
    return f"{km:.1f}km"


def distance_text(origin: tuple[float, float] | None, lat: float | None, lng: float | None,
                   fallback: str = "—") -> str:
    """计算原点到目标 POI 的距离文本。坐标缺失时返回 fallback。"""
    if origin is None or lat is None or lng is None:
        return fallback
    return format_distance(haversine_km(origin[0], origin[1], lat, lng))


def resolve_origin(city: str | None, lat: float | None, lng: float | None) -> tuple[float, float] | None:
    """确定计算距离的原点：优先用户定位，其次城市中心。"""
    if lat is not None and lng is not None:
        return (lat, lng)
    if city and city in CITY_CENTER:
        return CITY_CENTER[city]
    return None


def nearest_city(lat: float, lng: float) -> str:
    """无逆地理服务时按内置城市中心做最近城市兜底。"""
    if not CITY_CENTER:
        return settings.default_city
    return min(CITY_CENTER, key=lambda city: haversine_km(lat, lng, CITY_CENTER[city][0], CITY_CENTER[city][1]))


def amap_reverse_city(lat: float, lng: float) -> str | None:
    """高德逆地理编码；未配置高德时返回 None，由调用方兜底。"""
    if provider_name() != "amap":
        return None
    try:
        resp = httpx.get(
            f"{AMAP_BASE}/v3/geocode/regeo",
            params={"key": settings.amap_key, "location": f"{lng},{lat}", "extensions": "base"},
            timeout=5.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if str(data.get("status")) != "1":
            return None
        comp = data.get("regeocode", {}).get("addressComponent", {})
        city = comp.get("city") or comp.get("province") or None
        if isinstance(city, list):
            city = None
        return str(city).replace("市", "").strip() if city else None
    except (httpx.HTTPError, ValueError):
        return None


def transport_hint(transport: str | None) -> str:
    """根据出行方式给出路段交通建议文案。"""
    return {
        "自驾": "自驾前往，停车以地图实时信息为准",
        "公交": "公交可达，建议出发前查询实时班次",
        "地铁": "地铁直达，留意末班车时间",
        "步行": "步行可达，距离较近",
        "打车": "打车前往，高峰期注意排队",
    }.get(transport or "", "出行方式可参考地图实时路线规划")


def provider_name() -> str:
    """当前生效的地图数据来源标识。"""
    if settings.map_provider == "amap" and settings.amap_key:
        return "amap"
    if settings.map_provider == "tencent" and settings.tencent_map_key:
        return "tencent"
    return "stub"


def amap_search_around(lat: float, lng: float, radius_km: float = 5.0,
                       types: str = AMAP_DEFAULT_TYPES) -> list[dict]:
    """高德周边搜索，返回原始 POI 列表（方案 4.1 附近搜索）。失败返回 []。"""
    if provider_name() != "amap":
        return []
    try:
        resp = httpx.get(
            f"{AMAP_BASE}/v3/place/around",
            params={
                "key": settings.amap_key,
                "location": f"{lng},{lat}",
                "radius": int(radius_km * 1000),
                "types": types,
                "offset": 25,
                "page": 1,
                "extensions": "all",
            },
            timeout=8.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if str(data.get("status")) != "1":
            return []
        return data.get("pois") or []
    except (httpx.HTTPError, ValueError):
        return []


def amap_driving_distances(origin: tuple[float, float],
                           locations: list[tuple[float, float]]) -> list[float | None]:
    """高德驾车路程测量：origin 到各 location 的实际路程(米)。失败项为 None。"""
    if provider_name() != "amap" or not locations:
        return [None] * len(locations)
    try:
        resp = httpx.get(
            f"{AMAP_BASE}/v3/distance",
            params={
                "key": settings.amap_key,
                "origins": "|".join(f"{lng},{lat}" for lat, lng in locations),
                "destination": f"{origin[1]},{origin[0]}",
                "type": 1,
            },
            timeout=8.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if str(data.get("status")) != "1":
            return [None] * len(locations)
        out: list[float | None] = [None] * len(locations)
        for r in data.get("results", []):
            idx = int(r.get("origin_id", 0)) - 1
            if 0 <= idx < len(locations):
                try:
                    out[idx] = float(r.get("distance", 0))
                except (TypeError, ValueError):
                    out[idx] = None
        return out
    except (httpx.HTTPError, ValueError):
        return [None] * len(locations)


def parse_amap_poi(poi: dict) -> dict | None:
    """把高德 POI 标准化为入库字段。坐标缺失则返回 None。"""
    loc = poi.get("location") or ""
    if "," not in str(loc):
        return None
    try:
        lng, lat = (float(x) for x in str(loc).split(","))
    except ValueError:
        return None
    type_text = str(poi.get("type") or "")
    category = type_text.split(";")[0] if type_text else "地点"
    photos = poi.get("photos") or []
    image = ""
    if isinstance(photos, list) and photos and isinstance(photos[0], dict):
        image = photos[0].get("url") or ""
    distance = poi.get("distance")
    try:
        distance_m = float(distance) if distance not in (None, "", []) else None
    except (TypeError, ValueError):
        distance_m = None
    return {
        "provider_poi_id": str(poi.get("id") or ""),
        "name": str(poi.get("name") or "").strip(),
        "address": str(poi.get("address") or "") or None,
        "lat": lat,
        "lng": lng,
        "category": category,
        "type_tags": [t for t in type_text.split(";") if t][:3],
        "image": image,
        "distance_m": distance_m,
    }
