from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .emulator import run_emulator_diagnostic


@dataclass
class DeviceValidation:
    target: str
    installed: bool
    started: bool
    layout_dumped: bool
    screenshot_captured: bool
    clicked: bool
    report: str


@dataclass
class DslValidation:
    passed: bool
    result_file: Path
    report: str


def validate_on_device(project_dir: Path, hdc: Path, bundle: str, ability: str = "EntryAbility", click_text: str | None = None) -> DeviceValidation:
    project_dir = project_dir.resolve()
    hap = project_dir / "entry" / "build" / "default" / "outputs" / "default" / "app" / "entry-default.hap"
    layout = project_dir / "uitest-layout.json"
    screenshot = project_dir / "uitest-screenshot.png"
    after_layout = project_dir / "uitest-layout-after-click.json"
    after_screenshot = project_dir / "uitest-screenshot-after-click.png"

    target = _run([str(hdc), "list", "targets"], project_dir).strip()
    if not target or target == "[Empty]":
        return DeviceValidation(target="[Empty]", installed=False, started=False, layout_dumped=False, screenshot_captured=False, clicked=False, report="No hdc target is online.")

    install = _run([str(hdc), "install", str(hap)], project_dir)
    if "[Fail]" in install or "error:" in install.lower():
        return DeviceValidation(target=target, installed=False, started=False, layout_dumped=False, screenshot_captured=False, clicked=False, report=f"Install failed: {install.strip()}")
    start = _run([str(hdc), "shell", "aa", "start", "-a", ability, "-b", bundle], project_dir)
    time.sleep(2)
    _capture_layout_and_screen(hdc, project_dir, bundle, layout, screenshot, "/data/local/tmp/android2harmony-layout.json", "/data/local/tmp/android2harmony.png")
    if not _layout_has_content(layout):
        _bring_app_to_foreground(hdc, project_dir, bundle)
        start = _run([str(hdc), "shell", "aa", "start", "-a", ability, "-b", bundle], project_dir)
        time.sleep(2)
        _capture_layout_and_screen(hdc, project_dir, bundle, layout, screenshot, "/data/local/tmp/android2harmony-layout.json", "/data/local/tmp/android2harmony.png")
    clicked = False
    if click_text:
        bounds = _find_text_bounds(layout, click_text)
        if not bounds:
            _bring_app_to_foreground(hdc, project_dir, bundle)
            time.sleep(1)
            _capture_layout_and_screen(hdc, project_dir, bundle, layout, screenshot, "/data/local/tmp/android2harmony-layout.json", "/data/local/tmp/android2harmony.png")
            bounds = _find_text_bounds(layout, click_text)
        if not bounds:
            raise RuntimeError(f"Could not find clickable text in layout dump: {click_text}")
        x = int((bounds[0] + bounds[2]) / 2)
        y = int((bounds[1] + bounds[3]) / 2)
        _run([str(hdc), "shell", "uitest", "uiInput", "click", str(x), str(y)], project_dir)
        time.sleep(1)
        _run([str(hdc), "shell", "uitest", "dumpLayout", "-b", bundle, "-p", "/data/local/tmp/android2harmony-layout-after-click.json"], project_dir)
        _run([str(hdc), "shell", "uitest", "screenCap", "-p", "/data/local/tmp/android2harmony-after-click.png"], project_dir)
        _run([str(hdc), "file", "recv", "/data/local/tmp/android2harmony-layout-after-click.json", str(after_layout)], project_dir)
        _run([str(hdc), "file", "recv", "/data/local/tmp/android2harmony-after-click.png", str(after_screenshot)], project_dir)
        clicked = after_layout.exists() and after_screenshot.exists()

    lines = [
        f"Target: {target}",
        f"Install: {install.strip()}",
        f"Start: {start.strip()}",
        f"Layout: {layout}",
        f"Screenshot: {screenshot}",
    ]
    if click_text:
        lines.extend([f"ClickText: {click_text}", f"AfterClickLayout: {after_layout}", f"AfterClickScreenshot: {after_screenshot}"])
    return DeviceValidation(target=target, installed=True, started=True, layout_dumped=layout.exists(), screenshot_captured=screenshot.exists(), clicked=clicked, report="\n".join(lines))


