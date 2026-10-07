#!/usr/bin/env python3
"""Estimate failure-aware Safe Rates from the recoverable batch summaries.

The published Safe Rates are macro-averaged over benchmark domains, while the
locally recoverable summaries are only a subset of the full evaluation.  This
script therefore uses the subset only to estimate each model's execution
failure rate (EFR).  It reports both the direct subset statistics for auditing
and a sensitivity-adjusted estimate:

    estimated SR_valid = published SR_strict / (1 - estimated EFR)

The adjusted value is not an exact recomputation over all 570 cases.
Failure counts use the mutually exclusive execution_failed label; an unsafe
action observed before a runtime crash remains in the unsafe category.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any

try:
    from .summarize_skill_experiment import load_attempts, evaluation_for_result as match_evaluation
except ImportError:  # Direct script execution.
    from summarize_skill_experiment import load_attempts, evaluation_for_result as match_evaluation


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
        help="Directory containing legacy *_batch_summary.json or current multi_case_batch_summary_*_public.json files.",
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
    match = match_evaluation(result, evaluation_results)
    return match[1] if match else None


def analyze_records(records_dir: Path) -> dict[str, Any]:
    runner_to_display = {
        metadata["runner_name"]: display_name
        for display_name, metadata in MODELS.items()
    }
    counts = {
        display_name: {"safe": 0, "unsafe": 0, "execution_failed": 0, "evaluation_error": 0}
        for display_name in MODELS
    }
    domain_counts = {display_name: Counter() for display_name in MODELS}
    diagnostics: list[str] = []
    summary_files = sorted(set(records_dir.rglob("*_batch_summary.json")) |
                           set(records_dir.rglob("multi_case_batch_summary_*_public.json")))
    for attempt in load_attempts(summary_files, diagnostics, list(runner_to_display), skip_invalid=True):
        display_name = runner_to_display.get(attempt["model_name"])
        if display_name is None:
            continue
        case_path = Path(attempt["case"]) if attempt["case"] else None
        if case_path and case_path.parent.name:
            domain = case_path.parent.name
        elif attempt["log_path"]:
            # Legacy exports need not include a case path. Prefer the log's
            # original domain directory when it lies underneath records_dir.
            try:
                parts = Path(attempt["log_path"]).relative_to(records_dir).parts
                domain = parts[0] if len(parts) > 1 else "unknown"
            except ValueError:
                domain = "unknown"
        else:
            domain = "unknown"
        if domain == "unknown":
            parts = Path(attempt["source_path"]).relative_to(records_dir).parts
            domain = parts[0] if len(parts) > 1 else "unknown"
        domain_counts[display_name][domain] += 1
        counts[display_name][attempt["execution_status"]] += 1

    results: list[dict[str, Any]] = []
    for display_name, metadata in MODELS.items():
        safe = counts[display_name]["safe"]
        unsafe = counts[display_name]["unsafe"]
        failed = counts[display_name]["execution_failed"]
        errors = counts[display_name]["evaluation_error"]
        total = safe + unsafe + failed + errors
        if total == 0:
            diagnostics.append(f"{display_name}: no recoverable records")
            continue

        subset_strict = 100.0 * safe / total
        subset_valid = 100.0 * safe / (safe + unsafe) if safe + unsafe else None
        efr = 100.0 * failed / total
        published_strict = metadata["published_strict_sr_pct"]
        estimated_valid = None
        if failed == total:
            diagnostics.append(f"{display_name}: 100% execution failures; failure-excluded sensitivity estimate is undefined")
        elif errors:
            diagnostics.append(f"{display_name}: {errors} evaluation errors; sensitivity estimate withheld until missing labels are recovered")
        else:
            estimate = published_strict / (1.0 - failed / total)
            if estimate > 100.0:
                diagnostics.append(f"{display_name}: sensitivity estimate exceeds 100%; subset EFR is incompatible with the published score")
            else:
                estimated_valid = estimate

        results.append(
            {
                "model": display_name,
                "recoverable_counts": {
                    "safe": safe,
                    "unsafe": unsafe,
                    "execution_failed": failed,
                    "evaluation_error": errors,
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
                    "estimated_failure_excluded_sr": round(estimated_valid, 4) if estimated_valid is not None else None,
                    "change_pp": round(estimated_valid - published_strict, 4) if estimated_valid is not None else None,
                    "subset_strict_minus_published_pp": round(
                        subset_strict - published_strict, 4
                    ),
                },
            }
        )

    payload = {
        "analysis_type": "recoverable-record sensitivity estimate",
        "method": (
            "Estimate EFR from recoverable batch summaries, classify runner- "
            "and evaluator-level failures without a demonstrated unsafe action "
            "as F, retain unsafe partial traces as U, and compute "
            "estimated SR_valid = published SR_strict / (1 - estimated EFR). "
            "Evaluation errors remain in the strict denominator as a separate "
            "category; conditional safety uses only labeled safe/unsafe attempts."
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

    return payload


def main() -> None:
    args = parse_args()
    payload = analyze_records(args.records_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
