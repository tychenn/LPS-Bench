#!/usr/bin/env bash
# Backward-compatible entry point for already-submitted Slurm jobs.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/run_model_worker.sh" "$@"
