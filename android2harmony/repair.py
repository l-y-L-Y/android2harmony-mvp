from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .llm_provider import call_llm, extract_code_block


def create_repair_context(project_dir: Path, validation_file: Path | None = None, build_log: Path | None = None) -> dict[str, object]:
    project_dir = project_dir.resolve()
    validation_path = validation_file or project_dir / "agent-workspace" / "05-repair" / "device-validation-result.json"
    validation = _read_json(validation_path) if validation_path.exists() else {}
    build = build_log.read_text(encoding="utf-8", errors="ignore")[-20000:] if build_log and build_log.exists() else ""
    relevant_files = _collect_relevant_files(project_dir, validation)
    return {
        "project": str(project_dir),
        "validationFile": str(validation_path),
        "buildLog": build,
        "validation": validation,
        "relevantFiles": relevant_files,
    }


def diagnose_repair_context(
    context: dict[str, object],
    call_fn: Callable[[str, str, int], str] | None = None,
    max_tokens: int = 1600,
) -> dict[str, object]:
    validation = context.get("validation")
    if isinstance(validation, dict) and validation.get("passed") is True:
        return {
            "rootCause": "Validation passed; no repair required.",
            "failedCase": "",
            "evidence": [],
            "patchPlan": [],
            "filesToInspect": [],
            "risk": "none",
            "rerunCommands": [],
        }
    prompt = f"""Diagnose this Android-to-HarmonyOS generated project failure.

Return compact valid JSON only with keys:
- rootCause: string
- failedCase: string
- evidence: string[]
- patchPlan: string[]
- filesToInspect: string[]
- risk: string
- rerunCommands: string[]

Repair context:
```json
{json.dumps(context, ensure_ascii=False)[:24000]}
```
"""
    caller = call_fn or call_llm
    response = caller(prompt, "You are a HarmonyOS migration repair agent. Return JSON only.", max_tokens)
    candidate = extract_code_block(response, language="json")
    try:
        diagnosis = json.loads(candidate)
    except Exception:
        diagnosis = {
            "rootCause": "LLM diagnosis returned non-JSON output.",
            "failedCase": "",
            "evidence": [response[:2000]],
            "patchPlan": [],
            "filesToInspect": [],
            "risk": "unknown",
            "rerunCommands": [],
        }
    return _normalize_diagnosis(diagnosis, context)


def create_patch_plan(diagnosis: dict[str, object], context: dict[str, object]) -> dict[str, object]:
    steps = _as_string_list(diagnosis.get("patchPlan"))
    files = _as_string_list(diagnosis.get("filesToInspect"))
    target = files[0] if files else ""
    status = "no-op" if str(diagnosis.get("risk") or "").lower() == "none" and not steps else "proposed"
    return {
        "agent": "repair-patch-agent",
        "project": str(context.get("project", "")),
        "status": status,
        "rootCause": str(diagnosis.get("rootCause") or ""),
        "failedCase": str(diagnosis.get("failedCase") or ""),
        "evidence": _as_string_list(diagnosis.get("evidence")),
        "filesToInspect": files,
        "steps": [
            {
                "step": step,
                "target": target,
                "risk": str(diagnosis.get("risk") or "medium"),
                "verification": _as_string_list(diagnosis.get("rerunCommands")),
            }
            for step in steps
        ],
        "rerunCommands": _as_string_list(diagnosis.get("rerunCommands")),
        "applyAutomatically": False,
    }


