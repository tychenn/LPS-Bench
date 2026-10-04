import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import estimate_failure_aware_sr as failure_aware
from scripts import summarize_skill_experiment as summary
from scripts import summarize_skill_experiment_modelwise as modelwise


def runner(model, success=True, trace=None, case="examples/webbrowser/FA_1.json"):
    result = {"model_name": model, "success": success, "case": case}
    if trace:
        result["log_path"] = trace
    return result


def evaluated_case(runs, labels=None, status="success"):
    evaluations = {}
    for run, label in zip(runs, labels or []):
        if label is None:
            continue
        key = Path(run.get("log_path", "case_" + summary.safe_model_name(run["model_name"]))).stem
        evaluations[key] = {"model_name": run["model_name"], "execution_status": label}
        if run.get("log_path"):
            evaluations[key]["file"] = run["log_path"]
    return {"case": "examples/webbrowser/FA_1.json", "results": runs,
            "evaluation": {"status": status, "results": evaluations}}


def current_summary(cases, invocation=None):
    data = {"results": cases, "execution_attempt_count": sum(len(case["results"]) for case in cases)}
    if invocation:
        data["provenance"] = {"invocation_id": invocation}
    return data


class SummaryScriptsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_strict_counts_runner_failures_once_without_judge_results(self):
        runs = [runner("a"), runner("b", False), runner("c", False)]
        path = self.write("summary.json", current_summary([evaluated_case(runs, ["safe"])]))
        counts = summary.load_counts(path)
        self.assertEqual((counts.safe, counts.failed, counts.errors, counts.total), (1, 2, 0, 3))
        self.assertAlmostEqual(summary.score(counts, "strict"), 100 / 3)
        self.assertEqual(summary.score(counts, "behavioral"), 100)
        by_model = modelwise.load_counts_by_model(path)
        self.assertEqual(sum(item.total for item in by_model.values()), 3)
        self.assertEqual(by_model["b"].failed, 1)

    def test_failed_runner_and_its_judge_record_are_one_attempt(self):
        runs = [runner("qwen3:8b", False, "/logs/failed.txt")]
        path = self.write("summary.json", current_summary([evaluated_case(runs, ["safe"])]))
        counts = summary.load_counts(path)
        self.assertEqual((counts.safe, counts.failed, counts.total), (0, 1, 1))
        self.assertEqual(modelwise.load_counts_by_model(path)["qwen3:8b"].total, 1)

    def test_unsafe_action_before_crash_remains_unsafe_once(self):
        runs = [runner("qwen3:8b", False, "/logs/unsafe_then_crashed.txt")]
        case = evaluated_case(runs, ["unsafe"])
        record = next(iter(case["evaluation"]["results"].values()))
        record.update(runner_success=False, runtime_failure=True)
        path = self.write("multi_case_batch_summary_hybrid_original_public.json", current_summary([case]))
        counts = summary.load_counts(path)
        self.assertEqual((counts.unsafe, counts.failed, counts.total), (1, 0, 1))
        self.assertEqual(summary.score(counts, "behavioral"), 0)
        by_model = modelwise.load_counts_by_model(path)["qwen3:8b"]
        self.assertEqual((by_model.unsafe, by_model.failed, by_model.total), (1, 0, 1))
        result = next(item for item in failure_aware.analyze_records(self.root)["results"]
                      if item["model"] == "Qwen3-8B-Instruct")
        self.assertEqual((result["recoverable_counts"]["unsafe"], result["recoverable_counts"]["total"]), (1, 1))

    def test_evaluation_only_runtime_metadata_cannot_turn_a_crash_safe(self):
        data = {"results": [{"evaluation": {"status": "success", "results": {
            "FA_1_qwen3_8b": {"model_name": "qwen3:8b", "execution_status": "safe",
                               "runner_success": False, "runtime_failure": True}}}}]}
        counts = summary.load_counts(self.write("evaluation_only.json", data))
        self.assertEqual((counts.safe, counts.failed, counts.total), (0, 1, 1))

    def test_missing_judge_label_stays_in_strict_denominator(self):
        runs = [runner("a", trace="/logs/a.txt"), runner("b", trace="/logs/b.txt")]
        path = self.write("summary.json", current_summary([evaluated_case(runs, ["safe", None])]))
        counts = summary.load_counts(path)
        self.assertEqual((counts.safe, counts.errors, counts.total), (1, 1, 2))
        self.assertEqual(summary.score(counts, "strict"), 50)
        self.assertTrue(any("missing/invalid" in note for note in counts.diagnostics))
        self.assertEqual(modelwise.load_counts_by_model(path)["b"].errors, 1)

    def test_batch_judge_error_counts_each_model(self):
        runs = [runner("a"), runner("b")]
        path = self.write("summary.json", current_summary([evaluated_case(runs, status="error")]))
        counts = summary.load_counts(path)
        self.assertEqual((counts.errors, counts.total), (2, 2))
        by_model = modelwise.load_counts_by_model(path)
        self.assertEqual(by_model["a"].errors, 1)
        self.assertEqual(by_model["b"].errors, 1)
        self.assertIsNone(summary.score(counts, "behavioral"))

    def test_stale_evaluator_trace_does_not_score_a_different_attempt(self):
        run = runner("qwen3:8b", trace="/logs/current_qwen3_8b.txt")
        case = evaluated_case([run])
        case["evaluation"]["results"] = {
            "stale_qwen3_8b": {"file": "/logs/stale_qwen3_8b.txt", "execution_status": "safe"}}
        counts = summary.load_counts(self.write("summary.json", current_summary([case])))
        self.assertEqual((counts.safe, counts.errors, counts.total), (0, 1, 1))

    def test_evaluator_without_runner_does_not_create_extra_attempts(self):
        case = evaluated_case([runner("a", trace="/logs/a.txt")], ["safe"])
        case["evaluation"]["results"]["orphan"] = {"execution_status": "safe"}
        counts = summary.load_counts(self.write("summary.json", current_summary([case])))
        self.assertEqual(counts.total, 1)
        self.assertTrue(any("without a matching runner" in note for note in counts.diagnostics))

    def test_one_judge_record_cannot_score_two_runner_attempts(self):
        runs = [runner("qwen3:8b"), runner("qwen3:8b")]
        path = self.write("summary.json", current_summary([evaluated_case(runs, ["safe"])]))
        counts = summary.load_counts(path)
        self.assertEqual((counts.safe, counts.errors, counts.total), (1, 1, 2))
        self.assertEqual(summary.score(counts, "strict"), 50)
        self.assertTrue(any("already matched" in note for note in counts.diagnostics))

    def test_legacy_flat_and_evaluation_only_formats(self):
        flat = evaluated_case([runner("qwen3:8b", trace="/logs/FA_1_qwen3_8b.txt")], ["unsafe"])
        flat_path = self.write("flat.json", flat)
        self.assertEqual(summary.load_counts(flat_path).unsafe, 1)
        self.assertEqual(modelwise.load_counts_by_model(flat_path)["qwen3:8b"].unsafe, 1)
        eval_only = {"results": [{"case": "examples/webbrowser/FA_1.json", "evaluation": {
            "status": "success", "results": {"FA_1_qwen3_8b": {"execution_status": "safe"}}}}]}
        path = self.write("evaluation_only.json", eval_only)
        self.assertEqual(summary.load_counts(path).safe, 1)
        self.assertEqual(modelwise.load_counts_by_model(path, ["qwen3:8b"])["qwen3:8b"].safe, 1)

    def test_legacy_evaluation_error_is_visible_without_runner_metadata(self):
        data = {"results": [{"case": "FA_1.json", "evaluation": {"status": "error"}}]}
        counts = summary.load_counts(self.write("error.json", data))
        self.assertEqual((counts.errors, counts.total), (1, 1))
        self.assertTrue(counts.diagnostics)

    def test_custom_model_without_log_uses_unambiguous_evaluator_model(self):
        name = "custom/model:v2"
        case = evaluated_case([runner(name)])
        case["evaluation"]["results"] = {
            "FA_1_custom_model_v2": {"execution_status": "safe"}}
        path = self.write("custom.json", current_summary([case]))
        self.assertEqual(modelwise.load_counts_by_model(path, [name])[name].safe, 1)

    def test_current_filename_has_priority_and_legacy_is_supported(self):
        legacy = self.write("FA/multi_case_batch_summary_tool-only_public.json", {})
        self.assertEqual(summary.summary_path(self.root, "FA", "tool-only"), legacy)
        current = self.write("FA/multi_case_batch_summary_tool-only_original_public.json", {})
        self.assertEqual(summary.summary_path(self.root, "FA", "tool-only"), current)
        self.assertEqual(modelwise.summary_path(self.root, "FA", "tool-only"), current)
        self.assertEqual(summary.summary_path(self.root, "FA", "tool-only", "safety").name,
                         "multi_case_batch_summary_tool-only_safety_public.json")

    def test_duplicate_exports_and_repeated_roots_are_not_counted_twice(self):
        case = evaluated_case([runner("qwen3:8b", trace="/logs/qwen3.txt")], ["safe"])
        first = self.write("a.json", current_summary([case], "same-invocation"))
        copy = self.write("b.json", current_summary([case], "same-invocation"))
        flat = self.write("legacy.json", case)
        counts = modelwise.merge_counts_by_model([first, first, copy, flat])
        self.assertEqual(counts["qwen3:8b"].total, 1)

    def test_independent_repeats_and_repeated_case_entries_remain_attempts(self):
        case = evaluated_case([runner("qwen3:8b", trace="/logs/qwen3.txt")], ["safe"])
        first = self.write("a.json", current_summary([case], "invocation-a"))
        second = self.write("b.json", current_summary([case], "invocation-b"))
        self.assertEqual(modelwise.merge_counts_by_model([first, second])["qwen3:8b"].total, 2)
        repeated = self.write("repeat.json", current_summary([case, case], "invocation-c"))
        self.assertEqual(summary.load_counts(repeated).total, 2)

    def test_conflicting_duplicate_labels_are_rejected(self):
        first_case = evaluated_case([runner("qwen3:8b", trace="/logs/qwen3.txt")], ["safe"])
        second_case = evaluated_case([runner("qwen3:8b", trace="/logs/qwen3.txt")], ["unsafe"])
        first = self.write("a.json", current_summary([first_case], "same"))
        second = self.write("b.json", current_summary([second_case], "same"))
        with self.assertRaisesRegex(ValueError, "Conflicting labels"):
            modelwise.merge_counts_by_model([first, second])

    def test_declared_attempt_count_mismatch_is_rejected(self):
        data = current_summary([evaluated_case([runner("a")], ["safe"])])
        data["execution_attempt_count"] = 2
        with self.assertRaisesRegex(ValueError, "execution_attempt_count"):
            summary.load_counts(self.write("mismatch.json", data))

    def test_modelwise_missing_data_is_na_without_a_fabricated_zero_average(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["summary", "--original-root", str(self.root),
                          "--skill-root", str(self.root), "--model", "custom=custom:model"]), contextlib.redirect_stdout(output):
            modelwise.main()
        self.assertIn("N/A", output.getvalue())
        self.assertIn("missing: FA, OC, TS, PI", output.getvalue())
        self.assertNotIn("0.0", output.getvalue())

    def test_skill_cli_reads_current_filenames_and_reports_execution_failures(self):
        runs = [runner("a"), runner("b", False), runner("c", False)]
        for risk in summary.RISKS:
            self.write(f"original/{risk}/multi_case_batch_summary_tool-only_original_public.json",
                       current_summary([evaluated_case(runs, ["safe"])]))
            self.write(f"skill/{risk}/multi_case_batch_summary_skill-only_original_public.json",
                       current_summary([evaluated_case([runner("a")], ["safe"])]))
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["summary", "--original-root", str(self.root / "original"),
                          "--skill-root", str(self.root / "skill")]), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            summary.main()
        self.assertIn("33.3", output.getvalue())
        self.assertIn("100.0", output.getvalue())
        self.assertIn("2 execution failures", errors.getvalue())

    def test_failure_aware_reads_flat_and_nested_and_deduplicates_exports(self):
        safe_case = evaluated_case([runner("qwen3:8b", trace="/logs/safe.txt")], ["safe"])
        unsafe_case = evaluated_case([runner("qwen3:8b", trace="/logs/unsafe.txt")], ["unsafe"])
        self.write("webbrowser/FA_1_batch_summary.json", safe_case)
        self.write("multi_case_batch_summary_tool-only_original_public.json",
                   current_summary([safe_case, unsafe_case], "invocation"))
        payload = failure_aware.analyze_records(self.root)
        result = next(item for item in payload["results"] if item["model"] == "Qwen3-8B-Instruct")
        self.assertEqual(result["recoverable_counts"]["total"], 2)
        self.assertEqual(result["recoverable_subset_metrics_pct"]["strict_sr"], 50)
        self.assertEqual(result["recoverable_domain_counts"], {"webbrowser": 2})
        self.assertTrue(any("duplicate" in note for note in payload["diagnostics"]))

    def test_failure_aware_all_failed_returns_null_with_diagnostic(self):
        runs = [runner("qwen3:8b", False, "/logs/one.txt"), runner("qwen3:8b", False, "/logs/two.txt")]
        self.write("multi_case_batch_summary_tool-only_original_public.json",
                   current_summary([evaluated_case(runs)]))
        payload = failure_aware.analyze_records(self.root)
        result = next(item for item in payload["results"] if item["model"] == "Qwen3-8B-Instruct")
        self.assertEqual(result["recoverable_counts"]["total"], 2)
        self.assertEqual(result["recoverable_subset_metrics_pct"]["execution_failure_rate"], 100)
        self.assertIsNone(result["recoverable_subset_metrics_pct"]["failure_excluded_sr"])
        self.assertIsNone(result["published_and_sensitivity_estimate_pct"]["estimated_failure_excluded_sr"])
        self.assertIsNone(result["published_and_sensitivity_estimate_pct"]["change_pp"])
        self.assertTrue(any("100% execution failures" in note for note in payload["diagnostics"]))

    def test_failure_aware_missing_evaluation_is_separate_and_estimate_withheld(self):
        runs = [runner("qwen3:8b", trace="/logs/one.txt"), runner("qwen3:8b", trace="/logs/two.txt")]
        self.write("multi_case_batch_summary_hybrid_original_public.json",
                   current_summary([evaluated_case(runs, ["safe", None])]))
        payload = failure_aware.analyze_records(self.root)
        result = next(item for item in payload["results"] if item["model"] == "Qwen3-8B-Instruct")
        self.assertEqual(result["recoverable_counts"]["evaluation_error"], 1)
        self.assertEqual(result["recoverable_counts"]["total"], 2)
        self.assertEqual(result["recoverable_subset_metrics_pct"]["strict_sr"], 50)
        self.assertIsNone(result["published_and_sensitivity_estimate_pct"]["estimated_failure_excluded_sr"])

    def test_failure_aware_unreadable_summary_is_diagnosed(self):
        path = self.root / "bad_batch_summary.json"
        path.write_text("{bad-json", encoding="utf-8")
        payload = failure_aware.analyze_records(self.root)
        self.assertTrue(any("unreadable/invalid" in note for note in payload["diagnostics"]))


if __name__ == "__main__":
    unittest.main()
