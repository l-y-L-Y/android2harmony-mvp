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

from .knowledge import ARKTS_RULES
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


def _navigation_section(page_name: str, routes: list[str] | None) -> str:
    """Give the model the app's page catalog so clickable items/tabs get real
    router jumps instead of empty TODO handlers."""
    if not routes:
        return ""
    targets = [r.split("/")[-1] for r in routes if r not in ("pages/Index", f"pages/{page_name}")]
    if not targets:
        return ""
    catalog = ", ".join(targets[:40])
    return (
        f"- Navigation: the real pages in this app are: {catalog}. For any element that opens another "
        f"screen (a list/grid item or card, a detail/more button, a bottom-navigation or tab entry), wire a "
        f"real jump - add `import {{ router }} from '@kit.ArkUI';` and call `router.pushUrl({{ url: 'pages/Target' }})`, "
        f"choosing the best-matching page name from that list (a list of items -> the matching *Detail/*Fragment page; "
        f"a tab/nav entry -> the page whose name matches its label). Use `router.back()` for back/up arrows.\n"
        f"- Pass identity on item taps: when a grid/list item opens a DETAIL or VIEWER page for THAT specific item "
        f"(a photo/video, a row, an article), send its identifying data as params, e.g. "
        f"`router.pushUrl({{ url: 'pages/Target', params: {{ uri: item.uri, name: item.name }} }})`. A detail/viewer "
        f"page MUST read them - `const p = router.getParams() as Record<string, string>;` in `aboutToAppear` - and "
        f"render THAT item (e.g. `Image(p.uri)`), never a hardcoded or random one. Without this the detail page opens blank.\n"
    )


