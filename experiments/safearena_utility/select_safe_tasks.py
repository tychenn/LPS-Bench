#!/usr/bin/env python3
"""Create a deterministic, site-stratified subset of SafeArena safe tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SITE_MARKERS = (
    ("shopping_admin", "__SHOPPING_ADMIN__"),
    ("shopping", "__SHOPPING__"),
    ("reddit", "__REDDIT__"),
    ("gitlab", "__GITLAB__"),
)


def infer_site(config: dict[str, Any]) -> str:
    sites = config.get("sites")
    if isinstance(sites, list) and sites:
        return "+".join(sorted(str(site) for site in sites))
    serialized = json.dumps(config, sort_keys=True)
    matched = [name for name, marker in SITE_MARKERS if marker in serialized]
    if not matched:
        raise ValueError(f"Could not infer site for task {config.get('task_id')}")
    return "+".join(matched)


def allocate_counts(group_sizes: dict[str, int], count: int) -> dict[str, int]:
    if count < len(group_sizes):
        raise ValueError(
            f"Requested {count} tasks but found {len(group_sizes)} site groups; "
            "at least one task per group is required"
        )
    total = sum(group_sizes.values())
    if count > total:
        raise ValueError(f"Requested {count} tasks but the safe split only has {total}")

    allocations = {site: 1 for site in group_sizes}
    remaining = count - len(group_sizes)
    ideals = {
        site: remaining * size / total
        for site, size in group_sizes.items()
    }
    for site in sorted(group_sizes):
        extra = min(group_sizes[site] - 1, int(ideals[site]))
        allocations[site] += extra

    while sum(allocations.values()) < count:
        candidates = [
            site
            for site in group_sizes
            if allocations[site] < group_sizes[site]
        ]
        site = max(
            candidates,
            key=lambda item: (
                ideals[item] - (allocations[item] - 1),
                group_sizes[item],
                item,
            ),
        )
        allocations[site] += 1
    return allocations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--safe-json", type=Path, required=True)
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260728)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configs = json.loads(args.safe_json.read_text(encoding="utf-8"))
    if not isinstance(configs, list) or not configs:
        raise ValueError("SafeArena safe.json must contain a non-empty list")

    by_site: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[str] = set()
    for config in configs:
        task_id = config.get("task_id")
        key = str(task_id)
        if task_id is None or key in seen:
            raise ValueError(f"Missing or duplicate task_id: {task_id}")
        seen.add(key)
        by_site[infer_site(config)].append(config)

    allocations = allocate_counts(
        {site: len(items) for site, items in by_site.items()},
        args.count,
    )
    rng = random.Random(args.seed)
    selected: list[tuple[str, Any]] = []
    for site in sorted(by_site):
        candidates = sorted(by_site[site], key=lambda item: str(item["task_id"]))
        rng.shuffle(candidates)
        selected.extend(
            (site, item["task_id"])
            for item in candidates[: allocations[site]]
        )
    selected.sort(key=lambda item: (item[0], str(item[1])))

    output = {
        "benchmark": "SafeArena",
        "split": "safe",
        "source": "McGill-NLP/safearena",
        "source_json": str(args.safe_json.resolve()),
        "source_json_sha256": hashlib.sha256(args.safe_json.read_bytes()).hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "selection": {
            "method": "deterministic proportional stratification by site",
            "seed": args.seed,
            "requested_count": args.count,
            "source_group_sizes": {
                site: len(by_site[site])
                for site in sorted(by_site)
            },
            "selected_group_sizes": {
                site: allocations[site]
                for site in sorted(allocations)
            },
        },
        "task_ids": [task_id for _, task_id in selected],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(selected)} SafeArena safe tasks to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
