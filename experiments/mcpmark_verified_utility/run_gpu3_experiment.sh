#!/usr/bin/env bash
# Run the complete MCPMark utility experiment directly on gpu3 with four A40s.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
MODEL_MANIFEST="$SCRIPT_DIR/model_manifest.json"
TASK_MANIFEST="$SCRIPT_DIR/task_manifest.json"
SAFETY_PROMPT="$SCRIPT_DIR/safety_prompt.txt"
RUNNER="$SCRIPT_DIR/run_experiment.py"
WORKER="${MCPMARK_DIRECT_WORKER:-$SCRIPT_DIR/run_model_worker.sh}"
PYTHON_BOOTSTRAP="${PYTHON_BOOTSTRAP:-python3}"
MCPMARK_VENV="${MCPMARK_VENV:-$SCRIPT_DIR/.venv}"
PYTHON_BIN="$MCPMARK_VENV/bin/python"
RUN_TAG="${RUN_TAG:-$(date +%Y%m%d_%H%M%S)}"
EXP="${EXP:-$REPO_ROOT/runs/mcpmark_verified_utility_gpu3_${RUN_TAG}}"
EXPECTED_HOST="${MCPMARK_EXPECTED_HOST:-gpu3}"
GPU_IDS_TEXT="${MCPMARK_GPU_IDS:-0,1,2,3}"
SKIP_HOST_GPU_CHECK="${MCPMARK_SKIP_HOST_GPU_CHECK:-0}"
CONFIRM_NO_SLURM_JOBS="${MCPMARK_CONFIRM_NO_SLURM_JOBS:-0}"
OLLAMA_PORT_BASE="${MCPMARK_OLLAMA_PORT_BASE:-24000}"
MODEL_PRELOAD_TIMEOUT="${MCPMARK_MODEL_PRELOAD_TIMEOUT:-1260}"
PODMAN_LOCAL_ROOT="${MCPMARK_PODMAN_LOCAL_ROOT:-}"
PODMAN_XDG_RUNTIME_DIR="${MCPMARK_PODMAN_XDG_RUNTIME_DIR:-}"
PODMAN_STORAGE_CONFIG=""
PODMAN_GRAPH_ROOT=""
PODMAN_RUN_ROOT=""
PODMAN_FILESYSTEM_TYPE=""
SERVICES=(filesystem postgres playwright)
SCHEDULER_FINISHED=0
CONFIG_TEMP=""
STORAGE_CONFIG_TEMP=""
FAILURES=0
COMPLETED_UNITS=0
TOTAL_UNITS=12
UNIT_SEQUENCE=0
CHECK_ONLY=0

