from __future__ import annotations

import json
from pathlib import Path


def write_report_index(project_dir: Path) -> Path:
    project_dir = project_dir.resolve()
    out_dir = project_dir / "agent-workspace" / "06-report"
    out_dir.mkdir(parents=True, exist_ok=True)
    build = _read_json(out_dir / "build-summary.json")
    validation = _read_json(out_dir / "validation-summary.json")
    repair = _read_json(project_dir / "agent-workspace" / "05-repair" / "repair-diagnosis-llm.json")
    payload = {
        "agent": "report-index-agent",
        "project": str(project_dir),
        "build": _section(build, "build-summary.json"),
        "validation": _section(validation, "validation-summary.json"),
        "repair": _section(repair, "repair-diagnosis-llm.json"),
        "artifacts": {
            "migrationReport": "migration-report.json",
            "buildSummary": "agent-workspace/06-report/build-summary.json",
            "validationSummary": "agent-workspace/06-report/validation-summary.json",
            "repairDiagnosis": "agent-workspace/05-repair/repair-diagnosis-llm.json",
        },
    }
    output = out_dir / "report-index.json"
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "report-index.md").write_text(_report_index_md(payload), encoding="utf-8")
    return output


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        return data if isinstance(data, dict) else {"value": data}
    except Exception as exc:
        return {"status": "error", "path": str(path), "error": str(exc)}


def _section(data: dict[str, object], filename: str) -> dict[str, object]:
    if not data or data.get("status") == "missing":
        return {"status": "missing", "path": filename}
    if data.get("status") == "error":
        return {"status": "error", "path": filename, "error": data.get("error", "")}
    section = {
        "status": "success" if data.get("passed") is True or data.get("status") == "success" else "failed" if data.get("passed") is False or data.get("status") == "failed" else str(data.get("status", "unknown")),
        "path": filename,
    }
    for key in ["passed", "duration", "errorCount", "warningCount", "passRate", "caseCount", "passedCaseCount", "failedCaseCount", "rootCause", "risk"]:
        if key in data:
            section[key] = data[key]
    return section


def _report_index_md(payload: dict[str, object]) -> str:
    build = payload.get("build", {})
    validation = payload.get("validation", {})
    repair = payload.get("repair", {})
    lines = [
        "# Report Index",
        "",
        f"- Project: `{payload.get('project', '')}`",
        "",
        "## Build",
        f"- Status: {build.get('status', 'missing')}",
        f"- Path: `{build.get('path', '')}`",
        f"- Duration: {build.get('duration', '')}",
        f"- Errors: {build.get('errorCount', 0)}",
        f"- Warnings: {build.get('warningCount', 0)}",
        "",
        "## Validation",
        f"- Status: {validation.get('status', 'missing')}",
        f"- Path: `{validation.get('path', '')}`",
        f"- Pass rate: {validation.get('passRate', '')}",
        f"- Cases: {validation.get('caseCount', 0)}",
        "",
        "## Repair",
        f"- Status: {repair.get('status', 'missing')}",
        f"- Path: `{repair.get('path', '')}`",
        f"- Root cause: {repair.get('rootCause', '')}",
        f"- Risk: {repair.get('risk', '')}",
    ]
    return "\n".join(lines) + "\n"
