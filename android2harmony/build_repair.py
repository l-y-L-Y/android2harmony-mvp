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

from .knowledge import ARKTS_RULES, attribute_hints_for_errors
from .llm_page_agent import ARKUI_RULES, apply_arkts_fixups, _ensure_single_entry
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
    remaining: dict[str, list[str]] = field(default_factory=dict)


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


_ENTRY_ERR = re.compile(r"@Entry'?\s*decorator\.?\s*At File:\s*(.+?\.ets)")


def fix_entry_structural_errors(project_dir: Path, log: str) -> list[str]:
    """hvigor fails a page in main_pages.json that has zero or duplicate `@Entry`
    decorators with a structural error that carries NO line:col, so parse_build_errors
    can't see it and the loop would falsely report green. Deterministically force exactly
    one @Entry on each named file's main struct."""
    text = ANSI.sub("", log)
    fixed: list[str] = []
    for m in _ENTRY_ERR.finditer(text):
        p = Path(m.group(1).strip())
        if not p.exists() or p.suffix != ".ets":
            continue
        content = p.read_text(encoding="utf-8", errors="ignore")
        struct = _struct_name(content)
        if not struct:
            continue
        new = _ensure_single_entry(content, struct)
        if new != content:
            p.write_text(new, encoding="utf-8")
            fixed.append(p.name)
    return fixed


def _project_media(project_dir: Path) -> set[str]:
    names = {"foreground", "background", "starticon", "layered_image"}
    for sub in ["entry/src/main/resources/base/media", "AppScope/resources/base/media"]:
        d = project_dir / sub
        if d.exists():
            for f in d.iterdir():
                if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                    names.add(f.stem.lower())
    return names


