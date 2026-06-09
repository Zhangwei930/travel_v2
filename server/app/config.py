"""全局配置：从环境变量 / .env 读取。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./zhoumi.db"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "*"
    default_city: str = "成都"

    # 在线咨询入口总开关（默认关；过审后置 CONSULT_ENABLED=true 即对外开放）
    consult_enabled: bool = False

    map_provider: str = "stub"
    amap_key: str = ""
    tencent_map_key: str = ""

    dify_api_base: str = ""
    dify_api_key: str = ""

    ai_provider: str = "stub"
    ollama_base: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:3b"

    searxng_base: str = ""
    kb_similarity_threshold: float = 0.5
    admin_token: str = "change-me"
    weather_api_key: str = ""

    mimo_api_base: str = ""
    mimo_api_key: str = ""
    mimo_model: str = "mimo-v2.5-pro"

    # z-ai / GLM（经 NVIDIA NIM，OpenAI 兼容接口）
    zai_api_base: str = "https://integrate.api.nvidia.com/v1"
    zai_api_key: str = ""
    zai_model: str = "z-ai/glm-5.1"
    # 主模型被 NIM 限流(429)时回退到更稳的小模型，避免给用户兜底语
    zai_model_fallback: str = "meta/llama-3.1-8b-instruct"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
