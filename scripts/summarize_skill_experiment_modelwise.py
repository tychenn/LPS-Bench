#!/usr/bin/env python3
"""Summarize skill-extension experiments into the model-wise LaTeX table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

try:
    from .summarize_skill_experiment import (
        Counts, difference, fmt, load_attempts, score,
        result_model_name as infer_model_name, safe_model_name, summary_path,
    )
except ImportError:  # Direct script execution.
    from summarize_skill_experiment import (
        Counts, difference, fmt, load_attempts, score,
        result_model_name as infer_model_name, safe_model_name, summary_path,
    )

RISKS = ("FA", "OC", "TS", "PI")

DEFAULT_MODELS: Tuple[Tuple[str, str], ...] = (
    ("GPT-5.1", "gpt-5.1-chat-2025-11-13"),
    ("Gemini-3-Pro", "gemini-3-pro-preview"),
    ("Claude-4.5-Sonnet", "claude-sonnet-4-5-20250929"),
    ("DeepSeek-v3.2", "deepseek-v3.2"),
    ("Llama-3.1-70B-Instruct", "llama3.1:70b"),
    ("Qwen3-32B-Instruct", "qwen3:32b"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--original-root",
        type=Path,
        action="append",
        required=True,
        help="Root containing risk subdirectories for original runs. May be supplied multiple times.",
    )
    parser.add_argument(
        "--skill-root",
        type=Path,
        action="append",
        required=True,
        help="Root containing risk subdirectories for skill runs. May be supplied multiple times.",
    )
    parser.add_argument("--original-mode", default="tool-only")
    parser.add_argument("--skill-mode", default="skill-only")
    parser.add_argument("--system-prompt-mode", choices=["original", "hitl", "safety"], default="original")
    parser.add_argument(
        "--metric",
        choices=["strict", "behavioral"],
        default="strict",
        help=(
            "strict counts execution_failed/evaluation errors as not safe. "
            "behavioral excludes execution_failed/evaluation errors from the denominator."
        ),
    )
    parser.add_argument(
        "--model",
        action="append",
        metavar="LABEL=RAW_NAME",
        help="Model row mapping. Can be supplied multiple times. Defaults to the paper table models.",
    )
    return parser.parse_args()


def parse_models(values: List[str] | None) -> List[Tuple[str, str]]:
    if not values:
        return list(DEFAULT_MODELS)
    parsed: List[Tuple[str, str]] = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"--model must be LABEL=RAW_NAME, got {value!r}")
        label, raw = value.split("=", 1)
        parsed.append((label.strip(), raw.strip()))
    return parsed


def result_model_name(result_key: str, result: Dict) -> str:
    return infer_model_name(result_key, result, [raw for _, raw in DEFAULT_MODELS])


def load_counts_by_model(path: Path, model_names: Iterable[str] = ()) -> Dict[str, Counts]:
    if not path.exists():
        raise FileNotFoundError(path)

    return merge_counts_by_model([path], model_names)


def merge_counts_by_model(paths: Iterable[Path], model_names: Iterable[str] = ()) -> Dict[str, Counts]:
    merged: Dict[str, Counts] = {}
    names = list(dict.fromkeys([*model_names, *(raw for _, raw in DEFAULT_MODELS)]))
    diagnostics: List[str] = []
    existing = [path for path in paths if path.exists()]
    for attempt in load_attempts(existing, diagnostics, names):
        merged.setdefault(attempt["model_name"], Counts()).add_status(attempt["execution_status"])
    for note in diagnostics:
        print(note, file=sys.stderr)
    return merged


def safe_rate(counts: Counts, metric: str) -> float | None:
    return score(counts, metric)


def main() -> None:
    args = parse_args()
    models = parse_models(args.model)

    original: Dict[str, Dict[str, Counts]] = {}
    skill: Dict[str, Dict[str, Counts]] = {}
    for risk in RISKS:
        original[risk] = merge_counts_by_model(
            (summary_path(root, risk, args.original_mode, args.system_prompt_mode) for root in args.original_root),
            [raw for _, raw in models],
        )
        skill[risk] = merge_counts_by_model(
            (summary_path(root, risk, args.skill_mode, args.system_prompt_mode) for root in args.skill_root),
            [raw for _, raw in models],
        )

    print(f"Metric: {args.metric} Safe Rate")
    print(
        f"{'Model':<28} {'Orig Avg':>8} {'Skill Avg':>9} "
        f"{'FA d':>8} {'OC d':>8} {'TS d':>8} {'PI d':>8}"
    )
    print("\nLaTeX rows:")

    for label, raw_name in models:
        orig_srs: List[float | None] = []
        skill_srs: List[float | None] = []
        deltas: Dict[str, float | None] = {}
        missing: List[str] = []

        for risk in RISKS:
            orig_counts = original[risk].get(raw_name)
            skill_counts = skill[risk].get(raw_name)
            orig_sr = safe_rate(orig_counts, args.metric) if orig_counts else None
            skill_sr = safe_rate(skill_counts, args.metric) if skill_counts else None
            if orig_sr is None or skill_sr is None:
                missing.append(risk)
            for condition, counts in (("original", orig_counts), ("skill", skill_counts)):
                if counts and (counts.failed or counts.errors):
                    print(f"{label} {risk} {condition}: {counts.failed} execution failures; {counts.errors} evaluation errors", file=sys.stderr)
            orig_srs.append(orig_sr)
            skill_srs.append(skill_sr)
            deltas[risk] = difference(skill_sr, orig_sr)

        orig_avg = sum(orig_srs) / len(orig_srs) if all(value is not None for value in orig_srs) else None
        skill_avg = sum(skill_srs) / len(skill_srs) if all(value is not None for value in skill_srs) else None
        row = (
            f"{label} & {fmt(orig_avg)} & {fmt(skill_avg)} & "
            f"{fmt(deltas['FA'])} & {fmt(deltas['OC'])} & {fmt(deltas['TS'])} & {fmt(deltas['PI'])} \\\\"
        )
        if missing:
            row += f" % missing: {', '.join(missing)}"

        print(
            f"{label:<28} {fmt(orig_avg):>8} {fmt(skill_avg):>9} "
            f"{fmt(deltas['FA']):>8} {fmt(deltas['OC']):>8} "
            f"{fmt(deltas['TS']):>8} {fmt(deltas['PI']):>8}"
        )
        print(row)


if __name__ == "__main__":
    main()
