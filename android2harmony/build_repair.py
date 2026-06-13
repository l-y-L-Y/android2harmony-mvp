"""Build-repair loop (the "repair iteration agent").

Runs hvigor, parses ArkTS/ArkUI compile errors, and asks the model to fix each
failing .ets file (with its concrete errors + the ArkUI rule sheet), then rebuilds.
Iterates until the build passes or the iteration budget is exhausted.
"""
from __future__ import annotations

import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .llm_page_agent import ARKUI_RULES, apply_arkts_fixups
from .llm_provider import call_llm, extract_code_block

ANSI = re.compile(r"\x1b\[[0-9;]*m")
DEFAULT_HVIGORW = Path("D:/DevEco Studio/tools/hvigor/bin/hvigorw.bat")
DEFAULT_NODE_HOME = Path("D:/DevEco Studio/tools/node")
DEFAULT_SDK_HOME = Path("D:/DevEco Studio/sdk")


@dataclass
class RepairResult:
    passed: bool
    iterations: int
    initial_error_count: int
    final_error_count: int
    repaired_files: list[str] = field(default_factory=list)
    log_tail: str = ""


def run_hvigor_build(
    project_dir: Path,
    hvigorw: Path = DEFAULT_HVIGORW,
    node_home: Path = DEFAULT_NODE_HOME,
    sdk_home: Path = DEFAULT_SDK_HOME,
    timeout: int = 1800,
) -> tuple[bool, str]:
    env = dict(os.environ)
    env["DEVECO_SDK_HOME"] = str(sdk_home)
    # PowerShell's call operator handles the spaced "D:\DevEco Studio\..." paths
    # reliably, where cmd.exe quote-stripping does not.
    ps = f'& "{hvigorw}" assembleApp --node-home "{node_home}" --no-daemon'
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            cwd=str(project_dir), env=env, capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired as exc:
        return False, f"BUILD TIMEOUT after {timeout}s\n{exc.stdout or ''}"
    log = (proc.stdout or "") + "\n" + (proc.stderr or "")
    ok = proc.returncode == 0 and "BUILD SUCCESSFUL" in log
    return ok, log


def parse_build_errors(log: str) -> dict[str, list[str]]:
    """Map each failing .ets file path -> list of 'line:col message' strings."""
    text = ANSI.sub("", log)
    errors: dict[str, list[str]] = {}
    for m in re.finditer(r"Error Message:\s*(.+?)\s*At File:\s*(.+?\.ets):(\d+):(\d+)", text, re.S):
        msg = re.sub(r"\s+", " ", m.group(1)).strip().rstrip(".")
        path = m.group(2).strip()
        errors.setdefault(path, []).append(f"L{m.group(3)}:{m.group(4)} {msg}")
    return errors


def _project_media(project_dir: Path) -> set[str]:
    names = {"foreground", "background", "starticon", "layered_image"}
    for sub in ["entry/src/main/resources/base/media", "AppScope/resources/base/media"]:
        d = project_dir / sub
        if d.exists():
            for f in d.iterdir():
                if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                    names.add(f.stem.lower())
    return names


def build_repair_prompt(filename: str, content: str, errors: list[str]) -> str:
    error_block = "\n".join(f"- {e}" for e in errors)
    return f"""Fix the ArkTS/ArkUI compile errors in this single HarmonyOS page file.

{ARKUI_RULES}

Rules for your fix:
- Change ONLY what is needed to clear the errors below.
- PRESERVE all visible text exactly (especially Chinese) and keep the same layout/structure.
- Keep the same `@Entry @Component struct` name.
- Return the COMPLETE corrected .ets file. No markdown fences, no explanation.

hvigor compile errors in {filename}:
{error_block}

Current {filename}:
```ts
{content[:16000]}
```"""


def _struct_name(code: str) -> str | None:
    m = re.search(r"struct\s+([A-Za-z_][A-Za-z0-9_]*)", code)
    return m.group(1) if m else None


def _balanced(code: str) -> bool:
    return bool(code.strip()) and code.count("{") == code.count("}") and code.rstrip().endswith("}")


