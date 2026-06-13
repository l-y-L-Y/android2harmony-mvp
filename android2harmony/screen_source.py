"""Find the Kotlin/Java source (Activity/Fragment class) that backs a screen.

Android XML layouts are only the static skeleton - the real content (ViewPager
fragment lists, RecyclerView adapters, tab titles, click handlers, data) lives in the
Activity/Fragment code. Feeding that source alongside the layout lets the model render
what the screen actually shows instead of guessing from an empty container.
"""
from __future__ import annotations

import re
from pathlib import Path

from .model import AndroidModule

_CLASS = re.compile(r"\b(?:class|object)\s+([A-Z][A-Za-z0-9_]*)")


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _candidate_keys(page_name: str) -> set[str]:
    """Names a screen class might have for this page. Handles the Fragment/Activity
    affix word-order swap (page 'FragmentWanAndroid' <-> class 'WanAndroidFragment')."""
    keys = {_norm(page_name)}
    for affix in ("Fragment", "Activity"):
        if page_name.startswith(affix):
            base = page_name[len(affix):]
            keys.add(_norm(base + affix))  # reordered: WanAndroidFragment
            keys.add(_norm(base))
        if page_name.endswith(affix):
            base = page_name[: -len(affix)]
            keys.add(_norm(affix + base))
            keys.add(_norm(base))
    keys.discard("")
    return keys


def find_screen_source(module: AndroidModule, page_name: str, max_chars: int = 12000) -> str:
    """Return the source of the Activity/Fragment class backing this page, or ''."""
    keys = _candidate_keys(page_name)
    fuzzy: str | None = None
    for src in module.source_files:
        if src.suffix not in (".kt", ".java"):
            continue
        try:
            text = src.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        classes = [_norm(m.group(1)) for m in _CLASS.finditer(text)]
        if any(c in keys for c in classes):
            return text[:max_chars]
        # fuzzy fallback: a class that contains (or is contained by) the page key
        if fuzzy is None:
            tgt = _norm(page_name)
            if any(tgt and (tgt in c or c in tgt) and abs(len(c) - len(tgt)) <= 4 for c in classes):
                fuzzy = text[:max_chars]
    return fuzzy or ""
