#!/usr/bin/env python3
"""Validate, plan, preflight, and run the MCPMark Verified utility ablation.

The upstream MCPMark checkout remains unmodified. This wrapper freezes the
selected task set, injects an OpenAI-compatible local model configuration, and
changes only the effective system prompt between the two conditions.
"""

from __future__ import annotations

import argparse
import ast
import asyncio
import contextlib
import dataclasses
import hashlib
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from collections.abc import Iterator, Mapping, Sequence
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]
DEFAULT_UPSTREAM_ROOT = REPO_ROOT / "external" / "mcpmark"
DEFAULT_MANIFEST = EXPERIMENT_DIR / "task_manifest.json"
DEFAULT_MODEL_MANIFEST = EXPERIMENT_DIR / "model_manifest.json"
DEFAULT_SAFETY_PROMPT = EXPERIMENT_DIR / "safety_prompt.txt"
POSTGRES_CLIENT_PREFIX = EXPERIMENT_DIR / ".postgres-client"
DEFAULT_PLAYWRIGHT_NODE_PREFIX = EXPERIMENT_DIR / ".node-runtime"
VERIFIED_COMMIT = "cd45b7f57923b9b3985467f5139927575f83141c"
FROZEN_TASK_MANIFEST_SHA256 = (
    "84a084f8fef671564732078891b19090010dc18527cd5df0665febb43de6b571"
)
FROZEN_MODEL_MANIFEST_SHA256 = (
    "216693ba2abafd68baa5dc5d95860efe11242c8cc9f0dbbb89ef7bdd0ca9b71b"
)
FROZEN_SAFETY_PROMPT_SHA256 = (
    "863986fee0952dbcd0bd25dde8c2812f75b4cb26c24d0d775938d465a09c1bec"
)
UPSTREAM_SYSTEM_PROMPT = (
    "You are a helpful agent that uses tools iteratively to complete the user's task, "
    'and when finished, provides the final answer or simply states "Task completed" '
    "without further tool calls."
)
UPSTREAM_SYSTEM_PROMPT_SHA256 = (
    "97d8ca63c6f0639bf46f735eb9a43d40cc05505e9fb39b79cfe843f5bc0b7b11"
)
CONDITIONS = ("original", "safety")
EXPECTED_SERVICE_TASK_COUNTS = {
    "filesystem": 20,
    "postgres": 20,
    "playwright": 4,
}
LOGICAL_SERVICES = tuple(EXPECTED_SERVICE_TASK_COUNTS)
TOTAL_TASK_COUNT = sum(EXPECTED_SERVICE_TASK_COUNTS.values())
SUBSET_NAME = "MCPMark Verified deployment-feasible 3-service subset"
SAFE_LABEL_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
FILESYSTEM_TEMPLATE_CATEGORIES = (
    "desktop",
    "desktop_template",
    "file_context",
    "file_property",
    "folder_structure",
    "legal_document",
    "papers",
    "student_database",
    "threestudio",
    "votenet",
)
POSTGRES_TEMPLATE_DATABASES = (
    "employees",
    "chinook",
    "dvdrental",
    "sports",
    "lego",
)
PLAYWRIGHT_REQUIRED_TARGET_URLS = (
    "https://eval-web.mcpmark.ai/extraction",
    "https://arxiv.org/abs/2501.12948v1",
)
PLAYWRIGHT_ADVISORY_TARGET_URLS = ("https://x.com/arvin17x",)
INFRA_ERROR_MARKERS = (
    "state duplication error",
    "connection refused",
    "connection reset",
    "internal server error",
    "service unavailable",
    "network error",
    "rate limit",
    "ratelimit",
    "quota",
    "account balance",
    "overloaded",
    "thought_signature",
)
VERIFIER_INFRA_ERROR_MARKERS = (
    "connection refused",
    "connection reset",
    "temporary failure in name resolution",
    "name or service not known",
    "service unavailable",
    "timed out",
    "timeout expired",
    "http 500",
    "http 502",
    "http 503",
    "status code 500",
    "status code 502",
    "status code 503",
    "modulenotfounderror",
    "no module named",
    "could not connect to server",
)
FORMAL_RUNTIME_CONFIGURATION = {
    "temperature": 0.0,
    "max_tokens": 32768,
    "max_turns": 100,
    "timeout": 3600,
    "compaction_token": 999_999_999,
    "reasoning_effort": "default",
}
FORMAL_MODEL_CONFIGURATION = {
    "llama31_8b": {
        "display_name": "Llama-3.1-8B-Instruct",
        "served_model": "llama3.1:8b",
        "context_length": 131_072,
        "slurm_gres": "gpu:1",
        "slurm_memory": "24G",
        "startup_delay_seconds": 0,
    },
    "llama31_70b": {
        "display_name": "Llama-3.1-70B-Instruct",
        "served_model": "llama3.1:70b",
        "context_length": 131_072,
        "slurm_gres": "gpu:2",
        "slurm_memory": "52G",
        "startup_delay_seconds": 60,
    },
    "qwen3_8b": {
        "display_name": "Qwen3-8B-Instruct",
        "served_model": "qwen3:8b",
        "context_length": 40_960,
        "slurm_gres": "gpu:1",
        "slurm_memory": "24G",
        "startup_delay_seconds": 120,
    },
    "qwen3_32b": {
        "display_name": "Qwen3-32B-Instruct",
        "served_model": "qwen3:32b",
        "context_length": 40_960,
        "slurm_gres": "gpu:1",
        "slurm_memory": "36G",
        "startup_delay_seconds": 180,
    },
}
EXECUTION_CONFIGURATION_FIELDS = (
    "model_label",
    "served_model",
    "model_artifact_id",
    "base_url",
    "temperature",
    "max_tokens",
    "max_turns",
    "timeout",
    "compaction_token",
    "reasoning_effort",
)
SIDECAR_COMPATIBILITY_FIELDS = (
    "schema_version",
    "job_key",
    "condition",
    "model_label",
    "served_model",
    "model_artifact_id",
    "base_url",
    "logical_service",
    "mcp",
    "task",
    "run",
    "source_commit",
    "manifest_sha256",
    "model_manifest_sha256",
    "safety_prompt_sha256",
    "upstream_system_prompt_sha256",
    "effective_system_prompt_sha256",
    "temperature",
    "max_tokens",
    "max_turns",
    "timeout",
    "compaction_token",
    "reasoning_effort",
)


@dataclasses.dataclass(frozen=True)
class TaskSpec:
    logical_service: str
    mcp: str
    task: str

    @property
    def category(self) -> str:
        return self.task.split("/", 1)[0]

    @property
    def task_id(self) -> str:
        return self.task.split("/", 1)[1]

    @property
    def output_dir_name(self) -> str:
        return self.task.replace("/", "__", 1)


@dataclasses.dataclass(frozen=True)
class ModelSpec:
    label: str
    display_name: str
    served_model: str
    context_length: int | None = None


