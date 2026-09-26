#!/usr/bin/env bash
# Create the experiment virtual environment and install the pinned MCPMark clone.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MCPMARK_ROOT="${MCPMARK_ROOT:-$REPO_ROOT/external/mcpmark}"
MCPMARK_VENV="${MCPMARK_VENV:-$SCRIPT_DIR/.venv}"
POSTGRES_CLIENT_PREFIX="${MCPMARK_POSTGRES_CLIENT_PREFIX:-$SCRIPT_DIR/.postgres-client}"
PLAYWRIGHT_NODE_PREFIX="${MCPMARK_PLAYWRIGHT_NODE_PREFIX:-$SCRIPT_DIR/.node-runtime}"
PLAYWRIGHT_NODE_BROWSERS_PATH="${MCPMARK_PLAYWRIGHT_NODE_BROWSERS_PATH:-$PLAYWRIGHT_NODE_PREFIX/browsers}"
PLAYWRIGHT_MCP_PACKAGE="@playwright/mcp@0.0.68"
PLAYWRIGHT_MCP_VERSION="0.0.68"
PLAYWRIGHT_NODE_VERSION="1.59.0-alpha-1771104257000"
FILESYSTEM_MCP_PACKAGE="@modelcontextprotocol/server-filesystem@2025.12.18"
FILESYSTEM_MCP_VERSION="2025.12.18"
PYTHON_BOOTSTRAP="${PYTHON_BOOTSTRAP:-python3}"
CHECK_ONLY=0
POSTGRES_CLIENT_SOURCE=""

if [[ "$#" -gt 1 ]]; then
  echo "Usage: $0 [--check-only]" >&2
  exit 2
fi
if [[ "$#" -eq 1 ]]; then
  if [[ "$1" != "--check-only" ]]; then
    echo "Unknown option: $1" >&2
    echo "Usage: $0 [--check-only]" >&2
    exit 2
  fi
  CHECK_ONLY=1
fi

EXPECTED_COMMIT="$(
  "$PYTHON_BOOTSTRAP" - "$SCRIPT_DIR/task_manifest.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    print(json.load(handle)["source_commit"])
PY
)"

if [[ ! -d "$MCPMARK_ROOT/.git" ]]; then
  echo "Pinned MCPMark clone is missing: $MCPMARK_ROOT" >&2
  echo "Clone https://github.com/eval-sys/mcpmark.git at $EXPECTED_COMMIT first." >&2
  exit 1
fi

ACTUAL_COMMIT="$(git -C "$MCPMARK_ROOT" rev-parse HEAD)"
if [[ "$ACTUAL_COMMIT" != "$EXPECTED_COMMIT" ]]; then
  echo "MCPMark commit mismatch." >&2
  echo "  expected: $EXPECTED_COMMIT" >&2
  echo "  actual:   $ACTUAL_COMMIT" >&2
  exit 1
fi

