import json
import tempfile
import unittest
from pathlib import Path

from android2harmony.build_summary import parse_hvigor_log, write_build_summary
from android2harmony.cli import build_parser


class BuildSummaryTest(unittest.TestCase):
    def test_parse_hvigor_success_log(self):
        summary = parse_hvigor_log(
            """
> hvigor Finished :entry:default@CompileArkTS... after 7 s 140 ms
> hvigor BUILD SUCCESSFUL in 15 s 30 ms
"""
        )

        self.assertTrue(summary["passed"])
        self.assertEqual(summary["status"], "success")
        self.assertEqual(summary["errorCount"], 0)
        self.assertIn("15 s 30 ms", summary["duration"])

    def test_parse_hvigor_failure_log_extracts_errors(self):
        summary = parse_hvigor_log(
            """
> hvigor ERROR: Failed :entry:default@CompileArkTS...
Error Message: Object literal must correspond to some explicitly declared class At File: entry/src/main/ets/Foo.ets:12:8
> hvigor ERROR: BUILD FAILED in 13 s 70 ms
"""
        )

        self.assertFalse(summary["passed"])
        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["errorCount"], 2)
        self.assertIn("CompileArkTS", " ".join(summary["errors"]))
        self.assertIn("Foo.ets", " ".join(summary["errors"]))

    def test_write_build_summary_creates_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "hvigor.log"
            log.write_text("> hvigor BUILD SUCCESSFUL in 1 s 20 ms\n", encoding="utf-8")

            output = write_build_summary(root, log)

            self.assertTrue(output.exists())
            self.assertTrue(output.with_suffix(".md").exists())
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["agent"], "build-report-agent")
            self.assertEqual(data["status"], "success")
            self.assertIn("Build Summary", output.with_suffix(".md").read_text(encoding="utf-8"))

    def test_write_build_summary_reads_powershell_utf16_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "hvigor.log"
            log.write_text("> hvigor BUILD SUCCESSFUL in 2 s 10 ms\n", encoding="utf-16")

            output = write_build_summary(root, log)

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(data["passed"])
            self.assertEqual(data["duration"], "2 s 10 ms")

    def test_cli_accepts_build_summary_command(self):
        args = build_parser().parse_args(["build-summary", "D:/out/app", "--log", "D:/out/app/hvigor.log"])

        self.assertEqual(args.command, "build-summary")
        self.assertEqual(str(args.log), "D:\\out\\app\\hvigor.log")


if __name__ == "__main__":
    unittest.main()
