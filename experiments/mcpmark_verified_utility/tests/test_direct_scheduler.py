import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
DIRECT_SCRIPT = EXPERIMENT_DIR / "run_gpu3_experiment.sh"
MODELS = ("llama31_8b", "llama31_70b", "qwen3_8b", "qwen3_32b")
SERVICES = ("filesystem", "postgres", "playwright")
EXPECTED_GPU_COUNTS = {
    "llama31_8b": 1,
    "llama31_70b": 2,
    "qwen3_8b": 1,
    "qwen3_32b": 1,
}


@unittest.skipUnless(
    DIRECT_SCRIPT.is_file(),
    "production direct scheduler is not implemented yet",
)
class DirectSchedulerTests(unittest.TestCase):
    def test_direct_scheduler_obeys_service_and_gpu_constraints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script_dir = root / "script"
            script_dir.mkdir()
            shutil.copy2(DIRECT_SCRIPT, script_dir / DIRECT_SCRIPT.name)

            # Keep plan/validation behavior production-real while replacing only
            # host dependencies that this scheduler test must not exercise.
            for relative_path in (
                "model_manifest.json",
                "run_experiment.py",
                "run_model_slurm.sh",
                "task_manifest.json",
                "safety_prompt.txt",
                "postgres_mcp_constraints.txt",
                "bin/docker",
                "bin/pipx",
            ):
                source = EXPERIMENT_DIR / relative_path
                if not source.exists():
                    continue
                destination = script_dir / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(source)

            setup_log = root / "setup.log"
            setup = script_dir / "setup_environment.sh"
            setup.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
