"""Validation-gated repair learning cache (the blueprint's case/knowledge library, landed safely).

Records each VALIDATED repair as (error signature + original file content) -> fixed file content.
On a later repair with the identical signature, the proven fix is reused deterministically instead
of asking the (non-deterministic) model again. Benefits:
  - learning: successful "error -> fix" cases accumulate and are reused (case library).
  - reproducibility: re-transpiling the same project replays proven fixes, so a run can't randomly
    regress into a different/worse LLM output (the exact problem behind the $isRefreshing crash).

Validation gate: fixes are STAGED during a repair run and only COMMITTED to the persistent cache
when the build actually passes; failed runs are discarded. So only build-confirmed fixes are stored.

v1 matches on identical (file, errors, content). Upgrading the match to semantic similarity
(embeddings) turns this into the blueprint's vector knowledge base.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

_STORE_ENV = "ANDROID2HARMONY_REPAIR_CACHE"
_DEFAULT_STORE = Path.home() / ".android2harmony" / "repair-cache.json"

# Fixes proven valid this run but not yet build-confirmed.
_pending: dict[str, str] = {}


def _store_path() -> Path:
    return Path(os.getenv(_STORE_ENV, str(_DEFAULT_STORE)))


def _load() -> dict[str, str]:
    p = _store_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def make_key(filename: str, errors: list[str], content: str) -> str:
    h = hashlib.sha256()
    h.update(filename.encode("utf-8"))
    h.update(b"\x00")
    h.update("\n".join(sorted(errors)).encode("utf-8"))
    h.update(b"\x00")
    h.update(content.encode("utf-8"))
    return h.hexdigest()


def lookup(filename: str, errors: list[str], content: str) -> str | None:
    """Return a previously build-confirmed fix for this exact (file, errors, content), or None."""
    return _load().get(make_key(filename, errors, content))


def stage(filename: str, errors: list[str], content: str, fixed: str) -> None:
    """Record a candidate fix for the current run (committed only if the build later passes)."""
    _pending[make_key(filename, errors, content)] = fixed


def commit() -> int:
    """Persist staged fixes (call when the build PASSED). Returns number newly learned."""
    if not _pending:
        return 0
    store = _load()
    new = 0
    for k, v in _pending.items():
        if k not in store:
            new += 1
        store[k] = v
    p = _store_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    _pending.clear()
    return new


def discard() -> None:
    """Drop staged fixes (call when the build did NOT pass), so only validated fixes are learned."""
    _pending.clear()
