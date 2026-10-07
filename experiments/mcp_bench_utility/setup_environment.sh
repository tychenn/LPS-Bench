#!/usr/bin/env bash
# Install MCP-Bench dependencies without changing system packages.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHECKOUT="${MCPBENCH_CHECKOUT:-$REPO_ROOT/external/mcp-bench}"
VENV="${MCPBENCH_VENV:-$SCRIPT_DIR/.venv}"
NPM_PREFIX="${MCPBENCH_NPM_PREFIX:-$SCRIPT_DIR/.npm-prefix}"
CHECK_ONLY=0
USER_HOME_DIR="$(getent passwd "$(id -u)" | cut -d: -f6)"

if [[ -z "$USER_HOME_DIR" ]]; then
  echo "Could not resolve the current user's home directory." >&2
  exit 1
fi

if [[ "${1:-}" == "--check-only" ]]; then
  CHECK_ONLY=1
elif [[ "$#" -ne 0 ]]; then
  echo "Usage: $0 [--check-only]" >&2
  exit 2
fi

if [[ ! -d "$CHECKOUT/.git" ]]; then
  echo "MCP-Bench is not downloaded: $CHECKOUT" >&2
  echo "Run $SCRIPT_DIR/fetch_benchmark.sh first." >&2
  exit 1
fi
if [[ ! -f "$CHECKOUT/mcp_servers/install.sh" ]]; then
  echo "Invalid MCP-Bench checkout: $CHECKOUT" >&2
  exit 1
fi
for required in \
  "$CHECKOUT/mcp_servers/commands.json" \
  "$CHECKOUT/tasks/mcpbench_tasks_single_runner_format.json" \
  "$CHECKOUT/tasks/mcpbench_tasks_multi_2server_runner_format.json" \
  "$CHECKOUT/tasks/mcpbench_tasks_multi_3server_runner_format.json"; do
  [[ -s "$required" ]] || {
    echo "Required upstream file is missing: $required" >&2
    exit 1
  }
done

export PATH="$USER_HOME_DIR/.local/bin:$SCRIPT_DIR/bin:$NPM_PREFIX/bin:$PATH"
for command_name in git curl wget gcc make node npm ollama; do
  command -v "$command_name" >/dev/null || {
    echo "Required command is missing: $command_name" >&2
    exit 1
  }
done
node_major="$(node --version | sed -E 's/^v([0-9]+).*/\1/')"
if ! [[ "$node_major" =~ ^[0-9]+$ ]] || [[ "$node_major" -lt 18 ]]; then
  echo "Node.js 18+ is required; found $(node --version)." >&2
  exit 1
fi

if [[ "$CHECK_ONLY" == "0" && ! -x "$VENV/bin/python" ]]; then
  python_candidate="${MCPBENCH_PYTHON:-}"
  for candidate in \
    "$python_candidate" \
    "$USER_HOME_DIR/anaconda3/bin/python" \
    "$USER_HOME_DIR/miniconda3/bin/python" \
    "$REPO_ROOT/experiments/mcpmark_verified_utility/.venv/bin/python" \
    "python3.12" \
    "python3"; do
    [[ -n "$candidate" ]] || continue
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" -c \
        'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
        python_candidate="$candidate"
        break
      fi
    fi
  done
  if [[ -z "$python_candidate" ]]; then
    echo "Python 3.10+ is required." >&2
    exit 1
  fi
  "$python_candidate" -m venv "$VENV"
fi

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Experiment environment is missing: $VENV" >&2
  exit 1
fi
if ! "$VENV/bin/python" -c \
  'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
  echo "Experiment Python must be 3.10+." >&2
  exit 1
fi

export VIRTUAL_ENV="$VENV"
export PATH="$VENV/bin:$PATH"
export npm_config_prefix="$NPM_PREFIX"

if [[ "$CHECK_ONLY" == "0" ]]; then
  # Keep proxy changes scoped to this setup process and its children. Override
  # stale ~/.npmrc values with the currently working shell proxy without
  # editing either npm config or the parent environment.
  setup_proxy="${HTTPS_PROXY:-${HTTP_PROXY:-}}"
  export NO_PROXY="127.0.0.1,localhost${NO_PROXY:+,$NO_PROXY}"
  export no_proxy="$NO_PROXY"
  if [[ -n "$setup_proxy" ]]; then
    export npm_config_proxy="$setup_proxy"
    export npm_config_https_proxy="$setup_proxy"
  else
    export npm_config_proxy=null
    export npm_config_https_proxy=null
  fi

  python -m pip install \
    wheel \
    uv
  # The upstream Met Museum package imports node:process but omits @types/node
  # from devDependencies. Add it locally before the upstream TypeScript build.
  (
    cd "$CHECKOUT/mcp_servers/metmuseum-mcp"
    npm install --save-dev '@types/node@^24'
    node - "tsconfig.json" <<'JS'
const fs = require("node:fs");
const path = process.argv[2];
const config = JSON.parse(fs.readFileSync(path, "utf8"));
config.compilerOptions ||= {};
const types = new Set(config.compilerOptions.types || []);
types.add("node");
config.compilerOptions.types = [...types];
fs.writeFileSync(path, `${JSON.stringify(config, null, 2)}\n`);
JS
  )
  bash "$SCRIPT_DIR/install_selected_services.sh" \
    "$CHECKOUT" \
    "$SCRIPT_DIR/runner_requirements.txt"
  python "$SCRIPT_DIR/select_cases.py" \
    --checkout "$CHECKOUT" \
    --output-json "$SCRIPT_DIR/selected_tasks.json" \
    --output-markdown "$SCRIPT_DIR/selected_cases.md"
fi

python - <<'PY'
import importlib.metadata as metadata

import aiohttp
import json_repair
import jsonschema
import openai
import yaml
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp import FastMCP

major = int(metadata.version("mcp").split(".", 1)[0])
if major != 1:
    raise SystemExit(f"MCP SDK 1.x is required; found {metadata.version('mcp')}")
PY
for required_file in \
  "$SCRIPT_DIR/selected_tasks.json" \
  "$SCRIPT_DIR/selected_cases.md"; do
  [[ -s "$required_file" ]] || {
    echo "Frozen selection is missing: $required_file" >&2
    exit 1
  }
done
python "$SCRIPT_DIR/select_cases.py" \
  --checkout "$CHECKOUT" \
  --output-json "/tmp/mcpbench-selected-tasks-check.json" \
  --output-markdown "/tmp/mcpbench-selected-cases-check.md"
cmp -s "$SCRIPT_DIR/selected_tasks.json" \
  "/tmp/mcpbench-selected-tasks-check.json" || {
  echo "Frozen selected_tasks.json does not match the current checkout." >&2
  exit 1
}
cmp -s "$SCRIPT_DIR/selected_cases.md" \
  "/tmp/mcpbench-selected-cases-check.md" || {
  echo "Frozen selected_cases.md does not match the current checkout." >&2
  exit 1
}
rm -f -- \
  "/tmp/mcpbench-selected-tasks-check.json" \
  "/tmp/mcpbench-selected-cases-check.md"

echo "MCP-Bench environment and frozen task selection are ready."
