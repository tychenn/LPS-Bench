import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "summarize_results.py"
SPEC = importlib.util.spec_from_file_location("summarize_results", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
summarize_results = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summarize_results)

TEST_RUNTIME_CONFIGURATION = {
    "temperature": 0.0,
    "max_tokens": 32768,
    "max_turns": 100,
    "timeout": 3600,
    "compaction_token": 999_999_999,
    "reasoning_effort": "default",
}
TEST_PROMPT_HASHES = {
    "original": "1" * 64,
    "safety": "2" * 64,
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_meta(
    path: Path,
    value: object,
    *,
    condition: str,
    model: str,
    service: str,
    mcp: str,
    task: str,
    audit_contract: dict,
    run: int = 1,
    runner_status: str = "normal",
    base_url: str = "http://127.0.0.1:11434/v1",
    model_artifact_id: str = "a" * 12,
) -> None:
    if isinstance(value, dict):
        upstream_value = {
            "task_name": task.replace("/", "__"),
            "model_name": model,
            "reasoning_effort": audit_contract["runtime_configuration"][
                "reasoning_effort"
            ],
            "mcp": mcp,
            "timeout": audit_contract["runtime_configuration"]["timeout"],
            **value,
        }
    else:
        upstream_value = value
    write_json(path, upstream_value)
    execution_configuration = {
        "model_label": model,
        "served_model": audit_contract["served_models"][model],
        "model_artifact_id": model_artifact_id,
        "base_url": base_url,
        **audit_contract["runtime_configuration"],
    }
    write_json(
        path.with_name("experiment_meta.json"),
        {
            "condition": condition,
            "model_label": model,
            "logical_service": service,
            "mcp": mcp,
            "task": task,
            "run": run,
            "source_commit": audit_contract["source_commit"],
            "manifest_sha256": audit_contract["manifest_sha256"],
            "model_manifest_sha256": audit_contract["model_manifest_sha256"],
            "safety_prompt_sha256": audit_contract["safety_prompt_sha256"],
            "upstream_system_prompt_sha256": audit_contract[
                "upstream_system_prompt_sha256"
            ],
            "effective_system_prompt_sha256": audit_contract[
                "effective_system_prompt_sha256"
            ][condition],
            **execution_configuration,
            "execution_configuration_sha256": summarize_results._sha256_json(
                execution_configuration
            ),
            "upstream_meta_sha256": summarize_results._sha256_file(path),
            "prompt_verified_model_calls": 1,
            "runner_status": runner_status,
            "infrastructure_error": (
                "synthetic infrastructure failure"
                if runner_status == "infra_error"
                else None
            ),
        },
    )


def make_audit_contract(*models: str) -> dict:
    return {
        "source_commit": "test-commit",
        "manifest_sha256": "3" * 64,
        "model_manifest_sha256": "4" * 64,
        "safety_prompt_sha256": "5" * 64,
        "upstream_system_prompt_sha256": TEST_PROMPT_HASHES["original"],
        "effective_system_prompt_sha256": dict(TEST_PROMPT_HASHES),
        "runtime_configuration": dict(TEST_RUNTIME_CONFIGURATION),
        "served_models": {model: f"served/{model}" for model in models},
    }


def make_manifest() -> dict:
    return {
        "benchmark": "MCPMark Verified",
        "subset_name": "Test subset",
        "source_commit": "test-commit",
        "prompt_conditions": {
            "original": {
                "effective_system_prompt_sha256": TEST_PROMPT_HASHES["original"],
            },
            "safety": {
                "safety_prompt_sha256": "5" * 64,
                "effective_system_prompt_sha256": TEST_PROMPT_HASHES["safety"],
            },
        },
        "runtime_configuration": dict(TEST_RUNTIME_CONFIGURATION),
        "services": {
            "filesystem": [
                {"mcp": "filesystem", "task": "desktop/project_management"},
                {"mcp": "filesystem", "task": "papers/author_folders"},
            ],
            "playwright": [
                {
                    "mcp": "playwright",
                    "task": "eval_web/extraction_table",
                }
            ],
        },
        "evaluation_design": {"runs_per_task_condition": 1},
    }


def meta_path(root: Path, condition: str, model: str, service: str, task: str) -> Path:
    return (
        root
        / condition
        / f"{model}__{service}"
        / "run-1"
        / task.replace("/", "__")
        / "meta.json"
    )


class SummarizeResultsTests(unittest.TestCase):
    def test_expected_jobs_use_logical_service_and_manifest_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            jobs = summarize_results.expected_jobs(make_manifest(), ["model_a"], root)

        self.assertEqual(len(jobs), 6)
        playwright = next(
            job
            for job in jobs
            if job["mcp"] == "playwright" and job["condition"] == "original"
        )
        self.assertIn("model_a__playwright", str(playwright["meta_path"]))
        self.assertTrue(
            str(playwright["meta_path"]).endswith(
                "eval_web__extraction_table/meta.json"
            )
        )

    def test_missing_and_infra_are_separate_and_not_scored(self) -> None:
        manifest = make_manifest()
        audit_contract = make_audit_contract("model_a")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            # One normal pass, one malformed execution result, and four missing jobs.
            write_meta(
                meta_path(
                    root,
                    "original",
                    "model_a",
                    "filesystem",
                    "desktop/project_management",
                ),
                {"execution_result": {"success": True}},
                condition="original",
                model="model_a",
                service="filesystem",
                mcp="filesystem",
                task="desktop/project_management",
                audit_contract=audit_contract,
            )
            write_meta(
                meta_path(
                    root,
                    "original",
                    "model_a",
                    "filesystem",
                    "papers/author_folders",
                ),
                {"execution_result": {"success": "true"}},
                condition="original",
                model="model_a",
                service="filesystem",
                mcp="filesystem",
                task="papers/author_folders",
                audit_contract=audit_contract,
            )
            summary = summarize_results.summarize(
                manifest,
                ["model_a"],
                root,
                audit_contract,
            )

        quality = summary["data_quality"]
        self.assertEqual(quality["expected_jobs"], 6)
        self.assertEqual(quality["normal"], 1)
        self.assertEqual(quality["infra_error"], 1)
        self.assertEqual(quality["missing"], 4)
        filesystem = summary["model_results"]["model_a"]["services"]["filesystem"]
        self.assertEqual(filesystem["original"]["scored"], 1)
        self.assertEqual(filesystem["original"]["passed"], 1)
        self.assertEqual(filesystem["original"]["pass_rate"], 1.0)
        self.assertEqual(filesystem["paired"]["scored_pairs"], 0)
        self.assertIsNone(filesystem["paired"]["difference_safety_minus_original"])
        micro = summary["model_results"]["model_a"]["overall_task_micro_secondary"]
        self.assertEqual(micro["original"]["scored"], 1)
        self.assertEqual(micro["original"]["passed"], 1)
        self.assertEqual(micro["original"]["pass_rate"], 1.0)
        self.assertEqual(micro["safety"]["scored"], 0)
        self.assertEqual(micro["safety"]["passed"], 0)
        self.assertIsNone(micro["safety"]["pass_rate"])
        self.assertEqual(micro["paired"]["scored_pairs"], 0)
        self.assertIsNone(micro["paired"]["difference_safety_minus_original"])
        self.assertEqual(micro["paired"]["regressions"], 0)
        self.assertEqual(micro["paired"]["improvements"], 0)
        self.assertEqual(micro["paired"]["ties"], 0)

    def test_equal_service_macro_differs_from_unbalanced_task_micro(self) -> None:
        manifest = make_manifest()
        audit_contract = make_audit_contract("model_a")
        outcomes = {
            # Filesystem original=2/2, safety=1/2, paired delta=-0.5.
            ("original", "filesystem", "desktop/project_management"): True,
            ("safety", "filesystem", "desktop/project_management"): False,
            ("original", "filesystem", "papers/author_folders"): True,
            ("safety", "filesystem", "papers/author_folders"): True,
            # Playwright original=0/1, safety=1/1, paired delta=+1.0.
            ("original", "playwright", "eval_web/extraction_table"): False,
            ("safety", "playwright", "eval_web/extraction_table"): True,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for (condition, service, task), success in outcomes.items():
                write_meta(
                    meta_path(root, condition, "model_a", service, task),
                    {"execution_result": {"success": success}},
                    condition=condition,
                    model="model_a",
                    service=service,
                    mcp=service,
                    task=task,
                    audit_contract=audit_contract,
                )
            summary = summarize_results.summarize(
                manifest,
                ["model_a"],
                root,
                audit_contract,
            )

        model = summary["model_results"]["model_a"]
        filesystem = model["services"]["filesystem"]
        self.assertEqual(filesystem["paired"]["difference_safety_minus_original"], -0.5)
        self.assertEqual(filesystem["paired"]["regressions"], 1)
        playwright = model["services"]["playwright"]
        self.assertEqual(playwright["paired"]["difference_safety_minus_original"], 1.0)
        self.assertEqual(playwright["paired"]["improvements"], 1)

        macro = model["service_macro"]
        # Equal-service, not task-weighted: mean(1.0, 0.0) = 0.5.
        self.assertEqual(macro["original"]["pass_rate"], 0.5)
        # Equal-service: mean(0.5, 1.0) = 0.75.
        self.assertEqual(macro["safety"]["pass_rate"], 0.75)
        # Equal-service paired delta: mean(-0.5, +1.0) = +0.25.
        self.assertEqual(macro["paired"]["difference_safety_minus_original"], 0.25)
        self.assertTrue(macro["all_services_represented"])

        micro = model["overall_task_micro_secondary"]
        # Task-weighted across the unbalanced 2-task/1-task services.
        self.assertEqual(micro["original"]["scored"], 3)
        self.assertEqual(micro["original"]["passed"], 2)
        self.assertAlmostEqual(micro["original"]["pass_rate"], 2 / 3)
        self.assertEqual(micro["safety"]["scored"], 3)
        self.assertEqual(micro["safety"]["passed"], 2)
        self.assertAlmostEqual(micro["safety"]["pass_rate"], 2 / 3)
        self.assertNotEqual(
            macro["original"]["pass_rate"],
            micro["original"]["pass_rate"],
        )
        self.assertNotEqual(
            macro["safety"]["pass_rate"],
            micro["safety"]["pass_rate"],
        )
        self.assertEqual(micro["paired"]["scored_pairs"], 3)
        self.assertEqual(
            micro["paired"]["difference_safety_minus_original"],
            0.0,
        )
        self.assertEqual(micro["paired"]["regressions"], 1)
        self.assertEqual(micro["paired"]["improvements"], 1)
        self.assertEqual(micro["paired"]["ties"], 1)
        self.assertNotEqual(
            macro["paired"]["difference_safety_minus_original"],
            micro["paired"]["difference_safety_minus_original"],
        )

        markdown = summarize_results.render_markdown(summary)
        self.assertIn("Overall task micro (secondary)", markdown)
        self.assertIn(
            "| model_a | 66.7% (2/3) | 66.7% (2/3) | 3 | 0.0% | 1 | 1 | 1 |",
            markdown,
        )

    def test_models_are_kept_separate(self) -> None:
        manifest = {
            **make_manifest(),
            "services": {
                "filesystem": [
                    {"mcp": "filesystem", "task": "desktop/project_management"}
                ]
            },
        }
        audit_contract = make_audit_contract("model_pass", "model_fail")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for condition in ("original", "safety"):
                write_meta(
                    meta_path(
                        root,
                        condition,
                        "model_pass",
                        "filesystem",
                        "desktop/project_management",
                    ),
                    {"execution_result": {"success": True}},
                    condition=condition,
                    model="model_pass",
                    service="filesystem",
                    mcp="filesystem",
                    task="desktop/project_management",
                    audit_contract=audit_contract,
                )
                write_meta(
                    meta_path(
                        root,
                        condition,
                        "model_fail",
                        "filesystem",
                        "desktop/project_management",
                    ),
                    {"execution_result": {"success": False}},
                    condition=condition,
                    model="model_fail",
                    service="filesystem",
                    mcp="filesystem",
                    task="desktop/project_management",
                    audit_contract=audit_contract,
                )
            summary = summarize_results.summarize(
                manifest,
                ["model_pass", "model_fail"],
                root,
                audit_contract,
            )

        self.assertEqual(
            summary["model_results"]["model_pass"]["service_macro"]["original"][
                "pass_rate"
            ],
            1.0,
        )
        self.assertEqual(
            summary["model_results"]["model_fail"]["service_macro"]["original"][
                "pass_rate"
            ],
            0.0,
        )
        self.assertNotIn("overall_pass_rate", summary)

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            results_root = root / "results"
            manifest_path = root / "task_manifest.json"
            model_manifest_path = root / "model_manifest.json"
            output_dir = root / "reports"
            write_json(manifest_path, make_manifest())
            write_json(
                model_manifest_path,
                {
                    "models": [
                        {
                            "label": "model_a",
                            "served_model": "served/model_a",
                        }
                    ]
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--results-root",
                    str(results_root),
                    "--manifest",
                    str(manifest_path),
                    "--model-manifest",
                    str(model_manifest_path),
                    "--output-dir",
                    str(output_dir),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertTrue((output_dir / "summary.json").is_file())
            markdown = (output_dir / "summary.md").read_text(encoding="utf-8")
            self.assertIn("Per-model, per-service scores", markdown)
            self.assertIn("infrastructure errors", markdown)
            document = json.loads(
                (output_dir / "summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(document["data_quality"]["expected_jobs"], 6)

    def test_tampered_meta_hash_is_rejected(self) -> None:
        manifest = {
            **make_manifest(),
            "services": {
                "filesystem": [
                    {"mcp": "filesystem", "task": "desktop/project_management"}
                ]
            },
        }
        audit_contract = make_audit_contract("model_a")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = meta_path(
                root,
                "original",
                "model_a",
                "filesystem",
                "desktop/project_management",
            )
            write_meta(
                path,
                {"execution_result": {"success": True}},
                condition="original",
                model="model_a",
                service="filesystem",
                mcp="filesystem",
                task="desktop/project_management",
                audit_contract=audit_contract,
            )
            write_json(path, {"execution_result": {"success": False}})
            summary = summarize_results.summarize(
                manifest,
                ["model_a"],
                root,
                audit_contract,
            )

        self.assertEqual(summary["data_quality"]["normal"], 0)
        self.assertEqual(summary["data_quality"]["infra_error"], 1)
        self.assertIn(
            "SHA-256",
            summary["data_quality"]["issues"][0]["error"],
        )

    def test_pair_with_different_ephemeral_loopback_ports_is_accepted(self) -> None:
        manifest = {
            **make_manifest(),
            "services": {
                "filesystem": [
                    {"mcp": "filesystem", "task": "desktop/project_management"}
                ]
            },
        }
        audit_contract = make_audit_contract("model_a")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for condition, base_url in (
                ("original", "http://127.0.0.1:11434/v1"),
                ("safety", "http://127.0.0.1:22434/v1"),
            ):
                write_meta(
                    meta_path(
                        root,
                        condition,
                        "model_a",
                        "filesystem",
                        "desktop/project_management",
                    ),
                    {"execution_result": {"success": True}},
                    condition=condition,
                    model="model_a",
                    service="filesystem",
                    mcp="filesystem",
                    task="desktop/project_management",
                    audit_contract=audit_contract,
                    base_url=base_url,
                )
            summary = summarize_results.summarize(
                manifest,
                ["model_a"],
                root,
                audit_contract,
            )

        self.assertEqual(summary["data_quality"]["normal"], 2)
        self.assertEqual(summary["data_quality"]["infra_error"], 0)

    def test_pair_with_different_remote_endpoints_is_rejected(self) -> None:
        manifest = {
            **make_manifest(),
            "services": {
                "filesystem": [
                    {"mcp": "filesystem", "task": "desktop/project_management"}
                ]
            },
        }
        audit_contract = make_audit_contract("model_a")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for condition, base_url in (
                ("original", "https://api-a.example/v1"),
                ("safety", "https://api-b.example/v1"),
            ):
                write_meta(
                    meta_path(
                        root,
                        condition,
                        "model_a",
                        "filesystem",
                        "desktop/project_management",
                    ),
                    {"execution_result": {"success": True}},
                    condition=condition,
                    model="model_a",
                    service="filesystem",
                    mcp="filesystem",
                    task="desktop/project_management",
                    audit_contract=audit_contract,
                    base_url=base_url,
                )
            summary = summarize_results.summarize(
                manifest,
                ["model_a"],
                root,
                audit_contract,
            )

        self.assertEqual(summary["data_quality"]["normal"], 0)
        self.assertEqual(summary["data_quality"]["infra_error"], 2)

    def test_pair_with_different_model_artifacts_is_rejected(self) -> None:
        manifest = {
            **make_manifest(),
            "services": {
                "filesystem": [
                    {"mcp": "filesystem", "task": "desktop/project_management"}
                ]
            },
        }
        audit_contract = make_audit_contract("model_a")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for condition, artifact in (
                ("original", "a" * 12),
                ("safety", "b" * 12),
            ):
                write_meta(
                    meta_path(
                        root,
                        condition,
                        "model_a",
                        "filesystem",
                        "desktop/project_management",
                    ),
                    {"execution_result": {"success": True}},
                    condition=condition,
                    model="model_a",
                    service="filesystem",
                    mcp="filesystem",
                    task="desktop/project_management",
                    audit_contract=audit_contract,
                    model_artifact_id=artifact,
                )
            summary = summarize_results.summarize(
                manifest,
                ["model_a"],
                root,
                audit_contract,
            )

        self.assertEqual(summary["data_quality"]["normal"], 0)
        self.assertEqual(summary["data_quality"]["infra_error"], 2)

    def test_attempted_job_without_meta_is_infrastructure_error(self) -> None:
        manifest = {
            **make_manifest(),
            "services": {
                "filesystem": [
                    {"mcp": "filesystem", "task": "desktop/project_management"}
                ]
            },
        }
        audit_contract = make_audit_contract("model_a")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = meta_path(
                root,
                "original",
                "model_a",
                "filesystem",
                "desktop/project_management",
            )
            write_json(
                path.with_name("experiment_meta.json"),
                {
                    "condition": "original",
                    "model_label": "model_a",
                    "logical_service": "filesystem",
                    "mcp": "filesystem",
                    "task": "desktop/project_management",
                    "run": 1,
                    "runner_status": "infra_error",
                    "infrastructure_error": "synthetic setup exception",
                },
            )
            summary = summarize_results.summarize(
                manifest,
                ["model_a"],
                root,
                audit_contract,
            )

        self.assertEqual(summary["data_quality"]["infra_error"], 1)
        self.assertEqual(summary["data_quality"]["missing"], 1)
        self.assertEqual(
            summary["data_quality"]["issues"][0]["error"],
            "synthetic setup exception",
        )


if __name__ == "__main__":
    unittest.main()
