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
