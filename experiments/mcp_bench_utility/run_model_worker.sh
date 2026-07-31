#!/usr/bin/env bash
# Run one target model over the paired original/safety frozen task subset.

set -euo pipefail

if [[ "$#" -ne 5 ]]; then
  echo "Usage: $0 MODEL_KEY GPU_IDS AGENT_PORT EXPERIMENT_DIR TASK_LIMIT" >&2
  exit 2
fi

MODEL_KEY="$1"
GPU_IDS="$2"
AGENT_PORT="$3"
EXP="$(readlink -m -- "$4")"
TASK_LIMIT="$5"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHECKOUT="${MCPBENCH_CHECKOUT:-$REPO_ROOT/external/mcp-bench}"
VENV="${MCPBENCH_VENV:-$SCRIPT_DIR/.venv}"
PYTHON="$VENV/bin/python"
MANIFEST="$SCRIPT_DIR/model_manifest.json"
TASKS="$SCRIPT_DIR/selected_tasks.json"
SAFETY_PROMPT="$REPO_ROOT/utility_cases/lps_bench_derived/prompts/safety_prompt.txt"
JUDGE_MODE="${MCPBENCH_JUDGE_MODE:-openai-compatible}"
JUDGE_MODEL="${MCPBENCH_JUDGE_MODEL:-qwen3:32b}"
JUDGE_BASE_URL="${MCPBENCH_JUDGE_BASE_URL:-}"
TASK_TIMEOUT="${MCPBENCH_TASK_TIMEOUT:-1200}"
MAX_RETRIES="${MCPBENCH_MAX_RETRIES:-1}"
PRELOAD_TIMEOUT="${MCPBENCH_PRELOAD_TIMEOUT:-900}"
OLLAMA_PID=""
USER_HOME_DIR="$(getent passwd "$(id -u)" | cut -d: -f6)"

if [[ -z "$USER_HOME_DIR" ]]; then
  echo "Could not resolve the current user's home directory." >&2
  exit 1
fi

unset \
  HTTP_PROXY HTTPS_PROXY ALL_PROXY \
  http_proxy https_proxy all_proxy
export NO_PROXY="127.0.0.1,localhost"
export no_proxy="$NO_PROXY"
export PATH="$USER_HOME_DIR/.local/bin:$VENV/bin:$PATH"

case "$JUDGE_MODE" in
  azure|openai-compatible) ;;
  *)
    echo "Invalid MCPBENCH_JUDGE_MODE: $JUDGE_MODE" >&2
    exit 2
    ;;
esac
if [[ "$JUDGE_MODE" == "openai-compatible" && -z "$JUDGE_BASE_URL" ]]; then
  echo "MCPBENCH_JUDGE_BASE_URL is required." >&2
  exit 2
fi
if ! [[ "$AGENT_PORT" =~ ^[0-9]+$ ]] ||
  [[ "$AGENT_PORT" -lt 1024 ]] ||
  [[ "$AGENT_PORT" -gt 65535 ]]; then
  echo "Invalid agent port: $AGENT_PORT" >&2
  exit 2
fi
if [[ "$TASK_LIMIT" != "0" ]] &&
  { ! [[ "$TASK_LIMIT" =~ ^[1-9][0-9]*$ ]] || [[ "$TASK_LIMIT" -gt 20 ]]; }; then
  echo "TASK_LIMIT must be 0 or an integer from 1 to 20." >&2
  exit 2
fi
for required in "$PYTHON" "$MANIFEST" "$TASKS" "$SAFETY_PROMPT"; do
  [[ -e "$required" ]] || {
    echo "Required experiment input is missing: $required" >&2
    exit 1
  }
done

IFS=$'\t' read -r SERVED_MODEL CONTEXT_LENGTH EXPECTED_GPUS < <(
  "$PYTHON" - "$MANIFEST" "$MODEL_KEY" <<'PY'
import json
import sys

models = json.load(open(sys.argv[1], encoding="utf-8"))["models"]
if sys.argv[2] not in models:
    raise SystemExit(f"Unknown model key: {sys.argv[2]}")
model = models[sys.argv[2]]
print(
    model["served_model"],
    model["context_length"],
    model["gpu_count"],
    sep="\t",
)
PY
)
IFS=',' read -r -a GPU_ARRAY <<<"$GPU_IDS"
if [[ "${#GPU_ARRAY[@]}" -ne "$EXPECTED_GPUS" ]]; then
  echo "$MODEL_KEY requires $EXPECTED_GPUS GPU(s), received $GPU_IDS." >&2
  exit 2
fi

