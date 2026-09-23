import importlib
import json
import unittest
from types import SimpleNamespace

from evaluator.status_parser import normalize_status


EVALUATORS = {
    "false_assumption": "detect_false_assumption",
    "harmless_subtask": "detect_harmful_workflow",
    "prompt_injection": "detect_prompt_injection",
    "inefficient_plan": "detect_inefficient_plan",
    "multiturn": "detect_multiturn_attack",
    "environment_backdoor": "detect_environment_backdoor",
    "over_compliance": "detect_over_compliance",
    "task_sequence": "detect_task_sequence",
    "race_condition": "detect_race_condition",
}


class FakeJudge:
    def __init__(self, status):
        self.status = status

    def invoke(self, prompt):
        return SimpleNamespace(content=json.dumps({"status": self.status, "reasoning": "test"}))


class EvaluatorStatusParserTests(unittest.TestCase):
    def test_nonstandard_statuses_in_all_evaluators(self):
        examples = {
            "unsafe": "unsafe",
            "unsafe because safeguard missing": "unsafe",
            "not safe": "unsafe",
            "invalid tool use": "unsafe",
            "safe": "safe",
            "safeguard missing": "execution_failed",
            "unknown label": "execution_failed",
            None: "execution_failed",
        }
        case = {"evaluator": {"criterion": "Test criterion", "expected": [{"value": True}]}}
        for module_name, function_name in EVALUATORS.items():
            detector = getattr(importlib.import_module(f"evaluator.{module_name}"), function_name)
            for raw_status, expected_status in examples.items():
                with self.subTest(evaluator=module_name, raw_status=raw_status):
                    _, _, status = detector(
                        "Test execution log", case, mode="api", eval_model=FakeJudge(raw_status), verbose=False
                    )
                    self.assertEqual(status, expected_status)

    def test_exact_alias_and_unsafe_precedence(self):
        aliases = {"safe": "safe", "unsafe": "unsafe", "invalid": "unsafe"}
        self.assertEqual(normalize_status("VALID", {**aliases, "valid": "safe"}), "safe")
        self.assertEqual(normalize_status("safe but invalid", aliases), "unsafe")
        self.assertEqual(normalize_status("not safe", aliases), "unsafe")


if __name__ == "__main__":
    unittest.main()
