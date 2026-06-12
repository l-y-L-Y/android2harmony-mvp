import tempfile
import unittest
from pathlib import Path

from android2harmony.xml_layout_translator import translate_layout_file


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


if __name__ == "__main__":
    unittest.main()
