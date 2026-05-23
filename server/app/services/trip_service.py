"""攻略生成编排 — 对应方案文档 6.1 智能攻略生成工作流。

流程：参数解析 → 知识库检索 → 地图距离 → 知识不足触发 WebSearch
      → 生成攻略 → 质量校验（含免责声明/备用方案）→ 返回。
"""
from sqlalchemy.orm import Session

from app.config import settings
from app.models import PoiIndex, TravelKnowledge, TravelRoute, UserRequest
from app.schemas import PlanSource, PlanStop, TripGenerateIn, TripPlanOut
from app.services import ai_provider, map_provider
from app.services.weather_provider import get_weather, weather_source_label

# 场景对应的出游装备清单
GEAR_BY_SCENE: dict[str, list[str]] = {
    "fish": ["钓竿×2", "鱼饵(蚯蚓/玉米)", "折叠椅", "遮阳帽", "防虫液", "保温水壶", "垃圾袋"],
    "family": ["儿童水壶", "湿巾纸巾", "防晒霜", "小零食", "备用衣物"],
    "couple": ["相机/手机支架", "充电宝", "外套", "纸巾"],
    "rainy": ["雨伞", "防滑鞋", "充电宝", "口罩"],
    "budget": ["交通卡", "保温水壶", "舒适步行鞋", "零钱"],
}
DEFAULT_GEAR = ["身份证", "充电宝", "保温水壶", "纸巾", "常用药品"]

# 起始时间段 → 第一站到达时间
START_TIME = {"上午": "09:00", "下午": "14:00", "傍晚": "17:00", "晚上": "19:00"}


def _pick_route(payload: TripGenerateIn, city: str, db: Session) -> TravelRoute | None:
    q = db.query(TravelRoute).filter(TravelRoute.review_status == "approved")
    if payload.scene:
        scene_match = q.filter(TravelRoute.scene == payload.scene).first()
        if scene_match:
            return scene_match
    return q.filter(TravelRoute.city == city).first() or q.first()


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


def _route_stops(route: TravelRoute | None, transport: str | None, start: str, db: Session) -> list[PlanStop]:
    """用已审核路线模板组装站点，不触发 AI 生成。"""
    if not route:
        return []
    poi_ids = route.poi_ids or []
    pois = db.query(PoiIndex).filter(PoiIndex.id.in_(poi_ids)).all() if poi_ids else []
    poi_map = {p.id: p for p in pois}
    arrive = start
    stops: list[PlanStop] = []

    for idx, pid in enumerate(poi_ids, start=1):
        poi = poi_map.get(pid)
        if not poi:
            continue
        kn = db.query(TravelKnowledge).filter(TravelKnowledge.poi_id == pid).first()
        stay = (kn.play_duration if kn else None) or "1-2h"
        budget = (kn.budget_level if kn else None) or "以现场为准"
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
            transport=map_provider.transport_hint(transport),
            lat=poi.lat,
            lng=poi.lng,
        ))
        arrive = _add_minutes(arrive, 150)
    return stops


def route_plan_from_template(route: TravelRoute, city: str | None, db: Session) -> TripPlanOut:
    city_name = city or route.city or settings.default_city
    weather = get_weather(city_name)
    stops = _route_stops(route, None, "09:00", db)
    sources = [
        PlanSource(kind="地图", t=f"{city_name} POI · 距离/路线"),
        PlanSource(kind="天气", t=weather_source_label()),
        PlanSource(kind="知识库", t=f"路线模板 {route.display_no or route.id} · 已审核"),
    ]
    gear_scene = route.scene or ""
    summary = route.route_text or f"{route.title}，适合快速查看并按地图实时路线出发。"

    return TripPlanOut(
        no=f"ROUTE-{route.display_no or route.id}",
        title=route.title,
        summary=summary,
        totalBudget=route.budget_level or "以实际消费为准",
        totalTime=route.duration or "半日",
        people="通用",
        weather=f"{weather.icon} {weather.temp}° {weather.cond}",
        stops=stops,
        gearList=GEAR_BY_SCENE.get(gear_scene, DEFAULT_GEAR),
        backup=route.tips or "如目标地点人流较多或天气变化，可就近改为室内场馆或公园活动。",
        disclaimer="营业时间、票价、路线耗时以实时地图和官方信息为准，本攻略仅供参考。",
        sources=sources,
    )


def generate_plan(payload: TripGenerateIn, db: Session) -> TripPlanOut:
    city = payload.city or settings.default_city
    weather = get_weather(city)
    route = _pick_route(payload, city, db)

    # 知识库检索：取路线模板关联的 POI 及其出游知识
    sources: list[PlanSource] = [
        PlanSource(kind="地图", t=f"{city} POI · 距离/路线"),
        PlanSource(kind="天气", t=weather_source_label()),
    ]
    gear_scene = payload.scene or (route.scene if route else "")
    stops = _route_stops(route, payload.transport, _start_time(payload), db)

    if route and route.review_status == "approved":
        sources.append(PlanSource(kind="知识库", t=f"路线模板 {route.display_no or route.id} · 已审核"))

    route_city = (route.city if route else None) or city
    city_mismatch = route and route.city and route.city != city
    title = (route.title if route else f"{city}出游方案")
    summary_fallback = (
        f"根据{payload.time or '出行时段'}与天气（{weather.icon}{weather.temp}°{weather.cond}），"
        f"为{payload.people_type or '出游'}人群安排的{route.duration if route else '半日'}方案，"
        f"路线顺路、强度适中。"
        + (f"（注：当前数据覆盖城市为{route_city}，{city}数据扩充中）" if city_mismatch else "")
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
        gearList=GEAR_BY_SCENE.get(gear_scene, DEFAULT_GEAR),
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
