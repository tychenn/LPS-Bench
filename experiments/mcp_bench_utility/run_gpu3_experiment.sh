#!/usr/bin/env bash
# Direct two- or four-A40 scheduler for the MCP-Bench paired utility experiment.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHECKOUT="${MCPBENCH_CHECKOUT:-$REPO_ROOT/external/mcp-bench}"
VENV="${MCPBENCH_VENV:-$SCRIPT_DIR/.venv}"
PYTHON="$VENV/bin/python"
WORKER="$SCRIPT_DIR/run_model_worker.sh"
EXPECTED_HOST="${MCPBENCH_EXPECTED_HOST:-gpu3}"
GPU_IDS_TEXT="${MCPBENCH_GPU_IDS:-}"
PORT_BASE="${MCPBENCH_PORT_BASE:-25100}"
JUDGE_PORT="${MCPBENCH_JUDGE_PORT:-25099}"
JUDGE_MODE="${MCPBENCH_JUDGE_MODE:-local}"
JUDGE_MODEL="${MCPBENCH_JUDGE_MODEL:-}"
RUN_TAG="${RUN_TAG:-$(date +%Y%m%d_%H%M%S)}"
EXP="${EXP:-$REPO_ROOT/runs/mcp_bench_utility_gpu3_${RUN_TAG}}"
PRELOAD_TIMEOUT="${MCPBENCH_PRELOAD_TIMEOUT:-900}"
CHECK_ONLY=0
TASK_LIMIT=0
GPU_MODE=4
JUDGE_PID=""
RUNNING_PIDS=()
USER_HOME_DIR="$(getent passwd "$(id -u)" | cut -d: -f6)"

if [[ -z "$USER_HOME_DIR" ]]; then
  echo "Could not resolve the current user's home directory." >&2
  exit 1
fi

usage() {
  cat <<'EOF'
Usage: run_gpu3_experiment.sh [--two-gpu] [--check-only | --canary]

  --check-only  Verify the frozen checkout, dependencies, services, models,
                hostname, and free GPUs without starting target trajectories.
  --canary      Run one paired task for each model included in the selected mode.
  --two-gpu     Run Llama-8B, Qwen3-8B, and Qwen3-32B sequentially on the
                first selected GPU while the second hosts the local judge.
                Llama-70B is skipped until more GPUs are available.

The default runs all 20 frozen tasks under both prompt conditions.
Four-GPU mode uses GPU indices 0,1,2,3 by default. Two-GPU mode uses 0,1.
Override either list with MCPBENCH_GPU_IDS.

Judge modes:
  MCPBENCH_JUDGE_MODE=local   Fixed qwen3:32b Ollama judge on the last selected GPU.
  MCPBENCH_JUDGE_MODE=azure   Official o4-mini-compatible Azure judge.
  MCPBENCH_JUDGE_MODE=openai-compatible
                              External compatible judge; also set
                              MCPBENCH_JUDGE_BASE_URL and MCPBENCH_JUDGE_MODEL.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --check-only) CHECK_ONLY=1 ;;
    --canary) TASK_LIMIT=1 ;;
    --two-gpu) GPU_MODE=2 ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
done
if [[ "$CHECK_ONLY" == "1" && "$TASK_LIMIT" != "0" ]]; then
  echo "--check-only and --canary cannot be used together." >&2
  exit 2
fi
if [[ -z "$GPU_IDS_TEXT" ]]; then
  if [[ "$GPU_MODE" == "2" ]]; then
    GPU_IDS_TEXT="0,1"
  else
    GPU_IDS_TEXT="0,1,2,3"
  fi
fi

