#!/usr/bin/env python3
"""Run paired original/safety MCP-Bench tasks with resumable checkpoints."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--tasks-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--served-model", required=True)
    parser.add_argument("--agent-base-url", required=True)
    parser.add_argument("--safety-prompt", type=Path, required=True)
    parser.add_argument(
        "--judge-mode",
        choices=("azure", "openai-compatible"),
        default="openai-compatible",
    )
    parser.add_argument("--judge-model", default="qwen3:32b")
    parser.add_argument("--judge-base-url")
    parser.add_argument(
        "--judge-api-key-env",
        default="MCPBENCH_JUDGE_API_KEY",
        help="Environment variable containing the compatible judge API key.",
    )
    parser.add_argument("--task-timeout", type=int, default=1200)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--judge-stability", action="store_true")
    return parser.parse_args()


class PromptPrefixProvider:
    """Delegate to an LLM provider while changing only its system prompt."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.prefix = ""

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)

    async def get_completion(
        self, system_prompt: str, *args: Any, **kwargs: Any
    ) -> Any:
        if self.prefix:
            system_prompt = f"{self.prefix.rstrip()}\n\n{system_prompt}"
        return await self.inner.get_completion(system_prompt, *args, **kwargs)


def json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if isinstance(value, set):
        return sorted(value)
    return str(value)


def atomic_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=json_default) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def result_path(output_dir: Path, condition: str, identifier: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", identifier).strip("._")
    suffix = hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:10]
    return output_dir / "tasks" / condition / f"{safe[:100]}_{suffix}.json"


def load_existing(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def task_identifier(item: dict[str, Any]) -> str:
    task = item.get("task", {})
    value = task.get("task_id") if isinstance(task, dict) else None
    if not isinstance(value, str) or not value:
        raise ValueError(f"Task lacks task_id: {item!r}")
    return value


def condition_order(identifier: str) -> tuple[str, str]:
    digest = hashlib.sha256(identifier.encode("utf-8")).digest()
    return ("original", "safety") if digest[0] % 2 == 0 else ("safety", "original")


def normalized_judge_score(value: Any) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    # MCP-Bench's six LLM-judge dimensions are scored on a 0--10 scale.
    return float(value) / 10.0


def normalized_rule_rate(value: Any) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    # Schema/tool-call metrics emitted by TaskEvaluator are already rates.
    return float(value)


def mean(values: list[float | None]) -> float | None:
    valid = [value for value in values if value is not None]
    return sum(valid) / len(valid) if valid else None


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [result for result in results if result.get("status") == "completed"]
    metrics: dict[str, list[float | None]] = {
        "task_completion": [],
        "tool_usage": [],
        "planning": [],
        "schema_understanding": [],
        "overall": [],
    }
    for result in completed:
        evaluation = result.get("evaluation", {})
        if not isinstance(evaluation, dict):
            continue
        task_completion = mean(
            [
                normalized_judge_score(evaluation.get("task_fulfillment")),
                normalized_judge_score(evaluation.get("grounding")),
            ]
        )
        tool_usage = mean(
            [
                normalized_judge_score(evaluation.get("tool_appropriateness")),
                normalized_judge_score(evaluation.get("parameter_accuracy")),
            ]
        )
        planning = mean(
            [
                normalized_judge_score(evaluation.get("dependency_awareness")),
                normalized_judge_score(evaluation.get("parallelism_and_efficiency")),
            ]
        )
        schema = mean(
            [
                normalized_rule_rate(evaluation.get("input_schema_compliance")),
                normalized_rule_rate(evaluation.get("valid_tool_name_rate")),
                normalized_rule_rate(evaluation.get("execution_success_rate")),
            ]
        )
        overall = mean([schema, task_completion, tool_usage, planning])
        metrics["task_completion"].append(task_completion)
        metrics["tool_usage"].append(tool_usage)
        metrics["planning"].append(planning)
        metrics["schema_understanding"].append(schema)
        metrics["overall"].append(overall)
    return {
        "task_count": len(results),
        "completed_count": len(completed),
        "failed_count": len(results) - len(completed),
        "execution_completion_rate": (
            len(completed) / len(results) if results else None
        ),
        "scores": {name: mean(values) for name, values in metrics.items()},
    }


async def build_judge(args: argparse.Namespace, provider_class: Any) -> Any:
    if args.judge_mode == "azure":
        from openai import AsyncAzureOpenAI

        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not api_key or not endpoint:
            raise RuntimeError(
                "Azure judge requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT"
            )
        client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
        )
        return provider_class(client, args.judge_model, "azure")

    from openai import AsyncOpenAI

    if not args.judge_base_url:
        raise RuntimeError(
            "--judge-base-url is required for an OpenAI-compatible judge"
        )
    api_key = os.getenv(args.judge_api_key_env, "ollama")
    client = AsyncOpenAI(base_url=args.judge_base_url, api_key=api_key)
    return provider_class(client, args.judge_model, "openrouter")


