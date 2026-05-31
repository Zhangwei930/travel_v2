"""地图 API 适配器。

方案文档第 4 章：地图 API 负责真实地点、距离、路线，但不作为长期原始数据库。
默认 stub 模式用本地坐标做 haversine 距离计算，无需密钥即可运行；
配置 MAP_PROVIDER=amap 并填入 AMAP_KEY 后接入高德地图（周边搜索 + 真实路程）。
"""
import concurrent.futures
import time
from math import asin, cos, radians, sin, sqrt

import httpx

from app.config import settings

AMAP_BASE = "https://restapi.amap.com"
# 高德 POI 类型码：风景名胜大类(含公园/动植物园) / 博物馆 / 展览馆 / 美术馆 / 科技馆
AMAP_DEFAULT_TYPES = "110000|140100|140200|140400|140600"
AMAP_TYPES_BY_SCENE: dict[str, str] = {
    "family": "110000|140100|140600|080500",
    "couple": "110000|110200|110100|140400|140200",
    "rainy": "060100|140100|140400|140600",
    "budget": "110000|140100|061000",
    "fish": "110200|110100|140600",
    "photo": "110000|140000|061000|080600",
    "night": "050000|060100|061000|080600",
    "walk": "061000|110000|140000",
    "old": "110000|140100|060100",
    "hike": "110000|110200|110100",
}

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


