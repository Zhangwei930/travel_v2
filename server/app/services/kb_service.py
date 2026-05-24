"""出游助手问答 — 对应方案文档 6.2 客服问答 / 6.3 知识缺失补充工作流。

命中 FAQ/知识库 → 直接回答；未命中 → WebSearch + AI 总结 → 写入 kb_pending 待审核。
"""
from sqlalchemy.orm import Session

from app.config import settings
from app.models import FaqKnowledge
from app.schemas import AskIn, AskOut, AskSource, ChatTurn
from app.services import ai_provider, map_provider, websearch

SUGGESTED_CHIPS = ["停车方便吗？", "下雨改去哪？", "适合带孩子吗？", "傍晚还能玩什么？"]


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


def ask(payload: AskIn, db: Session) -> AskOut:
    question = payload.question.strip()
    city = payload.city or settings.default_city

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
            sources=[AskSource(k="知识库", v=f"FAQ · {best.category or '常见问题'}")],
            chips=SUGGESTED_CHIPS,
            from_kb=True,
        )

    # 未命中：触发 WebSearch + AI 总结，结果进入待审核
    results = websearch.search(f"{city} {merged_query}", db)
    snippets = "\n".join(f"- {r['title']}：{r['snippet']}" for r in results[:5])
    fallback = (
        "这个问题本地知识库暂未收录，已记录并转入补充流程。"
        "涉及营业时间、票价等实时信息，请以官方或地图实时查询为准。"
    )
    # 渲染历史对话块，让 AI 看到完整多轮上下文
    if history:
        lines = []
        for t in history:
            tag = "用户" if t.role == "user" else "助手"
            lines.append(f"  {tag}：{t.text.strip()}")
        context_block = "对话历史：\n" + "\n".join(lines) + "\n"
    else:
        context_block = ""
    prompt = (
        f"你是出游助手。根据以下搜索结果直接回答用户问题。\n"
        f"要求：\n"
        f"- 优先提炼搜索结果中的具体信息（地址、特色、建议游玩时间等）\n"
        f"- 营业时间、票价等实时数据，给出搜索结果中的参考值，并注明「以实时查询为准」\n"
        f"- 只有搜索结果与问题完全无关时，才说「暂未收录」\n"
        f"- 不得编造搜索结果中没有的具体数字或事实\n"
        f"- 回答控制在 150 字以内，简洁直接\n"
        f"- 若提供了上文，本次回答必须紧扣上文话题（地点、场景、人群），不要跳到无关推荐\n\n"
        f"{context_block}"
        f"用户当前问题：{question}\n"
        f"联网搜索摘要：\n{snippets or '（无搜索结果）'}"
    )
    answer = ai_provider.generate_text(prompt, fallback=fallback)

    websearch.create_pending(
        question=question, answer=answer, results=results,
        city=city, category="出游助手", db=db,
    )

    sources = [AskSource(k="知识库", v="未命中 · 已转待审核")]
    if results:
        sources.append(AskSource(k="WebSearch", v="联网补充结果"))
    if ai_provider.is_live() and answer != fallback:
        sources.append(AskSource(k="AI", v="候选答案生成"))

    return AskOut(text=answer, sources=sources, chips=SUGGESTED_CHIPS, from_kb=False)
