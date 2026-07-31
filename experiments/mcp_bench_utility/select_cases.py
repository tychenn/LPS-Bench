#!/usr/bin/env python3
"""Freeze an outcome-blind, deployment-feasible MCP-Bench task subset."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ALGORITHM_VERSION = "mcpbench-deployable-coverage-v2"
SEED = "lps-mcpbench-utility-2026-07-31"
STATIC_DEPLOYMENT_EXCLUSIONS = {
    "OSINT Intelligence": (
        "requires undeclared host binaries (whois, dnsrecon, and dnstwist)"
    ),
}
STRATA = (
    ("single", "mcpbench_tasks_single_runner_format.json", 10, 1),
    ("two_server", "mcpbench_tasks_multi_2server_runner_format.json", 6, 2),
    ("three_server", "mcpbench_tasks_multi_3server_runner_format.json", 4, 3),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkout",
        type=Path,
        default=Path("external/mcp-bench"),
        help="Official MCP-Bench checkout.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("experiments/mcp_bench_utility/selected_tasks.json"),
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=Path("experiments/mcp_bench_utility/selected_cases.md"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def flatten_tasks(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        tasks = data
    elif not isinstance(data, dict):
        raise ValueError(f"Unsupported task root: {type(data).__name__}")
    elif "server_tasks" in data:
        tasks = []
        for group in data["server_tasks"]:
            server_name = group.get("server_name", "")
            if "task" in group:
                tasks.append({"server_name": server_name, "task": group["task"]})
            else:
                tasks.extend(
                    {"server_name": server_name, "task": task}
                    for task in group.get("tasks", [])
                )
    elif "tasks" in data:
        tasks = data["tasks"]
    elif "combinations" in data:
        tasks = []
        for combination in data["combinations"]:
            servers = combination.get("servers", [])
            server_name = "+".join(servers)
            for task in combination.get("generated_tasks", []):
                tasks.append({"server_name": server_name, "task": task})
    else:
        raise ValueError("Task file has no recognized task collection")
    if not isinstance(tasks, list):
        raise ValueError("Flattened tasks are not a list")
    return tasks


def required_servers(item: dict[str, Any]) -> tuple[str, ...]:
    value = item.get("server_name", "")
    if isinstance(value, list):
        servers = value
    elif isinstance(value, str):
        servers = value.split("+")
    else:
        raise ValueError(f"Invalid server_name: {value!r}")
    normalized = tuple(server.strip() for server in servers if server.strip())
    if not normalized:
        raise ValueError("Task has no required server")
    return normalized


def task_id(item: dict[str, Any]) -> str:
    task = item.get("task")
    if not isinstance(task, dict):
        raise ValueError("Task entry lacks a task object")
    value = task.get("task_id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Task entry lacks a non-empty task_id")
    return value.strip()


def stable_tie_key(item: dict[str, Any]) -> str:
    material = "\0".join((SEED, task_id(item), *required_servers(item)))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def select_coverage(
    candidates: list[dict[str, Any]],
    quota: int,
    *,
    initial_covered: set[str] | None = None,
    initial_usage: Counter[str] | None = None,
) -> list[dict[str, Any]]:
    remaining = list(candidates)
    selected: list[dict[str, Any]] = []
    covered = set(initial_covered or ())
    usage: Counter[str] = Counter(initial_usage or {})
    while remaining and len(selected) < quota:
        winner = min(
            remaining,
            key=lambda item: (
                -len(set(required_servers(item)) - covered),
                sum(usage[server] for server in required_servers(item)),
                stable_tie_key(item),
            ),
        )
        remaining.remove(winner)
        selected.append(winner)
        servers = required_servers(winner)
        covered.update(servers)
        usage.update(servers)
    if len(selected) != quota:
        raise RuntimeError(
            f"Only {len(selected)} eligible tasks remain for quota {quota}"
        )
    return selected


def upstream_revision(checkout: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=checkout,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout.strip()


def main() -> int:
    args = parse_args()
    checkout = args.checkout.resolve()
    commands_path = checkout / "mcp_servers" / "commands.json"
    if not commands_path.is_file():
        raise SystemExit(f"Missing official commands file: {commands_path}")
    commands = json.loads(commands_path.read_text(encoding="utf-8"))
    if not isinstance(commands, dict):
        raise SystemExit("commands.json must contain an object")
    keyed_servers = {
        name
        for name, config in commands.items()
        if isinstance(config, dict) and config.get("env")
    }
    excluded_servers = keyed_servers | set(STATIC_DEPLOYMENT_EXCLUSIONS)

    selected_all: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    source_files: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    globally_covered: set[str] = set()
    global_usage: Counter[str] = Counter()
    for stratum, filename, quota, expected_server_count in STRATA:
        source_path = checkout / "tasks" / filename
        if not source_path.is_file():
            raise SystemExit(f"Missing official task file: {source_path}")
        source_files.append(
            {
                "path": f"tasks/{filename}",
                "sha256": sha256_file(source_path),
            }
        )
        items = flatten_tasks(json.loads(source_path.read_text(encoding="utf-8")))
        eligible: list[dict[str, Any]] = []
        for item in items:
            identifier = task_id(item)
            servers = required_servers(item)
            if len(servers) != expected_server_count:
                raise SystemExit(
                    f"{identifier}: expected {expected_server_count} required "
                    f"servers, found {servers}"
                )
            if identifier in seen_ids:
                raise SystemExit(f"Duplicate task ID across source files: {identifier}")
            seen_ids.add(identifier)
            if set(servers).isdisjoint(excluded_servers):
                eligible.append(item)
        chosen = select_coverage(
            eligible,
            quota,
            initial_covered=globally_covered,
            initial_usage=global_usage,
        )
        for item in chosen:
            frozen = copy.deepcopy(item)
            frozen_task = frozen.setdefault("task", {})
            # The formal subset does not launch distractor servers. This prevents
            # randomly selected credentialed services from invalidating a task.
            frozen_task["distraction_servers"] = []
            selected_all.append(frozen)
            globally_covered.update(required_servers(frozen))
            global_usage.update(required_servers(frozen))
            manifest_rows.append(
                {
                    "stratum": stratum,
                    "task_id": task_id(frozen),
                    "servers": list(required_servers(frozen)),
                    "source": f"tasks/{filename}",
                }
            )

    revision = upstream_revision(checkout)
    output = {
        "selection_metadata": {
            "algorithm_version": ALGORITHM_VERSION,
            "seed": SEED,
            "upstream_revision": revision,
            "source_files": source_files,
            "credentialed_servers_excluded": sorted(keyed_servers),
            "other_servers_excluded": STATIC_DEPLOYMENT_EXCLUSIONS,
            "quotas": {stratum: quota for stratum, _, quota, _ in STRATA},
            "task_count": len(selected_all),
            "distraction_servers": "disabled",
        },
        "tasks": selected_all,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Frozen MCP-Bench utility cases",
        "",
        f"- Upstream revision: `{revision}`",
        f"- Algorithm: `{ALGORITHM_VERSION}`",
        f"- Seed: `{SEED}`",
        f"- Total: {len(selected_all)} tasks",
        f"- Credentialed servers excluded: {', '.join(sorted(keyed_servers))}",
        "- Other deployment exclusions: "
        + "; ".join(
            f"{name} ({reason})"
            for name, reason in sorted(STATIC_DEPLOYMENT_EXCLUSIONS.items())
        ),
        "- Distractor servers: disabled",
        "",
        "| Stratum | Task ID | Required servers | Source |",
        "|---|---|---|---|",
    ]
    for row in manifest_rows:
        lines.append(
            f"| {row['stratum']} | `{row['task_id']}` | "
            f"{' + '.join(row['servers'])} | `{row['source']}` |"
        )
    lines.extend(["", "## Source file checksums", ""])
    for source in source_files:
        lines.append(f"- `{source['sha256']}  {source['path']}`")
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(selected_all)} tasks to {args.output_json}")
    print(f"Wrote frozen manifest to {args.output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
