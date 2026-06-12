import json
import unittest
from pathlib import Path

from android2harmony.model import AndroidProject
from android2harmony.pipeline import _test_dsl


class PipelineDslTest(unittest.TestCase):
    def test_pokedex_dsl_includes_back_navigation_case(self):
        project = AndroidProject(root=Path("D:/work/Android/Pokedex"), name="Pokedex", modules=[], settings_file=None, gradle_files=[])

        data = json.loads(_test_dsl(project, ["pages/ActivityMain", "pages/ActivityDetail"]))

        case_names = [case["name"] for case in data["cases"]]
        self.assertIn("back_from_detail_to_list", case_names)
        back_case = next(case for case in data["cases"] if case["name"] == "back_from_detail_to_list")
        self.assertIn({"action": "press_back"}, back_case["steps"])
        self.assertEqual(back_case["steps"][-1], {"assert": "text_visible", "target": "Bulbasaur"})


if __name__ == "__main__":
    unittest.main()
