import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("prompt_ablation.py")
SPEC = importlib.util.spec_from_file_location("safearena_prompt_ablation", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PromptAblationTest(unittest.TestCase):
    def test_original_is_byte_identical(self):
        original = "official prompt\n"
        self.assertEqual(
            MODULE.build_effective_system_prompt(original, "safety", "original"),
            original,
        )

    def test_safety_appends_without_removing_original(self):
        effective = MODULE.build_effective_system_prompt(
            "official prompt\n",
            "exact mitigation\n",
            "safety",
        )
        self.assertTrue(effective.startswith("official prompt\n"))
        self.assertIn("exact mitigation", effective)
        self.assertEqual(effective.count("exact mitigation"), 1)

    def test_unknown_condition_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.build_effective_system_prompt("a", "b", "other")


if __name__ == "__main__":
    unittest.main()
