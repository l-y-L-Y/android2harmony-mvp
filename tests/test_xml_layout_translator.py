import tempfile
import unittest
from pathlib import Path

from android2harmony.xml_layout_translator import page_to_layout_file, translate_layout_file


class XmlLayoutTranslatorTest(unittest.TestCase):
    def test_reserved_page_name_and_empty_stack_translate_safely(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = root / "search.xml"
            layout.write_text(
                """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
""",
                encoding="utf-8",
            )

            code = translate_layout_file(layout, "Search", {}, ["pages/Search"])

            self.assertIn("struct SearchPage", code)
            self.assertIn("Text('FrameLayout')", code)
            self.assertNotIn("Blank()", code)


    def test_page_to_layout_matches_activity_naming_conventions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout_dir = root / "res" / "layout"
            layout_dir.mkdir(parents=True)
            for name in ["activity_main.xml", "activity_detail.xml", "feedback.xml"]:
                (layout_dir / name).write_text("<x/>", encoding="utf-8")
            # MainActivity <-> activity_main (reversed word order), FeedBack <-> feedback
            self.assertEqual(page_to_layout_file(root, "pages/MainActivity").name, "activity_main.xml")
            self.assertEqual(page_to_layout_file(root, "pages/DetailActivity").name, "activity_detail.xml")
            self.assertEqual(page_to_layout_file(root, "pages/FeedBack").name, "feedback.xml")
            self.assertIsNone(page_to_layout_file(root, "pages/Nonexistent"))


if __name__ == "__main__":
    unittest.main()
