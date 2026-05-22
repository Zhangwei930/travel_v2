"""WebSearch 联网补充。

方案文档第 8 章：知识库命中率低时触发 WebSearch，结果先进入待审核（kb_pending），
不得直接作为正式答案。默认 stub 不真正联网，仅生成一条待审核占位记录。
配置 SEARXNG_BASE 后可接自建 SearXNG。
"""
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import KbPending, SearchCache


def _risk_level(question: str) -> str:
    """方案文档 8.3 风险分级。"""
    high = ("退款", "支付", "安全", "政策", "投诉", "赔偿")
    mid = ("营业时间", "票价", "门票", "停车", "活动", "闭馆")
    if any(k in question for k in high):
        return "高"
    if any(k in question for k in mid):
        return "中"
    return "低"


def search(query: str, db: Session) -> list[dict]:
    """执行联网搜索，结果写入 search_cache 并返回。"""
    cached = (
        db.query(SearchCache)
        .filter(SearchCache.query == query, SearchCache.expires_at > datetime.utcnow())
        .first()
    )
    if cached:
        return cached.results or []

    results: list[dict] = []
    if settings.searxng_base:
        try:
            resp = httpx.get(
                f"{settings.searxng_base.rstrip('/')}/search",
                params={"q": query, "format": "json"},
                timeout=8.0,
            )
            resp.raise_for_status()
            for item in resp.json().get("results", [])[:8]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("content", ""),
                    "url": item.get("url", ""),
                })
        except (httpx.HTTPError, ValueError):
            results = []

    db.add(SearchCache(
        query=query,
        results=results,
        expires_at=datetime.utcnow() + timedelta(hours=12),
    ))
    db.commit()
    return results


def create_pending(question: str, answer: str, results: list[dict], city: str | None,
                    category: str, db: Session) -> KbPending:
    """把联网/AI 生成的候选内容写入待审核知识表。同一问题已有 pending 记录则跳过。"""
    existing = (
        db.query(KbPending)
        .filter(KbPending.question == question, KbPending.status == "pending")
        .first()
    )
    if existing:
        return existing

    pending = KbPending(
        question=question,
        generated_answer=answer,
        source_urls=[r.get("url", "") for r in results if r.get("url")],
        city=city,
        category=category,
        risk_level=_risk_level(question),
        status="pending",
    )
    db.add(pending)
    db.commit()
    db.refresh(pending)
    return pending
