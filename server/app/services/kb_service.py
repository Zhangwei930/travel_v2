"""出游助手问答 — 对应方案文档 6.2 客服问答 / 6.3 知识缺失补充工作流。

命中 FAQ/知识库 → 直接回答；未命中 → WebSearch + AI 总结 → 写入 kb_pending 待审核。
"""
import datetime
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


def _location_cards(payload: AskIn, city: str, db: Session):
    if payload.lat is None or payload.lng is None:
        return [], []

    kn_rows = db.query(TravelKnowledge).filter(TravelKnowledge.review_status == "approved").all()
    kn_by_id = {kn.poi_id: kn for kn in kn_rows if kn.poi_id}
    rows = []
    for poi in db.query(PoiIndex).filter(PoiIndex.provider != "amap").all():
        if poi.lat is None or poi.lng is None:
            continue
        if map_provider.normalize_city(poi.city) != map_provider.normalize_city(city):
            continue
        kn = kn_by_id.get(poi.id)
        if payload.scene and not (kn and payload.scene in (kn.scene_ids or [])):
            continue
        rows.append((poi, kn))

    weather = get_weather(city)
    destinations = recommend_pois(
        rows,
        origin=(payload.lat, payload.lng),
        scene=payload.scene,
        weather=weather,
        limit=3,
    )
    routes = build_home_routes(
        db,
        city=city,
        scene=payload.scene,
        origin=(payload.lat, payload.lng),
        recommended=destinations,
        limit=2,
    )
    return destinations, routes


def ask(payload: AskIn, db: Session) -> AskOut:
    question = payload.question.strip()
    city = payload.city or settings.default_city
    time_now = _time_slot()

    # 上下文：优先取 history（多轮），fallback 到旧 context 字段（单条）
    history = [t for t in (payload.history or []) if (t.text or "").strip()]
    if not history and payload.context:
        history = [ChatTurn(role="user", text=payload.context.strip())]
    # 取最近 6 条；只保留 user/bot 两种角色
    history = [t for t in history[-6:] if t.role in ("user", "bot")]

    # 合并查询：拼最近 user 消息 + 当前问题 → 让 FAQ 匹配 / WebSearch 有完整语境
    # 例「温江景点」+「适合带孩子吗？」→ 合并查询包含"温江"，
    # 避免「适合带孩子吗？」单独命中通用 FAQ「成都带孩子玩什么」。
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

    # 命中知识库：直接回答
    if best and best_score >= settings.kb_similarity_threshold:
        return AskOut(
            text=best.answer,
            sources=[],
            chips=[],
            from_kb=True,
            destinations=[],
            routes=[],
            kb_status="hit",
        )

    # 未命中：WebSearch + AI 总结（结合位置和时间），结果写入待审核
    results = websearch.search(f"{city} {merged_query}", db)
    snippets = "\n".join(f"- {r['title']}：{r['snippet']}" for r in results[:5])
    fallback = "抱歉，暂时找不到相关信息，请换个说法再试试。"

    location_ctx = ""
    if payload.lat and payload.lng:
        location_ctx = f"用户当前位于{city}（坐标 {payload.lat:.4f}, {payload.lng:.4f}）。"
    elif city:
        location_ctx = f"用户当前在{city}。"

    weather_ctx = f"当前天气：{payload.weather}。" if payload.weather else ""

    if history:
        lines = [f"  {'用户' if t.role == 'user' else '助手'}：{t.text.strip()}" for t in history]
        context_block = "对话历史：\n" + "\n".join(lines) + "\n\n"
    else:
        context_block = ""

    prompt = (
        f"你是本地出游助手，专注于帮用户找到合适的本地出游目的地。\n"
        f"背景信息：{location_ctx}{weather_ctx}当前时段：{time_now}。\n\n"
        f"回答要求：\n"
        f"- 直接推荐 2-3 个具体地点，说明为何适合（人群、距离、当前时段）\n"
        f"- 若问题提到时间限制（如2小时内），要评估路程+游玩是否合理\n"
        f"- 营业时间、票价注明「以实时查询为准」\n"
        f"- 不得编造搜索结果中没有的数字或地点\n"
        f"- 回答控制在 200 字以内，口语化、直接\n"
        f"- 不要输出知识库、数据来源等内部术语\n\n"
        f"{context_block}"
        f"用户问题：{question}\n"
        f"参考资料：\n{snippets or '（无搜索结果）'}"
    )
    answer = ai_provider.generate_text(prompt, fallback=fallback)

    websearch.create_pending(
        question=question, answer=answer, results=results,
        city=city, category="出游助手", db=db,
    )

    return AskOut(
        text=answer,
        sources=[],
        chips=[],
        from_kb=False,
        destinations=[],
        routes=[],
        kb_status="miss",
    )