postgres_client_major() {
  local executable="$1"
  local version_output

  if ! version_output="$("$executable" --version 2>&1)"; then
    return 1
  fi
  if [[ "$version_output" =~ ([0-9]+)(\.[0-9]+)* ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}

postgres_client_dir_ready() {
  local candidate_dir="$1"
  local executable
  local major

  for executable in psql pg_restore; do
    if [[ ! -x "$candidate_dir/$executable" ]]; then
      return 1
    fi
    if ! major="$(postgres_client_major "$candidate_dir/$executable")"; then
      return 1
    fi
    if [[ "$major" != "17" ]]; then
      return 1
    fi
  done
}

system_postgres_client_ready() {
  local executable
  local executable_path
  local major

  for executable in psql pg_restore; do
    if ! executable_path="$(command -v "$executable")"; then
      return 1
    fi
    if ! major="$(postgres_client_major "$executable_path")"; then
      return 1
    fi
    if [[ "$major" != "17" ]]; then
      return 1
    fi
  done
}

resolve_conda() {
  local candidate="${MCPMARK_CONDA:-${CONDA_EXE:-}}"

  if [[ -n "$candidate" ]] && [[ -x "$candidate" ]]; then
    readlink -f -- "$candidate"
  elif command -v conda >/dev/null 2>&1; then
    command -v conda
  else
    return 1
  fi
}

prepare_postgres_client() {
  local conda_bin

  if postgres_client_dir_ready "$POSTGRES_CLIENT_PREFIX/bin"; then
    POSTGRES_CLIENT_SOURCE="$POSTGRES_CLIENT_PREFIX/bin"
    return 0
  fi
  if system_postgres_client_ready; then
    POSTGRES_CLIENT_SOURCE="system PATH"
    return 0
  fi
  if [[ "$CHECK_ONLY" == "1" ]]; then
    echo "PostgreSQL 17 psql/pg_restore are unavailable." >&2
    echo "Checked the local prefix and the current system PATH:" >&2
    echo "  local prefix: $POSTGRES_CLIENT_PREFIX/bin" >&2
    echo "Run $0 once without --check-only to install it with Conda." >&2
    return 1
  fi
  if ! conda_bin="$(resolve_conda)"; then
    echo "Conda is required to install the local PostgreSQL 17 client." >&2
    echo "Set MCPMARK_CONDA to an absolute Conda executable if needed." >&2
    echo "No sudo or system PostgreSQL installation is needed." >&2
    return 1
  fi
  if [[ -e "$POSTGRES_CLIENT_PREFIX" ]] &&
    [[ ! -d "$POSTGRES_CLIENT_PREFIX" ]]; then
    echo "PostgreSQL client prefix is not a directory:" >&2
    echo "  $POSTGRES_CLIENT_PREFIX" >&2
    return 1
  fi
  if [[ -d "$POSTGRES_CLIENT_PREFIX" ]] &&
    [[ ! -d "$POSTGRES_CLIENT_PREFIX/conda-meta" ]] &&
    [[ -n "$(find "$POSTGRES_CLIENT_PREFIX" -mindepth 1 -print -quit)" ]]; then
    echo "Refusing to replace a non-Conda directory:" >&2
    echo "  $POSTGRES_CLIENT_PREFIX" >&2
    return 1
  fi

  echo "Installing PostgreSQL 17 client into: $POSTGRES_CLIENT_PREFIX"
  if [[ -d "$POSTGRES_CLIENT_PREFIX/conda-meta" ]]; then
    "$conda_bin" install \
      --yes \
      --prefix "$POSTGRES_CLIENT_PREFIX" \
      --override-channels \
      --channel conda-forge \
      --strict-channel-priority \
      "postgresql=17.7"
  else
    "$conda_bin" create \
      --yes \
      --prefix "$POSTGRES_CLIENT_PREFIX" \
      --override-channels \
      --channel conda-forge \
      --strict-channel-priority \
      "postgresql=17.7"
  fi

  if ! postgres_client_dir_ready "$POSTGRES_CLIENT_PREFIX/bin"; then
    echo "Conda completed, but the local PostgreSQL 17 client is invalid." >&2
    return 1
  fi
  POSTGRES_CLIENT_SOURCE="$POSTGRES_CLIENT_PREFIX/bin"
}

check_node_playwright() {
  local mode="$1"

  if [[ ! -x "$PLAYWRIGHT_NODE_PREFIX/node_modules/.bin/playwright-mcp" ]] ||
    [[ ! -x "$PLAYWRIGHT_NODE_PREFIX/node_modules/.bin/playwright" ]] ||
    [[ ! -x "$PLAYWRIGHT_NODE_PREFIX/node_modules/.bin/mcp-server-filesystem" ]]; then
    echo "Pinned Node MCP runtime is missing:" >&2
    echo "  $PLAYWRIGHT_NODE_PREFIX" >&2
    return 1
  fi
  PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_NODE_BROWSERS_PATH" node - \
    "$PLAYWRIGHT_NODE_PREFIX" \
    "$PLAYWRIGHT_MCP_VERSION" \
    "$PLAYWRIGHT_NODE_VERSION" \
    "$FILESYSTEM_MCP_VERSION" \
    "$mode" <<'JS'
const fs = require("fs");
const path = require("path");

const [
  prefix,
  expectedMcp,
  expectedPlaywright,
  expectedFilesystem,
  mode,
] = process.argv.slice(2);
const modules = path.join(prefix, "node_modules");
const mcpPackage = require(path.join(modules, "@playwright/mcp/package.json"));
const filesystemPackage = require(
  path.join(modules, "@modelcontextprotocol/server-filesystem/package.json")
);
const playwrightPackage = require(path.join(modules, "playwright/package.json"));
const playwrightCorePackage = require(
  path.join(modules, "playwright-core/package.json")
);
if (mcpPackage.version !== expectedMcp)
  throw new Error(`Playwright MCP version ${mcpPackage.version} != ${expectedMcp}`);
if (filesystemPackage.version !== expectedFilesystem)
  throw new Error(
    `Filesystem MCP version ${filesystemPackage.version} != ${expectedFilesystem}`
  );
if (playwrightPackage.version !== expectedPlaywright)
  throw new Error(
    `Node Playwright version ${playwrightPackage.version} != ${expectedPlaywright}`
  );
if (playwrightCorePackage.version !== expectedPlaywright)
  throw new Error(
    `Node Playwright Core version ${playwrightCorePackage.version} != ${expectedPlaywright}`
  );
if (mcpPackage.dependencies.playwright !== expectedPlaywright)
  throw new Error("Playwright MCP no longer pins the frozen Node Playwright version");
if (mcpPackage.dependencies["playwright-core"] !== expectedPlaywright)
  throw new Error(
    "Playwright MCP no longer pins the frozen Node Playwright Core version"
  );

const { chromium } = require(path.join(modules, "playwright"));
const executable = chromium.executablePath();
if (mode === "launch") {
  if (!fs.existsSync(executable))
    throw new Error(`Node Chromium executable is missing: ${executable}`);
  (async () => {
    const browser = await chromium.launch({
      headless: true,
      args: ["--no-sandbox"],
    });
    await browser.close();
    console.log(`Node Chromium launch passed: ${executable}`);
  })().catch(error => {
    console.error(error);
    process.exit(1);
  });
} else {
  console.log(`Pinned Node Playwright package passed: ${playwrightPackage.version}`);
}
JS
}

ensure_node_playwright_package() {
  local effective_npm_proxy
  local npm_environment=(env PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1)

  if check_node_playwright package >/dev/null 2>&1; then
    echo "Pinned Node Filesystem and Playwright MCP packages are already installed."
    return 0
  fi
  effective_npm_proxy="${MCPMARK_NPM_PROXY:-${HTTPS_PROXY:-}}"
  if [[ -n "$effective_npm_proxy" ]]; then
    npm_environment+=(
      "npm_config_proxy=$effective_npm_proxy"
      "npm_config_https_proxy=$effective_npm_proxy"
    )
  fi
  echo "Installing pinned Node Filesystem and Playwright MCP into: $PLAYWRIGHT_NODE_PREFIX"
  "${npm_environment[@]}" npm install \
    --prefix "$PLAYWRIGHT_NODE_PREFIX" \
    --no-save \
    --package-lock=false \
    --ignore-scripts \
    --no-audit \
    --no-fund \
    "$FILESYSTEM_MCP_PACKAGE" \
    "$PLAYWRIGHT_MCP_PACKAGE"
  check_node_playwright package
}

install_node_playwright_browser() {
  local effective_download_proxy
  local download_environment=(
    env
    "PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_NODE_BROWSERS_PATH"
    "PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT=${MCPMARK_PLAYWRIGHT_DOWNLOAD_TIMEOUT_MS:-120000}"
  )

  effective_download_proxy="${MCPMARK_NPM_PROXY:-${HTTPS_PROXY:-}}"
  if [[ -n "$effective_download_proxy" ]]; then
    download_environment+=(
      "HTTPS_PROXY=$effective_download_proxy"
      "HTTP_PROXY=$effective_download_proxy"
    )
  fi
  echo "Installing Chromium for the pinned Node Playwright runtime."
  "${download_environment[@]}" \
    "$PLAYWRIGHT_NODE_PREFIX/node_modules/.bin/playwright" install chromium
}

if [[ "$CHECK_ONLY" == "1" ]]; then
  if [[ ! -x "$MCPMARK_VENV/bin/python" ]]; then
    echo "Experiment venv is missing: $MCPMARK_VENV" >&2
    exit 1
  fi
  "$MCPMARK_VENV/bin/python" -c \
    'import litellm, mcp, openai, playwright, psycopg2, src'
else
  if [[ ! -x "$MCPMARK_VENV/bin/python" ]]; then
    "$PYTHON_BOOTSTRAP" -m venv "$MCPMARK_VENV"
  fi
  "$MCPMARK_VENV/bin/python" -m pip install --upgrade pip setuptools wheel
  "$MCPMARK_VENV/bin/python" -m pip install --editable "$MCPMARK_ROOT"
fi

prepare_postgres_client

if [[ "$POSTGRES_CLIENT_SOURCE" == "$POSTGRES_CLIENT_PREFIX/bin" ]]; then
  export PATH="$POSTGRES_CLIENT_PREFIX/bin:$MCPMARK_VENV/bin:$SCRIPT_DIR/bin:$PATH"
else
  export PATH="$MCPMARK_VENV/bin:$SCRIPT_DIR/bin:$PATH"
fi

missing_executables=()
for executable in node npm npx ollama curl wget unzip pipx psql pg_restore; do
  if ! command -v "$executable" >/dev/null 2>&1; then
    missing_executables+=("$executable")
  fi
done
setup_failed=0
if [[ "${#missing_executables[@]}" -gt 0 ]]; then
  echo "Required executables are unavailable:" >&2
  printf '  - %s\n' "${missing_executables[@]}" >&2
  setup_failed=1
fi

if ! docker --version; then
  echo "A working Docker-compatible container CLI is required." >&2
  setup_failed=1
fi

if [[ "$CHECK_ONLY" == "0" ]] &&
  [[ "${MCPMARK_SKIP_MCP_SERVER_PREFETCH:-0}" != "1" ]]; then
  MCPMARK_REAL_PIPX="$MCPMARK_VENV/bin/pipx" \
    "$SCRIPT_DIR/bin/pipx" run "postgres-mcp==0.3.0" --help >/dev/null
elif [[ "$CHECK_ONLY" == "0" ]]; then
  echo "Skipping MCP server prefetch (MCPMARK_SKIP_MCP_SERVER_PREFETCH=1)."
fi

if [[ "$CHECK_ONLY" == "0" ]]; then
  ensure_node_playwright_package
fi

if [[ "$CHECK_ONLY" == "0" ]] &&
  [[ "${MCPMARK_SKIP_PLAYWRIGHT_INSTALL:-0}" != "1" ]]; then
  install_node_playwright_browser
  "$MCPMARK_VENV/bin/playwright" install chromium
elif [[ "$CHECK_ONLY" == "0" ]]; then
  echo "Skipping Chromium installation (MCPMARK_SKIP_PLAYWRIGHT_INSTALL=1)."
fi

if ! "$MCPMARK_VENV/bin/python" - <<'PY'
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    executable = Path(playwright.chromium.executable_path)
    if not executable.is_file():
        raise SystemExit(f"Chromium executable is missing: {executable}")
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    browser.close()
    print(f"Chromium launch passed: {executable}")
PY
then
  setup_failed=1
fi

if ! check_node_playwright launch; then
  setup_failed=1
fi

if [[ "$setup_failed" -ne 0 ]]; then
  echo "MCPMark environment is not ready; resolve the items above." >&2
  exit 1
fi

echo "MCPMark environment is ready."
echo "  repository: $MCPMARK_ROOT"
echo "  commit:     $ACTUAL_COMMIT"
echo "  venv:       $MCPMARK_VENV"
echo "  pg client:  $POSTGRES_CLIENT_SOURCE"
echo "  node MCP:   $PLAYWRIGHT_NODE_PREFIX"
echo "  node browser: $PLAYWRIGHT_NODE_BROWSERS_PATH"
echo "Activate the Python and PostgreSQL tools with:"
echo "  source \"$MCPMARK_VENV/bin/activate\""
if [[ "$POSTGRES_CLIENT_SOURCE" == "$POSTGRES_CLIENT_PREFIX/bin" ]]; then
  printf '  export PATH="%s/bin:$PATH"\n' "$POSTGRES_CLIENT_PREFIX"
fi
