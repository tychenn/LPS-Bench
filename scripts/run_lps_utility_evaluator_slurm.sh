#!/usr/bin/env bash
# Evaluate all completed utility trajectories with one fixed local judge.

set -euo pipefail

: "${EXP:?EXP must point to the experiment directory}"

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
PYTHON_BIN="${PYTHON_BIN:-/home/cty/anaconda3/envs/agentbenchmark/bin/python}"
JUDGE_MODEL="${JUDGE_MODEL:-qwen3:32b}"
ALLOW_OLLAMA_PULL="${ALLOW_OLLAMA_PULL:-0}"

cd "$REPO_ROOT"
mkdir -p "$EXP/slurm" "$EXP/status" "$EXP/evaluation"

export LANGCHAIN_TRACING_V2=false
export LANGCHAIN_TRACING=false
export LANGSMITH_TRACING=false
export OLLAMA_NUM_PREDICT="${JUDGE_NUM_PREDICT:-384}"
export OLLAMA_CLIENT_TIMEOUT="${OLLAMA_CLIENT_TIMEOUT:-300}"
export OLLAMA_REASONING=false
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-30m}"
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_FLASH_ATTENTION="${OLLAMA_FLASH_ATTENTION:-true}"
export OLLAMA_KV_CACHE_TYPE="${OLLAMA_KV_CACHE_TYPE:-q8_0}"
export OLLAMA_SCHED_SPREAD="${OLLAMA_SCHED_SPREAD:-true}"
export OLLAMA_NO_CLOUD=true
export OLLAMA_DEBUG="${OLLAMA_DEBUG:-1}"
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:?OLLAMA_CONTEXT_LENGTH must be set explicitly}"
export OLLAMA_LOAD_TIMEOUT="${OLLAMA_LOAD_TIMEOUT:-20m}"
export OLLAMA_LLM_LIBRARY="${OLLAMA_CUDA_LIBRARY:-cuda_v12}"
export OLLAMA_VULKAN="${LPS_OLLAMA_VULKAN:-false}"
OLLAMA_SERVER_BYPASS_PROXY="${OLLAMA_SERVER_BYPASS_PROXY:-1}"

JOB_ID="${SLURM_JOB_ID:-$$}"
export OLLAMA_HOST="127.0.0.1:$((20000 + JOB_ID % 20000))"
export NO_PROXY="127.0.0.1,localhost,${NO_PROXY:-}"
export no_proxy="127.0.0.1,localhost,${no_proxy:-}"

OLLAMA_LOG="$EXP/slurm/evaluator_ollama_${JOB_ID}.log"
GPU_STATUS="$EXP/status/evaluation.gpu_verified"
FAILED_STATUS="$EXP/status/evaluation.failed"
JUDGMENTS_PATH="$EXP/evaluation/utility_judgments.jsonl"
CONTEXT_VERIFIED_STATUS="$EXP/status/evaluation.context_verified"
OLLAMA_PID=""

fail_job() {
  local reason="$1"
  printf '%s\n' \
    "judge_model=$JUDGE_MODEL" \
    "failed_at=$(date -Is)" \
    "job_id=$JOB_ID" \
    "reason=$reason" > "$FAILED_STATUS"
  echo "[$(date -Is)] ERROR: $reason" >&2
  exit 1
}

if [[ -s "$JUDGMENTS_PATH" ]]; then
  if [[ ! -s "$CONTEXT_VERIFIED_STATUS" ]]; then
    fail_job "cached judgments exist without a context-verification marker; use a fresh EXP"
  fi
  recorded_judgments_sha256="$(
    awk -F= '$1 == "judgments_sha256" { print $2 }' "$CONTEXT_VERIFIED_STATUS"
  )"
  actual_judgments_sha256="$(sha256sum "$JUDGMENTS_PATH" | awk '{print $1}')"
  if [[ -z "$recorded_judgments_sha256" ||
    "$recorded_judgments_sha256" != "$actual_judgments_sha256" ]]; then
    fail_job "cached judgments changed after context verification; use a fresh EXP"
  fi
fi

echo "[$(date -Is)] evaluator job=$JOB_ID judge=$JUDGE_MODEL host=$(hostname)"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-<unset>}"
echo "OLLAMA_LLM_LIBRARY=$OLLAMA_LLM_LIBRARY OLLAMA_VULKAN=$OLLAMA_VULKAN OLLAMA_CONTEXT_LENGTH=$OLLAMA_CONTEXT_LENGTH"
if [[ -z "${CUDA_VISIBLE_DEVICES:-}" ]]; then
  fail_job "CUDA_VISIBLE_DEVICES is unset; this is not a GPU allocation"
