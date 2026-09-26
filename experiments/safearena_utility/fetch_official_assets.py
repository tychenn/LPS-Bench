#!/usr/bin/env python3
"""Download and verify the gated official SafeArena assets.

This intentionally does not fetch the separate WebArena shopping image.  It
only handles artifacts published by the two McGill-NLP SafeArena datasets.
Authentication is read through huggingface_hub's normal credential mechanism;
tokens are never printed or stored in experiment metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download, snapshot_download
from huggingface_hub.errors import HfHubHTTPError


# The environment-only repository named in the pinned SafeArena README now
# redirects to this canonical gated dataset, which contains both task JSON and
# environment archives. Resolve and pin one revision before downloading either.
TASK_REPO = "McGill-NLP/safearena"
ENV_REPO = TASK_REPO
ENV_ALLOW_PATTERNS = (
    "safearena_shopping_admin.tar.gz",
    "safearena_forum.tar.gz.*",
    "safearena_gitlab.tar.gz.*",
)
ENV_SHA256 = {
    "safearena_shopping_admin.tar.gz": (
        "82d136ad1a6d0db9e4a398ca9f38d9956cfbfb076d9ff84dddd32e0227628822"
    ),
    "safearena_forum.tar.gz": (
        "186490daed7f66512d9a7f5dd088c78d8dfc0f2c4890a6681d4424440372d321"
    ),
    "safearena_gitlab.tar.gz": (
        "26b773ff60ec4663c75dc9c0d8630b28da58c1e527d4b92a8fa6fe3a089256c8"
    ),
}


def sha256_file(path: Path, chunk_size: int = 16 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def find_unique(root: Path, filename: str) -> Path:
    matches = [path for path in root.rglob(filename) if path.is_file()]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one {filename!r} under {root}, found {len(matches)}"
        )
    return matches[0]


def copy_atomically(source: Path, destination: Path) -> None:
    temporary = destination.with_name(destination.name + ".partial")
    temporary.unlink(missing_ok=True)
    with source.open("rb") as input_file, temporary.open("wb") as output_file:
        shutil.copyfileobj(input_file, output_file, length=16 * 1024 * 1024)
    temporary.replace(destination)


def join_parts_atomically(parts: list[Path], destination: Path) -> None:
    if not parts:
        raise RuntimeError(f"No split archive parts found for {destination.name}")
    temporary = destination.with_name(destination.name + ".partial")
    temporary.unlink(missing_ok=True)
    with temporary.open("wb") as output_file:
        for part in parts:
            with part.open("rb") as input_file:
                shutil.copyfileobj(input_file, output_file, length=16 * 1024 * 1024)
    temporary.replace(destination)


def verify_archive(path: Path) -> dict[str, object]:
    expected = ENV_SHA256[path.name]
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(
            f"SHA-256 mismatch for {path}: expected {expected}, got {actual}"
        )
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": actual,
    }


def require_huggingface_access(include_environments: bool) -> dict[str, str]:
    api = HfApi()
    try:
        account = api.whoami()
        task_info = api.dataset_info(TASK_REPO)
        revisions = {"tasks": task_info.sha}
        if include_environments:
            revisions["environments"] = task_info.sha
    except HfHubHTTPError as error:
        message = (
            "Hugging Face authentication/access failed. Accept the terms for "
            f"https://huggingface.co/datasets/{TASK_REPO}"
        )
        message += ", then run `hf auth login` on the management node."
        raise RuntimeError(message) from error
    revisions["account"] = str(account.get("name", "authenticated"))
    return revisions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("external/safearena/data"),
    )
    parser.add_argument(
        "--assets-root",
        type=Path,
        default=Path("external/safearena-assets"),
    )
    parser.add_argument(
        "--include-environments",
        action="store_true",
        help="Also download and assemble the three large SafeArena Docker archives.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = (repo_root / args.data_dir).resolve()
    assets_root = (repo_root / args.assets_root).resolve()
    archives_dir = assets_root / "archives"
    downloads_dir = assets_root / "downloads"

    revisions = require_huggingface_access(args.include_environments)
    data_dir.mkdir(parents=True, exist_ok=True)
    task_files: dict[str, dict[str, object]] = {}
    for filename in ("safe.json", "harm.json"):
        downloaded = Path(
            hf_hub_download(
                repo_id=TASK_REPO,
                repo_type="dataset",
                revision=revisions["tasks"],
                filename=filename,
                local_dir=data_dir,
            )
        )
        task_files[filename] = {
            "path": str(downloaded.resolve()),
            "bytes": downloaded.stat().st_size,
            "sha256": sha256_file(downloaded),
        }

    archives: dict[str, dict[str, object]] = {}
    if args.include_environments:
        archives_dir.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=ENV_REPO,
            repo_type="dataset",
            revision=revisions["environments"],
            local_dir=downloads_dir,
            allow_patterns=list(ENV_ALLOW_PATTERNS),
        )

        admin_destination = archives_dir / "safearena_shopping_admin.tar.gz"
        if not admin_destination.exists():
            copy_atomically(
                find_unique(downloads_dir, admin_destination.name),
                admin_destination,
            )

        for stem in ("safearena_forum.tar.gz", "safearena_gitlab.tar.gz"):
            destination = archives_dir / stem
            if not destination.exists():
                parts = sorted(
                    path
                    for path in downloads_dir.rglob(stem + ".*")
                    if path.is_file() and not path.name.endswith(".metadata")
                )
                join_parts_atomically(parts, destination)

        for filename in ENV_SHA256:
            archives[filename] = verify_archive(archives_dir / filename)

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "repositories": {
            TASK_REPO: revisions["tasks"],
        },
        "task_files": task_files,
        "environment_archives": archives,
        "note": (
            "The separate official WebArena shopping_final_0712.tar is not "
            "published in either SafeArena dataset and is not downloaded here."
        ),
    }
    metadata_path = assets_root / "official_assets.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
