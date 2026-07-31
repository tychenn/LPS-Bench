#!/usr/bin/env bash
# Fetch the official MCP-Bench repository.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TARGET="${MCPBENCH_CHECKOUT:-$REPO_ROOT/external/mcp-bench}"
URL="https://github.com/Accenture/mcp-bench.git"

if [[ -e "$TARGET" && ! -d "$TARGET/.git" ]]; then
  echo "Refusing to overwrite non-checkout path: $TARGET" >&2
  exit 1
fi

if [[ ! -d "$TARGET/.git" ]]; then
  git clone "$URL" "$TARGET"
else
  echo "Checkout already exists; not pulling or changing its revision: $TARGET"
fi

revision="$(git -C "$TARGET" rev-parse HEAD)"
for required in \
  "$TARGET/mcp_servers/commands.json" \
  "$TARGET/tasks/mcpbench_tasks_single_runner_format.json" \
  "$TARGET/tasks/mcpbench_tasks_multi_2server_runner_format.json" \
  "$TARGET/tasks/mcpbench_tasks_multi_3server_runner_format.json"; do
  [[ -s "$required" ]] || {
    echo "Required upstream file is missing: $required" >&2
    exit 1
  }
done
echo "MCP-Bench checkout ready: $TARGET"
echo "Pinned revision for this setup: $revision"
