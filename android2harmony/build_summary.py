from __future__ import annotations

import json
import re
from pathlib import Path


def parse_hvigor_log(text: str) -> dict[str, object]:
    clean = _strip_ansi(text)
    passed = "BUILD SUCCESSFUL" in clean and "BUILD FAILED" not in clean
    failed = "BUILD FAILED" in clean or re.search(r"\bERROR:", clean) is not None
    status = "success" if passed else "failed" if failed else "unknown"
    duration_match = re.search(r"BUILD (?:SUCCESSFUL|FAILED) in ([^\r\n]+)", clean)
    errors = _extract_errors(clean)
    warnings = _extract_warnings(clean)
    return {
        "status": status,
        "passed": passed,
        "duration": duration_match.group(1).strip() if duration_match else "",
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def write_build_summary(project_dir: Path, log_file: Path) -> Path:
    project_dir = project_dir.resolve()
    out_dir = project_dir / "agent-workspace" / "06-report"
    out_dir.mkdir(parents=True, exist_ok=True)
    text = _read_log_text(log_file) if log_file.exists() else ""
    summary = parse_hvigor_log(text)
    summary.update(
        {
            "agent": "build-report-agent",
            "project": str(project_dir),
            "source": str(log_file),
        }
    )
    output = out_dir / "build-summary.json"
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "build-summary.md").write_text(_build_summary_md(summary), encoding="utf-8")
    try:
        from .report_index import write_report_index

        write_report_index(project_dir)
    except Exception:
        pass
    return output


def _read_log_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ["utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"]:
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            continue
        if "BUILD SUCCESSFUL" in text or "BUILD FAILED" in text or "hvigor" in text:
            return text
    return data.decode("utf-8", errors="ignore")


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _extract_errors(text: str) -> list[str]:
    errors: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "BUILD FAILED" in stripped or "BUILD SUCCESSFUL" in stripped:
            continue
        if "ERROR:" in stripped or "Error Message:" in stripped:
            errors.append(stripped)
    return errors[:80]


def _extract_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if "WARN:" in stripped:
            warnings.append(stripped)
    return warnings[:80]


def _build_summary_md(summary: dict[str, object]) -> str:
    lines = [
        "# Build Summary",
        "",
        f"- Result: {'PASS' if summary.get('passed') else 'FAIL' if summary.get('status') == 'failed' else 'UNKNOWN'}",
        f"- Status: {summary.get('status', 'unknown')}",
        f"- Duration: {summary.get('duration', '')}",
        f"- Errors: {summary.get('errorCount', 0)}",
        f"- Warnings: {summary.get('warningCount', 0)}",
        "",
        "## Errors",
    ]
    errors = summary.get("errors", [])
    if isinstance(errors, list) and errors:
        for item in errors:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"
