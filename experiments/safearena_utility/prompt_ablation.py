#!/usr/bin/env python3
"""Run one SafeArena safe-split model/prompt condition faithfully.

The official SafeArena benchmark, BrowserGym task implementation, AgentLab
GenericAgent, and evaluators are used unchanged. This wrapper only selects a
fixed subset and changes AgentLab's system-prompt text for the safety condition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SAFEARENA_COMMIT = "a146df4013b775b0fbaf9423ea60e697eb97589e"
AGENTLAB_COMMIT = "71ec578c376121af2152fe731bc1dbcbdb7e908a"
CONDITIONS = ("original", "safety")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_effective_system_prompt(
    original_prompt: str,
    safety_prompt: str,
    condition: str,
) -> str:
    """Return the sole prompt intervention used by the experiment."""
    if condition == "original":
        return original_prompt
    if condition != "safety":
        raise ValueError(f"Unsupported prompt condition: {condition}")
    if not safety_prompt.strip():
        raise ValueError("The safety prompt is empty")
    return (
        original_prompt.rstrip()
        + "\n\n"
        + "## Additional safety policy\n"
        + safety_prompt.strip()
        + "\n"
    )


def load_task_manifest(path: Path) -> tuple[list[Any], dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Task manifest must be a JSON object")
    if raw.get("benchmark") != "SafeArena" or raw.get("split") != "safe":
        raise ValueError("Task manifest must identify the SafeArena safe split")
    task_ids = raw.get("task_ids")
    if not isinstance(task_ids, list) or not task_ids:
        raise ValueError("Task manifest must contain a non-empty task_ids list")
    if len({str(task_id) for task_id in task_ids}) != len(task_ids):
        raise ValueError("Task manifest contains duplicate task IDs")
    return task_ids, raw


def checked_commit(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--model", required=True, help="Model ID exposed by the local endpoint")
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--base-url", required=True, help="OpenAI-compatible URL, including /v1")
    parser.add_argument("--api-key", default="ollama")
    parser.add_argument(
        "--safearena-root",
        type=Path,
        default=Path("external/safearena"),
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("external/safearena/data"),
    )
    parser.add_argument(
        "--task-manifest",
        type=Path,
        default=Path("experiments/safearena_utility/safe_tasks_40.json"),
    )
    parser.add_argument(
        "--safety-prompt-file",
        type=Path,
        default=Path("utility_cases/lps_bench_derived/prompts/safety_prompt.txt"),
    )
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--max-total-tokens", type=int, required=True)
    parser.add_argument("--max-new-tokens", type=int, default=1024)
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument("--n-relaunch", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    safearena_root = (repo_root / args.safearena_root).resolve()
    data_dir = (repo_root / args.data_dir).resolve()
    manifest_path = (repo_root / args.task_manifest).resolve()
    safety_prompt_path = (repo_root / args.safety_prompt_file).resolve()
    results_root = (repo_root / args.results_root).resolve()

    if checked_commit(safearena_root) != SAFEARENA_COMMIT:
        raise RuntimeError(
            f"SafeArena checkout is not pinned to required commit {SAFEARENA_COMMIT}"
        )
    if args.max_total_tokens <= args.max_new_tokens:
        raise ValueError("max-total-tokens must exceed max-new-tokens")

    task_ids, task_manifest = load_task_manifest(manifest_path)
    safety_prompt = safety_prompt_path.read_text(encoding="utf-8")

    # SafeArena reads all of these values at import time.
    os.environ["SAFEARENA_TASK"] = "safe"
    os.environ["SAFEARENA_DATA_DIR"] = str(data_dir)
    os.environ["AGENTLAB_EXP_ROOT"] = str(results_root)
    os.environ["VLLM_BASE_URL"] = args.base_url
    os.environ["VLLM_API_KEY"] = args.api_key
    # The Slurm job resets the official containers synchronously before each
    # condition, so SafeArena must not request its HTTP reset server again.
    os.environ["SAFEARENA_DISABLE_FULL_RESET"] = "true"
    sys.path.insert(0, str(safearena_root))

    from agentlab.agents import dynamic_prompting as dp
    from agentlab.experiments.study import Study
    from safearena import create_default_benchmark
    from safearena.config import SAFE_TASK_IDS
    from safearena.modeling import prepare_vllm_model

    official_task_ids = {str(task_id) for task_id in SAFE_TASK_IDS}
    unknown = [task_id for task_id in task_ids if str(task_id) not in official_task_ids]
    if unknown:
        raise ValueError(f"Manifest contains task IDs outside the official safe split: {unknown}")

    original_prompt = dp.SystemPrompt._prompt
    effective_prompt = build_effective_system_prompt(
        original_prompt=original_prompt,
        safety_prompt=safety_prompt,
        condition=args.condition,
    )
    dp.SystemPrompt._prompt = effective_prompt

    invocation_dir = results_root / "invocations"
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": "SafeArena",
        "split": "safe",
        "safearena_commit": SAFEARENA_COMMIT,
        "agentlab_commit": AGENTLAB_COMMIT,
        "condition": args.condition,
        "model": args.model,
        "model_label": args.model_label,
        "base_url": args.base_url,
        "task_manifest": str(manifest_path),
        "task_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "task_count": len(task_ids),
        "task_ids": task_ids,
        "selection": task_manifest.get("selection"),
        "official_system_prompt_sha256": sha256_text(original_prompt),
        "safety_prompt_sha256": sha256_text(safety_prompt),
        "effective_system_prompt_sha256": sha256_text(effective_prompt),
        "effective_system_prompt": effective_prompt,
        "max_total_tokens": args.max_total_tokens,
        "max_new_tokens": args.max_new_tokens,
        "max_prompt_tokens": args.max_total_tokens - args.max_new_tokens,
        "use_vision": False,
        "n_jobs": args.n_jobs,
        "n_relaunch": args.n_relaunch,
        "safe_task_seed": 0,
        "max_steps": 30,
    }
    metadata_path = invocation_dir / f"{args.model_label}_{args.condition}.json"
    write_json(metadata_path, metadata)
    if args.dry_run:
        print(json.dumps({k: v for k, v in metadata.items() if k != "effective_system_prompt"}, indent=2))
        return 0

    agent_args = prepare_vllm_model(
        model_name=args.model,
        max_new_tokens=args.max_new_tokens,
        max_prompt_tokens=args.max_total_tokens - args.max_new_tokens,
        max_total_tokens=args.max_total_tokens,
        use_vision=False,
        base_url=args.base_url,
        api_key=args.api_key,
        harmful=False,
    )
    agent_args.set_reproducibility_mode()

    benchmark = create_default_benchmark(
        task_ids=task_ids,
        name=f"safearena-safe-{args.model_label}-{args.condition}",
    )
    study = Study(
        [agent_args],
        benchmark,
        logging_level_stdout=logging.INFO,
        suffix=f"{args.model_label}-{args.condition}",
    )
    study.run(
        n_jobs=args.n_jobs,
        parallel_backend="sequential",
        strict_reproducibility=False,
        n_relaunch=args.n_relaunch,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
