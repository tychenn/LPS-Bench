import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
WORKER_SCRIPT = EXPERIMENT_DIR / "run_model_worker.sh"
MODEL_KEY = "llama31_8b"
SERVED_MODEL = "llama3.1:8b"
ARTIFACT_ID = "0123456789abcdef"
PROXY_VARIABLES = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


def write_executable(path: Path, body: str) -> None:
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    path.chmod(0o755)


class WorkerFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.script_dir = root / "script"
        self.script_dir.mkdir()
        shutil.copy2(WORKER_SCRIPT, self.script_dir / WORKER_SCRIPT.name)
        (self.script_dir / "bin").mkdir()

        manifest = {
            "schema_version": 1,
            "provider": "ollama",
            "models": {
                MODEL_KEY: {
                    "display_name": "fixture",
                    "served_model": SERVED_MODEL,
                    "context_length": 131072,
                    "slurm_gres": "gpu:1",
                    "slurm_memory": "1G",
                    "startup_delay_seconds": 0,
                }
            },
        }
        (self.script_dir / "model_manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )

        self.venv = root / "venv"
        venv_bin = self.venv / "bin"
        venv_bin.mkdir(parents=True)
        python = Path(sys.executable).resolve()
        (venv_bin / "python").symlink_to(python)
        (venv_bin / "python3").symlink_to(python)

        self.child_log = root / "child-events.jsonl"
        self._write_fake_runner()
        self._write_fake_ollama(venv_bin / "ollama")
        self._write_fake_curl(venv_bin / "curl")

        self.repo_root = root / "repo"
        self.repo_root.mkdir()
        self.experiment_root = root / "experiment"
        self.environment = os.environ.copy()
        self.environment.update(
            {
                "PATH": f"{venv_bin}{os.pathsep}{self.environment['PATH']}",
                "REPO_ROOT": str(self.repo_root),
                "MCPMARK_VENV": str(self.venv),
                "MCPMARK_DIRECT_MODE": "1",
                "MCPMARK_STRICT_GPU_CHECK": "0",
                "MCPMARK_OLLAMA_PORT": "24567",
                "OLLAMA_READY_TIMEOUT": "4",
                "ALLOW_OLLAMA_PULL": "0",
                "FAKE_CHILD_EVENT_LOG": str(self.child_log),
                "FAKE_OLLAMA_ARTIFACT_ID": ARTIFACT_ID,
                "FAKE_OLLAMA_MODEL": SERVED_MODEL,
            }
        )

    def _write_fake_runner(self) -> None:
        runner = self.script_dir / "run_experiment.py"
        runner.write_text(
            textwrap.dedent(
                """
                import json
                import os
                from pathlib import Path
                import sys

                proxy_names = (
                    "HTTP_PROXY",
                    "HTTPS_PROXY",
                    "ALL_PROXY",
                    "http_proxy",
                    "https_proxy",
                    "all_proxy",
                )
                event = {
                    "program": "run_experiment",
                    "command": sys.argv[1] if len(sys.argv) > 1 else "",
                    "proxy_environment": {
                        name: os.environ.get(name) for name in proxy_names
                    },
                    "no_proxy": os.environ.get("NO_PROXY"),
                    "lower_no_proxy": os.environ.get("no_proxy"),
                }
                with Path(os.environ["FAKE_CHILD_EVENT_LOG"]).open(
                    "a", encoding="utf-8"
                ) as handle:
                    handle.write(json.dumps(event, sort_keys=True) + "\\n")
                """
            ).lstrip(),
            encoding="utf-8",
        )

    def _write_fake_ollama(self, path: Path) -> None:
        write_executable(
            path,
            """
            #!/usr/bin/env python3
            import json
            import os
            from pathlib import Path
            import signal
            import sys
            import time

            proxy_names = (
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "ALL_PROXY",
                "http_proxy",
                "https_proxy",
                "all_proxy",
            )
            command = sys.argv[1] if len(sys.argv) > 1 else ""
            event = {
                "program": "ollama",
                "command": command,
                "proxy_environment": {
                    name: os.environ.get(name) for name in proxy_names
                },
                "no_proxy": os.environ.get("NO_PROXY"),
                "lower_no_proxy": os.environ.get("no_proxy"),
            }
            with Path(os.environ["FAKE_CHILD_EVENT_LOG"]).open(
                "a", encoding="utf-8"
            ) as handle:
                handle.write(json.dumps(event, sort_keys=True) + "\\n")

            if command == "serve":
                while True:
                    time.sleep(1)
            if command == "show":
                raise SystemExit(0)
            if command == "list":
                if os.environ.get("FAKE_OLLAMA_LIST_FAIL") == "1":
                    print("injected ollama list failure", file=sys.stderr)
                    raise SystemExit(37)
                signal.signal(signal.SIGPIPE, signal.SIG_DFL)
                model = os.environ["FAKE_OLLAMA_MODEL"]
                artifact = os.environ["FAKE_OLLAMA_ARTIFACT_ID"]
                print("NAME ID SIZE MODIFIED")
                print(f"{model} {artifact} 1 GB now")
                if os.environ.get("FAKE_OLLAMA_LARGE_LIST") == "1":
                    for index in range(100_000):
                        print(
                            "unused-{0}:latest fedcba9876543210 1 GB now".format(
                                index
                            )
                        )
                raise SystemExit(0)
            raise SystemExit(2)
            """,
        )

    def _write_fake_curl(self, path: Path) -> None:
        write_executable(
            path,
            """
            #!/usr/bin/env python3
            import json
            import os
            from pathlib import Path
            import sys

            proxy_names = (
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "ALL_PROXY",
                "http_proxy",
                "https_proxy",
                "all_proxy",
            )
            arguments = sys.argv[1:]
            is_preload = any(
                argument.endswith("/api/generate") for argument in arguments
            )
            event = {
                "program": "curl",
                "command": "preload" if is_preload else "ready",
                "arguments": arguments,
                "proxy_environment": {
                    name: os.environ.get(name) for name in proxy_names
                },
                "no_proxy": os.environ.get("NO_PROXY"),
                "lower_no_proxy": os.environ.get("no_proxy"),
            }
            if is_preload:
                payload_index = arguments.index("--data-binary") + 1
                output_index = arguments.index("--output") + 1
                event["payload"] = json.loads(arguments[payload_index])
            with Path(os.environ["FAKE_CHILD_EVENT_LOG"]).open(
                "a", encoding="utf-8"
            ) as handle:
                handle.write(json.dumps(event, sort_keys=True) + "\\n")
            if is_preload:
                if os.environ.get("FAKE_PRELOAD_FAIL") == "1":
                    print("injected preload failure", file=sys.stderr)
                    raise SystemExit(47)
                Path(arguments[output_index]).write_text(
                    json.dumps(
                        {
                            "model": os.environ["FAKE_OLLAMA_MODEL"],
                            "done": True,
                            "done_reason": "load",
                            "load_duration": 123,
                        }
                    ),
                    encoding="utf-8",
                )
            """,
        )

    def run(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "bash",
                str(self.script_dir / WORKER_SCRIPT.name),
                MODEL_KEY,
                "filesystem",
                "both",
                str(self.experiment_root),
            ],
            check=False,
            capture_output=True,
            text=True,
            env=self.environment,
            timeout=20,
        )

    def events(self) -> list[dict[str, object]]:
        return [
            json.loads(line)
            for line in self.child_log.read_text(encoding="utf-8").splitlines()
        ]


