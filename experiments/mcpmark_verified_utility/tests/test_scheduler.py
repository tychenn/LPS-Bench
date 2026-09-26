import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SUBMIT_SCRIPT = EXPERIMENT_DIR / "submit_experiment.sh"
MODELS = ("llama31_8b", "llama31_70b", "qwen3_8b", "qwen3_32b")
SERVICES = ("filesystem", "postgres", "playwright")
CONDITIONS = ("original", "safety")


class SchedulerTests(unittest.TestCase):
    def test_submit_builds_three_independent_eight_job_chains(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            # Exercise the production submit script from an isolated script
            # directory.  Only its environment-check dependency is replaced:
            # scheduler behavior still comes from the real submit script and
            # validate/plan behavior still comes from the real runner.
            script_dir = root / "script"
            script_dir.mkdir()
            shutil.copy2(SUBMIT_SCRIPT, script_dir / SUBMIT_SCRIPT.name)
            for relative_path in (
                "model_manifest.json",
                "run_experiment.py",
                "run_model_slurm.sh",
                "task_manifest.json",
                "safety_prompt.txt",
                "postgres_mcp_constraints.txt",
                "bin/pipx",
            ):
                destination = script_dir / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(EXPERIMENT_DIR / relative_path)

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

            fake_bin = root / "bin"
            fake_bin.mkdir()
            counter = root / "counter"
            counter.write_text("1000\n", encoding="utf-8")
            log = root / "sbatch.log"

            sbatch = fake_bin / "sbatch"
            sbatch.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
counter="$(<"$FAKE_SBATCH_COUNTER")"
counter=$((counter + 1))
printf '%s\n' "$counter" > "$FAKE_SBATCH_COUNTER"
printf '%s\t' "$@" >> "$FAKE_SBATCH_LOG"
printf '\n' >> "$FAKE_SBATCH_LOG"
printf '%s\n' "$counter"
""",
                encoding="utf-8",
            )
            sbatch.chmod(0o755)
            for executable in ("psql", "pg_restore"):
                path = fake_bin / executable
                path.write_text(
                    "#!/usr/bin/env bash\nexit 0\n",
                    encoding="utf-8",
                )
                path.chmod(0o755)

            experiment_root = root / "experiment"
            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{fake_bin}{os.pathsep}{environment['PATH']}",
                    "EXP": str(experiment_root),
                    "FAKE_SBATCH_COUNTER": str(counter),
                    "FAKE_SBATCH_LOG": str(log),
                    "FAKE_SETUP_LOG": str(setup_log),
                    "FAKE_ASSET_LOG": str(asset_log),
                    "MCPMARK_VENV": str(fake_venv),
                    "PYTHON_BOOTSTRAP": str(Path(sys.executable).resolve()),
                    "SBATCH_TIME": "24:00:00",
                    "PLAYWRIGHT_SBATCH_TIME": "48:00:00",
                }
            )
            completed = subprocess.run(
                ["bash", str(script_dir / SUBMIT_SCRIPT.name)],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            plan = json.loads(
                (experiment_root / "plan.json").read_text(encoding="utf-8")
            )
            self.assertEqual(plan["job_count"], 352)
            records = (experiment_root / "submission.txt").read_text(encoding="utf-8")
            self.assertEqual(records.count("submitted_job="), 24)
            self.assertEqual(records.count("service_tail_"), 3)
            self.assertIn("plan_job_count=352", records)
            self.assertFalse((experiment_root / "submission.in_progress").exists())
            self.assertEqual(
                setup_log.read_text(encoding="utf-8"),
                "--check-only\n",
            )
            self.assertEqual(
                asset_log.read_text(encoding="utf-8"),
                "--check-only\n",
            )

            invocations = [
                line.rstrip("\n").split("\t")
                for line in log.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(invocations), 24)
            job_id = 1000
            tails: dict[str, int] = {}
            index = 0
            for model in MODELS:
                for service in SERVICES:
                    for condition in CONDITIONS:
                        job_id += 1
                        arguments = invocations[index]
                        index += 1
                        self.assertIn(
                            f"--job-name=mcpv_{model}_{service}_{condition}",
                            arguments,
                        )
                        self.assertIn(
                            (
                                f"--output={experiment_root}/logs/"
                                f"{model}_{service}_{condition}_%j.out"
                            ),
                            arguments,
                        )
                        self.assertIn(
                            (
                                f"--error={experiment_root}/logs/"
                                f"{model}_{service}_{condition}_%j.err"
                            ),
                            arguments,
                        )
                        self.assertIn(
                            (
                                "--time=48:00:00"
                                if service == "playwright"
                                else "--time=24:00:00"
                            ),
                            arguments,
                        )
                        self.assertEqual(
                            arguments[-6:-1],
                            [
                                str(script_dir / "run_model_slurm.sh"),
                                model,
                                service,
                                condition,
                                str(experiment_root),
                            ],
                        )
                        dependencies = [
                            argument
                            for argument in arguments
                            if argument.startswith("--dependency=")
                        ]
                        if service in tails:
                            self.assertEqual(
                                dependencies,
                                [f"--dependency=afterany:{tails[service]}"],
                            )
                        else:
                            self.assertEqual(dependencies, [])
                        tails[service] = job_id

            self.assertEqual(set(tails), set(SERVICES))

            repeated = subprocess.run(
                ["bash", str(script_dir / SUBMIT_SCRIPT.name)],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn("already has a submission record", repeated.stderr)


if __name__ == "__main__":
    unittest.main()
