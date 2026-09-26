#!/usr/bin/env python3
"""Estimate failure-aware Safe Rates from the recoverable batch summaries.

The published Safe Rates are macro-averaged over benchmark domains, while the
locally recoverable summaries are only a subset of the full evaluation.  This
script therefore uses the subset only to estimate each model's execution
failure rate (EFR).  It reports both the direct subset statistics for auditing
and a sensitivity-adjusted estimate:

    estimated SR_valid = published SR_strict / (1 - estimated EFR)

The adjusted value is not an exact recomputation over all 570 cases.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any


MODELS = OrderedDict(
    [
        (
            "Llama-3.1-8B-Instruct",
            {"runner_name": "llama3.1:8b", "published_strict_sr_pct": 8.07},
        ),
        (
            "Llama-3.1-70B-Instruct",
            {"runner_name": "llama3.1:70b", "published_strict_sr_pct": 9.67},
        ),
        (
            "Qwen3-8B-Instruct",
            {"runner_name": "qwen3:8b", "published_strict_sr_pct": 5.90},
        ),
        (
            "Qwen3-32B-Instruct",
            {"runner_name": "qwen3:32b", "published_strict_sr_pct": 6.46},
        ),
    ]
)

VALID_LABELS = {"safe", "unsafe", "execution_failed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--records-dir",
        type=Path,
        default=Path("records"),
        help="Directory containing *_batch_summary.json files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tmp/5QNC_q1_sensitivity_results.json"),
        help="Path for the machine-readable result.",
    )
    return parser.parse_args()


def evaluation_for_result(
    result: dict[str, Any], evaluation_results: dict[str, Any]
) -> dict[str, Any] | None:
    """Match a successful runner result to its evaluator record."""
    log_path = result.get("log_path")
    if log_path:
        by_stem = evaluation_results.get(Path(log_path).stem)
        if isinstance(by_stem, dict):
            return by_stem

    for evaluation in evaluation_results.values():
        if not isinstance(evaluation, dict):
            continue
        if log_path and evaluation.get("file") == log_path:
            return evaluation
    return None


def main() -> None:
    args = parse_args()
    runner_to_display = {
        metadata["runner_name"]: display_name
        for display_name, metadata in MODELS.items()
    }
    counts = {
        display_name: {"safe": 0, "unsafe": 0, "execution_failed": 0}
        for display_name in MODELS
    }
    domain_counts = {display_name: Counter() for display_name in MODELS}
    diagnostics: list[str] = []
    summary_files = sorted(args.records_dir.rglob("*_batch_summary.json"))

    for summary_path in summary_files:
        relative_parts = summary_path.relative_to(args.records_dir).parts
        domain = relative_parts[0] if relative_parts else "unknown"
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            diagnostics.append(f"{summary_path}: unreadable summary ({exc})")
            continue

        evaluation_results = (
            summary.get("evaluation", {}).get("results", {})
            if isinstance(summary.get("evaluation"), dict)
            else {}
        )
        if not isinstance(evaluation_results, dict):
            evaluation_results = {}

        for result in summary.get("results", []):
            if not isinstance(result, dict):
                continue
            display_name = runner_to_display.get(result.get("model_name"))
            if display_name is None:
                continue
            domain_counts[display_name][domain] += 1

            # Runner failures and evaluator execution failures are deliberately
            # combined into the single F category used by the paper.
            if result.get("success") is not True:
                counts[display_name]["execution_failed"] += 1
                continue

            evaluation = evaluation_for_result(result, evaluation_results)
            label = (
                evaluation.get("execution_status")
                if isinstance(evaluation, dict)
                else None
            )
            if label not in VALID_LABELS:
                diagnostics.append(
                    f"{summary_path}: missing/invalid evaluator label for "
                    f"{result.get('model_name')}"
                )
                continue
            counts[display_name][label] += 1

    results: list[dict[str, Any]] = []
    for display_name, metadata in MODELS.items():
        safe = counts[display_name]["safe"]
        unsafe = counts[display_name]["unsafe"]
        failed = counts[display_name]["execution_failed"]
        total = safe + unsafe + failed
        if total == 0:
            diagnostics.append(f"{display_name}: no recoverable records")
            continue

        subset_strict = 100.0 * safe / total
        subset_valid = 100.0 * safe / (safe + unsafe) if safe + unsafe else None
        efr = 100.0 * failed / total
        published_strict = metadata["published_strict_sr_pct"]
        estimated_valid = published_strict / (1.0 - failed / total)

        results.append(
            {
                "model": display_name,
                "recoverable_counts": {
                    "safe": safe,
                    "unsafe": unsafe,
                    "execution_failed": failed,
                    "total": total,
                },
                "recoverable_domain_counts": dict(
                    sorted(domain_counts[display_name].items())
                ),
                "recoverable_subset_metrics_pct": {
                    "strict_sr": round(subset_strict, 4),
                    "failure_excluded_sr": (
                        round(subset_valid, 4) if subset_valid is not None else None
                    ),
                    "execution_failure_rate": round(efr, 4),
                },
                "published_and_sensitivity_estimate_pct": {
                    "published_strict_sr": published_strict,
                    "estimated_failure_excluded_sr": round(estimated_valid, 4),
                    "change_pp": round(estimated_valid - published_strict, 4),
                    "subset_strict_minus_published_pp": round(
                        subset_strict - published_strict, 4
                    ),
                },
            }
        )

    payload = {
        "analysis_type": "recoverable-record sensitivity estimate",
        "method": (
            "Estimate EFR from recoverable batch summaries, combine all runner- "
            "and evaluator-level execution failures into F, and compute "
            "estimated SR_valid = published SR_strict / (1 - estimated EFR)."
        ),
        "limitation": (
            "The recoverable summaries are not the complete 570-case evaluation; "
            "the adjusted values are sensitivity estimates, not exact full-corpus "
            "recalculations."
        ),
        "batch_summary_files_scanned": len(summary_files),
        "results": results,
        "diagnostics": diagnostics,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
