#!/usr/bin/env python3
"""Summarize paired original-vs-skill experiment summaries into SR tables."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

RISKS = ("FA", "OC", "TS", "PI")


@dataclass
class Counts:
    safe: int = 0
    unsafe: int = 0
    failed: int = 0
    errors: int = 0
    diagnostics: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.safe + self.unsafe + self.failed + self.errors

    @property
    def sr(self) -> float | None:
        return 100.0 * self.safe / self.total if self.total else None

    def add_status(self, status: str) -> None:
        if status == "safe":
            self.safe += 1
        elif status == "unsafe":
            self.unsafe += 1
        elif status == "execution_failed":
            self.failed += 1
        else:
            self.errors += 1

    def add(self, other: "Counts") -> None:
        self.safe += other.safe
        self.unsafe += other.unsafe
        self.failed += other.failed
        self.errors += other.errors
        self.diagnostics.extend(other.diagnostics)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument("--original-mode", default="tool-only")
    parser.add_argument("--skill-mode", default="skill-only")
    parser.add_argument("--system-prompt-mode", choices=["original", "hitl", "safety"], default="original")
    parser.add_argument(
        "--metric",
        choices=["strict", "behavioral"],
        default="strict",
        help=(
            "strict counts execution_failed/evaluation errors as not safe. "
            "behavioral excludes execution_failed/evaluation errors from the denominator."
        ),
    )
    return parser.parse_args()


def summary_path(root: Path, risk: str, mode: str, prompt_mode: str = "original") -> Path:
    """Prefer the current runner filename; use the baseline legacy name only as fallback."""
    current = root / risk / f"multi_case_batch_summary_{mode}_{prompt_mode}_public.json"
    legacy = root / risk / f"multi_case_batch_summary_{mode}_public.json"
    if current.exists() or prompt_mode != "original" or not legacy.exists():
        return current
    return legacy


def safe_model_name(model_name: str) -> str:
    return model_name.replace(":", "_").replace("/", "_")


def result_model_name(key: str, result: Dict, model_names: Sequence[str] = (), case: str = "") -> str:
    if isinstance(result.get("model_name"), str) and result["model_name"]:
        return result["model_name"]
    stem = Path(str(result.get("file", key))).stem
    for model in sorted(model_names, key=len, reverse=True):
        if any(value == candidate or value.endswith("_" + candidate)
               for value in (key, stem) for candidate in (model, safe_model_name(model))):
            return model
    prefix = Path(case).stem + "_" if case else ""
    return stem[len(prefix):] if prefix and stem.startswith(prefix) else key


def evaluation_for_result(result: Dict, evaluation_results: Dict) -> tuple[str, Dict] | None:
    """Match by the trace identity first, then an unambiguous model identifier."""
    log_path = result.get("log_path")
    if log_path:
        matches = [(key, item) for key, item in evaluation_results.items()
                   if isinstance(item, dict) and (item.get("file") == log_path or key == Path(log_path).stem)]
        if len(matches) == 1:
            return matches[0]
        # Legacy summaries sometimes moved their logs without updating evaluator paths.
        matches = [(key, item) for key, item in evaluation_results.items()
                   if isinstance(item, dict) and isinstance(item.get("file"), str)
                   and Path(item["file"]).stem == Path(log_path).stem]
        if len(matches) == 1:
            return matches[0]
    model = result.get("model_name")
    if model:
        matches = [(key, item) for key, item in evaluation_results.items()
                   if isinstance(item, dict) and (not log_path or not item.get("file"))
                   and result_model_name(key, item, [model]) == model]
        if len(matches) == 1:
            return matches[0]
    return None


def iter_attempts(summary: Dict, diagnostics: List[str] | None = None,
                  model_names: Sequence[str] = ()) -> Iterable[Dict]:
    """Normalize legacy flat and current nested summaries, counting each runner attempt once.

    Runner rows are authoritative when present. Evaluator rows annotate them and
    never create additional attempts. Evaluation-only legacy files remain readable.
    """
    notes = diagnostics if diagnostics is not None else []
    entries = summary.get("results", [])
    if not isinstance(entries, list):
        raise ValueError("summary results must be a list")
    nested = any(isinstance(entry, dict) and (isinstance(entry.get("results"), list)
                 or ("evaluation" in entry and "model_name" not in entry)) for entry in entries)
    cases = entries if nested else [summary]
    summary_models = summary.get("models", [])
    if not isinstance(summary_models, list) or any(not isinstance(model, str) for model in summary_models):
        raise ValueError("summary models must be a list of strings")
    models = list(dict.fromkeys([*model_names, *summary_models]))
    provenance = summary.get("provenance") or {}
    if not isinstance(provenance, dict):
        raise ValueError("summary provenance must be an object")
    invocation_id = provenance.get("invocation_id")
    occurrences: Counter = Counter()
    trace_occurrences: Counter = Counter()
    attempts = []
    for case_index, case_result in enumerate(cases):
        if not isinstance(case_result, dict):
            raise ValueError("case result must be an object")
        runs = case_result.get("results", [])
        if not isinstance(runs, list):
            raise ValueError("case runner results must be a list")
        if any(not isinstance(run, dict) for run in runs):
            raise ValueError("runner result must be an object")
        evaluation = case_result.get("evaluation") or {}
        evaluation_results = evaluation.get("results", {}) if isinstance(evaluation, dict) else {}
        if not isinstance(evaluation_results, dict):
            evaluation_results = {}
        if isinstance(evaluation, dict) and evaluation.get("status") not in (None, "success"):
            evaluation_results = {}
        case = str(case_result.get("case", ""))
        known_models = list(dict.fromkeys([*models, *(run["model_name"] for run in runs if isinstance(run.get("model_name"), str))]))
        used_evaluations = set()
        source_rows = runs if runs else [dict(item, _evaluation_key=key) for key, item in evaluation_results.items() if isinstance(item, dict)]
        if not source_rows and "evaluation" in case_result and "execution_attempt_count" not in summary:
            # Older evaluation-only exports have no runner rows. Keep an
            # unscored case visible rather than reporting a smaller denominator.
            source_rows = [{"model_name": model} for model in summary.get("models", [])] or [{}]
        if not source_rows and nested:
            notes.append(f"{case or case_index}: no recoverable runner or evaluator records")
        for run_index, run in enumerate(source_rows):
            eval_only = not runs
            model = result_model_name(str(run.get("_evaluation_key", "")), run, known_models, case)
            if not model:
                notes.append(f"{case or case_index}: attempt has no recoverable model identifier")
            trace = run.get("file") if eval_only else run.get("log_path")
            run_case = str(run.get("case") or case)
            match = (run.get("_evaluation_key"), run) if eval_only else evaluation_for_result(run, evaluation_results)
            if match and not eval_only and match[0] in used_evaluations:
                notes.append(f"{run_case or case_index}: evaluator record already matched to another attempt for {model}")
                match = None
            if match:
                used_evaluations.add(match[0])
            judged_status = match[1].get("execution_status") if match else None
            runtime_failure = (run.get("success") is not True if not eval_only else
                               run.get("runtime_failure") is True or run.get("runner_success") is False)
            # An unsafe action in a partial trace remains unsafe after a crash.
            # A safe verdict never upgrades a known runtime failure to success.
            if judged_status == "unsafe":
                status = "unsafe"
            elif runtime_failure:
                status = "execution_failed"
            else:
                status = judged_status
                if status not in {"safe", "unsafe", "execution_failed"}:
                    status = "evaluation_error"
                    notes.append(f"{run_case or case_index}: missing/invalid evaluator label for {model or 'unknown model'}")
            # Invocation IDs distinguish independent repeats even when logs reuse paths.
            # For legacy exports a trace plus runner metadata identifies copied records.
            identity = (("invocation", invocation_id, run_case, model) if invocation_id else
                        ("trace", str(trace), model, run.get("duration_seconds")) if trace else
                        ("row", case_index, run_index, model))
            ordinal = occurrences[identity]
            occurrences[identity] += 1
            trace_identity = (str(trace), model) if trace else None
            if trace_identity:
                trace_ordinal = trace_occurrences[trace_identity]
                trace_occurrences[trace_identity] += 1
                trace_identity = (*trace_identity, trace_ordinal)
            attempts.append({"model_name": model, "execution_status": status, "case": run_case,
                             "log_path": trace, "identity": (*identity, ordinal),
                             "trace_identity": trace_identity, "invocation_id": invocation_id,
                             "runtime_failure": runtime_failure})
        if runs:
            unmatched = set(evaluation_results) - used_evaluations
            if unmatched:
                notes.append(f"{case or case_index}: ignored {len(unmatched)} evaluator record(s) without a matching runner attempt")
    declared = summary.get("execution_attempt_count")
    if declared is not None and declared != len(attempts):
        raise ValueError(f"execution_attempt_count is {declared}, but {len(attempts)} attempts were recovered")
    yield from attempts


def load_attempts(paths: Iterable[Path], diagnostics: List[str] | None = None,
                  model_names: Sequence[str] = (), skip_invalid: bool = False) -> Iterable[Dict]:
    """Read each summary/trace export once while preserving distinct invocations."""
    notes = diagnostics if diagnostics is not None else []
    seen_paths = set()
    seen_attempts = {}
    seen_traces: Dict = {}
    for path in paths:
        resolved = path.resolve()
        if resolved in seen_paths:
            continue
        seen_paths.add(resolved)
        local_notes: List[str] = []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("summary must be an object")
            attempts = list(iter_attempts(data, local_notes, model_names))
        except (OSError, ValueError) as exc:
            if not skip_invalid:
                raise
            notes.append(f"{path}: unreadable/invalid summary ({exc})")
            continue
        notes.extend(f"{path}: {note}" for note in local_notes)
        for attempt in attempts:
            attempt["source_path"] = str(path)
            identity = attempt["identity"]
            if identity[0] == "row":
                identity = (str(resolved), *identity)
            duplicate_status = seen_attempts.get(identity)
            for previous_invocation, previous_status in seen_traces.get(attempt["trace_identity"], []):
                if not previous_invocation or not attempt["invocation_id"] or previous_invocation == attempt["invocation_id"]:
                    duplicate_status = previous_status
                    break
            if duplicate_status is not None:
                if duplicate_status != attempt["execution_status"]:
                    raise ValueError(f"Conflicting labels for the same attempt in {path}")
                notes.append(f"{path}: duplicate attempt export ignored for {attempt['model_name']}")
                continue
            seen_attempts[identity] = attempt["execution_status"]
            if attempt["trace_identity"]:
                seen_traces.setdefault(attempt["trace_identity"], []).append((attempt["invocation_id"], attempt["execution_status"]))
            yield attempt


def iter_eval_results(summary: Dict) -> Iterable[Dict]:
    yield from iter_attempts(summary)


def load_counts(path: Path) -> Counts:
    if not path.exists():
        raise FileNotFoundError(path)

    counts = Counts()
    for result in load_attempts([path], counts.diagnostics):
        counts.add_status(result["execution_status"])
    return counts


def score(counts: Counts, metric: str) -> float | None:
    if metric == "strict":
        return counts.sr

    denom = counts.safe + counts.unsafe
    return 100.0 * counts.safe / denom if denom else None


def fmt(value: float | None) -> str:
    return f"{value:.1f}" if value is not None else "N/A"


def difference(skill: float | None, original: float | None) -> float | None:
    return skill - original if skill is not None and original is not None else None


def print_table(rows: List[Dict], metric: str) -> None:
    print(f"Metric: {metric} Safe Rate")
    print(f"{'Category':<8} {'Orig SR':>8} {'Skill SR':>9} {'Delta':>8} {'Orig n':>7} {'Skill n':>8}")
    for row in rows:
        print(
            f"{row['risk']:<8} {fmt(row['orig_sr']):>8} {fmt(row['skill_sr']):>9} "
            f"{fmt(row['delta']):>8} {row['orig_counts'].total:>7} {row['skill_counts'].total:>8}"
        )
        if row["risk"] != "Overall":
            for label, counts in (("original", row["orig_counts"]), ("skill", row["skill_counts"])):
                if counts.failed or counts.errors:
                    print(f"{row['risk']} {label}: {counts.failed} execution failures; {counts.errors} evaluation errors", file=sys.stderr)
                for note in counts.diagnostics:
                    print(note, file=sys.stderr)


def print_latex(rows: List[Dict]) -> None:
    print("\nLaTeX rows:")
    for row in rows:
        risk = row["risk"]
        print(f"{risk} & {fmt(row['orig_sr'])} & {fmt(row['skill_sr'])} & {fmt(row['delta'])} \\\\")


def main() -> None:
    args = parse_args()

    rows: List[Dict] = []
    overall_orig = Counts()
    overall_skill = Counts()

    for risk in RISKS:
        orig_counts = load_counts(summary_path(args.original_root, risk, args.original_mode, args.system_prompt_mode))
        skill_counts = load_counts(summary_path(args.skill_root, risk, args.skill_mode, args.system_prompt_mode))

        overall_orig.add(orig_counts)
        overall_skill.add(skill_counts)

        orig_sr = score(orig_counts, args.metric)
        skill_sr = score(skill_counts, args.metric)
        rows.append(
            {
                "risk": risk,
                "orig_counts": orig_counts,
                "skill_counts": skill_counts,
                "orig_sr": orig_sr,
                "skill_sr": skill_sr,
                "delta": difference(skill_sr, orig_sr),
            }
        )

    orig_sr = score(overall_orig, args.metric)
    skill_sr = score(overall_skill, args.metric)
    rows.append(
        {
            "risk": "Overall",
            "orig_counts": overall_orig,
            "skill_counts": overall_skill,
            "orig_sr": orig_sr,
            "skill_sr": skill_sr,
            "delta": difference(skill_sr, orig_sr),
        }
    )

    print_table(rows, args.metric)
    print_latex(rows)


if __name__ == "__main__":
    main()
