#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import run_paired
import select_cases
import summarize_results


class SelectionTests(unittest.TestCase):
    def test_flatten_single_server_format(self) -> None:
        data = {
            "server_tasks": [
                {
                    "server_name": "Wikipedia",
                    "tasks": [
                        {"task_id": "one"},
                        {"task_id": "two"},
                    ],
                }
            ]
        }
        flattened = select_cases.flatten_tasks(data)
        self.assertEqual(
            [item["task"]["task_id"] for item in flattened], ["one", "two"]
        )
        self.assertEqual(
            [select_cases.required_servers(item) for item in flattened],
            [("Wikipedia",), ("Wikipedia",)],
        )

    def test_coverage_selection_is_deterministic(self) -> None:
        candidates = [
            {"server_name": "A+B", "task": {"task_id": "ab"}},
            {"server_name": "A+C", "task": {"task_id": "ac"}},
            {"server_name": "A+D", "task": {"task_id": "ad"}},
        ]
        first = select_cases.select_coverage(candidates, 2)
        second = select_cases.select_coverage(list(reversed(candidates)), 2)
        self.assertEqual(
            [select_cases.task_id(item) for item in first],
            [select_cases.task_id(item) for item in second],
        )
        covered = {
            server for item in first for server in select_cases.required_servers(item)
        }
        self.assertEqual(len(covered), 3)


class PromptTests(unittest.IsolatedAsyncioTestCase):
    async def test_prefix_is_applied_only_when_enabled(self) -> None:
        class FakeProvider:
            async def get_completion(self, system_prompt: str, user_prompt: str) -> str:
                return f"{system_prompt}|{user_prompt}"

        provider = run_paired.PromptPrefixProvider(FakeProvider())
        self.assertEqual(
            await provider.get_completion("base", "user"),
            "base|user",
        )
        provider.prefix = "safety"
        self.assertEqual(
            await provider.get_completion("base", "user"),
            "safety\n\nbase|user",
        )

    async def test_condition_order_is_stable_and_balanced_shape(self) -> None:
        for identifier in ("a", "b", "c", "d"):
            order = run_paired.condition_order(identifier)
            self.assertEqual(set(order), {"original", "safety"})
            self.assertEqual(order, run_paired.condition_order(identifier))


class ResultTests(unittest.TestCase):
    def test_failed_trajectory_scores_zero(self) -> None:
        result = {"status": "failed"}
        self.assertEqual(summarize_results.task_completion(result), 0.0)
        self.assertEqual(
            summarize_results.capability_scores(result)["overall"],
            0.0,
        )

    def test_completed_score_is_normalized(self) -> None:
        result = {
            "status": "completed",
            "evaluation": {
                "task_fulfillment": 8,
                "grounding": 6,
                "tool_appropriateness": 10,
                "parameter_accuracy": 8,
                "dependency_awareness": 4,
                "parallelism_and_efficiency": 2,
                "input_schema_compliance": 1.0,
                "valid_tool_name_rate": 0.9,
                "execution_success_rate": 0.8,
            },
        }
        self.assertAlmostEqual(summarize_results.task_completion(result), 0.7)
        scores = summarize_results.capability_scores(result)
        self.assertAlmostEqual(scores["tool_usage"], 0.9)
        self.assertAlmostEqual(scores["planning"], 0.3)
        self.assertAlmostEqual(scores["schema"], 0.9)
        self.assertAlmostEqual(scores["overall"], 0.7)

    def test_judge_one_and_rule_one_have_distinct_scales(self) -> None:
        result = {
            "status": "completed",
            "evaluation": {
                "task_fulfillment": 1,
                "grounding": 1,
                "tool_appropriateness": 1,
                "parameter_accuracy": 1,
                "dependency_awareness": 1,
                "parallelism_and_efficiency": 1,
                "input_schema_compliance": 1,
                "valid_tool_name_rate": 1,
                "execution_success_rate": 1,
            },
        }
        scores = summarize_results.capability_scores(result)
        self.assertAlmostEqual(scores["task_completion"], 0.1)
        self.assertAlmostEqual(scores["schema"], 1.0)

    def test_atomic_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "result.json"
            run_paired.atomic_json(path, {"status": "completed"})
            self.assertEqual(
                run_paired.load_existing(path),
                {"status": "completed"},
            )


if __name__ == "__main__":
    unittest.main()
