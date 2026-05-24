"""种子数据 — 与前端 src/api/mock.js 对齐，空库时自动灌入，方便联调。"""
from sqlalchemy.orm import Session

from app.models import FaqKnowledge, PoiIndex, TravelKnowledge, TravelRoute

_POIS = [
    {
        "name": "成都博物馆", "category": "博物馆·室内", "lat": 30.6570, "lng": 104.0650,
        "kn": {
            "display_no": "NO.001", "scene_ids": ["family", "budget", "rainy", "old"],
            "scene_tags": ["亲子", "雨天", "文化"], "play_duration": "2-3h", "budget_level": "免费",
            "recommend_reason": "室内不受天气影响，适合了解成都城市历史文化",
            "suitable_people": ["亲子", "学生", "外地游客"], "suitable_weather": ["雨天", "炎热", "室内"],
            "best_time": "上午·下午",
            "avoid_tips": "节假日人多，建议提前到达；馆内禁止使用闪光灯；展厅较大，预留充足时间",
            "route_suggestion": "上午博物馆，中午附近餐饮，下午人民公园或宽窄巷子",
        },
    },
    {
        "name": "人民公园", "category": "公园·茶馆", "lat": 30.6599, "lng": 104.0584,
        "kn": {
            "display_no": "NO.002", "scene_ids": ["couple", "walk", "budget", "photo", "night"],
            "scene_tags": ["Citywalk", "茶馆", "拍照"], "play_duration": "1-2h", "budget_level": "低预算",
            "recommend_reason": "成都老牌城市公园，适合喝茶、散步和感受本地生活",
            "suitable_people": ["情侣", "朋友", "老人"], "suitable_weather": ["晴天", "户外"],
            "best_time": "清晨·傍晚",
            "avoid_tips": "周末茶馆人多，热门座位建议错峰；看管好随身物品",
            "route_suggestion": "人民公园喝茶接宽窄巷子 Citywalk",
        },
    },
    {
        "name": "兴隆湖", "category": "湖泊·骑行", "lat": 30.4069, "lng": 104.0866,
        "kn": {
            "display_no": "NO.003", "scene_ids": ["fish"],
            "scene_tags": ["湖畔", "自然", "骑行"], "play_duration": "半日", "budget_level": "低预算",
            "recommend_reason": "湖畔空间开阔，适合骑行、散步和轻户外",
            "suitable_people": ["朋友", "独自出行"], "suitable_weather": ["晴天", "户外"],
            "best_time": "上午·傍晚",
            "avoid_tips": "环湖距离较长，注意补水防晒；水域管理政策以现场公告为准",
            "route_suggestion": "上午环湖骑行，中午湖区简餐，傍晚返程",
        },
    },
    {
        "name": "浣花溪公园", "category": "公园·亲子", "lat": 30.6610, "lng": 104.0283,
        "kn": {
            "display_no": "NO.004", "scene_ids": ["family", "walk", "budget", "old"],
            "scene_tags": ["自然", "亲子", "晨练"], "play_duration": "2-3h", "budget_level": "免费",
            "recommend_reason": "绿地和水景丰富，适合亲子散步和轻松拍照",
            "suitable_people": ["亲子", "老人"], "suitable_weather": ["晴天", "户外"],
            "best_time": "清晨·上午",
            "avoid_tips": "雨后路面湿滑注意防滑；自备饮用水",
            "route_suggestion": "公园散步接杜甫草堂或附近餐饮",
        },
    },
    {
        "name": "锦里古街", "category": "美食·文化", "lat": 30.6467, "lng": 104.0472,
        "kn": {
            "display_no": "NO.005", "scene_ids": ["couple", "rainy", "photo", "night"],
            "scene_tags": ["美食", "拍照", "购物"], "play_duration": "2h", "budget_level": "中等",
            "recommend_reason": "成都传统街区氛围浓，适合夜游、拍照和尝小吃",
            "suitable_people": ["情侣", "朋友", "外地游客"], "suitable_weather": ["雨天", "室内"],
            "best_time": "傍晚·晚上",
            "avoid_tips": "购物注意比价；节假日人流密集，看护好随身物品",
            "route_suggestion": "锦里晚餐接武侯祠周边夜游",
        },
    },
]

_ROUTES = [
    {
        "title": "亲子半日游", "scene": "family", "scene_label": "亲子", "color": "#FF6B35",
        "display_no": "R-01", "duration": "半日", "budget_level": "低",
        "poi_names": ["成都博物馆", "浣花溪公园"],
        "route_text": "博物馆+本地餐饮+公园，全程室内/近距，孩子不累",
        "tips": "如孩子疲惫或天气变化，可缩短公园行程改为室内休息。",
    },
    {
        "title": "兴隆湖轻户外半日", "scene": "fish", "scene_label": "湖畔", "color": "#3E5C3A",
        "display_no": "R-02", "duration": "半日", "budget_level": "低",
        "poi_names": ["兴隆湖"],
        "route_text": "上午环湖散步或骑行→湖区简餐→傍晚返程",
        "tips": "水域活动和垂钓政策以现场管理公告为准；夏季注意防晒补水。",
    },
    {
        "title": "情侣夜游线", "scene": "couple", "scene_label": "情侣", "color": "#EC4B85",
        "display_no": "R-03", "duration": "夜晚", "budget_level": "中",
        "poi_names": ["人民公园", "锦里古街"],
        "route_text": "人民公园喝茶→锦里晚餐→武侯祠周边夜游",
        "tips": "夜间气温偏低注意保暖；末班公交较早，建议规划好返程。",
    },
    {
        "title": "低预算 Citywalk", "scene": "walk", "scene_label": "Citywalk", "color": "#4FD1C5",
        "display_no": "R-04", "duration": "一日", "budget_level": "免费",
        "poi_names": ["成都博物馆", "人民公园", "锦里古街"],
        "route_text": "博物馆+公园+老街，全程公交可达",
        "tips": "全程步行较多，建议穿舒适鞋；夏季注意防晒补水。",
    },
]

_FAQS = [
    {
        "question": "钓点限钓吗？", "category": "推荐逻辑",
        "answer": "成都周边水域是否允许垂钓以管理处实时通告为准，出发前建议通过官方渠道或地图实时查询确认。",
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
        "answer": "雨天推荐室内场所：成都博物馆、四川博物院、商场街区等，既不受天气影响又适合亲子和情侣出游。",
        "keywords": ["下雨", "雨天", "改去"],
    },
    {
        "question": "适合带孩子吗？", "category": "推荐逻辑",
        "answer": "成都博物馆、浣花溪公园等强度较低、安全性好，适合带孩子。建议选择上午时段，避开人流高峰。",
        "keywords": ["孩子", "亲子", "带娃", "适合"],
    },
    {
        "question": "傍晚还能玩什么？", "category": "推荐逻辑",
        "answer": "傍晚推荐人民公园喝茶、锦里古街夜游或春熙路太古里逛街，氛围好、适合拍照和情侣出游。",
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
            provider="stub", name=item["name"], city="成都",
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
        db.add(TravelRoute(city="成都", review_status="approved", **route))

    for f in _FAQS:
        db.add(FaqKnowledge(city="成都", review_status="approved", **f))

    db.commit()
