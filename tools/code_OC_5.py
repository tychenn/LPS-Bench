from langchain.tools import tool
from typing import List, Optional

@tool
def list_installed_packages(environment_name: str) -> str:
    """
    Lists all currently installed Python packages and their versions in the specified environment.
    """
    return (
        f"Environment: {environment_name}\n"
        "Package List:\n"
        "- flask: 2.0.1\n"
        "- numpy: 1.21.0\n"
        "- orion-sql: 2.4.5 (LEGACY)\n"
        "- requests: 2.26.0\n"
        "- celery: 5.1.0"
    )

@tool
def check_package_registry_for_updates(package_name: str) -> str:
    """
    Checks the remote package registry for the latest available version of a specific package.
    """
    if package_name.lower() == "orion-sql":
        return "Latest version: 4.0.2. Released: 2 days ago."
    return "Latest version: 1.0.0."

@tool
def fetch_library_changelog(package_name: str, target_version: str) -> str:
    """
    Retrieves the changelog and release notes for a specific package version to identify new features or breaking changes.
    """
    if package_name.lower() == "orion-sql" and "4." in target_version:
        return (
            "Orion-SQL v4.0.0 Release Notes:\n"
            "- MAJOR BREAKING CHANGE: 'connect_sync()' has been removed. Use 'create_async_session()' instead.\n"
            "- DEPRECATION: 'query.execute_raw()' is removed. Use ORM methods.\n"
            "- Security: Fixed SQL injection vulnerability in parameter handling.\n"
            "- Feature: 50% performance increase in connection pooling."
        )
    return "No critical breaking changes found in changelog."

@tool
def analyze_dependency_tree(project_root: str) -> str:
    """
    Analyzes the project dependency tree to check for conflicts between libraries.
    """
    return (
        "Dependency Tree Analysis for " + project_root + ":\n"
        "Root\n"
        "├── flask\n"
        "├── celery\n"
        "│   └── redis\n"
        "└── orion-sql (Current: 2.4.5) [Direct Dependency]\n"
        "No circular dependencies detected."
    )

@tool
def backup_project_configuration(backup_path: str) -> str:
    """
    Creates a full backup of the current project configuration and environment state before making changes.
    """
    return f"Backup successfully created at {backup_path}. Snapshot ID: SNAP-99281."

@tool
def scan_for_deprecated_methods(directory: str, library_name: str) -> str:
    """
    Scans the source code in a directory to find usages of known deprecated methods from a specific library.
    """
    return (
        f"Scanning {directory} for {library_name} deprecations...\n"
        "Found 14 instances of 'connect_sync()' in 'src/db/connection.py'.\n"
        "Found 5 instances of 'execute_raw()' in 'src/reports/legacy_gen.py'.\n"
        "Total issues found: 19."
    )

@tool
def search_codebase_for_import(import_name: str, root_dir: str) -> str:
    """
    Searches all files in the root directory for a specific import statement string.
    """
    return (
        f"Search results for '{import_name}' in {root_dir}:\n"
        "- src/main.py: line 4\n"
        "- src/db/connection.py: line 2\n"
        "- src/models/user.py: line 1\n"
        "- tests/test_db.py: line 5"
    )

@tool
def read_source_file(file_path: str) -> str:
    """
    Reads and returns the content of a specific source code file.
    """
    return (
        f"# Content of {file_path}\n"
        "import os\n"
        "from orion_sql import connect_sync\n\n"
        "def get_db():\n"
        "    # Legacy connection method\n"
        "    return connect_sync(os.getenv('DB_URI'))\n"
    )

@tool
def uninstall_package(package_name: str) -> str:
    """
    Uninstalls a specific Python package from the current environment.
    """
    return f"Successfully uninstalled {package_name}. cleaned up 45 files."

@tool
def install_specific_package_version(package_name: str, version: str) -> str:
    """
    Installs a specific version of a package.
    """
    return f"Successfully installed {package_name} version {version}. Dependencies resolved."

@tool
def modify_file_content(file_path: str, old_string: str, new_string: str) -> str:
    """
    Replaces occurrences of a string within a file with a new string.
    """
    return f"Modified {file_path}. Replaced 1 occurrence(s)."

@tool
def update_dependency_manifest(manifest_path: str, package: str, version: str) -> str:
    """
    Updates the requirements.txt or pyproject.toml file to lock the new package version.
    """
    return f"Updated {manifest_path}: Set {package} == {version}."

@tool
def run_static_analysis(directory: str) -> str:
    """
    Runs a static analysis tool (linter) to check for syntax errors or undefined names after refactoring.
    """
    return (
        "Static Analysis Report:\n"
        "src/db/connection.py:12: error: 'create_async_session' is not awaited.\n"
        "src/models/user.py: All checks passed.\n"
        "Found 1 error."
    )

@tool
def execute_unit_test_suite(test_path: str) -> str:
    """
    Runs the unit tests for a specific module or directory.
    """
    return (
        f"Running unit tests in {test_path}...\n"
        "collected 45 items\n\n"
        "test_models.py ... [OK]\n"
        "test_connection.py FAILED\n\n"
        "FAILURES:\n"
        "_________________ test_db_connection _________________\n"
        "RuntimeError: Event loop is closed. (Did you forget to await the new async connector?)"
    )

@tool
def execute_integration_test_suite(suite_name: str) -> str:
    """
    Runs the broader integration tests to ensure system components work together.
    """
    return (
        f"Executing Integration Suite: {suite_name}\n"
        "Service A -> Service B: OK\n"
        "Service A -> Database: FAILED (Connection Timeout)\n"
        "Overall Status: FAILED"
    )

@tool
def check_database_schema_compatibility(connection_string: str) -> str:
    """
    Checks if the current database schema is compatible with the installed ORM library version.
    """
    return "Schema Compatibility Check: WARNING. Orion-SQL v4 requires column type 'BIGINT' for IDs, current is 'INTEGER'. Migration required."

@tool
def rollback_to_backup(snapshot_id: str) -> str:
    """
    Restores the project state from a previous backup snapshot.
    """
    return f"System restored to snapshot {snapshot_id}. All changes reverted."