class WorkerContractTests(unittest.TestCase):
    def test_large_ollama_list_does_not_trigger_pipefail_sigpipe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = WorkerFixture(Path(temporary))
            fixture.environment["FAKE_OLLAMA_LARGE_LIST"] = "1"

            completed = fixture.run()

            self.assertEqual(
                completed.returncode,
                0,
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            done = (
                fixture.experiment_root / "status" / f"{MODEL_KEY}_filesystem_both.done"
            )
            self.assertTrue(done.is_file())
            artifact = fixture.experiment_root / "model_artifacts" / f"{MODEL_KEY}.txt"
            self.assertEqual(
                artifact.read_text(encoding="utf-8"),
                f"{SERVED_MODEL}\t{ARTIFACT_ID}\n",
            )

    def test_worker_children_drop_proxies_without_mutating_parent(self) -> None:
        proxy_values = {
            name: f"http://proxy.invalid/{name}" for name in PROXY_VARIABLES
        }
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(os.environ, proxy_values, clear=False):
                fixture = WorkerFixture(Path(temporary))
                fixture.environment.update(proxy_values)
                fixture.environment["NO_PROXY"] = "parent.example"
                fixture.environment["no_proxy"] = "lower-parent.example"

                completed = fixture.run()

                self.assertEqual(
                    {name: os.environ.get(name) for name in PROXY_VARIABLES},
                    proxy_values,
                )

            self.assertEqual(
                completed.returncode,
                0,
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            events = fixture.events()
            self.assertGreaterEqual(len(events), 6)
            self.assertEqual(
                {
                    str(event["command"])
                    for event in events
                    if event["program"] == "run_experiment"
                },
                {"preflight", "run"},
            )
            for event in events:
                self.assertEqual(
                    event["proxy_environment"],
                    {name: None for name in PROXY_VARIABLES},
                    event,
                )
                self.assertIn("127.0.0.1", str(event["no_proxy"]).split(","))
                self.assertIn("localhost", str(event["no_proxy"]).split(","))
                self.assertIn(
                    "127.0.0.1",
                    str(event["lower_no_proxy"]).split(","),
                )
                self.assertIn(
                    "localhost",
                    str(event["lower_no_proxy"]).split(","),
                )

    def test_ollama_list_failure_writes_failed_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = WorkerFixture(Path(temporary))
            fixture.environment["FAKE_OLLAMA_LIST_FAIL"] = "1"

            completed = fixture.run()

            self.assertNotEqual(completed.returncode, 0)
            failed = (
                fixture.experiment_root
                / "status"
                / f"{MODEL_KEY}_filesystem_both.failed"
            )
            self.assertTrue(
                failed.is_file(),
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            failure_text = failed.read_text(encoding="utf-8")
            self.assertIn("reason=", failure_text)
            self.assertIn("ollama", failure_text.lower())
            self.assertIn("list", failure_text.lower())

    def test_model_is_preloaded_before_endpoint_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = WorkerFixture(Path(temporary))

            completed = fixture.run()

            self.assertEqual(
                completed.returncode,
                0,
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            events = fixture.events()
            preload_index = next(
                index
                for index, event in enumerate(events)
                if event["program"] == "curl" and event["command"] == "preload"
            )
            preflight_index = next(
                index
                for index, event in enumerate(events)
                if event["program"] == "run_experiment"
                and event["command"] == "preflight"
            )
            self.assertLess(preload_index, preflight_index)
            preload = events[preload_index]
            self.assertEqual(
                preload["payload"],
                {
                    "model": SERVED_MODEL,
                    "stream": False,
                    "keep_alive": "30m",
                    "options": {"num_ctx": 131072},
                },
            )
            response_paths = list(
                (fixture.experiment_root / "logs").glob(
                    f"{MODEL_KEY}_filesystem_both_preload_*.json"
                )
            )
            self.assertEqual(len(response_paths), 1)
            response = json.loads(response_paths[0].read_text(encoding="utf-8"))
            self.assertTrue(response["done"])
            runtime = (
                fixture.experiment_root
                / "status"
                / f"{MODEL_KEY}_filesystem_both.runtime"
            ).read_text(encoding="utf-8")
            self.assertIn("model_preload_timeout_seconds=1260\n", runtime)
            self.assertIn("model_preload_finished_at=", runtime)

    def test_model_preload_failure_writes_failed_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = WorkerFixture(Path(temporary))
            fixture.environment["FAKE_PRELOAD_FAIL"] = "1"

            completed = fixture.run()

            self.assertNotEqual(completed.returncode, 0)
            failed = (
                fixture.experiment_root
                / "status"
                / f"{MODEL_KEY}_filesystem_both.failed"
            )
            self.assertTrue(
                failed.is_file(),
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            failure_text = failed.read_text(encoding="utf-8").lower()
            self.assertIn("reason=", failure_text)
            self.assertIn("preload", failure_text)


if __name__ == "__main__":
    unittest.main()
