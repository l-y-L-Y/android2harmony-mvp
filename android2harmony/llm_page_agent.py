"""LLM-first ArkUI page generation.

Replaces the old "debug shell" template path: instead of stamping every page
with a debug-navigation scaffold, this asks the model to faithfully translate a
real Android layout (or Compose screen) into one ArkUI page, preserving the
original text (incl. Chinese) and visual structure.

Design notes:
- mimo-v2.5-pro is a reasoning model: a large share of output_tokens is spent on
  hidden reasoning, so max_tokens must be generous (default 12000) or the visible
  code gets truncated mid-file.
- Unknown `$r('app.media.X')` references are sanitized to a media name that
  actually exists in the generated project, otherwise hvigor fails to compile.
"""
from __future__ import annotations

import re
from typing import Callable

from .knowledge import ARKTS_RULES, component_cheatsheet
from .llm_provider import call_llm, extract_code_block

TEMPLATE_MEDIA = {"foreground", "background", "layered_image"}

PAGE_SYSTEM = (
    "You are a senior HarmonyOS ArkUI engineer migrating an Android app to HarmonyOS "
    "(Stage model, ArkTS). You translate ONE Android screen into ONE faithful, complete, "
    "compilable ArkUI page. Return ONLY the .ets file content - no markdown fences, no prose."
)

# ArkUI/ArkTS API rules distilled from real hvigor compile failures. Injected into
# both the page-generation prompt (prevention) and the build-repair prompt (cure).
ARKUI_RULES = """ArkUI/ArkTS API rules (violating these breaks the hvigor build):
- Layout: use Blank() for flexible space, NEVER Spacer(). Stack has NO .justifyContent - use Column/Row for justifyContent, or Stack({ alignContent: Alignment.Center }).
- Text: color is .fontColor(...), never .color(...). Text has NO .verticalAlign, .singleLine, .maxWidth, .includeFontPadding, .autoLink, .fontLinkColor. Use .maxLines(1) for one line, .constraintSize({ maxWidth: 200 }) to cap width, .textAlign(TextAlign.Center) to align.
- TextInput: set value via constructor `TextInput({ text: this.x, placeholder: '...' })`, never .text(...). It has NO .singleLine/.multiline/.autoLink/.maxLines.
- Image: .objectFit(ImageFit.Cover|Contain|Fill|Auto|None). backgroundImageSize uses ImageSize.Cover|Contain|Auto (there is NO ImageSize.Stretch).
- margin/padding: use numeric left/right/top/bottom (e.g. .margin({ left: 8, top: 4 })). Do NOT use start/end with a number - those RTL keys need LengthMetrics and fail to compile.
- Checkbox: selection is .select(boolean), not .selected. Toggle uses Toggle({ type: ToggleType.Switch, isOn: this.x }).
- There is NO AutoLink / AutoLinkType in ArkUI.
- State: EVERY identifier used in build() must be a declared @State/@Prop/local; reference fields as `this.field`. Do not use undeclared names.
- ArkTS forbids `any` and reading arbitrary properties off `Object`. For list/model rows, declare an `interface` and type arrays as `MyItem[]` (e.g. `@State items: NewsItem[] = [...]`), then access `item.title` on the typed item.
- Interfaces: declare each interface name ONCE per file (duplicate names cause arkts-no-decl-merging). Give every interface a unique, specific name.
- ArkTS has NO optional-by-omission: every object literal must set ALL fields its interface declares. If a field may be absent, mark it optional with `?` in the interface (e.g. `avatar?: string`). Keep every sample object consistent with its interface.
- @Entry @Component struct must have a `build()` and balanced braces."""


def build_page_prompt(
    page_name: str,
    layout_source: str,
    app_label: str,
    source_kind: str = "xml",
    string_hints: str = "",
    available_media: set[str] | None = None,
) -> str:
    media_list = ", ".join(sorted(available_media)) if available_media else "foreground, background"
    fence = "xml" if source_kind == "xml" else "kotlin"
    hints = f"\nString resources you may reference (name -> value):\n{string_hints}\n" if string_hints else ""
    return f"""Migrate this Android {source_kind} screen into a single HarmonyOS ArkUI page.

App: {app_label}
Page struct name (must match EXACTLY): {page_name}

HARD REQUIREMENTS:
- Output one complete, compilable ArkTS file: `@Entry @Component struct {page_name} {{ build() {{ ... }} }}`.
- PRESERVE every visible text string EXACTLY (Chinese stays Chinese, e.g. "检查新版本", "版本：1.0.0"). Never translate or anglicize UI text.
- Keep the app's ORIGINAL language. When you must invent tab labels, buttons, or sample data not given in the source, write them in the SAME language as the provided string resources / existing text (an English app stays English; a Chinese app stays Chinese). Do not switch languages.
- Faithfully reproduce the visual layout: orientation, ordering, alignment/gravity, spacing, bold/size emphasis, lists/grids, toolbars, inputs, buttons, images.
- Use real ArkUI components only: Text, Button, Image, Column, Row, Stack, Flex, List/ListItem, Grid/GridItem, TextInput, Checkbox, Toggle, Scroll, Divider, Tabs.
- Lists/RecyclerView/GridView: render with `ForEach` over a small local `@State` sample array of realistic items derived from the screen's domain (NOT generic "Sample Item").
- Media: only reference `$r('app.media.NAME')` where NAME is one of: {media_list}. If unsure, omit the image or use `$r('app.media.foreground')`. Never invent other resource names.
- Do NOT emit any "debug navigation", route-button list, or migration-scaffold UI.
- Unknown click actions: use empty `() => {{}}` with a `// TODO` comment.
- Self-contained: do not import project files. State fields must use `this.` inside methods.
- Output the COMPLETE file. Do not stop early or summarize.

{ARKUI_RULES}

{ARKTS_RULES}

{component_cheatsheet()}
{hints}
Android {source_kind} source:
```{fence}
{layout_source[:16000]}
```"""


