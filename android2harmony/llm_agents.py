from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .llm_provider import call_llm, extract_code_block, load_llm_config_from_env


@dataclass
class LLMRefineOptions:
    enabled: bool = False
    all_agents: bool = False
    max_pages: int = 0
    max_tokens: int = 6000
    max_agent_tokens: int = 1600
    uitrans_index: Path | None = None


@dataclass
class LLMAgentCall:
    agent: str
    status: str
    model: str
    reason: str
    prompt_chars: int
    response_chars: int
    prompt: str
    response: str


class LLMAgentRunner:
    def __init__(
        self,
        options: LLMRefineOptions,
        call_fn: Callable[[str, str, int], str] | None = None,
    ) -> None:
        self.options = options
        self.call_fn = call_fn or call_llm
        self.records: list[LLMAgentCall] = []
        self.model = load_llm_config_from_env().model
        self._lock = threading.Lock()

    def run(
        self,
        agent_name: str,
        prompt: str,
        system: str,
        fallback_content: str,
        validator: Callable[[str], bool] | None = None,
        normalizer: Callable[[str], str] | None = None,
        max_tokens: int | None = None,
    ) -> str:
        if not self.options.all_agents:
            self._record(agent_name, "skipped", "all_agents disabled", prompt, "")
            return fallback_content
        try:
            response = self.call_fn(prompt, system, max_tokens or self.options.max_agent_tokens)
            ok, candidate, reason = self._validate_response(response, validator, normalizer)
            if not ok:
                retry_prompt = prompt + "\n\nYour previous response was invalid or empty. Return only the required output format, with no explanation."
                retry_response = self.call_fn(retry_prompt, system, max_tokens or self.options.max_agent_tokens)
                retry_ok, retry_candidate, retry_reason = self._validate_response(retry_response, validator, normalizer)
                if retry_ok:
                    self._record(agent_name, "used", "llm output accepted after retry", retry_prompt, retry_response.strip())
                    return retry_candidate
                self._record(agent_name, "fallback", f"{retry_reason or reason}; kept rule-based artifact", retry_prompt, retry_response.strip())
                return fallback_content
            self._record(agent_name, "used", "llm output accepted", prompt, response.strip())
            return candidate
        except Exception as exc:
            self._record(agent_name, "fallback", f"{type(exc).__name__}: {exc}", prompt, "")
            return fallback_content

    def _validate_response(
        self,
        response: str,
        validator: Callable[[str], bool] | None,
        normalizer: Callable[[str], str] | None,
    ) -> tuple[bool, str, str]:
        raw_candidate = response.strip()
        candidate = normalizer(raw_candidate) if normalizer else raw_candidate
        if validator:
            try:
                valid = validator(candidate)
            except Exception as exc:
                return False, candidate, f"validation failed: {exc}"
            if not valid:
                return False, candidate, "validation failed"
        return True, candidate, ""

    def summary(self) -> dict[str, object]:
        return {
            "model": self.model,
            "mode": "all-agents-preferred" if self.options.all_agents else "page-refine-only",
            "agents": [
                {
                    "name": record.agent,
                    "status": record.status,
                    "model": record.model,
                    "reason": record.reason,
                    "promptChars": record.prompt_chars,
                    "responseChars": record.response_chars,
                }
                for record in self.records
            ],
        }

    def _record(self, agent: str, status: str, reason: str, prompt: str, response: str) -> None:
        with self._lock:
            self.records.append(
                LLMAgentCall(
                    agent=agent,
                    status=status,
                    model=self.model,
                    reason=reason,
                    prompt_chars=len(prompt),
                    response_chars=len(response),
                    prompt=prompt,
                    response=response,
                )
            )


