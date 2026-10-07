#!/usr/bin/env python3
"""Summarize paired MCPMark Verified prompt-ablation results.

Expected result layout:

    RESULTS/{original,safety}/{model}__{logical_service}/run-N/
        {category}__{task}/meta.json

The task and model manifests are the source of truth. A job is scoreable only
when its audit sidecar matches the frozen inputs/configuration, its ``meta.json``
hash matches that sidecar, a prompt-verified model call was recorded, and
``execution_result.success`` is boolean. Missing or infrastructure-invalid
results are reported separately and excluded from score denominators.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import urllib.parse


CONDITIONS = ("original", "safety")
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
PAIRING_CONFIGURATION_FIELDS = tuple(
    field for field in EXECUTION_CONFIGURATION_FIELDS if field != "base_url"
)
LOCAL_ENDPOINT_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _endpoint_identity(value: Any) -> str:
    """Normalize ephemeral loopback ports without weakening remote endpoint checks."""
    if not isinstance(value, str) or not value:
        raise ValueError("base_url is missing")
    parsed = urllib.parse.urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"invalid base_url: {value!r}")
    path = parsed.path.rstrip("/") or "/"
    if parsed.hostname in LOCAL_ENDPOINT_HOSTS:
        return f"loopback:{parsed.scheme}:{path}"
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc.lower(),
            path,
            "",
            "",
        )
    )


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def _deduplicate(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        value = raw_value.strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def parse_models_argument(value: str) -> list[str]:
    """Parse a comma-separated list of model labels."""
    models = _deduplicate(value.split(","))
    if not models:
        raise ValueError("--models must contain at least one model label")
    return models


def load_model_labels(path: Path) -> list[str]:
    """Load model labels from the experiment model manifest.

    The canonical shape is ``{"models": [{"label": "..."}]}``.  A mapping
    keyed by label is also accepted to make the summarizer tolerant of minor
    manifest-format changes.
    """
    document = _read_json(path)
    models_value = document.get("models") if isinstance(document, dict) else document

    labels: list[str] = []
    if isinstance(models_value, list):
        for item in models_value:
            if isinstance(item, str):
                labels.append(item)
            elif isinstance(item, dict) and isinstance(item.get("label"), str):
                labels.append(item["label"])
    elif isinstance(models_value, dict):
        for key, item in models_value.items():
            if isinstance(item, dict) and isinstance(item.get("label"), str):
                labels.append(item["label"])
            elif isinstance(key, str):
                labels.append(key)

    labels = _deduplicate(labels)
    if not labels:
        raise ValueError(f"No model labels found in {path}")
    return labels


def build_audit_contract(
    manifest: Mapping[str, Any],
    *,
    manifest_path: Path,
    model_manifest_path: Path,
) -> dict[str, Any]:
    """Build the exact input/configuration contract required for scoring."""
    prompt_conditions = manifest.get("prompt_conditions")
    runtime_configuration = manifest.get("runtime_configuration")
    if not isinstance(prompt_conditions, dict):
        raise ValueError("Task manifest has no prompt_conditions audit contract")
    if not isinstance(runtime_configuration, dict):
        raise ValueError("Task manifest has no runtime_configuration audit contract")

    original = prompt_conditions.get("original")
    safety = prompt_conditions.get("safety")
    if not isinstance(original, dict) or not isinstance(safety, dict):
        raise ValueError(
            "Task manifest prompt_conditions must define original and safety"
        )
    effective_prompts = {
        "original": original.get("effective_system_prompt_sha256"),
        "safety": safety.get("effective_system_prompt_sha256"),
    }
    if not all(
        isinstance(value, str) and len(value) == 64
        for value in effective_prompts.values()
    ):
        raise ValueError("Task manifest has invalid effective prompt hashes")
    safety_prompt_sha256 = safety.get("safety_prompt_sha256")
    if not isinstance(safety_prompt_sha256, str) or len(safety_prompt_sha256) != 64:
        raise ValueError("Task manifest has invalid safety prompt hash")

    model_manifest = _read_json(model_manifest_path)
    models_value = (
        model_manifest.get("models") if isinstance(model_manifest, dict) else None
    )
    if not isinstance(models_value, (dict, list)):
        raise ValueError("Model manifest must contain a models mapping or list")
    served_models: dict[str, str] = {}
    if isinstance(models_value, dict):
        entries = ({"label": label, **entry} for label, entry in models_value.items())
    else:
        entries = iter(models_value)
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Every model manifest entry must be an object")
        label = entry.get("label")
        served_model = entry.get("served_model", entry.get("ollama_model"))
        if not isinstance(label, str) or not isinstance(served_model, str):
            raise ValueError("Every model needs label and served_model strings")
        served_models[label] = served_model
    if not served_models:
        raise ValueError("Model manifest contains no served model IDs")

    source_commit = manifest.get("source_commit")
    if not isinstance(source_commit, str) or not source_commit:
        raise ValueError("Task manifest source_commit is missing")
    return {
        "source_commit": source_commit,
        "manifest_sha256": _sha256_file(manifest_path),
        "model_manifest_sha256": _sha256_file(model_manifest_path),
        "safety_prompt_sha256": safety_prompt_sha256,
        "upstream_system_prompt_sha256": effective_prompts["original"],
        "effective_system_prompt_sha256": effective_prompts,
        "runtime_configuration": dict(runtime_configuration),
        "served_models": served_models,
    }


def _validate_manifest(manifest: Mapping[str, Any]) -> None:
    services = manifest.get("services")
    if not isinstance(services, dict) or not services:
        raise ValueError("Task manifest must contain a non-empty 'services' object")

    seen: set[tuple[str, str, str]] = set()
    for logical_service, tasks in services.items():
        if not isinstance(logical_service, str) or not logical_service:
            raise ValueError("Every logical service must have a non-empty string name")
        if not isinstance(tasks, list) or not tasks:
            raise ValueError(f"Service {logical_service!r} has no task list")
        for task_spec in tasks:
            if not isinstance(task_spec, dict):
                raise ValueError(f"Invalid task entry under {logical_service!r}")
            mcp = task_spec.get("mcp")
            task = task_spec.get("task")
            if not isinstance(mcp, str) or not mcp:
                raise ValueError(f"Task under {logical_service!r} has no valid 'mcp'")
            if not isinstance(task, str) or "/" not in task:
                raise ValueError(
                    f"Task under {logical_service!r} must be category/task, got {task!r}"
                )
            identity = (logical_service, mcp, task)
            if identity in seen:
                raise ValueError(f"Duplicate task in manifest: {identity}")
            seen.add(identity)


def _runs_per_condition(manifest: Mapping[str, Any]) -> int:
    design = manifest.get("evaluation_design", {})
    value = design.get("runs_per_task_condition", 1) if isinstance(design, dict) else 1
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("evaluation_design.runs_per_task_condition must be >= 1")
    return value


def _task_dir_name(task: str) -> str:
    return task.replace("/", "__")


def _job_key(job: Mapping[str, Any]) -> tuple[str, str, str, int]:
    return (job["model"], job["service"], job["task"], job["run"])


def expected_jobs(
    manifest: Mapping[str, Any],
    model_labels: Sequence[str],
    results_root: Path,
    audit_contract: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build all expected jobs from the manifest, models and two conditions."""
    _validate_manifest(manifest)
    models = _deduplicate(model_labels)
    if not models:
        raise ValueError("At least one model label is required")

    jobs: list[dict[str, Any]] = []
    runs = _runs_per_condition(manifest)
    for condition in CONDITIONS:
        for model in models:
            for logical_service, tasks in manifest["services"].items():
                for task_spec in tasks:
                    for run_number in range(1, runs + 1):
                        meta_path = (
                            results_root
                            / condition
                            / f"{model}__{logical_service}"
                            / f"run-{run_number}"
                            / _task_dir_name(task_spec["task"])
                            / "meta.json"
                        )
                        sidecar_path = meta_path.with_name("experiment_meta.json")
                        jobs.append(
                            {
                                "condition": condition,
                                "model": model,
                                "service": logical_service,
                                "mcp": task_spec["mcp"],
                                "task": task_spec["task"],
                                "run": run_number,
                                "meta_path": meta_path,
                                "sidecar_path": sidecar_path,
                                "audit_contract": audit_contract,
                            }
                        )
    return jobs


