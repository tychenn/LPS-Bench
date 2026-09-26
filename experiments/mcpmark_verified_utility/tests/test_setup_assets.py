import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
import zipfile


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
ASSET_SCRIPT = EXPERIMENT_DIR / "prepare_service_assets.sh"
STATE_SCRIPT = EXPERIMENT_DIR / "prepare_state_assets.py"
SETUP_SCRIPT = EXPERIMENT_DIR / "setup_environment.sh"
ENV_EXAMPLE = EXPERIMENT_DIR / "mcp_env.example"
EXPECTED_COMMIT = "cd45b7f57923b9b3985467f5139927575f83141c"
POSTGRES_ARCHIVE = "pgvector_0.8.0-pg17-bookworm.tar"
LEGACY_GITHUB_ARCHIVE = "github-mcp-server_v0.15.0.tar"
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


def load_state_module():
    spec = importlib.util.spec_from_file_location(
        "mcpmark_utility_prepare_state_assets",
        STATE_SCRIPT,
    )
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {STATE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_fake_state(root: Path) -> dict[str, str]:
    filesystem_root = root / "test_environments"
    postgres_root = root / "postgres_state"
    for category in FILESYSTEM_CATEGORIES:
        category_root = filesystem_root / category
        category_root.mkdir(parents=True)
        (category_root / "fixture.txt").write_text(category, encoding="utf-8")
    postgres_root.mkdir()
    for database in POSTGRES_DATABASES:
        (postgres_root / f"{database}.backup").write_bytes(
            f"fixture:{database}".encode()
        )

    environment = os.environ.copy()
    environment.update(
        {
            "MCPMARK_PG_RESTORE": "/bin/true",
            "PYTHON_BOOTSTRAP": sys.executable,
        }
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(STATE_SCRIPT),
            "--mcpmark-root",
            str(root),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return environment


def run_asset(*arguments: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary:
        state_root = Path(temporary) / "mcpmark"
        state_root.mkdir()
        environment = prepare_fake_state(state_root)
        environment["MCPMARK_ROOT"] = str(state_root)
        return subprocess.run(
            ["bash", str(ASSET_SCRIPT), *arguments],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )


def write_tar(path: Path, payload_text: str) -> None:
    payload = path.with_suffix(".txt")
    payload.write_text(payload_text, encoding="utf-8")
    with tarfile.open(path, "w") as handle:
        handle.add(payload, arcname="payload.txt")
    payload.unlink()


def write_executable(path: Path, body: str) -> None:
    path.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\n{body}", encoding="utf-8")
    path.chmod(0o755)


class ServiceAssetScriptTests(unittest.TestCase):
    def test_default_and_small_alias_have_the_same_dry_run_plan(self) -> None:
        default = run_asset("--dry-run")
        small = run_asset("--small", "--dry-run")

        self.assertEqual(default.returncode, 0, default.stderr)
        self.assertEqual(small.returncode, 0, small.stderr)
        self.assertNotIn(LEGACY_GITHUB_ARCHIVE, small.stdout)
        self.assertIn(POSTGRES_ARCHIVE, small.stdout)
        self.assertIn("10 Filesystem categories + 5 PostgreSQL backups", small.stdout)
        self.assertEqual(default.stdout, small.stdout)

    def test_retired_asset_group_flag_is_rejected(self) -> None:
        completed = run_asset("--all", "--dry-run")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("Unknown option", completed.stderr)

    def test_check_only_does_not_create_a_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            asset_dir = Path(temporary) / "does-not-exist"
            completed = run_asset(
                "--small",
                "--check-only",
                "--archive-dir",
                str(asset_dir),
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("directory is missing", completed.stderr)
            self.assertFalse(asset_dir.exists())

    def test_check_only_validates_hashes_and_readable_tar_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            asset_dir = Path(temporary) / "assets"
            asset_dir.mkdir()
            archive = asset_dir / POSTGRES_ARCHIVE
            write_tar(archive, POSTGRES_ARCHIVE)
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            (asset_dir / "SHA256SUMS").write_text(
                f"{digest}  {POSTGRES_ARCHIVE}\n",
                encoding="utf-8",
            )

            completed = run_asset(
                "--small",
                "--check-only",
                "--archive-dir",
                str(asset_dir),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("SHA-256 and tar checks", completed.stdout)

    def test_check_only_tolerates_and_preserves_legacy_github_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            asset_dir = Path(temporary) / "assets"
            asset_dir.mkdir()
            postgres = asset_dir / POSTGRES_ARCHIVE
            write_tar(postgres, POSTGRES_ARCHIVE)
            legacy = asset_dir / LEGACY_GITHUB_ARCHIVE
            legacy.write_bytes(b"legacy archive is intentionally opaque")
            manifest_text = "".join(
                sorted(
                    (
                        f"{hashlib.sha256(postgres.read_bytes()).hexdigest()}  "
                        f"{POSTGRES_ARCHIVE}\n",
                        f"{hashlib.sha256(legacy.read_bytes()).hexdigest()}  "
                        f"{LEGACY_GITHUB_ARCHIVE}\n",
                    )
                )
            )
            manifest = asset_dir / "SHA256SUMS"
            manifest.write_text(manifest_text, encoding="utf-8")

            completed = run_asset(
                "--check-only",
                "--archive-dir",
                str(asset_dir),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                legacy.read_bytes(), b"legacy archive is intentionally opaque"
            )
            self.assertEqual(manifest.read_text(encoding="utf-8"), manifest_text)

    def test_check_only_does_not_require_missing_legacy_github_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            asset_dir = Path(temporary) / "assets"
            asset_dir.mkdir()
            postgres = asset_dir / POSTGRES_ARCHIVE
            write_tar(postgres, POSTGRES_ARCHIVE)
            postgres_digest = hashlib.sha256(postgres.read_bytes()).hexdigest()
            legacy_digest = hashlib.sha256(b"no longer present").hexdigest()
            (asset_dir / "SHA256SUMS").write_text(
                f"{legacy_digest}  {LEGACY_GITHUB_ARCHIVE}\n"
                f"{postgres_digest}  {POSTGRES_ARCHIVE}\n",
                encoding="utf-8",
            )

            completed = run_asset(
                "--check-only",
                "--archive-dir",
                str(asset_dir),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_matching_checksum_does_not_hide_an_invalid_tar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            asset_dir = Path(temporary) / "assets"
            asset_dir.mkdir()
            archive = asset_dir / POSTGRES_ARCHIVE
            archive.write_bytes(b"not a tar archive")
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            (asset_dir / "SHA256SUMS").write_text(
                f"{digest}  {POSTGRES_ARCHIVE}\n",
                encoding="utf-8",
            )

            completed = run_asset(
                "--small",
                "--check-only",
                "--archive-dir",
                str(asset_dir),
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("not a readable tar", completed.stderr)


class StateAssetScriptTests(unittest.TestCase):
    def run_state(
        self,
        root: Path,
        environment: dict[str, str],
        *arguments: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(STATE_SCRIPT),
                "--mcpmark-root",
                str(root),
                *arguments,
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def test_three_service_state_has_ten_filesystem_and_five_postgres_assets(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "mcpmark"
            root.mkdir()
            environment = prepare_fake_state(root)

            completed = self.run_state(root, environment, "--check-only")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("All 15 MCPMark state assets are ready", completed.stdout)
            self.assertFalse((root / "github_state").exists())
            filesystem_manifest = (
                root / "test_environments" / "SHA256SUMS.local"
            ).read_text(encoding="utf-8")
            self.assertEqual(len(filesystem_manifest.splitlines()), 10)

    def test_check_only_rejects_a_missing_filesystem_category(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "mcpmark"
            root.mkdir()
            environment = prepare_fake_state(root)
            missing = root / "test_environments" / FILESYSTEM_CATEGORIES[-1]
            for child in missing.iterdir():
                child.unlink()
            missing.rmdir()

            completed = self.run_state(root, environment, "--check-only")

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(f"Filesystem state is missing: {missing}", completed.stderr)

    def test_filesystem_downloads_extract_atomically_and_refreeze(self) -> None:
        module = load_state_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            downloads = root / "downloads"
            target = root / "test_environments"
            downloads.mkdir()
            for category in FILESYSTEM_CATEGORIES:
                archive = downloads / f"{category}.zip"
                with zipfile.ZipFile(archive, "w") as handle:
                    handle.writestr(f"{category}/fixture.txt", category)
                    handle.writestr(f"__MACOSX/._{category}", "AppleDouble metadata")

            def fake_download(url: str, destination: Path) -> None:
                source = downloads / url.rsplit("/", 1)[-1]
                destination.write_bytes(source.read_bytes())

            with mock.patch.object(module, "download", side_effect=fake_download):
                module.prepare_filesystem_states(target, check_only=False)

            module.prepare_filesystem_states(target, check_only=True)
            self.assertEqual(
                {
                    path.name
                    for path in target.iterdir()
                    if path.is_dir() and not path.name.startswith(".")
                },
                set(FILESYSTEM_CATEGORIES),
            )
            self.assertFalse(any(target.glob(".*.zip.part")))
            self.assertFalse(any(target.glob(".extract-*")))

    def test_filesystem_zip_rejects_an_unexpected_top_level_tree(self) -> None:
        module = load_state_module()
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "desktop.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("desktop/fixture.txt", "fixture")
                handle.writestr("unexpected/payload.txt", "payload")

            with self.assertRaisesRegex(
                module.StateAssetError,
                "unsafe or unexpected zip member",
            ):
                module.validate_zip(archive, "desktop")


class ThreeServiceConfigurationTests(unittest.TestCase):
    def test_setup_does_not_prefetch_notion(self) -> None:
        setup_text = SETUP_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("@modelcontextprotocol/server-filesystem@2025.12.18", setup_text)
        self.assertIn("@playwright/mcp@0.0.68", setup_text)
        self.assertIn("postgres-mcp==0.3.0", setup_text)
        self.assertNotIn("@notionhq/notion-mcp-server", setup_text)

    def test_environment_example_contains_no_github_or_notion_credentials(
        self,
    ) -> None:
        example = ENV_EXAMPLE.read_text(encoding="utf-8")
        for forbidden in (
            "GITHUB_TOKENS",
            "GITHUB_EVAL_ORG",
            "SOURCE_NOTION_API_KEY",
            "EVAL_NOTION_API_KEY",
        ):
            self.assertNotIn(forbidden, example)
        self.assertIn(
            "FILESYSTEM_TEST_ROOT=./test_environments",
            example,
        )


class SetupPostgresClientTests(unittest.TestCase):
    def make_fake_environment(
        self,
        root: Path,
        *,
        prefix_major: int | None,
        system_major: int | None,
    ) -> tuple[dict[str, str], Path]:
        fake_bin = root / "bin"
        fake_bin.mkdir()
        upstream = root / "upstream"
        (upstream / ".git").mkdir(parents=True)
        venv = root / "venv"
        (venv / "bin").mkdir(parents=True)
        prefix = root / "postgres-client"
        node_prefix = root / "node-runtime"
        node_bin = node_prefix / "node_modules" / ".bin"
        node_bin.mkdir(parents=True)
        for executable in (
            "mcp-server-filesystem",
            "playwright",
            "playwright-mcp",
        ):
            write_executable(node_bin / executable, "exit 0\n")

        python_body = (
            f'if [[ "${{2:-}}" == *"/task_manifest.json" ]]; then\n'
            f"  printf '%s\\n' '{EXPECTED_COMMIT}'\n"
            "fi\n"
        )
        write_executable(fake_bin / "python", python_body)
        write_executable(venv / "bin" / "python", python_body)
        write_executable(
            fake_bin / "git",
            f"printf '%s\\n' '{EXPECTED_COMMIT}'\n",
        )

        for executable in (
            "node",
            "npm",
            "npx",
            "ollama",
            "curl",
            "wget",
            "unzip",
            "pipx",
            "docker",
        ):
            write_executable(fake_bin / executable, "exit 0\n")

        if system_major is not None:
            for executable in ("psql", "pg_restore"):
                write_executable(
                    fake_bin / executable,
                    f"printf '%s\\n' '{executable} (PostgreSQL) {system_major}.7'\n",
                )
        if prefix_major is not None:
            (prefix / "bin").mkdir(parents=True)
            for executable in ("psql", "pg_restore"):
                write_executable(
                    prefix / "bin" / executable,
                    f"printf '%s\\n' '{executable} (PostgreSQL) {prefix_major}.7'\n",
                )

        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{fake_bin}{os.pathsep}/usr/bin:/bin",
                "MCPMARK_ROOT": str(upstream),
                "MCPMARK_VENV": str(venv),
                "MCPMARK_POSTGRES_CLIENT_PREFIX": str(prefix),
                "MCPMARK_PLAYWRIGHT_NODE_PREFIX": str(node_prefix),
                "MCPMARK_CONTAINER_CLI": str(fake_bin / "docker"),
                "PYTHON_BOOTSTRAP": str(fake_bin / "python"),
            }
        )
        return environment, prefix

    def run_setup(
        self, environment: dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SETUP_SCRIPT), "--check-only"],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def test_check_only_prefers_valid_local_pg17_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            environment, prefix = self.make_fake_environment(
                Path(temporary),
                prefix_major=17,
                system_major=16,
            )
            completed = self.run_setup(environment)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn(f"pg client:  {prefix}/bin", completed.stdout)

    def test_check_only_accepts_pg17_from_system_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            environment, _ = self.make_fake_environment(
                Path(temporary),
                prefix_major=None,
                system_major=17,
            )
            completed = self.run_setup(environment)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("pg client:  system PATH", completed.stdout)

    def test_check_only_rejects_non_pg17_clients_without_installing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            environment, prefix = self.make_fake_environment(
                Path(temporary),
                prefix_major=None,
                system_major=16,
            )
            completed = self.run_setup(environment)

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "PostgreSQL 17 psql/pg_restore are unavailable",
                completed.stderr,
            )
            self.assertFalse(prefix.exists())

    def test_check_only_rejects_missing_pinned_node_playwright(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment, _ = self.make_fake_environment(
                root,
                prefix_major=17,
                system_major=None,
            )
            node_prefix = Path(environment["MCPMARK_PLAYWRIGHT_NODE_PREFIX"])
            (node_prefix / "node_modules" / ".bin" / "playwright-mcp").unlink()

            completed = self.run_setup(environment)

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Pinned Node MCP runtime is missing", completed.stderr)


if __name__ == "__main__":
    unittest.main()
