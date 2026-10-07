#!/usr/bin/env bash
# Install only MCP servers referenced by the frozen deployment-feasible subset.

set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 MCPBENCH_CHECKOUT RUNNER_REQUIREMENTS" >&2
  exit 2
fi

CHECKOUT="$(readlink -m -- "$1")"
RUNNER_REQUIREMENTS="$(readlink -m -- "$2")"
SERVERS="$CHECKOUT/mcp_servers"
: "${VIRTUAL_ENV:?The experiment virtual environment must be active}"
EXPERIMENT_PYTHON="$VIRTUAL_ENV/bin/python"
[[ -x "$EXPERIMENT_PYTHON" ]] || {
  echo "Experiment Python is missing: $EXPERIMENT_PYTHON" >&2
  exit 1
}

[[ -f "$SERVERS/requirements.txt" ]] || {
  echo "MCP server requirements are missing: $SERVERS" >&2
  exit 1
}

echo "[mcp-bench setup] installing shared Python dependencies"
uv pip install -r "$SERVERS/requirements.txt"

NODE_SERVERS=(
  "context7-mcp"
  "dexpaprika-mcp"
  "hugeicons-mcp-server"
  "math-mcp"
  "metmuseum-mcp"
  "okx-mcp"
  "openapi-mcp-server"
)
for server in "${NODE_SERVERS[@]}"; do
  directory="$SERVERS/$server"
  echo "[mcp-bench setup] installing Node service: $server"
  (
    cd "$directory"
    npm install
    if [[ "$server" == "metmuseum-mcp" ]]; then
      npm install --save-dev \
        'typescript@^7' \
        '@types/node@^24' \
        '@types/image-to-base64@^2'
      npx tsc
    elif node -e \
      'const p=require("./package.json"); process.exit(p.scripts?.build ? 0 : 1)'; then
      npm run build
    fi
  )
done

REQUIREMENT_SERVERS=(
  "call-for-papers-mcp/call-for-papers-mcp-main"
  "car-price-mcp-main"
  "fruityvice-mcp"
  "game-trends-mcp"
  "movie-recommender-mcp/movie-reccomender-mcp"
)
for server in "${REQUIREMENT_SERVERS[@]}"; do
  echo "[mcp-bench setup] installing Python service requirements: $server"
  uv pip install -r "$SERVERS/$server/requirements.txt"
done

EDITABLE_SERVERS=(
  "mcp-nixos"
  "unit-converter-mcp"
  "medcalc"
  "paper-search-mcp"
  "scientific_computation_mcp"
  "time-mcp"
)
for server in "${EDITABLE_SERVERS[@]}"; do
  echo "[mcp-bench setup] installing Python service package: $server"
  uv pip install -e "$SERVERS/$server"
done

for server in "mcp-reddit" "wikipedia-mcp"; do
  echo "[mcp-bench setup] syncing uv-run service: $server"
  (
    cd "$SERVERS/$server"
    uv sync \
      --frozen \
      --no-dev \
      --python "$EXPERIMENT_PYTHON"
  )
done

# Server-specific requirements are loose and some can otherwise drift to MCP
# SDK 2.x or downgrade aiohttp. Reassert the tested runner constraints last.
echo "[mcp-bench setup] reasserting runner compatibility constraints"
python -m pip install -r "$RUNNER_REQUIREMENTS"

echo "[mcp-bench setup] selected service dependencies are installed"