class ValidationError(RuntimeError):
    """Raised when frozen experiment inputs do not validate."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return sha256_text(payload)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    temporary.replace(path)


def append_jsonl(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n")
        handle.flush()


def checked_commit(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def read_upstream_system_prompt(upstream_root: Path) -> str:
    """Read MCPMarkAgent.SYSTEM_PROMPT without importing upstream dependencies."""
    source_path = upstream_root / "src" / "agents" / "mcpmark_agent.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "MCPMarkAgent":
            for statement in node.body:
                if not isinstance(statement, ast.Assign):
                    continue
                if any(
                    isinstance(target, ast.Name) and target.id == "SYSTEM_PROMPT"
                    for target in statement.targets
                ):
                    value = ast.literal_eval(statement.value)
                    if not isinstance(value, str):
                        raise ValidationError("Upstream SYSTEM_PROMPT is not a string")
                    return value
    raise ValidationError("Could not locate MCPMarkAgent.SYSTEM_PROMPT")


def build_effective_prompt(
    original_prompt: str,
    safety_prompt: str,
    condition: str,
) -> str:
    """Build the sole prompt intervention used by the A/B experiment."""
    if condition == "original":
        return original_prompt
    if condition != "safety":
        raise ValueError(f"Unknown condition: {condition}")
    if not safety_prompt.strip():
        raise ValidationError("Safety prompt is empty")
    return (
        original_prompt.rstrip()
        + "\n\n"
        + "## Additional safety policy\n"
        + safety_prompt.strip()
        + "\n"
    )


def load_task_manifest(path: Path) -> tuple[dict[str, Any], list[TaskSpec]]:
    raw = read_json(path)
    if not isinstance(raw, dict):
        raise ValidationError("Task manifest root must be an object")
    if raw.get("benchmark") != "MCPMark Verified":
        raise ValidationError("Task manifest benchmark must be MCPMark Verified")
    if raw.get("subset_name") != SUBSET_NAME:
        raise ValidationError(f"Task manifest subset_name must be {SUBSET_NAME!r}")
    if raw.get("source_commit") != VERIFIED_COMMIT:
        raise ValidationError("Task manifest is not pinned to the Verified commit")
    if raw.get("task_suite") != "standard":
        raise ValidationError("The formal subset must use the standard suite")
    if raw.get("runtime_configuration") != FORMAL_RUNTIME_CONFIGURATION:
        raise ValidationError(
            "Task manifest runtime_configuration differs from the frozen formal design"
        )
    services = raw.get("services")
    if not isinstance(services, dict) or tuple(services) != LOGICAL_SERVICES:
        raise ValidationError(
            f"Manifest services must be ordered exactly as {LOGICAL_SERVICES}"
        )

    tasks: list[TaskSpec] = []
    for logical_service, entries in services.items():
        expected_count = EXPECTED_SERVICE_TASK_COUNTS[logical_service]
        if not isinstance(entries, list) or len(entries) != expected_count:
            raise ValidationError(
                f"Logical service {logical_service!r} must contain exactly "
                f"{expected_count} tasks"
            )
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValidationError("Every task entry must be an object")
            mcp = entry.get("mcp")
            task = entry.get("task")
            if not isinstance(mcp, str) or not isinstance(task, str):
                raise ValidationError("Every task needs string mcp and task fields")
            if task.count("/") != 1 or any(
                part in {"", ".", ".."} for part in task.split("/")
            ):
                raise ValidationError(f"Invalid category/task value: {task!r}")
            if mcp != logical_service:
                raise ValidationError(
                    f"Task {logical_service}/{task} has mismatched mcp {mcp}"
                )
            tasks.append(TaskSpec(logical_service, mcp, task))
        task_names = [
            task.task for task in tasks if task.logical_service == logical_service
        ]
        if task_names != sorted(task_names):
            raise ValidationError(
                f"Tasks for {logical_service!r} must be lexicographically ordered"
            )

    unique = {(task.mcp, task.task) for task in tasks}
    if len(tasks) != TOTAL_TASK_COUNT or len(unique) != TOTAL_TASK_COUNT:
        raise ValidationError(
            f"Manifest must contain {TOTAL_TASK_COUNT} unique physical tasks"
        )
    selection_policy = raw.get("selection_policy", {})
    if not isinstance(selection_policy, dict):
        raise ValidationError("Manifest selection_policy must be an object")
    if selection_policy.get("outcome_blind") is not True:
        raise ValidationError("Manifest must freeze an outcome-blind selection")
    if selection_policy.get("tasks_per_logical_service") != (
        EXPECTED_SERVICE_TASK_COUNTS
    ):
        raise ValidationError(
            "Manifest selection_policy task counts differ from the frozen subset"
        )
    if selection_policy.get("total_tasks") != TOTAL_TASK_COUNT:
        raise ValidationError("Manifest selection_policy total_tasks is not frozen")
    return raw, tasks


def load_model_manifest(path: Path) -> tuple[dict[str, Any], list[ModelSpec]]:
    raw = read_json(path)
    if not isinstance(raw, dict) or not isinstance(raw.get("models"), dict):
        raise ValidationError("Formal model manifest must contain a models mapping")
    if raw.get("provider") != "ollama":
        raise ValidationError("Formal model provider must be ollama")
    if tuple(raw["models"]) != tuple(FORMAL_MODEL_CONFIGURATION):
        raise ValidationError(
            "Formal model labels/order differ from the frozen four-model design"
        )
    models: list[ModelSpec] = []
    models_value = raw["models"]
    entries: list[dict[str, Any]] = []
    for label, value in models_value.items():
        if not isinstance(value, dict):
            raise ValidationError("Every model entry must be an object")
        expected = FORMAL_MODEL_CONFIGURATION[label]
        mismatched = [
            field
            for field, expected_value in expected.items()
            if value.get(field) != expected_value
        ]
        if mismatched:
            raise ValidationError(
                f"Frozen model configuration mismatch for {label}: {mismatched}"
            )
        entries.append({"label": label, **value})
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValidationError("Every model entry must be an object")
        label = entry.get("label")
        display = entry.get("display_name", entry.get("display"))
        served = entry.get("served_model", entry.get("ollama_model"))
        context = entry.get("context_length")
        if not all(
            isinstance(value, str) and value for value in (label, display, served)
        ):
            raise ValidationError(
                "Each model needs label, display_name, and served_model strings"
            )
        if not SAFE_LABEL_RE.fullmatch(label):
            raise ValidationError(f"Unsafe model label: {label!r}")
        if context is not None and (not isinstance(context, int) or context <= 0):
            raise ValidationError(f"Invalid context length for {label}")
        models.append(ModelSpec(label, display, served, context))
    if (
        len(models) != 4
        or len({model.label for model in models}) != 4
        or len({model.served_model for model in models}) != 4
    ):
        raise ValidationError(
            "The formal model manifest must contain four unique models"
        )
    return raw, models


def validate_task_source(task: TaskSpec, upstream_root: Path) -> dict[str, Any]:
    task_dir = upstream_root / "tasks" / task.mcp / "standard" / task.task
    required = ("description.md", "meta.json", "verify.py")
    missing = [name for name in required if not (task_dir / name).is_file()]
    if missing:
        raise ValidationError(f"{task.mcp}/{task.task} is missing {missing}")

    meta = read_json(task_dir / "meta.json")
    if not isinstance(meta, dict):
        raise ValidationError(f"{task.mcp}/{task.task}/meta.json is not an object")
    if meta.get("category_id") != task.category or meta.get("task_id") != task.task_id:
        raise ValidationError(
            f"Metadata ID mismatch for {task.mcp}/{task.task}: "
            f"{meta.get('category_id')}/{meta.get('task_id')}"
        )
    if meta.get("difficulty") != "L3":
        raise ValidationError(
            f"{task.mcp}/{task.task} must be a standard/L3 Verified task"
        )
    ast.parse(
        (task_dir / "verify.py").read_text(encoding="utf-8"),
        filename=str(task_dir / "verify.py"),
    )
    return {
        "logical_service": task.logical_service,
        "mcp": task.mcp,
        "task": task.task,
        "difficulty": meta.get("difficulty"),
    }


def validate_experiment_inputs(
    *,
    upstream_root: Path,
    manifest_path: Path,
    model_manifest_path: Path,
    safety_prompt_path: Path,
) -> dict[str, Any]:
    for path, label in (
        (upstream_root, "upstream checkout"),
        (manifest_path, "task manifest"),
        (model_manifest_path, "model manifest"),
        (safety_prompt_path, "safety prompt"),
    ):
        if not path.exists():
            raise ValidationError(f"Missing {label}: {path}")
    frozen_files = (
        (manifest_path, FROZEN_TASK_MANIFEST_SHA256, "task manifest"),
        (model_manifest_path, FROZEN_MODEL_MANIFEST_SHA256, "model manifest"),
        (safety_prompt_path, FROZEN_SAFETY_PROMPT_SHA256, "safety prompt"),
    )
    for path, expected_hash, label in frozen_files:
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise ValidationError(
                f"Frozen {label} hash mismatch: expected {expected_hash}, "
                f"found {actual_hash}"
            )

    commit = checked_commit(upstream_root)
    if commit != VERIFIED_COMMIT:
        raise ValidationError(
            f"MCPMark checkout is {commit}; required commit is {VERIFIED_COMMIT}"
        )
    status = subprocess.run(
        ["git", "-C", str(upstream_root), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if status:
        raise ValidationError(
            "The upstream MCPMark checkout has local modifications; restore the pinned "
            "checkout before formal runs"
        )

    manifest, tasks = load_task_manifest(manifest_path)
    _, models = load_model_manifest(model_manifest_path)
    task_checks = [validate_task_source(task, upstream_root) for task in tasks]

    original_prompt = read_upstream_system_prompt(upstream_root)
    if original_prompt != UPSTREAM_SYSTEM_PROMPT:
        raise ValidationError(
            "Upstream MCPMark system prompt differs from the frozen text"
        )
    if sha256_text(original_prompt) != UPSTREAM_SYSTEM_PROMPT_SHA256:
        raise ValidationError("Frozen upstream system-prompt hash does not match")

    safety_prompt = safety_prompt_path.read_text(encoding="utf-8")
    prompt_hashes = {
        condition: sha256_text(
            build_effective_prompt(original_prompt, safety_prompt, condition)
        )
        for condition in CONDITIONS
    }
    expected_prompt_contract = {
        "original": {
            "effective_system_prompt_sha256": prompt_hashes["original"],
        },
        "safety": {
            "safety_prompt_sha256": sha256_file(safety_prompt_path),
            "effective_system_prompt_sha256": prompt_hashes["safety"],
        },
    }
    if manifest.get("prompt_conditions") != expected_prompt_contract:
        raise ValidationError(
            "Task manifest prompt_conditions differs from the frozen prompt inputs"
        )
    counts = {
        service: sum(task.logical_service == service for task in tasks)
        for service in LOGICAL_SERVICES
    }
    physical_counts: dict[str, int] = {}
    for task in tasks:
        physical_counts[task.mcp] = physical_counts.get(task.mcp, 0) + 1
    expected = len(tasks) * len(models) * len(CONDITIONS)
    configured_expected = manifest.get("evaluation_design", {}).get(
        "expected_trajectories"
    )
    if configured_expected != expected:
        raise ValidationError(
            f"Manifest expected_trajectories={configured_expected}, calculated={expected}"
        )
    return {
        "ok": True,
        "verified_commit": commit,
        "upstream_clean": True,
        "manifest_sha256": sha256_file(manifest_path),
        "model_manifest_sha256": sha256_file(model_manifest_path),
        "safety_prompt_sha256": sha256_file(safety_prompt_path),
        "upstream_system_prompt_sha256": sha256_text(original_prompt),
        "effective_prompt_sha256": prompt_hashes,
        "logical_service_counts": counts,
        "physical_service_counts": physical_counts,
        "task_count": len(task_checks),
        "model_count": len(models),
        "condition_count": len(CONDITIONS),
        "expected_trajectories_k1": expected,
    }


def parse_selection(value: str, allowed: Sequence[str], label: str) -> tuple[str, ...]:
    if value.strip().lower() == "all":
        return tuple(allowed)
    requested = tuple(item.strip() for item in value.split(",") if item.strip())
    if not requested:
        raise ValidationError(f"No {label} selected")
    unknown = [item for item in requested if item not in allowed]
    if unknown:
        raise ValidationError(f"Unknown {label}: {unknown}; allowed: {list(allowed)}")
    if len(set(requested)) != len(requested):
        raise ValidationError(f"Duplicate {label} selection")
    return requested


def select_tasks(
    tasks: Sequence[TaskSpec],
    services: Sequence[str],
    limit_per_service: int | None = None,
) -> list[TaskSpec]:
    selected: list[TaskSpec] = []
    for service in services:
        service_tasks = [task for task in tasks if task.logical_service == service]
        if limit_per_service is not None:
            service_tasks = service_tasks[:limit_per_service]
        selected.extend(service_tasks)
    return selected


def build_plan(
    *,
    tasks: Sequence[TaskSpec],
    models: Sequence[ModelSpec],
    conditions: Sequence[str],
    runs: int,
) -> list[dict[str, Any]]:
    if runs <= 0:
        raise ValidationError("k must be positive")
    jobs: list[dict[str, Any]] = []
    for condition in conditions:
        for model in models:
            for task in tasks:
                for run_number in range(1, runs + 1):
                    jobs.append(
                        {
                            "job_key": (
                                f"{condition}|{model.label}|{task.mcp}|"
                                f"{task.task}|run-{run_number}"
                            ),
                            "condition": condition,
                            "model_label": model.label,
                            "display_name": model.display_name,
                            "served_model": model.served_model,
                            "logical_service": task.logical_service,
                            "mcp": task.mcp,
                            "task": task.task,
                            "run": run_number,
                        }
                    )
    if len({job["job_key"] for job in jobs}) != len(jobs):
        raise ValidationError("Generated plan contains duplicate job keys")
    return jobs


def resolve_api_key(base_url: str | None, api_key_env: str) -> tuple[str | None, str]:
    if api_key_env and os.getenv(api_key_env):
        return os.environ[api_key_env], f"environment:{api_key_env}"
    host = urllib.parse.urlparse(base_url or "").hostname
    if host in LOCAL_HOSTS:
        return "ollama", "local-placeholder"
    return None, f"missing:{api_key_env}"


def load_upstream_dotenv(upstream_root: Path) -> bool:
    """Load the upstream .mcp_env without overriding the caller's environment."""
    dotenv_path = upstream_root / ".mcp_env"
    if not dotenv_path.is_file():
        return False
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    load_dotenv(dotenv_path=dotenv_path, override=False)
    return True


