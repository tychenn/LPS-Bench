#!/usr/bin/env python3
"""Evaluate and summarize the paired LPS-derived utility experiment."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TRACING"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluator.utility_completion import (  # noqa: E402
    VALID_STATUSES,
    evaluate_utility_completion,
)
from langchain_ollama import ChatOllama  # noqa: E402


CASE_ROOT = REPO_ROOT / "utility_cases" / "lps_bench_derived" / "cases"
MODEL_SPECS = (
    {
        "display": "Llama-3.1-8B-Instruct",
        "ollama": "llama3.1:8b",
        "safe": "llama31_8b",
    },
    {
        "display": "Llama-3.1-70B-Instruct",
        "ollama": "llama3.1:70b",
        "safe": "llama31_70b",
    },
    {
        "display": "Qwen3-8B-Instruct",
        "ollama": "qwen3:8b",
        "safe": "qwen3_8b",
    },
    {
        "display": "Qwen3-32B-Instruct",
        "ollama": "qwen3:32b",
        "safe": "qwen3_32b",
    },
)
CONDITIONS = ("original", "safety")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--judge-model", default="qwen3:32b")
    parser.add_argument("--update-markdown", type=Path, default=None)
    parser.add_argument("--max-retries", type=int, default=3)
    return parser.parse_args()


def create_judge(model_name: str) -> Any:
    host = os.getenv("OLLAMA_HOST", "")
    if host and not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    kwargs: dict[str, Any] = {
        "model": model_name,
        "temperature": 0,
        "num_predict": int(os.getenv("JUDGE_NUM_PREDICT", "384")),
        "reasoning": False,
        "client_kwargs": {
            "trust_env": False,
            "timeout": float(os.getenv("OLLAMA_CLIENT_TIMEOUT", "300")),
        },
    }
    context_length = os.getenv("OLLAMA_CONTEXT_LENGTH")
    if context_length:
        parsed_context_length = int(context_length)
        if parsed_context_length <= 0:
            raise ValueError("OLLAMA_CONTEXT_LENGTH must be a positive integer")
        kwargs["num_ctx"] = parsed_context_length
    if host:
        kwargs["base_url"] = host
    return ChatOllama(**kwargs)


def expected_log_path(
    experiment_dir: Path,
    model: dict[str, str],
    condition: str,
    case_path: Path,
) -> Path:
    domain = case_path.parent.name
    case_id = case_path.stem
    safe_model = model["ollama"].replace(":", "_").replace("/", "_")
    return (
        experiment_dir
        / "agents"
        / model["safe"]
        / condition
        / domain
        / case_id
        / "tool-only"
        / condition
        / f"{case_id}_{safe_model}.txt"
    )


def result_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        record["model"],
        record["condition"],
        record["domain"],
        record["case_id"],
    )


def load_completed_results(
    path: Path,
) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    completed: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    if not path.is_file():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("execution_status") in VALID_STATUSES:
            completed[result_key(record)] = record
    return completed


def evaluate_with_retry(
    *,
    execution_log: str,
    case: dict[str, Any],
    judge: Any,
    max_retries: int,
) -> tuple[bool, str, str]:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return evaluate_utility_completion(
                execution_log,
                case,
                mode="api",
                eval_model=judge,
                eval_processor=None,
                verbose=False,
            )
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < max_retries:
                time.sleep(min(5, attempt))
    assert last_error is not None
    raise last_error


def format_rate(count: int, total: int) -> str:
    return f"{100.0 * count / total:.1f}% ({count}/{total})"


def format_delta(value: float) -> str:
    if abs(value) < 0.05:
        return "0.0 pp"
    sign = "+" if value > 0 else "−"
    return f"{sign}{abs(value):.1f} pp"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def aggregate(
    records: list[dict[str, Any]],
    *,
    expected_per_condition: int,
) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    for model in MODEL_SPECS:
        model_group: dict[str, Any] = {}
        for condition in CONDITIONS:
            selected = [
                record
                for record in records
                if record["model"] == model["display"]
                and record["condition"] == condition
            ]
            counts = Counter(record["execution_status"] for record in selected)
            completed = counts["completed"]
            model_group[condition] = {
                "total_expected": expected_per_condition,
                "total_evaluated": len(selected),
                "counts": {
                    status: counts[status]
                    for status in (
                        "completed",
                        "overrejected",
                        "task_failed",
                        "execution_failed",
                        "evaluation_error",
                        "missing",
                    )
                },
                "task_success_rate_pct": round(
                    100.0 * completed / expected_per_condition,
                    4,
                ),
                "overrejection_rate_pct": round(
                    100.0 * counts["overrejected"] / expected_per_condition,
                    4,
                ),
            }
        model_group["utility_change_pp"] = round(
            model_group["safety"]["task_success_rate_pct"]
            - model_group["original"]["task_success_rate_pct"],
            4,
        )
        groups[model["display"]] = model_group
    return groups


def render_summary_markdown(
    summary: dict[str, Any],
    *,
    expected_per_condition: int,
) -> str:
    lines = [
        "# LPS-Bench-derived utility experiment",
        "",
        f"Judge model: `{summary['judge_model']}`",
        "",
        "| Model | Original Prompt | Safety Prompt | Utility Change | Original ORR | Safety ORR |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model in MODEL_SPECS:
        group = summary["models"][model["display"]]
        original = group["original"]["counts"]
        safety = group["safety"]["counts"]
        lines.append(
            "| "
            + model["display"]
            + " | "
            + format_rate(original["completed"], expected_per_condition)
            + " | "
            + format_rate(safety["completed"], expected_per_condition)
            + " | "
            + format_delta(group["utility_change_pp"])
            + " | "
            + format_rate(original["overrejected"], expected_per_condition)
            + " | "
            + format_rate(safety["overrejected"], expected_per_condition)
            + " |"
        )
    lines.extend(
        [
            "",
            "Utility Change is `TSR_safety − TSR_original` in percentage points.",
            "",
        ]
    )
    return "\n".join(lines)


def update_rebuttal_table(
    markdown_path: Path,
    summary: dict[str, Any],
    *,
    expected_per_condition: int,
) -> None:
    text = markdown_path.read_text(encoding="utf-8")
    q3_start = text.find("> **Q3:")
    q4_start = text.find("> **Q4:", q3_start + 1)
    if q3_start < 0 or q4_start < 0:
        raise ValueError("Could not isolate the Q3 rebuttal section")

    q3 = text[q3_start:q4_start]
    table_start = q3.find("| Evaluation | Model |")
    if table_start < 0:
        raise ValueError("Could not find the Q3 utility table header")
    table_end = q3.find("\n\n", table_start)
    if table_end < 0:
        raise ValueError("Could not find the end of the Q3 utility table")

    table = q3[table_start:table_end]
    table_lines = table.splitlines()
    claws_rows = [
        row_index
        for row_index, line in enumerate(table_lines)
        if re.match(r"^\|\s*ClawsBench\s*\|", line)
    ]
    if len(claws_rows) != 1:
        raise ValueError("Could not uniquely locate the ClawsBench table boundary")
    lps_row_end = claws_rows[0]
    for index, model in enumerate(MODEL_SPECS):
        group = summary["models"][model["display"]]
        original_count = group["original"]["counts"]["completed"]
        safety_count = group["safety"]["counts"]["completed"]
        prefix = "LPS-Bench-derived utility cases" if index == 0 else ""
        replacement = (
            f"| {prefix} | {model['display']} | "
            f"{format_rate(original_count, expected_per_condition)} | "
            f"{format_rate(safety_count, expected_per_condition)} | "
            f"{format_delta(group['utility_change_pp'])} |"
        )
        matching_rows = [
            row_index
            for row_index, line in enumerate(table_lines[:lps_row_end])
            if re.match(
                r"^\|\s*(?:LPS-Bench-derived utility cases)?\s*\|\s*"
                + re.escape(model["display"])
                + r"\s*\|",
                line,
            )
        ]
        if len(matching_rows) != 1:
            raise ValueError(
                f"Could not uniquely update the rebuttal row for {model['display']}"
            )
        table_lines[matching_rows[0]] = replacement

    updated_table = "\n".join(table_lines)
    updated_q3 = q3[:table_start] + updated_table + q3[table_end:]
    updated_text = text[:q3_start] + updated_q3 + text[q4_start:]
    temporary_path = markdown_path.with_name(
        f".{markdown_path.name}.{os.getpid()}.tmp"
    )
    try:
        temporary_path.write_text(updated_text, encoding="utf-8")
        os.replace(temporary_path, markdown_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> None:
    args = parse_args()
    experiment_dir = args.experiment_dir.resolve()
    evaluation_dir = experiment_dir / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    results_path = evaluation_dir / "utility_judgments.jsonl"

    case_paths = sorted(CASE_ROOT.glob("*/*.json"))
    if len(case_paths) != 56:
        raise SystemExit(f"Expected 56 utility cases, found {len(case_paths)}")

    cached = load_completed_results(results_path)
    judge = create_judge(args.judge_model)
    expected_total = len(case_paths) * len(MODEL_SPECS) * len(CONDITIONS)
    progress = len(cached)

    with results_path.open("a", encoding="utf-8") as output:
        for model in MODEL_SPECS:
            for condition in CONDITIONS:
                for case_path in case_paths:
                    key = (
                        model["display"],
                        condition,
                        case_path.parent.name,
                        case_path.stem,
                    )
                    if key in cached:
                        continue

                    progress += 1
                    log_path = expected_log_path(
                        experiment_dir,
                        model,
                        condition,
                        case_path,
                    )
                    record: dict[str, Any] = {
                        "model": model["display"],
                        "ollama_model": model["ollama"],
                        "condition": condition,
                        "case_id": case_path.stem,
                        "domain": case_path.parent.name,
                        "case_file": str(case_path.relative_to(REPO_ROOT)),
                        "log_file": str(log_path.relative_to(REPO_ROOT)),
                        "judge_model": args.judge_model,
                    }
                    if not log_path.is_file():
                        record.update(
                            {
                                "pass": False,
                                "execution_status": "missing",
                                "reasoning": "Expected execution log was not found.",
                            }
                        )
                    else:
                        case = json.loads(case_path.read_text(encoding="utf-8"))
                        execution_log = log_path.read_text(encoding="utf-8")
                        try:
                            passed, reasoning, status = evaluate_with_retry(
                                execution_log=execution_log,
                                case=case,
                                judge=judge,
                                max_retries=args.max_retries,
                            )
                            record.update(
                                {
                                    "pass": passed,
                                    "execution_status": status,
                                    "reasoning": reasoning,
                                }
                            )
                        except Exception as exc:  # noqa: BLE001
                            record.update(
                                {
                                    "pass": False,
                                    "execution_status": "evaluation_error",
                                    "reasoning": str(exc),
                                }
                            )

                    output.write(json.dumps(record, ensure_ascii=False) + "\n")
                    output.flush()
                    cached[key] = record
                    print(
                        f"[{progress}/{expected_total}] {model['display']} "
                        f"{condition} {case_path.parent.name}/{case_path.stem}: "
                        f"{record['execution_status']}",
                        flush=True,
                    )

    records = list(cached.values())
    groups = aggregate(records, expected_per_condition=len(case_paths))
    summary = {
        "experiment_dir": display_path(experiment_dir),
        "judge_model": args.judge_model,
        "case_count": len(case_paths),
        "expected_trajectory_count": expected_total,
        "models": groups,
    }
    summary_path = evaluation_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    summary_markdown = render_summary_markdown(
        summary,
        expected_per_condition=len(case_paths),
    )
    (evaluation_dir / "summary.md").write_text(
        summary_markdown,
        encoding="utf-8",
    )

    incomplete: list[str] = []
    for model in MODEL_SPECS:
        for condition in CONDITIONS:
            group = groups[model["display"]][condition]
            if group["total_evaluated"] != len(case_paths):
                incomplete.append(f"{model['display']}:{condition}:count")
            if (
                group["counts"]["missing"]
                or group["counts"]["evaluation_error"]
            ):
                incomplete.append(f"{model['display']}:{condition}:errors")
    if incomplete:
        raise SystemExit(
            "Evaluation is incomplete; rebuttal table was not updated: "
            + ", ".join(incomplete)
        )

    if args.update_markdown is not None:
        update_rebuttal_table(
            args.update_markdown,
            summary,
            expected_per_condition=len(case_paths),
        )
        print(f"Updated rebuttal table: {args.update_markdown}")

    print(summary_markdown)


if __name__ == "__main__":
    main()
