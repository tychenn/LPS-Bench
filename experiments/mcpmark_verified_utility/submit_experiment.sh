#!/usr/bin/env bash
# Submit 24 jobs: all model/condition jobs are serialized within each service.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
MODEL_MANIFEST="$SCRIPT_DIR/model_manifest.json"
PYTHON_BOOTSTRAP="${PYTHON_BOOTSTRAP:-python3}"
RUN_TAG="${RUN_TAG:-$(date +%Y%m%d_%H%M%S)}"
EXP="${EXP:-$REPO_ROOT/runs/mcpmark_verified_utility_${RUN_TAG}}"
SBATCH_CPUS="${SBATCH_CPUS:-8}"
SBATCH_TIME="${SBATCH_TIME:-24:00:00}"
PLAYWRIGHT_SBATCH_TIME="${PLAYWRIGHT_SBATCH_TIME:-24:00:00}"
SBATCH_PARTITION="${SBATCH_PARTITION:-}"
SBATCH_MEMORY_OVERRIDE="${SBATCH_MEMORY_OVERRIDE:-}"
MCPMARK_STRICT_GPU_CHECK="${MCPMARK_STRICT_GPU_CHECK:-1}"

if [[ "$MCPMARK_STRICT_GPU_CHECK" != "0" ]] &&
  [[ "$MCPMARK_STRICT_GPU_CHECK" != "1" ]]; then
  echo "MCPMARK_STRICT_GPU_CHECK must be 0 or 1." >&2
  exit 2
fi

if ! command -v sbatch >/dev/null 2>&1; then
  echo "sbatch is unavailable; submit this script from a Slurm login node." >&2
  exit 1
fi
EFFECTIVE_VENV="${MCPMARK_VENV:-$SCRIPT_DIR/.venv}"
if [[ ! -x "$EFFECTIVE_VENV/bin/python" ]]; then
  echo "Experiment venv is missing: $EFFECTIVE_VENV" >&2
  echo "Run $SCRIPT_DIR/setup_environment.sh first." >&2
  exit 1
fi
if [[ ! -f "$SCRIPT_DIR/run_experiment.py" ]]; then
  echo "Experiment runner is missing: $SCRIPT_DIR/run_experiment.py" >&2
  exit 1
fi
if [[ -e "$EXP/submission.txt" || -e "$EXP/submission.in_progress" ]]; then
  echo "Experiment directory already has a submission record: $EXP" >&2
  echo "Use a new EXP, or inspect/cancel the recorded jobs before resubmitting." >&2
  exit 1
fi

"$SCRIPT_DIR/setup_environment.sh" --check-only
"$SCRIPT_DIR/prepare_service_assets.sh" --check-only
"$EFFECTIVE_VENV/bin/python" "$SCRIPT_DIR/run_experiment.py" validate

mapfile -t MODEL_KEYS < <(
  "$PYTHON_BOOTSTRAP" - "$MODEL_MANIFEST" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    models = json.load(handle)["models"]
print(*models, sep="\n")
PY
)
SERVICES=(filesystem postgres playwright)
CONDITIONS=(original safety)

mkdir -p "$EXP/logs" "$EXP/status" "$EXP/results"
PLAN_PATH="$EXP/plan.json"
"$EFFECTIVE_VENV/bin/python" "$SCRIPT_DIR/run_experiment.py" plan \
  --output "$PLAN_PATH" \
  --models all \
  --conditions all \
  --services all \
  --k 1

PLAN_JOB_COUNT="$(
  "$PYTHON_BOOTSTRAP" - "$PLAN_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    print(json.load(handle)["job_count"])
PY
)"
if [[ "$PLAN_JOB_COUNT" != "352" ]]; then
  echo "Frozen plan must contain exactly 352 jobs, found: $PLAN_JOB_COUNT" >&2
  exit 1
fi
SUBMISSION_RECORD="$EXP/submission.in_progress"
if ! (set -o noclobber; : > "$SUBMISSION_RECORD") 2>/dev/null; then
  echo "Another submission already owns: $SUBMISSION_RECORD" >&2
  exit 1
