"""地图 API 适配器。

方案文档第 4 章：地图 API 负责真实地点、距离、路线，但不作为长期原始数据库。
默认 stub 模式用本地坐标做 haversine 距离计算，无需密钥即可运行；
配置 MAP_PROVIDER=amap 并填入 AMAP_KEY 后接入高德地图（周边搜索 + 真实路程）。
"""
import concurrent.futures
import time
from math import asin, atan2, cos, degrees, radians, sin, sqrt

import httpx

from app.config import settings

AMAP_BASE = "https://restapi.amap.com"
AMAP_AROUND_MAX_RADIUS_KM = 50.0
# 高德 POI 类型码：风景名胜大类(含公园/动植物园) / 博物馆 / 展览馆 / 美术馆 / 科技馆
AMAP_DEFAULT_TYPES = "110000|140100|140200|140400|140600"
AMAP_TYPES_BY_SCENE: dict[str, str] = {
    "family": "110000|140100|140600|080500",
    "couple": "110000|110200|110100|140400|140200",
    "rainy": "060100|140100|140400|140600",
    "budget": "110000|140100|061000",
    "fish": "",
    "photo": "110000|140000|061000|080600",
    "night": "110000|050000|060100|080600",
    "walk": "061000|110000|140000",
    "old": "110000|140100|060100",
    "hike": "",
    "food": "050000",
    "cycle": "",
    "camp": "",
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


def amap_geocode(address: str, city: str | None = None) -> tuple[float, float] | None:
    """高德正向地理编码：地址（如"成都温江区"）→ (lat, lng)。失败返回 None。"""
    if provider_name() != "amap" or not address:
        return None
    try:
        params = {"key": settings.amap_key, "address": address}
        if city:
            params["city"] = city
        resp = httpx.get(f"{AMAP_BASE}/v3/geocode/geo", params=params, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        if str(data.get("status")) != "1":
            return None
        geocodes = data.get("geocodes") or []
        loc = (geocodes[0].get("location") if geocodes else "") or ""  # "lng,lat"
        lng_s, lat_s = loc.split(",")
        return (float(lat_s), float(lng_s))
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
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


def amap_types_for_scene(scene: str | None) -> str:
    return AMAP_TYPES_BY_SCENE.get(scene or "", AMAP_DEFAULT_TYPES)


SCENE_RADIUS_KM: dict[str, float] = {
    "fish": 30.0,   # 钓鱼场/湿地公园多在郊区，需更大半径
    "hike": 150.0,  # 山峰/景区多在远郊，周边搜索需切换到广域关键词搜索
}

# 各场景用关键词搜索命中知名目的地（数量少、分布广），配合 weight 排序横跨全半径，
# 避免在密集城区只召回最近 2km 的同质小场所
SCENE_KEYWORDS: dict[str, str] = {
    "family": "乐园|游乐园|动物园|海洋馆|主题公园|植物园|科技馆|博物馆|亲子",
    "couple": "公园|湖|景区|古镇|植物园|美术馆|博物馆|观景|江滩|花海",
    "rainy":  "博物馆|美术馆|科技馆|水族馆|海洋馆|图书馆|商场|影院",
    "budget": "公园|绿道|博物馆|广场|湖|景区|江滩",
    "night":  "夜景|江滩|绿道|夜市|酒吧街|步行街|不夜城|灯光秀|江滩公园",
    "walk":   "公园|绿道|古镇|街区|步行街|湖|江滩",
    "photo":  "古镇|景区|花海|湖|公园|植物园|美术馆|网红|打卡",
    "fish":   "钓鱼场|垂钓|钓鱼园|渔场|钓场|水库|湿地",
    "old":    "公园|景区|古镇|博物馆|植物园|寺|湖",
    "hike":   "风景区|景区|森林公园|雪山|名山",
    "food":   "美食|火锅|川菜|特色菜|小吃|本地菜|苍蝇馆子|老字号",
    "cycle":  "绿道|骑行道|自行车道|碧道|健身步道|绿道驿站|环湖路",
    "camp":   "露营|营地|帐篷|野餐|草坪|郊野公园|户外基地|房车营地|湿地公园",
}

HIKE_POSITIVE_TERMS = (
    "山", "峰", "岭", "峡", "谷", "岩", "崖", "坡", "峪", "沟",
    "登山", "爬山", "徒步", "山地",
    "森林公园", "国家森林公园", "自然保护区", "风景区",
)
HIKE_NEGATIVE_TERMS = (
    "码头", "渡口", "游船", "港", "餐厅", "饭店", "美食", "火锅", "串串",
    "天妇罗", "咖啡", "茶馆", "酒吧", "酒店", "民宿", "客栈", "商场",
    "购物", "商业街", "小区", "学校", "医院", "车站", "停车场", "湿地",
    "水库", "湖", "滨河", "江滩", "游乐园", "水上乐园", "寺", "庙",
    "道观", "禅院", "禅林", "清真寺", "教堂", "楼", "塔", "遗址",
    "大桥", "桥", "立交", "隧道", "收费站",
    # 餐饮/甜品/饮品（品牌名常含"爬山/登山"，如"爬山熊猫甜品蛋糕"）
    "甜品", "蛋糕", "烘焙", "面包", "饮品", "奶茶", "零食", "小吃", "烧烤", "雪糕",
    # 公司/机构/服务类（非出游目的地，避免"爬山虎人力资源/登山协会/汽修"误召回）
    "爬山虎", "人力资源", "公司", "企业", "集团", "协会", "俱乐部", "中介",
    "汽车", "汽修", "维修", "4S", "培训", "教育", "装饰", "建材", "五金",
    "超市", "便利店", "银行", "营业厅", "办公", "物业", "美容", "健身",
    "经营部", "服务部", "商行", "门市", "工作室", "事务所", "诊所", "药房",
    # 登山口/小道/设施类——只是山的入口或步道，不是目的地本体（用户要山岳/景区本体）
    "登山口", "登山道", "登山入口", "入口", "起点", "检票", "售票", "停车",
    "服务中心", "驿站", "休息点", "农家乐", "步道", "游步道", "徒步路线", "徒步起点",
    # 道路/广场/缆车/观景台/市集/露营等——名字带"雪山/XX山"但本身不是山岳目的地
    "大道", "广场", "索道", "缆车", "观景台", "市集", "露营", "度假区", "停车场",
)


def is_hike_destination(name: str | None,
                        category: str | None = None,
                        tags: list[str] | None = None,
                        address: str | None = None) -> bool:
    """登山场景只保留山岳/徒步类目的地，剔除码头、餐饮、普通公园等误召回。"""
    visible_text = " ".join([name or "", category or "", " ".join(tags or [])])
    text = " ".join([visible_text, address or ""])
    if not text.strip():
        return False
    if any(term in text for term in HIKE_NEGATIVE_TERMS):
        return False
    if "公园" in text and not any(term in visible_text for term in ("森林公园", "国家森林公园", "自然保护区")):
        return False
    return any(term in visible_text for term in HIKE_POSITIVE_TERMS)


# 美食场景：通用过滤之外再剔除纯饮品/连锁奶茶咖啡，突出正餐与特色馆子
# （便利店/超市已由 _NON_DEST_SERVICE_TERMS 在 is_outing_destination 里剔除，不重复）
_FOOD_NOISE_TERMS = (
    "星巴克", "瑞幸", "蜜雪冰城", "喜茶", "奈雪", "古茗", "茶百道", "霸王茶姬",
    "书亦", "益禾堂", "沪上阿姨", "1点点", "coco", "奶茶", "茶饮", "饮品",
    # 西式/连锁快餐——非本地出游美食目的地
    "麦当劳", "肯德基", "汉堡王", "汉堡", "必胜客", "披萨", "德克士", "华莱士", "塔斯汀",
)


def is_food_destination(name: str | None, category: str | None = None,
                        tags: list[str] | None = None) -> bool:
    """美食场景过滤：剔除纯饮品/连锁奶茶咖啡店，让正餐/特色馆子先行。"""
    text = " ".join([name or "", category or "", " ".join(tags or [])])
    return not any(t in text for t in _FOOD_NOISE_TERMS)


# 夜晚场景：剔除奶茶/商场，以及光叫"观景台/广场"没有具体身份的通用点
_NIGHT_NOISE_TERMS = (
    "茶百道", "蜜雪", "星巴克", "瑞幸", "奶茶", "茶饮", "便利店", "超市",
    "购物中心", "商场", "咖啡", "椰", "蛋糕", "烘焙", "面包",
)
_NIGHT_GENERIC_NAMES = (
    "观景台", "观景塔", "观景平台", "观景长廊", "观景点", "观景", "夜景", "码头", "广场",
)


def is_night_destination(name: str | None, category: str | None = None,
                         tags: list[str] | None = None) -> bool:
    """夜晚场景过滤：去掉商场/通用观景点名，以及（复用美食负向词）奶茶/快餐连锁
    ——它们常带"(XX滨江店)"后缀蹭进来。"""
    if (name or "").strip() in _NIGHT_GENERIC_NAMES:
        return False
    text = " ".join([name or "", category or "", " ".join(tags or [])])
    return not any(t in text for t in _NIGHT_NOISE_TERMS + _FOOD_NOISE_TERMS)


# 骑行场景：只保留绿道/骑行道，剔除关键词命中的沿线设施与非骑行点
CYCLE_POSITIVE_TERMS = (
    "绿道", "骑行", "自行车", "碧道", "步道", "健身道", "环湖路", "滨江路", "滨河路",
)
CYCLE_NEGATIVE_TERMS = (
    "店", "租赁", "租车", "公交", "地铁", "停车", "雕塑", "雕像", "博物", "乐园", "游乐", "营地",
    "售楼", "楼盘", "出租", "出售", "房产", "篮球", "网球", "厕所", "公厕",
    "卫生间", "公测", "加油", "服务区", "收费", "大门", "入口", "牌坊", "管理处",
)


def is_cycle_destination(name: str | None, category: str | None = None,
                         tags: list[str] | None = None) -> bool:
    """骑行场景：只保留绿道/骑行道，剔除沿线公交站/停车场/雕塑/乐园/营地/售楼等。"""
    text = " ".join([name or "", category or "", " ".join(tags or [])])
    if any(t in text for t in CYCLE_NEGATIVE_TERMS):
        return False
    return any(t in text for t in CYCLE_POSITIVE_TERMS)


# 露营场景：只保留营地/草坪/户外，剔除装备店/夏令营培训/设施等不相关内容
CAMP_POSITIVE_TERMS = (
    "露营", "营地", "帐篷", "野餐", "草坪", "草地", "郊野", "户外", "房车营", "湿地",
)
CAMP_NEGATIVE_TERMS = (
    "店", "销售", "批发", "专卖", "用品", "装备", "设备", "器材", "租赁", "租车",
    "夏令营", "拓展", "驾校", "公交", "地铁", "停车", "雕塑", "售楼",
    "楼盘", "出租", "出售", "厕所", "公厕", "管理处",
)


def is_camp_destination(name: str | None, category: str | None = None,
                        tags: list[str] | None = None) -> bool:
    """露营场景：只保留营地/草坪/户外点，剔除装备店/夏令营/设施等不相关内容。"""
    text = " ".join([name or "", category or "", " ".join(tags or [])])
    if any(t in text for t in CAMP_NEGATIVE_TERMS):
        return False
    return any(t in text for t in CAMP_POSITIVE_TERMS)


# 钓鱼场景：剔除渔具/钓具店等售卖类（"飞度渔具"这种不是钓点）
FISH_NEGATIVE_TERMS = ("渔具", "钓具", "装备", "用品", "器材", "专卖", "销售", "批发", "商行")


def is_fish_destination(name: str | None, category: str | None = None,
                        tags: list[str] | None = None) -> bool:
    """钓鱼场景：剔除渔具/钓具售卖店，只留真实钓点。"""
    text = " ".join([name or "", category or "", " ".join(tags or [])])
    return not any(t in text for t in FISH_NEGATIVE_TERMS)


# 通用"非出游目的地"过滤：去类型搜索后会混进餐馆/公司/汽修等，按高德顶级类别+名称剔除
_NON_DEST_CATEGORIES = ("公司企业", "汽车", "金融", "保险", "医疗", "政府")
# 餐饮类词：一般场景算噪声剔除，但「美食」场景下这些正是目的地 → allow_food 豁免
_NON_DEST_FOOD_TERMS = (
    "米铺", "米线", "面馆", "牛肉", "餐厅", "饭店", "餐馆", "小吃", "火锅",
    "烧烤", "串串", "烤肉", "快餐", "食府", "茶楼",
)
# 服务/商业类词：任何出游场景都不是目的地，始终剔除
_NON_DEST_SERVICE_TERMS = (
    "网吧", "棋牌", "KTV", "4S", "汽修", "汽配", "维修", "装饰", "建材", "五金",
    "超市", "便利店", "药房", "药店", "诊所", "美容", "美发", "理发", "人力资源",
    "协会", "俱乐部", "中介", "事务所", "工作室", "经营部", "服务部", "门市",
    "商行", "物业", "培训", "健身房", "爬山虎", "公司", "营业厅",
)


def is_outing_destination(name: str | None, category: str | None = None,
                          tags: list[str] | None = None, address: str | None = None,
                          allow_food: bool = False) -> bool:
    """通用过滤：剔除餐馆/公司/汽修/服务类等非出游目的地（所有场景共用）。
    allow_food=True（美食场景）时保留餐饮类，只剔除服务/商业类。"""
    cat = category or ""
    if any(c in cat for c in _NON_DEST_CATEGORIES):
        return False
    text = " ".join([name or "", cat, " ".join(tags or [])])
    if not allow_food and any(t in text for t in _NON_DEST_FOOD_TERMS):
        return False
    return not any(t in text for t in _NON_DEST_SERVICE_TERMS)


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
        "radius": int(min(radius_km, AMAP_AROUND_MAX_RADIUS_KM) * 1000),
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


def _fetch_text_page(page: int, city: str | None, types: str, keyword: str) -> list[dict]:
    """抓取关键字搜索单页，失败/无结果返回 []。用于超过周边搜索半径上限的场景。"""
    params = {
        "key": settings.amap_key,
        "types": types,
        "offset": 25,
        "page": page,
        "extensions": "all",
        "citylimit": "false",
    }
    if keyword:
        params["keywords"] = keyword
    if city:
        params["city"] = normalize_city(city)
    try:
        resp = httpx.get(f"{AMAP_BASE}/v3/place/text", params=params, timeout=8.0)
        resp.raise_for_status()
        data = resp.json()
        if str(data.get("status")) != "1":
            return []
        return data.get("pois") or []
    except (httpx.HTTPError, ValueError):
        return []


def amap_search_text(city: str | None,
                     types: str = AMAP_DEFAULT_TYPES,
                     keyword: str = "",
                     pages: int = 1) -> list[dict]:
    """高德关键字搜索，返回原始 POI 列表。用于 50km 以上的广域场景搜索。"""
    if provider_name() != "amap":
        return []
    pages_n = max(1, pages)
    cache_key = f"text|{normalize_city(city)}|{types}|{keyword}|{pages_n}"
    cached = _AROUND_CACHE.get(cache_key)
    if cached and cached[0] > time.time():
        return cached[1]

    if pages_n == 1:
        page_lists = [_fetch_text_page(1, city, types, keyword)]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(pages_n, 6)) as ex:
            futures = [
                ex.submit(_fetch_text_page, p, city, types, keyword)
                for p in range(1, pages_n + 1)
            ]
            page_lists = [f.result() for f in futures]

    out: list[dict] = []
    seen: set[str] = set()
    for pois in page_lists:
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


def _offset_latlng(lat: float, lng: float, dist_km: float, bearing_deg: float) -> tuple[float, float]:
    """从 (lat,lng) 沿 bearing 方向偏移 dist_km，返回新坐标。"""
    r = 6371.0
    br = radians(bearing_deg)
    lat1, lng1 = radians(lat), radians(lng)
    dr = dist_km / r
    lat2 = asin(sin(lat1) * cos(dr) + cos(lat1) * sin(dr) * cos(br))
    lng2 = lng1 + atan2(sin(br) * sin(dr) * cos(lat1), cos(dr) - sin(lat1) * sin(lat2))
    return degrees(lat2), degrees(lng2)


def amap_search_spread(lat: float, lng: float, radius_km: float,
                       types: str = AMAP_DEFAULT_TYPES, sortrule: str = "weight",
                       pages: int = 1) -> list[dict]:
    """距离分段采样：中心搜近处热门点 + 在 ~0.6R 处一圈偏移中心并发各搜一圈，
    把郊区远点也召回。密集城区只在中心搜会全堆在 2-4km，这样能铺满整个半径。
    radius<=8km 退化为普通中心搜索。"""
    tasks: list[tuple[float, float, float, int]] = [(lat, lng, min(radius_km, 8.0), pages)]
    if radius_km > 8:
        ring = radius_km * 0.6
        band = max(radius_km * 0.5, 6.0)
        for bearing in (0, 72, 144, 216, 288):
            olat, olng = _offset_latlng(lat, lng, ring, bearing)
            tasks.append((olat, olng, band, 1))

    def run(t: tuple) -> list[dict]:
        return amap_search_around(t[0], t[1], radius_km=t[2], types=types,
                                  sortrule=sortrule, pages=t[3])

    if len(tasks) == 1:
        return run(tasks[0])
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tasks), 6)) as ex:
        results = list(ex.map(run, tasks))
    out: list[dict] = []
    seen: set[str] = set()
    for items in results:
        for p in items:
            pid = str(p.get("id") or "")
            if pid and pid in seen:
                continue
            if pid:
                seen.add(pid)
            out.append(p)
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
