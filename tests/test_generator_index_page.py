import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import _index_page
from android2harmony.model import AndroidModule, AndroidProject


class GeneratorIndexPageTest(unittest.TestCase):
    def test_index_page_exposes_clickable_route_navigation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = AndroidProject(root=root, name="Tusky", modules=[], settings_file=None, gradle_files=[])
            module = AndroidModule(name="app", path=root / "app", kind="application", source_files=[], features={"android_api"})

            page = _index_page(project, module, ["pages/Index", "pages/ActivityLists"])

            self.assertIn("Generated HarmonyOS client migration", page)
            self.assertIn("NavigationCompat.push", page)
            self.assertIn("App entry", page)
            self.assertIn("Pages", page)
            self.assertIn("ActivityLists", page)
            self.assertIn("Open app", page)


if __name__ == "__main__":
    unittest.main()
