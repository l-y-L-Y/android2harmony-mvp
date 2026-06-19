"""Android -> HarmonyOS system-capability map (offline-app system APIs).

Single source of truth for which device capability an Android API belongs to, the
HarmonyOS Kit/API it maps to, the permission it needs, and the runtime adapter module
(an `XxxCompat.ets`, like MediaStoreCompat) that bridges them so the transpiled app
actually RUNS the capability instead of mocking it.

This drives: (1) capability detection over source, (2) permission injection, (3) which
adapter module the generator emits, (4) honest coverage reporting (done vs planned).
The authoritative data lives in data/system_api_map.json (sourced from official Kit
docs); exact Harmony symbols are pinned at adapter build time by the hvigor compile +
on-device probe (the compile is the final source of truth)."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_MAP_PATH = Path(__file__).parent / "data" / "system_api_map.json"


@lru_cache(maxsize=1)
def load_capabilities() -> list[dict]:
    return json.loads(_MAP_PATH.read_text(encoding="utf-8"))["capabilities"]


@lru_cache(maxsize=1)
def _detectors() -> list[tuple[dict, re.Pattern]]:
    out: list[tuple[dict, re.Pattern]] = []
    for cap in load_capabilities():
        pats = cap.get("android_detect") or []
        if pats:
            out.append((cap, re.compile("|".join(pats))))
    return out


def capability(cap_id: str) -> dict | None:
    return next((c for c in load_capabilities() if c["id"] == cap_id), None)


def detect_capabilities(source_text: str) -> list[str]:
    """Capability ids whose Android API patterns appear in the given source text,
    in declared (priority) order."""
    return [cap["id"] for cap, pat in _detectors() if pat.search(source_text)]


def permissions_for(cap_ids) -> list[str]:
    """Distinct ohos.permission.* required by the given capabilities (parenthetical
    notes in the data are stripped), preserving first-seen order."""
    perms: list[str] = []
    for cid in cap_ids:
        cap = capability(cid)
        if not cap:
            continue
        for raw in cap.get("permissions", []):
            p = raw.split(" ")[0].strip()
            if p.startswith("ohos.permission.") and p not in perms:
                perms.append(p)
    return perms


def adapter_for(cap_id: str) -> str | None:
    cap = capability(cap_id)
    return cap.get("adapter_module") if cap else None


def coverage() -> dict[str, list[str]]:
    """Capability titles grouped by adapter status: done / partial / planned."""
    out: dict[str, list[str]] = {}
    for cap in load_capabilities():
        out.setdefault(cap.get("status", "planned"), []).append(cap["title_cn"])
    return out