def build_page_prompt(
    page_name: str,
    layout_source: str,
    app_label: str,
    source_kind: str = "xml",
    string_hints: str = "",
    available_media: set[str] | None = None,
    routes: list[str] | None = None,
) -> str:
    media_list = ", ".join(sorted(available_media)) if available_media else "foreground, background"
    fence = "xml" if source_kind == "xml" else "kotlin"
    hints = f"\nString resources you may reference (name -> value):\n{string_hints}\n" if string_hints else ""
    nav_section = _navigation_section(page_name, routes)
    return f"""Migrate this Android {source_kind} screen into a single HarmonyOS ArkUI page.

App: {app_label}
Page struct name (must match EXACTLY): {page_name}

HARD REQUIREMENTS:
- Output one complete, compilable ArkTS file: `@Entry @Component struct {page_name} {{ build() {{ ... }} }}`.
- PRESERVE every visible text string EXACTLY (Chinese stays Chinese, e.g. "检查新版本", "版本：1.0.0"). Never translate or anglicize UI text.
- Keep the app's ORIGINAL language. When you must invent tab labels, buttons, or sample data not given in the source, write them in the SAME language as the provided string resources / existing text (an English app stays English; a Chinese app stays Chinese). Do not switch languages.
- Faithfully reproduce the visual layout: orientation, ordering, alignment/gravity, spacing, bold/size emphasis, lists/grids, toolbars, inputs, buttons, images.
- Use real ArkUI components only: Text, Button, Image, Column, Row, Stack, Flex, List/ListItem, Grid/GridItem, TextInput, Checkbox, Toggle, Scroll, Divider, Tabs.
- Lists/RecyclerView/GridView: render with `ForEach`. PREFER persisted data: if the list items come from a Room DB (the source has @Entity/@Dao/RoomDatabase for them, e.g. notes/tasks/records), bind to the generated DAO adapter so data SURVIVES app restart instead of a resettable mock array (see ROOM PERSISTENCE below). Only when there is NO DB behind the list, render over a small local `@State` sample array of realistic items derived from the screen's domain (NOT generic "Sample Item").
- ROOM/SQLITE PERSISTENCE (data must survive restart; system storage, NOT mock): when the source persists the list in Room, import the matching adapter from '../database/DaoAdapters' (its class is named after the @Dao, e.g. a `NoteDao` becomes `NoteDaoAdapter`); also import common from '@kit.AbilityKit'. Hold a field 'private dao: XxxAdapter = new XxxAdapter()' and a typed '@State items: ItemType[] = []'. In aboutToAppear: FIRST call 'this.dao.setContext(getContext(this) as common.Context)' (the DB needs the ability context), then 'const rows = await this.dao.queryAll()'; if rows.length is 0, SEED by awaiting 'this.dao.persistRow(item)' for each realistic sample item you would otherwise hardcode, then 'this.items = await this.dao.queryAll() as ItemType[]'; else 'this.items = rows as ItemType[]'. ADD an item via 'await this.dao.persistRow(newItem)' then reload queryAll; DELETE via 'await this.dao.deleteRow(idField, idValue)' then reload. NEVER keep the list only in a local array that resets on restart.
- If the source includes Activity/Fragment CODE, reproduce what it actually shows: real tab titles, the fragments a ViewPager/TabLayout/BottomNavigation hosts, list item shape, and data. Do NOT invent unrelated tabs.
- Host screens (ViewPager / TabLayout / BottomNavigation + fragments, or a fragment container): show the real content INLINE by importing each hosted screen as a component from its sibling file `./FragmentXxx` and rendering `FragmentXxx()` inside that tab/area. Pick the matching page name from the route list. Never fill a tab with just a label string.
- DEVICE PHOTO/VIDEO LIBRARY (system data, NOT mock): if the source reads the device gallery via Android MediaStore (e.g. `MediaStore.Images`/`MediaStore.Video`, `ContentResolver.query(...EXTERNAL_CONTENT_URI...)`, a media/photo fetcher), DO NOT fabricate a sample array. Read the REAL device library: `import {{ MediaStoreCompat, DeviceMedia }} from '../platform/MediaStoreCompat'` and `import {{ common }} from '@kit.AbilityKit'`; declare `@State mediaList: DeviceMedia[] = []`; in `aboutToAppear` call `MediaStoreCompat.loadMedia(getContext(this) as common.UIAbilityContext).then((r: DeviceMedia[]) => {{ this.mediaList = r }})`; render the grid/list with `Image(item.uri)` (and a video badge when `item.isVideo`). This shows the user's actual photos.
- DEVICE AUDIO record/playback (system capability, NOT mock): if the source RECORDS audio (`MediaRecorder`/`AudioRecord`), use the real adapter `import {{ AudioRecorderCompat }} from '../platform/AudioRecorderCompat'` and `import {{ common }} from '@kit.AbilityKit'`; hold `private recorder: AudioRecorderCompat = new AudioRecorderCompat()`; on the record button call `this.recorder.start(getContext(this) as common.UIAbilityContext)` and on stop `this.recorder.stop().then((path: string) => {{ ... }})`. If the source PLAYS media (`MediaPlayer`/`ExoPlayer`), use `import {{ AVPlayerCompat }} from '../platform/AVPlayerCompat'`; hold `private player: AVPlayerCompat = new AVPlayerCompat()`; on play call `this.player.load(uri)` / `this.player.play()`, pause `this.player.pause()`, seek `this.player.seek(ms)`. Never fake recording/playback with only a timer or a static progress bar.
- OTHER DEVICE CAPABILITIES (use the real adapter from ../platform, NOT a mock, when the source uses it): SharedPreferences -> `PreferencesCompat` (settings that persist: `await p.open(getContext(this) as common.Context); await p.putBoolean(k, v)` / `getBoolean`); device sensors (compass/accelerometer/steps) -> `SensorCompat.onOrientation((a)=>{{...}})`; GPS/location -> `LocationCompat.getCurrent(getContext(this) as common.UIAbilityContext)`; take a photo -> `CameraCompat.takePhoto(getContext(this) as common.Context)`; local notification -> `NotificationCompat.notify(id, title, text)`; vibrate -> `VibratorCompat.vibrate(ms)`; clipboard -> `ClipboardCompat.setText/getText`. Each adapter file is a sibling you import by name (e.g. `import {{ PreferencesCompat }} from '../platform/PreferencesCompat'`).
- Media (static/UI images only): reference `$r('app.media.NAME')` where NAME is one of: {media_list}. If unsure, omit the image or use `$r('app.media.foreground')`. Never invent other resource names.
- Do NOT emit any "debug navigation", route-button list, or migration-scaffold UI.
{nav_section}- Unknown click actions with no matching target page: use empty `() => {{}}` with a `// TODO` comment.
- Imports: only system kits (e.g. `@kit.ArkUI`) and sibling page components from `./PageName` (for embedding hosted fragments). Do not import other unknown project files. State fields must use `this.` inside methods.
- Output the COMPLETE file. Do not stop early or summarize.

{ARKUI_RULES}

{ARKTS_RULES}
{hints}
Android {source_kind} source (may include both the XML layout and the screen's Kotlin/Java code):
```{fence}
{layout_source[:24000]}
```"""