def write_repair_diagnosis(
    project_dir: Path,
    validation_file: Path | None = None,
    build_log: Path | None = None,
    call_fn: Callable[[str, str, int], str] | None = None,
) -> Path:
    project_dir = project_dir.resolve()
    out_dir = project_dir / "agent-workspace" / "05-repair"
    out_dir.mkdir(parents=True, exist_ok=True)
    context = create_repair_context(project_dir, validation_file=validation_file, build_log=build_log)
    (out_dir / "repair-diagnosis-input.json").write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")
    diagnosis = diagnose_repair_context(context, call_fn=call_fn)
    output = out_dir / "repair-diagnosis-llm.json"
    output.write_text(json.dumps(diagnosis, indent=2, ensure_ascii=False), encoding="utf-8")
    patch_plan = create_patch_plan(diagnosis, context)
    (out_dir / "repair-patch-plan.json").write_text(json.dumps(patch_plan, indent=2, ensure_ascii=False), encoding="utf-8")
    return output


def _read_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        return data if isinstance(data, dict) else {"value": data}
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}


def _normalize_diagnosis(diagnosis: object, context: dict[str, object]) -> dict[str, object]:
    if not isinstance(diagnosis, dict):
        diagnosis = {}
    project = str(context.get("project", "<generated-project>"))
    normalized = {
        "rootCause": str(diagnosis.get("rootCause") or "Unknown failure."),
        "failedCase": str(diagnosis.get("failedCase") or _first_failed_case(context)),
        "evidence": _as_string_list(diagnosis.get("evidence")),
        "patchPlan": _as_string_list(diagnosis.get("patchPlan")),
        "filesToInspect": _as_string_list(diagnosis.get("filesToInspect")),
        "risk": str(diagnosis.get("risk") or "medium"),
        "rerunCommands": _as_string_list(diagnosis.get("rerunCommands")),
    }
    if not normalized["patchPlan"]:
        normalized["patchPlan"] = [
            "Inspect listed files and compare generated ArkTS bindings against DSL failure evidence.",
            "Apply minimal translator rule or LLM guard changes, then regenerate the Harmony project.",
        ]
    if not normalized["filesToInspect"]:
        normalized["filesToInspect"] = [str(item.get("path")) for item in context.get("relevantFiles", []) if isinstance(item, dict) and item.get("path")]
    if not normalized["rerunCommands"]:
        normalized["rerunCommands"] = [
            f"python -m android2harmony.cli validate-dsl {project} --bundle com.skydoves.pokedex",
        ]
    return normalized


def _first_failed_case(context: dict[str, object]) -> str:
    validation = context.get("validation")
    if isinstance(validation, dict):
        for case in validation.get("cases", []):
            if isinstance(case, dict) and case.get("passed") is False:
                return str(case.get("name") or "")
    return ""


def _as_string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def _collect_relevant_files(project_dir: Path, validation: dict[str, object]) -> list[dict[str, str]]:
    paths: list[Path] = []
    text = json.dumps(validation, ensure_ascii=False)
    if "ActivityDetail" in text:
        paths.append(project_dir / "entry" / "src" / "main" / "ets" / "pages" / "ActivityDetail.ets")
    if "ActivityMain" in text or "Bulbasaur" in text:
        paths.append(project_dir / "entry" / "src" / "main" / "ets" / "pages" / "ActivityMain.ets")
    if not paths:
        pages_dir = project_dir / "entry" / "src" / "main" / "ets" / "pages"
        if pages_dir.exists():
            paths.extend(sorted(pages_dir.glob("*.ets"))[:4])
    paths.extend(
        [
            project_dir / "entry" / "src" / "main" / "ets" / "state" / "MigratedStores.ets",
            project_dir / "entry" / "src" / "main" / "ets" / "repositories" / "MigratedRepositories.ets",
            project_dir / "entry" / "src" / "main" / "ets" / "network" / "HttpClient.ets",
            project_dir / "agent-workspace" / "04-uitest" / "test-dsl.json",
        ]
    )
    seen: set[Path] = set()
    files: list[dict[str, str]] = []
    for path in paths:
        if path in seen or not path.exists() or not path.is_file():
            continue
        seen.add(path)
        files.append(
            {
                "path": str(path.relative_to(project_dir)),
                "content": path.read_text(encoding="utf-8", errors="ignore")[:10000],
            }
        )
    return files
