#!/usr/bin/env bash
# Run one model on one logical service and one or both prompt conditions.

set -euo pipefail

if [[ "$#" -ne 4 ]]; then
  echo "Usage: $0 MODEL_KEY SERVICE CONDITION EXPERIMENT_DIR" >&2
  exit 2
fi

MODEL_KEY="$1"
SERVICE="$2"
CONDITION="$3"
EXP="$4"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
MODEL_MANIFEST="$SCRIPT_DIR/model_manifest.json"
MCPMARK_VENV="${MCPMARK_VENV:-$SCRIPT_DIR/.venv}"
PYTHON_BIN="${PYTHON_BIN:-$MCPMARK_VENV/bin/python}"
POSTGRES_CLIENT_PREFIX="${POSTGRES_CLIENT_PREFIX:-$SCRIPT_DIR/.postgres-client}"
PLAYWRIGHT_NODE_PREFIX="${MCPMARK_PLAYWRIGHT_NODE_PREFIX:-$SCRIPT_DIR/.node-runtime}"
PLAYWRIGHT_NODE_BROWSERS_PATH="${MCPMARK_PLAYWRIGHT_NODE_BROWSERS_PATH:-$PLAYWRIGHT_NODE_PREFIX/browsers}"
SERVICE_ASSET_DIR="${MCPMARK_SERVICE_ASSET_DIR:-${MCPMARK_SERVICE_ASSET_ARCHIVE:-$REPO_ROOT/external/mcpmark-service-assets}}"
ALLOW_OLLAMA_PULL="${ALLOW_OLLAMA_PULL:-0}"
ALLOW_CONTAINER_PULL="${ALLOW_CONTAINER_PULL:-0}"
OLLAMA_READY_TIMEOUT="${OLLAMA_READY_TIMEOUT:-240}"
MODEL_PRELOAD_TIMEOUT="${MCPMARK_MODEL_PRELOAD_TIMEOUT:-1260}"
MCPMARK_STRICT_GPU_CHECK="${MCPMARK_STRICT_GPU_CHECK:-1}"
MCPMARK_DIRECT_MODE="${MCPMARK_DIRECT_MODE:-0}"
MCPMARK_PODMAN_SINGLE_ID_MODE="${MCPMARK_PODMAN_SINGLE_ID_MODE:-0}"
if [[ "$MCPMARK_DIRECT_MODE" != "0" && "$MCPMARK_DIRECT_MODE" != "1" ]]; then
  echo "MCPMARK_DIRECT_MODE must be 0 or 1." >&2
  exit 2
fi
if [[ "$MCPMARK_PODMAN_SINGLE_ID_MODE" != "0" &&
  "$MCPMARK_PODMAN_SINGLE_ID_MODE" != "1" ]]; then
  echo "MCPMARK_PODMAN_SINGLE_ID_MODE must be 0 or 1." >&2
  exit 2
fi

# tmux/SSH may carry a loopback proxy that exists only on the login client.
# Unset it inside this worker process tree only. This cannot modify the parent
# shell, VS Code, Codex, or user-level proxy configuration.
unset \
  HTTP_PROXY \
  HTTPS_PROXY \
  ALL_PROXY \
  http_proxy \
  https_proxy \
  all_proxy

if [[ "$MCPMARK_DIRECT_MODE" == "1" ]]; then
  JOB_ID="$$"
else
  JOB_ID="${SLURM_JOB_ID:-$$}"
fi
POSTGRES_IMAGE="docker.io/pgvector/pgvector:0.8.0-pg17-bookworm"
POSTGRES_CONTAINER=""
POSTGRES_CONTAINER_OWNER=""
POSTGRES_RUNTIME_OWNED=0
POSTGRES_PASSWORD_FILE=""

case "$SERVICE" in
  filesystem|postgres|playwright) ;;
  *)
    echo "Unknown logical service: $SERVICE" >&2
    exit 2
    ;;
esac
case "$CONDITION" in
  original|safety)
    RUN_CONDITIONS="$CONDITION"
    ;;
  both)
    RUN_CONDITIONS="original,safety"
    ;;
  *)
    echo "Unknown prompt condition: $CONDITION" >&2
    exit 2
    ;;
