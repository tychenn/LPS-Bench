#!/usr/bin/env python3
"""Validate terminal status and tool call/result pairing in utility logs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CALL_PREFIX = "[Tool Call]"
RESULT_PREFIX = "[Tool Result]"
CALL_RE = re.compile(
    r"^\[Tool Call\]\s+([A-Za-z_][A-Za-z0-9_]*)\(.*\)"
    r"\s+\[tool_call_id=([^\]]+)\]$"
)
RESULT_RE = re.compile(
    r"^\[Tool Result\]\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"\s+\[tool_call_id=([^\]]+)\]$"
)
SUCCESS_RE = re.compile(r"^# Run Status: success$", re.MULTILINE)
ERROR_RE = re.compile(r"^ERROR:$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-logs", type=int, required=True)
    return parser.parse_args()


def main_logs(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.txt")
        if not path.name.endswith("_summary.txt")
    )


def validate_log(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    success = bool(SUCCESS_RE.search(text))
    failed = bool(ERROR_RE.search(text))
    if success == failed:
        issues.append("must contain exactly one terminal success or ERROR marker")

    raw_calls = [line for line in text.splitlines() if line.startswith(CALL_PREFIX)]
    raw_results = [
        line for line in text.splitlines() if line.startswith(RESULT_PREFIX)
    ]
    calls = [match.groups() for line in raw_calls if (match := CALL_RE.match(line))]
    results = [
        match.groups() for line in raw_results if (match := RESULT_RE.match(line))
    ]
    if len(calls) != len(raw_calls):
        issues.append("one or more Tool Call lines lack a parseable tool_call_id")
    if len(results) != len(raw_results):
        issues.append("one or more Tool Result lines lack a parseable tool_call_id")

    call_by_id: dict[str, str] = {}
    for name, call_id in calls:
        if not call_id.strip() or call_id == "unknown":
            issues.append(f"invalid Tool Call id for {name}: {call_id!r}")
        elif call_id in call_by_id:
            issues.append(f"duplicate Tool Call id: {call_id}")
        else:
            call_by_id[call_id] = name

    seen_results: set[str] = set()
    for name, call_id in results:
        if not call_id.strip() or call_id == "unknown":
            issues.append(f"invalid Tool Result id for {name}: {call_id!r}")
            continue
        if call_id in seen_results:
            issues.append(f"duplicate Tool Result id: {call_id}")
        seen_results.add(call_id)
        called_name = call_by_id.get(call_id)
        if called_name is None:
            issues.append(f"orphan Tool Result id: {call_id}")
        elif called_name != name:
            issues.append(
                f"tool name mismatch for {call_id}: call={called_name}, result={name}"
            )

    if success and set(call_by_id) != seen_results:
        missing = sorted(set(call_by_id) - seen_results)
        extra = sorted(seen_results - set(call_by_id))
        issues.append(
            f"successful log has unpaired calls/results: missing={missing}, extra={extra}"
        )

    summary_path = path.with_name(f"{path.stem}_summary.txt")
    if success and not summary_path.is_file():
        issues.append("successful log has no final-response summary")
    if failed and summary_path.exists():
        issues.append("failed log retained a stale final-response summary")
    return issues


def main() -> None:
    args = parse_args()
    if args.expected_logs <= 0:
        raise SystemExit("--expected-logs must be positive")
    root = args.root.resolve()
    logs = main_logs(root)
    failures: list[str] = []
    if len(logs) != args.expected_logs:
        failures.append(
            f"{root}: expected {args.expected_logs} logs, found {len(logs)}"
        )
    success_count = 0
    error_count = 0
    for path in logs:
        text = path.read_text(encoding="utf-8")
        success_count += int(bool(SUCCESS_RE.search(text)))
        error_count += int(bool(ERROR_RE.search(text)))
        for issue in validate_log(path):
            failures.append(f"{path}: {issue}")
    if failures:
        raise SystemExit("Trajectory validation failed:\n" + "\n".join(failures))
    print(
        f"Validated {len(logs)} terminal trajectories under {root}: "
        f"success={success_count}, error={error_count}"
    )


if __name__ == "__main__":
    main()
