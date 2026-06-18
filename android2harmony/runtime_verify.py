"""Runtime verification loop (the missing "compiles != runs" guard).

repair-build only proves the project COMPILES. The model still emits code that
compiles green but throws at runtime (e.g. `Refresh({ refreshing: $isRefreshing })`
-> `ReferenceError: $isRefreshing is not defined` on launch). This stage installs the
built HAP, launches it, reads the HarmonyOS jscrash fault log, and feeds the runtime
error back into the LLM repair (just like a compile error) until the app launches clean.

Device steps go through hdc; the jscrash parser is pure and unit-tested.
"""
from __future__ import annotations

import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .build_repair import DEFAULT_HVIGORW, DEFAULT_NODE_HOME, DEFAULT_SDK_HOME, parse_build_errors, repair_file, run_hvigor_build
from .llm_page_agent import build_page_prompt  # noqa: F401  (kept for parity with compile repair)

DEFAULT_HDC = Path("D:/DevEco Studio/sdk/default/openharmony/toolchains/hdc.exe")
DEFAULT_TARGET = "127.0.0.1:5555"
FAULTLOG_DIR = "/data/log/faultlog/faultlogger"


@dataclass
class RuntimeCrash:
    error: str          # "ReferenceError: $isRefreshing is not defined"
    ets_relpath: str    # "pages/MainActivity.ets" (relative to entry/src/main/ets)


@dataclass
class RuntimeVerifyResult:
    launched_clean: bool
    iterations: int
    repaired_files: list[str] = field(default_factory=list)
    last_crash: str = ""


_RE_ERR_NAME = re.compile(r"^Error name:(.+)$", re.M)
_RE_ERR_MSG = re.compile(r"^Error message:(.+)$", re.M)
# topmost app frame: ...|src/main/ets/pages/MainActivity.ts:203:1
_RE_APP_FRAME = re.compile(r"src/main/ets/(.+?)\.(?:ts|ets|js)\b")


def parse_jscrash(text: str) -> RuntimeCrash | None:
    """Extract (error, offending .ets page) from a HarmonyOS jscrash log, or None."""
    name = _RE_ERR_NAME.search(text)
    msg = _RE_ERR_MSG.search(text)
    if not name and not msg:
        return None
    err = (name.group(1).strip() if name else "Error")
    if msg:
        err = f"{err}: {msg.group(1).strip()}"
    frame = _RE_APP_FRAME.search(text)
    if not frame:
        return None
    rel = frame.group(1).strip()  # e.g. "pages/MainActivity"
    return RuntimeCrash(error=err, ets_relpath=f"{rel}.ets")


def _hdc(hdc: Path, target: str, *args: str, timeout: int = 60) -> str:
    try:
        proc = subprocess.run(
            [str(hdc), "-t", target, *args],
            capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace",
        )
        return (proc.stdout or "") + "\n" + (proc.stderr or "")
    except subprocess.SubprocessError as exc:
        return f"hdc error: {exc}"


def _jscrash_files(hdc: Path, target: str, bundle: str) -> set[str]:
    out = _hdc(hdc, target, "shell", f"ls {FAULTLOG_DIR}/jscrash-{bundle}-* 2>/dev/null")
    return {ln.strip() for ln in out.splitlines() if ln.strip().endswith(".log")}


def _hap_path(project_dir: Path) -> Path:
    return project_dir / "entry" / "build" / "default" / "outputs" / "default" / "app" / "entry-default.hap"


def runtime_verify_and_repair(
    project_dir: Path,
    bundle: str,
    ability: str = "EntryAbility",
    target: str = DEFAULT_TARGET,
    hdc: Path = DEFAULT_HDC,
    hvigorw: Path = DEFAULT_HVIGORW,
    node_home: Path = DEFAULT_NODE_HOME,
    sdk_home: Path = DEFAULT_SDK_HOME,
    max_iters: int = 3,
    settle_seconds: int = 9,
    call_fn: Callable[[str, str, int], str] | None = None,
    log_sink: Callable[[str], None] | None = None,
) -> RuntimeVerifyResult:
    """Install -> launch -> catch jscrash -> repair the offending page -> rebuild -> repeat."""
    def emit(m: str) -> None:
        if log_sink:
            log_sink(m)

    repaired: list[str] = []
    ets_root = project_dir / "entry" / "src" / "main" / "ets"
    media: set[str] = set()
    last_crash = ""

    for it in range(1, max_iters + 1):
        seen = _jscrash_files(hdc, target, bundle)
        hap = _hap_path(project_dir)
        if not hap.exists():
            emit(f"[runtime {it}] HAP missing ({hap}); build first")
            return RuntimeVerifyResult(False, it, repaired, "HAP missing")
        _hdc(hdc, target, "install", str(hap), timeout=180)
        _hdc(hdc, target, "shell", "power-shell", "wakeup")
        _hdc(hdc, target, "shell", "aa", "start", "-a", ability, "-b", bundle)
        time.sleep(settle_seconds)

        new = _jscrash_files(hdc, target, bundle) - seen
        if not new:
            emit(f"[runtime {it}] launched clean (no new jscrash)")
            return RuntimeVerifyResult(True, it, repaired, "")
        crash_file = sorted(new)[-1]
        log = _hdc(hdc, target, "shell", f"cat {crash_file} 2>/dev/null | head -60")
        crash = parse_jscrash(log)
        if not crash:
            emit(f"[runtime {it}] crashed but could not parse jscrash; stopping")
            return RuntimeVerifyResult(False, it, repaired, "unparsed crash")
        last_crash = crash.error
        page = ets_root / crash.ets_relpath
        emit(f"[runtime {it}] crash in {crash.ets_relpath}: {crash.error}")
        if not page.exists():
            emit(f"[runtime {it}] offending page not found: {page}")
            return RuntimeVerifyResult(False, it, repaired, crash.error)

        runtime_err = (
            f"RUNTIME crash on launch (NOT a compile error): {crash.error}. The page compiles but "
            f"throws at runtime. Common cause: a bare `$name` reference (invalid) where it should be "
            f"`this.name` to read, or `$$this.name` for a two-way binding (e.g. Refresh/TextInput). "
            f"Fix the invalid reference/binding. Keep everything else identical."
        )
        if repair_file(page, [runtime_err], media, call_fn=call_fn, escalate=(it > 1)):
            repaired.append(crash.ets_relpath)
            emit(f"[runtime {it}] repaired {crash.ets_relpath}, rebuilding")
        else:
            emit(f"[runtime {it}] LLM produced no valid fix for {crash.ets_relpath}")
            return RuntimeVerifyResult(False, it, repaired, crash.error)

        ok, blog = run_hvigor_build(project_dir, hvigorw, node_home, sdk_home)
        if not ok:
            # the runtime fix re-introduced a compile error; clear it before relaunch
            errs = parse_build_errors(blog)
            for fp, el in errs.items():
                p = Path(fp)
                if p.exists() and p.suffix == ".ets":
                    repair_file(p, el, media, call_fn=call_fn, escalate=True)
            run_hvigor_build(project_dir, hvigorw, node_home, sdk_home)

    return RuntimeVerifyResult(False, max_iters, repaired, last_crash)