EXP="$(readlink -m -- "$EXP")"
if [[ "$SKIP_HOST_GPU_CHECK" == "0" ]]; then
  case "$EXP" in
    "$REPO_ROOT"/runs/*) ;;
    *)
      echo "Formal direct EXP must be a child of $REPO_ROOT/runs" >&2
      exit 2
      ;;
  esac
fi
case "$EXP" in
  /|"$REPO_ROOT"|"$REPO_ROOT/runs")
    echo "Refusing unsafe direct experiment directory: $EXP" >&2
    exit 2
    ;;
esac

usage() {
  cat <<'EOF'
Usage: run_gpu3_experiment.sh [--check-only]

Run the frozen 352-trajectory MCPMark Verified utility experiment directly on
gpu3. The scheduler launches 12 model × service workers; each worker runs both
original and safety conditions on one Ollama endpoint.

Required before a formal run:
  1. Cancel the old Slurm jobs.
  2. SSH to gpu3 and start a tmux session.
  3. Set MCPMARK_CONFIRM_NO_SLURM_JOBS=1.

Useful environment variables:
  EXP                         New or resumable experiment directory.
  MCPMARK_GPU_IDS             Four physical GPU indices (default: 0,1,2,3).
  MCPMARK_EXPECTED_HOST       Required short hostname (default: gpu3).
  MCPMARK_OLLAMA_PORT_BASE    First of 12 reserved ports (default: 24000).
  MCPMARK_MODEL_PRELOAD_TIMEOUT
                              Maximum model cold-load seconds (default: 1260).
  MCPMARK_PODMAN_LOCAL_ROOT   Podman graph storage on gpu3 local disk.

Test-only:
  MCPMARK_SKIP_HOST_GPU_CHECK=1
  MCPMARK_DIRECT_WORKER=/absolute/path/to/fake-worker
EOF
}

if [[ "$#" -ne 0 ]]; then
  if [[ "$#" -eq 1 ]]; then
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      --check-only)
        CHECK_ONLY=1
        ;;
      *)
        usage >&2
        exit 2
        ;;
    esac
  else
    usage >&2
    exit 2
  fi
fi

for value_name in SKIP_HOST_GPU_CHECK CONFIRM_NO_SLURM_JOBS; do
  value="${!value_name}"
  if [[ "$value" != "0" && "$value" != "1" ]]; then
    echo "$value_name must be 0 or 1." >&2
    exit 2
  fi
done
if ! [[ "$OLLAMA_PORT_BASE" =~ ^[0-9]+$ ]] ||
  [[ "$OLLAMA_PORT_BASE" -lt 1024 ]] ||
  [[ $((OLLAMA_PORT_BASE + TOTAL_UNITS - 1)) -gt 65535 ]]; then
  echo "MCPMARK_OLLAMA_PORT_BASE must reserve 12 ports within 1024-65535." >&2
  exit 2
fi
if ! [[ "$MODEL_PRELOAD_TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then
  echo "MCPMARK_MODEL_PRELOAD_TIMEOUT must be a positive integer." >&2
  exit 2
fi
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Experiment Python is missing: $PYTHON_BIN" >&2
  echo "Run $SCRIPT_DIR/setup_environment.sh first." >&2
  exit 1
fi
if [[ ! -x "$WORKER" ]]; then
  echo "Direct worker is not executable: $WORKER" >&2
  exit 1
fi
if [[ ! -f "$RUNNER" || ! -f "$MODEL_MANIFEST" ]]; then
  echo "Frozen runner or model manifest is missing." >&2
  exit 1
fi
if ! command -v flock >/dev/null 2>&1; then
  echo "flock is required for the direct scheduler lock." >&2
  exit 1
fi
if ! command -v setsid >/dev/null 2>&1; then
  echo "setsid is required for isolated worker process groups." >&2
  exit 1
fi

IFS=',' read -r -a GPU_IDS <<<"$GPU_IDS_TEXT"
if [[ "${#GPU_IDS[@]}" -ne 4 ]]; then
  echo "MCPMARK_GPU_IDS must contain exactly four comma-separated GPU indices." >&2
  exit 2
fi
declare -A SEEN_GPU_IDS=()
for gpu_id in "${GPU_IDS[@]}"; do
  if ! [[ "$gpu_id" =~ ^[0-9]+$ ]]; then
    echo "Invalid GPU index in MCPMARK_GPU_IDS: $gpu_id" >&2
    exit 2
  fi
  if [[ -n "${SEEN_GPU_IDS[$gpu_id]:-}" ]]; then
    echo "Duplicate GPU index in MCPMARK_GPU_IDS: $gpu_id" >&2
    exit 2
  fi
  SEEN_GPU_IDS[$gpu_id]=1
done

if [[ "$SKIP_HOST_GPU_CHECK" == "0" ]]; then
  if [[ "$CONFIRM_NO_SLURM_JOBS" != "1" ]]; then
    cat >&2 <<'EOF'
Refusing to start until the previous Slurm jobs are confirmed cancelled.
On the login node run:
  scancel {3799..3822}
  squeue -u "$USER"
Then export MCPMARK_CONFIRM_NO_SLURM_JOBS=1 on gpu3.
EOF
    exit 2
  fi
  actual_host="$(hostname -s)"
  if [[ "$actual_host" != "$EXPECTED_HOST" ]]; then
    echo "Direct formal run requires host $EXPECTED_HOST; current host: $actual_host" >&2
    exit 1
  fi
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "nvidia-smi is unavailable on $actual_host." >&2
    exit 1
  fi
  mapfile -t GPU_INVENTORY < <(
    env -u CUDA_VISIBLE_DEVICES \
      nvidia-smi --query-gpu=index,name --format=csv,noheader
  )
  for gpu_id in "${GPU_IDS[@]}"; do
    inventory_line="$(
      printf '%s\n' "${GPU_INVENTORY[@]}" |
        awk -F',' -v target="$gpu_id" '
          {
            gpu_index = $1
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", gpu_index)
            if (gpu_index == target) {
              print
            }
          }
        '
    )"
    if [[ -z "$inventory_line" ]]; then
      echo "GPU index $gpu_id is absent from nvidia-smi." >&2
      exit 1
    fi
    if [[ "$inventory_line" != *A40* ]]; then
      echo "GPU $gpu_id is not an A40: $inventory_line" >&2
      exit 1
    fi
  done
  BUSY_GPU_PROCESSES="$(
    env -u CUDA_VISIBLE_DEVICES \
      nvidia-smi \
      --query-compute-apps=pid,process_name \
      --format=csv,noheader 2>/dev/null |
      sed '/^[[:space:]]*$/d' || true
  )"
  if [[ -n "$BUSY_GPU_PROCESSES" ]]; then
    echo "Refusing to share gpu3 with existing compute processes:" >&2
    printf '%s\n' "$BUSY_GPU_PROCESSES" >&2
    exit 1
  fi
fi

if [[ -e "$EXP/submission.txt" || -e "$EXP/submission.in_progress" ]]; then
  echo "Refusing to mix a direct run with a Slurm experiment directory: $EXP" >&2
  echo "Choose a new EXP for the gpu3 run." >&2
  exit 1
fi

mkdir -p "$EXP/logs/direct" "$EXP/status" "$EXP/results"
exec 9>"$EXP/direct_scheduler.lock"
if ! flock -n 9; then
  echo "Another direct scheduler already owns: $EXP" >&2
  exit 1
fi

declare -A PID_MODEL=()
declare -A PID_SERVICE=()
declare -A PID_GPUS=()
declare -A PID_PORT=()
declare -A SERVICE_PID=()
declare -A GPU_BUSY=()
declare -A MODEL_GPU_COUNT=()
declare -A NEXT_MODEL_INDEX=()

for gpu_id in "${GPU_IDS[@]}"; do
  GPU_BUSY[$gpu_id]=0
done
for service in "${SERVICES[@]}"; do
  NEXT_MODEL_INDEX[$service]=0
done

terminate_worker_groups() {
  local pid
  local remaining

  for pid in "${!PID_MODEL[@]}"; do
    kill -TERM -- "-$pid" 2>/dev/null || true
  done
  for _ in {1..20}; do
    remaining=0
    for pid in "${!PID_MODEL[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
        remaining=1
      fi
    done
    [[ "$remaining" == "0" ]] && break
    sleep 0.5
  done
  for pid in "${!PID_MODEL[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill -KILL -- "-$pid" 2>/dev/null || true
    fi
    wait "$pid" 2>/dev/null || true
  done
}

cleanup_scheduler() {
  if [[ "$SCHEDULER_FINISHED" != "1" ]]; then
    terminate_worker_groups
  fi
  if [[ -n "$CONFIG_TEMP" && -e "$CONFIG_TEMP" ]]; then
    rm -f -- "$CONFIG_TEMP"
  fi
  if [[ -n "$STORAGE_CONFIG_TEMP" && -e "$STORAGE_CONFIG_TEMP" ]]; then
    rm -f -- "$STORAGE_CONFIG_TEMP"
  fi
}
trap cleanup_scheduler EXIT
trap 'exit 130' INT HUP
trap 'exit 143' TERM

prepare_local_podman_storage() {
  local current_uid
  local experiment_digest
  local fuse_overlayfs
  local owner_uid
  local free_bytes
  local podman_info_json
  local runtime_path

  current_uid="$(id -u)"
  experiment_digest="$(
    "$PYTHON_BIN" - "$EXP" <<'PY'
import hashlib
import sys

print(hashlib.sha256(sys.argv[1].encode()).hexdigest()[:16])
PY
  )"
  if [[ -z "$PODMAN_LOCAL_ROOT" ]]; then
    PODMAN_LOCAL_ROOT="/var/tmp/mcpmark-verified-utility-podman-${current_uid}/${experiment_digest}"
  fi
  if [[ -z "$PODMAN_XDG_RUNTIME_DIR" ]]; then
    PODMAN_XDG_RUNTIME_DIR="/run/user/${current_uid}/mcpmark-verified-utility-${experiment_digest}"
  fi
  PODMAN_LOCAL_ROOT="$(readlink -m -- "$PODMAN_LOCAL_ROOT")"
  PODMAN_XDG_RUNTIME_DIR="$(readlink -m -- "$PODMAN_XDG_RUNTIME_DIR")"

  case "$PODMAN_LOCAL_ROOT" in
    /|/tmp|/var/tmp)
      echo "Refusing unsafe Podman local root: $PODMAN_LOCAL_ROOT" >&2
      exit 2
      ;;
  esac
  if [[ "$PODMAN_LOCAL_ROOT" == *'"'* ||
    "$PODMAN_LOCAL_ROOT" == *\\* ||
    "$PODMAN_LOCAL_ROOT" == *$'\n'* ]]; then
    echo "Podman local root contains unsupported characters." >&2
    exit 2
  fi
  if [[ "$PODMAN_XDG_RUNTIME_DIR" == *'"'* ||
    "$PODMAN_XDG_RUNTIME_DIR" == *\\* ||
    "$PODMAN_XDG_RUNTIME_DIR" == *$'\n'* ]]; then
    echo "Podman XDG runtime path contains unsupported characters." >&2
    exit 2
  fi
  if [[ "$SKIP_HOST_GPU_CHECK" == "0" ]]; then
    case "$PODMAN_LOCAL_ROOT" in
      /tmp/*|/var/tmp/*) ;;
      *)
        echo \
          "Formal Podman storage must be under gpu3 local /tmp or /var/tmp: $PODMAN_LOCAL_ROOT" \
          >&2
        exit 2
        ;;
    esac
    case "$PODMAN_XDG_RUNTIME_DIR" in
      "/run/user/${current_uid}/"*) ;;
      *)
        echo \
          "Formal Podman runtime must be under /run/user/${current_uid}: $PODMAN_XDG_RUNTIME_DIR" \
          >&2
        exit 2
        ;;
    esac
  fi

  for runtime_path in "$PODMAN_LOCAL_ROOT" "$PODMAN_XDG_RUNTIME_DIR"; do
    if [[ -L "$runtime_path" ]]; then
      echo "Refusing symlinked Podman runtime path: $runtime_path" >&2
      exit 2
    fi
    mkdir -p -- "$runtime_path"
    owner_uid="$(stat -c '%u' "$runtime_path")"
    if [[ "$owner_uid" != "$current_uid" ]]; then
      echo "Podman runtime path is not owned by uid $current_uid: $runtime_path" >&2
      exit 2
    fi
    chmod 700 "$runtime_path"
  done

  PODMAN_GRAPH_ROOT="$PODMAN_LOCAL_ROOT/graphroot"
  PODMAN_RUN_ROOT="$PODMAN_XDG_RUNTIME_DIR/containers"
  mkdir -p -- "$PODMAN_GRAPH_ROOT"
  chmod 700 "$PODMAN_GRAPH_ROOT"
  PODMAN_FILESYSTEM_TYPE="$(stat -f -c '%T' "$PODMAN_GRAPH_ROOT")"
  if [[ "$SKIP_HOST_GPU_CHECK" == "0" ]]; then
    case "$PODMAN_FILESYSTEM_TYPE" in
      xfs|ext2/ext3|ext4|btrfs|tmpfs) ;;
      *)
        echo \
          "Podman graphroot is not on an approved local filesystem: $PODMAN_FILESYSTEM_TYPE ($PODMAN_GRAPH_ROOT)" \
          >&2
        exit 1
        ;;
    esac
    free_bytes="$(
      df -PB1 "$PODMAN_GRAPH_ROOT" |
        awk 'NR == 2 {print $4}'
    )"
    if ! [[ "$free_bytes" =~ ^[0-9]+$ ]] ||
      [[ "$free_bytes" -lt 5368709120 ]]; then
      echo "Podman graphroot needs at least 5 GiB free: $PODMAN_GRAPH_ROOT" >&2
      exit 1
    fi
  fi

  fuse_overlayfs="$(command -v fuse-overlayfs || true)"
  if [[ -z "$fuse_overlayfs" ]]; then
    if [[ "$SKIP_HOST_GPU_CHECK" == "0" ]]; then
      echo "fuse-overlayfs is required for rootless Podman." >&2
      exit 1
    fi
    fuse_overlayfs="/usr/bin/fuse-overlayfs"
  fi

  mkdir -p "$EXP/runtime/podman"
  chmod 700 "$EXP/runtime" "$EXP/runtime/podman"
  PODMAN_STORAGE_CONFIG="$EXP/runtime/podman/storage.conf"
  STORAGE_CONFIG_TEMP="$(mktemp "$EXP/runtime/podman/.storage.conf.XXXXXX")"
  {
    printf '[storage]\n'
    printf 'driver = "overlay"\n'
    printf 'graphroot = "%s"\n' "$PODMAN_GRAPH_ROOT"
    printf 'rootless_storage_path = "%s"\n' "$PODMAN_GRAPH_ROOT"
    printf '\n[storage.options.overlay]\n'
    printf 'mount_program = "%s"\n' "$fuse_overlayfs"
    printf 'ignore_chown_errors = "true"\n'
    printf 'mountopt = "nodev"\n'
  } >"$STORAGE_CONFIG_TEMP"
  chmod 600 "$STORAGE_CONFIG_TEMP"
  if [[ -f "$PODMAN_STORAGE_CONFIG" ]]; then
    if ! cmp -s "$STORAGE_CONFIG_TEMP" "$PODMAN_STORAGE_CONFIG"; then
      echo \
        "Existing experiment-local Podman configuration is incompatible: $PODMAN_STORAGE_CONFIG" \
        >&2
      diff -u "$PODMAN_STORAGE_CONFIG" "$STORAGE_CONFIG_TEMP" >&2 || true
      exit 1
    fi
    rm -f -- "$STORAGE_CONFIG_TEMP"
  else
    mv -- "$STORAGE_CONFIG_TEMP" "$PODMAN_STORAGE_CONFIG"
  fi
  STORAGE_CONFIG_TEMP=""

  export CONTAINERS_STORAGE_CONF="$PODMAN_STORAGE_CONFIG"
  export MCPMARK_PODMAN_LOCAL_ROOT="$PODMAN_LOCAL_ROOT"
  export MCPMARK_PODMAN_XDG_RUNTIME_DIR="$PODMAN_XDG_RUNTIME_DIR"
  export MCPMARK_PODMAN_SINGLE_ID_MODE=1
  unset MCPMARK_CONTAINER_CLI

  if [[ "$SKIP_HOST_GPU_CHECK" == "0" ]]; then
    if ! command -v podman >/dev/null 2>&1; then
      echo "podman is required for the formal gpu3 experiment." >&2
      exit 1
    fi
    podman_info_json="$("$SCRIPT_DIR/bin/docker" info --format json)" ||
      {
        echo "Could not initialize experiment-local Podman storage." >&2
        exit 1
      }
    PODMAN_INFO_JSON="$podman_info_json" "$PYTHON_BIN" - \
      "$PODMAN_GRAPH_ROOT" \
      "$PODMAN_RUN_ROOT" \
      "$PODMAN_FILESYSTEM_TYPE" <<'PY'
import json
import os
import sys

expected_graphroot, expected_runroot, filesystem_type = sys.argv[1:]
info = json.loads(os.environ["PODMAN_INFO_JSON"])
store = info.get("store", {})
actual_graphroot = store.get("graphRoot")
actual_runroot = store.get("runRoot")
driver = store.get("graphDriverName")
if actual_graphroot != expected_graphroot:
    raise SystemExit(
        f"Podman graphroot mismatch: {actual_graphroot!r} != {expected_graphroot!r}"
    )
if actual_runroot != expected_runroot:
    raise SystemExit(
        f"Podman runroot mismatch: {actual_runroot!r} != {expected_runroot!r}"
    )
if driver != "overlay":
    raise SystemExit(f"Podman storage driver is not overlay: {driver!r}")
print(
    "Experiment-local Podman storage ready: "
    f"{actual_graphroot} ({filesystem_type}), runroot={actual_runroot}"
)
PY
  fi
}

prepare_local_podman_storage

"$SCRIPT_DIR/setup_environment.sh" --check-only
"$SCRIPT_DIR/prepare_service_assets.sh" --check-only
"$PYTHON_BIN" "$RUNNER" validate
if [[ "$CHECK_ONLY" == "1" ]]; then
  echo "Direct gpu3 experiment preflight passed: $EXP"
  SCHEDULER_FINISHED=1
  exit 0
fi

PLAN_PATH="$EXP/plan.json"
if [[ ! -f "$PLAN_PATH" ]]; then
  "$PYTHON_BIN" "$RUNNER" plan \
    --output "$PLAN_PATH" \
    --models all \
    --conditions all \
    --services all \
    --k 1
fi
"$PYTHON_BOOTSTRAP" - \
  "$PLAN_PATH" \
  "$MODEL_MANIFEST" \
  "$TASK_MANIFEST" \
  "$SAFETY_PROMPT" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

plan_path = Path(sys.argv[1])
model_manifest_path = Path(sys.argv[2])
task_manifest_path = Path(sys.argv[3])
safety_prompt_path = Path(sys.argv[4])
with plan_path.open(encoding="utf-8") as handle:
    plan = json.load(handle)
with model_manifest_path.open(encoding="utf-8") as handle:
    models = json.load(handle)["models"]
if plan.get("job_count") != 352 or len(plan.get("jobs", [])) != 352:
    raise SystemExit("The direct-run plan must contain exactly 352 jobs")
if plan.get("models") != list(models):
    raise SystemExit("The direct-run plan model order is incompatible")
if plan.get("conditions") != ["original", "safety"]:
    raise SystemExit("The direct-run plan conditions are incompatible")
if plan.get("services") != ["filesystem", "postgres", "playwright"]:
    raise SystemExit("The direct-run plan services are incompatible")
digest = hashlib.sha256(model_manifest_path.read_bytes()).hexdigest()
if plan.get("model_manifest_sha256") != digest:
    raise SystemExit("The direct-run plan model manifest hash is incompatible")
digest = hashlib.sha256(task_manifest_path.read_bytes()).hexdigest()
if plan.get("task_manifest_sha256") != digest:
    raise SystemExit("The direct-run plan task manifest hash is incompatible")
digest = hashlib.sha256(safety_prompt_path.read_bytes()).hexdigest()
if plan.get("safety_prompt_sha256") != digest:
    raise SystemExit("The direct-run plan safety prompt hash is incompatible")
with task_manifest_path.open(encoding="utf-8") as handle:
    task_manifest = json.load(handle)
if plan.get("source_commit") != task_manifest.get("source_commit"):
    raise SystemExit("The direct-run plan source commit is incompatible")
PY

mapfile -t MODEL_RESOURCE_LINES < <(
  "$PYTHON_BOOTSTRAP" - "$MODEL_MANIFEST" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    models = json.load(handle)["models"]
for model_key, model in models.items():
    gres = model.get("slurm_gres")
    if not isinstance(gres, str) or not gres.startswith("gpu:"):
        raise SystemExit(f"invalid frozen GPU resource for {model_key}: {gres!r}")
    try:
        gpu_count = int(gres.removeprefix("gpu:"))
    except ValueError as error:
        raise SystemExit(
            f"invalid frozen GPU resource for {model_key}: {gres!r}"
        ) from error
    if gpu_count not in (1, 2):
        raise SystemExit(f"unsupported GPU count for {model_key}: {gpu_count}")
    print(model_key, gpu_count, sep="\t")
PY
)
MODELS=()
for resource_line in "${MODEL_RESOURCE_LINES[@]}"; do
  IFS=$'\t' read -r model_key gpu_count <<<"$resource_line"
  MODELS+=("$model_key")
  MODEL_GPU_COUNT[$model_key]="$gpu_count"
done
if [[ "${#MODELS[@]}" -ne 4 ]]; then
  echo "Direct scheduling requires exactly four frozen models." >&2
  exit 1
fi

CONFIG_PATH="$EXP/direct_run_config.txt"
CONFIG_TEMP="$(mktemp "$EXP/.direct_run_config.XXXXXX")"
{
  printf 'schema_version=1\n'
  printf 'execution_mode=gpu3-direct-four-a40\n'
  printf 'expected_host=%s\n' "$EXPECTED_HOST"
  printf 'gpu_ids=%s\n' "$GPU_IDS_TEXT"
  printf 'ollama_port_base=%s\n' "$OLLAMA_PORT_BASE"
  printf 'task_manifest_sha256=%s\n' \
    "$(sha256sum "$TASK_MANIFEST" | awk '{print $1}')"
  printf 'model_manifest_sha256=%s\n' \
    "$(sha256sum "$MODEL_MANIFEST" | awk '{print $1}')"
  printf 'runner_sha256=%s\n' \
    "$(sha256sum "$RUNNER" | awk '{print $1}')"
  printf 'worker_sha256=%s\n' \
    "$(sha256sum "$WORKER" | awk '{print $1}')"
  printf 'docker_wrapper_sha256=%s\n' \
    "$(sha256sum "$SCRIPT_DIR/bin/docker" | awk '{print $1}')"
  printf 'pipx_wrapper_sha256=%s\n' \
    "$(sha256sum "$SCRIPT_DIR/bin/pipx" | awk '{print $1}')"
  printf 'scheduler_sha256=%s\n' \
    "$(sha256sum "${BASH_SOURCE[0]}" | awk '{print $1}')"
  printf 'plan_sha256=%s\n' \
    "$(sha256sum "$PLAN_PATH" | awk '{print $1}')"
  printf 'plan_job_count=352\n'
  printf 'worker_units=12\n'
  printf 'conditions=original,safety\n'
  printf 'services=filesystem,postgres,playwright\n'
  printf 'proxy_policy=unset-worker-http-https-all-proxy\n'
  printf 'model_preload_timeout_seconds=%s\n' "$MODEL_PRELOAD_TIMEOUT"
  printf 'podman_storage_config=%s\n' "$PODMAN_STORAGE_CONFIG"
  printf 'podman_storage_config_sha256=%s\n' \
    "$(sha256sum "$PODMAN_STORAGE_CONFIG" | awk '{print $1}')"
  printf 'podman_graphroot=%s\n' "$PODMAN_GRAPH_ROOT"
  printf 'podman_runroot=%s\n' "$PODMAN_RUN_ROOT"
  printf 'podman_filesystem_type=%s\n' "$PODMAN_FILESYSTEM_TYPE"
  printf 'podman_single_id_mode=1\n'
} >"$CONFIG_TEMP"
if [[ -f "$CONFIG_PATH" ]]; then
  if ! cmp -s "$CONFIG_TEMP" "$CONFIG_PATH"; then
    echo "Existing direct-run configuration is incompatible: $CONFIG_PATH" >&2
    diff -u "$CONFIG_PATH" "$CONFIG_TEMP" >&2 || true
    exit 1
  fi
  rm -f -- "$CONFIG_TEMP"
  CONFIG_TEMP=""
else
  mv -- "$CONFIG_TEMP" "$CONFIG_PATH"
  CONFIG_TEMP=""
fi

if [[ -f "$EXP/direct_run.done" ]]; then
  echo "Direct experiment is already complete: $EXP"
  SCHEDULER_FINISHED=1
  exit 0
fi
rm -f -- "$EXP/direct_run.failed"

status_is_complete() {
  local model_key="$1"
  local service="$2"
  local status_file="$EXP/status/${model_key}_${service}_both.done"

  [[ -f "$status_file" ]] || return 1
  grep -Fqx "model_key=$model_key" "$status_file" &&
    grep -Fqx "service=$service" "$status_file" &&
    grep -Fqx "condition=both" "$status_file"
}

advance_completed_units() {
  local service="$1"
  local index
  local model_key

  index="${NEXT_MODEL_INDEX[$service]}"
  while [[ "$index" -lt "${#MODELS[@]}" ]]; do
    model_key="${MODELS[$index]}"
    if ! status_is_complete "$model_key" "$service"; then
      break
    fi
    echo \
      "[$(date -Is)] resume-skip model=$model_key service=$service status=done"
    index=$((index + 1))
    COMPLETED_UNITS=$((COMPLETED_UNITS + 1))
  done
  NEXT_MODEL_INDEX[$service]="$index"
}

free_gpu_count() {
  local gpu_id
  local count=0

  for gpu_id in "${GPU_IDS[@]}"; do
    if [[ "${GPU_BUSY[$gpu_id]}" == "0" ]]; then
      count=$((count + 1))
    fi
  done
  printf '%s\n' "$count"
}

allocate_gpus() {
  local needed="$1"
  local gpu_id
  local selected=()

  for gpu_id in "${GPU_IDS[@]}"; do
    if [[ "${GPU_BUSY[$gpu_id]}" == "0" ]]; then
      selected+=("$gpu_id")
      if [[ "${#selected[@]}" -eq "$needed" ]]; then
        break
      fi
    fi
  done
  if [[ "${#selected[@]}" -ne "$needed" ]]; then
    return 1
  fi
  for gpu_id in "${selected[@]}"; do
    GPU_BUSY[$gpu_id]=1
  done
  ALLOCATED_GPUS="$(IFS=,; printf '%s' "${selected[*]}")"
}

release_gpus() {
  local gpu_text="$1"
  local released=()
  local gpu_id

  IFS=',' read -r -a released <<<"$gpu_text"
  for gpu_id in "${released[@]}"; do
    GPU_BUSY[$gpu_id]=0
  done
}

launch_unit() {
  local model_key="$1"
  local service="$2"
  local gpu_count="${MODEL_GPU_COUNT[$model_key]}"
  local port
  local log_prefix
  local pid

  allocate_gpus "$gpu_count" || return 1
  port=$((OLLAMA_PORT_BASE + UNIT_SEQUENCE))
  UNIT_SEQUENCE=$((UNIT_SEQUENCE + 1))
  log_prefix="$EXP/logs/direct/${model_key}_${service}_both"
  echo \
    "[$(date -Is)] launch model=$model_key service=$service gpus=$ALLOCATED_GPUS port=$port"
  setsid env \
    -u HTTP_PROXY \
    -u HTTPS_PROXY \
    -u ALL_PROXY \
    -u http_proxy \
    -u https_proxy \
    -u all_proxy \
    -u MCPMARK_CONTAINER_CLI \
    "CUDA_VISIBLE_DEVICES=$ALLOCATED_GPUS" \
    "CONTAINERS_STORAGE_CONF=$PODMAN_STORAGE_CONFIG" \
    "MCPMARK_DIRECT_MODE=1" \
    "MCPMARK_OLLAMA_PORT=$port" \
    "MCPMARK_MODEL_PRELOAD_TIMEOUT=$MODEL_PRELOAD_TIMEOUT" \
    "MCPMARK_PODMAN_LOCAL_ROOT=$PODMAN_LOCAL_ROOT" \
    "MCPMARK_PODMAN_SINGLE_ID_MODE=1" \
    "MCPMARK_PODMAN_XDG_RUNTIME_DIR=$PODMAN_XDG_RUNTIME_DIR" \
    "MCPMARK_STRICT_GPU_CHECK=1" \
    "REPO_ROOT=$REPO_ROOT" \
    "MCPMARK_VENV=$MCPMARK_VENV" \
    "$WORKER" "$model_key" "$service" both "$EXP" \
    >"${log_prefix}.out" 2>"${log_prefix}.err" &
  pid=$!
  PID_MODEL[$pid]="$model_key"
  PID_SERVICE[$pid]="$service"
  PID_GPUS[$pid]="$ALLOCATED_GPUS"
  PID_PORT[$pid]="$port"
  SERVICE_PID[$service]="$pid"
  NEXT_MODEL_INDEX[$service]=$((NEXT_MODEL_INDEX[$service] + 1))
}

for service in "${SERVICES[@]}"; do
  advance_completed_units "$service"
done

while [[ "$COMPLETED_UNITS" -lt "$TOTAL_UNITS" ]]; do
  # Consider two-GPU service heads before one-GPU heads so a ready 70B unit
  # cannot be starved by later small-model work.
  for desired_gpu_count in 2 1; do
    for service in "${SERVICES[@]}"; do
      [[ -z "${SERVICE_PID[$service]:-}" ]] || continue
      advance_completed_units "$service"
      index="${NEXT_MODEL_INDEX[$service]}"
      [[ "$index" -lt "${#MODELS[@]}" ]] || continue
      model_key="${MODELS[$index]}"
      gpu_count="${MODEL_GPU_COUNT[$model_key]}"
      [[ "$gpu_count" -eq "$desired_gpu_count" ]] || continue
      available="$(free_gpu_count)"
      if [[ "$available" -ge "$gpu_count" ]]; then
        launch_unit "$model_key" "$service"
      fi
    done
  done

  if [[ "${#PID_MODEL[@]}" -eq 0 ]]; then
    if [[ "$COMPLETED_UNITS" -ge "$TOTAL_UNITS" ]]; then
      break
    fi
    echo "Direct scheduler deadlock: pending units exist but none can launch." >&2
    exit 1
  fi

  active_pids=("${!PID_MODEL[@]}")
  finished_pid=""
  set +e
  wait -n -p finished_pid "${active_pids[@]}"
  worker_status=$?
  set -e
  if [[ -z "$finished_pid" || -z "${PID_MODEL[$finished_pid]:-}" ]]; then
    echo "Could not identify the completed direct worker." >&2
    exit 1
  fi

  model_key="${PID_MODEL[$finished_pid]}"
  service="${PID_SERVICE[$finished_pid]}"
  allocated="${PID_GPUS[$finished_pid]}"
  port="${PID_PORT[$finished_pid]}"
  release_gpus "$allocated"
  unset 'SERVICE_PID[$service]'
  unset 'PID_MODEL[$finished_pid]'
  unset 'PID_SERVICE[$finished_pid]'
  unset 'PID_GPUS[$finished_pid]'
  unset 'PID_PORT[$finished_pid]'
  COMPLETED_UNITS=$((COMPLETED_UNITS + 1))

  if [[ "$worker_status" -eq 0 ]]; then
    if [[ "$WORKER" == "$SCRIPT_DIR/run_model_worker.sh" ]] &&
      ! status_is_complete "$model_key" "$service"; then
      worker_status=1
      echo \
        "[$(date -Is)] worker exited zero without a valid done file: model=$model_key service=$service" \
        >&2
    fi
  fi
  if [[ "$worker_status" -eq 0 ]]; then
    echo \
      "[$(date -Is)] complete model=$model_key service=$service gpus=$allocated port=$port"
  else
    FAILURES=$((FAILURES + 1))
    echo \
      "[$(date -Is)] failed model=$model_key service=$service gpus=$allocated port=$port exit=$worker_status" \
      >&2
  fi
done

if [[ "$FAILURES" -ne 0 ]]; then
  printf '%s\n' \
    "failed_units=$FAILURES" \
    "finished_at=$(date -Is)" >"$EXP/direct_run.failed"
  echo \
    "Direct run finished with $FAILURES failed unit(s); rerun the same command to resume." \
    >&2
  SCHEDULER_FINISHED=1
  exit 1
fi

printf '%s\n' \
  "worker_units=12" \
  "expected_trajectories=352" \
  "completed_at=$(date -Is)" >"$EXP/direct_run.done"
SCHEDULER_FINISHED=1
echo "Direct gpu3 experiment completed: $EXP"
