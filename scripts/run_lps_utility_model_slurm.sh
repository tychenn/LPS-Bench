#!/usr/bin/env bash
# Verify Ollama is using CUDA, then run both prompt conditions for one model.

set -euo pipefail

AGENT_STEP_LIMIT="${AGENT_STEP_LIMIT:-128}"
if ! [[ "$AGENT_STEP_LIMIT" =~ ^[1-9][0-9]*$ ]]; then
  echo "AGENT_STEP_LIMIT must be a positive integer: $AGENT_STEP_LIMIT" >&2
  exit 1
fi
AGENT_REPEAT_CALL_LIMIT="${AGENT_REPEAT_CALL_LIMIT:-12}"
if ! [[ "$AGENT_REPEAT_CALL_LIMIT" =~ ^[1-9][0-9]*$ ]]; then
  echo "AGENT_REPEAT_CALL_LIMIT must be a positive integer: $AGENT_REPEAT_CALL_LIMIT" >&2
  exit 1
fi
export AGENT_REPEAT_CALL_LIMIT

: "${EXP:?EXP must point to the experiment directory}"
: "${MODEL:?MODEL must be an Ollama model name}"
: "${SAFE:?SAFE must be a filesystem-safe model label}"

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
PYTHON_BIN="${PYTHON_BIN:-/home/cty/anaconda3/envs/agentbenchmark/bin/python}"
CASE_LIST="${CASE_LIST:-$EXP/case_list.txt}"
ALLOW_OLLAMA_PULL="${ALLOW_OLLAMA_PULL:-0}"
GPU_SMOKE_ONLY="${GPU_SMOKE_ONLY:-0}"
GPU_SMOKE_TIMEOUT="${GPU_SMOKE_TIMEOUT:-1200}"
PREFLIGHT_REQUIRED_MODELS="${PREFLIGHT_REQUIRED_MODELS:-}"
PREFLIGHT_AGENT_SMOKE_CASE="${PREFLIGHT_AGENT_SMOKE_CASE:-}"
OLLAMA_SERVER_BYPASS_PROXY="${OLLAMA_SERVER_BYPASS_PROXY:-1}"
OLLAMA_START_DELAY="${OLLAMA_START_DELAY:-0}"

cd "$REPO_ROOT"
mkdir -p "$EXP/slurm" "$EXP/status" "$EXP/agents/$SAFE"

export LANGCHAIN_TRACING_V2=false
export LANGCHAIN_TRACING=false
export LANGSMITH_TRACING=false
export OLLAMA_NUM_PREDICT="${OLLAMA_NUM_PREDICT:-768}"
export OLLAMA_CLIENT_TIMEOUT="${OLLAMA_CLIENT_TIMEOUT:-300}"
export OLLAMA_REASONING="${OLLAMA_REASONING:-false}"
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

# CUDA autodetection timed out in the first run and silently fell back to CPU.
# Force the bundled CUDA 12 backend and explicitly disable the inherited Vulkan
# setting. Both values can still be changed deliberately through the variables
# on the right-hand side.
export OLLAMA_LLM_LIBRARY="${OLLAMA_CUDA_LIBRARY:-cuda_v12}"
export OLLAMA_VULKAN="${LPS_OLLAMA_VULKAN:-false}"

JOB_ID="${SLURM_JOB_ID:-$$}"
export OLLAMA_HOST="127.0.0.1:$((20000 + JOB_ID % 20000))"
export NO_PROXY="127.0.0.1,localhost,${NO_PROXY:-}"
export no_proxy="127.0.0.1,localhost,${no_proxy:-}"

OLLAMA_LOG="$EXP/slurm/${SAFE}_ollama_${JOB_ID}.log"
SMOKE_RESPONSE="$EXP/status/${SAFE}.gpu_smoke_response.json"
GPU_STATUS="$EXP/status/${SAFE}.gpu_verified"
FAILED_STATUS="$EXP/status/${SAFE}.failed"
OLLAMA_PID=""

fail_job() {
  local reason="$1"
  printf '%s\n' \
    "model=$MODEL" \
    "failed_at=$(date -Is)" \
    "job_id=$JOB_ID" \
    "reason=$reason" > "$FAILED_STATUS"
  echo "[$(date -Is)] ERROR: $reason" >&2
  exit 1
}

echo "[$(date -Is)] job=$JOB_ID model=$MODEL host=$(hostname)"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-<unset>}"
echo "OLLAMA_LLM_LIBRARY=$OLLAMA_LLM_LIBRARY OLLAMA_VULKAN=$OLLAMA_VULKAN OLLAMA_CONTEXT_LENGTH=$OLLAMA_CONTEXT_LENGTH"