fi
if ! [[ "$OLLAMA_CONTEXT_LENGTH" =~ ^[1-9][0-9]*$ ]]; then
  fail_job "OLLAMA_CONTEXT_LENGTH must be a positive integer"
fi
if ! command -v nvidia-smi >/dev/null 2>&1 || ! nvidia-smi; then
  fail_job "nvidia-smi could not communicate with the allocated GPU"
fi

# See the model runner for details: cold-loading Ollama's bundled CUDA backend
# can exceed its fixed 30-second GPU-discovery watchdog on these nodes.
OLLAMA_BIN="$(readlink -f "$(command -v ollama)")"
OLLAMA_LIBRARY_ROOT="${OLLAMA_LIBRARY_ROOT:-$(cd "$(dirname "$OLLAMA_BIN")/../lib/ollama" && pwd)}"
OLLAMA_CUDA_DIR="$OLLAMA_LIBRARY_ROOT/$OLLAMA_LLM_LIBRARY"
if [[ ! -d "$OLLAMA_CUDA_DIR" ]]; then
  fail_job "requested CUDA backend directory does not exist: $OLLAMA_CUDA_DIR"
fi
echo "[$(date -Is)] warming CUDA backend files from $OLLAMA_CUDA_DIR"
while IFS= read -r -d '' cuda_library; do
  if ! timeout 180 dd \
    if="$cuda_library" \
    of=/dev/null \
    bs=16M \
    status=none; then
    fail_job "could not warm CUDA backend file: $cuda_library"
  fi
done < <(find "$OLLAMA_CUDA_DIR" -maxdepth 1 -type f -print0)

unset \
  ROCR_VISIBLE_DEVICES \
  HIP_VISIBLE_DEVICES \
  GPU_DEVICE_ORDINAL \
  HSA_OVERRIDE_GFX_VERSION \
  GGML_VK_VISIBLE_DEVICES

cleanup() {
  if [[ -n "$OLLAMA_PID" ]]; then
    kill "$OLLAMA_PID" 2>/dev/null || true
    wait "$OLLAMA_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

ready=0
for launch_attempt in 1 2 3; do
  attempt_log="${OLLAMA_LOG%.log}_attempt${launch_attempt}.log"
  ln -sfn "$(basename "$attempt_log")" "$OLLAMA_LOG"
  if [[ "$OLLAMA_SERVER_BYPASS_PROXY" == "1" ]]; then
    env \
      -u HTTP_PROXY \
      -u HTTPS_PROXY \
      -u http_proxy \
      -u https_proxy \
      ollama serve > "$attempt_log" 2>&1 &
  else
    ollama serve > "$attempt_log" 2>&1 &
  fi
  OLLAMA_PID=$!

  ready=0
  for _ in {1..90}; do
    if ollama list >/dev/null 2>&1; then
      ready=1
      break
    fi
    if ! kill -0 "$OLLAMA_PID" 2>/dev/null; then
      break
    fi
    sleep 2
  done
  if [[ "$ready" -eq 1 ]] &&
    grep -Eqi 'inference compute.*library=CUDA' "$attempt_log"; then
    break
  fi
  echo "[$(date -Is)] evaluator Ollama launch attempt $launch_attempt failed CUDA discovery" >&2
  tail -n 160 "$attempt_log" >&2 || true
  kill "$OLLAMA_PID" 2>/dev/null || true
  wait "$OLLAMA_PID" 2>/dev/null || true
  OLLAMA_PID=""
  ready=0
  sleep 5
done
if [[ "$ready" -ne 1 ]]; then
  tail -n 120 "$OLLAMA_LOG" >&2 || true
  fail_job "evaluator Ollama server did not become ready with CUDA after 3 attempts"
fi

if ! ollama show "$JUDGE_MODEL" >/dev/null 2>&1; then
  if [[ "$ALLOW_OLLAMA_PULL" == "1" ]]; then
    if ! ollama pull "$JUDGE_MODEL"; then
      fail_job "required judge model $JUDGE_MODEL could not be pulled"
    fi
  else
    fail_job "required judge model is missing: $JUDGE_MODEL"
  fi
fi

# Verify the judge itself is loaded through CUDA before evaluating 448 logs.
if ! printf \
  '{"model":"%s","prompt":"Reply with OK.","stream":false,"keep_alive":"30m","options":{"num_ctx":%s,"num_predict":1,"temperature":0}}' \
  "$JUDGE_MODEL" "$OLLAMA_CONTEXT_LENGTH" |
  curl \
    --fail \
    --silent \
    --show-error \
    --max-time 600 \
    --header 'Content-Type: application/json' \
    --data-binary @- \
    "http://$OLLAMA_HOST/api/generate" > "$EXP/status/evaluation.gpu_smoke_response.json"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "judge model smoke request failed or timed out"
fi

OLLAMA_PS="$(ollama ps)"
printf '%s\n' "$OLLAMA_PS"
if ! printf '%s\n' "$OLLAMA_PS" |
  awk -v model="$JUDGE_MODEL" -v context="$OLLAMA_CONTEXT_LENGTH" '
    NR > 1 &&
    $1 == model &&
    toupper($0) ~ /100%[[:space:]]+GPU/ &&
    $0 ~ ("(^|[[:space:]])" context "([[:space:]]|$)") { found = 1 }
    END { exit(found ? 0 : 1) }
  '; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "ollama ps does not report 100% GPU execution at context $OLLAMA_CONTEXT_LENGTH for judge $JUDGE_MODEL"
fi
if ! grep -Eqi \
  'inference compute.*library=CUDA|loaded CUDA backend|device=CUDA|offload(ed|ing).*(layer|weight).*GPU' \
  "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "judge Ollama log contains no CUDA backend or GPU-offload evidence"
fi

NVIDIA_COMPUTE_APPS="$(
  nvidia-smi \
    --query-compute-apps=pid,process_name,used_gpu_memory \
    --format=csv,noheader 2>/dev/null || true
)"
if [[ -z "$NVIDIA_COMPUTE_APPS" ]]; then
  fail_job "nvidia-smi reports no process holding GPU memory for the judge"
