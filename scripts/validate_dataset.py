#!/usr/bin/env python3
"""Check that published cases can resolve their tools, evaluators, and skills."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_DIRS = (
    ROOT / "examples",
    ROOT / "utility_cases/lps_bench_derived/cases",
    ROOT / "candidate_cases",
)
BENIGN_RISKS = {"TS", "OC", "FA", "IP"}
ADVERSARIAL_RISKS = {"HS", "MT", "EB", "RC", "PI"}


def defined_functions(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def uses_host_files_without_sandbox(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    if "_bind_mock_runtime" in source:
        return False
    tree = ast.parse(source, filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        name = function.id if isinstance(function, ast.Name) else None
        if isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name):
            name = f"{function.value.id}.{function.attr}"
        if name in {"open", "os.makedirs", "os.remove", "os.rename", "shutil.rmtree", "shutil.move", "shutil.copy2"}:
            return True
    return False


def validate() -> tuple[int, list[str]]:
    errors: list[str] = []
    count = 0
    main_counts: Counter[str] = Counter()
    function_cache: dict[Path, set[str]] = {}
    case_records: list[tuple[Path, dict]] = []
    for case_dir in CASE_DIRS:
        for path in sorted(case_dir.rglob("*.json")):
            count += 1
            try:
                case = json.loads(path.read_text(encoding="utf-8"))
                case_records.append((path, case))
                if not isinstance(case["instruction"], str) or not case["instruction"].strip():
                    raise ValueError("empty instruction")
                if case_dir == ROOT / "examples":
                    risk = path.stem.split("_", 1)[0]
                    is_skill = "_skill_" in path.stem
                    intent = "benign" if is_skill or risk in BENIGN_RISKS else "adversarial"
                    if risk not in BENIGN_RISKS | ADVERSARIAL_RISKS:
                        raise ValueError(f"unknown risk {risk}")
                    expected_meta = {
                        "case_id": f"{path.parent.name}_{path.stem}",
                        "domain": path.parent.name,
                        "risk_type": risk,
                        "user_intent": intent,
                    }
                    for key, expected in expected_meta.items():
                        if case.get("meta", {}).get(key) != expected:
                            errors.append(f"{path}: meta.{key} must be {expected!r}")
                    if is_skill and risk == "PI" and case.get("meta", {}).get("attack_source") != "skill_body":
                        errors.append(f"{path}: PI-Skill attack_source must be skill_body")
                    main_counts["skill" if is_skill else intent] += 1
                for section, default_dir, names_key in (
                    ("MCP", ROOT / "tools", "tools"),
                    ("evaluator", ROOT / "evaluator", "func"),
                ):
                    config = case[section]
                    configured = Path(config["file"])
                    target = configured if configured.is_absolute() else ROOT / configured
                    if not target.is_file():
                        target = default_dir / configured.name
                    if not target.is_file():
                        errors.append(f"{path}: missing {section} file {config['file']}")
                        continue
                    if target not in function_cache:
                        function_cache[target] = defined_functions(target)
                        if section == "MCP" and uses_host_files_without_sandbox(target):
                            errors.append(f"{target}: host file access lacks mock sandbox binding")
                    for name in config[names_key]:
                        if name not in function_cache[target]:
                            errors.append(f"{path}: {target} does not define {name}")
                mcp_names = set(case["MCP"]["tools"])
                for skill in case.get("skills", {}).get("available", []):
                    entry = ROOT / skill["bundle"]["entry"]
                    if not entry.is_file():
                        errors.append(f"{path}: missing skill entry {entry}")
                    for name in skill.get("bound_mcp_tools", []):
                        if name not in mcp_names:
                            errors.append(f"{path}: skill binds undeclared tool {name}")
                pair = case.get("meta", {}).get("paired_case_id")
                if pair:
                    domain = case["meta"]["domain"]
                    prefix = f"{domain}_"
                    pair_name = pair[len(prefix):] if pair.startswith(prefix) else pair
                    if "/" in pair:
                        pair_path = ROOT / "examples" / f"{pair}.json"
                    else:
                        pair_path = ROOT / "examples" / domain / f"{pair_name}.json"
                    if not pair_path.is_file():
                        errors.append(f"{path}: missing paired case {pair}")
            except (OSError, SyntaxError, ValueError, KeyError, TypeError) as exc:
                errors.append(f"{path}: {exc}")
    # A criterion naming a tool from another case can silently make its safe
    # path impossible. Restrict this check to quoted, function-shaped names;
    # project IDs and payload fields are deliberately excluded.
    all_tool_names = {
        name for _, case in case_records for name in case["MCP"]["tools"]
    }
    for path, case in case_records:
        quoted_names = set(re.findall(
            r"['\"`]([a-z][a-z0-9]*(?:_[a-z0-9]+)+)['\"`]",
            case["evaluator"]["criterion"],
        ))
        own_tools = set(case["MCP"]["tools"])
        tool_source = ROOT / "tools" / Path(case["MCP"]["file"]).name
        source_text = tool_source.read_text(encoding="utf-8") if tool_source.is_file() else ""
        for name in sorted(quoted_names & all_tool_names - own_tools):
            if name not in source_text and name not in case["instruction"]:
                errors.append(f"{path}: criterion names unavailable tool {name}")
    expected_counts = {"benign": 252, "adversarial": 318, "skill": 40}
    if dict(main_counts) != expected_counts:
        errors.append(f"examples/ counts {dict(main_counts)} differ from paper {expected_counts}")
    manifest_path = ROOT / "utility_cases/lps_bench_derived/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest["cases"]:
        for hash_key, path_key in (
            ("derived_case_sha256", "derived_case"),
            ("dedicated_tool_copy_sha256", "dedicated_tool_copy"),
        ):
            target = ROOT / row[path_key]
            if hashlib.sha256(target.read_bytes()).hexdigest() != row[hash_key]:
                errors.append(f"{target}: {hash_key} differs from utility manifest")
    return count, errors


if __name__ == "__main__":
    case_count, problems = validate()
    for problem in problems:
        print(problem)
    print(f"Checked {case_count} cases; {len(problems)} problem(s).")
    raise SystemExit(bool(problems))
