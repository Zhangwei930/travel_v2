"""出游助手问答 — 对应方案文档 6.2 客服问答 / 6.3 知识缺失补充工作流。

命中 FAQ/知识库 → 直接回答；未命中 → WebSearch + AI 总结 → 写入 kb_pending 待审核。
"""
import datetime
import re
from sqlalchemy.orm import Session

from app.config import settings
from app.models import FaqKnowledge, PoiIndex, TravelKnowledge
from app.schemas import AskIn, AskOut, AskSource, ChatTurn
from app.services import ai_provider, map_provider, websearch
from app.services.recommend_service import recommend_pois
from app.services.route_builder import build_home_routes
from app.services.weather_provider import get_weather


def _time_slot() -> str:
    h = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).hour
    if h < 11:
        return "上午"
    if h < 14:
        return "中午"
    if h < 18:
        return "下午"
    return "夜晚"


def _city_matches(row_city: str | None, requested_city: str | None) -> bool:
    if not row_city:
        return True
    return map_provider.normalize_city(row_city) == map_provider.normalize_city(requested_city)


def _score(question: str, faq: FaqKnowledge) -> float:
    """简易相似度：字面重合 + 关键词命中比例。生产环境替换为向量检索。"""
    # FAQ 原问题（去尾部标点）整体出现在用户问题中，视为强命中
    faq_q = (faq.question or "").rstrip("？?。.！! ")
    if faq_q and faq_q in question:
        return 1.0
    keywords = faq.keywords or []
    if not keywords:
        return 0.0
    hit = sum(1 for k in keywords if k and k in question)
    return hit / len(keywords)


_AREA_RE = re.compile(r"([一-龥]{2,5}?(?:区|县|镇|新区))")
# "X附近/周边/一带"里的地标（如"温江金马河附近"→温江金马河，可直接地理编码）
_NEARBY_RE = re.compile(r"([一-龥]{2,8})(?:附近|周边|周围|那边|一带)")
_LOC_PREFIX_RE = re.compile(r"^(带我去|我想去|我要去|想去|要去|我们|咱们|想在|这边|那边|这|那|在)")
# 这些词不是可定位地点，别拿去地理编码（否则误定位/白跑一次高德）
_AREA_BLOCKLIST = ("小区", "市区", "景区", "郊区", "社区", "地区", "园区",
                   "城区", "片区", "辖区", "库区", "山区", "林区", "矿区",
                   "公司", "单位", "我家", "学校", "这里", "那里", "附近", "周边")


def _area_in_question(question: str | None) -> str:
    """问题里的地点（行政区，或"X附近"里的地标，如"温江区"/"温江金马河"），用于把
    推荐定位到那里而非用户当前位置。剔除 小区/市区/公司 等非地点误命中。"""
    q = question or ""
    if not q:
        return ""
    # 优先"X附近/周边"里的地标
    m = _NEARBY_RE.search(q)
    if m:
        loc = _LOC_PREFIX_RE.sub("", m.group(1))
        if len(loc) >= 2 and not any(b in loc for b in _AREA_BLOCKLIST):
            return loc
    # 其次行政区/县/镇
    for mm in _AREA_RE.finditer(q):
        area = mm.group(1)
        if not any(b in area for b in _AREA_BLOCKLIST):
            return area
    return ""


# 自由文本里推断场景，让卡片搜对类型（露营→营地，带孩子→亲子点）。
# 活动类（露营/骑行/钓鱼/登山/美食）放前面，比人群类（带孩子）优先，
# 这样"带孩子露营"按露营搜而不是亲子点。
_SCENE_HINTS = [
    ("camp", ("露营", "营地", "野营", "扎营", "帐篷")),
    ("cycle", ("骑行", "绿道", "自行车道")),
    ("fish", ("钓鱼", "垂钓")),
    ("hike", ("登山", "爬山", "徒步", "爬坡")),
    ("food", ("美食", "好吃", "餐厅", "吃饭", "馆子", "火锅")),
    ("photo", ("拍照", "打卡", "出片")),
    ("family", ("带孩子", "亲子", "小孩", "儿童", "娃", "宝宝")),
    ("couple", ("情侣", "约会")),
    ("rainy", ("雨天", "下雨", "室内")),
    ("night", ("夜市", "夜游", "夜景")),
]


def _infer_scene(question: str | None) -> str | None:
    if not question:
        return None
    for scene, kws in _SCENE_HINTS:
        if any(k in question for k in kws):
            return scene
    return None


_MAX_KM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:公里|千米|km|KM|Km)")


def _max_km_in_question(question: str | None) -> float | None:
    """问题里的距离上限（如"附近10公里内"→10.0）；"X公里外"不算上限。"""
    if not question:
        return None
    m = _MAX_KM_RE.search(question)
    if not m or question[m.end():m.end() + 1] == "外":
        return None
    try:
        km = float(m.group(1))
    except ValueError:
        return None
    return km if 0 < km <= 100 else None