fi
if ! awk '
  /load_tensors: offloaded [0-9]+\/[0-9]+ layers to GPU/ {
    split($3, counts, "/")
    if (counts[1] == counts[2]) {
      fully_offloaded = 1
    }
  }
  END { exit(fully_offloaded ? 0 : 1) }
' "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "not all judge model layers were offloaded to GPU"
fi
if ! grep -Eq \
  "llama_context: n_ctx[[:space:]]+=[[:space:]]+${OLLAMA_CONTEXT_LENGTH}$" \
  "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "judge runtime context does not match $OLLAMA_CONTEXT_LENGTH"
fi
if ! grep -Eq \
  "print_info: n_ctx_train[[:space:]]+=[[:space:]]+${OLLAMA_CONTEXT_LENGTH}$" \
  "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "$OLLAMA_CONTEXT_LENGTH is not the judge model's native context limit"
fi
{
  printf '%s\n' \
    "judge_model=$JUDGE_MODEL" \
    "verified_at=$(date -Is)" \
    "job_id=$JOB_ID" \
    "host=$(hostname)" \
    "cuda_visible_devices=$CUDA_VISIBLE_DEVICES" \
    "context_length=$OLLAMA_CONTEXT_LENGTH" \
    "ollama_llm_library=$OLLAMA_LLM_LIBRARY"
  printf 'ollama_ps=%q\n' "$OLLAMA_PS"
  printf 'nvidia_compute_apps=%q\n' "$NVIDIA_COMPUTE_APPS"
} > "$GPU_STATUS"
rm -f "$FAILED_STATUS"
echo "[$(date -Is)] CUDA smoke test passed for judge $JUDGE_MODEL"

for safe_model in llama31_8b llama31_70b qwen3_8b qwen3_32b; do
  "$PYTHON_BIN" scripts/validate_lps_utility_trajectories.py \
    --root "$EXP/agents/$safe_model" \
    --expected-logs 112
done

"$PYTHON_BIN" scripts/evaluate_lps_utility_experiment.py \
  --experiment-dir "$EXP" \
  --judge-model "$JUDGE_MODEL"

if grep -Eq \
  'truncating input messages which exceed context length|truncated = [1-9][0-9]*|slot context shift' \
  "$OLLAMA_LOG"; then
  fail_job "judge requests exceeded the configured native context; rebuttal table was not updated"
fi

judgments_sha256="$(sha256sum "$JUDGMENTS_PATH" | awk '{print $1}')"
printf '%s\n' \
  "judge_model=$JUDGE_MODEL" \
  "context_length=$OLLAMA_CONTEXT_LENGTH" \
  "judgments_sha256=$judgments_sha256" \
  "verified_at=$(date -Is)" \
  "job_id=$JOB_ID" > "$CONTEXT_VERIFIED_STATUS"

# The second pass consumes the cached judgments and only publishes the table
# after the no-truncation gate above has passed.
"$PYTHON_BIN" scripts/evaluate_lps_utility_experiment.py \
  --experiment-dir "$EXP" \
  --judge-model "$JUDGE_MODEL" \
  --update-markdown tmp/5QNC_backup.md

printf '%s\n' \
  "judge_model=$JUDGE_MODEL" \
  "context_length=$OLLAMA_CONTEXT_LENGTH" \
  "completed_at=$(date -Is)" \
  "job_id=$JOB_ID" > "$EXP/status/evaluation.done"
echo "[$(date -Is)] evaluation complete"
