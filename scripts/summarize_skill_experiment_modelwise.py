#!/usr/bin/env python3
"""Summarize skill-extension experiments into the model-wise LaTeX table."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

RISKS = ("FA", "OC", "TS", "PI")

DEFAULT_MODELS: Tuple[Tuple[str, str], ...] = (
    ("GPT-5.1", "gpt-5.1-chat-2025-11-13"),
    ("Gemini-3-Pro", "gemini-3-pro-preview"),
    ("Claude-4.5-Sonnet", "claude-sonnet-4-5-20250929"),
    ("DeepSeek-v3.2", "deepseek-v3.2"),
    ("Llama-3.1-70B-Instruct", "llama3.1:70b"),
    ("Qwen3-32B-Instruct", "qwen3:32b"),
)


@dataclass
class Counts:
    safe: int = 0
    unsafe: int = 0
    failed: int = 0
    errors: int = 0

    @property
    def total(self) -> int:
        return self.safe + self.unsafe + self.failed + self.errors

    def add_status(self, status: str) -> None:
        if status == "safe":
            self.safe += 1
        elif status == "unsafe":
            self.unsafe += 1
        elif status == "execution_failed":
            self.failed += 1
        else:
            self.errors += 1


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


def summary_path(root: Path, risk: str, mode: str) -> Path:
    return root / risk / f"multi_case_batch_summary_{mode}_public.json"


def result_model_name(result_key: str, result: Dict) -> str:
    # The evaluator result key is usually "<case>_<model>", and the agent result
    # stores the model name explicitly. Prefer explicit metadata when available.
    model_name = result.get("model_name")
    if isinstance(model_name, str):
        return model_name

    file_path = result.get("file")
    if isinstance(file_path, str):
        stem = Path(file_path).stem
        for _, raw in DEFAULT_MODELS:
            if stem.endswith(raw):
                return raw

    for _, raw in DEFAULT_MODELS:
        if result_key.endswith(raw) or result_key.endswith(safe_model_name(raw)):
            return raw
    return result_key


def safe_model_name(model_name: str) -> str:
    return model_name.replace(":", "_").replace("/", "_")


def load_counts_by_model(path: Path) -> Dict[str, Counts]:
    if not path.exists():
        raise FileNotFoundError(path)

    data = json.loads(path.read_text(encoding="utf-8"))
    counts: Dict[str, Counts] = {}

    for case_result in data.get("results", []):
        # Account for model execution failures that never reached evaluation.
        for run in case_result.get("results", []):
            model_name = run.get("model_name")
            if not model_name:
                continue
            counts.setdefault(model_name, Counts())
            if not run.get("success"):
                counts[model_name].add_status("error")

        evaluation = case_result.get("evaluation") or {}
        if evaluation.get("status") != "success":
            continue

        for key, eval_result in evaluation.get("results", {}).items():
            file_path = eval_result.get("file")
            matched_model = None
            if isinstance(file_path, str):
                stem = Path(file_path).stem
                for model_name in counts:
                    if stem.endswith(model_name) or stem.endswith(safe_model_name(model_name)):
                        matched_model = model_name
                        break
            model_name = matched_model or result_model_name(key, eval_result)
            counts.setdefault(model_name, Counts()).add_status(eval_result.get("execution_status", "error"))

    return counts


def merge_counts_by_model(paths: Iterable[Path]) -> Dict[str, Counts]:
    merged: Dict[str, Counts] = {}
    for path in paths:
        if not path.exists():
            continue
        for model_name, counts in load_counts_by_model(path).items():
            target = merged.setdefault(model_name, Counts())
            target.safe += counts.safe
            target.unsafe += counts.unsafe
            target.failed += counts.failed
            target.errors += counts.errors
    return merged


def safe_rate(counts: Counts, metric: str) -> float:
    if metric == "strict":
        denom = counts.total
    else:
        denom = counts.safe + counts.unsafe
    return 100.0 * counts.safe / denom if denom else 0.0


def fmt(value: float) -> str:
    return f"{value:.1f}"


def main() -> None:
    args = parse_args()
    models = parse_models(args.model)

    original: Dict[str, Dict[str, Counts]] = {}
    skill: Dict[str, Dict[str, Counts]] = {}
    for risk in RISKS:
        original[risk] = merge_counts_by_model(
            summary_path(root, risk, args.original_mode) for root in args.original_root
        )
        skill[risk] = merge_counts_by_model(
            summary_path(root, risk, args.skill_mode) for root in args.skill_root
        )

    print(f"Metric: {args.metric} Safe Rate")
    print(
        f"{'Model':<28} {'Orig Avg':>8} {'Skill Avg':>9} "
        f"{'FA d':>8} {'OC d':>8} {'TS d':>8} {'PI d':>8}"
    )
    print("\nLaTeX rows:")

    for label, raw_name in models:
        orig_srs: List[float] = []
        skill_srs: List[float] = []
        deltas: Dict[str, float] = {}
        missing: List[str] = []

        for risk in RISKS:
            orig_counts = original[risk].get(raw_name)
            skill_counts = skill[risk].get(raw_name)
            if orig_counts is None or skill_counts is None or orig_counts.total == 0 or skill_counts.total == 0:
                missing.append(risk)
                orig_sr = 0.0
                skill_sr = 0.0
            else:
                orig_sr = safe_rate(orig_counts, args.metric)
                skill_sr = safe_rate(skill_counts, args.metric)
            orig_srs.append(orig_sr)
            skill_srs.append(skill_sr)
            deltas[risk] = skill_sr - orig_sr

        orig_avg = sum(orig_srs) / len(orig_srs)
        skill_avg = sum(skill_srs) / len(skill_srs)
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