def generate_arkui_page(
    page_name: str,
    layout_source: str,
    app_label: str,
    source_kind: str = "xml",
    string_hints: str = "",
    available_media: set[str] | None = None,
    max_tokens: int = 12000,
    call_fn: Callable[[str, str, int], str] | None = None,
) -> str:
    """Generate one ArkUI page from an Android screen. Raises RuntimeError on failure."""
    call = call_fn or call_llm
    prompt = build_page_prompt(page_name, layout_source, app_label, source_kind, string_hints, available_media)
    media = _media_lower(available_media)

    last_err = ""
    for attempt in range(3):
        p = prompt if attempt == 0 else prompt + "\n\nYour previous output was invalid or truncated. Return the COMPLETE valid .ets file only."
        try:
            response = call(p, PAGE_SYSTEM, max_tokens)
        except Exception as exc:  # network/timeout: worth another attempt before falling back
            last_err = f"{type(exc).__name__}: {exc}"
            continue
        code = sanitize_page(extract_code_block(response), page_name, media)
        ok, reason = validate_page(code, page_name)
        if ok:
            return code
        last_err = reason
    raise RuntimeError(f"LLM page generation failed for {page_name}: {last_err}")


def _media_lower(available_media: set[str] | None) -> set[str]:
    base = {m.lower() for m in TEMPLATE_MEDIA}
    if available_media:
        base |= {m.lower() for m in available_media}
    return base


def sanitize_page(code: str, page_name: str, available_media: set[str]) -> str:
    code = code.strip()
    # strip stray markdown fences if extract missed them
    code = re.sub(r"^```[a-zA-Z]*\n", "", code)
    code = re.sub(r"\n```$", "", code).strip()

    # fix unknown media references so the project compiles
    def fix_media(match: re.Match[str]) -> str:
        name = match.group(1)
        if name.lower() in available_media:
            return match.group(0)
        return "$r('app.media.foreground')"

    code = re.sub(r"\$r\('app\.media\.([^']+)'\)", fix_media, code)

    # ensure the struct name matches the route page name exactly
    m = re.search(r"struct\s+([A-Za-z_][A-Za-z0-9_]*)", code)
    if m and m.group(1) != page_name:
        code = re.sub(rf"\bstruct\s+{re.escape(m.group(1))}\b", f"struct {page_name}", code, count=1)
    return apply_arkts_fixups(code)


def apply_arkts_fixups(code: str) -> str:
    """Deterministic fixes for unambiguous ArkUI API mistakes that the model repeats.
    Only safe, context-free substitutions live here; semantic errors go to LLM repair."""
    # Spacer -> Blank (Spacer does not exist in ArkUI)
    code = re.sub(r"\bSpacer\s*\(", "Blank(", code)
    # ImageSize.Stretch -> Cover (Stretch is not a valid ImageSize)
    code = code.replace("ImageSize.Stretch", "ImageSize.Cover")
    # startIcon is the launcher icon, not page content; lowercase 'starticon' also fails
    # to resolve (real resource is camelCase). Always use the page placeholder instead.
    code = re.sub(r"\$r\('app\.media\.start[Ii]con'\)", "$r('app.media.foreground')", code)
    # margin/padding start:/end: (RTL LocalizedEdges) require LengthMetrics, not a raw
    # number. left:/right: accept numbers, so retarget numeric directional keys.
    code = re.sub(r"\bstart:\s*(-?\d)", r"left: \1", code)
    code = re.sub(r"\bend:\s*(-?\d)", r"right: \1", code)
    return code


def validate_page(code: str, page_name: str) -> tuple[bool, str]:
    if not code.strip():
        return False, "empty"
    if "@Component" not in code:
        return False, "missing @Component"
    if f"struct {page_name}" not in code:
        return False, "missing struct name"
    if "build()" not in code:
        return False, "missing build()"
    opens = code.count("{")
    closes = code.count("}")
    if opens != closes:
        return False, f"unbalanced braces ({opens} open / {closes} close) - likely truncated"
    if not code.rstrip().endswith("}"):
        return False, "does not end with '}' - likely truncated"
    return True, ""
