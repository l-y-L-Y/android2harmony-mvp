"""Jetpack Compose screen discovery.

Compose apps have no XML layouts - the UI lives in `@Composable` Kotlin functions.
A screen-level composable (`fun XxxScreen(...)`, `XxxRoute`, `XxxPage`) maps to one
HarmonyOS page. The whole .kt file is fed to the model as context, because a screen
file usually contains the screen plus its private helper composables, which is exactly
what is needed to render it faithfully.
"""
from __future__ import annotations

import re
from pathlib import Path

from .model import AndroidModule

# A top-level composable whose name ends in Screen/Route/Page is treated as a screen.
_SCREEN_FUN = re.compile(
    r"@Composable\b[\s\S]{0,400}?\bfun\s+([A-Z][A-Za-z0-9_]*(?:Screen|Route|Page))\s*\(",
)
_PREVIEW = re.compile(r"@Preview\b")


def discover_compose_screens(module: AndroidModule) -> dict[str, Path]:
    """Map screen page-name -> the .kt file that defines it. Preview/sample composables
    are skipped. First definition wins so a public screen beats a private duplicate."""
    screens: dict[str, Path] = {}
    for src in module.source_files:
        if src.suffix != ".kt":
            continue
        try:
            text = src.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "@Composable" not in text:
            continue
        for m in _SCREEN_FUN.finditer(text):
            name = m.group(1)
            # skip obvious preview/demo wrappers
            head = text[max(0, m.start() - 200):m.start()]
            if _PREVIEW.search(head) or name.startswith("Preview"):
                continue
            screens.setdefault(name, src)
    return screens


def is_compose_module(module: AndroidModule) -> bool:
    """A module is Compose-driven when it has screen composables and few/no layouts."""
    return bool(discover_compose_screens(module))


def compose_screen_source(file_path: Path, max_chars: int = 24000) -> str:
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    return text[:max_chars]
