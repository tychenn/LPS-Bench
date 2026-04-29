#!/usr/bin/env bash
# Run one local Ollama model on the 40 skill-augmented cases in tool-only and skill-only modes.

set -euo pipefail

: "${EXP:?EXP must point to the experiment directory}"
: "${MODEL:?MODEL must be an Ollama model name}"
: "${SAFE:?SAFE must be a filesystem-safe model label}"

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
cd "$REPO_ROOT"

PY="${PYTHON:-python}"

: "${AGENT_BASE_URL:?AGENT_BASE_URL must point to the evaluator API endpoint}"
: "${AGENT_API_KEY:?AGENT_API_KEY must contain the evaluator API key}"

JOB_ID="${SLURM_JOB_ID:-$$}"
export OLLAMA_HOST="127.0.0.1:$((20000 + JOB_ID % 20000))"
export NO_PROXY="127.0.0.1,localhost,${NO_PROXY:-}"
export no_proxy="127.0.0.1,localhost,${no_proxy:-}"
export OLLAMA_NUM_PREDICT="${OLLAMA_NUM_PREDICT:-768}"
export OLLAMA_CLIENT_TIMEOUT="${OLLAMA_CLIENT_TIMEOUT:-180}"
export OLLAMA_REASONING="${OLLAMA_REASONING:-false}"
ollama serve > "$EXP/slurm/${SAFE}_ollama_${JOB_ID}.log" 2>&1 &
OLLAMA_PID=$!
trap 'kill "$OLLAMA_PID" 2>/dev/null || true' EXIT

for _ in {1..60}; do
  if ollama list >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

ollama list
EVAL_MODEL=deepseek-v3.2

for R in FA OC TS PI; do
  CASES=$(tr "\n" " " < "$EXP/case_lists/${R}_skill.txt")

  echo "[$(date -Is)] ${MODEL} tool-only ${R}"
  "$PY" agent.py \
    --cases $CASES \
    --models "$MODEL" \
    --output-dir "$EXP/local_${SAFE}/tool/$R" \
    --capability-mode tool-only \
    --evaluate \
    --eval-mode api \
    --eval-model "$EVAL_MODEL" \
    --log-level ERROR

  echo "[$(date -Is)] ${MODEL} skill-only ${R}"
  "$PY" agent.py \
    --cases $CASES \
    --models "$MODEL" \
    --output-dir "$EXP/local_${SAFE}/skill/$R" \
    --capability-mode skill-only \
    --evaluate \
    --eval-mode api \
    --eval-model "$EVAL_MODEL" \
    --log-level ERROR
done

echo "[$(date -Is)] ${MODEL} done"