def amap_reverse_geocode(lat: float, lng: float) -> dict:
    """高德逆地理编码，返回 {"city": str|None, "landmark": str|None}。"""
    if provider_name() != "amap":
        return {"city": None, "landmark": None}
    try:
        resp = httpx.get(
            f"{AMAP_BASE}/v3/geocode/regeo",
            params={"key": settings.amap_key, "location": f"{lng},{lat}", "extensions": "all", "radius": 500},
            timeout=5.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if str(data.get("status")) != "1":
            return {"city": None, "landmark": None}
        regeo = data.get("regeocode", {})
        comp = regeo.get("addressComponent", {})
        city = comp.get("city") or comp.get("province") or None
        if isinstance(city, list):
            city = None
        city = str(city).replace("市", "").strip() if city else None
        # 取最近 POI 名称作为地标
        pois = regeo.get("pois") or []
        landmark = pois[0].get("name") if pois and isinstance(pois, list) else None
        return {"city": city, "landmark": landmark}
    except (httpx.HTTPError, ValueError):
        return {"city": None, "landmark": None}


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


def amap_types_for_scene(scene: str | None) -> str:
    return AMAP_TYPES_BY_SCENE.get(scene or "", AMAP_DEFAULT_TYPES)


SCENE_RADIUS_KM: dict[str, float] = {
    "fish": 30.0,   # 钓鱼场/湿地公园多在郊区，需更大半径
    "hike": 30.0,   # 山峰/景区多在郊区，需更大半径
}

# 各场景用关键词搜索命中知名目的地（数量少、分布广），配合 weight 排序横跨全半径，
# 避免在密集城区只召回最近 2km 的同质小场所
SCENE_KEYWORDS: dict[str, str] = {
    "family": "乐园|游乐园|动物园|海洋馆|主题公园|植物园|科技馆|博物馆|亲子",
    "couple": "公园|湖|景区|古镇|植物园|美术馆|博物馆|观景|江滩|花海",
    "rainy":  "博物馆|美术馆|科技馆|水族馆|海洋馆|图书馆|商场|影院",
    "budget": "公园|绿道|博物馆|广场|湖|景区|江滩",
    "night":  "夜市|酒吧|商业街|步行街|夜景|观景|江滩|塔",
    "walk":   "公园|绿道|古镇|街区|步行街|湖|江滩",
    "photo":  "古镇|景区|花海|湖|公园|植物园|美术馆|网红|打卡",
    "fish":   "垂钓|钓鱼|鱼塘|湿地公园|水库",
    "old":    "公园|景区|古镇|博物馆|植物园|寺|湖",
    "hike":   "登山|山|山峰|徒步|爬山|景区|森林公园|风景区",
}


def pages_for_radius(radius_km: float) -> int:
    """半径越大抓越多页（每页25个POI），让结果横跨整个半径而非只堆最近一圈。
    多页改为并发抓取，故页数不再线性拖慢延迟；上限 8 页以控高德配额。
    （15km 仍为 5 页，结果与之前一致；仅 30/50km 略收。）"""
    return max(5, min(8, round(radius_km / 6)))


# 周边搜索进程内缓存：场景列表与首页 feed 共用，TTL 内重复请求不再打高德
_AROUND_CACHE: dict[str, tuple[float, list]] = {}
_AROUND_TTL = 1800.0   # 30 分钟


def _fetch_around_page(page: int, lat: float, lng: float, radius_km: float,
                       types: str, keyword: str, sortrule: str) -> list[dict]:
    """抓取周边搜索单页，失败/无结果返回 []。供并发调用。"""
    params = {
        "key": settings.amap_key,
        "location": f"{lng},{lat}",
        "radius": int(radius_km * 1000),
        "types": types,
        "offset": 25,
        "page": page,
        "extensions": "all",
        "sortrule": sortrule,
    }
    if keyword:
        params["keywords"] = keyword
    try:
        resp = httpx.get(f"{AMAP_BASE}/v3/place/around", params=params, timeout=8.0)
        resp.raise_for_status()
        data = resp.json()
        if str(data.get("status")) != "1":
            return []
        return data.get("pois") or []
    except (httpx.HTTPError, ValueError):
        return []


def amap_search_around(lat: float, lng: float, radius_km: float = 15.0,
                       types: str = AMAP_DEFAULT_TYPES,
                       keyword: str = "", sortrule: str = "distance",
                       pages: int = 1) -> list[dict]:
    """高德周边搜索，返回原始 POI 列表（方案 4.1 附近搜索）。失败返回 []。

    sortrule: distance（按距离，近→远）/ weight（按热度，能横跨全半径召回知名点）。
    pages: 抓取的页数（每页 25 个）；多页并发抓取，避免大半径下顺序请求拖慢、前端超时。
    结果按 ~1km 网格坐标缓存，TTL 内复用，省高德配额与延迟。
    """
    if provider_name() != "amap":
        return []
    cache_key = f"{round(lat, 2)}|{round(lng, 2)}|{int(radius_km)}|{types}|{keyword}|{sortrule}|{pages}"
    cached = _AROUND_CACHE.get(cache_key)
    if cached and cached[0] > time.time():
        return cached[1]

    pages_n = max(1, pages)
    if pages_n == 1:
        page_lists = [_fetch_around_page(1, lat, lng, radius_km, types, keyword, sortrule)]
    else:
        # 顺序 N×~1.5s → 并发约等于单次调用耗时，避免大半径下前端超时
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(pages_n, 6)) as ex:
            futures = [
                ex.submit(_fetch_around_page, p, lat, lng, radius_km, types, keyword, sortrule)
                for p in range(1, pages_n + 1)
            ]
            page_lists = [f.result() for f in futures]

    out: list[dict] = []
    seen: set[str] = set()
    for pois in page_lists:        # 保持页序：靠前页（更相关/更近）优先
        for p in pois:
            pid = str(p.get("id") or "")
            if pid and pid in seen:
                continue
            if pid:
                seen.add(pid)
            out.append(p)
    if out:
        _AROUND_CACHE[cache_key] = (time.time() + _AROUND_TTL, out)
        if len(_AROUND_CACHE) > 500:
            oldest = min(_AROUND_CACHE, key=lambda k: _AROUND_CACHE[k][0])
            _AROUND_CACHE.pop(oldest, None)
    return out


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
    if image.startswith("http://"):          # 小程序不支持 http 图片，统一 https
        image = "https://" + image[len("http://"):]
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