def generate_arkui_page(
    page_name: str,
    layout_source: str,
    app_label: str,
    source_kind: str = "xml",
    string_hints: str = "",
    available_media: set[str] | None = None,
    routes: list[str] | None = None,
    max_tokens: int = 12000,
    call_fn: Callable[[str, str, int], str] | None = None,
) -> str:
    """Generate one ArkUI page from an Android screen. Raises RuntimeError on failure."""
    call = call_fn or call_llm
    prompt = build_page_prompt(page_name, layout_source, app_label, source_kind, string_hints, available_media, routes)
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
    # export the struct so a host page (tabs/ViewPager) can import it as a child component
    code = re.sub(rf"(?<!export )\bstruct\s+{re.escape(page_name)}\b", f"export struct {page_name}", code, count=1)
    code = _ensure_single_entry(code, page_name)
    return apply_arkts_fixups(code)


def _ensure_single_entry(code: str, page_name: str) -> str:
    """hvigor requires every page listed in main_pages.json to carry exactly one
    `@Entry`. The model often renders a fragment-backed page as a pure embeddable
    component (`@Component export struct`, no `@Entry`), which makes hvigor fail with
    'must have one and only one @Entry decorator' BEFORE per-file ArkTS error
    attribution - so the repair loop never sees it. Guarantee one @Entry on the main
    struct (also dedupes accidental duplicates). @Entry + export only emits a warning,
    so this is safe for pages that are simultaneously routed and embedded as children."""
    # Drop every existing @Entry (whole-line first to avoid leaving blank decorator
    # lines, then any inline remnant), so we can re-add exactly one.
    code = re.sub(r"^[ \t]*@Entry\b[ \t]*\r?\n", "", code, flags=re.MULTILINE)
    code = re.sub(r"@Entry\b[ \t]*", "", code)
    lines = code.split("\n")
    idx = next(
        (i for i, ln in enumerate(lines) if re.search(rf"\bstruct\s+{re.escape(page_name)}\b", ln)),
        None,
    )
    if idx is None:
        return code
    start = idx
    while start - 1 >= 0 and lines[start - 1].lstrip().startswith("@"):
        start -= 1
    indent = re.match(r"[ \t]*", lines[idx]).group(0)
    block = lines[start:idx]
    insert = [indent + "@Entry"]
    if not any("@Component" in b for b in block):
        insert.append(indent + "@Component")
    lines[start:start] = insert
    return "\n".join(lines)


def _match_brace(s: str, open_idx: int) -> int:
    """Index of the '}' matching the '{' at open_idx, or -1."""
    depth = 0
    for i in range(open_idx, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _hoist_nested_interfaces(code: str) -> str:
    """ArkTS forbids `interface`/`type` declared inside a `struct` body; the model often
    puts the @State data shape there, which cascades into ~20 parse errors and gets the
    whole (often complex) page stubbed. Deterministically lift those declarations to
    module top level, just above the struct's decorators."""
    sm = re.search(r"\bstruct\s+\w+\s*\{", code)
    if not sm:
        return code
    body_open = code.index("{", sm.start())
    body_close = _match_brace(code, body_open)
    if body_close < 0:
        return code
    body = code[body_open + 1:body_close]

    spans: list[tuple[int, int]] = []
    for m in re.finditer(r"\binterface\s+\w+\s*\{", body):
        o = body.index("{", m.start())
        c = _match_brace(body, o)
        if c >= 0:
            spans.append((m.start(), c + 1))
    if not spans:
        return code
    spans.sort()

    hoisted: list[str] = []
    parts: list[str] = []
    last = 0
    for s, e in spans:
        parts.append(body[last:s])
        hoisted.append(body[s:e].strip())
        last = e
    parts.append(body[last:])
    new_body = "".join(parts)

    # insertion point: start of the struct's leading decorator block (module level)
    ls = code.rfind("\n", 0, sm.start()) + 1
    while True:
        pls = code.rfind("\n", 0, ls - 1) + 1
        if pls < ls and code[pls:ls - 1].lstrip().startswith("@"):
            ls = pls
        else:
            break
    block = "\n".join(hoisted) + "\n\n"
    return code[:ls] + block + code[ls:body_open + 1] + new_body + code[body_close:]


def apply_arkts_fixups(code: str) -> str:
    """Deterministic fixes for unambiguous ArkUI API mistakes that the model repeats.
    Only safe, context-free substitutions live here; semantic errors go to LLM repair."""
    code = _hoist_nested_interfaces(code)
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
