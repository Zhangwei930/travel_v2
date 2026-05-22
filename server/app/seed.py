"""种子数据 — 与前端 src/api/mock.js 对齐，空库时自动灌入，方便联调。"""
from sqlalchemy.orm import Session

from app.models import FaqKnowledge, PoiIndex, TravelKnowledge, TravelRoute

_POIS = [
    {
        "name": "新疆博物馆", "category": "博物馆·室内", "lat": 43.8419, "lng": 87.5683,
        "kn": {
            "display_no": "NO.001", "scene_ids": ["family", "budget", "rainy", "old"],
            "scene_tags": ["亲子", "雨天", "文化"], "play_duration": "2-3h", "budget_level": "免费",
            "recommend_reason": "室内不受天气影响，了解新疆历史文化",
            "cover_image": "https://picsum.photos/seed/zn1/400/300",
            "suitable_people": ["亲子", "学生", "外地游客"], "suitable_weather": ["雨天", "炎热", "室内"],
            "best_time": "上午·下午",
            "avoid_tips": "节假日人多，建议提前到达；馆内禁止使用闪光灯；展厅较大，预留充足时间",
            "route_suggestion": "上午博物馆，中午附近餐饮，下午水磨沟公园",
        },
    },
    {
        "name": "红山公园", "category": "公园·登高", "lat": 43.8089, "lng": 87.6010,
        "kn": {
            "display_no": "NO.002", "scene_ids": ["couple", "walk", "budget", "photo", "night"],
            "scene_tags": ["Citywalk", "晨练", "拍照"], "play_duration": "1-2h", "budget_level": "免费",
            "recommend_reason": "乌鲁木齐市标，登高俯瞰城市全景",
            "cover_image": "https://picsum.photos/seed/zn2/400/300",
            "suitable_people": ["情侣", "朋友", "老人"], "suitable_weather": ["晴天", "户外"],
            "best_time": "清晨·傍晚",
            "avoid_tips": "登高路段较陡，老人小孩注意安全；傍晚风大注意保暖",
            "route_suggestion": "红山夜景接大巴扎晚餐",
        },
    },
    {
        "name": "柴窝堡水库", "category": "水库·钓点", "lat": 43.5667, "lng": 88.0833,
        "kn": {
            "display_no": "NO.003", "scene_ids": ["fish"],
            "scene_tags": ["钓鱼", "自然", "自驾"], "play_duration": "半日", "budget_level": "低预算",
            "recommend_reason": "周边知名钓点，鱼种丰富，自驾可达",
            "cover_image": "https://picsum.photos/seed/zn3/400/300",
            "suitable_people": ["朋友", "独自出行"], "suitable_weather": ["晴天", "户外"],
            "best_time": "清晨",
            "avoid_tips": "限钓政策以管理处实时通告为准；岸边蚊虫多需防虫液；强风时段注意防风",
            "route_suggestion": "清晨出发下竿，中午岸边野餐，傍晚返程",
        },
    },
    {
        "name": "水磨沟公园", "category": "公园·清晨", "lat": 43.8267, "lng": 87.6500,
        "kn": {
            "display_no": "NO.004", "scene_ids": ["family", "walk", "budget", "old"],
            "scene_tags": ["自然", "亲子", "晨练"], "play_duration": "2-3h", "budget_level": "免费",
            "recommend_reason": "清晨适合散步，水景宜人，人少",
            "cover_image": "https://picsum.photos/seed/zn4/400/300",
            "suitable_people": ["亲子", "老人"], "suitable_weather": ["晴天", "户外"],
            "best_time": "清晨·上午",
            "avoid_tips": "雨后路面湿滑注意防滑；自备饮用水",
            "route_suggestion": "公园散步接周边室内活动",
        },
    },
    {
        "name": "国际大巴扎", "category": "购物·文化", "lat": 43.7800, "lng": 87.6150,
        "kn": {
            "display_no": "NO.005", "scene_ids": ["couple", "rainy", "photo", "night"],
            "scene_tags": ["美食", "拍照", "购物"], "play_duration": "2h", "budget_level": "中等",
            "recommend_reason": "西域文化与美食荟萃，拍照出片率高",
            "cover_image": "https://picsum.photos/seed/zn5/400/300",
            "suitable_people": ["情侣", "朋友", "外地游客"], "suitable_weather": ["雨天", "室内"],
            "best_time": "傍晚·晚上",
            "avoid_tips": "购物注意比价；节假日人流密集，看护好随身物品",
            "route_suggestion": "大巴扎晚餐接咖啡店夜游",
        },
    },
]

