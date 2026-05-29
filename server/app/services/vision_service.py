"""图片视觉识别服务。

流程：
  1. 视觉 AI 识别图片 -> 得到文字描述（优先 Mimo/OpenAI-compat，其次 Dify，其次 Ollama）
  2. 把描述作为问题传给 kb_service.ask -> 走完整流程：
     KB命中 -> 直接返回；未命中 -> WebSearch + AI -> 写入 pending KB -> 返回
  3. 无视觉模型时：提示用户用文字描述
"""
import base64

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.schemas import AskIn, AskOut, AskSource, VisionAskIn
from app.services import kb_service

VISION_PROMPT = (
    "请描述这张图片中的场所或地点：类型（公园/景区/街道/室内等）、"
    "环境特征、氛围风格。用一句话概括，不超过40字。"
)


def _mimo_describe(image_base64: str) -> str | None:
    """用 Mimo（OpenAI 兼容）视觉接口描述图片，失败返回 None。"""
    if not (settings.mimo_api_base and settings.mimo_api_key):
        return None
    try:
        resp = httpx.post(
            f"{settings.mimo_api_base.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.mimo_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.mimo_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": VISION_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                },
                            },
                        ],
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.3,
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        choices = resp.json().get("choices", [])
        text = choices[0].get("message", {}).get("content", "").strip() if choices else ""
        return text or None
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
        return None


def _ollama_describe(image_base64: str) -> str | None:
    """用 Ollama 视觉模型描述图片，失败返回 None。"""
    if settings.ai_provider != "ollama":
        return None
    try:
        resp = httpx.post(
            f"{settings.ollama_base.rstrip('/')}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": VISION_PROMPT,
                "images": [image_base64],
                "stream": False,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
        return text or None
    except (httpx.HTTPError, ValueError):
        return None


def _dify_describe(image_base64: str) -> str | None:
    """用 Dify 多模态应用描述图片，失败返回 None。"""
    if not (settings.dify_api_base and settings.dify_api_key):
        return None
    base = settings.dify_api_base.rstrip("/")
    headers = {"Authorization": f"Bearer {settings.dify_api_key}"}
    try:
        img_bytes = base64.b64decode(image_base64)
        upload = httpx.post(
            f"{base}/files/upload",
            headers=headers,
            files={"file": ("image.jpg", img_bytes, "image/jpeg")},
            data={"user": "zhoumi"},
            timeout=30.0,
        )
        upload.raise_for_status()
        file_id = upload.json().get("id")
        if not file_id:
            return None
        chat = httpx.post(
            f"{base}/chat-messages",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "inputs": {},
                "query": VISION_PROMPT,
                "response_mode": "blocking",
                "user": "zhoumi",
                "files": [{"type": "image", "transfer_method": "local_file", "upload_file_id": file_id}],
            },
            timeout=60.0,
        )
        chat.raise_for_status()
        text = chat.json().get("answer", "").strip()
        return text or None
    except (httpx.HTTPError, ValueError, KeyError):
        return None


def ask_vision(payload: VisionAskIn, db: Session) -> AskOut:
    # 1. 视觉 AI 识别图片（按优先级：Mimo -> Dify -> Ollama）
    description = (
        _mimo_describe(payload.image_base64)
        or _dify_describe(payload.image_base64)
        or _ollama_describe(payload.image_base64)
    )

    if description:
        # 2. 用描述查 KB -> 完整 KB->WebSearch->记录 流程
        ask_in = AskIn(
            question=f"图片内容：{description}。请根据这个场景推荐附近类似的出游地点。",
            city=payload.city,
            lat=payload.lat,
            lng=payload.lng,
            intent="vision",
        )
        result = kb_service.ask(ask_in, db)
        result.sources = [AskSource(k="Vision", v=f"图片识别：{description[:20]}")] + list(result.sources)
        return result

    # 3. 无视觉模型：提示用户用文字描述
    return AskOut(
        text=(
            "图片已收到！目前视觉模型暂未返回结果，"
            "请用文字描述你在图片中看到的场所（如：公园、水边咖啡馆、古建筑街道），"
            "我来帮你找附近类似的地方。"
        ),
        sources=[AskSource(k="提示", v="视觉模型未响应")],
        chips=["附近有公园吗", "类似室内场所", "这种街道风格的地方"],
        from_kb=False,
        destinations=[],
        routes=[],
        kb_status="vision_no_model",
    )
