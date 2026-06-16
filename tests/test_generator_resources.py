import json
import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import (
    _copy_resources,
    _sanitize_resource_name,
    _strings_json,
)
from android2harmony.model import AndroidModule


class SanitizeResourceNameTest(unittest.TestCase):
    def test_dotted_and_dashed_names(self):
        self.assertEqual(_sanitize_resource_name("nb.title.app"), "nb_title_app")
        self.assertEqual(_sanitize_resource_name("a-b.c"), "a_b_c")
        self.assertEqual(_sanitize_resource_name("123x")[0], "_")
        self.assertEqual(_sanitize_resource_name("..."), "res")


class StringsJsonTest(unittest.TestCase):
    def test_illegal_string_names_are_sanitized_and_deduped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            values = root / "src" / "main" / "res" / "values"
            values.mkdir(parents=True)
            (values / "strings.xml").write_text(
                '<resources>'
                '<string name="nb.title.app">标题</string>'
                '<string name="nb_title_app">撞名</string>'
                '<string name="ok_name">保留</string>'
                '</resources>',
                encoding="utf-8",
            )
            module = AndroidModule(name="app", path=root, kind="application")
            data = json.loads(_strings_json(module, "Demo"))
            names = [s["name"] for s in data["string"]]
            # every emitted name is HarmonyOS-legal
            self.assertTrue(all(c.isalnum() or c == "_" for n in names for c in n))
            self.assertIn("nb_title_app", names)
            # dotted name collapsed to the same key as the existing one -> only once
            self.assertEqual(names.count("nb_title_app"), 1)
            self.assertIn("ok_name", names)


class CopyResourcesDedupTest(unittest.TestCase):
    def test_same_stem_different_extension_media_is_deduped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            res = root / "res" / "drawable"
            res.mkdir(parents=True)
            (res / "ic_play.png").write_bytes(b"a")
            (res / "ic_play.webp").write_bytes(b"b")
            out = root / "out"
            module = AndroidModule(
                name="app", path=root, kind="application",
                resource_files=[res / "ic_play.png", res / "ic_play.webp"],
            )
            copied = _copy_resources(module, out)
            media_dir = out / "entry" / "src" / "main" / "resources" / "base" / "media"
            stems = [p.stem for p in media_dir.iterdir()]
            self.assertEqual(stems.count("ic_play"), 1)  # only one survives -> no name conflict
            self.assertEqual(len(copied), 1)


if __name__ == "__main__":
    unittest.main()
