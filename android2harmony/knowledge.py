"""ArkUI/ArkTS knowledge base.

Bootstraps the compile-error knowledge from authoritative sources instead of
discovering every rule one app at a time:
- `data/arkui_components.json`: distilled official ArkUI component -> valid attribute
  names (from the UITrans / DevEco component reference, 138 components).
- ARKTS_RULES: the official "TypeScript -> ArkTS" strictness constraints (arkts-no-*).

Used two ways:
- generation: inject a compact cheatsheet + ArkTS rules so the model avoids errors.
- repair: given a "Property 'x' does not exist on type 'YAttribute'" error, look up the
  real valid attributes of component Y and hand them to the model (targeted, not guessed).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent / "data" / "arkui_components.json"

# Components that show up on almost every migrated page; their valid attributes are
# worth surfacing up front during generation.
_COMMON = [
    "Text", "Column", "Row", "Stack", "Flex", "Image", "Button", "TextInput",
    "List", "ListItem", "Grid", "GridItem", "Scroll", "Tabs", "Divider", "Blank",
    "Checkbox", "Toggle", "Progress", "Badge", "Swiper", "Search",
]

# Official TypeScript -> ArkTS adaptation constraints (the arkts-no-* rule family).
ARKTS_RULES = """ArkTS strictness (official constraints - violating them fails the build):
- No `any`/`unknown`. Type every variable, parameter, @State field and array element.
- No object literal as a type. Declare an `interface`/`class` and reference it by name.
- No declaration merging: each interface/class/type name must be unique in the file.
- An object literal must match a declared interface and include ALL its required fields
  (mark truly optional fields with `?`). Arrays of rows: `items: Row[] = [...]`.
- Plain data carriers use `interface`; access fields as `obj.field` on the typed object.
- No adding properties not declared on a type; no structural casts between unrelated types.
- Reference component state via `this.field` inside build()/methods."""


@lru_cache(maxsize=1)
def _components() -> dict[str, list[str]]:
    try:
        return json.loads(_DATA.read_text(encoding="utf-8"))
    except Exception:
        return {}


def valid_attributes(component: str) -> list[str]:
    """Valid attribute names for a component. Accepts 'Stack' or 'StackAttribute'."""
    name = re.sub(r"Attribute$", "", component.strip())
    return _components().get(name, [])


@lru_cache(maxsize=1)
def component_cheatsheet() -> str:
    comps = _components()
    lines = ["ArkUI component attributes (use ONLY these; anything else fails to compile):"]
    for name in _COMMON:
        attrs = comps.get(name)
        if attrs:
            shown = ", ".join(attrs[:16])
            lines.append(f"- {name}: {shown}")
        elif name in comps:
            lines.append(f"- {name}: (container)")
    return "\n".join(lines)


def attribute_hints_for_errors(errors: list[str]) -> str:
    """For repair: extract component types from 'does not exist on type XAttribute'
    errors and return their real valid attributes, so the fix is informed not guessed."""
    types: list[str] = []
    seen: set[str] = set()
    for err in errors:
        for m in re.finditer(r"type '([A-Za-z0-9_]+)Attribute'", err):
            name = m.group(1)
            if name not in seen and name in _components():
                seen.add(name)
                types.append(name)
    if not types:
        return ""
    lines = ["Valid attributes for the components in these errors (use only these):"]
    for name in types:
        lines.append(f"- {name}: {', '.join(_components()[name])}")
    return "\n".join(lines)
