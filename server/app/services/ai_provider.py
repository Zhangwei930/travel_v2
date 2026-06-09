"""AI 生成适配器（z-ai/GLM · MiMo · Dify · Ollama · stub）。

OpenAI 兼容的云模型（z-ai GLM 经 NVIDIA NIM、MiMo）优先；其次 Dify 工作流、本地 Ollama。
6.4 Prompt 约束：不得编造营业时间、票价、实时交通；价格/营业/耗时需提示以实时信息为准。
默认 stub 不依赖任何模型，按模板生成文案，保证零配置可运行。
"""
import json

import httpx

from app.config import settings

PROMPT_RULES = (
    "你是用户身边的本地出游小助手，像朋友聊天一样自然、口语、简洁，别用书面语和长篇大论。"
    "不得编造营业时间、票价和实时交通信息；涉及价格、营业状态、路线耗时须提示「以实时地图和官方信息为准」。"
)


def _provider() -> str:
    if settings.ai_provider == "zai" and settings.zai_api_base and settings.zai_api_key:
        return "zai"
    if settings.ai_provider == "mimo" and settings.mimo_api_base and settings.mimo_api_key:
        return "mimo"
    if settings.dify_api_base and settings.dify_api_key:
        return "dify"
    if settings.ai_provider == "ollama":
        return "ollama"
    return "stub"


def generate_text(prompt: str, *, fallback: str = "") -> str:
    """通用文本生成。优先 z-ai/GLM → MiMo → Dify → Ollama → stub。"""
    provider = _provider()
    if provider == "zai":
        # 主模型(如 70b 可能被 NIM 限流 429)失败/返空时，回退到备用小模型(8b)，
        # 二者都失败才给兜底语，避免一限流就"找不到"
        for model in (settings.zai_model, settings.zai_model_fallback):
            if not model:
                continue
            try:
                text = _generate_openai_compatible(
                    base=settings.zai_api_base, api_key=settings.zai_api_key,
                    model=model, prompt=prompt, fallback="",
                    # 关思考链仅 GLM 支持；换其他模型不发该参数，避免 NIM 400
                    extra=({"chat_template_kwargs": {"thinking": False}} if "glm" in model.lower() else {}),
                )
            except (httpx.HTTPError, ValueError):
                text = ""
            if text:
                return text
        return fallback
    try:
        if provider == "mimo":
            return _generate_openai_compatible(
                base=settings.mimo_api_base, api_key=settings.mimo_api_key,
                model=settings.mimo_model, prompt=prompt, fallback=fallback,
            )
        if provider == "dify":
            return _generate_with_dify(prompt, fallback=fallback)
        if provider == "ollama":
            resp = httpx.post(
                f"{settings.ollama_base.rstrip('/')}/api/generate",
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
                timeout=120.0,
            )
            resp.raise_for_status()
            return resp.json().get("response", "") or fallback
    except (httpx.HTTPError, ValueError):
        return fallback
    return fallback


def supports_stream() -> bool:
    """当前 provider 是否支持流式（OpenAI 兼容的 zai/mimo，或 Dify 工作流）。"""
    return _provider() in ("zai", "mimo", "dify")


def generate_stream(prompt: str):
    """流式生成，逐段 yield 文本增量。zai/mimo/dify 支持；其他直接返回（调用方走非流式兜底）。"""
    provider = _provider()
    if provider == "dify":
        yield from _stream_with_dify(prompt)
        return
    if provider == "zai":
        base, key, model = settings.zai_api_base, settings.zai_api_key, settings.zai_model
        # 关思考链仅 GLM 支持；其他模型(如 qwen)不发，避免 NIM 400
        extra = {"chat_template_kwargs": {"thinking": False}} if "glm" in model.lower() else {}
    elif provider == "mimo":
        base, key, model = settings.mimo_api_base, settings.mimo_api_key, settings.mimo_model
        extra = {}
    else:
        return
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": PROMPT_RULES},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
        "stream": True,
    }
    body.update(extra)
    try:
        with httpx.stream(
            "POST", f"{base.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=body, timeout=120.0,
        ) as resp:
            resp.raise_for_status()
            for raw in resp.iter_lines():
                if not raw:
                    continue
                line = raw.decode() if isinstance(raw, bytes) else raw
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    delta = json.loads(data)["choices"][0]["delta"].get("content")
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
                if delta:
                    yield delta
    except httpx.HTTPError:
        return


def _generate_openai_compatible(*, base: str, api_key: str, model: str,
                                prompt: str, fallback: str,
                                extra: dict | None = None) -> str:
    """OpenAI 兼容 /chat/completions 调用（z-ai GLM、MiMo 等共用）。"""
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": PROMPT_RULES},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }
    if extra:
        body.update(extra)
    resp = httpx.post(
        f"{base.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=15.0,   # 主模型慢于 15s 直接超时 → 上层回退到更快的备用小模型
    )
    resp.raise_for_status()
    choices = resp.json().get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "") or fallback
    return fallback


def _stream_with_dify(prompt: str):
    """Dify 工作流流式：response_mode=streaming，逐段 yield text_chunk 文本增量。"""
    base = settings.dify_api_base.rstrip("/")
    try:
        with httpx.stream(
            "POST", f"{base}/workflows/run",
            headers={"Authorization": f"Bearer {settings.dify_api_key}",
                     "Content-Type": "application/json"},
            json={"inputs": {"query": prompt, "prompt": prompt},
                  "response_mode": "streaming", "user": "zhoumi"},
            timeout=120.0,
        ) as resp:
            resp.raise_for_status()
            for raw in resp.iter_lines():
                if not raw:
                    continue
                line = raw.decode() if isinstance(raw, bytes) else raw
                if not line.startswith("data:"):
                    continue
                try:
                    obj = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
                if obj.get("event") == "text_chunk":
                    text = (obj.get("data") or {}).get("text")
                    if text:
                        yield text
    except httpx.HTTPError:
        return


def _generate_with_dify(prompt: str, *, fallback: str) -> str:
    base = settings.dify_api_base.rstrip("/")
    headers = {"Authorization": f"Bearer {settings.dify_api_key}"}

    # Prefer Workflow Apps. The same prompt is passed under both common names so
    # the Dify workflow can choose either variable without backend changes.
    workflow_resp = httpx.post(
        f"{base}/workflows/run",
        headers=headers,
        json={
            "inputs": {"query": prompt, "prompt": prompt},
            "response_mode": "blocking",
            "user": "zhoumi",
        },
        timeout=60.0,
    )
    if workflow_resp.status_code < 400:
        text = _extract_dify_workflow_text(workflow_resp.json())
        if text:
            return text

    completion_resp = httpx.post(
        f"{base}/completion-messages",
        headers=headers,
        json={"inputs": {}, "query": prompt, "response_mode": "blocking", "user": "zhoumi"},
        timeout=60.0,
    )
    completion_resp.raise_for_status()
    return completion_resp.json().get("answer", "") or fallback


def _extract_dify_workflow_text(payload: dict) -> str:
    data = payload.get("data") if isinstance(payload, dict) else None
    outputs = data.get("outputs") if isinstance(data, dict) else None
    if not isinstance(outputs, dict):
        return ""

    for key in ("answer", "text", "result", "output"):
        value = outputs.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    for value in outputs.values():
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def is_live() -> bool:
    """是否接入了真实 AI（决定数据源标签是否标注 AI 生成）。"""
    return _provider() != "stub"