def configure_frozen_service_environment(upstream_root: Path) -> Path:
    """Pin credential-free service settings to this upstream checkout."""
    filesystem_root = (upstream_root / "test_environments").resolve()
    frozen = {
        "FILESYSTEM_TEST_ROOT": str(filesystem_root),
        "FILESYSTEM_CLEANUP": "True",
        "PLAYWRIGHT_BROWSER": "chromium",
        "PLAYWRIGHT_HEADLESS": "True",
        "PLAYWRIGHT_NETWORK_ORIGINS": "*",
        "PLAYWRIGHT_USER_PROFILE": "isolated",
        "PLAYWRIGHT_VIEWPORT_WIDTH": "1280",
        "PLAYWRIGHT_VIEWPORT_HEIGHT": "720",
    }
    os.environ.update(frozen)
    return filesystem_root


def configured_runtime_path(current: str | None) -> str:
    """Build the child PATH with pinned local runtime tools first."""
    entries = [
        str(EXPERIMENT_DIR / "bin"),
        str(Path(sys.executable).absolute().parent),
        str(POSTGRES_CLIENT_PREFIX / "bin"),
    ]
    existing = current.split(os.pathsep) if current else []
    return os.pathsep.join(
        entries + [entry for entry in existing if entry not in entries]
    )


def ensure_runtime_path() -> None:
    """Expose this interpreter, PostgreSQL 17, and Docker shim to children."""
    os.environ["PATH"] = configured_runtime_path(os.environ.get("PATH"))


def ensure_local_endpoint_bypass(base_url: str | None) -> None:
    """Keep localhost model traffic out of environment-configured HTTP proxies."""
    host = urllib.parse.urlparse(base_url or "").hostname
    if host not in LOCAL_HOSTS:
        return
    required = ("127.0.0.1", "localhost", "::1")
    for variable in ("NO_PROXY", "no_proxy"):
        values = [
            value.strip()
            for value in os.environ.get(variable, "").split(",")
            if value.strip()
        ]
        for value in required:
            if value not in values:
                values.append(value)
        os.environ[variable] = ",".join(values)


def endpoint_identity(value: Any) -> str:
    """Normalize only the ephemeral port of a loopback model endpoint."""
    if not isinstance(value, str) or not value:
        raise ValidationError("Model base_url is missing")
    parsed = urllib.parse.urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValidationError(f"Invalid model base_url: {value!r}")
    path = parsed.path.rstrip("/") or "/"
    if parsed.hostname in LOCAL_HOSTS:
        return f"loopback:{parsed.scheme}:{path}"
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc.lower(), path, "", ""))


def mappings_compatible(
    found: Mapping[str, Any],
    expected: Mapping[str, Any],
    fields: Sequence[str],
) -> bool:
    """Compare audit documents while allowing loopback ports to be ephemeral."""
    for field in fields:
        if field != "base_url":
            if found.get(field) != expected.get(field):
                return False
            continue
        try:
            if endpoint_identity(found.get(field)) != endpoint_identity(
                expected.get(field)
            ):
                return False
        except ValidationError:
            return False
    return True


def http_json(
    url: str,
    *,
    api_key: str | None,
    payload: Mapping[str, Any] | None = None,
    timeout: float = 30.0,
) -> Any:
    headers = {"Accept": "application/json"}
    data = None
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers)
    host = urllib.parse.urlparse(url).hostname
    if host in LOCAL_HOSTS:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        response_context = opener.open(request, timeout=timeout)
    else:
        response_context = urllib.request.urlopen(request, timeout=timeout)
    with response_context as response:
        return json.loads(response.read().decode("utf-8"))


def add_check(
    checks: list[dict[str, Any]],
    name: str,
    ok: bool,
    detail: str,
    *,
    required: bool = True,
) -> None:
    checks.append(
        {"name": name, "ok": bool(ok), "required": required, "detail": detail}
    )


def executable_check(checks: list[dict[str, Any]], executable: str) -> None:
    resolved = shutil.which(executable)
    add_check(
        checks,
        f"executable:{executable}",
        resolved is not None,
        resolved or "not found on PATH",
    )


def module_check(checks: list[dict[str, Any]], module: str) -> None:
    found = importlib.util.find_spec(module) is not None
    add_check(
        checks,
        f"python-module:{module}",
        found,
        "available" if found else "not installed in this Python environment",
    )


def filesystem_mcp_runtime_check(checks: list[dict[str, Any]]) -> None:
    """Launch the pinned Filesystem MCP and require a real tool call."""
    node_prefix = Path(
        os.getenv(
            "MCPMARK_PLAYWRIGHT_NODE_PREFIX",
            str(DEFAULT_PLAYWRIGHT_NODE_PREFIX),
        )
    ).expanduser()
    server = node_prefix / "node_modules" / ".bin" / "mcp-server-filesystem"
    if not server.is_file() or not os.access(server, os.X_OK):
        add_check(
            checks,
            "filesystem-mcp-smoke",
            False,
            f"pinned Filesystem MCP executable is missing: {server}",
        )
        return

    marker = "MCPMARK_FILESYSTEM_MCP_READY.txt"
    with tempfile.TemporaryDirectory(prefix="mcpmark-fs-mcp-smoke-") as temporary:
        root = Path(temporary)
        (root / marker).write_text("ready\n", encoding="utf-8")

        async def smoke() -> str:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            parameters = StdioServerParameters(
                command=str(server),
                args=[str(root)],
                env=os.environ.copy(),
                cwd=str(EXPERIMENT_DIR),
            )
            async with stdio_client(parameters) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "list_directory",
                        {"path": str(root)},
                        read_timeout_seconds=timedelta(seconds=30),
                    )
                    if result.isError:
                        raise RuntimeError("list_directory returned an MCP error")
                    text = "\n".join(
                        str(getattr(block, "text", ""))
                        for block in result.content
                        if getattr(block, "text", None) is not None
                    )
                    if marker not in text:
                        raise RuntimeError(
                            "list_directory response did not contain the smoke marker"
                        )
                    return text

        try:
            asyncio.run(asyncio.wait_for(smoke(), timeout=60))
        except Exception as error:
            add_check(checks, "filesystem-mcp-smoke", False, str(error))
        else:
            add_check(
                checks,
                "filesystem-mcp-smoke",
                True,
                f"list_directory succeeded via {server}",
            )


