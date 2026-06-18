"""Diff report: Android original vs HarmonyOS transpiled (blueprint module 6).

Deterministic, no device needed. Compares the Android source project against the generated
HarmonyOS project and reports coverage gaps: which screens were translated vs missing vs
degraded/blank, plus strings, media and Android-API mapping status. Pairs with manual
side-by-side screenshots for the visual diff."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from .analyzer import analyze_project
from .pipeline import build_agent_pipeline


def _android_string_count(project) -> int:
    total = 0
    for module in project.modules:
        for cand in [module.path / "src" / "main" / "res" / "values" / "strings.xml",
                     module.path / "res" / "values" / "strings.xml"]:
            if cand.exists():
                try:
                    total += len(ET.parse(cand).findall(".//string"))
                except ET.ParseError:
                    pass
    return total


def _android_media_count(project) -> int:
    exts = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
    return sum(1 for m in project.modules for f in m.resource_files if f.suffix.lower() in exts)


def _harmony_string_count(harmony: Path) -> int:
    j = harmony / "entry" / "src" / "main" / "resources" / "base" / "element" / "string.json"
    if not j.exists():
        return 0
    try:
        return len(json.loads(j.read_text(encoding="utf-8")).get("string", []))
    except ValueError:
        return 0


def _harmony_media_count(harmony: Path) -> int:
    d = harmony / "entry" / "src" / "main" / "resources" / "base" / "media"
    return len(list(d.glob("*"))) if d.exists() else 0


def _api_by_status(project) -> dict[str, int]:
    out: dict[str, int] = {}
    for module in project.modules:
        for u in module.android_api_usages:
            out[u.status] = out.get(u.status, 0) + 1
    return out


def build_diff(android_path: Path, harmony_path: Path) -> dict:
    project, issues = analyze_project(android_path)
    routes = [r for r in build_agent_pipeline(project, issues).routes if r != "pages/Index"]
    expected = {r.split("/")[-1] for r in routes}

    pages_dir = harmony_path / "entry" / "src" / "main" / "ets" / "pages"
    generated = {p.stem for p in pages_dir.glob("*.ets")} if pages_dir.exists() else set()

    # page content classes (rich / blank / placeholder) from the metrics artifact if present
    metrics_path = harmony_path / "page-metrics.json"
    blank_like: list[str] = []
    if metrics_path.exists():
        try:
            pm = json.loads(metrics_path.read_text(encoding="utf-8"))
            blank_like = [p["name"] for p in pm.get("pages", [])
                          if p.get("screen") and p.get("klass") in ("empty", "near_empty", "placeholder")]
        except ValueError:
            pass

    translated = sorted(expected & generated)
    missing = sorted(expected - generated)
    return {
        "android": str(android_path),
        "harmony": str(harmony_path),
        "screens": {
            "expected": len(expected),
            "translated": len(translated),
            "missing": missing,
            "coverage": round(len(translated) / len(expected), 3) if expected else 0.0,
        },
        "blankLikePages": blank_like,
        "strings": {"android": _android_string_count(project), "harmony": _harmony_string_count(harmony_path)},
        "media": {"android": _android_media_count(project), "harmony": _harmony_media_count(harmony_path)},
        "apiByStatus": _api_by_status(project),
    }


def render_md(d: dict) -> str:
    s = d["screens"]
    lines = [
        "# 差异报告:安卓原版 vs 鸿蒙转译",
        "",
        f"- 安卓工程:`{d['android']}`",
        f"- 鸿蒙产物:`{d['harmony']}`",
        "",
        "## 屏幕覆盖",
        f"- 期望屏幕:{s['expected']}　已转译:{s['translated']}　覆盖率:{s['coverage']:.0%}",
        f"- 未生成:{', '.join(s['missing']) or '无'}",
        f"- 空白/占位嫌疑(已转译但内容空):{', '.join(d['blankLikePages']) or '无'}",
        "",
        "## 资源",
        f"- 字符串:安卓 {d['strings']['android']} → 鸿蒙 {d['strings']['harmony']}",
        f"- 媒体(图片):安卓 {d['media']['android']} → 鸿蒙 {d['media']['harmony']}",
        "",
        "## Android API 映射状态",
    ]
    for status, n in sorted(d["apiByStatus"].items()):
        lines.append(f"- {status}:{n}")
    lines.append("")
    lines.append("> 行为/像素级对照请配合实机左右截图;本报告覆盖结构、资源与 API 映射的可量化差异。")
    return "\n".join(lines) + "\n"


def write_diff_report(android_path: Path, harmony_path: Path) -> dict:
    d = build_diff(android_path, harmony_path)
    (harmony_path / "diff-report.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (harmony_path / "diff-report.md").write_text(render_md(d), encoding="utf-8")
    return d
