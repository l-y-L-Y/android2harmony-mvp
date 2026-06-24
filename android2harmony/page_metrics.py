"""Static page-content metrics: detect generated ArkUI pages that compile and run
but render (near-)empty content -- the "silent blank page" fidelity loss that the
build-repair degrade counter cannot see (it only counts pages it had to stub).

Heuristic, source-level (no device/LLM needed). Classifies every generated page so a
batch can report a blank/placeholder ratio and we can track it falling over time.

Known limitation: a page whose only content is a `ForEach` over a state list that is
empty at runtime (data-driven blank) is classified `rich` here -- catching that needs
the on-device dumpLayout check (follow-up). This module catches the structural cases we
have actually observed: explicit placeholders, and pages that render <=1 content node
(e.g. gank FragmentHome = a single edit icon on a colored background)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

# Visible-text markers that mean "this is a placeholder shown to the user", not content.
_PLACEHOLDER_MARKERS = ("占位", "此处显示", "敬请期待", "暂无", "coming soon", "comming soon", "todo")

# Container widgets that carry a (potentially long) list of real content.
_LIST_WIDGETS = ("List", "Grid", "ForEach", "LazyForEach", "Swiper", "Tabs", "WaterFlow")
# Leaf/interactive widgets that count as visible content.
_LEAF_WIDGETS = (
    "Image", "TextInput", "TextArea", "Button", "Search", "Toggle",
    "Checkbox", "Slider", "Radio", "TextPicker", "Rating", "QRCode", "Web", "Video",
)

PAGE_CLASSES = ("rich", "minimal", "near_empty", "empty", "placeholder")

# Markers exclusive to the rule-based template fallback (xml_layout_translator._page_shell),
# emitted when LLM page generation failed/timed out and the page degraded to a low-fidelity
# stub (mock `MigratedListItem` data, page-name-as-title, string app.media paths). LLM pages
# route via `@kit.ArkUI`'s `router` and never touch these; the launcher Index uses only
# `NavigationCompat.replace`, not `.params`/`MigratedListItem` -- so neither false-positives.
# A fallback page can score structurally "rich" (it has a Grid/ForEach) yet be unfaithful, so
# we track it as its own dimension and exclude it from the faithful-rich ratio.
_FALLBACK_MARKERS = ("interface MigratedListItem", "NavigationCompat.params(")

# Names that are NOT real screens: RecyclerView item templates (adapter_*.xml) and
# intentional empty-state / loading views. These are near-empty BY DESIGN, so they must
# not count against the blank-like ratio (which should reflect real screens only).
_NON_SCREEN = re.compile(r"(?i)(^Adapter|^Item|Adapter$|EmptyView|NoData|NoNetwork|Loading|Placeholder)")

_BLANK_LIKE = ("empty", "near_empty", "placeholder")


@dataclass
class PageMetric:
    name: str
    klass: str
    texts: int
    images: int
    lists: int
    inputs: int
    embedded: int
    content: int
    screen: bool
    fallback: bool = False


def _struct_name(code: str) -> str:
    m = re.search(r"\bstruct\s+([A-Za-z_]\w*)", code)
    return m.group(1) if m else ""


def _count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text))


def classify_page(code: str, page_names: tuple[str, ...] = ()) -> PageMetric:
    # Count the WHOLE struct (not just from build()): content often lives in @Builder
    # methods declared before build() (e.g. SideBarContainer host pages). ArkUI widgets
    # only appear in render code, so imports/interfaces don't inflate the counts.
    body_nc = re.sub(r"//[^\n]*", "", code)
    self_name = _struct_name(code)

    texts = _count(r"\bText\s*\(", body_nc)
    images = _count(r"\bImage\s*\(", body_nc)
    lists = sum(_count(rf"\b{w}\s*\(", body_nc) for w in _LIST_WIDGETS)
    inputs = sum(_count(rf"\b{w}\s*\(", body_nc) for w in _LEAF_WIDGETS if w != "Image")
    # A page that embeds another generated page component (e.g. `FragmentLogin()`)
    # delegates its rendering -- it is not blank.
    embedded = sum(
        _count(rf"\b{re.escape(n)}\s*\(\s*\)", body_nc)
        for n in page_names if n and n != self_name
    )

    literals = re.findall(r"\bText\s*\(\s*['\"]([^'\"]*)['\"]", body_nc)
    is_placeholder = any(
        marker in lit.lower() if marker.isascii() else marker in lit
        for lit in literals for marker in _PLACEHOLDER_MARKERS
    )

    content = texts + images + inputs + 3 * lists
    if is_placeholder and lists == 0 and embedded == 0 and content <= 4:
        klass = "placeholder"
    elif lists > 0 or embedded >= 1:
        klass = "rich"
    elif content == 0:
        klass = "empty"
    elif content <= 1:
        klass = "near_empty"
    elif content <= 3:
        klass = "minimal"
    else:
        klass = "rich"
    screen = _NON_SCREEN.search(self_name or "") is None
    fallback = any(marker in code for marker in _FALLBACK_MARKERS)
    return PageMetric("", klass, texts, images, lists, inputs, embedded, content, screen, fallback)


def project_page_metrics(project_dir: Path) -> dict:
    pages_dir = Path(project_dir) / "entry" / "src" / "main" / "ets" / "pages"
    files = sorted(pages_dir.glob("*.ets"))
    sources = {f: f.read_text(encoding="utf-8", errors="ignore") for f in files}
    page_names = tuple(n for n in (_struct_name(s) for s in sources.values()) if n)

    metrics: list[PageMetric] = []
    for f in files:
        m = classify_page(sources[f], page_names)
        m.name = f.name
        metrics.append(m)

    by_class = {c: sum(1 for m in metrics if m.klass == c) for c in PAGE_CLASSES}
    screens = [m for m in metrics if m.screen]
    # "blank-like" counts only real screens -> item templates / empty-state views excluded
    blank_like = sum(1 for m in screens if m.klass in _BLANK_LIKE)
    # rule-template fallbacks may LOOK rich (Grid/ForEach over mock data) but are unfaithful,
    # so they do not count toward the faithful-rich ratio.
    fallback_pages = sum(1 for m in screens if m.fallback)
    rich = sum(1 for m in screens if m.klass == "rich" and not m.fallback)
    nscreen = len(screens)
    return {
        "project": Path(project_dir).name,
        "totalPages": len(metrics),
        "screenPages": nscreen,
        "excludedNonScreen": len(metrics) - nscreen,
        "byClass": by_class,
        "blankLikePages": blank_like,
        "blankLikeRatio": round(blank_like / nscreen, 3) if nscreen else 0.0,
        "fallbackPages": fallback_pages,
        "fallbackRatio": round(fallback_pages / nscreen, 3) if nscreen else 0.0,
        "richRatio": round(rich / nscreen, 3) if nscreen else 0.0,
        "pages": [asdict(m) for m in metrics],
    }


def render_metrics_md(report: dict) -> str:
    lines = [
        f"# 页面内容度量：{report['project']}",
        "",
        f"- 屏幕页数：{report['screenPages']}（另排除非屏幕页 {report['excludedNonScreen']} 个：列表项/空状态）",
        f"- 空白/占位嫌疑屏幕：{report['blankLikePages']}（占比 {report['blankLikeRatio']:.0%}）",
        f"- 规则模板兜底屏幕（LLM 失败/超时降级，低保真，建议复核）：{report.get('fallbackPages', 0)}（占比 {report.get('fallbackRatio', 0):.0%}）",
        f"- 富内容屏幕占比（已剔除兜底页）：{report['richRatio']:.0%}",
        "- 分类：" + "，".join(f"{c}={report['byClass'][c]}" for c in PAGE_CLASSES),
        "",
        "| 页面 | 分类 | 文本 | 图片 | 列表 | 交互 | 嵌入 | 屏幕 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for p in report["pages"]:
        if p.get("fallback"):
            flag = " ⚠️兜底"
        elif p["screen"] and p["klass"] in _BLANK_LIKE:
            flag = " ⚠️"
        else:
            flag = ""
        lines.append(
            f"| {p['name']} | {p['klass']}{flag} | {p['texts']} | {p['images']} | "
            f"{p['lists']} | {p['inputs']} | {p['embedded']} | {'是' if p['screen'] else '否'} |"
        )
    return "\n".join(lines) + "\n"


def write_page_metrics(project_dir: Path) -> dict:
    report = project_page_metrics(project_dir)
    out = Path(project_dir)
    (out / "page-metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "page-metrics.md").write_text(render_metrics_md(report), encoding="utf-8")
    return report