esac

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Experiment Python is missing: $PYTHON_BIN" >&2
  echo "Run $SCRIPT_DIR/setup_environment.sh first." >&2
  exit 1
fi

IFS=$'\t' read -r MODEL CONTEXT_LENGTH STARTUP_DELAY EXPECTED_GPU_COUNT < <(
  "$PYTHON_BIN" - "$MODEL_MANIFEST" "$MODEL_KEY" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    models = json.load(handle)["models"]
try:
    model = models[sys.argv[2]]
except KeyError:
    raise SystemExit(f"Unknown model key: {sys.argv[2]}")
gres = model.get("slurm_gres")
if not isinstance(gres, str) or not gres.startswith("gpu:"):
    raise SystemExit(f"Invalid frozen GPU resource for {sys.argv[2]}: {gres!r}")
try:
    gpu_count = int(gres.removeprefix("gpu:"))
except ValueError as error:
    raise SystemExit(
        f"Invalid frozen GPU resource for {sys.argv[2]}: {gres!r}"
    ) from error
print(
    model["served_model"],
    model["context_length"],
    model["startup_delay_seconds"],
    gpu_count,
    sep="\t",
)
PY
)

if ! [[ "$CONTEXT_LENGTH" =~ ^[1-9][0-9]*$ ]]; then
  echo "Invalid context length for $MODEL_KEY: $CONTEXT_LENGTH" >&2
  exit 1
fi
if ! [[ "$STARTUP_DELAY" =~ ^[0-9]+$ ]]; then
  echo "Invalid startup delay for $MODEL_KEY: $STARTUP_DELAY" >&2
  exit 1
fi
if ! [[ "$EXPECTED_GPU_COUNT" =~ ^[1-9][0-9]*$ ]]; then
  echo "Invalid GPU count for $MODEL_KEY: $EXPECTED_GPU_COUNT" >&2
  exit 1
fi
if [[ "$MCPMARK_STRICT_GPU_CHECK" != "0" ]] &&
  [[ "$MCPMARK_STRICT_GPU_CHECK" != "1" ]]; then
  echo "MCPMARK_STRICT_GPU_CHECK must be 0 or 1." >&2
  exit 2
fi
if [[ "$ALLOW_CONTAINER_PULL" != "0" && "$ALLOW_CONTAINER_PULL" != "1" ]]; then
  echo "ALLOW_CONTAINER_PULL must be 0 or 1." >&2
  exit 2
