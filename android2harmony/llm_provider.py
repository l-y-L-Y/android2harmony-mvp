from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class LLMConfig:
    provider: str
    base_url: str
    model: str
    auth_env: str
    timeout_seconds: int


def load_llm_config_from_env() -> LLMConfig:
    provider = os.getenv("ANDROID2HARMONY_LLM_PROVIDER", "anthropic-compatible")
    if provider == "openai-compatible":
        base_url = os.getenv("OPENAI_BASE_URL", os.getenv("ANTHROPIC_BASE_URL", "")).rstrip("/")
        auth_env = "OPENAI_API_KEY" if os.getenv("OPENAI_API_KEY") else "ANTHROPIC_AUTH_TOKEN"
    else:
        base_url = os.getenv("ANTHROPIC_BASE_URL", "").rstrip("/")
        auth_env = "ANTHROPIC_AUTH_TOKEN"
    return LLMConfig(
        provider=provider,
        base_url=base_url,
        model=os.getenv(
            "ANDROID2HARMONY_LLM_MODEL",
            os.getenv("ANTHROPIC_MODEL", os.getenv("ANTHROPIC_DEFAULT_SONNET_MODEL", "mimo-v2.5-pro")),
        ),
        auth_env=auth_env,
        timeout_seconds=int(os.getenv("ANDROID2HARMONY_LLM_TIMEOUT", "180")),
    )


def call_llm(prompt: str, system: str = "You are an Android to HarmonyOS migration agent.", max_tokens: int = 4096) -> str:
    config = load_llm_config_from_env()
    if config.provider == "openai-compatible":
        return call_openai_compatible(prompt, system=system, max_tokens=max_tokens)
    return call_anthropic_compatible(prompt, system=system, max_tokens=max_tokens)


def call_openai_compatible(prompt: str, system: str = "You are an Android to HarmonyOS migration agent.", max_tokens: int = 4096) -> str:
    config = load_llm_config_from_env()
    token = os.getenv(config.auth_env)
    if not config.base_url:
        raise RuntimeError("OPENAI_BASE_URL or ANTHROPIC_BASE_URL is not set.")
    if not token:
        raise RuntimeError(f"{config.auth_env} is not set.")

    endpoint = f"{config.base_url}/chat/completions"
    payload = {
        "model": config.model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(_llm_error_message(config, exc.code, body, "OpenAI-compatible")) from exc

    choices = result.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict)).strip()
    return str(content).strip()


def call_anthropic_compatible(prompt: str, system: str = "You are an Android to HarmonyOS migration agent.", max_tokens: int = 4096) -> str:
    config = load_llm_config_from_env()
    token = os.getenv(config.auth_env)
    if not config.base_url:
        raise RuntimeError("ANTHROPIC_BASE_URL is not set.")
    if not token:
        raise RuntimeError(f"{config.auth_env} is not set.")

    endpoint = f"{config.base_url}/v1/messages"
    payload = {
        "model": config.model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": token,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(_llm_error_message(config, exc.code, body, "Anthropic-compatible")) from exc

    blocks = result.get("content", [])
    return "\n".join(block.get("text", "") for block in blocks if block.get("type") == "text").strip()


def _llm_error_message(config: LLMConfig, status_code: int, body: str, protocol: str) -> str:
    hint = ""
    lower = body.lower()
    if "model" in lower or "模型不存在" in body:
        hint = " Hint: check the model id accepted by this proxy and protocol."
    if "余额不足" in body or "无可用资源包" in body:
        hint = " Hint: the proxy accepted the request shape but reports no usable balance/resource package."
    return f"LLM request failed via {protocol} for model '{config.model}': HTTP {status_code}: {body}{hint}"


def extract_code_block(text: str, language: str = "typescript") -> str:
    fence_markers = [f"```{language}", "```ets", "```ts", "```"]
    for marker in fence_markers:
        start = text.find(marker)
        if start < 0:
            continue
        start += len(marker)
        end = text.find("```", start)
        if end > start:
            return text[start:end].strip()
    return text.strip()