if [[ -z "${CUDA_VISIBLE_DEVICES:-}" ]]; then
  fail_job "CUDA_VISIBLE_DEVICES is unset; this is not a GPU allocation"
fi
if ! [[ "$OLLAMA_CONTEXT_LENGTH" =~ ^[1-9][0-9]*$ ]]; then
  fail_job "OLLAMA_CONTEXT_LENGTH must be a positive integer"
fi
if ! command -v nvidia-smi >/dev/null 2>&1; then
  fail_job "nvidia-smi is unavailable on the allocated node"
fi
if ! nvidia-smi; then
  fail_job "nvidia-smi could not communicate with the allocated GPU"
fi

if ! [[ "$OLLAMA_START_DELAY" =~ ^[0-9]+$ ]]; then
  fail_job "OLLAMA_START_DELAY must be a non-negative integer"
fi
if [[ "$OLLAMA_START_DELAY" -gt 0 ]]; then
  echo "[$(date -Is)] delaying Ollama startup by ${OLLAMA_START_DELAY}s to avoid concurrent CUDA discovery"
  sleep "$OLLAMA_START_DELAY"
fi

# Ollama 0.30.10 has a fixed 30-second CUDA-discovery watchdog. On these
# compute nodes, cold-reading the bundled 1.2 GiB CUDA backend from shared
# storage takes about 32 seconds, even though the backend successfully finds
# the A40. Warm the real library files into the node page cache first so the
# discovery subprocess completes before that watchdog.
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

# Slurm exports AMD/OpenCL aliases alongside CUDA_VISIBLE_DEVICES. They are
# unnecessary on this NVIDIA-only node and make Ollama probe the same ordinal
# through multiple backend-specific variables.
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
    # The submit host's loopback proxy is not reachable from compute nodes.
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
  echo "[$(date -Is)] Ollama launch attempt $launch_attempt failed CUDA discovery" >&2
  tail -n 160 "$attempt_log" >&2 || true
  kill "$OLLAMA_PID" 2>/dev/null || true
  wait "$OLLAMA_PID" 2>/dev/null || true
  OLLAMA_PID=""
  ready=0
  sleep 5
done
if [[ "$ready" -ne 1 ]]; then
  tail -n 120 "$OLLAMA_LOG" >&2 || true
  fail_job "Ollama server did not become ready with CUDA after 3 attempts"
fi

# Do not spend minutes loading the model on CPU when CUDA bootstrap already
# failed. The later smoke checks still verify the loaded model and VRAM use.
if ! grep -Eqi 'inference compute.*library=CUDA' "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "Ollama did not discover a CUDA inference device"
fi

if ! ollama show "$MODEL" >/dev/null 2>&1; then
  if [[ "$ALLOW_OLLAMA_PULL" == "1" ]]; then
    echo "[$(date -Is)] pulling missing model $MODEL"
    if ! ollama pull "$MODEL"; then
      fail_job "required model $MODEL is missing and could not be pulled"
    fi
  else
    fail_job "required Ollama model is missing: $MODEL"
  fi
fi
ollama list

# Loading and generating one token is required before `ollama ps` can report
# the actual compute backend. Formal cases are not started until this succeeds.
echo "[$(date -Is)] running CUDA smoke test for $MODEL"
if ! printf \
  '{"model":"%s","prompt":"Reply with OK.","stream":false,"keep_alive":"30m","options":{"num_ctx":%s,"num_predict":1,"temperature":0}}' \
  "$MODEL" "$OLLAMA_CONTEXT_LENGTH" |
  curl \
    --fail \
    --silent \
    --show-error \
    --max-time "$GPU_SMOKE_TIMEOUT" \
    --header 'Content-Type: application/json' \
    --data-binary @- \
    "http://$OLLAMA_HOST/api/generate" > "$SMOKE_RESPONSE"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "the model-load smoke request failed or timed out"
fi

OLLAMA_PS="$(ollama ps)"
printf '%s\n' "$OLLAMA_PS"
if ! printf '%s\n' "$OLLAMA_PS" |
  awk -v model="$MODEL" -v context="$OLLAMA_CONTEXT_LENGTH" '
    NR > 1 &&
    $1 == model &&
    toupper($0) ~ /100%[[:space:]]+GPU/ &&
    $0 ~ ("(^|[[:space:]])" context "([[:space:]]|$)") { found = 1 }
    END { exit(found ? 0 : 1) }
  '; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "ollama ps does not report 100% GPU execution at context $OLLAMA_CONTEXT_LENGTH for $MODEL"
