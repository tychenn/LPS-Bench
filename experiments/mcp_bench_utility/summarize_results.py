#!/usr/bin/env python3
"""Summarize paired MCP-Bench utility results without calling any model."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def normalized_judge_score(value: Any) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    # MCP-Bench's LLM-judge dimensions use a 0--10 scale.
    return float(value) / 10.0


def normalized_rule_rate(value: Any) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    # Rule-based schema/tool-call metrics are already in [0, 1].
    return float(value)


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def task_completion(result: dict[str, Any]) -> float | None:
    if result.get("status") != "completed":
        return 0.0
    evaluation = result.get("evaluation")
    if not isinstance(evaluation, dict):
        return None
    values = [
        normalized_judge_score(evaluation.get("task_fulfillment")),
        normalized_judge_score(evaluation.get("grounding")),
    ]
    valid = [value for value in values if value is not None]
    return mean(valid)


def capability_scores(result: dict[str, Any]) -> dict[str, float | None]:
    if result.get("status") != "completed":
        return {
            "task_completion": 0.0,
            "tool_usage": 0.0,
            "planning": 0.0,
            "schema": 0.0,
            "overall": 0.0,
        }
    evaluation = result.get("evaluation", {})
    if not isinstance(evaluation, dict):
        return {}

    def judge_metric(*names: str) -> float | None:
        values = [normalized_judge_score(evaluation.get(name)) for name in names]
        return mean([value for value in values if value is not None])

    def rule_metric(*names: str) -> float | None:
        values = [normalized_rule_rate(evaluation.get(name)) for name in names]
        return mean([value for value in values if value is not None])

    scores = {
        "task_completion": judge_metric("task_fulfillment", "grounding"),
        "tool_usage": judge_metric("tool_appropriateness", "parameter_accuracy"),
        "planning": judge_metric("dependency_awareness", "parallelism_and_efficiency"),
        "schema": rule_metric(
            "input_schema_compliance",
            "valid_tool_name_rate",
            "execution_success_rate",
        ),
    }
    scores["overall"] = mean([value for value in scores.values() if value is not None])
    return scores


def load_results(directory: Path) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    if not directory.is_dir():
        return loaded
    for path in sorted(directory.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        identifier = value.get("task_id")
        if isinstance(identifier, str):
            loaded[identifier] = value
    return loaded


def fmt_score(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def fmt_delta(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:+.1f} pp".replace("-", "−")


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    script_dir = Path(__file__).resolve().parent
    model_manifest = json.loads(
        (script_dir / "model_manifest.json").read_text(encoding="utf-8")
    )["models"]
    selection = json.loads(
        (script_dir / "selected_tasks.json").read_text(encoding="utf-8")
    )
    expected_ids = [item["task"]["task_id"] for item in selection.get("tasks", [])]
    stratum_by_id: dict[str, str] = {}
    for item in selection.get("tasks", []):
        identifier = item["task"]["task_id"]
        server_count = len(item.get("server_name", "").split("+"))
        stratum_by_id[identifier] = {
            1: "single",
            2: "two_server",
            3: "three_server",
        }.get(server_count, "unknown")

    report: dict[str, Any] = {
        "run_dir": str(run_dir),
        "expected_task_count": len(expected_ids),
        "models": {},
    }
    rows: list[dict[str, Any]] = []
    for model_key, model in model_manifest.items():
        model_dir = run_dir / "results" / model_key
        conditions = {
            condition: load_results(model_dir / "tasks" / condition)
            for condition in ("original", "safety")
        }
        model_report: dict[str, Any] = {}
        condition_scores: dict[str, float | None] = {}
        for condition, results in conditions.items():
            existing = [
                results[identifier]
                for identifier in expected_ids
                if identifier in results
            ]
            completed = [
                result for result in existing if result.get("status") == "completed"
            ]
            per_task = [task_completion(result) for result in existing]
            valid_task_scores = [value for value in per_task if value is not None]
            aggregates: defaultdict[str, list[float]] = defaultdict(list)
            strata: defaultdict[str, list[float]] = defaultdict(list)
            for identifier, result in results.items():
                if identifier not in stratum_by_id:
                    continue
                scores = capability_scores(result)
                for name, value in scores.items():
                    if value is not None:
                        aggregates[name].append(value)
                completion = scores.get("task_completion")
                if completion is not None:
                    strata[stratum_by_id[identifier]].append(completion)
            condition_score = mean(valid_task_scores)
            condition_scores[condition] = condition_score
            model_report[condition] = {
                "existing": len(existing),
                "completed": len(completed),
                "failed": len(existing) - len(completed),
                "missing": len(expected_ids) - len(existing),
                "failure_inclusive_task_completion": condition_score,
                "capabilities": {
                    name: mean(values) for name, values in aggregates.items()
                },
                "task_completion_by_stratum": {
                    name: mean(values) for name, values in strata.items()
                },
            }
        paired = [
            identifier
            for identifier in expected_ids
            if identifier in conditions["original"]
            and identifier in conditions["safety"]
        ]
        delta = (
            condition_scores["safety"] - condition_scores["original"]
            if condition_scores["safety"] is not None
            and condition_scores["original"] is not None
            else None
        )
        model_report["paired_tasks"] = len(paired)
        model_report["utility_change"] = delta
        report["models"][model_key] = model_report
        rows.append(
            {
                "display_name": model["display_name"],
                "original": condition_scores["original"],
                "safety": condition_scores["safety"],
                "delta": delta,
                "paired": len(paired),
                "expected": len(expected_ids),
                "original_failures": model_report["original"]["failed"],
                "safety_failures": model_report["safety"]["failed"],
            }
        )

    summary_json = args.output.with_suffix(".json")
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# MCP-Bench utility summary",
        "",
        f"Run: `{run_dir}`",
        "",
        "Task completion is the failure-inclusive mean of MCP-Bench judge "
        "`task_fulfillment` and `grounding`. A recorded failed trajectory "
        "contributes zero; a not-yet-run task is shown as missing and is not "
        "silently scored.",
        "",
        "| Model | Original | Safety | Change | Paired | Failures O/S |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['display_name']} | {fmt_score(row['original'])} | "
            f"{fmt_score(row['safety'])} | {fmt_delta(row['delta'])} | "
            f"{row['paired']}/{row['expected']} | "
            f"{row['original_failures']}/{row['safety_failures']} |"
        )
    lines.extend(
        [
            "",
            f"Machine-readable details: `{summary_json}`",
            "",
        ]
    )
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Wrote {summary_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
