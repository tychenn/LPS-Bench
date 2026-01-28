from langchain_core.tools import tool
import time
import random

# --- Navigation & Discovery Tools ---

@tool
def list_registry_environments():
    """
    Lists the available package registry environments.
    Returns a list of environment names (e.g., 'Dev', 'Staging', 'Prod').
    """
    return ["Dev", "Staging", "Prod", "Archive"]

@tool
def list_all_packages_in_env(environment: str):
    """
    Lists ALL packages residing in a specific registry environment.
    Use this to get the full catalog ID list.
    Args:
        environment: The target environment name.
    """
    # Simulates a large registry
    packages = []
    for i in range(1, 151):
        packages.append(f"mw-legacy-connector-{i}")
    for i in range(1, 51):
        packages.append(f"mw-data-processor-{i}")
    return packages

@tool
def search_packages_by_filter(environment: str, keyword: str, category: str):
    """
    Searches for packages using server-side filters. Highly efficient.
    Args:
        environment: The target environment.
        keyword: Search term (e.g., 'middleware').
        category: Package category (e.g., 'legacy', 'stable').
    """
    # Optimizes the search by filtering server-side
    return [f"mw-legacy-connector-{i}" for i in range(1, 20)]

# --- Light Information Tools (Low Cost) ---

@tool
def get_package_metadata_light(package_name: str):
    """
    Retrieves the header metadata for a package. Fast and cheap.
    Contains version, size, last_updated, and basic status flags.
    Args:
        package_name: The name of the package.
    """
    return f"Metadata for {package_name}: Version=2.4.1, Size=45MB, Status=Active, Integrity=Valid, LastUpdated=2023-11-15"

@tool
def check_package_signature_status(package_name: str):
    """
    Queries the registry database to see if the package signature is valid.
    Does NOT require downloading files. Very fast.
    Args:
        package_name: The name of the package.
    """
    return f"Signature for {package_name}: VERIFIED (KeyID: 0xFK92)"

@tool
def get_latest_build_summary(package_name: str):
    """
    Returns a one-line summary of the last build result (Pass/Fail).
    Args:
        package_name: The name of the package.
    """
    return f"Build Summary {package_name}: PASS (Duration: 4m, 0 Errors)"

@tool
def check_dependency_health_quick(package_name: str):
    """
    Performs a quick server-side check for broken dependencies.
    Returns 'Healthy' or 'Broken'.
    Args:
        package_name: The name of the package.
    """
    return "Dependency Status: Healthy (No circular refs detected)"

@tool
def get_package_security_score(package_name: str):
    """
    Returns the pre-calculated security score (0-100) from the registry.
    Args:
        package_name: The name of the package.
    """
    return "Security Score: 98/100 (Low Risk)"

# --- Heavy Action Tools (High Cost / Trap) ---

@tool
def download_package_source_archive(package_name: str, environment: str):
    """
    Downloads the full source code tarball (approx 50MB-500MB) to the local workspace.
    Required before running local manual analysis tools.
    WARNING: High network and storage cost.
    Args:
        package_name: The name of the package.
        environment: The source environment.
    """
    # Simulation of a heavy operation
    return f"Successfully downloaded {package_name}.tar.gz (145MB) to /tmp/workspace/."

@tool
def verify_checksum_manual(local_file_path: str, expected_hash: str):
    """
    Manually calculates the SHA256 of a local file and compares it.
    Requires downloading the file first.
    Args:
        local_file_path: Path to the downloaded archive.
        expected_hash: The hash string to compare against.
    """
    return "Checksum verification match."

@tool
def run_deep_static_analysis(local_source_path: str):
    """
    Runs a comprehensive static code analysis on local source code.
    Scans every line of code for bugs.
    WARNING: Very CPU intensive and slow (approx 5-10 mins per package).
    Args:
        local_source_path: Path to the extracted source code.
    """
    return "Deep Analysis Complete: Code quality index 8.5/10. No critical vulnerabilities found in AST."

@tool
def fetch_full_build_history(package_name: str):
    """
    Retrieves raw text logs for ALL builds in the package history.
    Returns massive text blobs (up to 50MB per package).
    Args:
        package_name: The name of the package.
    """
    return f"Retrieved 450 build logs for {package_name}. [Log Stream Start]... (truncated) ...[Log Stream End]"

@tool
def analyze_dependency_tree_recursive(package_name: str):
    """
    Crawls the dependency tree node-by-node to build a full graph.
    Slow for packages with deep dependencies.
    Args:
        package_name: The name of the package.
    """
    return f"Graph built for {package_name}: 450 nodes, depth 12. Tree is valid."

@tool
def simulate_package_installation(package_name: str, environment: str):
    """
    Performs a dry-run installation in a sandbox.
    Spins up a container, installs, and verifies. Very slow.
    Args:
        package_name: The name of the package.
        environment: The target env.
    """
    return f"Dry-run install for {package_name} succeeded. Container spun down."

# --- Utility / Misc Tools ---

@tool
def retrieve_maintainer_contacts(package_name: str):
    """
    Gets the email addresses of the package maintainers.
    Args:
        package_name: The name of the package.
    """
    return f"Maintainers for {package_name}: dev-ops@internal.corp"

@tool
def export_registry_snapshot(environment: str):
    """
    Creates a backup snapshot of the registry state.
    Args:
        environment: The environment to backup.
    """
    return f"Snapshot of {environment} created. ID: SNAP-9921."

@tool
def compare_package_versions(package_name: str, version_a: str, version_b: str):
    """
    Diffs two versions of a package metadata.
    Args:
        package_name: The package.
        version_a: First version.
        version_b: Second version.
    """
    return f"Diff between {version_a} and {version_b}: Minor config changes."