fi
if ! grep -Eqi \
  'inference compute.*library=CUDA|loaded CUDA backend|device=CUDA|offload(ed|ing).*(layer|weight).*GPU' \
  "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "Ollama log contains no CUDA backend or GPU-offload evidence"
fi

NVIDIA_COMPUTE_APPS="$(
  nvidia-smi \
    --query-compute-apps=pid,process_name,used_gpu_memory \
    --format=csv,noheader 2>/dev/null || true
)"
printf '%s\n' "$NVIDIA_COMPUTE_APPS"
if [[ -z "$NVIDIA_COMPUTE_APPS" ]]; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "nvidia-smi reports no process holding GPU memory after model load"
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
  fail_job "not all model layers were offloaded to GPU"
fi
if ! grep -Eq \
  "llama_context: n_ctx[[:space:]]+=[[:space:]]+${OLLAMA_CONTEXT_LENGTH}$" \
  "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "runtime context does not match $OLLAMA_CONTEXT_LENGTH"
fi
if ! grep -Eq \
  "print_info: n_ctx_train[[:space:]]+=[[:space:]]+${OLLAMA_CONTEXT_LENGTH}$" \
  "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "$OLLAMA_CONTEXT_LENGTH is not the model's native context limit"
fi
visible_gpu_count="$(awk -F',' '{print NF}' <<<"$CUDA_VISIBLE_DEVICES")"
if [[ "$visible_gpu_count" -gt 1 ]]; then
  for local_gpu in $(seq 0 $((visible_gpu_count - 1))); do
    if ! grep -Eq \
      "CUDA${local_gpu} (model|KV) buffer size[[:space:]]+=[[:space:]]+[1-9]" \
      "$OLLAMA_LOG"; then
      tail -n 160 "$OLLAMA_LOG" >&2 || true
      fail_job "multi-GPU spread is missing CUDA${local_gpu}"
    fi
  done
fi

