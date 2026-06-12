import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from android2harmony.device_validator import _find_text_bounds, _run_dsl_case, write_validation_summary


class DeviceValidatorTest(unittest.TestCase):
    def test_find_text_bounds_returns_none_for_empty_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            layout = Path(tmp) / "layout.json"
            layout.write_text("", encoding="utf-8")

            self.assertIsNone(_find_text_bounds(layout, "Bulbasaur"))

    def test_find_text_bounds_returns_none_for_invalid_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            layout = Path(tmp) / "layout.json"
            layout.write_text("{", encoding="utf-8")

            self.assertIsNone(_find_text_bounds(layout, "Bulbasaur"))

    def test_run_dsl_case_supports_press_back_action(self):
        commands = []

        def fake_run(command, cwd):
            commands.append(command)
            return ""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = {"name": "back", "steps": [{"action": "press_back"}]}

            with patch("android2harmony.device_validator._run", side_effect=fake_run), patch(
                "android2harmony.device_validator._capture_layout_and_screen"
            ):
                result = _run_dsl_case(root, Path("hdc.exe"), "com.example", "EntryAbility", case, 0)

            self.assertTrue(result["passed"])
            self.assertIn(["hdc.exe", "shell", "uitest", "uiInput", "keyEvent", "Back"], commands)

    def test_write_validation_summary_creates_report_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = root / "agent-workspace" / "05-repair" / "device-validation-result.json"
            result.parent.mkdir(parents=True)
            result.write_text(
                """{
  "passed": true,
  "bundle": "com.example",
  "cases": [
    {"name": "cold_start", "passed": true, "errors": []},
    {"name": "back_from_detail_to_list", "passed": true, "errors": []}
  ]
}
""",
                encoding="utf-8",
            )

            summary_path = write_validation_summary(root, result)

            self.assertTrue(summary_path.exists())
            self.assertTrue(summary_path.with_suffix(".md").exists())
            self.assertIn("2/2", summary_path.read_text(encoding="utf-8"))
            markdown = summary_path.with_suffix(".md").read_text(encoding="utf-8")
            self.assertIn("Validation Summary", markdown)
            self.assertIn("back_from_detail_to_list", markdown)


if __name__ == "__main__":
    unittest.main()