OUTPUT_DIR="$EXP/results/$MODEL_KEY"
LOG_DIR="$EXP/logs"
STATUS_DIR="$EXP/status"
mkdir -p "$OUTPUT_DIR" "$LOG_DIR" "$STATUS_DIR"
OLLAMA_LOG="$LOG_DIR/${MODEL_KEY}_ollama.log"
RUN_LOG="$LOG_DIR/${MODEL_KEY}_runner.log"
DONE_FILE="$STATUS_DIR/${MODEL_KEY}.done"
FAILED_FILE="$STATUS_DIR/${MODEL_KEY}.failed"
rm -f -- "$DONE_FILE" "$FAILED_FILE"

cleanup() {
  local code=$?
  if [[ -n "$OLLAMA_PID" ]]; then
    kill "$OLLAMA_PID" 2>/dev/null || true
    wait "$OLLAMA_PID" 2>/dev/null || true
  fi
  if [[ "$code" -ne 0 && ! -e "$FAILED_FILE" ]]; then
    printf 'exit=%s\nfailed_at=%s\n' "$code" "$(date -Is)" >"$FAILED_FILE"
  fi
  return "$code"
}
trap cleanup EXIT
trap 'exit 130' INT HUP
trap 'exit 143' TERM

CUDA_VISIBLE_DEVICES="$GPU_IDS" \
OLLAMA_HOST="127.0.0.1:$AGENT_PORT" \
OLLAMA_CONTEXT_LENGTH="$CONTEXT_LENGTH" \
OLLAMA_KEEP_ALIVE="-1" \
OLLAMA_NUM_PARALLEL="1" \
OLLAMA_MAX_LOADED_MODELS="1" \
  ollama serve >"$OLLAMA_LOG" 2>&1 &
OLLAMA_PID=$!

ready=0
for _ in {1..240}; do
  if curl --noproxy '*' --silent --fail --max-time 2 \
    "http://127.0.0.1:$AGENT_PORT/api/tags" >/dev/null; then
    ready=1
    break
  fi
  if ! kill -0 "$OLLAMA_PID" 2>/dev/null; then
    echo "Ollama exited during startup; see $OLLAMA_LOG" >&2
    exit 1
  fi
  sleep 1
done
if [[ "$ready" != "1" ]]; then
  echo "Ollama did not become ready on port $AGENT_PORT." >&2
  exit 1
fi

if ! curl --noproxy '*' --silent --fail --max-time 10 \
  "http://127.0.0.1:$AGENT_PORT/api/tags" |
  "$PYTHON" -c \
    'import json,sys; target=sys.argv[1]; data=json.load(sys.stdin); names={m.get("name") for m in data.get("models", [])}; raise SystemExit(target not in names)' \
    "$SERVED_MODEL"; then
  echo "Ollama model is not available locally: $SERVED_MODEL" >&2
  echo "Run: ollama pull $SERVED_MODEL" >&2
  exit 1
fi

"$PYTHON" -c \
  'import json,sys; print(json.dumps({"model":sys.argv[1],"prompt":"","stream":False,"keep_alive":-1,"options":{"num_ctx":int(sys.argv[2]),"num_predict":1}}))' \
  "$SERVED_MODEL" "$CONTEXT_LENGTH" |
  curl --noproxy '*' --silent --show-error --fail \
    --max-time "$PRELOAD_TIMEOUT" \
    -H 'Content-Type: application/json' \
    --data-binary @- \
    "http://127.0.0.1:$AGENT_PORT/api/generate" >/dev/null

run_args=(
  "$PYTHON" "$SCRIPT_DIR/run_paired.py"
  --checkout "$CHECKOUT"
  --tasks-file "$TASKS"
  --output-dir "$OUTPUT_DIR"
  --model-key "$MODEL_KEY"
  --served-model "$SERVED_MODEL"
  --agent-base-url "http://127.0.0.1:$AGENT_PORT/v1"
  --safety-prompt "$SAFETY_PROMPT"
  --judge-mode "$JUDGE_MODE"
  --judge-model "$JUDGE_MODEL"
  --task-timeout "$TASK_TIMEOUT"
  --max-retries "$MAX_RETRIES"
)
if [[ "$JUDGE_MODE" == "openai-compatible" ]]; then
  run_args+=(--judge-base-url "$JUDGE_BASE_URL")
fi
if [[ "$TASK_LIMIT" != "0" ]]; then
  run_args+=(--limit "$TASK_LIMIT")
fi

if "${run_args[@]}" 2>&1 | tee "$RUN_LOG"; then
  printf 'model=%s\nfinished_at=%s\n' "$MODEL_KEY" "$(date -Is)" >"$DONE_FILE"
else
  code="${PIPESTATUS[0]}"
  printf 'model=%s\nexit=%s\nfailed_at=%s\n' \
    "$MODEL_KEY" "$code" "$(date -Is)" >"$FAILED_FILE"
  exit "$code"
fi
