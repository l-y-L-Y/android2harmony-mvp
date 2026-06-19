import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import _page_source_kind
from android2harmony.model import AndroidModule


def _module_with_source(root: Path, class_name: str, body_len: int = 400) -> AndroidModule:
    src = root / "app" / "src" / "main" / "kotlin" / f"{class_name}.kt"
    src.parent.mkdir(parents=True)
    body = "// fullscreen viewer built in code\n" + ("val x = loadImage(uri)\n" * (body_len // 20))
    src.write_text(f"class {class_name} {{\n{body}\n}}\n", encoding="utf-8")
    return AndroidModule(name="app", path=root / "app", kind="application", source_files=[src])


class CodeDrivenPageRoutingTest(unittest.TestCase):
    def test_no_layout_but_real_source_routes_to_code_not_placeholder(self):
        # PhotoActivity: no XML layout, no Compose, but a real PhotoActivity.kt that builds
        # the fullscreen viewer in code. Must translate from source ("code"), not placeholder.
        with tempfile.TemporaryDirectory() as tmp:
            module = _module_with_source(Path(tmp), "PhotoActivity")
            kind, path = _page_source_kind(module, "PhotoActivity", "pages/PhotoActivity", {})
            self.assertEqual(kind, "code")
            self.assertIsNone(path)

    def test_no_layout_and_no_source_falls_back_to_placeholder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app").mkdir(parents=True)
            module = AndroidModule(name="app", path=root / "app", kind="application", source_files=[])
            kind, path = _page_source_kind(module, "GhostActivity", "pages/GhostActivity", {})
            self.assertIsNone(kind)
            self.assertIsNone(path)

    def test_trivial_stub_source_does_not_qualify_as_code(self):
        # a near-empty class is not worth an LLM page; should stay a placeholder
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "app" / "src" / "main" / "kotlin" / "TinyActivity.kt"
            src.parent.mkdir(parents=True)
            src.write_text("class TinyActivity\n", encoding="utf-8")
            module = AndroidModule(name="app", path=root / "app", kind="application", source_files=[src])
            kind, _ = _page_source_kind(module, "TinyActivity", "pages/TinyActivity", {})
            self.assertIsNone(kind)


if __name__ == "__main__":
    unittest.main()
