import json
import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import _report_json, _report_md
from android2harmony.model import AndroidProject


class GeneratorReportTest(unittest.TestCase):
    def test_report_mentions_validation_summary_and_press_back_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = AndroidProject(root=Path(tmp), name="Sample", modules=[], settings_file=None, gradle_files=[])

            payload = json.loads(_report_json(project, []))
            markdown = _report_md(project, [], Path(tmp) / "out")

            self.assertIn("press_back", payload["validation"]["supportedActions"])
            self.assertIn("validation-summary.json", payload["validation"]["summary"])
            self.assertIn("report-index.json", payload["validation"]["reportIndex"])
            self.assertIn("validation-summary.md", markdown)
            self.assertIn("report-index.md", markdown)
            self.assertIn("press_back", markdown)


if __name__ == "__main__":
    unittest.main()