def validate_dsl_on_device(
    project_dir: Path,
    hdc: Path,
    bundle: str,
    ability: str = "EntryAbility",
    dsl_file: Path | None = None,
    emulator_diagnostics: bool = True,
    repair_diagnostics: bool = False,
) -> DslValidation:
    project_dir = project_dir.resolve()
    dsl_path = dsl_file or project_dir / "agent-workspace" / "04-uitest" / "test-dsl.json"
    result_file = project_dir / "agent-workspace" / "05-repair" / "device-validation-result.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    dsl = json.loads(dsl_path.read_text(encoding="utf-8", errors="ignore"))
    cases = dsl.get("cases", [])
    base = validate_on_device(project_dir, hdc, bundle, ability)
    emulator_report: dict[str, object] | None = None
    results: list[dict[str, object]] = []
    passed = base.installed and base.started and base.layout_dumped and base.screenshot_captured
    if not passed:
        if emulator_diagnostics and base.target == "[Empty]":
            diagnostic = run_emulator_diagnostic(
                hdc=hdc,
                wait_seconds=20,
                report_file=result_file.parent / "emulator-diagnostic.json",
            )
            emulator_report = diagnostic.to_dict()
        for index, case in enumerate(cases):
            name = str(case.get("name", f"case_{index}")) if isinstance(case, dict) else f"case_{index}"
            results.append(
                {
                    "name": name,
                    "passed": False,
                    "errors": [base.report],
                    "layout": str(project_dir / f"uitest-dsl-{index}-layout.json"),
                    "screenshot": str(project_dir / f"uitest-dsl-{index}.png"),
                    "skipped": True,
                }
            )
        payload = {
            "agent": "repair-iteration-agent",
            "project": str(project_dir),
            "dsl": str(dsl_path),
            "bundle": bundle,
            "passed": False,
            "baseReport": base.report,
            "emulatorDiagnostic": emulator_report,
            "cases": results,
        }
        result_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        write_validation_summary(project_dir, result_file)
        _maybe_write_repair_diagnostics(project_dir, result_file, payload, repair_diagnostics)
        return DslValidation(False, result_file, f"DSL validation: FAIL\nResult: {result_file}")
    for index, case in enumerate(cases):
        case_result = _run_dsl_case(project_dir, hdc, bundle, ability, case, index)
        results.append(case_result)
        passed = passed and bool(case_result.get("passed"))
    payload = {
        "agent": "repair-iteration-agent",
        "project": str(project_dir),
        "dsl": str(dsl_path),
        "bundle": bundle,
        "passed": passed,
        "baseReport": base.report,
        "cases": results,
    }
    result_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_validation_summary(project_dir, result_file)
    if not passed:
        _maybe_write_repair_diagnostics(project_dir, result_file, payload, repair_diagnostics)
    report = f"DSL validation: {'PASS' if passed else 'FAIL'}\nResult: {result_file}"
    return DslValidation(passed=passed, result_file=result_file, report=report)


def write_validation_summary(project_dir: Path, result_file: Path) -> Path:
    project_dir = project_dir.resolve()
    out_dir = project_dir / "agent-workspace" / "06-report"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = _read_json_file(result_file)
    cases = result.get("cases", []) if isinstance(result, dict) else []
    case_rows = [case for case in cases if isinstance(case, dict)]
    passed_cases = [case for case in case_rows if case.get("passed") is True]
    failed_cases = [case for case in case_rows if case.get("passed") is False]
    summary = {
        "agent": "validation-report-agent",
        "project": str(project_dir),
        "source": str(result_file),
        "bundle": str(result.get("bundle", "")) if isinstance(result, dict) else "",
        "passed": bool(result.get("passed")) if isinstance(result, dict) else False,
        "caseCount": len(case_rows),
        "passedCaseCount": len(passed_cases),
        "failedCaseCount": len(failed_cases),
        "passRate": f"{len(passed_cases)}/{len(case_rows)}" if case_rows else "0/0",
        "cases": [
            {
                "name": str(case.get("name", "")),
                "passed": bool(case.get("passed")),
                "errors": case.get("errors", []),
                "layout": str(case.get("layout", "")),
                "screenshot": str(case.get("screenshot", "")),
            }
            for case in case_rows
        ],
    }
    output = out_dir / "validation-summary.json"
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "validation-summary.md").write_text(_validation_summary_md(summary), encoding="utf-8")
    try:
        from .report_index import write_report_index

        write_report_index(project_dir)
    except Exception:
        pass
    return output


def _validation_summary_md(summary: dict[str, object]) -> str:
    lines = [
        "# Validation Summary",
        "",
        f"- Bundle: `{summary.get('bundle', '')}`",
        f"- Result: {'PASS' if summary.get('passed') else 'FAIL'}",
        f"- Case pass rate: {summary.get('passRate', '0/0')}",
        "",
        "## Cases",
    ]
    cases = summary.get("cases", [])
    if isinstance(cases, list):
        for case in cases:
            if not isinstance(case, dict):
                continue
            status = "PASS" if case.get("passed") else "FAIL"
            lines.append(f"- `{case.get('name', '')}`: {status}")
            errors = case.get("errors", [])
            if isinstance(errors, list) and errors:
                lines.append(f"  - Errors: {'; '.join(str(item) for item in errors)}")
    return "\n".join(lines) + "\n"


