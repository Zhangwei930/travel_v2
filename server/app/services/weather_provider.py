"""天气适配器。

方案文档要求实时数据（天气）必须实时调用，不得由 AI 编造。
默认 stub 返回占位天气；配置 WEATHER_API_KEY 后可接和风天气等真实服务。
"""
import httpx

from app.config import settings
from app.schemas import WeatherOut
from app.services import map_provider

AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"
CITY_ADCODE = {
    "北京": "110000",
    "上海": "310000",
    "广州": "440100",
    "深圳": "440300",
    "成都": "510100",
    "重庆": "500000",
    "杭州": "330100",
    "武汉": "420100",
    "西安": "610100",
    "南京": "320100",
    "苏州": "320500",
    "乌鲁木齐": "650100",
}


def _advice(temp: int, cond: str) -> str:
    if "雨" in cond or "雪" in cond:
        return "建议室内活动"
    if temp >= 32:
        return "炎热，注意防晒补水"
    if temp <= 0:
        return "寒冷，注意保暖"
    return "适合出游"


def _icon_for(cond: str) -> str:
    if "雨" in cond:
        return "rain"
    if "雪" in cond:
        return "snow"
    if "阴" in cond:
        return "overcast"
    if "云" in cond:
        return "cloudy"
    return "sunny"


def _stub_weather() -> WeatherOut:
    cond = "晴"
    temp = 22
    return WeatherOut(
        temp=temp,
        cond=cond,
        icon=_icon_for(cond),
        advice=_advice(temp, cond),
        wind="东北风 2 级",
        source="stub",
    )


def _amap_city(city: str | None) -> str:
    normalized = map_provider.normalize_city(city)
    return CITY_ADCODE.get(normalized, normalized)


def _amap_live_weather(city: str | None, key: str) -> WeatherOut | None:
    resp = httpx.get(
        AMAP_WEATHER_URL,
        params={"key": key, "city": _amap_city(city), "extensions": "base"},
        timeout=5.0,
    )
    resp.raise_for_status()
    data = resp.json()
    if str(data.get("status")) != "1":
        return None
    lives = data.get("lives") or []
    if not lives:
        return None

    live = lives[0]
    cond = str(live.get("weather") or "晴")
    try:
        temp = int(float(live.get("temperature")))
    except (TypeError, ValueError):
        temp = 22
    wind_direction = str(live.get("winddirection") or "").strip()
    wind_power = str(live.get("windpower") or "").strip()
    wind = f"{wind_direction}风 {wind_power} 级".strip()
    return WeatherOut(
        temp=temp,
        cond=cond,
        icon=_icon_for(cond),
        advice=_advice(temp, cond),
        wind=wind if wind != "风  级" else "",
        source="amap",
    )


def get_weather(city: str | None = None) -> WeatherOut:
    """返回指定城市天气；配置高德 key 时请求实时天气，否则返回示例天气。"""
    key = settings.weather_api_key or settings.amap_key
    if not key:
        return _stub_weather()
    try:
        return _amap_live_weather(city, key) or _stub_weather()
    except (httpx.HTTPError, ValueError, KeyError):
        return _stub_weather()


def weather_source_label() -> str:
    """天气数据源展示文案；当前实现没有真实天气接入，不能误称实时。"""
    if settings.weather_api_key or settings.amap_key:
        return "高德天气 API"
    return "示例天气 · 未接入实时 API"
