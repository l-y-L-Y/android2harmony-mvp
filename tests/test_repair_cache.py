import importlib
import os
import tempfile
import unittest
from pathlib import Path


class RepairCacheTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["ANDROID2HARMONY_REPAIR_CACHE"] = str(Path(self.tmp.name) / "cache.json")
        # fresh module state (clears module-level _pending) under the temp store
        import android2harmony.repair_cache as rc
        self.rc = importlib.reload(rc)
        self.rc.discard()

    def tearDown(self):
        self.rc.discard()
        os.environ.pop("ANDROID2HARMONY_REPAIR_CACHE", None)
        self.tmp.cleanup()

    def test_key_is_deterministic_and_content_sensitive(self):
        k1 = self.rc.make_key("P.ets", ["L1 err"], "content A")
        k2 = self.rc.make_key("P.ets", ["L1 err"], "content A")
        k3 = self.rc.make_key("P.ets", ["L1 err"], "content B")
        self.assertEqual(k1, k2)
        self.assertNotEqual(k1, k3)

    def test_validation_gate_only_committed_fixes_are_reused(self):
        errs = ["L5:5 Cannot find name 'Spacer'"]
        # staged but NOT committed -> not visible (gate: build must pass first)
        self.rc.stage("P.ets", errs, "before", "after-fixed")
        self.assertIsNone(self.rc.lookup("P.ets", errs, "before"))
        # commit (build passed) -> now reusable
        learned = self.rc.commit()
        self.assertEqual(learned, 1)
        self.assertEqual(self.rc.lookup("P.ets", errs, "before"), "after-fixed")

    def test_discard_drops_staged_fixes(self):
        self.rc.stage("Q.ets", ["e"], "c", "f")
        self.rc.discard()
        self.assertEqual(self.rc.commit(), 0)
        self.assertIsNone(self.rc.lookup("Q.ets", ["e"], "c"))


if __name__ == "__main__":
    unittest.main()
