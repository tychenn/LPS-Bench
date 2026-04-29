#!/usr/bin/env python3
"""Summarize paired original-vs-skill experiment summaries into SR tables."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

RISKS = ("FA", "OC", "TS", "PI")


@dataclass
class Counts:
    safe: int = 0
    unsafe: int = 0
    failed: int = 0
    errors: int = 0

    @property
    def total(self) -> int:
        return self.safe + self.unsafe + self.failed + self.errors

    @property
    def sr(self) -> float:
        return 100.0 * self.safe / self.total if self.total else 0.0

    def add(self, other: "Counts") -> None:
        self.safe += other.safe
        self.unsafe += other.unsafe
        self.failed += other.failed
        self.errors += other.errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--skill-root", type=Path, required=True)
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
    return parser.parse_args()


def summary_path(root: Path, risk: str, mode: str) -> Path:
    return root / risk / f"multi_case_batch_summary_{mode}_public.json"


def iter_eval_results(summary: Dict) -> Iterable[Dict]:
    for case_result in summary.get("results", []):
        evaluation = case_result.get("evaluation") or {}
        if evaluation.get("status") != "success":
            yield {"execution_status": "error"}
            continue
        results = evaluation.get("results", {})
        if not results:
            yield {"execution_status": "error"}
            continue
        yield from results.values()


def load_counts(path: Path) -> Counts:
    if not path.exists():
        raise FileNotFoundError(path)

    data = json.loads(path.read_text(encoding="utf-8"))
    counts = Counts()
    for result in iter_eval_results(data):
        status = result.get("execution_status")
        if status == "safe":
            counts.safe += 1
        elif status == "unsafe":
            counts.unsafe += 1
        elif status == "execution_failed":
            counts.failed += 1
        else:
            counts.errors += 1
    return counts


def score(counts: Counts, metric: str) -> float:
    if metric == "strict":
        return counts.sr

    denom = counts.safe + counts.unsafe
    return 100.0 * counts.safe / denom if denom else 0.0


def fmt(value: float) -> str:
    return f"{value:.1f}"


def print_table(rows: List[Dict], metric: str) -> None:
    print(f"Metric: {metric} Safe Rate")
    print(f"{'Category':<8} {'Orig SR':>8} {'Skill SR':>9} {'Delta':>8} {'Orig n':>7} {'Skill n':>8}")
    for row in rows:
        print(
            f"{row['risk']:<8} {fmt(row['orig_sr']):>8} {fmt(row['skill_sr']):>9} "
            f"{fmt(row['delta']):>8} {row['orig_counts'].total:>7} {row['skill_counts'].total:>8}"
        )


def print_latex(rows: List[Dict]) -> None:
    print("\nLaTeX rows:")
    for row in rows:
        risk = row["risk"]
        print(f"{risk} & {fmt(row['orig_sr'])} & {fmt(row['skill_sr'])} & {fmt(row['delta'])} \\\\")


def main() -> None:
    args = parse_args()

    rows: List[Dict] = []
    overall_orig = Counts()
    overall_skill = Counts()

    for risk in RISKS:
        orig_counts = load_counts(summary_path(args.original_root, risk, args.original_mode))
        skill_counts = load_counts(summary_path(args.skill_root, risk, args.skill_mode))

        overall_orig.add(orig_counts)
        overall_skill.add(skill_counts)

        orig_sr = score(orig_counts, args.metric)
        skill_sr = score(skill_counts, args.metric)
        rows.append(
            {
                "risk": risk,
                "orig_counts": orig_counts,
                "skill_counts": skill_counts,
                "orig_sr": orig_sr,
                "skill_sr": skill_sr,
                "delta": skill_sr - orig_sr,
            }
        )

    orig_sr = score(overall_orig, args.metric)
    skill_sr = score(overall_skill, args.metric)
    rows.append(
        {
            "risk": "Overall",
            "orig_counts": overall_orig,
            "skill_counts": overall_skill,
            "orig_sr": orig_sr,
            "skill_sr": skill_sr,
            "delta": skill_sr - orig_sr,
        }
    )

    print_table(rows, args.metric)
    print_latex(rows)


if __name__ == "__main__":
    main()
