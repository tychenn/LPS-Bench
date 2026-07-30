#!/usr/bin/env python3
"""Validate schema, provenance, interfaces, and isolation of the utility set."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TRACING"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = REPO_ROOT / "utility_cases" / "lps_bench_derived"
SCHEMA_PATH = REPO_ROOT / "schemas" / "lps_case_v2.schema.json"
STATE_PATHS = (
    REPO_ROOT / "fs_state.json",
    REPO_ROOT / "sim_state.json",
    REPO_ROOT / "simulated_multimedia_env",
    Path("/tmp/hft_simulation_env"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DATASET_ROOT)
    parser.add_argument(
        "--report",
        type=Path,
        default=DATASET_ROOT / "validation" / "full_validation_report.json",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_state(path: Path) -> Any:
    if not path.exists():
        return None
    if path.is_file():
        return {"type": "file", "sha256": sha256_file(path)}
    return {
        "type": "directory",
        "files": {
            str(child.relative_to(path)): sha256_file(child)
            for child in sorted(path.rglob("*"))
            if child.is_file()
        },
    }


def load_module(path: Path) -> Any:
    module_name = f"_lps_utility_validation_{path.stem}_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


def tool_args_schema(tool_obj: Any) -> dict[str, Any]:
    args = getattr(tool_obj, "args", None)
    if isinstance(args, dict):
        return args
    schema = getattr(tool_obj, "args_schema", None)
    if schema is not None:
        if hasattr(schema, "model_json_schema"):
            return schema.model_json_schema()
        if hasattr(schema, "schema"):
            return schema.schema()
    return {}


def example_value(schema: dict[str, Any]) -> Any:
    if "default" in schema:
        return schema["default"]
    if schema.get("enum"):
        return schema["enum"][0]
    for union_key in ("anyOf", "oneOf"):
        options = schema.get(union_key)
        if isinstance(options, list):
            usable = [option for option in options if option.get("type") != "null"]
            if usable:
                return example_value(usable[0])
    value_type = schema.get("type", "string")
    if value_type == "integer":
        return max(1, int(schema.get("minimum", 1)))
    if value_type == "number":
        return max(1.0, float(schema.get("minimum", 1.0)))
    if value_type == "boolean":
        return False
    if value_type == "array":
        return [example_value(schema.get("items", {"type": "string"}))]
    if value_type == "object":
        return {}
    return "utility_test"


def example_tool_arguments(tool_obj: Any) -> dict[str, Any]:
    schema = tool_args_schema(tool_obj)
    properties = schema.get("properties") if "properties" in schema else schema
    if not isinstance(properties, dict):
        return {}
    return {
        name: example_value(value_schema)
        for name, value_schema in properties.items()
        if isinstance(value_schema, dict)
    }


def capture_invocation(tool_obj: Any, arguments: dict[str, Any]) -> tuple[str, str]:
    try:
        result = tool_obj.invoke(arguments)
        return "return", repr(result)
    except Exception as exc:  # noqa: BLE001
        return "exception", f"{type(exc).__name__}: {exc}"


def validate_identifier_integrity(dataset_root: Path) -> dict[str, int]:
    """Guard identifiers that must remain distinct while staying deterministic."""
    image_module_path = dataset_root / "tools" / "multi_media_u_eb_01.py"
    image_modules = (load_module(image_module_path), load_module(image_module_path))
    filenames = (
        "landscape_01.jpg",
        "portrait_02.jpg",
        "event_03.jpg",
        "vip_donor_04.jpg",
        "crowd_05.jpg",
    )
    image_runs: list[list[str]] = []
    for module in image_modules:
        outputs = [
            str(module.load_image_to_memory.invoke({"filename": filename}))
            for filename in filenames
        ]
        identifiers = []
        for output in outputs:
            match = re.search(r"\bIMG_\d+\b", output)
            if match is None:
                raise AssertionError(f"Image buffer ID missing from output: {output}")
            identifiers.append(match.group(0))
        image_runs.append(identifiers)
    if image_runs[0] != image_runs[1]:
        raise AssertionError(
            f"Image buffer IDs differ across fresh imports: {image_runs}"
        )
    if len(set(image_runs[0])) != len(filenames):
        raise AssertionError(f"Distinct images share buffer IDs: {image_runs[0]}")
    histogram = str(
        image_modules[0].analyze_image_histogram.invoke(
            {"buffer_id": image_runs[0][0]}
        )
    )
    if image_runs[0][0] not in histogram:
        raise AssertionError(
            f"Image buffer ID was not preserved downstream: {histogram}"
        )

    session_module = load_module(
        dataset_root / "tools" / "social_media_u_fa_01.py"
    )
    sessions = session_module.list_active_sessions.invoke(
        {"account_id": "acc_8823_us"}
    )
    session_ids = [item.get("session_id") for item in sessions]
    expected_session_ids = ["sess_001", "sess_002", "sess_003"]
    if session_ids != expected_session_ids:
        raise AssertionError(
            "Security-session identifiers were altered or merged: "
            f"{session_ids} != {expected_session_ids}"
        )
    termination = str(
        session_module.terminate_session.invoke(
            {"session_id": "sess_003", "force_logout": "true"}
        )
    )
    if "sess_003" not in termination:
        raise AssertionError(
            f"Target session ID was not preserved downstream: {termination}"
        )

    archive_module_path = dataset_root / "tools" / "social_media_u_oc_01.py"
    archive_modules = (load_module(archive_module_path), load_module(archive_module_path))
    comment_ids = ("cmt_a1", "cmt_b2")
    archive_runs: list[list[str]] = []
    for module in archive_modules:
        outputs = [
            str(
                module.archive_moderation_evidence.invoke(
                    {
                        "content_id": comment_id,
                        "reason": "policy evidence",
                        "raw_content": "captured customer-service comment",
                    }
                )
            )
            for comment_id in comment_ids
        ]
        identifiers = []
        for output in outputs:
            match = re.search(r"\bREF_[0-9a-fA-F]{8}\b", output)
            if match is None:
                raise AssertionError(f"Archive reference missing from output: {output}")
            identifiers.append(match.group(0))
        archive_runs.append(identifiers)
    if archive_runs[0] != archive_runs[1]:
        raise AssertionError(
            f"Archive references differ across fresh imports: {archive_runs}"
        )
    if len(set(archive_runs[0])) != len(comment_ids):
        raise AssertionError(
            f"Distinct evidence archives share references: {archive_runs[0]}"
        )

    return {
        "session_ids_preserved": len(session_ids),
        "unique_image_buffer_ids": len(set(image_runs[0])),
        "unique_archive_references": len(set(archive_runs[0])),
    }


def validate(dataset_root: Path) -> dict[str, Any]:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    manifest_path = dataset_root / "manifest.json"
    selection_path = dataset_root / "source_selection.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_validator = Draft202012Validator(schema)

    entries = manifest["cases"]
    if len(entries) != 56 or manifest.get("case_count") != 56:
        raise AssertionError("Manifest must contain exactly 56 cases")
    if manifest.get("tool_copy_count") != 56:
        raise AssertionError("Manifest must contain 56 dedicated tool copies")
    if len(selection.get("cases", [])) != 56:
        raise AssertionError("Source selection must contain 56 mappings")

    case_paths = sorted((dataset_root / "cases").glob("*/*.json"))
    tool_paths = sorted((dataset_root / "tools").glob("*_u_*_01.py"))
    if len(case_paths) != 56:
        raise AssertionError(f"Expected 56 case JSON files, found {len(case_paths)}")
    if len(tool_paths) != 56:
        raise AssertionError(f"Expected 56 copied tool files, found {len(tool_paths)}")

    expected_case_paths = {entry["derived_case"] for entry in entries}
    expected_tool_paths = {entry["dedicated_tool_copy"] for entry in entries}
    if len(expected_case_paths) != 56 or len(expected_tool_paths) != 56:
        raise AssertionError("Each case must map to a unique case file and unique tool copy")
    if expected_case_paths != {str(path.relative_to(REPO_ROOT)) for path in case_paths}:
        raise AssertionError("Manifest/case file set mismatch")
    if expected_tool_paths != {str(path.relative_to(REPO_ROOT)) for path in tool_paths}:
        raise AssertionError("Manifest/tool-copy file set mismatch")

    state_before = {str(path): path_state(path) for path in STATE_PATHS}
    schema_validated = 0
    interfaces_validated = 0
    neutralized_invocations = 0
    override_invocations = 0
    fresh_imports_validated = 0
    deterministic_tool_invocations = 0

    for entry in entries:
        case_path = REPO_ROOT / entry["derived_case"]
        tool_copy_path = REPO_ROOT / entry["dedicated_tool_copy"]
        source_case_path = REPO_ROOT / entry["source_case"]
        source_tool_path = REPO_ROOT / entry["source_tool"]

        if sha256_file(source_case_path) != entry["source_case_sha256"]:
            raise AssertionError(f"Source case changed: {source_case_path}")
        if sha256_file(source_tool_path) != entry["source_tool_sha256"]:
            raise AssertionError(f"Source tool changed: {source_tool_path}")
        if sha256_file(case_path) != entry["derived_case_sha256"]:
            raise AssertionError(f"Derived case hash mismatch: {case_path}")
        if sha256_file(tool_copy_path) != entry["dedicated_tool_copy_sha256"]:
            raise AssertionError(f"Tool copy hash mismatch: {tool_copy_path}")

        source_bytes = source_tool_path.read_bytes()
        copied_bytes = tool_copy_path.read_bytes()
        if not copied_bytes.startswith(source_bytes.rstrip(b"\n") + b"\n"):
            raise AssertionError(f"Tool copy does not preserve its source prefix: {tool_copy_path}")

        case = json.loads(case_path.read_text(encoding="utf-8"))
        errors = sorted(schema_validator.iter_errors(case), key=lambda error: list(error.path))
        if errors:
            rendered = "; ".join(
                f"{'/'.join(map(str, error.path))}: {error.message}" for error in errors
            )
            raise AssertionError(f"Schema failure in {case_path}: {rendered}")
        schema_validated += 1

        if case["meta"]["case_id"] != entry["case_id"]:
            raise AssertionError(f"Case ID mismatch in {case_path}")
        if case["meta"]["user_intent"] != "benign":
            raise AssertionError(f"Utility case is not marked benign: {case_path}")
        if case["meta"]["capability_surface"] != "mcp_only":
            raise AssertionError(f"Utility case must be MCP-only: {case_path}")
        if case["MCP"]["file"] != entry["dedicated_tool_copy"]:
            raise AssertionError(f"Case does not point to its dedicated tool copy: {case_path}")

        source_case = json.loads(source_case_path.read_text(encoding="utf-8"))
        if case["MCP"]["tools"] != source_case["MCP"]["tools"]:
            raise AssertionError(f"Configured tool interface changed: {case_path}")
        expected_pair = f"{entry['domain']}/{Path(entry['source_case']).stem}"
        if case["meta"]["paired_case_id"] != expected_pair:
            raise AssertionError(f"Source pairing mismatch: {case_path}")

        compile(
            tool_copy_path.read_text(encoding="utf-8"),
            str(tool_copy_path),
            "exec",
        )
        source_module = load_module(source_tool_path)
        derived_module_a = load_module(tool_copy_path)
        derived_module_b = load_module(tool_copy_path)

        for tool_name in case["MCP"]["tools"]:
            source_tool = getattr(source_module, tool_name)
            derived_tool_a = getattr(derived_module_a, tool_name)
            derived_tool_b = getattr(derived_module_b, tool_name)
            if getattr(source_tool, "name", None) != getattr(derived_tool_a, "name", None):
                raise AssertionError(f"Tool name changed: {entry['case_id']}::{tool_name}")
            if tool_args_schema(source_tool) != tool_args_schema(derived_tool_a):
                raise AssertionError(f"Argument schema changed: {entry['case_id']}::{tool_name}")
            if derived_tool_a is derived_tool_b:
                raise AssertionError(f"Fresh imports share tool objects: {entry['case_id']}::{tool_name}")

            arguments = example_tool_arguments(derived_tool_a)
            result_a = capture_invocation(derived_tool_a, arguments)
            result_b = capture_invocation(derived_tool_b, arguments)
            if result_a != result_b:
                raise AssertionError(
                    "Tool output differs across fresh deterministic imports: "
                    f"{entry['case_id']}::{tool_name}\nA={result_a}\nB={result_b}"
                )
            interfaces_validated += 1
            deterministic_tool_invocations += 1
        fresh_imports_validated += 1

        for tool_name in entry["neutralized_tools"]:
            result = getattr(derived_module_a, tool_name).func()
            if "UTILITY_CASE_DISABLED" not in str(result) or "no state was changed" not in str(result):
                raise AssertionError(
                    f"Neutralized tool is not side-effect-free: {entry['case_id']}::{tool_name}"
                )
            neutralized_invocations += 1

        for tool_name in entry["deterministic_output_overrides"]:
            result_a = getattr(derived_module_a, tool_name).func()
            result_b = getattr(derived_module_b, tool_name).func()
            if result_a != result_b or not str(result_a).strip():
                raise AssertionError(
                    f"Output override is not deterministic: {entry['case_id']}::{tool_name}"
                )
            override_invocations += 1

    identifier_checks = validate_identifier_integrity(dataset_root)

    state_after = {str(path): path_state(path) for path in STATE_PATHS}
    if state_before != state_after:
        changed = [
            path for path in state_before if state_before[path] != state_after[path]
        ]
        raise AssertionError(f"Validation/imports changed mock filesystem state: {changed}")

    expected_distribution = json.loads(
        (dataset_root / "validation" / "expected_distribution.json").read_text(
            encoding="utf-8"
        )
    )
    distribution = manifest["distribution"]
    if distribution["total_cases"] != expected_distribution["total_cases"]:
        raise AssertionError("Total distribution mismatch")
    for key in ("by_domain", "by_source_risk", "by_impact", "per_domain_impact"):
        if distribution[key] != expected_distribution[key]:
            raise AssertionError(f"Distribution mismatch for {key}")

    original_prompt = (dataset_root / "prompts" / "original_prompt.txt").read_text(
        encoding="utf-8"
    )
    safety_prompt = (dataset_root / "prompts" / "safety_prompt.txt").read_text(
        encoding="utf-8"
    )
    if not original_prompt.strip() or not safety_prompt.strip():
        raise AssertionError("Both prompt conditions require non-empty prompt files")
    if original_prompt == safety_prompt:
        raise AssertionError("Original and safety prompt conditions must differ")

    return {
        "status": "passed",
        "dataset_root": str(dataset_root.relative_to(REPO_ROOT)),
        "checks": {
            "case_count": len(case_paths),
            "dedicated_tool_copy_count": len(tool_paths),
            "schema_validated_cases": schema_validated,
            "tool_interfaces_validated": interfaces_validated,
            "fresh_module_imports_validated": fresh_imports_validated,
            "deterministic_tool_invocations": deterministic_tool_invocations,
            "neutralized_tool_invocations": neutralized_invocations,
            "deterministic_override_invocations": override_invocations,
            "source_hashes_unchanged": True,
            "source_tool_prefixes_preserved": True,
            "configured_tool_lists_preserved": True,
            "state_paths_unchanged": True,
            "distribution_exact": True,
            "paired_prompt_files_present": True,
            **identifier_checks,
        },
    }


def main() -> None:
    args = parse_args()
    report = validate(args.dataset_root.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
