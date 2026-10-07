#!/usr/bin/env bash
# Prepare pinned static assets used by the MCPMark utility experiment.

set -euo pipefail
umask 077

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MCPMARK_ROOT="${MCPMARK_ROOT:-$REPO_ROOT/external/mcpmark}"
DEFAULT_ARCHIVE_DIR="$REPO_ROOT/external/mcpmark-service-assets"
ARCHIVE_DIR="${MCPMARK_SERVICE_ASSET_DIR:-${MCPMARK_SERVICE_ASSET_ARCHIVE:-$DEFAULT_ARCHIVE_DIR}}"
DRY_RUN=0
CHECK_ONLY=0

POSTGRES_IMAGE="docker.io/pgvector/pgvector:0.8.0-pg17-bookworm"
POSTGRES_ARCHIVE="pgvector_0.8.0-pg17-bookworm.tar"
LEGACY_GITHUB_ARCHIVE="github-mcp-server_v0.15.0.tar"

ACTIVE_NAMES=(
  "$POSTGRES_ARCHIVE"
)
RECOGNIZED_NAMES=(
  "${ACTIVE_NAMES[@]}"
  "$LEGACY_GITHUB_ARCHIVE"
)

usage() {
  cat <<'EOF'
Usage: prepare_service_assets.sh [OPTIONS]

Prepare the pinned PostgreSQL image and the three-service static state assets:
  pgvector_0.8.0-pg17-bookworm.tar
  10 Filesystem category trees
  5 PostgreSQL template backups

An existing github-mcp-server_v0.15.0.tar and its SHA256SUMS entry are retained
as legacy data, but are neither required, validated, downloaded, nor deleted.

Options:
  --small                   Compatibility no-op; the small set is always used.
  --check-only              Validate existing files; never pull,
                            download, create directories, or update checksums.
  --archive-dir DIR         Shared archive directory. Defaults to
                            external/mcpmark-service-assets.
  --dry-run                Print the frozen plan without changing local state.
  -h, --help               Show this help.

Compatibility aliases:
  --verify-only             Alias for --check-only.

MCPMARK_SERVICE_ASSET_DIR (or the legacy MCPMARK_SERVICE_ASSET_ARCHIVE) may set
the archive directory. MCPMARK_CONTAINER_CLI may be "podman" or an absolute
Docker/Podman path.
EOF
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --small)
      shift
      ;;
    --check-only)
      CHECK_ONLY=1
      shift
      ;;
    --archive-dir)
      if [[ "$#" -lt 2 ]] || [[ -z "$2" ]]; then
        echo "--archive-dir requires a non-empty directory." >&2
        exit 2
      fi
      ARCHIVE_DIR="$2"
      shift 2
      ;;
    --verify-only)
      CHECK_ONLY=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$DRY_RUN" == "1" ]] && [[ "$CHECK_ONLY" == "1" ]]; then
  echo "--dry-run and --check-only are mutually exclusive." >&2
  exit 2
fi
ARCHIVE_DIR="$(readlink -m -- "$ARCHIVE_DIR")"
case "$ARCHIVE_DIR" in
  /|"$REPO_ROOT"|"$SCRIPT_DIR")
    echo "Refusing unsafe archive directory: $ARCHIVE_DIR" >&2
    exit 2
    ;;
esac

echo "MCPMark service asset plan"
echo "  archive directory: $ARCHIVE_DIR"
echo "  image: $POSTGRES_IMAGE -> $POSTGRES_ARCHIVE"
echo "  state: 10 Filesystem categories + 5 PostgreSQL backups"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "Dry run complete; no directories, images, or downloads were changed."
  exit 0
fi

if [[ "$CHECK_ONLY" == "1" ]] && [[ ! -d "$ARCHIVE_DIR" ]]; then
  echo "Service asset directory is missing: $ARCHIVE_DIR" >&2
  exit 1
fi
if [[ "$CHECK_ONLY" != "1" ]]; then
  mkdir -p -- "$ARCHIVE_DIR"
fi
if [[ ! -d "$ARCHIVE_DIR" ]]; then
  echo "Service asset path is not a directory: $ARCHIVE_DIR" >&2
  exit 1
fi
if [[ "$CHECK_ONLY" == "1" ]]; then
  if [[ ! -r "$ARCHIVE_DIR" ]] || [[ ! -x "$ARCHIVE_DIR" ]]; then
    echo "Archive directory is not readable: $ARCHIVE_DIR" >&2
    exit 1
  fi
elif [[ ! -w "$ARCHIVE_DIR" ]]; then
  echo "Archive directory is not writable: $ARCHIVE_DIR" >&2
  exit 1
fi

SHA256_MANIFEST="$ARCHIVE_DIR/SHA256SUMS"

