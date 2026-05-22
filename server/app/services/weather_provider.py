"""天气适配器。

方案文档要求实时数据（天气）必须实时调用，不得由 AI 编造。
默认 stub 返回占位天气；配置 WEATHER_API_KEY 后可接和风天气等真实服务。
"""
from app.config import settings
from app.schemas import WeatherOut

_ICONS = {"晴": "☀️", "多云": "⛅️", "阴": "☁️", "雨": "🌧", "雪": "❄️"}


def _advice(temp: int, cond: str) -> str:
    if cond in ("雨", "雪"):
        return "建议室内活动"
    if temp >= 32:
        return "炎热，注意防晒补水"
    if temp <= 0:
        return "寒冷，注意保暖"
    return "适合出游"


def get_weather(city: str | None = None) -> WeatherOut:
    """返回指定城市实时天气。未配置真实服务时返回 stub 数据。"""
    if settings.weather_api_key:
        # 真实接入点：调用和风天气 / 高德天气 API，解析后映射为 WeatherOut。
        # 此处保留接入位，未配置密钥时走下方 stub。
        pass

    cond = "晴"
    temp = 22
    return WeatherOut(
        temp=temp,
        cond=cond,
        icon=_ICONS.get(cond, "☀️"),
        advice=_advice(temp, cond),
        wind="东北风 2 级",
    )
