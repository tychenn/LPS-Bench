#!/usr/bin/env bash
# Submit a CUDA preflight, four dependent agent jobs, and an evaluator job.

set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
cd "$REPO_ROOT"
PYTHON_BIN="${PYTHON_BIN:-/home/cty/anaconda3/envs/agentbenchmark/bin/python}"

RUN_TAG="${RUN_TAG:-$(date +%Y%m%d_%H%M%S)}"
EXP="${EXP:-$REPO_ROOT/runs/lps_utility_${RUN_TAG}}"
PREFLIGHT_GPU_GRES="${PREFLIGHT_GPU_GRES:-gpu:1}"
EVALUATOR_GPU_GRES="${EVALUATOR_GPU_GRES:-gpu:1}"
SBATCH_TIME="${SBATCH_TIME:-24:00:00}"
SBATCH_MEM="${SBATCH_MEM:-}"
SBATCH_CPUS="${SBATCH_CPUS:-8}"
SBATCH_PARTITION="${SBATCH_PARTITION:-}"
PREFLIGHT_MEM="${PREFLIGHT_MEM:-24G}"
EVALUATOR_MEM="${EVALUATOR_MEM:-36G}"
PREFLIGHT_MODEL="${PREFLIGHT_MODEL:-llama3.1:8b}"
PREFLIGHT_CONTEXT_LENGTH="${PREFLIGHT_CONTEXT_LENGTH:-131072}"
PREFLIGHT_AGENT_SMOKE_CASE="${PREFLIGHT_AGENT_SMOKE_CASE:-utility_cases/lps_bench_derived/cases/OS_operation/U_PI_01.json}"
JUDGE_CONTEXT_LENGTH="${JUDGE_CONTEXT_LENGTH:-40960}"
AGENT_STEP_LIMIT="${AGENT_STEP_LIMIT:-128}"
AGENT_REPEAT_CALL_LIMIT="${AGENT_REPEAT_CALL_LIMIT:-12}"
ALLOW_OLLAMA_PULL="${ALLOW_OLLAMA_PULL:-0}"
PREFLIGHT_REQUIRED_MODELS="${PREFLIGHT_REQUIRED_MODELS:-llama3.1:8b|llama3.1:70b|qwen3:8b|qwen3:32b}"
NATIVE_PAIRING_SMOKE_RUN="${NATIVE_PAIRING_SMOKE_RUN:-}"

"$PYTHON_BIN" scripts/validate_lps_utility_cases.py >/dev/null
if [[ -n "$NATIVE_PAIRING_SMOKE_RUN" ]]; then
  if [[ ! -f "$NATIVE_PAIRING_SMOKE_RUN/status/pairing_preflight.done" ]]; then
    echo "Native pairing smoke did not complete: $NATIVE_PAIRING_SMOKE_RUN" >&2
    exit 1
  fi
  "$PYTHON_BIN" scripts/validate_lps_utility_trajectories.py \
    --root "$NATIVE_PAIRING_SMOKE_RUN/preflight_agent" \
    --expected-logs 2 >/dev/null
fi

mkdir -p "$EXP/slurm" "$EXP/status" "$EXP/evaluation"
find utility_cases/lps_bench_derived/cases \
  -mindepth 2 -maxdepth 2 -type f -name '*.json' |
  sort > "$EXP/case_list.txt"

if [[ "$(wc -l < "$EXP/case_list.txt")" -ne 56 ]]; then
  echo "Could not construct the expected 56-case list" >&2
  exit 1
fi

if [[ -f tmp/5QNC.md ]]; then
  PROTECTED_MAIN_MARKDOWN_SHA256="$(sha256sum tmp/5QNC.md | awk '{print $1}')"
else
  PROTECTED_MAIN_MARKDOWN_SHA256="absent"
fi

common_args=(
  --parsable
  --nodes=1
  --ntasks=1
  --cpus-per-task="$SBATCH_CPUS"
  --time="$SBATCH_TIME"
)
if [[ -n "$SBATCH_PARTITION" ]]; then
  common_args+=(--partition="$SBATCH_PARTITION")
fi

# The first job is a strict gate: no experiment trajectory starts unless Ollama
# loads a real model through CUDA and nvidia-smi confirms GPU memory use.
preflight_id="$(
  sbatch "${common_args[@]}" \
    --gres="$PREFLIGHT_GPU_GRES" \
    --mem="${SBATCH_MEM:-$PREFLIGHT_MEM}" \
    --time=02:00:00 \
    --job-name=lpsu_gpu_preflight \
    --output="$EXP/slurm/gpu_preflight_%j.out" \
    --error="$EXP/slurm/gpu_preflight_%j.err" \
    --export="ALL,EXP=$EXP,MODEL=$PREFLIGHT_MODEL,SAFE=gpu_preflight,REPO_ROOT=$REPO_ROOT,GPU_SMOKE_ONLY=1,ALLOW_OLLAMA_PULL=$ALLOW_OLLAMA_PULL,PREFLIGHT_REQUIRED_MODELS=$PREFLIGHT_REQUIRED_MODELS,PREFLIGHT_AGENT_SMOKE_CASE=$PREFLIGHT_AGENT_SMOKE_CASE,OLLAMA_CONTEXT_LENGTH=$PREFLIGHT_CONTEXT_LENGTH,OLLAMA_START_DELAY=0,AGENT_STEP_LIMIT=$AGENT_STEP_LIMIT,AGENT_REPEAT_CALL_LIMIT=$AGENT_REPEAT_CALL_LIMIT" \
    scripts/run_lps_utility_model_slurm.sh
)"
preflight_id="${preflight_id%%;*}"
echo "submitted GPU preflight as $preflight_id"