is_recognized_name() {
  local candidate="$1"
  local recognized

  for recognized in "${RECOGNIZED_NAMES[@]}"; do
    if [[ "$candidate" == "$recognized" ]]; then
      return 0
    fi
  done
  return 1
}

assert_regular_or_missing() {
  local path="$1"

  if [[ -L "$path" ]]; then
    echo "Refusing symbolic link at managed asset path: $path" >&2
    exit 1
  fi
  if [[ -e "$path" ]] && [[ ! -f "$path" ]]; then
    echo "Managed asset path is not a regular file: $path" >&2
    exit 1
  fi
}

validate_manifest() {
  local hash
  local filename
  local extra
  local line_count=0
  local unique_count

  assert_regular_or_missing "$SHA256_MANIFEST"
  if [[ ! -f "$SHA256_MANIFEST" ]]; then
    for filename in "${ACTIVE_NAMES[@]}"; do
      if [[ -e "$ARCHIVE_DIR/$filename" ]]; then
        echo "Refusing unmanaged existing archive without SHA256SUMS:" >&2
        echo "  $ARCHIVE_DIR/$filename" >&2
        exit 1
      fi
    done
    return 0
  fi

  while read -r hash filename extra; do
    line_count=$((line_count + 1))
    if [[ ! "$hash" =~ ^[0-9a-f]{64}$ ]] ||
      [[ -z "$filename" ]] ||
      [[ -n "${extra:-}" ]] ||
      ! is_recognized_name "$filename"; then
      echo "Invalid SHA256SUMS entry on line $line_count." >&2
      exit 1
    fi
    if [[ "$filename" != "$LEGACY_GITHUB_ARCHIVE" ]]; then
      assert_regular_or_missing "$ARCHIVE_DIR/$filename"
      if [[ ! -f "$ARCHIVE_DIR/$filename" ]]; then
        echo "SHA256SUMS references a missing archive: $filename" >&2
        exit 1
      fi
    fi
  done < "$SHA256_MANIFEST"
  if [[ "$line_count" -eq 0 ]]; then
    echo "SHA256SUMS is empty." >&2
    exit 1
  fi
  unique_count="$(
    awk '{print $2}' "$SHA256_MANIFEST" | LC_ALL=C sort -u | wc -l
  )"
  if [[ "$unique_count" -ne "$line_count" ]]; then
    echo "SHA256SUMS contains duplicate filenames." >&2
    exit 1
  fi
}

manifest_has_file() {
  local filename="$1"

  [[ -f "$SHA256_MANIFEST" ]] &&
    awk -v filename="$filename" '$2 == filename {found = 1} END {exit !found}' \
      "$SHA256_MANIFEST"
}

record_archive() {
  local partial_path="$1"
  local filename="$2"
  local final_path="$ARCHIVE_DIR/$filename"
  local digest
  local manifest_temp

  if [[ ! -s "$partial_path" ]]; then
    echo "Prepared archive is empty: $partial_path" >&2
    exit 1
  fi
  if ! tar --list --file="$partial_path" >/dev/null; then
    echo "Prepared file is not a readable tar archive: $partial_path" >&2
    exit 1
  fi
  digest="$(sha256sum "$partial_path" | awk '{print $1}')"
  mv -- "$partial_path" "$final_path"

  manifest_temp="$(mktemp "$ARCHIVE_DIR/.SHA256SUMS.XXXXXX")"
  if [[ -f "$SHA256_MANIFEST" ]]; then
    cat "$SHA256_MANIFEST" > "$manifest_temp"
  fi
  printf '%s  %s\n' "$digest" "$filename" >> "$manifest_temp"
  LC_ALL=C sort -k2,2 -o "$manifest_temp" "$manifest_temp"
  mv -- "$manifest_temp" "$SHA256_MANIFEST"
  echo "  recorded sha256=$digest"
}

archive_is_ready() {
  local filename="$1"
  local expected_size="${2:-}"
  local final_path="$ARCHIVE_DIR/$filename"
  local actual_size
  local expected_hash
  local actual_hash

  assert_regular_or_missing "$final_path"
  if [[ ! -e "$final_path" ]]; then
    return 1
  fi
  if ! manifest_has_file "$filename"; then
    echo "Existing archive is not represented in SHA256SUMS:" >&2
    echo "  $final_path" >&2
    exit 1
  fi
  if [[ -n "$expected_size" ]]; then
    actual_size="$(stat -c '%s' "$final_path")"
    if [[ "$actual_size" -ne "$expected_size" ]]; then
      echo "Existing archive has the wrong byte length: $final_path" >&2
      echo "  expected: $expected_size" >&2
      echo "  actual:   $actual_size" >&2
      exit 1
    fi
  fi
  expected_hash="$(
    awk -v filename="$filename" '$2 == filename {print $1}' "$SHA256_MANIFEST"
  )"
  actual_hash="$(sha256sum "$final_path" | awk '{print $1}')"
  if [[ "$actual_hash" != "$expected_hash" ]]; then
    echo "Service archive failed its recorded SHA-256 check: $final_path" >&2
    echo "  expected: $expected_hash" >&2
    echo "  actual:   $actual_hash" >&2
    exit 1
  fi
  if ! tar --list --file="$final_path" >/dev/null; then
    echo "Service archive is not a readable tar file: $final_path" >&2
    exit 1
  fi
  return 0
}