def repair_file(
    path: Path,
    errors: list[str],
    media: set[str],
    call_fn: Callable[[str, str, int], str] | None = None,
    max_tokens: int = 12000,
) -> bool:
    """Repair one file in place. Returns True if a valid replacement was written."""
    call = call_fn or call_llm
    content = path.read_text(encoding="utf-8", errors="ignore")
    struct = _struct_name(content)
    prompt = build_repair_prompt(path.name, content, errors)
    system = "You are a senior HarmonyOS ArkUI engineer fixing compile errors. Return only the corrected .ets file."
    fixed = apply_arkts_fixups(extract_code_block(call(prompt, system, max_tokens)))

    def fix_media(match: re.Match[str]) -> str:
        return match.group(0) if match.group(1).lower() in media else "$r('app.media.foreground')"

    fixed = re.sub(r"\$r\('app\.media\.([^']+)'\)", fix_media, fixed)
    if not _balanced(fixed):
        return False
    if struct and f"struct {struct}" not in fixed:
        return False
    path.write_text(fixed, encoding="utf-8")
    return True


def repair_build(
    project_dir: Path,
    max_iters: int = 3,
    hvigorw: Path = DEFAULT_HVIGORW,
    node_home: Path = DEFAULT_NODE_HOME,
    sdk_home: Path = DEFAULT_SDK_HOME,
    call_fn: Callable[[str, str, int], str] | None = None,
    log_sink: Callable[[str], None] | None = None,
) -> RepairResult:
    media = _project_media(project_dir)
    repaired: list[str] = []
    initial = -1
    log = ""

    def emit(msg: str) -> None:
        if log_sink:
            log_sink(msg)

    # Free deterministic pass first: clears the mechanical errors (Spacer, startIcon, ...)
    # without spending any LLM calls, so the repair loop only tackles real semantic errors.
    fixed_count = 0
    for ets in (project_dir / "entry" / "src" / "main" / "ets").rglob("*.ets"):
        before = ets.read_text(encoding="utf-8", errors="ignore")
        after = apply_arkts_fixups(before)
        if after != before:
            ets.write_text(after, encoding="utf-8")
            fixed_count += 1
    if fixed_count:
        emit(f"[fixups] applied deterministic ArkUI fixes to {fixed_count} files")

    for it in range(1, max_iters + 1):
        ok, log = run_hvigor_build(project_dir, hvigorw, node_home, sdk_home)
        errors = parse_build_errors(log)
        total = sum(len(v) for v in errors.values())
        if initial < 0:
            initial = total
        emit(f"[iter {it}] build {'OK' if ok else 'FAIL'} - {total} errors across {len(errors)} files")
        if ok:
            return RepairResult(True, it, initial, 0, repaired, log[-2000:])
        if not errors:
            # build failed but no parseable ets errors (config/resource issue)
            return RepairResult(False, it, initial, total, repaired, log[-2000:])

        def _repair(item: tuple[str, list[str]]) -> str:
            file_path, file_errors = item
            p = Path(file_path)
            if not p.exists() or p.suffix != ".ets":
                return ""
            try:
                if repair_file(p, file_errors, media, call_fn=call_fn):
                    return f"  repaired {p.name} ({len(file_errors)} errors)|{p.name}"
                return f"  skipped {p.name} (invalid LLM output)"
            except Exception as exc:
                return f"  error repairing {p.name}: {exc}"

        workers = max(1, int(os.getenv("ANDROID2HARMONY_LLM_CONCURRENCY", "4")))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for line in pool.map(_repair, list(errors.items())):
                if not line:
                    continue
                if "|" in line:
                    msg, name = line.rsplit("|", 1)
                    repaired.append(name)
                    emit(msg)
                else:
                    emit(line)

    ok, log = run_hvigor_build(project_dir, hvigorw, node_home, sdk_home)
    errors = parse_build_errors(log)
    total = sum(len(v) for v in errors.values())
    emit(f"[final] build {'OK' if ok else 'FAIL'} - {total} errors")
    return RepairResult(ok, max_iters, initial, total, repaired, log[-2000:])