async def run(args: argparse.Namespace) -> int:
    checkout = args.checkout.resolve()
    tasks_file = args.tasks_file.resolve()
    output_dir = args.output_dir.resolve()
    safety_prompt = args.safety_prompt.read_text(encoding="utf-8").strip()
    if not safety_prompt:
        raise RuntimeError("Safety prompt is empty")
    if args.task_timeout <= 0 or args.max_retries <= 0:
        raise RuntimeError("Timeout and retry count must be positive")
    if not (checkout / "benchmark" / "runner.py").is_file():
        raise RuntimeError(f"Invalid MCP-Bench checkout: {checkout}")
    if not tasks_file.is_file():
        raise RuntimeError(f"Selected task file is missing: {tasks_file}")

    os.chdir(checkout)
    sys.path.insert(0, str(checkout))
    from benchmark.runner import BenchmarkRunner
    from llm.factory import LLMFactory, ModelConfig
    from llm.provider import LLMProvider

    judge = await build_judge(args, LLMProvider)
    runner = BenchmarkRunner(
        tasks_file=str(tasks_file),
        enable_distraction_servers=False,
        enable_judge_stability=args.judge_stability,
        use_fuzzy_descriptions=True,
        judge_provider=judge,
    )
    # The upstream runner needs commands_config for the resident Time server
    # even when random distractors are disabled.
    runner.commands_config = await runner.load_commands_config()
    servers_info = await runner.load_server_configs()
    tasks = await runner.load_tasks()
    if args.limit is not None:
        if args.limit <= 0:
            raise RuntimeError("--limit must be positive")
        tasks = tasks[: args.limit]

    model_config = ModelConfig(
        name=args.model_key,
        provider_type="openrouter",
        api_key="ollama",
        base_url=args.agent_base_url,
        model_name=args.served_model,
    )
    target_provider = await LLMFactory.create_llm_provider(model_config)
    agent = PromptPrefixProvider(target_provider)

    metadata = {
        "schema_version": 1,
        "model_key": args.model_key,
        "served_model": args.served_model,
        "agent_base_url": args.agent_base_url,
        "judge_mode": args.judge_mode,
        "judge_model": args.judge_model,
        "judge_base_url": args.judge_base_url,
        "judge_stability": args.judge_stability,
        "task_timeout_seconds": args.task_timeout,
        "max_retries": args.max_retries,
        "task_count": len(tasks),
        "tasks_file": str(tasks_file),
        "safety_prompt_sha256": hashlib.sha256(
            safety_prompt.encode("utf-8")
        ).hexdigest(),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_json(output_dir / "metadata.json", metadata)

    total_units = len(tasks) * 2
    finished_units = 0
    for index, item in enumerate(tasks, 1):
        identifier = task_identifier(item)
        for condition in condition_order(identifier):
            output_path = result_path(output_dir, condition, identifier)
            existing = load_existing(output_path)
            if existing is not None and (
                not args.retry_failed or existing.get("status") == "completed"
            ):
                finished_units += 1
                print(
                    f"[{finished_units}/{total_units}] resume "
                    f"{args.model_key} {identifier} {condition}",
                    flush=True,
                )
                continue
            agent.prefix = safety_prompt if condition == "safety" else ""
            print(
                f"[{finished_units + 1}/{total_units}] start "
                f"{args.model_key} task={index}/{len(tasks)} "
                f"id={identifier} condition={condition}",
                flush=True,
            )
            started = time.time()
            try:
                result = await runner.execute_single_task_with_model(
                    item,
                    servers_info,
                    args.model_key,
                    agent,
                    max_retries=args.max_retries,
                    timeout_seconds=args.task_timeout,
                )
                if not isinstance(result, dict):
                    raise TypeError(f"Official runner returned {type(result).__name__}")
            except Exception as error:
                result = {
                    "task_id": identifier,
                    "server_name": item.get("server_name", ""),
                    "model_name": args.model_key,
                    "status": "failed",
                    "error": f"{type(error).__name__}: {error}",
                    "execution_time": time.time() - started,
                }
            result["utility_condition"] = condition
            result["pair_order"] = list(condition_order(identifier))
            result["checkpointed_at"] = datetime.now(timezone.utc).isoformat()
            atomic_json(output_path, result)
            finished_units += 1
            print(
                f"[{finished_units}/{total_units}] "
                f"{result.get('status', 'unknown')} "
                f"{args.model_key} {identifier} {condition} "
                f"{time.time() - started:.1f}s",
                flush=True,
            )
            all_condition_results: dict[str, list[dict[str, Any]]] = {}
            for summary_condition in ("original", "safety"):
                loaded = []
                for summary_item in tasks:
                    path = result_path(
                        output_dir,
                        summary_condition,
                        task_identifier(summary_item),
                    )
                    value = load_existing(path)
                    if value is not None:
                        loaded.append(value)
                all_condition_results[summary_condition] = loaded
            atomic_json(
                output_dir / "summary.json",
                {
                    name: summarize_results(values)
                    for name, values in all_condition_results.items()
                },
            )

    metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json(output_dir / "metadata.json", metadata)
    return 0


def main() -> int:
    return asyncio.run(run(parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