def enhance_artifact_with_llm(
    runner: LLMAgentRunner,
    agent_name: str,
    artifact_path: str,
    content: str,
    context: str,
) -> str:
    is_json = artifact_path.endswith(".json")
    is_markdown = artifact_path.endswith(".md")
    if is_json:
        return _enhance_json_artifact_with_llm(runner, agent_name, artifact_path, content, context)
    format_rule = (
        "Return Markdown only."
        if is_markdown
        else "Return plain text only."
    )
    prompt = f"""Enhance this Android-to-HarmonyOS migration agent artifact with more accurate, useful content.

Rules:
- Preserve the artifact purpose and path: {artifact_path}
- {format_rule}
- Do not invent files that are not implied by the input.
- If uncertain, keep the original rule-based content and add cautious notes.
- Prefer concrete migration details over generic text.
- Keep the response concise enough to avoid truncation.

Project context:
```json
{context[:5000]}
```

Rule-based artifact:
```text
{content[:9000]}
```
"""
    validator: Callable[[str], bool] | None = _nonempty_validator
    return runner.run(
        agent_name=agent_name,
        prompt=prompt,
        system="You are a senior Android to HarmonyOS migration agent using mimo-v2.5-pro to improve migration artifacts.",
        fallback_content=content,
        validator=validator,
    )


def _enhance_json_artifact_with_llm(
    runner: LLMAgentRunner,
    agent_name: str,
    artifact_path: str,
    content: str,
    context: str,
) -> str:
    prompt = f"""Review this Android-to-HarmonyOS migration JSON artifact.

Rules:
- Return valid JSON only.
- Do not return the full artifact.
- Return only a compact review object with these keys:
  - findings: string[]
  - risks: string[]
  - recommendations: string[]
  - confidence: "low" | "medium" | "high"
- Do not invent files that are not implied by the input.

Project context:
```json
{context[:3500]}
```

Artifact path: {artifact_path}

Rule-based JSON artifact:
```json
{content[:5000]}
```
"""
    review_text = runner.run(
        agent_name=agent_name,
        prompt=prompt,
        system="You are a senior Android to HarmonyOS migration reviewer. Return compact valid JSON only.",
        fallback_content="",
        validator=_json_validator,
        normalizer=_json_candidate,
        max_tokens=700,
    )
    if not review_text:
        return content
    try:
        base = json.loads(content)
        review = json.loads(review_text)
    except Exception:
        return content
    if isinstance(base, dict):
        base["llmReview"] = review
        return json.dumps(base, indent=2, ensure_ascii=False)
    return json.dumps({"artifact": base, "llmReview": review}, indent=2, ensure_ascii=False)


