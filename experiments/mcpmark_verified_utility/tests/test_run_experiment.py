import asyncio
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "run_experiment.py"
PIPX_WRAPPER = SCRIPT.parent / "bin" / "pipx"
DOCKER_WRAPPER = SCRIPT.parent / "bin" / "docker"
NPX_WRAPPER = SCRIPT.parent / "bin" / "npx"
SPEC = importlib.util.spec_from_file_location("mcpmark_run_experiment", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
run_experiment = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_experiment
SPEC.loader.exec_module(run_experiment)


def make_sidecar_base(task: run_experiment.TaskSpec) -> dict:
    execution_configuration = {
        "model_label": "qwen3_8b",
        "served_model": "qwen3:8b",
        "model_artifact_id": "a" * 12,
        "base_url": "http://127.0.0.1:11434/v1",
        **run_experiment.FORMAL_RUNTIME_CONFIGURATION,
    }
    return {
        "schema_version": 1,
        "job_key": f"original|qwen3_8b|{task.mcp}|{task.task}|run-1",
        "condition": "original",
        "model_label": "qwen3_8b",
        "served_model": "qwen3:8b",
        "model_artifact_id": execution_configuration["model_artifact_id"],
        "base_url": execution_configuration["base_url"],
        "logical_service": task.logical_service,
        "mcp": task.mcp,
        "task": task.task,
        "run": 1,
        "source_commit": run_experiment.VERIFIED_COMMIT,
        "manifest_sha256": "1" * 64,
        "model_manifest_sha256": "2" * 64,
        "safety_prompt_sha256": "3" * 64,
        "upstream_system_prompt_sha256": (run_experiment.UPSTREAM_SYSTEM_PROMPT_SHA256),
        "effective_system_prompt_sha256": (
            run_experiment.UPSTREAM_SYSTEM_PROMPT_SHA256
        ),
        "execution_configuration_sha256": run_experiment.sha256_json(
            execution_configuration
        ),
        **run_experiment.FORMAL_RUNTIME_CONFIGURATION,
    }


class FakeEvaluator:
    def __init__(
        self,
        task: run_experiment.TaskSpec,
        task_dir: Path,
        controller: types.SimpleNamespace,
        new_meta: dict | None,
    ):
        selected = types.SimpleNamespace(
            category_id=task.category,
            task_id=task.task_id,
        )
        self.task_manager = types.SimpleNamespace(
            filter_tasks=lambda _task_filter: [selected]
        )
        self.cleaned = []
        self.state_manager = types.SimpleNamespace(
            clean_up=lambda value: self.cleaned.append(value)
        )
        self.task_dir = task_dir
        self.controller = controller
        self.new_meta = new_meta
        self.run_calls = 0

    def run_evaluation(self, _task_filter: str) -> types.SimpleNamespace:
        self.run_calls += 1
        if self.new_meta is None:
            raise AssertionError("A normally resumed result must not run upstream")
        self.task_dir.mkdir(parents=True, exist_ok=True)
        run_experiment.write_json_atomic(
            self.task_dir / "meta.json",
            self.new_meta,
        )
        self.controller.main_call_count += 1
        return types.SimpleNamespace(total_tasks=1)


class RunExperimentTests(unittest.TestCase):
    def test_effective_prompts_are_frozen_and_differ_only_by_append(self) -> None:
        original = run_experiment.UPSTREAM_SYSTEM_PROMPT
        safety = "Safety line one.\nSafety line two.\n"

        self.assertEqual(
            run_experiment.build_effective_prompt(original, safety, "original"),
            original,
        )
        effective = run_experiment.build_effective_prompt(original, safety, "safety")
        self.assertEqual(
            effective,
            original + "\n\n## Additional safety policy\n" + safety,
        )
        self.assertTrue(effective.startswith(original))

    def test_frozen_manifest_builds_352_unique_jobs(self) -> None:
        _, tasks = run_experiment.load_task_manifest(run_experiment.DEFAULT_MANIFEST)
        _, models = run_experiment.load_model_manifest(
            run_experiment.DEFAULT_MODEL_MANIFEST
        )
        jobs = run_experiment.build_plan(
            tasks=tasks,
            models=models,
            conditions=run_experiment.CONDITIONS,
            runs=1,
        )

        self.assertEqual(len(tasks), 44)
        self.assertEqual(len(models), 4)
        self.assertEqual(len(jobs), 352)
        self.assertEqual(len({job["job_key"] for job in jobs}), 352)
        self.assertEqual(sum(job["mcp"] == "playwright" for job in jobs), 32)
        self.assertTrue(all(job["mcp"] != "playwright_webarena" for job in jobs))

    def test_limit_is_applied_per_logical_service(self) -> None:
        _, tasks = run_experiment.load_task_manifest(run_experiment.DEFAULT_MANIFEST)
        selected = run_experiment.select_tasks(
            tasks,
            run_experiment.LOGICAL_SERVICES,
            limit_per_service=1,
        )
        self.assertEqual(len(selected), 3)
        self.assertEqual(
            {task.logical_service for task in selected},
            set(run_experiment.LOGICAL_SERVICES),
        )

    def test_completion_controller_checks_prompt_and_overrides_sampling(self) -> None:
        captured = {}

        async def fake_completion(*args, **kwargs):
            captured.update(kwargs)
            return {"ok": True}

        controller = run_experiment.CompletionController(
            fake_completion,
            expected_prompt="frozen prompt",
            temperature=0.0,
            max_tokens=1234,
        )
        response = asyncio.run(
            controller(
                model="openai/test",
                messages=[
                    {"role": "system", "content": "frozen prompt"},
                    {"role": "user", "content": "task"},
                ],
                tools=[{"type": "function", "function": {"name": "tool"}}],
                temperature=1.0,
                max_tokens=32768,
            )
        )

        self.assertEqual(response, {"ok": True})
        self.assertEqual(captured["temperature"], 0.0)
        self.assertEqual(captured["max_tokens"], 1234)
        self.assertEqual(controller.main_call_count, 1)
        self.assertEqual(controller.total_call_count, 1)

    def test_completion_controller_rejects_wrong_system_prompt(self) -> None:
        async def fake_completion(*args, **kwargs):
            return {"ok": True}

        controller = run_experiment.CompletionController(
            fake_completion,
            expected_prompt="expected",
            temperature=0,
            max_tokens=100,
        )
        with self.assertRaisesRegex(RuntimeError, "does not match"):
            asyncio.run(
                controller(
                    messages=[{"role": "system", "content": "wrong"}],
                    tools=[{"type": "function", "function": {"name": "tool"}}],
                )
            )

    def test_endpoint_preflight_lists_model_and_forces_tool_call(self) -> None:
        calls = []

        def fake_http_json(url, *, api_key, payload=None, timeout):
            calls.append((url, api_key, payload, timeout))
            if url.endswith("/models"):
                return {"data": [{"id": "qwen3:8b"}]}
            self.assertNotIn("tool_choice", payload)
            self.assertEqual(payload["max_tokens"], 512)
            return {
                "choices": [
                    {
                        "finish_reason": "tool_calls",
                        "message": {
                            "reasoning": "use the requested tool",
                            "tool_calls": [{"function": {"name": "return_ok"}}],
                        },
                    }
                ]
            }

        checks = []
        with mock.patch.object(
            run_experiment,
            "http_json",
            side_effect=fake_http_json,
        ):
            run_experiment.endpoint_preflight(
                checks,
                base_url="http://127.0.0.1:11434/v1",
                served_model="qwen3:8b",
                api_key="local-placeholder",
                tool_call_smoke=True,
            )

        self.assertEqual(len(calls), 2)
        self.assertTrue(all(check["ok"] for check in checks))
        self.assertEqual(
            {check["name"] for check in checks},
            {"model-listed", "tool-call-capability"},
        )
        capability = next(
            check for check in checks if check["name"] == "tool-call-capability"
        )
        self.assertIn("finish_reason='tool_calls'", capability["detail"])
        self.assertIn("reasoning_chars=22", capability["detail"])

    def test_frozen_service_environment_uses_checkout_local_filesystem_root(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            upstream = Path(temporary) / "upstream"
            upstream.mkdir()
            with mock.patch.dict(
                os.environ,
                {
                    "FILESYSTEM_TEST_ROOT": "/wrong/root",
                    "PLAYWRIGHT_BROWSER": "firefox",
                },
                clear=False,
            ):
                root = run_experiment.configure_frozen_service_environment(upstream)
                self.assertEqual(root, (upstream / "test_environments").resolve())
                self.assertEqual(os.environ["FILESYSTEM_TEST_ROOT"], str(root))
                self.assertEqual(os.environ["PLAYWRIGHT_BROWSER"], "chromium")

    def test_filesystem_state_check_requires_all_ten_populated_categories(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            upstream = Path(temporary)
            state_root = upstream / "test_environments"
            for category in run_experiment.FILESYSTEM_TEMPLATE_CATEGORIES:
                category_root = state_root / category
                category_root.mkdir(parents=True)
                (category_root / "fixture.txt").write_text(
                    category,
                    encoding="utf-8",
                )
            checks = []
            run_experiment.filesystem_state_check(checks, upstream_root=upstream)
            self.assertTrue(checks[0]["ok"])

            missing = state_root / run_experiment.FILESYSTEM_TEMPLATE_CATEGORIES[-1]
            for child in missing.iterdir():
                child.unlink()
            missing.rmdir()
            checks = []
            run_experiment.filesystem_state_check(checks, upstream_root=upstream)
            self.assertFalse(checks[0]["ok"])
            self.assertIn("missing or empty", checks[0]["detail"])

    def test_local_http_requests_bypass_environment_proxies(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"ok": true}'
        opener = mock.MagicMock()
        opener.open.return_value = response

        with (
            mock.patch.object(
                run_experiment.urllib.request,
                "build_opener",
                return_value=opener,
            ) as build_opener,
            mock.patch.object(run_experiment.urllib.request, "urlopen") as urlopen,
        ):
            result = run_experiment.http_json(
                "http://127.0.0.1:11434/v1/models",
                api_key="local-placeholder",
            )

        self.assertEqual(result, {"ok": True})
        build_opener.assert_called_once()
        opener.open.assert_called_once()
        urlopen.assert_not_called()

    def test_local_model_runtime_adds_no_proxy_entries(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"NO_PROXY": "internal.example", "no_proxy": ""},
            clear=False,
        ):
            run_experiment.ensure_local_endpoint_bypass("http://127.0.0.1:11434/v1")
            self.assertEqual(
                os.environ["NO_PROXY"].split(","),
                ["internal.example", "127.0.0.1", "localhost", "::1"],
            )
            self.assertEqual(
                os.environ["no_proxy"].split(","),
                ["127.0.0.1", "localhost", "::1"],
            )

    def test_resume_compatibility_normalizes_only_loopback_ports(self) -> None:
        fields = (
            "served_model",
            "model_artifact_id",
            "base_url",
            "temperature",
        )
        expected = {
            "served_model": "qwen3:8b",
            "model_artifact_id": "a" * 12,
            "base_url": "http://127.0.0.1:21001/v1",
            "temperature": 0.0,
        }
        resumed = {
            **expected,
            "base_url": "http://127.0.0.1:31999/v1",
        }
        self.assertTrue(run_experiment.mappings_compatible(resumed, expected, fields))

        resumed["model_artifact_id"] = "b" * 12
        self.assertFalse(run_experiment.mappings_compatible(resumed, expected, fields))
        resumed = {
            **expected,
            "base_url": "https://different.example/v1",
        }
        self.assertFalse(run_experiment.mappings_compatible(resumed, expected, fields))

    def test_sidecar_resume_allows_a_new_loopback_port(self) -> None:
        task = run_experiment.TaskSpec(
            "filesystem",
            "filesystem",
            "desktop/project_management",
        )
        expected = make_sidecar_base(task)
        found = {
            **expected,
            "base_url": "http://127.0.0.1:29999/v1",
        }
        found_configuration = {
            field: found.get(field)
            for field in run_experiment.EXECUTION_CONFIGURATION_FIELDS
        }
        found["execution_configuration_sha256"] = run_experiment.sha256_json(
            found_configuration
        )
        with tempfile.TemporaryDirectory() as temporary:
            sidecar = Path(temporary) / "experiment_meta.json"
            run_experiment.write_json_atomic(sidecar, found)
            self.assertTrue(run_experiment.sidecar_compatible(sidecar, expected))

            found["model_artifact_id"] = "b" * 12
            found_configuration = {
                field: found.get(field)
                for field in run_experiment.EXECUTION_CONFIGURATION_FIELDS
            }
            found["execution_configuration_sha256"] = run_experiment.sha256_json(
                found_configuration
            )
            run_experiment.write_json_atomic(sidecar, found)
            self.assertFalse(run_experiment.sidecar_compatible(sidecar, expected))

    def test_runtime_path_includes_bundled_postgres_client(self) -> None:
        with mock.patch.dict(os.environ, {"PATH": "/usr/bin"}, clear=False):
            run_experiment.ensure_runtime_path()
            run_experiment.ensure_runtime_path()
            entries = os.environ["PATH"].split(os.pathsep)

        postgres_bin = str(run_experiment.POSTGRES_CLIENT_PREFIX / "bin")
        wrapper_bin = str(run_experiment.EXPERIMENT_DIR / "bin")
        python_bin = str(Path(sys.executable).absolute().parent)
        self.assertIn(postgres_bin, entries)
        self.assertEqual(entries[0], wrapper_bin)
        self.assertLess(entries.index(wrapper_bin), entries.index(python_bin))
        self.assertLess(entries.index(postgres_bin), entries.index("/usr/bin"))
        self.assertEqual(entries.count(postgres_bin), 1)

    def test_rootless_image_names_are_normalized(self) -> None:
        self.assertEqual(
            run_experiment.normalize_container_image(
                "docker.io/pgvector/pgvector:0.8.0-pg17-bookworm"
            ),
            "pgvector/pgvector:0.8.0-pg17-bookworm",
        )

    def test_container_image_listing_normalizes_podman_localhost_prefix(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["podman", "images"],
            returncode=0,
            stdout="docker.io/pgvector/pgvector:0.8.0-pg17-bookworm\n",
            stderr="",
        )
        with mock.patch.object(
            run_experiment.subprocess,
            "run",
            return_value=completed,
        ):
            ok, _detail, images = run_experiment.list_container_images("podman")

        self.assertTrue(ok)
        self.assertIn("pgvector/pgvector:0.8.0-pg17-bookworm", images)

    def test_playwright_mcp_smoke_fails_closed_without_pinned_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            checks = []
            with mock.patch.dict(
                os.environ,
                {"MCPMARK_PLAYWRIGHT_NODE_PREFIX": temporary},
                clear=False,
            ):
                run_experiment.playwright_mcp_runtime_check(checks)

        self.assertEqual(
            checks,
            [
                {
                    "name": "playwright-mcp-browser-smoke",
                    "ok": False,
                    "required": True,
                    "detail": (
                        f"pinned Playwright MCP executable is missing: "
                        f"{temporary}/node_modules/.bin/playwright-mcp"
                    ),
                }
            ],
        )

    def test_filesystem_mcp_smoke_fails_closed_without_pinned_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            checks = []
            with mock.patch.dict(
                os.environ,
                {"MCPMARK_PLAYWRIGHT_NODE_PREFIX": temporary},
                clear=False,
            ):
                run_experiment.filesystem_mcp_runtime_check(checks)

        self.assertEqual(
            checks,
            [
                {
                    "name": "filesystem-mcp-smoke",
                    "ok": False,
                    "required": True,
                    "detail": (
                        f"pinned Filesystem MCP executable is missing: "
                        f"{temporary}/node_modules/.bin/mcp-server-filesystem"
                    ),
                }
            ],
        )

    def test_npx_wrapper_routes_only_frozen_playwright_command_locally(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            node_prefix = Path(temporary) / "node"
            local_server = node_prefix / "node_modules" / ".bin" / "playwright-mcp"
            local_server.parent.mkdir(parents=True)
            local_server.write_text(
                (
                    "#!/usr/bin/env bash\n"
                    "printf 'output_dir=%s\\n' "
                    '"${PLAYWRIGHT_MCP_OUTPUT_DIR:-}"\n'
                    "printf 'working_dir=%s\\n' \"$PWD\"\n"
                    "printf '%s\\n' \"$@\"\n"
                ),
                encoding="utf-8",
            )
            local_server.chmod(0o755)
            output_root = Path(temporary) / "playwright-output"
            environment = os.environ.copy()
            environment["MCPMARK_PLAYWRIGHT_NODE_PREFIX"] = str(node_prefix)
            environment["MCPMARK_PLAYWRIGHT_OUTPUT_ROOT"] = str(output_root)
            environment.pop("PLAYWRIGHT_MCP_OUTPUT_DIR", None)
            completed = subprocess.run(
                [
                    str(NPX_WRAPPER),
                    "-y",
                    "@playwright/mcp@0.0.68",
                    "--headless",
                    "--isolated",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            output_lines = completed.stdout.splitlines()
            output_dir = Path(output_lines[0].removeprefix("output_dir="))
            self.assertEqual(output_dir.parent, output_root)
            self.assertRegex(output_dir.name, r"^server-[1-9][0-9]*$")
            self.assertTrue(output_dir.is_dir())
            self.assertEqual(output_dir.stat().st_mode & 0o777, 0o700)
            working_dir = Path(output_lines[1].removeprefix("working_dir="))
            self.assertEqual(working_dir, output_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(output_lines[2:], ["--headless", "--isolated"])

    def test_npx_wrapper_routes_frozen_filesystem_command_locally(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            node_prefix = Path(temporary) / "node"
            local_server = (
                node_prefix / "node_modules" / ".bin" / "mcp-server-filesystem"
            )
            local_server.parent.mkdir(parents=True)
            local_server.write_text(
                "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\"\n",
                encoding="utf-8",
            )
            local_server.chmod(0o755)
            environment = os.environ.copy()
            environment["MCPMARK_PLAYWRIGHT_NODE_PREFIX"] = str(node_prefix)
            completed = subprocess.run(
                [
                    str(NPX_WRAPPER),
                    "-y",
                    "@modelcontextprotocol/server-filesystem@2025.12.18",
                    "/tmp/test-root",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.splitlines(), ["/tmp/test-root"])

    def test_docker_wrapper_rewrites_publish_to_loopback(self) -> None:
        environment = os.environ.copy()
        environment.update(
            {
                "MCPMARK_CONTAINER_CLI": "/bin/echo",
                "MCPMARK_DOCKER_LOOPBACK_ONLY": "1",
            }
        )
        completed = subprocess.run(
            [
                str(DOCKER_WRAPPER),
                "run",
                "--name",
                "test",
                "-p",
                "41001:80",
                "image",
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "run --name test -p 127.0.0.1:41001:80 image",
            completed.stdout,
        )

    def test_docker_wrapper_refuses_non_loopback_publish(self) -> None:
        environment = os.environ.copy()
        environment.update(
            {
                "MCPMARK_CONTAINER_CLI": "/bin/echo",
                "MCPMARK_DOCKER_LOOPBACK_ONLY": "1",
            }
        )
        completed = subprocess.run(
            [
                str(DOCKER_WRAPPER),
                "run",
                "--publish",
                "0.0.0.0:41001:80",
                "image",
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Refusing non-loopback", completed.stderr)

    def test_docker_wrapper_scopes_xdg_runtime_to_podman_child(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime_dir = root / "podman-runtime"
            runtime_dir.mkdir(mode=0o700)
            fake_podman = root / "podman"
            fake_podman.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
printf 'xdg=%s\\n' "${XDG_RUNTIME_DIR:-}"
printf 'args=%s\\n' "$*"
""",
                encoding="utf-8",
            )
            fake_podman.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                {
                    "MCPMARK_CONTAINER_CLI": str(fake_podman),
                    "MCPMARK_PODMAN_XDG_RUNTIME_DIR": str(runtime_dir),
                    "XDG_RUNTIME_DIR": "/parent/runtime/must-not-be-used",
                }
            )

            completed = subprocess.run(
                [str(DOCKER_WRAPPER), "info", "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.splitlines(),
            [
                f"xdg={runtime_dir}",
                "args=info --format json",
            ],
        )
        self.assertEqual(
            environment["XDG_RUNTIME_DIR"],
            "/parent/runtime/must-not-be-used",
        )

    def test_postgres_pipx_wrapper_injects_frozen_mcp_constraint(self) -> None:
        environment = os.environ.copy()
        environment["MCPMARK_REAL_PIPX"] = "/bin/echo"
        completed = subprocess.run(
            [
                str(PIPX_WRAPPER),
                "run",
                "postgres-mcp==0.3.0",
                "--access-mode=unrestricted",
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("run --pip-args=--constraint ", completed.stdout)
        self.assertIn("postgres_mcp_constraints.txt", completed.stdout)
        self.assertIn(
            "postgres-mcp==0.3.0 --access-mode=unrestricted",
            completed.stdout,
        )

    def test_postgres_pipx_wrapper_recovers_from_self_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary)
            wrapper = experiment_dir / "bin" / "pipx"
            wrapper.parent.mkdir()
            wrapper.write_bytes(PIPX_WRAPPER.read_bytes())
            wrapper.chmod(0o755)
            constraints = experiment_dir / "postgres_mcp_constraints.txt"
            constraints.write_text("mcp==1.13.1\n", encoding="utf-8")
            real_pipx = experiment_dir / ".venv" / "bin" / "pipx"
            real_pipx.parent.mkdir(parents=True)
            real_pipx.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*"
""",
                encoding="utf-8",
            )
            real_pipx.chmod(0o755)
            environment = os.environ.copy()
            environment["MCPMARK_REAL_PIPX"] = str(wrapper)

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
                env=environment,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.strip(),
            (f"run --pip-args=--constraint {constraints} postgres-mcp==0.3.0 --help"),
        )

    def test_infrastructure_failures_are_not_confused_with_task_failure(self) -> None:
        setup_failure = {
            "execution_result": {
                "success": False,
                "error_message": "State Duplication Error",
            }
        }
        normal_verifier_failure = {
            "execution_result": {
                "success": False,
                "error_message": None,
                "verification_error": "expected state was not found",
            }
        }
        turn_limit = {
            "execution_result": {
                "success": False,
                "error_message": "Max turns (100) exceeded",
            }
        }

        self.assertIsNotNone(
            run_experiment.infer_infrastructure_error(
                setup_failure, fresh_model_calls=0
            )
        )
        self.assertIsNone(
            run_experiment.infer_infrastructure_error(
                normal_verifier_failure, fresh_model_calls=1
            )
        )
        self.assertIsNone(
            run_experiment.infer_infrastructure_error(turn_limit, fresh_model_calls=1)
        )
        for model_side_failure in (
            "Agent execution failed",
            "Execution timed out after 3600 seconds",
            "Too many consecutive failures",
        ):
            with self.subTest(model_side_failure=model_side_failure):
                self.assertIsNone(
                    run_experiment.infer_infrastructure_error(
                        {
                            "execution_result": {
                                "success": False,
                                "error_message": model_side_failure,
                            }
                        },
                        fresh_model_calls=1,
                    )
                )
        verifier_connection_failure = {
            "execution_result": {
                "success": False,
                "error_message": None,
                "verification_error": "connection refused by PostgreSQL",
            }
        }
        self.assertIsNotNone(
            run_experiment.infer_infrastructure_error(
                verifier_connection_failure,
                fresh_model_calls=1,
            )
        )
        missing_expected_output = {
            "execution_result": {
                "success": False,
                "error_message": None,
                "verification_error": (
                    "FileNotFoundError: expected output directory was not created"
                ),
            }
        }
        self.assertIsNone(
            run_experiment.infer_infrastructure_error(
                missing_expected_output,
                fresh_model_calls=1,
            )
        )

    def test_normal_result_resumes_without_rewriting_or_rerunning(self) -> None:
        task = run_experiment.TaskSpec(
            "filesystem",
            "filesystem",
            "desktop/project_management",
        )
        sidecar_base = make_sidecar_base(task)
        controller = types.SimpleNamespace(main_call_count=5)
        with tempfile.TemporaryDirectory() as temporary:
            results_root = Path(temporary)
            task_dir = results_root / "task"
            meta_path = task_dir / "meta.json"
            meta = {
                "execution_result": {
                    "success": False,
                    "error_message": None,
                    "verification_error": "expected state was not found",
                }
            }
            run_experiment.write_json_atomic(meta_path, meta)
            stored_sidecar = {
                **sidecar_base,
                "completed_at": "2026-01-01T00:00:00+00:00",
                "upstream_meta_sha256": run_experiment.sha256_file(meta_path),
                "prompt_verified_model_calls": 2,
                "resumed": False,
                "runner_status": "normal",
                "infrastructure_error": None,
            }
            sidecar_path = task_dir / "experiment_meta.json"
            run_experiment.write_json_atomic(sidecar_path, stored_sidecar)
            evaluator = FakeEvaluator(task, task_dir, controller, new_meta=None)

            result = run_experiment.run_one_task(
                evaluator=evaluator,
                task=task,
                task_dir=task_dir,
                results_root=results_root,
                sidecar_base=sidecar_base,
                controller=controller,
                force_rerun=False,
            )

            self.assertTrue(result["resumed"])
            self.assertEqual(result["runner_status"], "normal")
            self.assertEqual(evaluator.run_calls, 0)
            self.assertEqual(
                run_experiment.read_json(sidecar_path),
                stored_sidecar,
            )

    def test_infrastructure_result_is_cleaned_and_retried(self) -> None:
        task = run_experiment.TaskSpec(
            "filesystem",
            "filesystem",
            "desktop/project_management",
        )
        sidecar_base = make_sidecar_base(task)
        controller = types.SimpleNamespace(main_call_count=0)
        with tempfile.TemporaryDirectory() as temporary:
            results_root = Path(temporary)
            task_dir = results_root / "task"
            meta_path = task_dir / "meta.json"
            old_meta = {
                "execution_result": {
                    "success": False,
                    "error_message": "Connection refused by the model endpoint",
                }
            }
            run_experiment.write_json_atomic(meta_path, old_meta)
            run_experiment.write_json_atomic(
                task_dir / "experiment_meta.json",
                {
                    **sidecar_base,
                    "upstream_meta_sha256": run_experiment.sha256_file(meta_path),
                    "prompt_verified_model_calls": 1,
                    "runner_status": "infra_error",
                    "infrastructure_error": old_meta["execution_result"][
                        "error_message"
                    ],
                },
            )
            new_meta = {
                "execution_result": {
                    "success": False,
                    "error_message": None,
                    "verification_error": "expected state was not found",
                }
            }
            evaluator = FakeEvaluator(
                task,
                task_dir,
                controller,
                new_meta=new_meta,
            )

            result = run_experiment.run_one_task(
                evaluator=evaluator,
                task=task,
                task_dir=task_dir,
                results_root=results_root,
                sidecar_base=sidecar_base,
                controller=controller,
                force_rerun=False,
            )

            self.assertEqual(evaluator.run_calls, 1)
            self.assertTrue(evaluator.cleaned)
            self.assertTrue(result["retried_infrastructure_error"])
            self.assertEqual(result["runner_status"], "normal")
            self.assertEqual(result["prompt_verified_model_calls"], 1)

    def test_exception_sidecar_without_meta_is_retried(self) -> None:
        task = run_experiment.TaskSpec(
            "filesystem",
            "filesystem",
            "desktop/project_management",
        )
        sidecar_base = make_sidecar_base(task)
        controller = types.SimpleNamespace(main_call_count=0)
        with tempfile.TemporaryDirectory() as temporary:
            results_root = Path(temporary)
            task_dir = results_root / "task"
            run_experiment.write_json_atomic(
                task_dir / "experiment_meta.json",
                {
                    **sidecar_base,
                    "upstream_meta_sha256": None,
                    "prompt_verified_model_calls": 0,
                    "runner_status": "infra_error",
                    "infrastructure_error": "synthetic setup exception",
                },
            )
            evaluator = FakeEvaluator(
                task,
                task_dir,
                controller,
                new_meta={
                    "execution_result": {
                        "success": True,
                        "error_message": None,
                    }
                },
            )

            result = run_experiment.run_one_task(
                evaluator=evaluator,
                task=task,
                task_dir=task_dir,
                results_root=results_root,
                sidecar_base=sidecar_base,
                controller=controller,
                force_rerun=False,
            )

            self.assertEqual(evaluator.run_calls, 1)
            self.assertTrue(result["retried_infrastructure_error"])
            self.assertEqual(result["runner_status"], "normal")

    def test_tampered_resumed_meta_is_rejected(self) -> None:
        task = run_experiment.TaskSpec(
            "filesystem",
            "filesystem",
            "desktop/project_management",
        )
        sidecar_base = make_sidecar_base(task)
        controller = types.SimpleNamespace(main_call_count=0)
        with tempfile.TemporaryDirectory() as temporary:
            results_root = Path(temporary)
            task_dir = results_root / "task"
            meta_path = task_dir / "meta.json"
            run_experiment.write_json_atomic(
                meta_path,
                {"execution_result": {"success": True}},
            )
            run_experiment.write_json_atomic(
                task_dir / "experiment_meta.json",
                {
                    **sidecar_base,
                    "upstream_meta_sha256": "0" * 64,
                    "prompt_verified_model_calls": 1,
                    "runner_status": "normal",
                    "infrastructure_error": None,
                },
            )
            evaluator = FakeEvaluator(task, task_dir, controller, new_meta=None)

            with self.assertRaisesRegex(RuntimeError, "hash does not match"):
                run_experiment.run_one_task(
                    evaluator=evaluator,
                    task=task,
                    task_dir=task_dir,
                    results_root=results_root,
                    sidecar_base=sidecar_base,
                    controller=controller,
                    force_rerun=False,
                )

    def test_cli_validate_and_offline_dry_run(self) -> None:
        validate = subprocess.run(
            [sys.executable, str(SCRIPT), "validate"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(validate.returncode, 0, validate.stderr)
        report = json.loads(validate.stdout)
        self.assertEqual(report["expected_trajectories_k1"], 352)

        with tempfile.TemporaryDirectory() as temporary:
            results = Path(temporary) / "results"
            dry_run = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "run",
                    "--results-root",
                    str(results),
                    "--model-label",
                    "qwen3_8b",
                    "--served-model",
                    "qwen3:8b",
                    "--base-url",
                    "http://127.0.0.1:9/v1",
                    "--conditions",
                    "original,safety",
                    "--services",
                    "filesystem,postgres",
                    "--k",
                    "1",
                    "--temperature",
                    "0",
                    "--dry-run",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        document = json.loads(dry_run.stdout)
        self.assertEqual(document["job_count"], 80)

        incompatible = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "run",
                "--results-root",
                "/tmp/mcpmark-invalid-config",
                "--model-label",
                "qwen3_8b",
                "--served-model",
                "qwen3:8b",
                "--base-url",
                "http://127.0.0.1:9/v1",
                "--services",
                "filesystem",
                "--max-turns",
                "99",
                "--dry-run",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(incompatible.returncode, 2)
        self.assertIn("requires --max-turns=100", incompatible.stderr)


if __name__ == "__main__":
    unittest.main()