validate_manifest

prepare_state_assets() {
  local state_python="${PYTHON_BOOTSTRAP:-}"
  local arguments=(
    "$SCRIPT_DIR/prepare_state_assets.py"
    --mcpmark-root
    "$MCPMARK_ROOT"
  )

  if [[ -z "$state_python" ]]; then
    if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
      state_python="$SCRIPT_DIR/.venv/bin/python"
    elif command -v python3 >/dev/null 2>&1; then
      state_python="$(command -v python3)"
    else
      echo "Python 3 is required to prepare MCPMark state assets." >&2
      exit 1
    fi
  fi
  if [[ "$CHECK_ONLY" == "1" ]]; then
    arguments+=(--check-only)
  fi
  "$state_python" "${arguments[@]}"
}

prepare_state_assets

if [[ "$CHECK_ONLY" == "1" ]]; then
  for required_name in "${ACTIVE_NAMES[@]}"; do
    if ! archive_is_ready "$required_name"; then
      echo "Required service archive is missing: $ARCHIVE_DIR/$required_name" >&2
      exit 1
    fi
  done
  echo "All requested service archives passed SHA-256 and tar checks."
  exit 0
fi

resolve_container_cli() {
  if [[ -x "$SCRIPT_DIR/bin/docker" ]]; then
    printf '%s\n' "$SCRIPT_DIR/bin/docker"
  else
    return 1
  fi
}

resolve_local_image() {
  local canonical_ref="$1"
  local candidate
  local without_registry
  local basename_ref
  local candidates=("$canonical_ref")

  without_registry="$canonical_ref"
  if [[ "$canonical_ref" == docker.io/* ]]; then
    without_registry="${canonical_ref#docker.io/}"
  fi
  basename_ref="${canonical_ref##*/}"
  candidates+=(
    "localhost/$without_registry"
    "localhost/$basename_ref"
  )

  for candidate in "${candidates[@]}"; do
    if "$CONTAINER_CLI" image inspect "$candidate" >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

prepare_registry_image() {
  local canonical_ref="$1"
  local filename="$2"
  local partial_path="$ARCHIVE_DIR/$filename.part"
  local local_ref

  assert_regular_or_missing "$partial_path"
  if archive_is_ready "$filename"; then
    echo "Archive already verified: $filename"
    return 0
  fi
  if [[ -s "$partial_path" ]] &&
    tar --list --file="$partial_path" >/dev/null 2>&1; then
    echo "Promoting an already complete partial archive: $filename"
    record_archive "$partial_path" "$filename"
    return 0
  fi

  echo "Pulling pinned image: $canonical_ref"
  "$CONTAINER_CLI" pull "$canonical_ref"
  if ! local_ref="$(resolve_local_image "$canonical_ref")"; then
    echo "Pulled image is not visible to $CONTAINER_CLI: $canonical_ref" >&2
    exit 1
  fi
  if [[ "$local_ref" != "$canonical_ref" ]]; then
    echo "Normalizing Podman local reference $local_ref -> $canonical_ref"
    "$CONTAINER_CLI" tag "$local_ref" "$canonical_ref"
  fi

  # Registry pulls resume through the container runtime's layer cache. Image
  # archive serialization itself is restarted into this exact partial file.
  rm -f -- "$partial_path"
  echo "Saving shared archive: $filename"
  "$CONTAINER_CLI" save --output "$partial_path" "$canonical_ref"
  record_archive "$partial_path" "$filename"
}

if ! CONTAINER_CLI="$(resolve_container_cli)"; then
  echo "The experiment Docker-compatible wrapper is missing." >&2
  exit 1
fi
if ! "$CONTAINER_CLI" --version >/dev/null; then
  echo "No supported container CLI was found." >&2
  echo "Set MCPMARK_CONTAINER_CLI=podman or to an absolute executable." >&2
  exit 1
fi
prepare_registry_image "$POSTGRES_IMAGE" "$POSTGRES_ARCHIVE"

echo "Service asset preparation complete."
echo "  SHA-256 manifest: $SHA256_MANIFEST"