def build_repair_prompt(filename: str, content: str, errors: list[str], escalate: bool = False) -> str:
    error_block = "\n".join(f"- {e}" for e in errors)
    attr_hints = attribute_hints_for_errors(errors)
    attr_section = f"\n{attr_hints}\n" if attr_hints else ""
    # When earlier automated fixes on THIS file did not clear the errors, the current code
    # IS the previous attempt. Tell the model so, and push it toward minimal, safe rewrites
    # (replace any uncertain construct with a plain Text) so the loop converges instead of oscillating.
    escalation = (
        "\nIMPORTANT: a previous automated fix on this file did NOT work - the code below is that "
        "attempt and the errors below still remain. Do not repeat the same approach. Make the MINIMAL "
        "change that is certainly valid ArkUI. If any widget/attribute is uncertain, replace just that "
        "widget with a simple `Text('...')` keeping its visible text, rather than risk another error.\n"
        if escalate else ""
    )
    return f"""Fix the ArkTS/ArkUI compile errors in this single HarmonyOS page file.

{ARKUI_RULES}

{ARKTS_RULES}
{attr_section}{escalation}
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


def _safe_placeholder(struct_name: str) -> str:
    """A page that always compiles - used as the last-resort stub so one unfixable
    file never fails the whole build."""
    return (
        "@Entry\n@Component\nstruct " + struct_name + " {\n"
        "  build() {\n"
        "    Column() {\n"
        f"      Text('{struct_name}')\n"
        "        .fontSize(20)\n"
        "        .fontWeight(FontWeight.Bold)\n"
        "        .margin({ bottom: 8 })\n"
        "      Text('此页面包含迁移时无法自动修复的代码，已降级为占位。')\n"
        "        .fontSize(13)\n"
        "        .fontColor('#9CA3AF')\n"
        "    }\n"
        "    .width('100%')\n"
        "    .height('100%')\n"
        "    .justifyContent(FlexAlign.Center)\n"
        "    .alignItems(HorizontalAlign.Center)\n"
        "  }\n}\n"
    )


def guarantee_compile_file(path: Path, errors: list[str]) -> str:
    """Last resort to keep the build green. Comment out the exact error lines if that
    leaves the file syntactically balanced; otherwise replace the whole page with a safe
    placeholder. Returns 'lines' | 'placeholder' describing what was done."""
    content = path.read_text(encoding="utf-8", errors="ignore")
    struct = _struct_name(content) or path.stem
    lines = content.splitlines()
    bad = sorted({int(m.group(1)) for e in errors for m in [re.match(r"L(\d+):", e)] if m})
    # Try line-level neutralization for error lines that carry no braces (safe to drop).
    if bad:
        changed = False
        for ln in bad:
            i = ln - 1
            if 0 <= i < len(lines) and "{" not in lines[i] and "}" not in lines[i]:
                stripped = lines[i].strip()
                if stripped and not stripped.startswith("//"):
                    lines[i] = "      // [a2h-stub] " + stripped
                    changed = True
        if changed:
            candidate = "\n".join(lines) + "\n"
            if _balanced(candidate):
                path.write_text(candidate, encoding="utf-8")
                return "lines"
    path.write_text(_safe_placeholder(struct), encoding="utf-8")
    return "placeholder"


def repair_file(
    path: Path,
    errors: list[str],
    media: set[str],
    call_fn: Callable[[str, str, int], str] | None = None,
    max_tokens: int = 12000,
    escalate: bool = False,
) -> bool:
    """Repair one file in place. Returns True if a valid replacement was written."""
    call = call_fn or call_llm
    content = path.read_text(encoding="utf-8", errors="ignore")
    struct = _struct_name(content)
    prompt = build_repair_prompt(path.name, content, errors, escalate=escalate)
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

    attempts: dict[str, int] = {}  # per-file repair attempts, to escalate when stuck
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
            # build failed but no parseable ets errors. Most often this is the
            # structural "@Entry" error (no line:col) which we can fix deterministically.
            structural = fix_entry_structural_errors(project_dir, log)
            if structural:
                emit(f"[iter {it}] forced single @Entry on {len(structural)} page(s): {', '.join(structural)}")
                continue
            return RepairResult(False, it, initial, total, repaired, log[-2000:])

        def _repair(item: tuple[str, list[str]]) -> str:
            file_path, file_errors = item
            p = Path(file_path)
            if not p.exists() or p.suffix != ".ets":
                return ""
            escalate = attempts.get(file_path, 0) >= 1  # already tried -> change strategy
            try:
                if repair_file(p, file_errors, media, call_fn=call_fn, escalate=escalate):
                    tag = " (escalated)" if escalate else ""
                    return f"  repaired {p.name} ({len(file_errors)} errors){tag}|{p.name}"
                return f"  skipped {p.name} (invalid LLM output)"
            except Exception as exc:
                return f"  error repairing {p.name}: {exc}"

        for fp in errors:
            attempts[fp] = attempts.get(fp, 0) + 1
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

    # Guarantee-compile stage: the few errors the LLM could not converge on are neutralized
    # deterministically (comment the offending lines, else stub the whole page) so the build
    # is always green. Degraded pages are recorded for the fidelity report.
    stubbed: list[str] = []
    for guarantee_pass in range(2):
        ok, log = run_hvigor_build(project_dir, hvigorw, node_home, sdk_home)
        errors = parse_build_errors(log)
        total = sum(len(v) for v in errors.values())
        if ok:
            break
        if not errors:
            structural = fix_entry_structural_errors(project_dir, log)
            if structural:
                emit(f"[guarantee {guarantee_pass + 1}] forced single @Entry on {len(structural)} page(s): {', '.join(structural)}")
                continue
            break
        emit(f"[guarantee {guarantee_pass + 1}] {total} errors remain in {len(errors)} files; neutralizing to keep build green")
        for file_path, file_errors in errors.items():
            p = Path(file_path)
            if not p.exists() or p.suffix != ".ets":
                continue
            if guarantee_pass == 0:
                how = guarantee_compile_file(p, file_errors)
            else:  # second pass: force a placeholder for anything still broken
                p.write_text(_safe_placeholder(_struct_name(p.read_text(encoding="utf-8", errors="ignore")) or p.stem), encoding="utf-8")
                how = "placeholder"
            stubbed.append(f"{p.name}:{how}")
            emit(f"  neutralized {p.name} -> {how}")

    ok, log = run_hvigor_build(project_dir, hvigorw, node_home, sdk_home)
    errors = parse_build_errors(log)
    if not ok and not errors and fix_entry_structural_errors(project_dir, log):
        ok, log = run_hvigor_build(project_dir, hvigorw, node_home, sdk_home)
        errors = parse_build_errors(log)
    total = sum(len(v) for v in errors.values())
    emit(f"[final] build {'OK' if ok else 'FAIL'} - {total} errors" + (f"; {len(stubbed)} pages degraded to keep build green" if stubbed else ""))
    return RepairResult(ok, max_iters, initial, total, repaired, log[-2000:], remaining=errors)