def _read_json_file(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        return data if isinstance(data, dict) else {"value": data}
    except Exception as exc:
        return {"error": str(exc)}


def _maybe_write_repair_diagnostics(project_dir: Path, result_file: Path, payload: dict[str, object], enabled: bool) -> None:
    if not enabled:
        return
    try:
        from .repair import write_repair_diagnosis

        output = write_repair_diagnosis(project_dir, validation_file=result_file)
        payload["repairDiagnosis"] = str(output)
        payload["repairPatchPlan"] = str(output.with_name("repair-patch-plan.json"))
    except Exception as exc:
        payload["repairDiagnosisError"] = str(exc)
    result_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_dsl_case(project_dir: Path, hdc: Path, bundle: str, ability: str, case: dict, index: int) -> dict[str, object]:
    name = str(case.get("name", f"case_{index}"))
    layout = project_dir / f"uitest-dsl-{index}-layout.json"
    screenshot = project_dir / f"uitest-dsl-{index}.png"
    steps = case.get("steps", [])
    errors: list[str] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        try:
            if step.get("action") == "launch":
                _run([str(hdc), "shell", "aa", "start", "-a", ability, "-b", bundle], project_dir)
                time.sleep(1)
                _capture_layout_and_screen(hdc, project_dir, bundle, layout, screenshot, f"/data/local/tmp/android2harmony-dsl-{index}.json", f"/data/local/tmp/android2harmony-dsl-{index}.png")
                if not _layout_has_content(layout):
                    _bring_app_to_foreground(hdc, project_dir, bundle)
                    _capture_layout_and_screen(hdc, project_dir, bundle, layout, screenshot, f"/data/local/tmp/android2harmony-dsl-{index}.json", f"/data/local/tmp/android2harmony-dsl-{index}.png")
            elif step.get("action") == "click_text":
                target = str(step.get("target", ""))
                bounds = _find_text_bounds(layout, target)
                if not bounds:
                    errors.append(f"text not found: {target}")
                    continue
                x = int((bounds[0] + bounds[2]) / 2)
                y = int((bounds[1] + bounds[3]) / 2)
                _run([str(hdc), "shell", "uitest", "uiInput", "click", str(x), str(y)], project_dir)
                time.sleep(1)
                _capture_layout_and_screen(hdc, project_dir, bundle, layout, screenshot, f"/data/local/tmp/android2harmony-dsl-{index}.json", f"/data/local/tmp/android2harmony-dsl-{index}.png")
            elif step.get("action") == "press_back":
                _run([str(hdc), "shell", "uitest", "uiInput", "keyEvent", "Back"], project_dir)
                time.sleep(1)
                _capture_layout_and_screen(hdc, project_dir, bundle, layout, screenshot, f"/data/local/tmp/android2harmony-dsl-{index}.json", f"/data/local/tmp/android2harmony-dsl-{index}.png")
            elif step.get("assert") == "page_visible":
                target = str(step.get("target", ""))
                if not _assert_page_visible(layout, target):
                    errors.append(f"page not visible: {target}")
            elif step.get("assert") == "text_visible":
                target = str(step.get("target", ""))
                if not _find_text_bounds(layout, target):
                    _capture_layout_and_screen(hdc, project_dir, bundle, layout, screenshot, f"/data/local/tmp/android2harmony-dsl-{index}.json", f"/data/local/tmp/android2harmony-dsl-{index}.png")
                if not _find_text_bounds(layout, target):
                    errors.append(f"text not visible: {target}")
            elif step.get("assert") == "wait_text":
                target = str(step.get("target", ""))
                timeout_ms = int(step.get("timeoutMs", 5000) or 5000)
                if not _wait_for_text(hdc, project_dir, bundle, layout, screenshot, target, timeout_ms, index):
                    errors.append(f"text not visible before timeout: {target}")
        except Exception as exc:
            errors.append(str(exc))
    return {"name": name, "passed": len(errors) == 0, "errors": errors, "layout": str(layout), "screenshot": str(screenshot)}


def _assert_page_visible(layout: Path, target: str) -> bool:
    page = target.split("/")[-1]
    title = re.sub(r"^Activity", "", page)
    if page == "Index":
        title = "Index"
    if _find_text_bounds(layout, title):
        return True
    if title and _find_text_bounds(layout, title.replace("Activity", "")):
        return True
    return _layout_has_content(layout)


def _capture_layout_and_screen(hdc: Path, project_dir: Path, bundle: str, layout: Path, screenshot: Path, remote_layout: str, remote_screenshot: str) -> None:
    _run([str(hdc), "shell", "uitest", "dumpLayout", "-b", bundle, "-p", remote_layout], project_dir)
    _run([str(hdc), "shell", "uitest", "screenCap", "-p", remote_screenshot], project_dir)
    _run([str(hdc), "file", "recv", remote_layout, str(layout)], project_dir)
    _run([str(hdc), "file", "recv", remote_screenshot, str(screenshot)], project_dir)


def _wait_for_text(hdc: Path, project_dir: Path, bundle: str, layout: Path, screenshot: Path, text: str, timeout_ms: int, index: int) -> bool:
    deadline = time.time() + max(timeout_ms, 500) / 1000
    while time.time() <= deadline:
        try:
            if layout.exists() and _find_text_bounds(layout, text):
                return True
        except Exception:
            pass
        _capture_layout_and_screen(
            hdc,
            project_dir,
            bundle,
            layout,
            screenshot,
            f"/data/local/tmp/android2harmony-dsl-{index}.json",
            f"/data/local/tmp/android2harmony-dsl-{index}.png",
        )
        try:
            if _find_text_bounds(layout, text):
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def _bring_app_to_foreground(hdc: Path, project_dir: Path, bundle: str) -> None:
    desktop_layout = project_dir / "uitest-desktop-layout.json"
    _run([str(hdc), "shell", "uitest", "uiInput", "keyEvent", "Home"], project_dir)
    time.sleep(1)
    _run([str(hdc), "shell", "uitest", "dumpLayout", "-p", "/data/local/tmp/android2harmony-desktop-layout.json"], project_dir)
    _run([str(hdc), "file", "recv", "/data/local/tmp/android2harmony-desktop-layout.json", str(desktop_layout)], project_dir)
    labels = _candidate_labels(bundle)
    for label in labels:
        bounds = _find_text_bounds(desktop_layout, label)
        if bounds:
            x = int((bounds[0] + bounds[2]) / 2)
            y = int((bounds[1] + bounds[3]) / 2)
            _run([str(hdc), "shell", "uitest", "uiInput", "click", str(x), str(y)], project_dir)
            time.sleep(2)
            return


def _candidate_labels(bundle: str) -> list[str]:
    last = bundle.rsplit(".", 1)[-1]
    title = last[:1].upper() + last[1:]
    return [title, last, last.replace("-", " ").title()]


def _layout_has_content(layout: Path) -> bool:
    data = _read_layout_json(layout)
    if data is None:
        return False
    for node in _walk_nodes(data):
        attrs = node.get("attributes", node) if isinstance(node, dict) else {}
        values = [str(attrs.get(key, "")) for key in ["text", "value", "content", "description", "bounds"]]
        if any(value and value not in {"[0,0][0,0]"} for value in values):
            return True
    return False


def _run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, timeout=120)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}\n{output}")
    return output