fi
if ! [[ "$MODEL_PRELOAD_TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then
  echo "MCPMARK_MODEL_PRELOAD_TIMEOUT must be a positive integer." >&2
  exit 2
fi

mkdir -p "$EXP/logs" "$EXP/status" "$EXP/results"
OLLAMA_LOG="$EXP/logs/${MODEL_KEY}_${SERVICE}_${CONDITION}_ollama_${JOB_ID}.log"
PRELOAD_RESPONSE="$EXP/logs/${MODEL_KEY}_${SERVICE}_${CONDITION}_preload_${JOB_ID}.json"
STATUS_FILE="$EXP/status/${MODEL_KEY}_${SERVICE}_${CONDITION}.done"
FAILED_FILE="$EXP/status/${MODEL_KEY}_${SERVICE}_${CONDITION}.failed"
RUNTIME_FILE="$EXP/status/${MODEL_KEY}_${SERVICE}_${CONDITION}.runtime"
OLLAMA_PID=""
PRELOAD_TEMP=""

rm -f -- "$FAILED_FILE" "$STATUS_FILE"

fail_job() {
  local reason="$1"
  printf '%s\n' \
    "model_key=$MODEL_KEY" \
    "served_model=$MODEL" \
    "service=$SERVICE" \
    "condition=$CONDITION" \
    "job_id=$JOB_ID" \
    "failed_at=$(date -Is)" \
    "reason=$reason" > "$FAILED_FILE"
  echo "[$(date -Is)] ERROR: $reason" >&2
  exit 1
}

cleanup() {
  local exit_status=$?
  local postgres_observed_owner

  if [[ "$exit_status" -ne 0 ]] &&
    [[ ! -f "$FAILED_FILE" ]] &&
    [[ ! -f "$STATUS_FILE" ]]; then
    printf '%s\n' \
      "model_key=$MODEL_KEY" \
      "served_model=$MODEL" \
      "service=$SERVICE" \
      "condition=$CONDITION" \
      "job_id=$JOB_ID" \
      "failed_at=$(date -Is)" \
      "reason=Unexpected worker exit with status $exit_status" >"$FAILED_FILE"
  fi
  if [[ -n "$OLLAMA_PID" ]]; then
    kill "$OLLAMA_PID" 2>/dev/null || true
    wait "$OLLAMA_PID" 2>/dev/null || true
  fi
  if [[ "$POSTGRES_RUNTIME_OWNED" == "1" ]] &&
    [[ -n "$POSTGRES_CONTAINER" ]] &&
    [[ -n "$POSTGRES_CONTAINER_OWNER" ]]; then
    postgres_observed_owner="$(
      docker inspect \
        --format '{{ index .Config.Labels "org.mcpmark.utility.owner" }}' \
        "$POSTGRES_CONTAINER" 2>/dev/null || true
    )"
    if [[ "$postgres_observed_owner" == "$POSTGRES_CONTAINER_OWNER" ]]; then
      docker rm --force --volumes "$POSTGRES_CONTAINER" >/dev/null 2>&1 || true
    else
      echo \
        "[$(date -Is)] refusing to remove PostgreSQL container with mismatched owner label: $POSTGRES_CONTAINER" \
        >&2
    fi
  fi
  if [[ -n "$POSTGRES_PASSWORD_FILE" && -f "$POSTGRES_PASSWORD_FILE" ]]; then
    rm -f -- "$POSTGRES_PASSWORD_FILE"
  fi
  if [[ -n "$PRELOAD_TEMP" && -f "$PRELOAD_TEMP" ]]; then
    rm -f -- "$PRELOAD_TEMP"
  fi
  return "$exit_status"
}
trap cleanup EXIT
trap 'exit 130' INT HUP
trap 'exit 143' TERM

cd "$REPO_ROOT"

export PATH="$SCRIPT_DIR/bin:$MCPMARK_VENV/bin:$POSTGRES_CLIENT_PREFIX/bin:$PATH"
export MCPMARK_REAL_PIPX="$MCPMARK_VENV/bin/pipx"
export MCPMARK_DOCKER_LOOPBACK_ONLY=1
export MCPMARK_PLAYWRIGHT_NODE_PREFIX="$PLAYWRIGHT_NODE_PREFIX"
export MCPMARK_PLAYWRIGHT_NODE_BROWSERS_PATH="$PLAYWRIGHT_NODE_BROWSERS_PATH"

normalize_image_tag() {
  local image="$1"
  image="${image#localhost/}"
  image="${image#docker.io/library/}"
  image="${image#docker.io/}"
  printf '%s\n' "$image"
}

container_image_present() {
  local target="$1"
  local output
  local visible
  target="$(normalize_image_tag "$target")"
  if ! output="$(docker images --format '{{.Repository}}:{{.Tag}}')"; then
    return 2
  fi
  while IFS= read -r visible; do
    [[ -n "$visible" ]] || continue
    if [[ "$(normalize_image_tag "$visible")" == "$target" ]]; then
      return 0
    fi
  done <<<"$output"
  return 1
}

ensure_container_image() {
  local image="$1"
  local archive="$2"
  if container_image_present "$image"; then
    return
  fi
  if [[ -f "$archive" ]]; then
    echo "[$(date -Is)] loading container image from $archive"
    docker load --input "$archive" >/dev/null ||
      fail_job "Could not load container image archive: $archive"
  elif [[ "$ALLOW_CONTAINER_PULL" == "1" && "$image" == */* ]]; then
    echo "[$(date -Is)] pulling missing container image $image"
    docker pull "$image" >/dev/null ||
      fail_job "Could not pull container image: $image"
  else
    fail_job \
      "Missing image $image and archive $archive (run prepare_service_assets.sh)"
  fi
  if ! container_image_present "$image"; then
    fail_job "Image is still unavailable after preparation: $image"
  fi
}

prepare_postgres_runtime() {
  local postgres_run_args
  local elapsed
  local postgres_container_candidate
  local postgres_container_owner
  local mapped_port
  local mapped_port_number
  local postgres_password
  local ready

  ensure_container_image \
    "$POSTGRES_IMAGE" \
    "$SERVICE_ASSET_DIR/pgvector_0.8.0-pg17-bookworm.tar"
  postgres_container_candidate="mcpv-pg-${JOB_ID}"
  postgres_password="$(
    "$PYTHON_BIN" - <<'PY'
import secrets
print(secrets.token_hex(24))
PY
  )"
  postgres_container_owner="$(
    "$PYTHON_BIN" - <<'PY'
import secrets
print(secrets.token_hex(24))
PY
  )"
  POSTGRES_PASSWORD_FILE="$(
    mktemp "${TMPDIR:-/tmp}/mcpmark-postgres-env.XXXXXX"
  )"
  chmod 600 "$POSTGRES_PASSWORD_FILE"
  printf 'POSTGRES_USER=postgres\nPOSTGRES_PASSWORD=%s\nPOSTGRES_DB=postgres\n' \
    "$postgres_password" >"$POSTGRES_PASSWORD_FILE"

  postgres_run_args=(
    run
    --detach
    --name "$postgres_container_candidate"
    --label "org.mcpmark.utility.job=$JOB_ID"
    --label "org.mcpmark.utility.owner=$postgres_container_owner"
    --pull=never
  )
  if [[ "$MCPMARK_PODMAN_SINGLE_ID_MODE" == "1" ]]; then
    postgres_run_args+=(
      --userns=keep-id:uid=999,gid=999
      --user=999:999
      --sysctl "net.ipv4.ping_group_range=999 999"
    )
  fi
  postgres_run_args+=(
    --env-file "$POSTGRES_PASSWORD_FILE"
    --publish "127.0.0.1::5432"
    "$POSTGRES_IMAGE"
  )
  docker "${postgres_run_args[@]}" >/dev/null ||
    fail_job "Could not start the dedicated PostgreSQL container"
  POSTGRES_CONTAINER="$postgres_container_candidate"
  POSTGRES_CONTAINER_OWNER="$postgres_container_owner"
  POSTGRES_RUNTIME_OWNED=1
  rm -f -- "$POSTGRES_PASSWORD_FILE"
  POSTGRES_PASSWORD_FILE=""

  mapped_port="$(docker port "$POSTGRES_CONTAINER" 5432/tcp)" ||
    fail_job "Could not inspect the PostgreSQL port mapping"
  if [[ "$mapped_port" =~ ^127\.0\.0\.1:([1-9][0-9]{0,4})$ ]]; then
    mapped_port_number="${BASH_REMATCH[1]}"
  else
    fail_job "PostgreSQL did not receive a loopback-only port mapping"
  fi
  if [[ "$mapped_port_number" -gt 65535 ]]; then
    fail_job "PostgreSQL received an invalid loopback port mapping"
  fi

  ready=0
  for ((elapsed = 0; elapsed < 180; elapsed += 2)); do
    if docker exec "$POSTGRES_CONTAINER" \
      pg_isready --host 127.0.0.1 --username postgres --dbname postgres \
      >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 2
  done
  if [[ "$ready" != "1" ]]; then
    docker logs "$POSTGRES_CONTAINER" 2>&1 | tail -n 120 >&2 || true
    fail_job "Dedicated PostgreSQL did not become ready"
  fi

  export POSTGRES_HOST=127.0.0.1
  export POSTGRES_PORT="$mapped_port_number"
  export POSTGRES_DATABASE=postgres
  export POSTGRES_USERNAME=postgres
  export POSTGRES_PASSWORD="$postgres_password"
  if ! PGPASSWORD="$POSTGRES_PASSWORD" psql \
    --host "$POSTGRES_HOST" \
    --port "$POSTGRES_PORT" \
    --username "$POSTGRES_USERNAME" \
    --dbname "$POSTGRES_DATABASE" \
    --no-password \
    --tuples-only \
    --command "SELECT 1" >/dev/null; then
    fail_job "Host PostgreSQL 17 client could not connect to the dedicated database"
  fi
  echo "[$(date -Is)] dedicated PostgreSQL is ready on loopback"
}

case "$SERVICE" in
  postgres)
    prepare_postgres_runtime
    ;;
esac

{
  printf 'service=%s\n' "$SERVICE"
  printf 'condition=%s\n' "$CONDITION"
  printf 'job_id=%s\n' "$JOB_ID"
  printf 'host=%s\n' "$(hostname)"
  printf 'external_proxy_policy=disabled-in-worker\n'
  printf 'containers_storage_conf=%s\n' "${CONTAINERS_STORAGE_CONF:-}"
  printf 'podman_local_root=%s\n' "${MCPMARK_PODMAN_LOCAL_ROOT:-}"
  printf 'podman_xdg_runtime_dir=%s\n' "${MCPMARK_PODMAN_XDG_RUNTIME_DIR:-}"
  printf 'podman_single_id_mode=%s\n' "$MCPMARK_PODMAN_SINGLE_ID_MODE"
  case "$SERVICE" in
    postgres)
      printf 'container_image=%s\n' "$POSTGRES_IMAGE"
      printf 'postgres_host=%s\n' "$POSTGRES_HOST"
      printf 'postgres_port=%s\n' "$POSTGRES_PORT"
      printf 'postgres_container=%s\n' "$POSTGRES_CONTAINER"
      ;;
  esac
  printf 'prepared_at=%s\n' "$(date -Is)"
} >"$RUNTIME_FILE"

if [[ "$MCPMARK_STRICT_GPU_CHECK" == "1" ]]; then
  if [[ -z "${CUDA_VISIBLE_DEVICES:-}" ]]; then
    fail_job "CUDA_VISIBLE_DEVICES is unset while strict GPU checking is enabled"
  fi
  IFS=',' read -r -a visible_gpu_ids <<<"$CUDA_VISIBLE_DEVICES"
  if [[ "${#visible_gpu_ids[@]}" -ne "$EXPECTED_GPU_COUNT" ]]; then
    fail_job \
      "$MODEL_KEY requires $EXPECTED_GPU_COUNT GPU(s), but CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
  fi
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    fail_job "nvidia-smi is unavailable while strict GPU checking is enabled"
  fi
  if ! nvidia-smi >/dev/null; then
    fail_job "nvidia-smi cannot communicate with the allocated GPU"
  fi
fi

export OPENAI_API_KEY="${OPENAI_API_KEY:-ollama}"
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_CONTEXT_LENGTH="$CONTEXT_LENGTH"
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-30m}"
export OLLAMA_FLASH_ATTENTION="${OLLAMA_FLASH_ATTENTION:-true}"
export OLLAMA_KV_CACHE_TYPE="${OLLAMA_KV_CACHE_TYPE:-q8_0}"
export OLLAMA_SCHED_SPREAD="${OLLAMA_SCHED_SPREAD:-true}"
export OLLAMA_NO_CLOUD=true
export OLLAMA_LLM_LIBRARY="${OLLAMA_CUDA_LIBRARY:-cuda_v12}"
export OLLAMA_VULKAN=false
OLLAMA_PORT="${MCPMARK_OLLAMA_PORT:-$((20000 + JOB_ID % 20000))}"
if ! [[ "$OLLAMA_PORT" =~ ^[0-9]+$ ]] ||
  [[ "$OLLAMA_PORT" -lt 1024 ]] ||
  [[ "$OLLAMA_PORT" -gt 65535 ]]; then
  fail_job "MCPMARK_OLLAMA_PORT must be an integer from 1024 through 65535"
fi
export OLLAMA_HOST="127.0.0.1:$OLLAMA_PORT"
export OPENAI_BASE_URL="http://$OLLAMA_HOST/v1"
export NO_PROXY="127.0.0.1,localhost,${NO_PROXY:-}"
export no_proxy="127.0.0.1,localhost,${no_proxy:-}"
printf '%s\n' \
  "cuda_visible_devices=${CUDA_VISIBLE_DEVICES:-}" \
  "expected_gpu_count=$EXPECTED_GPU_COUNT" \
  "ollama_port=$OLLAMA_PORT" >>"$RUNTIME_FILE"

if [[ "$MCPMARK_STRICT_GPU_CHECK" == "1" ]]; then
  export OLLAMA_DEBUG="${OLLAMA_DEBUG:-1}"
  export OLLAMA_LOAD_TIMEOUT="${OLLAMA_LOAD_TIMEOUT:-20m}"

  # Ollama's CUDA discovery has a short watchdog. On this cluster, cold-reading
  # the bundled backend from shared storage can exceed it and silently leave
  # Ollama on CPU. Read every backend file into the compute node's page cache
  # before starting the server.
  OLLAMA_BIN="$(readlink -f "$(command -v ollama)")"
  OLLAMA_LIBRARY_ROOT="${OLLAMA_LIBRARY_ROOT:-$(
    cd "$(dirname "$OLLAMA_BIN")/../lib/ollama" && pwd
  )}"
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

  # Slurm exports backend aliases that are irrelevant on these NVIDIA nodes and
  # can make Ollama probe the same ordinal through AMD or Vulkan paths.
  unset \
    ROCR_VISIBLE_DEVICES \
    HIP_VISIBLE_DEVICES \
    GPU_DEVICE_ORDINAL \
    HSA_OVERRIDE_GFX_VERSION \
    GGML_VK_VISIBLE_DEVICES
fi

if [[ "$STARTUP_DELAY" -gt 0 ]]; then
  sleep "$STARTUP_DELAY"
fi

ready=0
launch_attempts=1
if [[ "$MCPMARK_STRICT_GPU_CHECK" == "1" ]]; then
  launch_attempts=3
fi

for ((launch_attempt = 1; launch_attempt <= launch_attempts; launch_attempt++)); do
  attempt_log="${OLLAMA_LOG%.log}_attempt${launch_attempt}.log"
  ln -sfn "$(basename "$attempt_log")" "$OLLAMA_LOG"
  if [[ "${OLLAMA_SERVER_BYPASS_PROXY:-1}" == "1" ]]; then
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
  for ((elapsed = 0; elapsed < OLLAMA_READY_TIMEOUT; elapsed += 2)); do
    if curl \
      --fail \
      --silent \
      --show-error \
      --max-time 5 \
      "http://$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then
      ready=1
      break
    fi
    if ! kill -0 "$OLLAMA_PID" 2>/dev/null; then
      break
    fi
    sleep 2
  done

  if [[ "$ready" -eq 1 ]] &&
    {
      [[ "$MCPMARK_STRICT_GPU_CHECK" == "0" ]] ||
        grep -Eqi 'inference compute.*library=CUDA' "$attempt_log"
    }; then
    break
  fi

  echo "[$(date -Is)] Ollama launch attempt $launch_attempt failed" >&2
  tail -n 160 "$attempt_log" >&2 || true
  kill "$OLLAMA_PID" 2>/dev/null || true
  wait "$OLLAMA_PID" 2>/dev/null || true
  OLLAMA_PID=""
  ready=0
  if [[ "$launch_attempt" -lt "$launch_attempts" ]]; then
    sleep 5
  fi
done

if [[ "$ready" -ne 1 ]]; then
  tail -n 120 "$OLLAMA_LOG" >&2 || true
  if [[ "$MCPMARK_STRICT_GPU_CHECK" == "1" ]]; then
    fail_job "Ollama did not become ready with CUDA after 3 attempts"
  fi
  fail_job "Ollama did not become ready"
fi
if [[ "$MCPMARK_STRICT_GPU_CHECK" == "1" ]] &&
  ! grep -Eqi 'inference compute.*library=CUDA' "$OLLAMA_LOG"; then
  tail -n 160 "$OLLAMA_LOG" >&2 || true
  fail_job "Ollama did not discover a CUDA inference device"
fi

if ! ollama show "$MODEL" >/dev/null 2>&1; then
  if [[ "$ALLOW_OLLAMA_PULL" == "1" ]]; then
    ollama pull "$MODEL" || fail_job "Could not pull missing model $MODEL"
  else
    fail_job "Required Ollama model is missing: $MODEL"
  fi
fi
if ! OLLAMA_LIST_OUTPUT="$(ollama list)"; then
  fail_job "Could not list local Ollama models"
fi
MODEL_ARTIFACT_ID="$(
  awk -v model="$MODEL" '
    NR > 1 && $1 == model && !found {
      print $2
      found = 1
    }
  ' <<<"$OLLAMA_LIST_OUTPUT"
)"
unset OLLAMA_LIST_OUTPUT
if [[ ! "$MODEL_ARTIFACT_ID" =~ ^[0-9a-f]{12,64}$ ]]; then
  fail_job "Could not resolve an Ollama artifact ID for $MODEL"
fi
MODEL_ARTIFACT_DIR="$EXP/model_artifacts"
MODEL_ARTIFACT_FILE="$MODEL_ARTIFACT_DIR/${MODEL_KEY}.txt"
MODEL_ARTIFACT_LOCK="$MODEL_ARTIFACT_DIR/${MODEL_KEY}.lock"
mkdir -p "$MODEL_ARTIFACT_DIR"
exec {artifact_lock_fd}>"$MODEL_ARTIFACT_LOCK"
if ! flock "$artifact_lock_fd"; then
  fail_job "Could not lock the model artifact contract for $MODEL_KEY"
fi
if [[ -f "$MODEL_ARTIFACT_FILE" ]]; then
  if ! IFS=$'\t' read -r expected_model expected_artifact extra \
    <"$MODEL_ARTIFACT_FILE"; then
    flock -u "$artifact_lock_fd" || true
    fail_job "Could not read the model artifact contract for $MODEL_KEY"
  fi
  if [[ "$expected_model" != "$MODEL" ]] ||
    [[ "$expected_artifact" != "$MODEL_ARTIFACT_ID" ]] ||
    [[ -n "${extra:-}" ]]; then
    flock -u "$artifact_lock_fd" || true
    fail_job \
      "Ollama artifact contract mismatch for $MODEL_KEY: expected $expected_model/$expected_artifact, found $MODEL/$MODEL_ARTIFACT_ID"
  fi
else
  artifact_temp="$MODEL_ARTIFACT_DIR/.${MODEL_KEY}.${JOB_ID}.tmp"
  printf '%s\t%s\n' "$MODEL" "$MODEL_ARTIFACT_ID" >"$artifact_temp"
  mv -- "$artifact_temp" "$MODEL_ARTIFACT_FILE"
fi
flock -u "$artifact_lock_fd"
exec {artifact_lock_fd}>&-

# /api/tags, `ollama show`, and `ollama list` only prove that the server and
# manifest are available; they do not load model tensors.  Keep cold loading
# outside the short tool-call capability smoke so a large model is not
# cancelled when that smoke's HTTP timeout expires.
PRELOAD_PAYLOAD="$(
  "$PYTHON_BIN" - "$MODEL" "$CONTEXT_LENGTH" "$OLLAMA_KEEP_ALIVE" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "model": sys.argv[1],
            "stream": False,
            "keep_alive": sys.argv[3],
            "options": {"num_ctx": int(sys.argv[2])},
        },
        separators=(",", ":"),
    )
)
PY
)"
PRELOAD_TEMP="$(mktemp "$EXP/logs/.model-preload.${MODEL_KEY}.${SERVICE}.XXXXXX")"
PRELOAD_STARTED_AT="$(date -Is)"
printf '%s\n' \
  "model_preload_timeout_seconds=$MODEL_PRELOAD_TIMEOUT" \
  "model_preload_started_at=$PRELOAD_STARTED_AT" >>"$RUNTIME_FILE"
echo \
  "[$PRELOAD_STARTED_AT] preload model=$MODEL_KEY service=$SERVICE timeout=${MODEL_PRELOAD_TIMEOUT}s"
if ! curl \
  --fail \
  --silent \
  --show-error \
  --connect-timeout 10 \
  --max-time "$MODEL_PRELOAD_TIMEOUT" \
  --header 'Content-Type: application/json' \
  --request POST \
  --data-binary "$PRELOAD_PAYLOAD" \
  --output "$PRELOAD_TEMP" \
  "http://$OLLAMA_HOST/api/generate"; then
  fail_job "Ollama model preload failed or timed out"
fi
if ! PRELOAD_DETAIL="$(
  "$PYTHON_BIN" - "$PRELOAD_TEMP" "$MODEL" <<'PY'
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])
expected_model = sys.argv[2]
try:
    document = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    raise SystemExit(f"invalid preload response: {error}") from error
if not isinstance(document, dict) or document.get("done") is not True:
    raise SystemExit("preload response does not report done=true")
observed_model = document.get("model")
if observed_model not in (None, expected_model):
    raise SystemExit(
        f"preload response model mismatch: {observed_model!r} != {expected_model!r}"
    )
load_duration = document.get("load_duration")
done_reason = document.get("done_reason")
print(f"done_reason={done_reason!r} load_duration={load_duration!r}")
PY
)"; then
  fail_job "Ollama returned an invalid model preload response"
fi
mv -- "$PRELOAD_TEMP" "$PRELOAD_RESPONSE"
PRELOAD_TEMP=""
PRELOAD_FINISHED_AT="$(date -Is)"
printf '%s\n' \
  "model_preload_finished_at=$PRELOAD_FINISHED_AT" \
  "model_preload_response=$PRELOAD_RESPONSE" >>"$RUNTIME_FILE"
echo "[$PRELOAD_FINISHED_AT] preload complete $PRELOAD_DETAIL"

echo \
  "[$(date -Is)] preflight model=$MODEL_KEY service=$SERVICE condition=$CONDITION host=$(hostname)"
"$PYTHON_BIN" "$SCRIPT_DIR/run_experiment.py" preflight \
  --services "$SERVICE" \
  --base-url "$OPENAI_BASE_URL" \
  --served-model "$MODEL" ||
  fail_job "MCP/Ollama preflight failed"

if [[ "$MCPMARK_STRICT_GPU_CHECK" == "1" ]]; then
  OLLAMA_PS="$(ollama ps)"
  printf '%s\n' "$OLLAMA_PS"
  if ! printf '%s\n' "$OLLAMA_PS" |
    awk -v model="$MODEL" -v context="$CONTEXT_LENGTH" '
      NR > 1 &&
      $1 == model &&
      toupper($0) ~ /100%[[:space:]]+GPU/ &&
      $0 ~ ("(^|[[:space:]])" context "([[:space:]]|$)") {
        found = 1
      }
      END { exit(found ? 0 : 1) }
    '; then
    tail -n 120 "$OLLAMA_LOG" >&2 || true
    fail_job \
      "ollama ps does not show $MODEL at context $CONTEXT_LENGTH on 100% GPU"
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
    tail -n 120 "$OLLAMA_LOG" >&2 || true
    fail_job "nvidia-smi reports no GPU compute process after model preflight"
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
    "llama_context: n_ctx[[:space:]]+=[[:space:]]+${CONTEXT_LENGTH}$" \
    "$OLLAMA_LOG"; then
    tail -n 160 "$OLLAMA_LOG" >&2 || true
    fail_job "runtime context does not match $CONTEXT_LENGTH"
  fi
  if ! grep -Eq \
    "print_info: n_ctx_train[[:space:]]+=[[:space:]]+${CONTEXT_LENGTH}$" \
    "$OLLAMA_LOG"; then
    tail -n 160 "$OLLAMA_LOG" >&2 || true
    fail_job "$CONTEXT_LENGTH is not the model's native context limit"
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
fi

echo \
  "[$(date -Is)] run model=$MODEL_KEY service=$SERVICE condition=$CONDITION"
"$PYTHON_BIN" "$SCRIPT_DIR/run_experiment.py" run \
  --results-root "$EXP/results" \
  --model-label "$MODEL_KEY" \
  --served-model "$MODEL" \
  --model-artifact-id "$MODEL_ARTIFACT_ID" \
  --base-url "$OPENAI_BASE_URL" \
  --conditions "$RUN_CONDITIONS" \
  --services "$SERVICE" \
  --temperature 0 \
  --k 1 \
  --continue-on-error ||
  fail_job "Benchmark run failed"

printf '%s\n' \
  "model_key=$MODEL_KEY" \
  "served_model=$MODEL" \
  "service=$SERVICE" \
  "condition=$CONDITION" \
  "job_id=$JOB_ID" \
  "strict_gpu_check=$MCPMARK_STRICT_GPU_CHECK" \
  "cuda_visible_devices=${CUDA_VISIBLE_DEVICES:-}" \
  "expected_gpu_count=$EXPECTED_GPU_COUNT" \
  "ollama_port=$OLLAMA_PORT" \
  "context_length=$CONTEXT_LENGTH" \
  "ollama_artifact_id=$MODEL_ARTIFACT_ID" \
  "completed_at=$(date -Is)" > "$STATUS_FILE"
rm -f "$FAILED_FILE"
echo \
  "[$(date -Is)] completed model=$MODEL_KEY service=$SERVICE condition=$CONDITION"
