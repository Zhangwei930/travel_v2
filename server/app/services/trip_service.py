"""攻略生成编排 — 对应方案文档 6.1 智能攻略生成工作流。

流程：参数解析 → 知识库检索 → 地图距离 → 知识不足触发 WebSearch
      → 生成攻略 → 质量校验（含免责声明/备用方案）→ 返回。
"""
from sqlalchemy.orm import Session

from app.config import settings
from app.models import PoiIndex, SceneGear, TravelKnowledge, TravelRoute, UserRequest
from app.schemas import PlanSource, PlanStop, TripGenerateIn, TripPlanOut
from app.services import ai_provider, map_provider
from app.services.weather_provider import get_weather, weather_source_label
from app.taxonomy import GEAR_BY_SCENE, DEFAULT_GEAR


def _resolve_gear(scene_id: str, db: Session) -> list[str]:
    """优先从 scene_gear 表读取（可运营），兜底回 taxonomy 常量。"""
    if scene_id:
        row = db.query(SceneGear).filter(SceneGear.scene_id == scene_id).first()
        if row and row.items:
            return list(row.items)
    return GEAR_BY_SCENE.get(scene_id, DEFAULT_GEAR)

# 起始时间段 → 第一站到达时间
START_TIME = {"上午": "09:00", "下午": "14:00", "傍晚": "17:00", "晚上": "19:00"}

# 站间默认交通时间（分钟）；按 stop.stay 推算游玩时长，再叠加这个交通时长。
_TRANSIT_MINUTES = 30


def _stay_to_minutes(stay: str | None, default: int = 90) -> int:
    """把 '1-2h' / '2小时' / '30min' / '半日' 等粗粒度时长解析成分钟。"""
    if not stay:
        return default
    s = str(stay).strip().lower()
    if "半日" in s or "上午" in s or "下午" in s:
        return 240
    if "全天" in s or "一日" in s:
        return 480
    s2 = (
        s.replace("h", "")
         .replace("小时", "")
         .replace("min", "")
         .replace("分钟", "")
         .strip()
    )
    try:
        if "-" in s2:
            a, b = s2.split("-", 1)
            mid = (float(a) + float(b)) / 2
        else:
            mid = float(s2)
    except ValueError:
        return default
    # 小数字按小时（1-12），大数字按分钟（>12）
    return int(mid * 60) if mid <= 12 else int(mid)


def _pick_route(payload: TripGenerateIn, city: str, db: Session) -> TravelRoute | None:
    # 只选 poi_ids 非空的路线（早期 seed 留下大量没有 POI 关联的占位 route）
    # 同时按 id 升序，让结果稳定可复现
    q = db.query(TravelRoute).filter(
        TravelRoute.review_status == "approved",
        TravelRoute.city == city,
        TravelRoute.poi_ids != [],
    ).order_by(TravelRoute.id)
    if payload.scene:
        return q.filter(TravelRoute.scene == payload.scene).first()
    return q.first()


def _add_minutes(hhmm: str, minutes: int) -> str:
    h, m = map(int, hhmm.split(":"))
    total = (h * 60 + m + minutes) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def _start_time(payload: TripGenerateIn) -> str:
    text = payload.time or ""
    for key, val in START_TIME.items():
        if key in text:
            return val
    return "09:00"


