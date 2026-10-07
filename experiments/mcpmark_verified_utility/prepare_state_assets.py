#!/usr/bin/env python3
"""Prepare the pinned Filesystem and PostgreSQL MCPMark state assets."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import zipfile


FILESYSTEM_CATEGORIES = (
    "desktop",
    "desktop_template",
    "file_context",
    "file_property",
    "folder_structure",
    "legal_document",
    "papers",
    "student_database",
    "threestudio",
    "votenet",
)
POSTGRES_DATABASES = ("employees", "chinook", "dvdrental", "sports", "lego")
FILESYSTEM_BASE_URL = "https://storage.mcpmark.ai/filesystem"
POSTGRES_BASE_URL = "https://storage.mcpmark.ai/postgres"
FILESYSTEM_HASH_MANIFEST = "SHA256SUMS.local"
POSTGRES_HASH_MANIFEST = "SHA256SUMS.local"
DOWNLOAD_CHUNK_BYTES = 1024 * 1024
MAX_ZIP_MEMBERS = 200_000
MAX_ZIP_UNCOMPRESSED_BYTES = 8 * 1024 * 1024 * 1024


class StateAssetError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(DOWNLOAD_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_zip(path: Path, expected_root: str) -> None:
    """Reject malformed archives before handing them to the system unzip tool.

    Official MCPMark Filesystem archives were created on macOS and contain
    AppleDouble metadata under ``__MACOSX``. Those members are validated for
    path and file-type safety but are deliberately excluded during extraction.
    """
    if not path.is_file() or path.stat().st_size == 0:
        raise StateAssetError(f"missing or empty zip: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if not members or len(members) > MAX_ZIP_MEMBERS:
                raise StateAssetError(
                    f"{path}: unexpected zip member count: {len(members)}"
                )
            total_size = sum(member.file_size for member in members)
            if total_size > MAX_ZIP_UNCOMPRESSED_BYTES:
                raise StateAssetError(
                    f"{path}: uncompressed size exceeds the safety limit"
                )

            seen: set[str] = set()
            expected_members = 0
            for member in members:
                member_path = PurePosixPath(member.filename)
                parts = member_path.parts
                normalized = member_path.as_posix().rstrip("/")
                if (
                    member_path.is_absolute()
                    or not parts
                    or ".." in parts
                    or parts[0] not in {expected_root, "__MACOSX"}
                    or not normalized
                    or normalized in seen
                ):
                    raise StateAssetError(
                        f"{path}: unsafe or unexpected zip member: {member.filename!r}"
                    )
                seen.add(normalized)
                mode = member.external_attr >> 16
                file_type = stat.S_IFMT(mode)
                if stat.S_ISLNK(mode):
                    raise StateAssetError(
                        f"{path}: symbolic links are not accepted: {member.filename!r}"
                    )
                if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise StateAssetError(
                        f"{path}: special files are not accepted: {member.filename!r}"
                    )
                if parts[0] == expected_root:
                    expected_members += 1

            if expected_members == 0:
                raise StateAssetError(
                    f"{path}: archive contains no members under {expected_root!r}"
                )

            bad_member = archive.testzip()
            if bad_member is not None:
                raise StateAssetError(f"{path}: CRC failure in {bad_member!r}")
    except (OSError, zipfile.BadZipFile) as error:
        raise StateAssetError(f"invalid zip {path}: {error}") from error


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url, headers={"User-Agent": "MCPMark-utility-setup/1"}
    )
    try:
        with (
            urllib.request.urlopen(request, timeout=120) as response,
            destination.open("wb") as output,
        ):
            for chunk in iter(lambda: response.read(DOWNLOAD_CHUNK_BYTES), b""):
                output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
    except Exception as error:
        raise StateAssetError(f"download failed for {url}: {error}") from error


def filesystem_tree_digest(root: Path, category: str) -> str:
    """Validate one extracted tree and hash content plus task-relevant mtimes."""
    if root.is_symlink() or not root.is_dir():
        raise StateAssetError(f"Filesystem state is missing: {root}")

    digest = hashlib.sha256()
    regular_files = 0
    try:
        entries = sorted(
            root.rglob("*"),
            key=lambda path: path.relative_to(root).as_posix(),
        )
    except OSError as error:
        raise StateAssetError(f"could not enumerate Filesystem state {root}: {error}")

    for path in entries:
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise StateAssetError(
                f"{category}: symbolic links are not accepted: {relative}"
            )
        try:
            metadata = path.stat()
        except OSError as error:
            raise StateAssetError(f"{category}: could not stat {relative}: {error}")
        if path.is_dir():
            digest.update(b"D\0")
            digest.update(relative.encode("utf-8", errors="surrogateescape"))
            digest.update(b"\0")
            continue
        if not path.is_file():
            raise StateAssetError(
                f"{category}: special files are not accepted: {relative}"
            )

        regular_files += 1
        digest.update(b"F\0")
        digest.update(relative.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")
        digest.update(f"{stat.S_IMODE(metadata.st_mode):o}".encode("ascii"))
        digest.update(b"\0")
        digest.update(str(metadata.st_mtime_ns).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(metadata.st_size).encode("ascii"))
        digest.update(b"\0")
        try:
            with path.open("rb") as handle:
                for chunk in iter(
                    lambda: handle.read(DOWNLOAD_CHUNK_BYTES),
                    b"",
                ):
                    digest.update(chunk)
        except OSError as error:
            raise StateAssetError(f"{category}: could not read {relative}: {error}")
        digest.update(b"\0")

    if regular_files == 0:
        raise StateAssetError(f"Filesystem state has no regular files: {root}")
    return digest.hexdigest()


def read_hashes(
    path: Path,
    *,
    allowed_names: set[str],
    label: str,
) -> dict[str, str]:
    if not path.exists():
        return {}
    if path.is_symlink() or not path.is_file():
        raise StateAssetError(f"unsafe {label} checksum manifest: {path}")
    hashes: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise StateAssetError(f"could not read {label} checksum manifest: {error}")
    for line_number, line in enumerate(lines, 1):
        fields = line.split()
        if (
            len(fields) != 2
            or len(fields[0]) != 64
            or any(character not in "0123456789abcdef" for character in fields[0])
            or fields[1] not in allowed_names
            or fields[1] in hashes
        ):
            raise StateAssetError(
                f"invalid {label} checksum entry on line {line_number}"
            )
        hashes[fields[1]] = fields[0]
    return hashes


def write_hashes(root: Path, filename: str, hashes: dict[str, str]) -> None:
    manifest = root / filename
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{filename}.",
        dir=root,
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            for asset_name in sorted(hashes):
                output.write(f"{hashes[asset_name]}  {asset_name}\n")
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(manifest)
    finally:
        temporary.unlink(missing_ok=True)


def extract_zip(path: Path, destination: Path, expected_root: str) -> None:
    """Extract only the validated task tree, excluding macOS metadata."""
    unzip = shutil.which("unzip")
    if unzip is None:
        raise StateAssetError("unzip is required to prepare Filesystem state assets")
    try:
        completed = subprocess.run(
            [
                unzip,
                "-q",
                "-o",
                str(path),
                f"{expected_root}/*",
                "-d",
                str(destination),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise StateAssetError(f"could not extract {path}: {error}") from error
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise StateAssetError(f"could not extract {path}: {detail}")


def prepare_filesystem_states(
    filesystem_root: Path,
    *,
    check_only: bool,
) -> None:
    if check_only and not filesystem_root.is_dir():
        raise StateAssetError(
            f"Filesystem state directory is missing: {filesystem_root}"
        )
    if not check_only:
        filesystem_root.mkdir(parents=True, exist_ok=True)

    manifest_path = filesystem_root / FILESYSTEM_HASH_MANIFEST
    recorded = read_hashes(
        manifest_path,
        allowed_names=set(FILESYSTEM_CATEGORIES),
        label="Filesystem",
    )
    observed: dict[str, str] = {}

    for category in FILESYSTEM_CATEGORIES:
        target = filesystem_root / category
        if not target.exists():
            if check_only:
                raise StateAssetError(f"Filesystem state is missing: {target}")
            part = filesystem_root / f".{category}.zip.part"
            if part.is_symlink() or (part.exists() and not part.is_file()):
                raise StateAssetError(f"unsafe partial download path: {part}")
            try:
                validate_zip(part, category)
                print(f"Using complete partial Filesystem download: {part.name}")
            except StateAssetError:
                print(f"Downloading Filesystem state: {category}")
                download(f"{FILESYSTEM_BASE_URL}/{category}.zip", part)
                validate_zip(part, category)

            extraction_root = Path(
                tempfile.mkdtemp(
                    prefix=f".extract-{category}-",
                    dir=filesystem_root,
                )
            )
            try:
                extract_zip(part, extraction_root, category)
                extracted = extraction_root / category
                filesystem_tree_digest(extracted, category)
                if target.exists():
                    raise StateAssetError(
                        f"refusing to replace state created concurrently: {target}"
                    )
                extracted.rename(target)
            finally:
                shutil.rmtree(extraction_root, ignore_errors=True)
            part.unlink()

        digest = filesystem_tree_digest(target, category)
        expected = recorded.get(category)
        if expected is not None and digest != expected:
            raise StateAssetError(
                f"Filesystem state checksum mismatch for {category}: "
                f"expected {expected}, got {digest}"
            )
        observed[category] = digest
        print(f"Filesystem state verified: {category}")

    if check_only and observed != recorded:
        raise StateAssetError(
            f"Filesystem checksum manifest is missing or incomplete: {manifest_path}; "
            "run prepare_service_assets.sh once without --check-only"
        )
    if not check_only and observed != recorded:
        write_hashes(filesystem_root, FILESYSTEM_HASH_MANIFEST, observed)
        print(f"Filesystem checksum manifest updated: {FILESYSTEM_HASH_MANIFEST}")


def resolve_pg_restore() -> str:
    configured = os.getenv("MCPMARK_PG_RESTORE")
    candidates = []
    if configured:
        candidates.append(configured)
    experiment_dir = Path(__file__).resolve().parent
    candidates.append(str(experiment_dir / ".postgres-client" / "bin" / "pg_restore"))
    path_candidate = shutil.which("pg_restore")
    if path_candidate:
        candidates.append(path_candidate)
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    raise StateAssetError(
        "PG17 pg_restore is unavailable; run setup_environment.sh first"
    )


def validate_postgres_backup(path: Path, pg_restore: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise StateAssetError(f"PostgreSQL backup is missing or empty: {path}")
    try:
        completed = subprocess.run(
            [pg_restore, "--list", str(path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise StateAssetError(f"could not inspect {path}: {error}") from error
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        suffix = f": {detail[-1]}" if detail else ""
        raise StateAssetError(f"invalid PostgreSQL archive {path}{suffix}")


def prepare_postgres_backups(
    postgres_root: Path,
    *,
    check_only: bool,
) -> None:
    if check_only and not postgres_root.is_dir():
        raise StateAssetError(f"PostgreSQL state directory is missing: {postgres_root}")
    if not check_only:
        postgres_root.mkdir(parents=True, exist_ok=True)
    pg_restore = resolve_pg_restore()
    manifest_path = postgres_root / POSTGRES_HASH_MANIFEST
    backup_names = {f"{name}.backup" for name in POSTGRES_DATABASES}
    recorded = read_hashes(
        manifest_path,
        allowed_names=backup_names,
        label="PostgreSQL",
    )
    observed: dict[str, str] = {}

    for database in POSTGRES_DATABASES:
        filename = f"{database}.backup"
        target = postgres_root / filename
        part = postgres_root / f".{filename}.part"
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise StateAssetError(f"unsafe PostgreSQL state path: {target}")
        if not target.exists():
            if check_only:
                raise StateAssetError(f"PostgreSQL backup is missing: {target}")
            if part.is_symlink() or (part.exists() and not part.is_file()):
                raise StateAssetError(f"unsafe partial download path: {part}")
            try:
                validate_postgres_backup(part, pg_restore)
                print(f"Using complete partial PostgreSQL download: {part.name}")
            except StateAssetError:
                print(f"Downloading PostgreSQL state: {database}")
                download(f"{POSTGRES_BASE_URL}/{filename}", part)
                validate_postgres_backup(part, pg_restore)
            if target.exists():
                raise StateAssetError(
                    f"refusing to replace state created concurrently: {target}"
                )
            part.rename(target)

        validate_postgres_backup(target, pg_restore)
        digest = sha256_file(target)
        expected = recorded.get(filename)
        if expected is not None and digest != expected:
            raise StateAssetError(
                f"PostgreSQL backup checksum mismatch for {filename}: "
                f"expected {expected}, got {digest}"
            )
        observed[filename] = digest
        print(f"PostgreSQL state verified: {filename}")

    if check_only and observed != recorded:
        raise StateAssetError(
            f"PostgreSQL checksum manifest is missing or incomplete: {manifest_path}; "
            "run prepare_service_assets.sh once without --check-only"
        )
    if not check_only and observed != recorded:
        write_hashes(postgres_root, POSTGRES_HASH_MANIFEST, observed)
        print(f"PostgreSQL checksum manifest updated: {POSTGRES_HASH_MANIFEST}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcpmark-root", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    mcpmark_root = arguments.mcpmark_root.resolve()
    if not mcpmark_root.is_dir():
        raise StateAssetError(f"MCPMark root is missing: {mcpmark_root}")

    prepare_filesystem_states(
        mcpmark_root / "test_environments",
        check_only=arguments.check_only,
    )
    prepare_postgres_backups(
        mcpmark_root / "postgres_state",
        check_only=arguments.check_only,
    )
    print("All 15 MCPMark state assets are ready.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StateAssetError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
