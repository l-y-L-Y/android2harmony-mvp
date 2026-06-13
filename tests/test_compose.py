from pathlib import Path

from android2harmony.compose import compose_screen_source, discover_compose_screens
from android2harmony.model import AndroidModule


def _module(tmp_path: Path, files: dict[str, str]) -> AndroidModule:
    srcs = []
    for name, content in files.items():
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        srcs.append(p)
    return AndroidModule(name="app", path=tmp_path, kind="application", source_files=srcs)


def test_discovers_screen_composables(tmp_path: Path):
    files = {
        "Home.kt": "@Composable\nfun HomeScreen(vm: HomeViewModel) {\n  Column { Text(\"hi\") }\n}\n",
        "Detail.kt": "@Composable\nfun DetailRoute(id: String) {\n  Text(\"detail\")\n}\n",
        "Util.kt": "fun helper() = 1\n",  # no composable -> ignored
    }
    screens = discover_compose_screens(_module(tmp_path, files))
    assert set(screens) == {"HomeScreen", "DetailRoute"}
    assert screens["HomeScreen"].name == "Home.kt"


def test_skips_preview_composables(tmp_path: Path):
    files = {
        "Prev.kt": "@Preview\n@Composable\nfun PreviewHomeScreen() {\n  HomeScreen()\n}\n",
    }
    screens = discover_compose_screens(_module(tmp_path, files))
    assert screens == {}


def test_compose_source_truncates(tmp_path: Path):
    f = tmp_path / "Big.kt"
    f.write_text("x" * 50000, encoding="utf-8")
    assert len(compose_screen_source(f, max_chars=1000)) == 1000


def test_non_kotlin_ignored(tmp_path: Path):
    files = {"Layout.java": "@Composable fun HomeScreen() {}"}
    assert discover_compose_screens(_module(tmp_path, files)) == {}
