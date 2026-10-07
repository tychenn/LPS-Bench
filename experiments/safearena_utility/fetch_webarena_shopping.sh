#!/usr/bin/env bash
# Fetch the official WebArena shopping image used by SafeArena.

set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
ASSETS_ROOT="${ASSETS_ROOT:-$REPO_ROOT/external/safearena-assets}"
ARCHIVES_DIR="$ASSETS_ROOT/archives"
DESTINATION="$ARCHIVES_DIR/shopping_final_0712.tar"
PARTIAL="$DESTINATION.partial"
EXPECTED_BYTES=67575898112
SOURCE_URL="${SOURCE_URL:-http://metis.lti.cs.cmu.edu/webarena-images/shopping_final_0712.tar}"

mkdir -p "$ARCHIVES_DIR"

available_kib="$(df -Pk "$ARCHIVES_DIR" | awk 'NR == 2 {print $4}')"
required_kib=$(( (EXPECTED_BYTES + 1023) / 1024 ))
if [[ "$available_kib" -lt "$required_kib" ]]; then
  echo "Insufficient free space under $ARCHIVES_DIR" >&2
  exit 1
fi

if [[ -f "$DESTINATION" ]]; then
  actual_bytes="$(stat -c '%s' "$DESTINATION")"
  if [[ "$actual_bytes" -ne "$EXPECTED_BYTES" ]]; then
    echo "Existing file has unexpected size: $actual_bytes bytes" >&2
    exit 1
  fi
else
  echo "Downloading official WebArena shopping image to $PARTIAL"
  echo "The upstream is 67,575,898,112 bytes and supports resumed downloads."
  curl \
    --location \
    --fail \
    --silent \
    --show-error \
    --retry 10 \
    --retry-all-errors \
    --retry-delay 5 \
    --continue-at - \
    --output "$PARTIAL" \
    "$SOURCE_URL"

  actual_bytes="$(stat -c '%s' "$PARTIAL")"
  if [[ "$actual_bytes" -ne "$EXPECTED_BYTES" ]]; then
    echo "Downloaded file has unexpected size: $actual_bytes bytes" >&2
    exit 1
  fi
  mv "$PARTIAL" "$DESTINATION"
fi

sha256sum "$DESTINATION" | tee "$DESTINATION.sha256.local"
echo "The SHA-256 above is locally recorded; WebArena does not publish one."