def _classify_job(job: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(job["meta_path"])
    sidecar_path = Path(job["sidecar_path"])
    base = {
        key: job[key] for key in ("condition", "model", "service", "mcp", "task", "run")
    }
    base["path"] = str(path)

    if not path.is_file() and not sidecar_path.is_file():
        return {**base, "status": "missing", "error": "meta.json not found"}

    if not sidecar_path.is_file():
        return {
            **base,
            "status": "infra_error",
            "error": "experiment_meta.json not found; prompt condition is unaudited",
        }
    try:
        sidecar = _read_json(sidecar_path)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return {
            **base,
            "status": "infra_error",
            "error": f"Could not read experiment_meta.json: {error}",
        }
    if not isinstance(sidecar, dict):
        return {
            **base,
            "status": "infra_error",
            "error": "experiment_meta.json root is not an object",
        }

    expected_sidecar = {
        "condition": job["condition"],
        "model_label": job["model"],
        "logical_service": job["service"],
        "mcp": job["mcp"],
        "task": job["task"],
        "run": job["run"],
    }
    mismatched = [
        field
        for field, expected in expected_sidecar.items()
        if sidecar.get(field) != expected
    ]
    if mismatched:
        return {
            **base,
            "status": "infra_error",
            "error": (
                "experiment_meta.json identity mismatch: " + ", ".join(mismatched)
            ),
        }

    if not path.is_file():
        return {
            **base,
            "status": "infra_error",
            "error": (
                sidecar.get("infrastructure_error")
                or "meta.json not found after an attempted trajectory"
            ),
        }

    audit_contract = job.get("audit_contract")
    if isinstance(audit_contract, Mapping):
        served_models = audit_contract.get("served_models")
        effective_prompts = audit_contract.get("effective_system_prompt_sha256")
        runtime_configuration = audit_contract.get("runtime_configuration")
        if not isinstance(served_models, Mapping):
            return {
                **base,
                "status": "infra_error",
                "error": "invalid served-model audit contract",
            }
        if job["model"] not in served_models:
            return {
                **base,
                "status": "infra_error",
                "error": f"model is absent from audit contract: {job['model']}",
            }
        expected_audit = {
            "source_commit": audit_contract.get("source_commit"),
            "manifest_sha256": audit_contract.get("manifest_sha256"),
            "model_manifest_sha256": audit_contract.get("model_manifest_sha256"),
            "safety_prompt_sha256": audit_contract.get("safety_prompt_sha256"),
            "upstream_system_prompt_sha256": audit_contract.get(
                "upstream_system_prompt_sha256"
            ),
            "effective_system_prompt_sha256": (
                effective_prompts.get(job["condition"])
                if isinstance(effective_prompts, Mapping)
                else None
            ),
            "served_model": served_models[job["model"]],
        }
        audit_mismatches = [
            field
            for field, expected in expected_audit.items()
            if sidecar.get(field) != expected
        ]
        if isinstance(runtime_configuration, Mapping):
            audit_mismatches.extend(
                field
                for field, expected in runtime_configuration.items()
                if sidecar.get(field) != expected
            )
        else:
            audit_mismatches.append("runtime_configuration")
        if audit_mismatches:
            return {
                **base,
                "status": "infra_error",
                "error": (
                    "experiment audit contract mismatch: " + ", ".join(audit_mismatches)
                ),
            }

    expected_meta_sha256 = sidecar.get("upstream_meta_sha256")
    try:
        actual_meta_sha256 = _sha256_file(path)
    except OSError as error:
        return {
            **base,
            "status": "infra_error",
            "error": f"Could not hash meta.json: {error}",
        }
    if expected_meta_sha256 != actual_meta_sha256:
        return {
            **base,
            "status": "infra_error",
            "error": "meta.json SHA-256 does not match experiment_meta.json",
        }

    execution_configuration = {
        field: sidecar.get(field) for field in EXECUTION_CONFIGURATION_FIELDS
    }
    execution_configuration_sha256 = _sha256_json(execution_configuration)
    if sidecar.get("execution_configuration_sha256") != execution_configuration_sha256:
        return {
            **base,
            "status": "infra_error",
            "error": "execution configuration hash mismatch",
        }
    artifact_id = sidecar.get("model_artifact_id")
    if (
        not isinstance(artifact_id, str)
        or len(artifact_id) < 12
        or len(artifact_id) > 64
        or any(character not in "0123456789abcdef" for character in artifact_id)
    ):
        return {
            **base,
            "status": "infra_error",
            "error": "model_artifact_id is missing or invalid",
        }
    try:
        endpoint_identity = _endpoint_identity(sidecar.get("base_url"))
    except ValueError as error:
        return {
            **base,
            "status": "infra_error",
            "error": str(error),
        }
    pairing_configuration = {
        field: sidecar.get(field) for field in PAIRING_CONFIGURATION_FIELDS
    }
    pairing_configuration["endpoint_identity"] = endpoint_identity
    pairing_configuration_sha256 = _sha256_json(pairing_configuration)

    runner_status = sidecar.get("runner_status")
    if runner_status == "infra_error":
        return {
            **base,
            "status": "infra_error",
            "error": sidecar.get("infrastructure_error")
            or "runner classified the trajectory as infrastructure failure",
        }
    if runner_status != "normal":
        return {
            **base,
            "status": "infra_error",
            "error": f"invalid runner_status in experiment_meta.json: {runner_status!r}",
        }
    prompt_verified_calls = sidecar.get("prompt_verified_model_calls")
    if (
        isinstance(prompt_verified_calls, bool)
        or not isinstance(prompt_verified_calls, int)
        or prompt_verified_calls <= 0
    ):
        return {
            **base,
            "status": "infra_error",
            "error": "no prompt-verified model call recorded",
        }

    try:
        meta = _read_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return {
            **base,
            "status": "infra_error",
            "error": f"Could not read valid JSON: {error}",
        }

    if not isinstance(meta, dict):
        return {
            **base,
            "status": "infra_error",
            "error": "meta.json root is not an object",
        }

    if isinstance(audit_contract, Mapping):
        runtime_configuration = audit_contract["runtime_configuration"]
        expected_upstream_meta = {
            "task_name": _task_dir_name(job["task"]),
            "model_name": job["model"],
            "reasoning_effort": runtime_configuration["reasoning_effort"],
            "mcp": job["mcp"],
            "timeout": runtime_configuration["timeout"],
        }
        upstream_mismatches = [
            field
            for field, expected in expected_upstream_meta.items()
            if meta.get(field) != expected
        ]
        if upstream_mismatches:
            return {
                **base,
                "status": "infra_error",
                "error": (
                    "upstream meta identity/config mismatch: "
                    + ", ".join(upstream_mismatches)
                ),
            }

    execution_result = meta.get("execution_result")
    if not isinstance(execution_result, dict):
        return {
            **base,
            "status": "infra_error",
            "error": "execution_result is missing or is not an object",
        }
    success = execution_result.get("success")
    if type(success) is not bool:  # Deliberately reject 0/1 and truthy strings.
        return {
            **base,
            "status": "infra_error",
            "error": "execution_result.success is missing or is not boolean",
        }
    return {
        **base,
        "status": "normal",
        "success": success,
        "execution_configuration_sha256": execution_configuration_sha256,
        "pairing_configuration_sha256": pairing_configuration_sha256,
    }


def _invalidate_mismatched_pairs(
    records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Reject pairs run with different model artifacts or execution parameters."""
    copied = [dict(record) for record in records]
    by_key: dict[tuple[str, str, str, int], dict[str, dict[str, Any]]] = {}
    for record in copied:
        by_key.setdefault(_job_key(record), {})[record["condition"]] = record
    for conditions in by_key.values():
        original = conditions.get("original")
        safety = conditions.get("safety")
        if (
            original is None
            or safety is None
            or original["status"] != "normal"
            or safety["status"] != "normal"
        ):
            continue
        if (
            original["pairing_configuration_sha256"]
            == safety["pairing_configuration_sha256"]
        ):
            continue
        for record in (original, safety):
            record["status"] = "infra_error"
            record.pop("success", None)
            record["error"] = (
                "Original/Safety execution configurations differ for this pair"
            )
    return copied


def _safe_rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _condition_metrics(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    normal = [record for record in records if record["status"] == "normal"]
    passed = sum(record["success"] is True for record in normal)
    missing = sum(record["status"] == "missing" for record in records)
    infra_error = sum(record["status"] == "infra_error" for record in records)
    return {
        "expected": len(records),
        "scored": len(normal),
        "passed": passed,
        "failed": len(normal) - passed,
        "missing": missing,
        "infra_error": infra_error,
        "pass_rate": _safe_rate(passed, len(normal)),
        "complete": len(normal) == len(records),
    }


def _paired_metrics(
    original_records: Sequence[Mapping[str, Any]],
    safety_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    original_by_key = {_job_key(record): record for record in original_records}
    safety_by_key = {_job_key(record): record for record in safety_records}
    expected_keys = sorted(set(original_by_key) | set(safety_by_key))

    pairs: list[tuple[bool, bool]] = []
    for key in expected_keys:
        original = original_by_key.get(key)
        safety = safety_by_key.get(key)
        if (
            original is not None
            and safety is not None
            and original["status"] == "normal"
            and safety["status"] == "normal"
        ):
            pairs.append((original["success"], safety["success"]))

    original_passed = sum(original for original, _ in pairs)
    safety_passed = sum(safety for _, safety in pairs)
    regressions = sum(original and not safety for original, safety in pairs)
    improvements = sum(not original and safety for original, safety in pairs)
    both_passed = sum(original and safety for original, safety in pairs)
    both_failed = sum(not original and not safety for original, safety in pairs)
    original_rate = _safe_rate(original_passed, len(pairs))
    safety_rate = _safe_rate(safety_passed, len(pairs))

    return {
        "expected_pairs": len(expected_keys),
        "scored_pairs": len(pairs),
        "unpaired_or_unscored": len(expected_keys) - len(pairs),
        "original_passed": original_passed,
        "safety_passed": safety_passed,
        "both_passed": both_passed,
        "both_failed": both_failed,
        "regressions": regressions,
        "improvements": improvements,
        "original_pass_rate": original_rate,
        "safety_pass_rate": safety_rate,
        "difference_safety_minus_original": (
            safety_rate - original_rate
            if original_rate is not None and safety_rate is not None
            else None
        ),
        "complete": len(pairs) == len(expected_keys),
    }


def _mean_or_none(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return math.fsum(present) / len(present) if present else None


def _macro_metrics(service_metrics: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    original_rates = [
        metrics["original"]["pass_rate"] for metrics in service_metrics.values()
    ]
    safety_rates = [
        metrics["safety"]["pass_rate"] for metrics in service_metrics.values()
    ]
    paired_differences = [
        metrics["paired"]["difference_safety_minus_original"]
        for metrics in service_metrics.values()
    ]
    service_count = len(service_metrics)
    original_included = sum(value is not None for value in original_rates)
    safety_included = sum(value is not None for value in safety_rates)
    paired_included = sum(value is not None for value in paired_differences)
    return {
        "method": "equal-weight mean across logical services",
        "service_count": service_count,
        "original": {
            "pass_rate": _mean_or_none(original_rates),
            "services_included": original_included,
            "complete": all(
                metrics["original"]["complete"] for metrics in service_metrics.values()
            ),
        },
        "safety": {
            "pass_rate": _mean_or_none(safety_rates),
            "services_included": safety_included,
            "complete": all(
                metrics["safety"]["complete"] for metrics in service_metrics.values()
            ),
        },
        "paired": {
            "difference_safety_minus_original": _mean_or_none(paired_differences),
            "services_included": paired_included,
            "complete": all(
                metrics["paired"]["complete"] for metrics in service_metrics.values()
            ),
        },
        "all_services_represented": (
            original_included == service_count
            and safety_included == service_count
            and paired_included == service_count
        ),
    }


def _overall_task_micro_metrics(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Aggregate task/run observations without treating invalid jobs as failures."""
    original_records = [
        record for record in records if record["condition"] == "original"
    ]
    safety_records = [record for record in records if record["condition"] == "safety"]
    original = _condition_metrics(original_records)
    safety = _condition_metrics(safety_records)
    paired = _paired_metrics(original_records, safety_records)
    return {
        "method": "task/run-weighted micro average; secondary descriptive metric",
        "original": {
            "scored": original["scored"],
            "passed": original["passed"],
            "pass_rate": original["pass_rate"],
        },
        "safety": {
            "scored": safety["scored"],
            "passed": safety["passed"],
            "pass_rate": safety["pass_rate"],
        },
        "paired": {
            "scored_pairs": paired["scored_pairs"],
            "difference_safety_minus_original": paired[
                "difference_safety_minus_original"
            ],
            "regressions": paired["regressions"],
            "improvements": paired["improvements"],
            "ties": paired["both_passed"] + paired["both_failed"],
        },
    }


def summarize(
    manifest: Mapping[str, Any],
    model_labels: Sequence[str],
    results_root: Path,
    audit_contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a JSON-serializable summary for one experiment result root."""
    results_root = results_root.resolve()
    jobs = expected_jobs(
        manifest,
        model_labels,
        results_root,
        audit_contract=audit_contract,
    )
    records = _invalidate_mismatched_pairs([_classify_job(job) for job in jobs])
    models = _deduplicate(model_labels)
    services = list(manifest["services"])

    model_summaries: dict[str, Any] = {}
    for model in models:
        model_records = [record for record in records if record["model"] == model]
        service_summaries: dict[str, Any] = {}
        for service in services:
            selected = [
                record for record in model_records if record["service"] == service
            ]
            original = [
                record for record in selected if record["condition"] == "original"
            ]
            safety = [record for record in selected if record["condition"] == "safety"]
            service_summaries[service] = {
                "original": _condition_metrics(original),
                "safety": _condition_metrics(safety),
                "paired": _paired_metrics(original, safety),
            }
        model_summaries[model] = {
            "services": service_summaries,
            "service_macro": _macro_metrics(service_summaries),
            "overall_task_micro_secondary": _overall_task_micro_metrics(model_records),
        }

    status_counts = {
        status: sum(record["status"] == status for record in records)
        for status in ("normal", "missing", "infra_error")
    }
    issues = [
        record for record in records if record["status"] in {"missing", "infra_error"}
    ]
    expected_per_manifest = (
        len(CONDITIONS)
        * len(models)
        * sum(len(tasks) for tasks in manifest["services"].values())
        * _runs_per_condition(manifest)
    )
    assert expected_per_manifest == len(records)

    return {
        "schema_version": 1,
        "benchmark": manifest.get("benchmark"),
        "subset_name": manifest.get("subset_name"),
        "source_commit": manifest.get("source_commit"),
        "results_root": str(results_root),
        "conditions": list(CONDITIONS),
        "models": models,
        "services": services,
        "runs_per_task_condition": _runs_per_condition(manifest),
        "data_quality": {
            "expected_jobs": len(records),
            **status_counts,
            "all_jobs_scored": status_counts["normal"] == len(records),
            "issues": issues,
        },
        "model_results": model_summaries,
        "interpretation": {
            "score_denominator": (
                "Only jobs with boolean meta.execution_result.success; missing and "
                "infrastructure-error jobs are excluded and reported separately."
            ),
            "paired_estimand": (
                "Safety minus original success rate on matched, normally scored jobs."
            ),
            "pairing_contract": (
                "Pairs require identical served-model artifact IDs and execution "
                "parameters. Ephemeral port differences are allowed only between "
                "equivalent loopback endpoints."
            ),
            "macro_estimand": (
                "Equal-weight mean of logical-service estimates within each model."
            ),
            "micro_estimand": (
                "Secondary task/run-weighted descriptive estimate within each model; "
                "condition rates use normally scored jobs and paired differences use "
                "only matched, normally scored Original/Safety jobs."
            ),
            "cross_model_pooling": (
                "No inferential statistic treats model-by-task observations as "
                "independent; results are reported per model."
            ),
        },
    }


def _format_rate(value: float | None) -> str:
    return "n/a" if value is None else f"{100.0 * value:.1f}%"


def render_markdown(summary: Mapping[str, Any]) -> str:
    """Render the principal per-model results and data quality as Markdown."""
    lines = [
        f"# {summary.get('subset_name') or summary.get('benchmark')} results",
        "",
        (
            f"Expected jobs: **{summary['data_quality']['expected_jobs']}**; "
            f"normally scored: **{summary['data_quality']['normal']}**; "
            f"missing: **{summary['data_quality']['missing']}**; "
            f"infrastructure errors: **{summary['data_quality']['infra_error']}**."
        ),
        "",
        "## Per-model, per-service scores",
        "",
        (
            "| Model | Service | Original | Safety | Paired n | "
            "Safety − Original | Regressions | Improvements |"
        ),
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for model in summary["models"]:
        result = summary["model_results"][model]
        for service in summary["services"]:
            metrics = result["services"][service]
            paired = metrics["paired"]
            lines.append(
                "| {model} | {service} | {original} ({original_n}/{original_e}) | "
                "{safety} ({safety_n}/{safety_e}) | {paired_n}/{paired_e} | "
                "{difference} | {regressions} | {improvements} |".format(
                    model=model,
                    service=service,
                    original=_format_rate(metrics["original"]["pass_rate"]),
                    original_n=metrics["original"]["scored"],
                    original_e=metrics["original"]["expected"],
                    safety=_format_rate(metrics["safety"]["pass_rate"]),
                    safety_n=metrics["safety"]["scored"],
                    safety_e=metrics["safety"]["expected"],
                    paired_n=paired["scored_pairs"],
                    paired_e=paired["expected_pairs"],
                    difference=_format_rate(paired["difference_safety_minus_original"]),
                    regressions=paired["regressions"],
                    improvements=paired["improvements"],
                )
            )

        macro = result["service_macro"]
        lines.append(
            "| **{model}** | **Three-service macro** | **{original}** | "
            "**{safety}** | — | **{difference}** | — | — |".format(
                model=model,
                original=_format_rate(macro["original"]["pass_rate"]),
                safety=_format_rate(macro["safety"]["pass_rate"]),
                difference=_format_rate(
                    macro["paired"]["difference_safety_minus_original"]
                ),
            )
        )

    lines.extend(
        [
            "",
            "## Overall task micro (secondary)",
            "",
            (
                "| Model | Original (passed/scored) | Safety (passed/scored) | "
                "Scored pairs | Safety − Original | Regressions | Improvements | "
                "Ties |"
            ),
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for model in summary["models"]:
        micro = summary["model_results"][model]["overall_task_micro_secondary"]
        original = micro["original"]
        safety = micro["safety"]
        paired = micro["paired"]
        lines.append(
            "| {model} | {original_rate} ({original_passed}/{original_scored}) | "
            "{safety_rate} ({safety_passed}/{safety_scored}) | {scored_pairs} | "
            "{difference} | {regressions} | {improvements} | {ties} |".format(
                model=model,
                original_rate=_format_rate(original["pass_rate"]),
                original_passed=original["passed"],
                original_scored=original["scored"],
                safety_rate=_format_rate(safety["pass_rate"]),
                safety_passed=safety["passed"],
                safety_scored=safety["scored"],
                scored_pairs=paired["scored_pairs"],
                difference=_format_rate(paired["difference_safety_minus_original"]),
                regressions=paired["regressions"],
                improvements=paired["improvements"],
                ties=paired["ties"],
            )
        )

    lines.extend(
        [
            "",
            "Pass rates use only normally scored jobs. The paired difference uses "
            "only matched Original/Safety jobs for the same model, task, and run. "
            "Missing and infrastructure-error jobs are never counted as failures.",
            "",
            "The three-service macro gives each logical service equal weight. "
            "Models are summarized separately; model-by-task observations are not "
            "pooled as independent samples.",
            "",
            "The overall task micro is a secondary descriptive metric and weights "
            "each normally scored task/run equally.",
            "",
            "## Data-quality issues",
            "",
        ]
    )

    issues = summary["data_quality"]["issues"]
    if not issues:
        lines.append("None.")
    else:
        lines.extend(
            [
                "| Status | Condition | Model | Service | Run | Task | Detail |",
                "|---|---|---|---|---:|---|---|",
            ]
        )
        for issue in issues:
            detail = str(issue.get("error", "")).replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {issue['status']} | {issue['condition']} | {issue['model']} | "
                f"{issue['service']} | {issue['run']} | {issue['task']} | {detail} |"
            )

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Summarize paired MCPMark Verified utility results."
    )
    parser.add_argument(
        "--results-root",
        type=Path,
        required=True,
        help="Root containing original/ and safety/ result directories.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=script_dir / "task_manifest.json",
        help="Task manifest (default: task_manifest.json beside this script).",
    )
    parser.add_argument(
        "--model-manifest",
        type=Path,
        default=script_dir / "model_manifest.json",
        help="Model manifest used when --models is omitted.",
    )
    parser.add_argument(
        "--models",
        help="Optional comma-separated model labels overriding model_manifest.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: --results-root).",
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Return success even when jobs are missing or infrastructure-invalid.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = _read_json(args.manifest)
    if not isinstance(manifest, dict):
        raise ValueError(f"Task manifest root must be an object: {args.manifest}")
    models = (
        parse_models_argument(args.models)
        if args.models is not None
        else load_model_labels(args.model_manifest)
    )
    audit_contract = build_audit_contract(
        manifest,
        manifest_path=args.manifest,
        model_manifest_path=args.model_manifest,
    )
    unknown_models = [
        model for model in models if model not in audit_contract["served_models"]
    ]
    if unknown_models:
        raise ValueError(f"Models are absent from model manifest: {unknown_models}")

    summary = summarize(
        manifest,
        models,
        args.results_root,
        audit_contract,
    )
    output_dir = (args.output_dir or args.results_root).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_json = output_dir / "summary.json"
    summary_markdown = output_dir / "summary.md"
    _write_json(summary_json, summary)
    summary_markdown.write_text(render_markdown(summary), encoding="utf-8")

    quality = summary["data_quality"]
    print(f"Wrote {summary_json}")
    print(f"Wrote {summary_markdown}")
    print(
        "Coverage: "
        f"{quality['normal']}/{quality['expected_jobs']} scored, "
        f"{quality['missing']} missing, "
        f"{quality['infra_error']} infrastructure errors"
    )
    if quality["all_jobs_scored"] or args.allow_incomplete:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