def _find_text_bounds(layout: Path, text: str) -> tuple[int, int, int, int] | None:
    data = _read_layout_json(layout)
    if data is None:
        return None
    for node in _walk_nodes(data):
        attrs = node.get("attributes", node) if isinstance(node, dict) else {}
        values = [str(attrs.get(key, "")) for key in ["text", "value", "content", "description"]]
        if any(text == value or text in value for value in values):
            bounds = _extract_bounds(attrs)
            if bounds:
                return bounds
    return None


def _read_layout_json(layout: Path) -> object | None:
    if not layout.exists() or layout.stat().st_size == 0:
        return None
    try:
        return json.loads(layout.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return None


def _walk_nodes(value: object) -> list[dict]:
    nodes: list[dict] = []
    if isinstance(value, dict):
        nodes.append(value)
        for child in value.values():
            nodes.extend(_walk_nodes(child))
    elif isinstance(value, list):
        for item in value:
            nodes.extend(_walk_nodes(item))
    return nodes


def _extract_bounds(node: dict) -> tuple[int, int, int, int] | None:
    for key in ["bounds", "rect", "area"]:
        raw = node.get(key)
        if isinstance(raw, str):
            numbers = [int(item) for item in re.findall(r"-?\d+", raw)]
            if len(numbers) >= 4:
                return numbers[0], numbers[1], numbers[2], numbers[3]
        if isinstance(raw, dict):
            keys = ["left", "top", "right", "bottom"]
            if all(item in raw for item in keys):
                return int(raw["left"]), int(raw["top"]), int(raw["right"]), int(raw["bottom"])
    if all(key in node for key in ["left", "top", "right", "bottom"]):
        return int(node["left"]), int(node["top"]), int(node["right"]), int(node["bottom"])
    return None