{
  printf '%s\n' \
    "model=$MODEL" \
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
echo "[$(date -Is)] CUDA smoke test passed for $MODEL"

if [[ "$GPU_SMOKE_ONLY" == "1" ]]; then
  if [[ -n "$PREFLIGHT_REQUIRED_MODELS" ]]; then
    IFS='|' read -r -a required_models <<< "$PREFLIGHT_REQUIRED_MODELS"
    for required_model in "${required_models[@]}"; do
      if ollama show "$required_model" >/dev/null 2>&1; then
        echo "[$(date -Is)] required model ready: $required_model"
        continue
      fi
      if [[ "$ALLOW_OLLAMA_PULL" != "1" ]]; then
        fail_job "required model is missing: $required_model"
      fi
      echo "[$(date -Is)] pulling missing required model $required_model"
      if ! ollama pull "$required_model"; then
        fail_job "required model $required_model is missing and could not be pulled"
      fi
    done
  fi
  if [[ -n "$PREFLIGHT_AGENT_SMOKE_CASE" ]]; then
    if [[ ! -f "$PREFLIGHT_AGENT_SMOKE_CASE" ]]; then
      fail_job "agent smoke case is missing: $PREFLIGHT_AGENT_SMOKE_CASE"
    fi
    smoke_case_domain="$(basename "$(dirname "$PREFLIGHT_AGENT_SMOKE_CASE")")"
    smoke_case_id="$(basename "$PREFLIGHT_AGENT_SMOKE_CASE" .json)"
    smoke_safe_model="${MODEL//:/_}"
    smoke_safe_model="${smoke_safe_model//\//_}"
    for smoke_condition in original safety; do
      smoke_output="$EXP/preflight_agent/$smoke_condition"
      "$PYTHON_BIN" agent.py \
        --cases "$PREFLIGHT_AGENT_SMOKE_CASE" \
        --models "$MODEL" \
        --output-dir "$smoke_output" \
        --capability-mode tool-only \
        --system-prompt-mode "$smoke_condition" \
        --safety-prompt-file utility_cases/lps_bench_derived/prompts/safety_prompt.txt \
        --step-limit "$AGENT_STEP_LIMIT" \
        --log-level ERROR
      "$PYTHON_BIN" scripts/validate_lps_utility_trajectories.py \
        --root "$smoke_output" \
        --expected-logs 1
      smoke_log="$smoke_output/$smoke_case_domain/$smoke_case_id/tool-only/$smoke_condition/${smoke_case_id}_${smoke_safe_model}.txt"
      if [[ ! -f "$smoke_log" ]] ||
        ! grep -q '^# Run Status: success$' "$smoke_log"; then
        fail_job "agent smoke did not complete for $MODEL/$smoke_condition"
      fi
      if [[ "$smoke_condition" == "original" ]] &&
        ! grep -q '^\[Tool Call\]' "$smoke_log"; then
        fail_job "agent smoke emitted no executable tool call for $MODEL/original"
      fi
      if ! grep -q '^\[Tool Call\]' "$smoke_log" &&
        awk '
          /^step: model$/ { in_model = 1; next }
          /^step: / { in_model = 0 }
          in_model && /"(name|tool|tool_name|function)"[[:space:]]*:/ {
            found = 1
          }
          END { exit(found ? 0 : 1) }
        ' "$smoke_log"; then
        fail_job "agent smoke emitted unexecuted textual tool calls for $MODEL/$smoke_condition"
      fi
    done
  fi
  if grep -Eq \
    'truncating input messages which exceed context length|truncated = [1-9][0-9]*|slot context shift' \
    "$OLLAMA_LOG"; then
    fail_job "preflight agent requests exceeded the configured native context"
  fi
  printf '%s\n' \
    "model=$MODEL" \
    "context_length=$OLLAMA_CONTEXT_LENGTH" \
    "agent_step_limit=$AGENT_STEP_LIMIT" \
    "agent_repeat_call_limit=$AGENT_REPEAT_CALL_LIMIT" \
    "completed_at=$(date -Is)" \
    "job_id=$JOB_ID" \
    "mode=gpu-smoke-and-model-preflight" \
    "required_models=$PREFLIGHT_REQUIRED_MODELS" > "$EXP/status/${SAFE}.done"
  echo "[$(date -Is)] GPU and model preflight complete"
  exit 0
fi

mapfile -t ALL_CASES < "$CASE_LIST"
if [[ "${#ALL_CASES[@]}" -ne 56 ]]; then
  fail_job "expected 56 cases in $CASE_LIST, found ${#ALL_CASES[@]}"
fi

safe_model="${MODEL//:/_}"
safe_model="${safe_model//\//_}"

for condition in original safety; do
  pending=()
  for case_path in "${ALL_CASES[@]}"; do
    domain="$(basename "$(dirname "$case_path")")"
    case_id="$(basename "$case_path" .json)"
    log_path="$EXP/agents/$SAFE/$condition/$domain/$case_id/tool-only/$condition/${case_id}_${safe_model}.txt"
    if [[ -f "$log_path" ]] && {
      grep -q '^# Run Status: success$' "$log_path" ||
        grep -q '^ERROR:$' "$log_path"
    }; then
      continue
    fi
    pending+=("$case_path")
  done

  echo "[$(date -Is)] model=$MODEL condition=$condition pending=${#pending[@]}"
  if [[ "${#pending[@]}" -eq 0 ]]; then
    continue
  fi

  "$PYTHON_BIN" agent.py \
    --cases "${pending[@]}" \
    --models "$MODEL" \
    --output-dir "$EXP/agents/$SAFE/$condition" \
    --capability-mode tool-only \
    --system-prompt-mode "$condition" \
    --safety-prompt-file utility_cases/lps_bench_derived/prompts/safety_prompt.txt \
    --step-limit "$AGENT_STEP_LIMIT" \
    --log-level ERROR
  "$PYTHON_BIN" scripts/validate_lps_utility_trajectories.py \
    --root "$EXP/agents/$SAFE/$condition" \
    --expected-logs 56
done

"$PYTHON_BIN" scripts/validate_lps_utility_trajectories.py \
  --root "$EXP/agents/$SAFE" \
  --expected-logs 112

if grep -Eq \
  'truncating input messages which exceed context length|truncated = [1-9][0-9]*|slot context shift' \
  "$OLLAMA_LOG"; then
  fail_job "formal agent requests exceeded the configured native context"
fi

printf '%s\n' \
  "model=$MODEL" \
  "context_length=$OLLAMA_CONTEXT_LENGTH" \
  "agent_step_limit=$AGENT_STEP_LIMIT" \
  "agent_repeat_call_limit=$AGENT_REPEAT_CALL_LIMIT" \
  "completed_at=$(date -Is)" \
  "job_id=$JOB_ID" > "$EXP/status/${SAFE}.done"
echo "[$(date -Is)] model=$MODEL complete"