def generate_plan(payload: TripGenerateIn, db: Session) -> TripPlanOut:
    city = map_provider.normalize_city(payload.city) or settings.default_city
    weather = get_weather(city)
    route = _pick_route(payload, city, db)

    # 知识库检索：取路线模板关联的 POI 及其出游知识
    stops: list[PlanStop] = []
    sources: list[PlanSource] = [
        PlanSource(kind="地图", t=f"{city} POI · 距离/路线"),
        PlanSource(kind="天气", t=weather_source_label()),
    ]
    gear_scene = payload.scene or (route.scene if route else "")

    poi_ids = route.poi_ids if route else []
    pois = db.query(PoiIndex).filter(PoiIndex.id.in_(poi_ids)).all() if poi_ids else []
    poi_map = {p.id: p for p in pois}
    arrive = _start_time(payload)

    for idx, pid in enumerate(poi_ids, start=1):
        poi = poi_map.get(pid)
        if not poi:
            continue
        kn = db.query(TravelKnowledge).filter(TravelKnowledge.poi_id == pid).first()
        stay = (kn.play_duration if kn else None) or "1-2h"
        budget = (kn.budget_level if kn else None) or "以官方为准"
        reason = (kn.recommend_reason if kn else None) or "顺路安排，体验本地玩法"
        tip = (kn.avoid_tips if kn else None) or "营业、票价以官方实时信息为准"
        stops.append(PlanStop(
            idx=idx,
            name=poi.name,
            cat=poi.category or "地点",
            arrive=arrive,
            stay=stay,
            budget=budget,
            reason=reason,
            tip=tip,
            transport=map_provider.transport_hint(payload.transport),
            lat=poi.lat,
            lng=poi.lng,
        ))
        # 下一站到达时间 = 当前到达 + 本站游玩时长 + 站间交通时间
        arrive = _add_minutes(arrive, _stay_to_minutes(stay) + _TRANSIT_MINUTES)

    if route and route.review_status == "approved":
        sources.append(PlanSource(kind="知识库", t=f"路线模板 {route.display_no or route.id} · 已审核"))

    title = (route.title if route else f"{city}出游方案")
    summary_fallback = (
        f"根据{payload.time or '出行时段'}与天气（{weather.icon}{weather.temp}°{weather.cond}），"
        f"为{payload.people_type or '出游'}人群安排的{route.duration if route else '半日'}方案，"
        f"路线顺路、强度适中。"
    )
    stop_details = "\n".join(
        f"  {s.idx}. {s.name}（{s.cat}）抵达{s.arrive}，停留{s.stay}，预算{s.budget}，"
        f"推荐理由：{s.reason}"
        for s in stops
    ) or "  （暂无具体站点）"
    prompt = (
        f"{ai_provider.PROMPT_RULES}\n"
        f"城市：{city}\n时段：{payload.time}\n人群：{payload.people_type}\n"
        f"预算：{payload.budget}\n交通：{payload.transport}\n偏好：{'、'.join(payload.preferences)}\n"
        f"天气：{weather.icon}{weather.temp}°{weather.cond}\n"
        f"路线名称：{title}\n"
        f"站点明细：\n{stop_details}\n"
        f"请根据以上站点信息，用一句话（40字以内）概括该出游方案的核心亮点，不要编造营业时间和票价。"
    )
    summary = ai_provider.generate_text(prompt, fallback=summary_fallback)
    if ai_provider.is_live() and summary != summary_fallback:
        sources.append(PlanSource(kind="AI", t="攻略文案生成"))

    # 质量校验：免责声明与备用方案必须存在（方案文档合规约束）
    backup = (route.tips if route and route.tips else
              "如目标地点人流较多或天气变化，可就近改为室内场馆或公园活动。")
    disclaimer = "营业时间、票价、路线耗时以实时地图和官方信息为准，本攻略仅供参考。"

    plan = TripPlanOut(
        no=f"PLAN-{_plan_serial(db)}",
        title=title,
        summary=summary,
        totalBudget=payload.budget or "人均 80-180 元",
        totalTime=route.duration if route else "约 4 小时",
        people=payload.people_type or "2 人",
        weather=f"{weather.icon} {weather.temp}° {weather.cond}",
        stops=stops,
        gearList=_resolve_gear(gear_scene, db),
        backup=backup,
        disclaimer=disclaimer,
        sources=sources,
    )

    db.add(UserRequest(
        city=city, lat=payload.lat, lng=payload.lng,
        params=payload.model_dump(), result=plan.model_dump(),
    ))
    db.commit()
    return plan


def _plan_serial(db: Session) -> str:
    from datetime import datetime
    seq = db.query(UserRequest).count() + 1
    return f"{datetime.utcnow():%Y-%m%d}-{seq:03d}"