def _location_cards(payload: AskIn, city: str, db: Session):
    # 用户问到某个区/县/镇/地标时，把搜索点定位到那里；否则用用户当前位置
    search_lat, search_lng = payload.lat, payload.lng
    area = _area_in_question(payload.question)
    if area:
        coords = map_provider.amap_geocode(f"{city}{area}", city=city)
        if coords:
            search_lat, search_lng = coords
    if search_lat is None or search_lng is None:
        return [], []

    # "X公里内"显式上限优先；否则问到区域用 20km 覆盖整片、就近用 15km
    max_km = _max_km_in_question(payload.question)
    search_radius = max_km or (20.0 if area else 15.0)
    search_pages = 2

    # 场景：当前问句优先；当前没说则看上文（"附近露营"→"10公里内"沿用露营）
    eff_scene = payload.scene or _infer_scene(payload.question)
    if not eff_scene:
        hist_text = " ".join((t.text or "") for t in (payload.history or []) if t.role == "user")
        eff_scene = _infer_scene(hist_text)

    # 优先实时高德召回附近点（带场景类型、按热度横跨半径，单页控延迟）；
    # stub/无 key 或无结果时回落到种子库 POI。
    from app.routers.home import _amap_rows  # 局部 import，避免 service↔router 顶层耦合
    # 带场景关键词搜（如"乐园|动物园|古镇"），召回知名点而非身边杂点；无场景用通用知名词
    scene_kw = (map_provider.SCENE_KEYWORDS.get(eff_scene or "", "")
                or "景点|景区|公园|古镇|绿道|网红打卡|博物馆|商圈")
    rows = _amap_rows(db, search_lat, search_lng, city, eff_scene,
                      radius_km=search_radius, pages=search_pages, sortrule="weight", keyword=scene_kw)
    from_amap = bool(rows)   # 高德热度序，用 preserve_order 直推热门点
    if not rows:
        kn_rows = db.query(TravelKnowledge).filter(TravelKnowledge.review_status == "approved").all()
        kn_by_id = {kn.poi_id: kn for kn in kn_rows if kn.poi_id}
        for poi in db.query(PoiIndex).filter(PoiIndex.provider != "amap").all():
            if poi.lat is None or poi.lng is None:
                continue
            if map_provider.normalize_city(poi.city) != map_provider.normalize_city(city):
                continue
            kn = kn_by_id.get(poi.id)
            if eff_scene and not (kn and eff_scene in (kn.scene_ids or [])):
                continue
            rows.append((poi, kn))

    weather = get_weather(city)
    # 距离以搜索点为准（就近=用户位置，问到区域=该区域），与"X公里内"过滤口径一致
    dist_origin = (search_lat, search_lng)
    destinations = recommend_pois(
        rows,
        origin=dist_origin,
        scene=eff_scene,
        weather=weather,
        limit=6,
        preserve_order=from_amap,
        max_km=max_km,
    )
    routes = build_home_routes(
        db,
        city=city,
        scene=eff_scene,
        origin=dist_origin,
        recommended=destinations,
        limit=2,
    )
    return destinations, routes


def _source_from_faq(faq: FaqKnowledge) -> AskSource:
    label = faq.category or faq.question
    return AskSource(k="知识库", v=label)


def _prepare(payload: AskIn, db: Session) -> dict:
    """决定走 KB 命中还是 LLM 兜底；LLM 时一并备好 prompt 和待审核所需数据。"""
    question = payload.question.strip()
    city = payload.city or settings.default_city
    time_now = _time_slot()

    # 上下文：优先取 history（多轮），fallback 到旧 context 字段（单条）
    history = [t for t in (payload.history or []) if (t.text or "").strip()]
    if not history and payload.context:
        history = [ChatTurn(role="user", text=payload.context.strip())]
    history = [t for t in history[-6:] if t.role in ("user", "bot")]

    # 合并查询：拼最近 user 消息 + 当前问题，让 FAQ 匹配 / WebSearch 有完整语境
    user_history = [t.text.strip() for t in history if t.role == "user"]
    merged_query = (" ".join(user_history[-2:]) + " " + question).strip() if user_history else question

    rows = db.query(FaqKnowledge).filter(FaqKnowledge.review_status == "approved").all()
    faqs = [faq for faq in rows if _city_matches(faq.city, city)]
    best: FaqKnowledge | None = None
    best_score = 0.0
    for faq in faqs:
        s = _score(merged_query, faq)
        if s > best_score:
            best, best_score = faq, s

    if best and best_score >= settings.kb_similarity_threshold:
        return {"mode": "kb", "text": best.answer, "source": _source_from_faq(best), "city": city}

    # 未命中：WebSearch + 组 prompt（命中位置/时间上下文）
    results = websearch.search(f"{city} {merged_query}", db)
    snippets = "\n".join(f"- {r['title']}：{r['snippet']}" for r in results[:5])
    fallback = "抱歉，暂时找不到相关信息，请换个说法再试试。"

    if payload.lat and payload.lng:
        location_ctx = f"用户当前位于{city}（坐标 {payload.lat:.4f}, {payload.lng:.4f}）。"
    elif city:
        location_ctx = f"用户当前在{city}。"
    else:
        location_ctx = ""
    weather_ctx = f"当前天气：{payload.weather}。" if payload.weather else ""
    if history:
        lines = [f"  {'用户' if t.role == 'user' else '助手'}：{t.text.strip()}" for t in history]
        context_block = "对话历史：\n" + "\n".join(lines) + "\n\n"
    else:
        context_block = ""

    prompt = (
        f"你是用户身边的出游小助手，帮ta找附近好玩的地方。\n"
        f"背景：{location_ctx}{weather_ctx}（现在{time_now}，仅供参考，别据此假设用户什么时候去）\n\n"
        f"回答要求：\n"
        f"- 推荐 5-6 个具体地点，每个用一句话说为啥适合（人群、远近）\n"
        f"- 除非用户明确问到时段，否则别假设ta晚上去、别硬套夜游\n"
        f"- 若问题提到时间限制（如2小时内），评估下路程+游玩来不来得及\n"
        f"- 营业时间、票价说「以实时查询为准」，别编数字或地点\n"
        f"- 别在文字里写具体距离/公里/车程数字（容易算错，下方卡片已显示真实距离），只说「离得近/有点远」即可\n"
        f"- 像跟朋友聊天那样口语、自然、简洁，220 字内；别分 Day1/Day2、别加小标题或内部术语\n\n"
        f"{context_block}"
        f"用户问题：{question}\n"
        f"参考资料：\n{snippets or '（无搜索结果）'}"
    )
    return {"mode": "llm", "prompt": prompt, "fallback": fallback,
            "results": results, "question": question, "city": city}


