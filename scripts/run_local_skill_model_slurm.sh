#!/usr/bin/env bash
# Run one local Ollama model for the skill-extension experiment on a GPU node.

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
  echo "[$(date -Is)] ${MODEL} original ${R}"
  ORIG_CASES=$(tr "\n" " " < "$EXP/case_lists/${R}_original.txt")
  "$PY" agent.py \
    --cases $ORIG_CASES \
    --models "$MODEL" \
    --output-dir "$EXP/local_${SAFE}/original/$R" \
    --capability-mode tool-only \
    --evaluate \
    --eval-mode api \
    --eval-model "$EVAL_MODEL" \
    --log-level ERROR

  echo "[$(date -Is)] ${MODEL} skill ${R}"
  SKILL_CASES=$(tr "\n" " " < "$EXP/case_lists/${R}_skill.txt")
  "$PY" agent.py \
    --cases $SKILL_CASES \
    --models "$MODEL" \
    --output-dir "$EXP/local_${SAFE}/skill/$R" \
    --capability-mode skill-only \
    --evaluate \
    --eval-mode api \
    --eval-model "$EVAL_MODEL" \
    --log-level ERROR
done

echo "[$(date -Is)] ${MODEL} done"