[[ "$#" -eq 1 && "$1" == "--check-only" ]]
printf '%s\\n' "$1" > "$FAKE_SETUP_LOG"
""",
                encoding="utf-8",
            )
            setup.chmod(0o755)

            asset_log = root / "asset.log"
            asset_check = script_dir / "prepare_service_assets.sh"
            asset_check.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
[[ "$#" -eq 1 && "$1" == "--check-only" ]]
printf '%s\\n' "$1" > "$FAKE_ASSET_LOG"
""",
                encoding="utf-8",
            )
            asset_check.chmod(0o755)

            fake_venv = root / "venv"
            (fake_venv / "bin").mkdir(parents=True)
            (fake_venv / "bin" / "python").symlink_to(Path(sys.executable).resolve())

            event_log = root / "worker-events.jsonl"
            fake_worker = root / "fake-worker.py"
            fake_worker.write_text(
                """#!/usr/bin/env python3
import fcntl
import json
import os
import sys
import time

if len(sys.argv) != 5:
    raise SystemExit(f"expected MODEL SERVICE CONDITION EXP, got: {sys.argv!r}")

model, service, condition, experiment = sys.argv[1:]
event_log = os.environ["FAKE_DIRECT_WORKER_LOG"]
cuda_devices = os.environ.get("CUDA_VISIBLE_DEVICES", "")

def emit(event):
    record = {
        "event": event,
        "time_ns": time.monotonic_ns(),
        "pid": os.getpid(),
        "model": model,
        "service": service,
        "condition": condition,
        "experiment": experiment,
        "cuda_visible_devices": cuda_devices,
        "proxy_environment": {
            name: os.environ.get(name)
            for name in (
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "ALL_PROXY",
                "http_proxy",
                "https_proxy",
                "all_proxy",
            )
        },
        "containers_storage_conf": os.environ.get("CONTAINERS_STORAGE_CONF"),
        "podman_local_root": os.environ.get("MCPMARK_PODMAN_LOCAL_ROOT"),
        "podman_xdg_runtime_dir": os.environ.get(
            "MCPMARK_PODMAN_XDG_RUNTIME_DIR"
        ),
        "container_cli": os.environ.get("MCPMARK_CONTAINER_CLI"),
    }
    with open(event_log, "a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.write(json.dumps(record, sort_keys=True) + "\\n")
        handle.flush()
        fcntl.flock(handle, fcntl.LOCK_UN)

emit("start")
time.sleep(float(os.environ.get("FAKE_DIRECT_WORKER_SECONDS", "0.20")))
emit("end")
""",
                encoding="utf-8",
            )
            fake_worker.chmod(0o755)

            fake_bin = root / "bin"
            fake_bin.mkdir()
            forbidden_log = root / "forbidden-command.log"
            for executable in ("sbatch", "ollama", "nvidia-smi"):
                path = fake_bin / executable
                path.write_text(
                    """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$0 $*" >> "$FORBIDDEN_COMMAND_LOG"
exit 97
""",
                    encoding="utf-8",
                )
                path.chmod(0o755)

            experiment_root = root / "experiment"
            podman_local_root = root / "podman-local"
            podman_xdg_runtime = root / "podman-xdg"
            proxy_names = (
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "ALL_PROXY",
                "http_proxy",
                "https_proxy",
                "all_proxy",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{fake_bin}{os.pathsep}{environment['PATH']}",
                    "EXP": str(experiment_root),
                    "REPO_ROOT": str(EXPERIMENT_DIR.parents[1]),
                    "MCPMARK_VENV": str(fake_venv),
                    "PYTHON_BOOTSTRAP": str(Path(sys.executable).resolve()),
                    "MCPMARK_DIRECT_WORKER": str(fake_worker),
                    "MCPMARK_SKIP_HOST_GPU_CHECK": "1",
                    "MCPMARK_GPU_IDS": "0,1,2,3",
                    "MCPMARK_PODMAN_LOCAL_ROOT": str(podman_local_root),
                    "MCPMARK_PODMAN_XDG_RUNTIME_DIR": str(podman_xdg_runtime),
                    "CUDA_VISIBLE_DEVICES": "0,1,2,3",
                    "FAKE_DIRECT_WORKER_LOG": str(event_log),
                    "FAKE_DIRECT_WORKER_SECONDS": "0.20",
                    "FAKE_SETUP_LOG": str(setup_log),
                    "FAKE_ASSET_LOG": str(asset_log),
                    "FORBIDDEN_COMMAND_LOG": str(forbidden_log),
                }
            )
            for proxy_name in proxy_names:
                environment[proxy_name] = f"http://{proxy_name}.invalid:9999"
            parent_proxy_values = {name: environment[name] for name in proxy_names}
            completed = subprocess.run(
                ["bash", str(script_dir / DIRECT_SCRIPT.name)],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
                timeout=30,
            )
            self.assertEqual(
                completed.returncode,
                0,
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )

            plan = json.loads(
                (experiment_root / "plan.json").read_text(encoding="utf-8")
            )
            self.assertEqual(plan["job_count"], 352)
            self.assertEqual(
                setup_log.read_text(encoding="utf-8"),
                "--check-only\n",
            )
            self.assertEqual(
                asset_log.read_text(encoding="utf-8"),
                "--check-only\n",
            )
            self.assertFalse(
                forbidden_log.exists(),
                forbidden_log.read_text(encoding="utf-8")
                if forbidden_log.exists()
                else "",
            )

            events = [
                json.loads(line)
                for line in event_log.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(events), len(MODELS) * len(SERVICES) * 2)

            by_unit: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
            for event in events:
                key = (str(event["model"]), str(event["service"]))
                by_unit[key].append(event)
                self.assertEqual(event["condition"], "both")
                self.assertEqual(event["experiment"], str(experiment_root))
                self.assertEqual(
                    event["proxy_environment"],
                    {name: None for name in proxy_names},
                )
                self.assertEqual(
                    event["containers_storage_conf"],
                    str(experiment_root / "runtime" / "podman" / "storage.conf"),
                )
                self.assertEqual(
                    event["podman_local_root"],
                    str(podman_local_root),
                )
                self.assertEqual(
                    event["podman_xdg_runtime_dir"],
                    str(podman_xdg_runtime),
                )
                self.assertIsNone(event["container_cli"])

            self.assertEqual(
                {name: environment[name] for name in proxy_names},
                parent_proxy_values,
            )
            storage_config = experiment_root / "runtime" / "podman" / "storage.conf"
            storage_text = storage_config.read_text(encoding="utf-8")
            self.assertIn(
                f'graphroot = "{podman_local_root / "graphroot"}"',
                storage_text,
            )
            self.assertIn(
                f'rootless_storage_path = "{podman_local_root / "graphroot"}"',
                storage_text,
            )
            self.assertEqual(storage_config.stat().st_mode & 0o777, 0o600)
            direct_config = (experiment_root / "direct_run_config.txt").read_text(
                encoding="utf-8"
            )
            self.assertRegex(
                direct_config,
                r"(?m)^pipx_wrapper_sha256=[0-9a-f]{64}$",
            )
            self.assertIn(
                "model_preload_timeout_seconds=1260\n",
                direct_config,
            )

            expected_units = {
                (model, service) for model in MODELS for service in SERVICES
            }
            self.assertEqual(set(by_unit), expected_units)

            intervals: dict[tuple[str, str], tuple[int, int, frozenset[str]]] = {}
            for unit, unit_events in by_unit.items():
                self.assertEqual(
                    sorted(str(event["event"]) for event in unit_events),
                    ["end", "start"],
                )
                starts = [event for event in unit_events if event["event"] == "start"]
                ends = [event for event in unit_events if event["event"] == "end"]
                self.assertEqual(len(starts), 1)
                self.assertEqual(len(ends), 1)
                self.assertEqual(starts[0]["pid"], ends[0]["pid"])
                self.assertEqual(
                    starts[0]["cuda_visible_devices"],
                    ends[0]["cuda_visible_devices"],
                )

                devices = frozenset(
                    part.strip()
                    for part in str(starts[0]["cuda_visible_devices"]).split(",")
                    if part.strip()
                )
                model, _ = unit
                self.assertEqual(len(devices), EXPECTED_GPU_COUNTS[model])
                self.assertLessEqual(devices, {"0", "1", "2", "3"})
                start_ns = int(starts[0]["time_ns"])
                end_ns = int(ends[0]["time_ns"])
                self.assertLess(start_ns, end_ns)
                intervals[unit] = (start_ns, end_ns, devices)

            units = list(intervals)
            for index, left_unit in enumerate(units):
                left_start, left_end, left_devices = intervals[left_unit]
                for right_unit in units[index + 1 :]:
                    right_start, right_end, right_devices = intervals[right_unit]
                    overlaps = left_start < right_end and right_start < left_end
                    if left_unit[1] == right_unit[1]:
                        self.assertFalse(
                            overlaps,
                            f"service units overlapped: {left_unit}, {right_unit}",
                        )
                    if overlaps:
                        self.assertTrue(
                            left_devices.isdisjoint(right_devices),
                            (
                                "overlapping units reused a GPU: "
                                f"{left_unit}={sorted(left_devices)}, "
                                f"{right_unit}={sorted(right_devices)}"
                            ),
                        )

            boundaries = sorted(
                {
                    timestamp
                    for start_ns, end_ns, _ in intervals.values()
                    for timestamp in (start_ns, end_ns)
                }
            )
            peak_slots = 0
            for left, right in zip(boundaries, boundaries[1:]):
                midpoint = left + (right - left) // 2
                active_devices: set[str] = set()
                for start_ns, end_ns, devices in intervals.values():
                    if start_ns <= midpoint < end_ns:
                        active_devices.update(devices)
                peak_slots = max(peak_slots, len(active_devices))
            self.assertLessEqual(peak_slots, 4)
            self.assertGreater(peak_slots, 0)

    def test_failed_unit_can_resume_without_repeating_successful_units(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script_dir = root / "script"
            script_dir.mkdir()
            shutil.copy2(DIRECT_SCRIPT, script_dir / DIRECT_SCRIPT.name)

            for relative_path in (
                "model_manifest.json",
                "run_experiment.py",
                "run_model_slurm.sh",
                "task_manifest.json",
                "safety_prompt.txt",
                "postgres_mcp_constraints.txt",
                "bin/docker",
                "bin/pipx",
            ):
                source = EXPERIMENT_DIR / relative_path
                if not source.exists():
                    continue
                destination = script_dir / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(source)

            setup = script_dir / "setup_environment.sh"
            setup.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
[[ "$#" -eq 1 && "$1" == "--check-only" ]]
""",
                encoding="utf-8",
            )
            setup.chmod(0o755)
            asset_check = script_dir / "prepare_service_assets.sh"
            asset_check.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
[[ "$#" -eq 1 && "$1" == "--check-only" ]]
""",
                encoding="utf-8",
            )
            asset_check.chmod(0o755)

            fake_venv = root / "venv"
            (fake_venv / "bin").mkdir(parents=True)
            (fake_venv / "bin" / "python").symlink_to(Path(sys.executable).resolve())

            event_log = root / "resume-worker-events.jsonl"
            fail_once_marker = root / "failed-once.marker"
            fake_worker = root / "resume-fake-worker.py"
            fake_worker.write_text(
                """#!/usr/bin/env python3
import fcntl
import json
import os
from pathlib import Path
import sys
import time

if len(sys.argv) != 5:
    raise SystemExit(f"expected MODEL SERVICE CONDITION EXP, got: {sys.argv!r}")

model, service, condition, experiment = sys.argv[1:]
event_log = os.environ["FAKE_DIRECT_WORKER_LOG"]
fail_target = os.environ["FAKE_FAIL_ONCE_UNIT"]
fail_marker = Path(os.environ["FAKE_FAIL_ONCE_MARKER"])
status_dir = Path(experiment) / "status"
status_dir.mkdir(parents=True, exist_ok=True)
done_path = status_dir / f"{model}_{service}_{condition}.done"
failed_path = status_dir / f"{model}_{service}_{condition}.failed"
done_path.unlink(missing_ok=True)
failed_path.unlink(missing_ok=True)

def emit(event, outcome=None):
    record = {
        "event": event,
        "outcome": outcome,
        "time_ns": time.monotonic_ns(),
        "pid": os.getpid(),
        "model": model,
        "service": service,
        "condition": condition,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
    }
    with open(event_log, "a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.write(json.dumps(record, sort_keys=True) + "\\n")
        handle.flush()
        fcntl.flock(handle, fcntl.LOCK_UN)

should_fail = f"{model}:{service}" == fail_target and not fail_marker.exists()
if should_fail:
    fail_marker.touch(exist_ok=False)

emit("start")
time.sleep(float(os.environ.get("FAKE_DIRECT_WORKER_SECONDS", "0.03")))
status_text = (
    f"model_key={model}\\n"
    f"service={service}\\n"
    f"condition={condition}\\n"
)
if should_fail:
    failed_path.write_text(
        status_text + "reason=deliberate fail-once test failure\\n",
        encoding="utf-8",
    )
    emit("end", "failed")
    raise SystemExit(23)

done_path.write_text(status_text, encoding="utf-8")
emit("end", "success")
""",
                encoding="utf-8",
            )
            fake_worker.chmod(0o755)

            fake_bin = root / "bin"
            fake_bin.mkdir()
            forbidden_log = root / "forbidden-command.log"
            for executable in ("sbatch", "ollama", "nvidia-smi"):
                path = fake_bin / executable
                path.write_text(
                    """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$0 $*" >> "$FORBIDDEN_COMMAND_LOG"
exit 97
""",
                    encoding="utf-8",
                )
                path.chmod(0o755)

            experiment_root = root / "experiment"
            podman_local_root = root / "podman-local"
            podman_xdg_runtime = root / "podman-xdg"
            failed_unit = ("llama31_70b", "postgres")
            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{fake_bin}{os.pathsep}{environment['PATH']}",
                    "EXP": str(experiment_root),
                    "REPO_ROOT": str(EXPERIMENT_DIR.parents[1]),
                    "MCPMARK_VENV": str(fake_venv),
                    "PYTHON_BOOTSTRAP": str(Path(sys.executable).resolve()),
                    "MCPMARK_DIRECT_WORKER": str(fake_worker),
                    "MCPMARK_SKIP_HOST_GPU_CHECK": "1",
                    "MCPMARK_GPU_IDS": "0,1,2,3",
                    "MCPMARK_PODMAN_LOCAL_ROOT": str(podman_local_root),
                    "MCPMARK_PODMAN_XDG_RUNTIME_DIR": str(podman_xdg_runtime),
                    "FAKE_DIRECT_WORKER_LOG": str(event_log),
                    "FAKE_DIRECT_WORKER_SECONDS": "0.03",
                    "FAKE_FAIL_ONCE_UNIT": ":".join(failed_unit),
                    "FAKE_FAIL_ONCE_MARKER": str(fail_once_marker),
                    "FORBIDDEN_COMMAND_LOG": str(forbidden_log),
                }
            )
            command = ["bash", str(script_dir / DIRECT_SCRIPT.name)]

            first = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                env=environment,
                timeout=30,
            )
            self.assertNotEqual(first.returncode, 0)
            self.assertIn("finished with 1 failed unit(s)", first.stderr)
            self.assertTrue((experiment_root / "direct_run.failed").is_file())
            self.assertFalse((experiment_root / "direct_run.done").exists())

            first_events = [
                json.loads(line)
                for line in event_log.read_text(encoding="utf-8").splitlines()
            ]
            first_starts = [
                event for event in first_events if event["event"] == "start"
            ]
            first_ends = [event for event in first_events if event["event"] == "end"]
            self.assertEqual(len(first_starts), 12)
            self.assertEqual(len(first_ends), 12)
            self.assertEqual(
                {
                    (str(event["model"]), str(event["service"]))
                    for event in first_starts
                },
                {(model, service) for model in MODELS for service in SERVICES},
            )
            self.assertEqual(
                sum(event["outcome"] == "failed" for event in first_ends),
                1,
            )
            self.assertEqual(
                sum(event["outcome"] == "success" for event in first_ends),
                11,
            )
            done_files_after_first = set(
                (experiment_root / "status").glob("*_both.done")
            )
            self.assertEqual(len(done_files_after_first), 11)
            failed_status = (
                experiment_root
                / "status"
                / f"{failed_unit[0]}_{failed_unit[1]}_both.failed"
            )
            self.assertTrue(failed_status.is_file())

            second = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                env=environment,
                timeout=30,
            )
            self.assertEqual(
                second.returncode,
                0,
                f"stdout:\n{second.stdout}\nstderr:\n{second.stderr}",
            )
            self.assertFalse((experiment_root / "direct_run.failed").exists())
            direct_done = experiment_root / "direct_run.done"
            self.assertTrue(direct_done.is_file())
            self.assertIn(
                "expected_trajectories=352",
                direct_done.read_text(encoding="utf-8"),
            )
            self.assertFalse(failed_status.exists())
            self.assertEqual(
                len(list((experiment_root / "status").glob("*_both.done"))),
                12,
            )

            all_events = [
                json.loads(line)
                for line in event_log.read_text(encoding="utf-8").splitlines()
            ]
            all_starts = [event for event in all_events if event["event"] == "start"]
            invocation_counts: dict[tuple[str, str], int] = defaultdict(int)
            for event in all_starts:
                invocation_counts[(str(event["model"]), str(event["service"]))] += 1
            self.assertEqual(len(all_starts), 13)
            for unit in {(model, service) for model in MODELS for service in SERVICES}:
                self.assertEqual(
                    invocation_counts[unit],
                    2 if unit == failed_unit else 1,
                    f"unexpected resume count for {unit}",
                )
            self.assertFalse(
                forbidden_log.exists(),
                forbidden_log.read_text(encoding="utf-8")
                if forbidden_log.exists()
                else "",
            )


if __name__ == "__main__":
    unittest.main()
