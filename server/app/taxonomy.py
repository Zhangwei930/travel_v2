"""场景与标签体系 — 对应方案文档附录 A。场景为固定分类，不入库。"""

SCENES: list[dict] = [
    {"id": "family", "no": "01", "label": "亲子游", "icon": "👨‍👩‍👧", "color": "#FF6B35", "desc": "轻松不太累"},
    {"id": "couple", "no": "02", "label": "情侣约会", "icon": "💑", "color": "#EC4B85", "desc": "拍照·夜游"},
    {"id": "rainy", "no": "03", "label": "雨天室内", "icon": "☔️", "color": "#5B7CFA", "desc": "博物馆·商场"},
    {"id": "budget", "no": "04", "label": "低预算", "icon": "🪙", "color": "#4FD1C5", "desc": "免费·Citywalk"},
    {"id": "fish", "no": "05", "label": "钓鱼", "icon": "🎣", "color": "#3E5C3A", "desc": "水库·黄金时段"},
    {"id": "photo", "no": "06", "label": "拍照打卡", "icon": "📸", "color": "#A855F7", "desc": "地标·出片"},
    {"id": "night", "no": "07", "label": "夜游", "icon": "🌃", "color": "#1F2937", "desc": "夜市·灯光"},
    {"id": "walk", "no": "08", "label": "Citywalk", "icon": "🚶", "color": "#84CC16", "desc": "慢走·人文"},
    {"id": "old", "no": "09", "label": "适老", "icon": "👵", "color": "#F4B942", "desc": "轻量·无障碍"},
]

SCENE_LABELS: dict[str, str] = {s["id"]: s["label"] for s in SCENES}
SCENE_COLORS: dict[str, str] = {s["id"]: s["color"] for s in SCENES}


# ─── 装备清单（单一权威字典，供 /api/gear/list 与 /api/trip/generate 共用）──────
# 历史上 trip_service.py 和 routers/gear.py 各维护一份，导致同场景在两个接口返回不同。
# 现在统一在此处维护，两侧 import 即可。
GEAR_BY_SCENE: dict[str, list[str]] = {
    "fish":   ["钓竿×2", "鱼饵(蚯蚓/玉米)", "折叠椅", "遮阳帽", "防虫液", "保温水壶", "垃圾袋"],
    "family": ["儿童水壶", "湿巾", "防晒霜", "创可贴", "零食", "雨伞", "备用衣物"],
    "couple": ["相机/手机支架", "充电宝", "外套", "纸巾"],
    "rainy":  ["雨伞", "防滑鞋", "防水鞋套", "干毛巾", "充电宝", "口罩"],
    "budget": ["交通卡", "保温水壶", "舒适步行鞋", "零钱"],
    "photo":  ["相机/手机", "充电宝", "三脚架", "备用电池", "镜头布"],
    "night":  ["保暖外套", "手电筒/手机灯", "充电宝", "纸巾"],
    "walk":   ["舒适运动鞋", "保温水壶", "防晒霜", "小背包"],
    "old":    ["保温水壶", "常用药", "防滑鞋", "折叠凳"],
}
DEFAULT_GEAR: list[str] = ["身份证", "充电宝", "保温水壶", "纸巾", "常用药品"]