def filesystem_state_check(
    checks: list[dict[str, Any]],
    *,
    upstream_root: Path,
) -> None:
    state_root = (upstream_root / "test_environments").resolve()
    invalid: list[str] = []
    if state_root.is_symlink() or not state_root.is_dir():
        invalid.append(f"missing state root: {state_root}")
    else:
        for category in FILESYSTEM_TEMPLATE_CATEGORIES:
            category_root = state_root / category
            try:
                populated = category_root.is_dir() and any(category_root.iterdir())
            except OSError as error:
                invalid.append(f"{category}: {error}")
                continue
            if category_root.is_symlink() or not populated:
                invalid.append(f"{category}: missing or empty")
        if not os.access(state_root, os.R_OK | os.W_OK | os.X_OK):
            invalid.append("state root is not readable/writable")
    add_check(
        checks,
        "filesystem-template-states",
        not invalid,
        (
            f"{len(FILESYSTEM_TEMPLATE_CATEGORIES)} populated category roots at "
            f"{state_root}"
            if not invalid
            else "; ".join(invalid)
        ),
    )


def playwright_runtime_check(checks: list[dict[str, Any]]) -> None:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            executable = Path(playwright.chromium.executable_path)
            if not executable.is_file():
                raise RuntimeError(f"Chromium executable is missing: {executable}")
            browser = playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox"],
            )
            browser.close()
    except Exception as error:
        add_check(checks, "chromium-runtime", False, str(error))
    else:
        add_check(
            checks,
            "chromium-runtime",
            True,
            f"launched {executable}",
        )


def playwright_target_egress_check(checks: list[dict[str, Any]]) -> None:
    """Verify that formal Playwright target origins are reachable in Chromium."""
    required_observations: list[str] = []
    required_failures: list[str] = []
    advisory_observations: list[str] = []
    advisory_failures: list[str] = []
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox"],
            )
            try:
                page = browser.new_page(viewport={"width": 1280, "height": 720})
                targets = (
                    *((url, True) for url in PLAYWRIGHT_REQUIRED_TARGET_URLS),
                    *((url, False) for url in PLAYWRIGHT_ADVISORY_TARGET_URLS),
                )
                for url, required in targets:
                    observations = (
                        required_observations if required else advisory_observations
                    )
                    failures = required_failures if required else advisory_failures
                    try:
                        response = page.goto(
                            url,
                            wait_until="domcontentloaded",
                            timeout=45_000,
                        )
                        status = response.status if response is not None else None
                        observations.append(f"{url} -> {status}")
                        if status is None or status >= 500:
                            failures.append(f"{url}: HTTP {status}")
                    except Exception as error:
                        failures.append(f"{url}: {error}")
            finally:
                browser.close()
    except Exception as error:
        required_failures.append(str(error))
        advisory_failures.append(str(error))
    add_check(
        checks,
        "playwright-target-egress",
        not required_failures,
        (
            "; ".join(required_observations)
            if not required_failures
            else "; ".join(required_failures)
        ),
    )
    add_check(
        checks,
        "playwright-advisory-x-egress",
        not advisory_failures,
        (
            "; ".join(advisory_observations)
            if not advisory_failures
            else "; ".join(advisory_failures)
        ),
        required=False,
    )