_ROUTES = [
    {
        "title": "亲子半日游", "scene": "family", "scene_label": "亲子", "color": "#FF6B35",
        "display_no": "R-01", "duration": "半日", "budget_level": "低",
        "poi_names": ["新疆博物馆", "水磨沟公园"],
        "route_text": "博物馆+本地餐饮+公园，全程室内/近距，孩子不累",
        "tips": "如孩子疲惫或天气变化，可缩短公园行程改为室内休息。",
    },
    {
        "title": "柴窝堡钓鱼一日", "scene": "fish", "scene_label": "钓鱼", "color": "#3E5C3A",
        "display_no": "R-02", "duration": "一日", "budget_level": "中",
        "poi_names": ["柴窝堡水库"],
        "route_text": "清晨出发→水库下竿→中午岸边野餐→傍晚返程",
        "tips": "若清晨刮 4 级以上大风，改为水磨沟公园+室内活动；水位变化无鱼讯可转点下游小水库。",
    },
    {
        "title": "情侣夜游线", "scene": "couple", "scene_label": "情侣", "color": "#EC4B85",
        "display_no": "R-03", "duration": "夜晚", "budget_level": "中",
        "poi_names": ["红山公园", "国际大巴扎"],
        "route_text": "红山夜景→大巴扎晚餐→咖啡店",
        "tips": "夜间气温偏低注意保暖；末班公交较早，建议规划好返程。",
    },
    {
        "title": "低预算 Citywalk", "scene": "walk", "scene_label": "Citywalk", "color": "#4FD1C5",
        "display_no": "R-04", "duration": "一日", "budget_level": "免费",
        "poi_names": ["新疆博物馆", "红山公园", "水磨沟公园"],
        "route_text": "公园+老街+二道桥，全程公交可达",
        "tips": "全程步行较多，建议穿舒适鞋；夏季注意防晒补水。",
    },
]

_FAQS = [
    {
        "question": "钓点限钓吗？", "category": "推荐逻辑",
        "answer": "柴窝堡等水库是否限钓以管理处实时通告为准，出发前建议通过官方渠道或地图实时查询确认。",
        "keywords": ["钓点", "限钓", "钓鱼"],
    },
    {
        "question": "需要钓鱼证吗？", "category": "推荐逻辑",
        "answer": "部分水域需办理垂钓许可，是否需要钓鱼证以当地渔政及管理处规定为准，请提前咨询确认。",
        "keywords": ["钓鱼证", "钓鱼", "证"],
    },
    {
        "question": "停车方便吗？", "category": "停车",
        "answer": "大部分景点设有停车场，但节假日车位紧张。具体停车位置和收费以地图实时信息为准，建议错峰前往。",
        "keywords": ["停车", "车位", "方便"],
    },
    {
        "question": "下雨改去哪？", "category": "天气",
        "answer": "雨天推荐室内场所：新疆博物馆、国际大巴扎等，既不受天气影响又适合亲子和情侣出游。",
        "keywords": ["下雨", "雨天", "改去"],
    },
    {
        "question": "适合带孩子吗？", "category": "推荐逻辑",
        "answer": "新疆博物馆、水磨沟公园等强度较低、安全性好，适合带孩子。建议选择上午时段，避开人流高峰。",
        "keywords": ["孩子", "亲子", "带娃", "适合"],
    },
    {
        "question": "傍晚还能玩什么？", "category": "推荐逻辑",
        "answer": "傍晚推荐红山公园看夜景、国际大巴扎逛夜市，灯光氛围好、适合拍照和情侣夜游。",
        "keywords": ["傍晚", "夜游", "晚上", "玩什么"],
    },
    {
        "question": "门票多少钱？", "category": "门票",
        "answer": "各景点票价不同，部分公园博物馆免费。具体票价和优惠政策以景区官方公告为准，本系统不提供实时报价。",
        "keywords": ["门票", "票价", "多少钱"],
    },
]


def seed_if_empty(db: Session) -> None:
    if db.query(PoiIndex).count() > 0:
        return

    poi_ids_by_name: dict[str, int] = {}
    for item in _POIS:
        poi = PoiIndex(
            provider="stub", name=item["name"], city="乌鲁木齐",
            category=item["category"], lat=item["lat"], lng=item["lng"], source="seed",
        )
        db.add(poi)
        db.flush()
        poi_ids_by_name[poi.name] = poi.id
        db.add(TravelKnowledge(poi_id=poi.id, content_source="人工", review_status="approved", **item["kn"]))

    for r in _ROUTES:
        route = dict(r)
        poi_names = route.pop("poi_names")
        route["poi_ids"] = [poi_ids_by_name[name] for name in poi_names]
        db.add(TravelRoute(city="乌鲁木齐", review_status="approved", **route))

    for f in _FAQS:
        db.add(FaqKnowledge(city="乌鲁木齐", review_status="approved", **f))

    db.commit()
