#!/usr/bin/env python3
"""Build paired original/skill case lists for skill-extension experiments."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

RISKS = ("FA", "OC", "TS", "PI")
PAIRED_ID_RE = re.compile(r"^(?P<domain>.+)_(?P<risk>FA|OC|TS|PI)_(?P<idx>\d+)$")
SKILL_FILE_RE = re.compile(r"^(?P<risk>FA|OC|TS|PI)_skill_(?P<idx>\d+)\.json$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples-dir", type=Path, default=Path("examples"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--max-per-risk",
        type=int,
        default=10,
        help="Maximum skill cases per risk subset. Use 0 to keep all discovered cases.",
    )
    return parser.parse_args()


def paired_case_path(examples_dir: Path, paired_case_id: str) -> Path:
    match = PAIRED_ID_RE.match(paired_case_id)
    if not match:
        raise ValueError(f"Unsupported paired_case_id format: {paired_case_id}")
    domain = match.group("domain")
    risk = match.group("risk")
    idx = match.group("idx")
    return examples_dir / domain / f"{risk}_{idx}.json"


def skill_sort_key(path: Path) -> Tuple[str, int, str]:
    match = SKILL_FILE_RE.match(path.name)
    if not match:
        return path.name, 0, str(path)
    return match.group("risk"), int(match.group("idx")), str(path)


def discover_skill_cases(examples_dir: Path) -> Dict[str, List[Tuple[Path, Path]]]:
    by_risk: Dict[str, List[Tuple[Path, Path]]] = {risk: [] for risk in RISKS}
    for skill_path in sorted(examples_dir.glob("**/*_skill_*.json"), key=skill_sort_key):
        risk = skill_path.name.split("_", 1)[0]
        if risk not in by_risk:
            continue

        case_data = json.loads(skill_path.read_text(encoding="utf-8"))
        paired_case_id = case_data.get("meta", {}).get("paired_case_id")
        if not paired_case_id:
            raise ValueError(f"{skill_path} has no meta.paired_case_id")

        original_path = paired_case_path(examples_dir, paired_case_id)
        if not original_path.exists():
            raise FileNotFoundError(f"Paired original case not found for {skill_path}: {original_path}")

        by_risk[risk].append((skill_path, original_path))

    return by_risk


def write_list(path: Path, items: Iterable[Path]) -> None:
    path.write_text("\n".join(str(item) for item in items) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    by_risk = discover_skill_cases(args.examples_dir)
    max_per_risk = args.max_per_risk if args.max_per_risk > 0 else None

    for risk in RISKS:
        pairs = by_risk[risk]
        if max_per_risk is not None:
            pairs = pairs[:max_per_risk]

        skill_cases = [skill for skill, _ in pairs]
        original_cases = [original for _, original in pairs]

        write_list(args.output_dir / f"{risk}_skill.txt", skill_cases)
        write_list(args.output_dir / f"{risk}_original.txt", original_cases)
        print(f"{risk}: {len(pairs)} pairs")
        if len(by_risk[risk]) != len(pairs):
            print(f"  selected first {len(pairs)} of {len(by_risk[risk])} discovered skill cases")


if __name__ == "__main__":
    main()