def playwright_mcp_runtime_check(checks: list[dict[str, Any]]) -> None:
    """Launch the pinned Node MCP server and require a real browser tool call."""
    node_prefix = Path(
        os.getenv(
            "MCPMARK_PLAYWRIGHT_NODE_PREFIX",
            str(DEFAULT_PLAYWRIGHT_NODE_PREFIX),
        )
    ).expanduser()
    node_browsers_path = Path(
        os.getenv(
            "MCPMARK_PLAYWRIGHT_NODE_BROWSERS_PATH",
            str(node_prefix / "browsers"),
        )
    ).expanduser()
    server = node_prefix / "node_modules" / ".bin" / "playwright-mcp"
    if not server.is_file() or not os.access(server, os.X_OK):
        add_check(
            checks,
            "playwright-mcp-browser-smoke",
            False,
            f"pinned Playwright MCP executable is missing: {server}",
        )
        return

    marker = "MCPMARK_NODE_BROWSER_READY"
    target = (
        "data:text/html,%3Ctitle%3Emcpmark-node-smoke%3C/title%3E"
        f"%3Ch1%3E{marker}%3C/h1%3E"
    )

    async def smoke() -> str:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        environment = os.environ.copy()
        environment["PLAYWRIGHT_BROWSERS_PATH"] = str(node_browsers_path)
        parameters = StdioServerParameters(
            command=str(server),
            args=[
                "--headless",
                "--isolated",
                "--no-sandbox",
                "--browser",
                "chromium",
                "--viewport-size",
                "1280,720",
            ],
            env=environment,
            cwd=str(EXPERIMENT_DIR),
        )
        async with stdio_client(parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(
                    "browser_navigate",
                    {"url": target},
                    read_timeout_seconds=timedelta(seconds=60),
                )
                try:
                    if result.isError:
                        raise RuntimeError("browser_navigate returned an MCP error")
                    text = "\n".join(
                        str(getattr(block, "text", ""))
                        for block in result.content
                        if getattr(block, "text", None) is not None
                    )
                    if marker not in text:
                        raise RuntimeError(
                            "browser_navigate response did not contain the smoke marker"
                        )
                    return text
                finally:
                    await session.call_tool(
                        "browser_close",
                        {},
                        read_timeout_seconds=timedelta(seconds=30),
                    )

    try:
        asyncio.run(asyncio.wait_for(smoke(), timeout=120))
    except Exception as error:
        add_check(checks, "playwright-mcp-browser-smoke", False, str(error))
    else:
        add_check(
            checks,
            "playwright-mcp-browser-smoke",
            True,
            f"browser_navigate launched Chromium via {server}",
        )


def postgres_mcp_runtime_check(checks: list[dict[str, Any]]) -> None:
    real_pipx = shutil.which("pipx")
    wrapper = EXPERIMENT_DIR / "bin" / "pipx"
    if real_pipx is None or not wrapper.is_file():
        add_check(
            checks,
            "postgres-mcp-runtime",
            False,
            "pipx or the experiment compatibility wrapper is missing",
        )
        return
    environment = os.environ.copy()
    environment["MCPMARK_REAL_PIPX"] = real_pipx
    try:
        completed = subprocess.run(
            [
                str(wrapper),
                "run",
                "postgres-mcp==0.3.0",
                "--help",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        add_check(checks, "postgres-mcp-runtime", False, str(error))
        return
    add_check(
        checks,
        "postgres-mcp-runtime",
        completed.returncode == 0,
        (
            "postgres-mcp 0.3.0 starts with the frozen MCP constraint"
            if completed.returncode == 0
            else (completed.stderr.strip() or "postgres-mcp startup check failed")
        ),
    )


def postgres_client_version_check(checks: list[dict[str, Any]]) -> None:
    versions: dict[str, str] = {}
    majors: dict[str, int] = {}
    for executable in ("psql", "pg_restore"):
        if shutil.which(executable) is None:
            return
        try:
            completed = subprocess.run(
                [executable, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            add_check(checks, "postgres-client-major", False, str(error))
            return
        output = (completed.stdout or completed.stderr).strip()
        match = re.search(r"\b(\d+)(?:\.\d+)?\b", output)
        if completed.returncode != 0 or match is None:
            add_check(
                checks,
                "postgres-client-major",
                False,
                f"could not parse {executable} version: {output}",
            )
            return
        versions[executable] = output
        majors[executable] = int(match.group(1))
    add_check(
        checks,
        "postgres-client-major",
        set(majors.values()) == {17},
        "; ".join(versions.values()),
    )


def postgres_backup_check(
    checks: list[dict[str, Any]],
    *,
    upstream_root: Path,
) -> None:
    backup_root = upstream_root / "postgres_state"
    invalid: list[str] = []
    for database in POSTGRES_TEMPLATE_DATABASES:
        backup = backup_root / f"{database}.backup"
        if not backup.is_file():
            invalid.append(f"{database}: missing")
            continue
        try:
            completed = subprocess.run(
                ["pg_restore", "--list", str(backup)],
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            invalid.append(f"{database}: {error}")
            continue
        if completed.returncode != 0:
            invalid.append(f"{database}: pg_restore --list failed")
    add_check(
        checks,
        "postgres-template-backups",
        not invalid,
        (
            f"{len(POSTGRES_TEMPLATE_DATABASES)} validated PG archives"
            if not invalid
            else "; ".join(invalid)
        ),
    )


def container_cli() -> str | None:
    configured = os.getenv("MCPMARK_CONTAINER_CLI")
    if configured:
        return configured
    if shutil.which("docker"):
        return "docker"
    if shutil.which("podman"):
        return "podman"
    return None


def normalize_container_image(image: str) -> str:
    """Normalize rootless Podman aliases used for Docker-style short names."""
    normalized = image.strip()
    for prefix in ("localhost/", "docker.io/library/", "docker.io/"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
    return normalized


def list_container_images(cli: str) -> tuple[bool, str, set[str]]:
    try:
        completed = subprocess.run(
            [cli, "images", "--format", "{{.Repository}}:{{.Tag}}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, str(error), set()
    if completed.returncode != 0:
        return False, completed.stderr.strip() or "container image query failed", set()
    images = {
        normalize_container_image(line)
        for line in completed.stdout.splitlines()
        if line.strip()
    }
    return True, f"{len(images)} image tags visible", images


def endpoint_preflight(
    checks: list[dict[str, Any]],
    *,
    base_url: str | None,
    served_model: str | None,
    api_key: str | None,
    tool_call_smoke: bool,
) -> None:
    if not base_url or not served_model:
        add_check(
            checks,
            "model-endpoint",
            False,
            "--base-url and --served-model are required",
        )
        return
    models_url = base_url.rstrip("/") + "/models"
    try:
        response = http_json(models_url, api_key=api_key, timeout=30)
        ids = {
            item.get("id")
            for item in response.get("data", [])
            if isinstance(item, dict)
        }
        add_check(
            checks,
            "model-listed",
            served_model in ids,
            (
                f"{served_model!r} present in /models"
                if served_model in ids
                else f"{served_model!r} absent; endpoint lists {sorted(x for x in ids if x)}"
            ),
        )
    except (
        OSError,
        AttributeError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
    ) as error:
        add_check(checks, "model-listed", False, f"/models request failed: {error}")
        return

    if not tool_call_smoke:
        add_check(
            checks,
            "tool-call-capability",
            True,
            "skipped by explicit option",
            required=False,
        )
        return
    payload = {
        "model": served_model,
        "messages": [
            {
                "role": "system",
                "content": "Call the return_ok tool exactly once. Do not answer in text.",
            },
            {"role": "user", "content": "Run the endpoint tool-call smoke test."},
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "return_ok",
                    "description": "Return a fixed smoke-test result.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
            }
        ],
        "temperature": 0,
        # Qwen3 uses its output budget for thinking before emitting a tool
        # call.  Its deterministic smoke response needs about 140 tokens, so
        # 128 creates a false negative even though the endpoint supports tools.
        "max_tokens": 512,
        "stream": False,
    }
    try:
        response = http_json(
            base_url.rstrip("/") + "/chat/completions",
            api_key=api_key,
            payload=payload,
            timeout=180,
        )
        message = response["choices"][0]["message"]
        finish_reason = response["choices"][0].get("finish_reason")
        calls = message.get("tool_calls") or []
        name = (
            calls[0].get("function", {}).get("name")
            if calls and isinstance(calls[0], dict)
            else None
        )
        reasoning = message.get("reasoning") or message.get("thinking") or ""
        content = message.get("content") or ""
        add_check(
            checks,
            "tool-call-capability",
            name == "return_ok",
            (
                f"received tool call {name!r}; finish_reason={finish_reason!r}; "
                f"reasoning_chars={len(reasoning)}; content_chars={len(content)}"
            ),
        )
    except (
        OSError,
        AttributeError,
        ValueError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
    ) as error:
        add_check(
            checks,
            "tool-call-capability",
            False,
            f"chat/completions tool smoke failed: {error}",
        )


def run_preflight(
    *,
    upstream_root: Path,
    services: Sequence[str],
    base_url: str | None,
    served_model: str | None,
    api_key_env: str,
    tool_call_smoke: bool,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    configure_frozen_service_environment(upstream_root)
    try:
        commit = checked_commit(upstream_root)
    except (OSError, subprocess.CalledProcessError) as error:
        commit = ""
        add_check(checks, "upstream-checkout", False, str(error))
    else:
        add_check(
            checks,
            "upstream-checkout",
            commit == VERIFIED_COMMIT,
            f"HEAD={commit}",
        )

    for executable in ("git", "node", "npm", "npx"):
        executable_check(checks, executable)
    for module in ("dotenv", "litellm", "mcp"):
        module_check(checks, module)
    if "playwright" in services:
        module_check(checks, "playwright")
        playwright_runtime_check(checks)
        playwright_target_egress_check(checks)
        playwright_mcp_runtime_check(checks)
    if "postgres" in services:
        module_check(checks, "psycopg2")

    api_key, api_key_source = resolve_api_key(base_url, api_key_env)
    add_check(
        checks,
        "model-api-key",
        api_key is not None,
        api_key_source,
    )
    endpoint_preflight(
        checks,
        base_url=base_url,
        served_model=served_model,
        api_key=api_key,
        tool_call_smoke=tool_call_smoke,
    )

    if "filesystem" in services:
        filesystem_mcp_runtime_check(checks)
        filesystem_state_check(checks, upstream_root=upstream_root)

    needs_container = "postgres" in services
    images: set[str] = set()
    cli = container_cli()
    if needs_container:
        add_check(
            checks,
            "container-cli",
            cli is not None,
            cli or "neither docker nor podman is available",
        )
        if cli:
            ok, detail, images = list_container_images(cli)
            add_check(checks, "container-runtime", ok, detail)

    if "postgres" in services:
        postgres_image_ref = "docker.io/pgvector/pgvector:0.8.0-pg17-bookworm"
        postgres_image = normalize_container_image(postgres_image_ref)
        add_check(
            checks,
            "postgres-image",
            postgres_image in images,
            (
                f"{postgres_image_ref} present"
                if postgres_image in images
                else f"{postgres_image_ref} not present"
            ),
        )
        for executable in ("psql", "pg_restore", "pipx"):
            executable_check(checks, executable)
        postgres_client_version_check(checks)
        postgres_backup_check(checks, upstream_root=upstream_root)
        postgres_mcp_runtime_check(checks)
        host = os.getenv("POSTGRES_HOST", "localhost")
        try:
            port = int(os.getenv("POSTGRES_PORT", "5432"))
        except ValueError:
            port = -1
        reachable = False
        detail = f"{host}:{port}"
        if 1 <= port <= 65535:
            try:
                with socket.create_connection((host, port), timeout=3):
                    reachable = True
            except OSError as error:
                detail += f" unreachable: {error}"
        else:
            detail += " invalid port"
        add_check(checks, "postgres-tcp", reachable, detail)

    failed_required = [
        check for check in checks if check["required"] and not check["ok"]
    ]
    return {
        "ok": not failed_required,
        "created_at": utc_now(),
        "services": list(services),
        "base_url": base_url,
        "served_model": served_model,
        "api_key_source": api_key_source,
        "container_cli": cli,
        "checks": checks,
        "failed_required": [check["name"] for check in failed_required],
    }


class CompletionController:
    """Enforce the frozen prompt and sampling parameters at every model call."""

    def __init__(
        self,
        original_callable: Any,
        *,
        expected_prompt: str,
        temperature: float,
        max_tokens: int,
    ):
        self.original_callable = original_callable
        self.expected_prompt = expected_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.main_call_count = 0
        self.total_call_count = 0

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.total_call_count += 1
        if kwargs.get("tools"):
            messages = kwargs.get("messages")
            if not isinstance(messages, list) or not messages:
                raise RuntimeError("Tool-enabled model call has no messages")
            first = messages[0]
            if (
                not isinstance(first, dict)
                or first.get("role") != "system"
                or first.get("content") != self.expected_prompt
            ):
                raise RuntimeError(
                    "Effective MCPMark system prompt does not match the frozen condition"
                )
            self.main_call_count += 1
        kwargs["temperature"] = self.temperature
        kwargs["max_tokens"] = self.max_tokens
        return await self.original_callable(*args, **kwargs)


@contextlib.contextmanager
def upstream_runtime(
    *,
    upstream_root: Path,
    model_label: str,
    served_model: str,
    base_url: str,
    api_key: str,
    effective_prompt: str,
    temperature: float,
    max_tokens: int,
    max_turns: int,
) -> Iterator[tuple[Any, Any, CompletionController]]:
    """Import and configure the pinned upstream runtime without editing it."""
    old_cwd = Path.cwd()
    old_path = list(sys.path)
    old_env = {
        "MCPMARK_LOCAL_API_KEY": os.getenv("MCPMARK_LOCAL_API_KEY"),
        "MCPMARK_LOCAL_BASE_URL": os.getenv("MCPMARK_LOCAL_BASE_URL"),
        "MCPMARK_REAL_PIPX": os.getenv("MCPMARK_REAL_PIPX"),
        "MCPMARK_DOCKER_LOOPBACK_ONLY": os.getenv("MCPMARK_DOCKER_LOOPBACK_ONLY"),
        "MCPMARK_PLAYWRIGHT_NODE_PREFIX": os.getenv("MCPMARK_PLAYWRIGHT_NODE_PREFIX"),
        "MCPMARK_PLAYWRIGHT_NODE_BROWSERS_PATH": os.getenv(
            "MCPMARK_PLAYWRIGHT_NODE_BROWSERS_PATH"
        ),
        "PATH": os.getenv("PATH"),
    }
    os.environ["MCPMARK_LOCAL_API_KEY"] = api_key
    os.environ["MCPMARK_LOCAL_BASE_URL"] = base_url
    pipx_candidate = Path(sys.executable).absolute().parent / "pipx"
    if pipx_candidate.is_file():
        os.environ["MCPMARK_REAL_PIPX"] = str(pipx_candidate)
    # Container-backed services are consumed only from the same process/node.
    # Never expose their ports on a shared host interface.
    os.environ["MCPMARK_DOCKER_LOOPBACK_ONLY"] = "1"
    os.environ.setdefault(
        "MCPMARK_PLAYWRIGHT_NODE_PREFIX",
        str(DEFAULT_PLAYWRIGHT_NODE_PREFIX),
    )
    os.environ.setdefault(
        "MCPMARK_PLAYWRIGHT_NODE_BROWSERS_PATH",
        str(DEFAULT_PLAYWRIGHT_NODE_PREFIX / "browsers"),
    )
    os.environ["PATH"] = configured_runtime_path(old_env["PATH"])
    os.chdir(upstream_root)
    sys.path.insert(0, str(upstream_root))

    try:
        from src.agents.mcpmark_agent import MCPMarkAgent
        from src.evaluator import MCPEvaluator
        from src.model_config import ModelConfig
        import litellm

        imported_evaluator = Path(sys.modules["src.evaluator"].__file__).resolve()
        if not imported_evaluator.is_relative_to(upstream_root.resolve()):
            raise RuntimeError(f"Imported wrong src package: {imported_evaluator}")

        missing_model_config = object()
        previous_model_config = ModelConfig.MODEL_CONFIGS.get(
            model_label,
            missing_model_config,
        )
        ModelConfig.MODEL_CONFIGS[model_label] = {
            "provider": "openai",
            "api_key_var": "MCPMARK_LOCAL_API_KEY",
            "base_url_var": "MCPMARK_LOCAL_BASE_URL",
            "litellm_input_model_name": f"openai/{served_model}",
        }
        previous_prompt = MCPMarkAgent.SYSTEM_PROMPT
        previous_max_turns = MCPMarkAgent.MAX_TURNS
        previous_acompletion = litellm.acompletion
        controller = CompletionController(
            previous_acompletion,
            expected_prompt=effective_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        MCPMarkAgent.SYSTEM_PROMPT = effective_prompt
        MCPMarkAgent.MAX_TURNS = max_turns
        litellm.acompletion = controller
        try:
            yield MCPEvaluator, MCPMarkAgent, controller
        finally:
            litellm.acompletion = previous_acompletion
            MCPMarkAgent.SYSTEM_PROMPT = previous_prompt
            MCPMarkAgent.MAX_TURNS = previous_max_turns
            if previous_model_config is missing_model_config:
                ModelConfig.MODEL_CONFIGS.pop(model_label, None)
            else:
                ModelConfig.MODEL_CONFIGS[model_label] = previous_model_config
    finally:
        os.chdir(old_cwd)
        sys.path[:] = old_path
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def expected_task_dir(
    results_root: Path,
    *,
    condition: str,
    model_label: str,
    logical_service: str,
    run_number: int,
    task: TaskSpec,
) -> Path:
    return (
        results_root
        / condition
        / f"{model_label}__{logical_service}"
        / f"run-{run_number}"
        / task.output_dir_name
    )


def sidecar_compatible(path: Path, expected: Mapping[str, Any]) -> bool:
    if not path.is_file():
        return False
    try:
        found = read_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    if not isinstance(found, Mapping):
        return False
    for document in (found, expected):
        configuration = {
            field: document.get(field) for field in EXECUTION_CONFIGURATION_FIELDS
        }
        if document.get("execution_configuration_sha256") != sha256_json(configuration):
            return False
    return mappings_compatible(
        found,
        expected,
        SIDECAR_COMPATIBILITY_FIELDS,
    )


def infer_infrastructure_error(
    meta: Mapping[str, Any],
    *,
    fresh_model_calls: int,
) -> str | None:
    execution = meta.get("execution_result")
    if not isinstance(execution, dict):
        return "meta.json lacks an execution_result object"
    if type(execution.get("success")) is not bool:
        return "meta.json execution_result.success is not boolean"
    error_message = execution.get("error_message")
    if isinstance(error_message, str):
        error_lower = error_message.lower()
        if not error_lower.startswith("max turns ("):
            for marker in INFRA_ERROR_MARKERS:
                if marker in error_lower:
                    return error_message
    verification_error = execution.get("verification_error")
    if isinstance(verification_error, str):
        verification_lower = verification_error.lower()
        for marker in VERIFIER_INFRA_ERROR_MARKERS:
            if marker in verification_lower:
                return f"Verifier infrastructure error: {verification_error}"
    if fresh_model_calls <= 0:
        return "No tool-enabled model call reached the configured endpoint"
    return None


def safe_remove_task_dir(task_dir: Path, results_root: Path) -> None:
    resolved_task = task_dir.resolve()
    resolved_root = results_root.resolve()
    if (
        not resolved_task.is_relative_to(resolved_root)
        or resolved_task == resolved_root
    ):
        raise RuntimeError(f"Refusing to remove unsafe path: {resolved_task}")
    if task_dir.exists():
        shutil.rmtree(task_dir)


def run_one_task(
    *,
    evaluator: Any,
    task: TaskSpec,
    task_dir: Path,
    results_root: Path,
    sidecar_base: Mapping[str, Any],
    controller: CompletionController,
    force_rerun: bool,
) -> dict[str, Any]:
    meta_path = task_dir / "meta.json"
    sidecar_path = task_dir / "experiment_meta.json"

    matching = evaluator.task_manager.filter_tasks(task.task)
    if len(matching) != 1:
        raise RuntimeError(
            f"Upstream filter {task.mcp}:{task.task} resolved {len(matching)} tasks"
        )
    selected = matching[0]
    if selected.category_id != task.category or str(selected.task_id) != task.task_id:
        raise RuntimeError(
            f"Upstream filter mismatch: {selected.category_id}/{selected.task_id}"
        )

    retried_infrastructure_error = False
    if force_rerun:
        with contextlib.suppress(Exception):
            evaluator.state_manager.clean_up(selected)
        safe_remove_task_dir(task_dir, results_root)
    elif meta_path.exists() or sidecar_path.exists():
        if not sidecar_compatible(sidecar_path, sidecar_base):
            raise RuntimeError(
                f"Existing result is incompatible or unaudited: {task_dir}. "
                "Use a new results root or pass --force-rerun for this exact task."
            )
        existing_sidecar = read_json(sidecar_path)
        if not isinstance(existing_sidecar, dict):
            raise RuntimeError(f"Invalid audit sidecar: {sidecar_path}")
        runner_status = existing_sidecar.get("runner_status")
        if not meta_path.is_file():
            if (
                runner_status != "infra_error"
                or existing_sidecar.get("upstream_meta_sha256") is not None
            ):
                raise RuntimeError(
                    f"Existing result has no matching upstream meta: {task_dir}. "
                    "Use --force-rerun for this exact task."
                )
            with contextlib.suppress(Exception):
                evaluator.state_manager.clean_up(selected)
            safe_remove_task_dir(task_dir, results_root)
            retried_infrastructure_error = True
        elif existing_sidecar.get("upstream_meta_sha256") != sha256_file(meta_path):
            raise RuntimeError(
                f"Existing result hash does not match its audit sidecar: {task_dir}. "
                "Use --force-rerun for this exact task."
            )
        elif runner_status == "normal":
            stored_calls = existing_sidecar.get("prompt_verified_model_calls")
            existing_meta = read_json(meta_path)
            if (
                not isinstance(stored_calls, int)
                or stored_calls <= 0
                or not isinstance(existing_meta, dict)
                or infer_infrastructure_error(
                    existing_meta,
                    fresh_model_calls=stored_calls,
                )
                is not None
            ):
                raise RuntimeError(
                    f"Existing normal result fails audit validation: {task_dir}. "
                    "Use --force-rerun for this exact task."
                )
            return {
                **existing_sidecar,
                "resumed": True,
                "resumed_at": utc_now(),
            }
        elif runner_status != "infra_error":
            raise RuntimeError(
                f"Existing result has invalid runner_status={runner_status!r}: "
                f"{task_dir}"
            )
        else:
            with contextlib.suppress(Exception):
                evaluator.state_manager.clean_up(selected)
            safe_remove_task_dir(task_dir, results_root)
            retried_infrastructure_error = True

    calls_before = controller.main_call_count
    report = evaluator.run_evaluation(task.task)
    fresh_calls = controller.main_call_count - calls_before
    if report.total_tasks != 1:
        raise RuntimeError(
            f"Expected one task result for {task.mcp}:{task.task}, got {report.total_tasks}"
        )
    if not meta_path.is_file():
        raise RuntimeError(f"Upstream evaluator did not create {meta_path}")
    meta = read_json(meta_path)
    if not isinstance(meta, dict):
        raise RuntimeError(f"Invalid upstream meta root at {meta_path}")
    infrastructure_error = infer_infrastructure_error(
        meta,
        fresh_model_calls=fresh_calls,
    )
    if infrastructure_error:
        with contextlib.suppress(Exception):
            evaluator.state_manager.clean_up(selected)
    sidecar = {
        **sidecar_base,
        "completed_at": utc_now(),
        "upstream_meta_sha256": sha256_file(meta_path),
        "prompt_verified_model_calls": fresh_calls,
        "resumed": False,
        "retried_infrastructure_error": retried_infrastructure_error,
        "runner_status": "infra_error" if infrastructure_error else "normal",
        "infrastructure_error": infrastructure_error,
    }
    write_json_atomic(sidecar_path, sidecar)
    return sidecar


def run_jobs(args: argparse.Namespace) -> int:
    validation = validate_experiment_inputs(
        upstream_root=args.upstream_root,
        manifest_path=args.manifest,
        model_manifest_path=args.model_manifest,
        safety_prompt_path=args.safety_prompt,
    )
    _, all_tasks = load_task_manifest(args.manifest)
    manifest_document = read_json(args.manifest)
    frozen_runs = manifest_document.get("evaluation_design", {}).get(
        "runs_per_task_condition"
    )
    if args.k != frozen_runs:
        raise ValidationError(
            f"The frozen formal design requires k={frozen_runs}; received k={args.k}"
        )
    _, all_models = load_model_manifest(args.model_manifest)
    model_by_label = {model.label: model for model in all_models}
    if args.model_label not in model_by_label:
        raise ValidationError(
            f"Unknown model label {args.model_label!r}; "
            f"allowed: {sorted(model_by_label)}"
        )
    frozen_model = model_by_label[args.model_label]
    if args.served_model != frozen_model.served_model:
        raise ValidationError(
            f"{args.model_label} must use served model {frozen_model.served_model!r}, "
            f"not {args.served_model!r}"
        )
    if not args.dry_run and (
        not isinstance(args.model_artifact_id, str)
        or re.fullmatch(r"[0-9a-f]{12,64}", args.model_artifact_id) is None
    ):
        raise ValidationError(
            "--model-artifact-id must be the 12-64 digit Ollama artifact ID"
        )
    for field, expected in FORMAL_RUNTIME_CONFIGURATION.items():
        actual = getattr(args, field)
        if actual != expected:
            raise ValidationError(
                f"The frozen formal design requires --{field.replace('_', '-')}="
                f"{expected}; received {actual}"
            )
    conditions = parse_selection(args.conditions, CONDITIONS, "conditions")
    services = parse_selection(args.services, LOGICAL_SERVICES, "services")
    selection_key = "+".join(services)
    selected_tasks = select_tasks(all_tasks, services, args.limit)
    jobs = build_plan(
        tasks=selected_tasks,
        models=[frozen_model],
        conditions=conditions,
        runs=args.k,
    )
    results_root = args.results_root.resolve()
    dry_run_document = {
        "schema_version": 1,
        "dry_run": True,
        "created_at": utc_now(),
        "results_root": str(results_root),
        "configuration": {
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "max_turns": args.max_turns,
            "timeout": args.timeout,
            "compaction_token": args.compaction_token,
            "reasoning_effort": args.reasoning_effort,
            "k": args.k,
            "limit_per_service": args.limit,
        },
        "input_hashes": {
            "task_manifest": validation["manifest_sha256"],
            "model_manifest": validation["model_manifest_sha256"],
            "safety_prompt": validation["safety_prompt_sha256"],
        },
        "job_count": len(jobs),
        "jobs": jobs,
    }
    if args.dry_run:
        print(json.dumps(dry_run_document, indent=2, ensure_ascii=False))
        return 0

    ensure_local_endpoint_bypass(args.base_url)
    load_upstream_dotenv(args.upstream_root)
    configure_frozen_service_environment(args.upstream_root)
    api_key, api_key_source = resolve_api_key(args.base_url, args.api_key_env)
    if api_key is None:
        raise ValidationError(
            f"Set {args.api_key_env} for the non-local model endpoint"
        )
    if not args.skip_preflight:
        preflight = run_preflight(
            upstream_root=args.upstream_root,
            services=services,
            base_url=args.base_url,
            served_model=args.served_model,
            api_key_env=args.api_key_env,
            tool_call_smoke=not args.skip_tool_call_smoke,
        )
        preflight_path = (
            results_root / "preflight" / f"{args.model_label}__{selection_key}.json"
        )
        write_json_atomic(preflight_path, preflight)
        if not preflight["ok"]:
            raise RuntimeError(
                "Preflight failed: " + ", ".join(preflight["failed_required"])
            )

    safety_text = args.safety_prompt.read_text(encoding="utf-8")
    original_prompt = read_upstream_system_prompt(args.upstream_root)
    ledger_path = (
        results_root / "job_status" / f"{args.model_label}__{selection_key}.jsonl"
    )
    errors = 0

    for condition in conditions:
        effective_prompt = build_effective_prompt(
            original_prompt,
            safety_text,
            condition,
        )
        invocation = {
            "schema_version": 1,
            "created_at": utc_now(),
            "benchmark": "MCPMark Verified",
            "subset_name": SUBSET_NAME,
            "source_commit": VERIFIED_COMMIT,
            "condition": condition,
            "model_label": args.model_label,
            "display_name": frozen_model.display_name,
            "served_model": args.served_model,
            "model_artifact_id": args.model_artifact_id,
            "base_url": args.base_url,
            "api_key_source": api_key_source,
            "task_manifest": str(args.manifest),
            "task_manifest_sha256": validation["manifest_sha256"],
            "model_manifest_sha256": validation["model_manifest_sha256"],
            "safety_prompt_sha256": validation["safety_prompt_sha256"],
            "upstream_system_prompt_sha256": sha256_text(original_prompt),
            "effective_system_prompt_sha256": sha256_text(effective_prompt),
            "effective_system_prompt": effective_prompt,
            "services": list(services),
            "task_count": len(selected_tasks),
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "max_turns": args.max_turns,
            "timeout": args.timeout,
            "compaction_token": args.compaction_token,
            "reasoning_effort": args.reasoning_effort,
            "k": args.k,
            "limit_per_service": args.limit,
        }
        invocation_path = (
            results_root
            / "invocations"
            / condition
            / f"{args.model_label}__{selection_key}.json"
        )
        if invocation_path.exists():
            existing = read_json(invocation_path)
            compatibility_fields = (
                "task_manifest_sha256",
                "model_manifest_sha256",
                "effective_system_prompt_sha256",
                "served_model",
                "model_artifact_id",
                "temperature",
                "max_tokens",
                "max_turns",
                "timeout",
                "compaction_token",
                "reasoning_effort",
                "base_url",
                "services",
                "task_count",
                "limit_per_service",
                "k",
            )
            if not isinstance(existing, Mapping) or not mappings_compatible(
                existing,
                invocation,
                compatibility_fields,
            ):
                raise RuntimeError(
                    f"Incompatible invocation already exists: {invocation_path}"
                )
        else:
            write_json_atomic(invocation_path, invocation)

        with upstream_runtime(
            upstream_root=args.upstream_root,
            model_label=args.model_label,
            served_model=args.served_model,
            base_url=args.base_url,
            api_key=api_key,
            effective_prompt=effective_prompt,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            max_turns=args.max_turns,
        ) as (evaluator_class, _agent_class, controller):
            for run_number in range(1, args.k + 1):
                for logical_service in services:
                    service_tasks = [
                        task
                        for task in selected_tasks
                        if task.logical_service == logical_service
                    ]
                    physical_services = tuple(
                        dict.fromkeys(task.mcp for task in service_tasks)
                    )
                    for physical_service in physical_services:
                        physical_tasks = [
                            task
                            for task in service_tasks
                            if task.mcp == physical_service
                        ]
                        evaluator = None
                        try:
                            evaluator = evaluator_class(
                                mcp_service=physical_service,
                                model=args.model_label,
                                timeout=args.timeout,
                                exp_name=f"run-{run_number}",
                                output_dir=results_root / condition,
                                reasoning_effort=args.reasoning_effort,
                                agent_name="mcpmark",
                                task_suite="standard",
                                compaction_token=args.compaction_token,
                            )
                            for task in physical_tasks:
                                job_key = (
                                    f"{condition}|{args.model_label}|{task.mcp}|"
                                    f"{task.task}|run-{run_number}"
                                )
                                task_dir = expected_task_dir(
                                    results_root,
                                    condition=condition,
                                    model_label=args.model_label,
                                    logical_service=logical_service,
                                    run_number=run_number,
                                    task=task,
                                )
                                sidecar_base = {
                                    "schema_version": 1,
                                    "job_key": job_key,
                                    "condition": condition,
                                    "model_label": args.model_label,
                                    "served_model": args.served_model,
                                    "model_artifact_id": args.model_artifact_id,
                                    "base_url": args.base_url,
                                    "logical_service": logical_service,
                                    "mcp": task.mcp,
                                    "task": task.task,
                                    "run": run_number,
                                    "source_commit": VERIFIED_COMMIT,
                                    "manifest_sha256": validation["manifest_sha256"],
                                    "model_manifest_sha256": validation[
                                        "model_manifest_sha256"
                                    ],
                                    "safety_prompt_sha256": validation[
                                        "safety_prompt_sha256"
                                    ],
                                    "upstream_system_prompt_sha256": sha256_text(
                                        original_prompt
                                    ),
                                    "effective_system_prompt_sha256": sha256_text(
                                        effective_prompt
                                    ),
                                    "execution_configuration_sha256": sha256_json(
                                        {
                                            "model_label": args.model_label,
                                            "served_model": args.served_model,
                                            "model_artifact_id": (
                                                args.model_artifact_id
                                            ),
                                            "base_url": args.base_url,
                                            "temperature": args.temperature,
                                            "max_tokens": args.max_tokens,
                                            "max_turns": args.max_turns,
                                            "timeout": args.timeout,
                                            "compaction_token": args.compaction_token,
                                            "reasoning_effort": args.reasoning_effort,
                                        }
                                    ),
                                    "temperature": args.temperature,
                                    "max_tokens": args.max_tokens,
                                    "max_turns": args.max_turns,
                                    "timeout": args.timeout,
                                    "compaction_token": args.compaction_token,
                                    "reasoning_effort": args.reasoning_effort,
                                }
                                append_jsonl(
                                    ledger_path,
                                    {
                                        "event": "started",
                                        "at": utc_now(),
                                        "job_key": job_key,
                                    },
                                )
                                task_calls_before = controller.main_call_count
                                try:
                                    result = run_one_task(
                                        evaluator=evaluator,
                                        task=task,
                                        task_dir=task_dir,
                                        results_root=results_root,
                                        sidecar_base=sidecar_base,
                                        controller=controller,
                                        force_rerun=args.force_rerun,
                                    )
                                except BaseException as error:
                                    errors += 1
                                    meta_path = task_dir / "meta.json"
                                    sidecar_path = task_dir / "experiment_meta.json"
                                    if (
                                        not meta_path.exists()
                                        and not sidecar_path.exists()
                                    ):
                                        write_json_atomic(
                                            sidecar_path,
                                            {
                                                **sidecar_base,
                                                "completed_at": utc_now(),
                                                "upstream_meta_sha256": None,
                                                "prompt_verified_model_calls": (
                                                    controller.main_call_count
                                                    - task_calls_before
                                                ),
                                                "resumed": False,
                                                "runner_status": "infra_error",
                                                "infrastructure_error": (
                                                    f"{type(error).__name__}: {error}"
                                                ),
                                            },
                                        )
                                    with contextlib.suppress(Exception):
                                        evaluator.state_manager.clean_up(None)
                                    append_jsonl(
                                        ledger_path,
                                        {
                                            "event": "exception",
                                            "at": utc_now(),
                                            "job_key": job_key,
                                            "error_type": type(error).__name__,
                                            "error": str(error),
                                        },
                                    )
                                    if not args.continue_on_error:
                                        raise
                                else:
                                    append_jsonl(
                                        ledger_path,
                                        {
                                            "event": "finished",
                                            "at": utc_now(),
                                            "job_key": job_key,
                                            "runner_status": result["runner_status"],
                                        },
                                    )
                                    if result["runner_status"] == "infra_error":
                                        errors += 1
                                        if not args.continue_on_error:
                                            raise RuntimeError(
                                                f"Infrastructure failure for {job_key}: "
                                                f"{result['infrastructure_error']}"
                                            )
                        except BaseException:
                            if evaluator is not None:
                                with contextlib.suppress(Exception):
                                    evaluator.state_manager.clean_up(None)
                            if not args.continue_on_error:
                                raise
                            errors += 1
    return 1 if errors else 0


def add_path_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--upstream-root",
        type=Path,
        default=DEFAULT_UPSTREAM_ROOT,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
    )
    parser.add_argument(
        "--model-manifest",
        type=Path,
        default=DEFAULT_MODEL_MANIFEST,
    )
    parser.add_argument(
        "--safety-prompt",
        type=Path,
        default=DEFAULT_SAFETY_PROMPT,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate frozen source, manifests, tasks, and prompts",
    )
    add_path_arguments(validate_parser)

    plan_parser = subparsers.add_parser(
        "plan",
        help="Generate the immutable trajectory plan without running services",
    )
    add_path_arguments(plan_parser)
    plan_parser.add_argument("--output", type=Path, required=True)
    plan_parser.add_argument("--models", default="all")
    plan_parser.add_argument("--conditions", default="all")
    plan_parser.add_argument("--services", default="all")
    plan_parser.add_argument("--k", type=int, default=1)

    preflight_parser = subparsers.add_parser(
        "preflight",
        help="Check endpoint, dependencies, service assets, and target connectivity",
    )
    add_path_arguments(preflight_parser)
    preflight_parser.add_argument("--services", default="all")
    preflight_parser.add_argument("--base-url")
    preflight_parser.add_argument("--served-model")
    preflight_parser.add_argument(
        "--api-key-env",
        default="MCPMARK_MODEL_API_KEY",
    )
    preflight_parser.add_argument("--skip-tool-call-smoke", action="store_true")
    preflight_parser.add_argument("--json-output", type=Path)

    run_parser = subparsers.add_parser(
        "run",
        help="Run one frozen model across selected prompt conditions and services",
    )
    add_path_arguments(run_parser)
    run_parser.add_argument("--results-root", type=Path, required=True)
    run_parser.add_argument("--model-label", required=True)
    run_parser.add_argument("--served-model", required=True)
    run_parser.add_argument(
        "--model-artifact-id",
        help="Ollama artifact ID; required for every non-dry formal invocation",
    )
    run_parser.add_argument("--base-url", required=True)
    run_parser.add_argument(
        "--api-key-env",
        default="MCPMARK_MODEL_API_KEY",
    )
    run_parser.add_argument("--conditions", default="original,safety")
    run_parser.add_argument("--services", default="all")
    run_parser.add_argument(
        "--limit",
        type=int,
        help="Smoke-test limit applied independently within each logical service",
    )
    run_parser.add_argument("--k", type=int, default=1)
    run_parser.add_argument("--temperature", type=float, default=0.0)
    run_parser.add_argument("--max-tokens", type=int, default=32768)
    run_parser.add_argument("--max-turns", type=int, default=100)
    run_parser.add_argument("--timeout", type=int, default=3600)
    run_parser.add_argument("--compaction-token", type=int, default=999_999_999)
    run_parser.add_argument(
        "--reasoning-effort",
        default="default",
        choices=("default", "minimal", "low", "medium", "high", "xhigh", "max"),
    )
    run_parser.add_argument("--dry-run", action="store_true")
    run_parser.add_argument("--skip-preflight", action="store_true")
    run_parser.add_argument("--skip-tool-call-smoke", action="store_true")
    run_parser.add_argument("--continue-on-error", action="store_true")
    run_parser.add_argument(
        "--force-rerun",
        action="store_true",
        help="Delete only each selected task's existing result directory before rerun",
    )
    return parser


def normalize_paths(args: argparse.Namespace) -> None:
    for name in ("upstream_root", "manifest", "model_manifest", "safety_prompt"):
        value = getattr(args, name, None)
        if value is not None:
            setattr(args, name, value.expanduser().resolve())
    if getattr(args, "results_root", None) is not None:
        args.results_root = args.results_root.expanduser().resolve()
    if getattr(args, "output", None) is not None:
        args.output = args.output.expanduser().resolve()
    if getattr(args, "json_output", None) is not None:
        args.json_output = args.json_output.expanduser().resolve()


def main(argv: Sequence[str] | None = None) -> int:
    ensure_runtime_path()
    parser = build_parser()
    args = parser.parse_args(argv)
    normalize_paths(args)
    try:
        if args.command == "validate":
            report = validate_experiment_inputs(
                upstream_root=args.upstream_root,
                manifest_path=args.manifest,
                model_manifest_path=args.model_manifest,
                safety_prompt_path=args.safety_prompt,
            )
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0

        if args.command == "plan":
            validation = validate_experiment_inputs(
                upstream_root=args.upstream_root,
                manifest_path=args.manifest,
                model_manifest_path=args.model_manifest,
                safety_prompt_path=args.safety_prompt,
            )
            _, all_tasks = load_task_manifest(args.manifest)
            _, all_models = load_model_manifest(args.model_manifest)
            labels = parse_selection(
                args.models,
                tuple(model.label for model in all_models),
                "models",
            )
            model_by_label = {model.label: model for model in all_models}
            conditions = parse_selection(args.conditions, CONDITIONS, "conditions")
            services = parse_selection(
                args.services,
                LOGICAL_SERVICES,
                "services",
            )
            jobs = build_plan(
                tasks=select_tasks(all_tasks, services),
                models=[model_by_label[label] for label in labels],
                conditions=conditions,
                runs=args.k,
            )
            document = {
                "schema_version": 1,
                "created_at": utc_now(),
                "benchmark": "MCPMark Verified",
                "subset_name": SUBSET_NAME,
                "source_commit": VERIFIED_COMMIT,
                "task_manifest_sha256": validation["manifest_sha256"],
                "model_manifest_sha256": validation["model_manifest_sha256"],
                "safety_prompt_sha256": validation["safety_prompt_sha256"],
                "models": list(labels),
                "conditions": list(conditions),
                "services": list(services),
                "k": args.k,
                "job_count": len(jobs),
                "jobs": jobs,
            }
            write_json_atomic(args.output, document)
            print(f"Wrote {len(jobs)} frozen jobs to {args.output}")
            return 0

        if args.command == "preflight":
            load_upstream_dotenv(args.upstream_root)
            services = parse_selection(
                args.services,
                LOGICAL_SERVICES,
                "services",
            )
            report = run_preflight(
                upstream_root=args.upstream_root,
                services=services,
                base_url=args.base_url,
                served_model=args.served_model,
                api_key_env=args.api_key_env,
                tool_call_smoke=not args.skip_tool_call_smoke,
            )
            if args.json_output:
                write_json_atomic(args.json_output, report)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["ok"] else 1

        if args.command == "run":
            if args.limit is not None and args.limit <= 0:
                raise ValidationError("--limit must be positive")
            if args.k <= 0:
                raise ValidationError("--k must be positive")
            if args.max_tokens <= 0 or args.max_turns <= 0 or args.timeout <= 0:
                raise ValidationError(
                    "token, turn, and timeout limits must be positive"
                )
            return run_jobs(args)
    except (
        ValidationError,
        RuntimeError,
        OSError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    parser.error(f"Unhandled command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