EXP="$(readlink -m -- "$EXP")"
case "$EXP" in
  "$REPO_ROOT"/runs/*) ;;
  *)
    echo "EXP must be a child of $REPO_ROOT/runs" >&2
    exit 2
    ;;
esac
case "$EXP" in
  /|"$REPO_ROOT"|"$REPO_ROOT/runs")
    echo "Unsafe experiment directory: $EXP" >&2
    exit 2
    ;;
esac

IFS=',' read -r -a GPU_IDS <<<"$GPU_IDS_TEXT"
if [[ "${#GPU_IDS[@]}" -ne "$GPU_MODE" ]]; then
  echo "MCPBENCH_GPU_IDS must contain $GPU_MODE comma-separated GPU indices." >&2
  exit 2
fi
declare -A SEEN_GPUS=()
for gpu_id in "${GPU_IDS[@]}"; do
  if ! [[ "$gpu_id" =~ ^[0-9]+$ ]] || [[ -n "${SEEN_GPUS[$gpu_id]:-}" ]]; then
    echo "Invalid or duplicate GPU ID: $gpu_id" >&2
    exit 2
  fi
  SEEN_GPUS[$gpu_id]=1
done
if [[ "$GPU_MODE" == "2" ]]; then
  JUDGE_GPU_ID="${GPU_IDS[1]}"
else
  JUDGE_GPU_ID="${GPU_IDS[3]}"
fi
if ! [[ "$PORT_BASE" =~ ^[0-9]+$ ]] ||
  ! [[ "$JUDGE_PORT" =~ ^[0-9]+$ ]]; then
  echo "Ports must be integers." >&2
  exit 2
fi
case "$JUDGE_MODE" in
  local|azure|openai-compatible) ;;
  *)
    echo "Invalid MCPBENCH_JUDGE_MODE: $JUDGE_MODE" >&2
    exit 2
    ;;
esac

for required in \
  "$PYTHON" \
  "$WORKER" \
  "$SCRIPT_DIR/selected_tasks.json" \
  "$SCRIPT_DIR/selected_cases.md"; do
  [[ -e "$required" ]] || {
    echo "Required experiment input is missing: $required" >&2
    echo "Run $SCRIPT_DIR/setup_environment.sh first." >&2
    exit 1
  }
done
if [[ "$(hostname -s)" != "$EXPECTED_HOST" ]]; then
  echo "This direct experiment must run on $EXPECTED_HOST; current host is $(hostname -s)." >&2
  exit 1
fi
command -v nvidia-smi >/dev/null || {
  echo "nvidia-smi is unavailable." >&2
  exit 1
}
export PATH="$USER_HOME_DIR/.local/bin:$VENV/bin:$PATH"
command -v ollama >/dev/null || {
  echo "ollama is unavailable." >&2
  exit 1
}

for gpu_id in "${GPU_IDS[@]}"; do
  gpu_line="$(
    env -u CUDA_VISIBLE_DEVICES \
      nvidia-smi --query-gpu=index,name --format=csv,noheader |
      awk -F',' -v target="$gpu_id" '
        {
          gpu_index=$1
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", gpu_index)
          if (gpu_index == target) print
        }
      '
  )"
  if [[ -z "$gpu_line" || "$gpu_line" != *A40* ]]; then
    echo "GPU $gpu_id is missing or is not an A40: $gpu_line" >&2
    exit 1
  fi
done
busy=""
for gpu_id in "${GPU_IDS[@]}"; do
  gpu_busy="$(
    env -u CUDA_VISIBLE_DEVICES \
      nvidia-smi -i "$gpu_id" \
      --query-compute-apps=pid,process_name \
      --format=csv,noheader 2>/dev/null |
      sed '/^[[:space:]]*$/d' || true
  )"
  if [[ -n "$gpu_busy" ]]; then
    busy+="${busy:+$'\n'}GPU $gpu_id: $gpu_busy"
  fi
done
if [[ -n "$busy" ]]; then
  echo "Refusing to share the selected GPUs with existing compute processes:" >&2
  printf '%s\n' "$busy" >&2
  exit 1
fi

if [[ "$JUDGE_MODE" == "azure" ]]; then
  : "${AZURE_OPENAI_API_KEY:?Azure judge key is missing}"
  : "${AZURE_OPENAI_ENDPOINT:?Azure judge endpoint is missing}"
  export MCPBENCH_JUDGE_MODE="azure"
  JUDGE_MODEL="${JUDGE_MODEL:-o4-mini}"
  export MCPBENCH_JUDGE_MODEL="$JUDGE_MODEL"
elif [[ "$JUDGE_MODE" == "openai-compatible" ]]; then
  : "${MCPBENCH_JUDGE_BASE_URL:?Compatible judge base URL is missing}"
  JUDGE_MODEL="${JUDGE_MODEL:-o4-mini}"
  export MCPBENCH_JUDGE_MODE="openai-compatible"
  export MCPBENCH_JUDGE_MODEL="$JUDGE_MODEL"
else
  JUDGE_MODEL="${JUDGE_MODEL:-qwen3:32b}"
  export MCPBENCH_JUDGE_MODE="openai-compatible"
  export MCPBENCH_JUDGE_MODEL="$JUDGE_MODEL"
  export MCPBENCH_JUDGE_BASE_URL="http://127.0.0.1:$JUDGE_PORT/v1"
  export MCPBENCH_JUDGE_API_KEY="ollama"
fi

mkdir -p "$EXP/logs" "$EXP/status" "$EXP/results"
env \
  -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  -u http_proxy -u https_proxy -u all_proxy \
  "$PYTHON" "$SCRIPT_DIR/preflight_selected.py" \
    --checkout "$CHECKOUT" \
    --tasks-file "$SCRIPT_DIR/selected_tasks.json" \
    --output "$EXP/preflight.json"

if [[ "$CHECK_ONLY" == "1" ]]; then
  echo "All MCP-Bench checks passed; no trajectories were started."
  exit 0
fi

cleanup() {
  local code=$?
  local pid
  for pid in "${RUNNING_PIDS[@]}"; do
    kill -TERM -- "-$pid" 2>/dev/null || true
  done
  if [[ -n "$JUDGE_PID" ]]; then
    kill "$JUDGE_PID" 2>/dev/null || true
    wait "$JUDGE_PID" 2>/dev/null || true
  fi
  return "$code"
}
trap cleanup EXIT
trap 'exit 130' INT HUP
trap 'exit 143' TERM

if [[ "$JUDGE_MODE" == "local" ]]; then
  CUDA_VISIBLE_DEVICES="$JUDGE_GPU_ID" \
  OLLAMA_HOST="127.0.0.1:$JUDGE_PORT" \
  OLLAMA_CONTEXT_LENGTH="40960" \
  OLLAMA_KEEP_ALIVE="-1" \
  OLLAMA_NUM_PARALLEL="1" \
  OLLAMA_MAX_LOADED_MODELS="1" \
    ollama serve >"$EXP/logs/judge_ollama.log" 2>&1 &
  JUDGE_PID=$!
  judge_ready=0
  for _ in {1..240}; do
    if curl --noproxy '*' --silent --fail --max-time 2 \
      "http://127.0.0.1:$JUDGE_PORT/api/tags" >/dev/null; then
      judge_ready=1
      break
    fi
    if ! kill -0 "$JUDGE_PID" 2>/dev/null; then
      echo "Judge Ollama exited during startup." >&2
      exit 1
    fi
    sleep 1
  done
  [[ "$judge_ready" == "1" ]] || {
    echo "Judge Ollama failed to start." >&2
    exit 1
  }
  if ! curl --noproxy '*' --silent --fail --max-time 10 \
    "http://127.0.0.1:$JUDGE_PORT/api/tags" |
    "$PYTHON" -c \
      'import json,sys; target=sys.argv[1]; data=json.load(sys.stdin); names={m.get("name") for m in data.get("models", [])}; raise SystemExit(target not in names)' \
      "$JUDGE_MODEL"; then
    echo "Local judge model is not available: $JUDGE_MODEL" >&2
    echo "Run: ollama pull $JUDGE_MODEL" >&2
    exit 1
  fi
  "$PYTHON" -c \
    'import json,sys; print(json.dumps({"model":sys.argv[1],"prompt":"","stream":False,"keep_alive":-1,"options":{"num_ctx":40960,"num_predict":1}}))' \
    "$JUDGE_MODEL" |
    curl --noproxy '*' --silent --show-error --fail \
      --max-time "$PRELOAD_TIMEOUT" \
      -H 'Content-Type: application/json' \
      --data-binary @- \
      "http://127.0.0.1:$JUDGE_PORT/api/generate" >/dev/null
fi

launch_worker() {
  local model_key="$1"
  local gpu_ids="$2"
  local port="$3"
  local log="$EXP/logs/${model_key}_worker.log"
  setsid "$WORKER" \
    "$model_key" "$gpu_ids" "$port" "$EXP" "$TASK_LIMIT" \
    >"$log" 2>&1 &
  RUNNING_PIDS+=("$!")
  echo "[$(date -Is)] launched model=$model_key gpu=$gpu_ids port=$port"
}

wait_stage() {
  local stage_failures=0
  local pid
  for pid in "${RUNNING_PIDS[@]}"; do
    if ! wait "$pid"; then
      stage_failures=$((stage_failures + 1))
    fi
  done
  RUNNING_PIDS=()
  return "$stage_failures"
}

small_failures=0
large_failures=0
if [[ "$GPU_MODE" == "2" ]]; then
  port_offset=0
  for model_key in llama31_8b qwen3_8b qwen3_32b; do
    launch_worker \
      "$model_key" "${GPU_IDS[0]}" "$((PORT_BASE + port_offset))"
    stage_failures=0
    wait_stage || stage_failures=$?
    small_failures=$((small_failures + stage_failures))
    port_offset=$((port_offset + 1))
  done
else
  launch_worker "llama31_8b" "${GPU_IDS[0]}" "$PORT_BASE"
  launch_worker "qwen3_8b" "${GPU_IDS[1]}" "$((PORT_BASE + 1))"
  launch_worker "qwen3_32b" "${GPU_IDS[2]}" "$((PORT_BASE + 2))"
  wait_stage || small_failures=$?

  launch_worker \
    "llama31_70b" "${GPU_IDS[0]},${GPU_IDS[1]}" "$((PORT_BASE + 3))"
  wait_stage || large_failures=$?
fi

"$PYTHON" "$SCRIPT_DIR/summarize_results.py" \
  --run-dir "$EXP" \
  --output "$EXP/summary.md"

total_failures=$((small_failures + large_failures))
if [[ "$total_failures" -ne 0 ]]; then
  echo "Experiment finished with $total_failures failed model worker(s)." >&2
  exit 1
fi
if [[ "$GPU_MODE" == "2" ]]; then
  echo "Two-GPU partial run completed; llama31_70b remains pending."
fi
echo "MCP-Bench utility experiment completed: $EXP"