def _mentioned(answer: str, name: str) -> bool:
    """答案里是否提到该地点。卡名常带后缀(如"锦城公园-林坡花韵")，
    答案里多用主名("锦城公园")，故按主名(去掉 -/（/· 等后缀)匹配。"""
    if not name:
        return False
    if name in answer:
        return True
    core = re.split(r"[-（(·•|/]", name)[0].strip()
    return len(core) >= 3 and core in answer


def _inject_destinations(prompt_info: dict, destinations) -> None:
    """把卡片用的真实附近地点注入 prompt，让 LLM 只从这些点里推荐，
    保证文字推荐与下方卡片一致（避免文字推甲、卡片显示乙的"乱推"）。"""
    if prompt_info.get("mode") != "llm" or not destinations:
        return
    lines = "\n".join(f"- {d.name}（{d.distance}·{d.category}）" for d in destinations)
    prompt_info["prompt"] += (
        "\n\n【可推荐的附近地点——下方卡片就是这几个】\n"
        f"{lines}\n"
        "请把上面这些地点都推荐给用户（5-6 个），每个用一句话说明为何适合"
        "（人群/距离），不要推荐列表以外的地方。"
    )


def ask(payload: AskIn, db: Session) -> AskOut:
    p = _prepare(payload, db)
    destinations, routes = _location_cards(payload, p["city"], db)
    _inject_destinations(p, destinations)
    if p["mode"] == "kb":
        return AskOut(text=p["text"], sources=[p["source"]], chips=[], from_kb=True,
                      destinations=destinations, routes=routes, kb_status="hit")
    answer = ai_provider.generate_text(p["prompt"], fallback=p["fallback"])
    # 卡片只保留答案里实际推荐到的地点；全都没匹配上时退回前 3 个热门候选，避免 0 卡片
    picked = [d for d in destinations if _mentioned(answer, d.name)]
    destinations = picked or destinations[:3]
    websearch.create_pending(question=p["question"], answer=answer, results=p["results"],
                             city=p["city"], category="出游助手", db=db)
    return AskOut(text=answer, sources=[], chips=[], from_kb=False,
                  destinations=destinations, routes=routes, kb_status="miss")


def ask_stream_events(payload: AskIn, db: Session):
    """流式生成器：yield (event_type, data)。KB 命中即时整段返回，未命中逐字流式。"""
    p = _prepare(payload, db)
    destinations, routes = _location_cards(payload, p["city"], db)
    _inject_destinations(p, destinations)
    sources = [p["source"]] if p["mode"] == "kb" else []
    if p["mode"] == "kb":
        yield ("meta", {"from_kb": True, "kb_status": "hit", "sources": sources,
                        "destinations": destinations, "routes": routes})
        yield ("text", p["text"])
        yield ("done", None)
        return

    yield ("meta", {"from_kb": False, "kb_status": "miss", "sources": sources,
                    "destinations": destinations, "routes": routes})
    full = ""
    if ai_provider.supports_stream():
        for delta in ai_provider.generate_stream(p["prompt"]):
            full += delta
            yield ("chunk", delta)
    answer = full.strip() or ai_provider.generate_text(p["prompt"], fallback=p["fallback"])
    if not full.strip():
        yield ("text", answer)      # 流式无输出时补发整段（兜底）
    websearch.create_pending(question=p["question"], answer=answer, results=p["results"],
                             city=p["city"], category="出游助手", db=db)
    yield ("done", None)