def _json_validator(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:
        return False


def _nonempty_validator(text: str) -> bool:
    return bool(text.strip())


def _json_candidate(text: str) -> str:
    candidate = extract_code_block(text, language="json")
    if _json_validator(candidate):
        return candidate
    start_obj = text.find("{")
    end_obj = text.rfind("}")
    if 0 <= start_obj < end_obj:
        candidate = text[start_obj : end_obj + 1].strip()
        if _json_validator(candidate):
            return candidate
    start_arr = text.find("[")
    end_arr = text.rfind("]")
    if 0 <= start_arr < end_arr:
        candidate = text[start_arr : end_arr + 1].strip()
        if _json_validator(candidate):
            return candidate
    return text.strip()


def refine_arkui_page_with_llm(
    page_name: str,
    android_xml: str,
    rule_based_ets: str,
    options: LLMRefineOptions,
    runner: LLMAgentRunner | None = None,
) -> str:
    if not options.enabled:
        return rule_based_ets

    prompt = _page_refine_prompt(page_name, android_xml, rule_based_ets, _load_rules_summary(options.uitrans_index))
    system = (
        "You are a senior HarmonyOS ArkUI migration agent. "
        "Return only compilable ArkTS/ArkUI code for one .ets page. "
        "Do not explain. Do not use markdown unless asked."
    )
    if runner:
        response = runner.run(
            agent_name=f"ui-migration-agent:{page_name}",
            prompt=prompt,
            system=system,
            fallback_content=rule_based_ets,
            validator=lambda text: _looks_like_ets_page(_sanitize_llm_page(extract_code_block(text)), page_name)
            and _preserves_required_page_bindings(_sanitize_llm_page(extract_code_block(text)), page_name, rule_based_ets),
            max_tokens=options.max_tokens,
        )
    else:
        response = call_llm(prompt, system=system, max_tokens=options.max_tokens)
    code = _sanitize_llm_page(extract_code_block(response))
    if not _looks_like_ets_page(code, page_name):
        raise RuntimeError(f"LLM returned invalid ArkUI page for {page_name}")
    return code


def diagnose_build_failure_with_llm(build_log: str, relevant_files: dict[str, str], max_tokens: int = 4096) -> str:
    files = "\n\n".join(f"## {path}\n```ts\n{content[:6000]}\n```" for path, content in relevant_files.items())
    prompt = f"""Diagnose this HarmonyOS Hvigor/ArkTS build failure and propose minimal source changes.

Build log:
```text
{build_log[-12000:]}
```

Relevant files:
{files}

Return JSON with:
- rootCause
- filesToChange
- patchPlan
- risk
"""
    return call_llm(prompt, system="You are a HarmonyOS build repair agent.", max_tokens=max_tokens)


def _page_refine_prompt(page_name: str, android_xml: str, rule_based_ets: str, rules_summary: str) -> str:
    return f"""Improve a rule-generated Android XML to HarmonyOS ArkUI page.

Constraints:
- Return a full .ets file only.
- Keep the struct name exactly `{page_name}`.
- Use ArkUI declarative syntax that compiles in a Stage Model HarmonyOS project.
- Do not import unavailable third-party libraries.
- Preserve visible Android UI intent: toolbar/search, text, buttons, checkboxes, lists/grids, images, spacing.
- Preserve generated navigation code from the draft: keep router import, MockServer import, navRoutes state, route Button list, and router.pushUrl handlers if present.
- Preserve MockServer.sampleItems() usage if the draft uses it, so local test data stays centralized.
- Hide Android views with `android:visibility="gone"` unless they are necessary as empty-state fallbacks.
- Prefer Grid for RecyclerView/GridView with ids containing `grid`.
- Prefer TextInput for search widgets.
- Keep placeholder sample data generic and reusable, not project-specific business logic.
- Only reference media resources that already exist in the generated template: `$r('app.media.foreground')`, `$r('app.media.background')`, `$r('app.media.startIcon')`.
- Do not invent resource names such as `ic_default_placeholder`.
- Avoid comments except short TODO comments for unmigrated behavior.

UITrans-derived rule index:
```json
{rules_summary}
```

Android XML:
```xml
{android_xml[:18000]}
```

Rule-generated ArkUI draft:
```ts
{rule_based_ets[:18000]}
```
"""


def _load_rules_summary(path: Path | None) -> str:
    if not path or not path.exists():
        return "{}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "{}"
    return json.dumps(
        {
            "promptFiles": data.get("promptFiles", [])[:30],
            "componentDocumentSamples": data.get("componentDocumentSamples", [])[:60],
            "recommendedUse": data.get("recommendedUse", []),
        },
        ensure_ascii=False,
        indent=2,
    )


def _looks_like_ets_page(code: str, page_name: str) -> bool:
    if not ("@Component" in code and f"struct {page_name}" in code and "build()" in code):
        return False
    if "router." in code and "import router" not in code:
        return False
    return True


def _preserves_required_page_bindings(code: str, page_name: str, rule_based_ets: str) -> bool:
    if page_name != "ActivityDetail":
        return True
    required = ["detailInfo", "loadDetail", "detailField('height'", "detailField('hp'"]
    if all(item in rule_based_ets for item in required):
        return all(item in code for item in required)
    return True


def _sanitize_llm_page(code: str) -> str:
    import re

    allowed_media = {"foreground", "background", "startIcon", "layered_image"}

    def replace_media(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in allowed_media:
            return match.group(0)
        return "$r('app.media.foreground')"

    code = re.sub(r"\$r\('app\.media\.([^']+)'\)", replace_media, code)
    state_names = re.findall(r"@State\s+private\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", code)
    for name in state_names:
        code = re.sub(rf"(?<![\w.]){name}(?!\w)", f"this.{name}", code)
        code = code.replace(f"private this.{name}", f"private {name}")
        code = code.replace(f"@State this.{name}", f"@State {name}")
        code = code.replace(f"this.this.{name}", f"this.{name}")
    return code