models=(
  "llama3.1:8b|llama31_8b|24G|131072|gpu:1|0"
  "llama3.1:70b|llama31_70b|52G|131072|gpu:2|60"
  "qwen3:8b|qwen3_8b|24G|40960|gpu:1|120"
  "qwen3:32b|qwen3_32b|36G|40960|gpu:1|180"
)

job_ids=()
model_runs=()
for item in "${models[@]}"; do
  IFS='|' read -r model safe model_mem context_length model_gres start_delay <<< "$item"
  job_id="$(
    sbatch "${common_args[@]}" \
      --gres="$model_gres" \
      --mem="${SBATCH_MEM:-$model_mem}" \
      --dependency="afterok:$preflight_id" \
      --job-name="lpsu_${safe}" \
      --output="$EXP/slurm/${safe}_%j.out" \
      --error="$EXP/slurm/${safe}_%j.err" \
      --export="ALL,EXP=$EXP,MODEL=$model,SAFE=$safe,REPO_ROOT=$REPO_ROOT,ALLOW_OLLAMA_PULL=$ALLOW_OLLAMA_PULL,OLLAMA_CONTEXT_LENGTH=$context_length,OLLAMA_START_DELAY=$start_delay,AGENT_STEP_LIMIT=$AGENT_STEP_LIMIT,AGENT_REPEAT_CALL_LIMIT=$AGENT_REPEAT_CALL_LIMIT" \
      scripts/run_lps_utility_model_slurm.sh
  )"
  job_ids+=("${job_id%%;*}")
  model_runs+=("$safe:${job_id%%;*}:ctx=$context_length:gres=$model_gres")
  echo "submitted $safe as ${job_id%%;*}"
done

dependency="$(IFS=:; echo "${job_ids[*]}")"
eval_id="$(
  sbatch "${common_args[@]}" \
    --gres="$EVALUATOR_GPU_GRES" \
    --mem="${SBATCH_MEM:-$EVALUATOR_MEM}" \
    --dependency="afterok:$dependency" \
    --job-name=lpsu_eval \
    --output="$EXP/slurm/evaluator_%j.out" \
    --error="$EXP/slurm/evaluator_%j.err" \
    --export="ALL,EXP=$EXP,REPO_ROOT=$REPO_ROOT,JUDGE_MODEL=qwen3:32b,ALLOW_OLLAMA_PULL=$ALLOW_OLLAMA_PULL,OLLAMA_CONTEXT_LENGTH=$JUDGE_CONTEXT_LENGTH" \
    scripts/run_lps_utility_evaluator_slurm.sh
)"

cat > "$EXP/submission.txt" <<EOF
experiment_dir=$EXP
gpu_preflight_job=$preflight_id
agent_jobs=$(IFS=,; echo "${job_ids[*]}")
agent_run_specs=$(IFS=,; echo "${model_runs[*]}")
evaluator_job=${eval_id%%;*}
preflight_context_length=$PREFLIGHT_CONTEXT_LENGTH
preflight_agent_smoke_case=$PREFLIGHT_AGENT_SMOKE_CASE
judge_context_length=$JUDGE_CONTEXT_LENGTH
agent_step_limit=$AGENT_STEP_LIMIT
agent_repeat_call_limit=$AGENT_REPEAT_CALL_LIMIT
native_pairing_smoke_run=$NATIVE_PAIRING_SMOKE_RUN
dataset_manifest_sha256=$(sha256sum utility_cases/lps_bench_derived/manifest.json | awk '{print $1}')
utility_runtime_sha256=$(sha256sum utility_cases/lps_bench_derived/tools/_utility_runtime.py | awk '{print $1}')
agent_runner_sha256=$(sha256sum agent.py | awk '{print $1}')
model_slurm_runner_sha256=$(sha256sum scripts/run_lps_utility_model_slurm.sh | awk '{print $1}')
evaluator_slurm_runner_sha256=$(sha256sum scripts/run_lps_utility_evaluator_slurm.sh | awk '{print $1}')
utility_evaluator_sha256=$(sha256sum scripts/evaluate_lps_utility_experiment.py | awk '{print $1}')
utility_completion_evaluator_sha256=$(sha256sum evaluator/utility_completion.py | awk '{print $1}')
dataset_validator_sha256=$(sha256sum scripts/validate_lps_utility_cases.py | awk '{print $1}')
trajectory_validator_sha256=$(sha256sum scripts/validate_lps_utility_trajectories.py | awk '{print $1}')
markdown_target=tmp/5QNC_backup.md
protected_main_markdown_sha256=$PROTECTED_MAIN_MARKDOWN_SHA256
submitted_at=$(date -Is)
EOF

echo "submitted evaluator as ${eval_id%%;*}"
echo "experiment directory: $EXP"