fi
{
  printf 'experiment_dir=%s\n' "$EXP"
  printf 'submission_started_at=%s\n' "$(date -Is)"
  printf 'task_manifest_sha256=%s\n' "$(sha256sum "$SCRIPT_DIR/task_manifest.json" | awk '{print $1}')"
  printf 'model_manifest_sha256=%s\n' "$(sha256sum "$MODEL_MANIFEST" | awk '{print $1}')"
  printf 'runner_sha256=%s\n' "$(sha256sum "$SCRIPT_DIR/run_experiment.py" | awk '{print $1}')"
  printf 'slurm_runner_sha256=%s\n' "$(sha256sum "$SCRIPT_DIR/run_model_slurm.sh" | awk '{print $1}')"
  printf 'pipx_shim_sha256=%s\n' "$(sha256sum "$SCRIPT_DIR/bin/pipx" | awk '{print $1}')"
  printf 'postgres_constraints_sha256=%s\n' "$(sha256sum "$SCRIPT_DIR/postgres_mcp_constraints.txt" | awk '{print $1}')"
  printf 'plan_sha256=%s\n' "$(sha256sum "$PLAN_PATH" | awk '{print $1}')"
  printf 'plan_job_count=%s\n' "$PLAN_JOB_COUNT"
  printf 'strict_gpu_check=%s\n' "$MCPMARK_STRICT_GPU_CHECK"
  printf 'default_walltime=%s\n' "$SBATCH_TIME"
  printf 'playwright_walltime=%s\n' "$PLAYWRIGHT_SBATCH_TIME"
} >> "$SUBMISSION_RECORD"

common_args=(
  --parsable
  --nodes=1
  --ntasks=1
  --cpus-per-task="$SBATCH_CPUS"
)
if [[ -n "$SBATCH_PARTITION" ]]; then
  common_args+=(--partition="$SBATCH_PARTITION")
fi

declare -A service_tail=()
job_records=()

for model_key in "${MODEL_KEYS[@]}"; do
  IFS=$'\t' read -r served_model gres memory < <(
    "$PYTHON_BOOTSTRAP" - "$MODEL_MANIFEST" "$model_key" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    model = json.load(handle)["models"][sys.argv[2]]
print(model["served_model"], model["slurm_gres"], model["slurm_memory"], sep="\t")
PY
  )

  for service in "${SERVICES[@]}"; do
    for condition in "${CONDITIONS[@]}"; do
      submit_args=("${common_args[@]}" --gres="$gres")
      job_time="$SBATCH_TIME"
      if [[ "$service" == "playwright" ]]; then
        job_time="$PLAYWRIGHT_SBATCH_TIME"
      fi
      submit_args+=(--time="$job_time")
      submit_args+=(--mem="${SBATCH_MEMORY_OVERRIDE:-$memory}")
      submit_args+=(--job-name="mcpv_${model_key}_${service}_${condition}")
      submit_args+=(
        --output="$EXP/logs/${model_key}_${service}_${condition}_%j.out"
      )
      submit_args+=(
        --error="$EXP/logs/${model_key}_${service}_${condition}_%j.err"
      )
      if [[ -n "${service_tail[$service]:-}" ]]; then
        submit_args+=(--dependency="afterany:${service_tail[$service]}")
      fi

      raw_job_id="$(
        sbatch "${submit_args[@]}" \
          "$SCRIPT_DIR/run_model_slurm.sh" \
          "$model_key" "$service" "$condition" "$EXP"
      )"
      job_id="${raw_job_id%%;*}"
      service_tail[$service]="$job_id"
      job_records+=(
        "$model_key:$served_model:$service:$condition:$job_id"
      )
      printf 'submitted_job=%s:%s:%s:%s:%s\n' \
        "$model_key" "$served_model" "$service" "$condition" "$job_id" \
        >> "$SUBMISSION_RECORD"
      echo \
        "submitted model=$model_key service=$service condition=$condition job=$job_id"
    done
  done
done

{
  printf 'submission_completed_at=%s\n' "$(date -Is)"
  printf 'jobs=%s\n' "$(IFS=,; echo "${job_records[*]}")"
  for service in "${SERVICES[@]}"; do
    printf 'service_tail_%s=%s\n' "$service" "${service_tail[$service]}"
  done
} >> "$SUBMISSION_RECORD"
mv "$SUBMISSION_RECORD" "$EXP/submission.txt"

echo "Experiment directory: $EXP"
echo "All model/condition jobs are serialized within each logical service."
