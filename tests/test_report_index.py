import json
import tempfile
import unittest
from pathlib import Path

from android2harmony.cli import build_parser
from android2harmony.report_index import write_report_index


class ReportIndexTest(unittest.TestCase):
    def test_write_report_index_aggregates_build_and_validation_summaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_dir = root / "agent-workspace" / "06-report"
            report_dir.mkdir(parents=True)
            (report_dir / "build-summary.json").write_text(
                json.dumps({"status": "success", "passed": True, "duration": "1 s", "errorCount": 0, "warningCount": 1}),
                encoding="utf-8",
            )
            (report_dir / "validation-summary.json").write_text(
                json.dumps({"passed": True, "passRate": "3/3", "caseCount": 3, "passedCaseCount": 3, "failedCaseCount": 0}),
                encoding="utf-8",
            )
            repair_dir = root / "agent-workspace" / "05-repair"
            repair_dir.mkdir(parents=True)
            (repair_dir / "repair-diagnosis-llm.json").write_text(
                json.dumps({"rootCause": "ok", "risk": "low", "patchPlan": []}),
                encoding="utf-8",
            )

            output = write_report_index(root)

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["build"]["status"], "success")
            self.assertEqual(data["validation"]["passRate"], "3/3")
            self.assertEqual(data["repair"]["risk"], "low")
            self.assertTrue(output.with_suffix(".md").exists())
            self.assertIn("Report Index", output.with_suffix(".md").read_text(encoding="utf-8"))

    def test_write_report_index_handles_missing_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            output = write_report_index(root)

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["build"]["status"], "missing")
            self.assertEqual(data["validation"]["status"], "missing")

    def test_cli_accepts_report_index_command(self):
        args = build_parser().parse_args(["report-index", "D:/out/app"])

        self.assertEqual(args.command, "report-index")
        self.assertEqual(str(args.project), "D:\\out\\app")


if __name__ == "__main__":
    unittest.main()
