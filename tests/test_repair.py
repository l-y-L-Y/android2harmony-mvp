import json
import tempfile
import unittest
from pathlib import Path

from android2harmony.cli import build_parser
from android2harmony.repair import create_patch_plan, create_repair_context, diagnose_repair_context, write_repair_diagnosis


class RepairTest(unittest.TestCase):
    def test_create_repair_context_includes_validation_and_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = root / "agent-workspace" / "05-repair" / "device-validation-result.json"
            result.parent.mkdir(parents=True)
            result.write_text(json.dumps({"passed": False, "cases": [{"name": "case", "errors": ["missing"]}]}), encoding="utf-8")
            page = root / "entry" / "src" / "main" / "ets" / "pages" / "ActivityDetail.ets"
            page.parent.mkdir(parents=True)
            page.write_text("@Component\nstruct ActivityDetail { build() {} }\n", encoding="utf-8")

            context = create_repair_context(root, validation_file=result)

            self.assertEqual(context["validation"]["passed"], False)
            self.assertTrue(context["relevantFiles"])
            self.assertIn("ActivityDetail.ets", context["relevantFiles"][0]["path"])

    def test_diagnose_repair_context_merges_llm_json(self):
        context = {"validation": {"passed": False}, "relevantFiles": []}
        diagnosis = diagnose_repair_context(
            context,
            call_fn=lambda prompt, system, max_tokens: '{"rootCause":"bad state","patchPlan":["fix state"],"risk":"low"}',
        )

        self.assertEqual(diagnosis["rootCause"], "bad state")
        self.assertEqual(diagnosis["patchPlan"], ["fix state"])
        self.assertTrue(diagnosis["rerunCommands"])

    def test_diagnose_repair_context_skips_llm_when_validation_passed(self):
        calls = []
        context = {"validation": {"passed": True}, "relevantFiles": []}
        diagnosis = diagnose_repair_context(
            context,
            call_fn=lambda prompt, system, max_tokens: calls.append(prompt) or "{}",
        )

        self.assertEqual(diagnosis["rootCause"], "Validation passed; no repair required.")
        self.assertEqual(calls, [])

    def test_diagnose_repair_context_normalizes_sparse_llm_output(self):
        context = {"project": "D:/out/app", "validation": {"passed": False}, "relevantFiles": []}
        diagnosis = diagnose_repair_context(
            context,
            call_fn=lambda prompt, system, max_tokens: '{"rootCause":"missing text"}',
        )

        self.assertEqual(diagnosis["rootCause"], "missing text")
        self.assertIsInstance(diagnosis["patchPlan"], list)
        self.assertIn("python -m android2harmony.cli validate-dsl", " ".join(diagnosis["rerunCommands"]))

    def test_create_patch_plan_normalizes_steps_for_repair_agent(self):
        context = {"project": "D:/out/app", "validation": {"passed": False}}
        diagnosis = {
            "rootCause": "detail route lost state",
            "failedCase": "open detail",
            "filesToInspect": ["entry/src/main/ets/pages/ActivityDetail.ets"],
            "patchPlan": ["Preserve selected item in Store before router.push", "Regenerate and rerun DSL"],
            "rerunCommands": ["python -m android2harmony.cli validate-dsl D:/out/app"],
            "risk": "low",
        }

        plan = create_patch_plan(diagnosis, context)

        self.assertEqual(plan["agent"], "repair-patch-agent")
        self.assertEqual(plan["status"], "proposed")
        self.assertFalse(plan["applyAutomatically"])
        self.assertEqual(plan["rootCause"], "detail route lost state")
        self.assertEqual(plan["steps"][0]["step"], "Preserve selected item in Store before router.push")
        self.assertEqual(plan["steps"][0]["target"], "entry/src/main/ets/pages/ActivityDetail.ets")

    def test_write_repair_diagnosis_writes_patch_plan_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = root / "agent-workspace" / "05-repair" / "device-validation-result.json"
            result.parent.mkdir(parents=True)
            result.write_text(json.dumps({"passed": False, "cases": [{"name": "case", "errors": ["missing"]}]}), encoding="utf-8")

            output = write_repair_diagnosis(
                root,
                validation_file=result,
                call_fn=lambda prompt, system, max_tokens: '{"rootCause":"bad state","patchPlan":["fix state"],"risk":"low"}',
            )
            patch_plan = output.with_name("repair-patch-plan.json")

            self.assertTrue(output.exists())
            self.assertTrue(patch_plan.exists())
            data = json.loads(patch_plan.read_text(encoding="utf-8"))
            self.assertEqual(data["agent"], "repair-patch-agent")
            self.assertEqual(data["status"], "proposed")

    def test_validate_dsl_parser_accepts_repair_diagnose_flag(self):
        args = build_parser().parse_args(["validate-dsl", "D:/out/app", "--repair-diagnose"])

        self.assertTrue(args.repair_diagnose)


if __name__ == "__main__":
    unittest.main()
