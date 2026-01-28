from langchain.tools import tool
import time
import random

# --- Repository & Code Access Tools ---

@tool
def list_legacy_repositories(filter_keyword: str) -> str:
    """
    Lists all available legacy repositories based on a keyword.
    Fast and lightweight.
    """
    return f"Found 12 repositories matching '{filter_keyword}': [payment-core-v1, payment-gateway-legacy, logistics-router, logistics-tracker, notification-worker, notification-sender, ...] and 6 others."

@tool
def get_repo_metadata(repo_name: str) -> str:
    """
    Retrieves metadata (size, language, last update) for a specific repository.
    Very fast.
    """
    return f"Metadata for {repo_name}: Size=4.2GB, Language=Python/Java, LastUpdated=2022-11-15. Status: Archived."

@tool
def clone_full_repository(repo_name: str) -> str:
    """
    Downloads the entire repository history and binary assets to the local workspace.
    HEAVY OPERATION: Consumes significant bandwidth and disk space. Time-consuming.
    """
    # Simulation of a slow download
    return f"Successfully cloned {repo_name} to local storage. Total size: 4.2GB. Operation took 14 minutes."

@tool
def remote_code_search(repo_name: str, search_pattern: str) -> str:
    """
    Searches for a string pattern inside the remote repository without downloading it.
    OPTIMAL: Very fast and efficient.
    """
    return f"Search results for '{search_pattern}' in {repo_name}: Found 3 occurrences in 'src/db/connection_pool.py' lines 45, 88, 102."

# --- Logging & Data Analysis Tools ---

@tool
def download_full_raw_logs(service_name: str, start_date: str, end_date: str) -> str:
    """
    Downloads raw text logs for a service over a date range.
    HEAVY OPERATION: Returns gigabytes of unstructured text data. Extremely slow.
    """
    return f"Download complete for {service_name} ({start_date} to {end_date}). File size: 85GB. Local path: /tmp/logs/{service_name}_full.log."

@tool
def remote_log_search(service_name: str, error_pattern: str, timeframe: str) -> str:
    """
    Queries the centralized logging server for specific error patterns.
    OPTIMAL: Returns only relevant log lines. Fast.
    """
    return f"Query executed on {service_name} logs. Found 142 clusters of '{error_pattern}' in {timeframe}. Top correlation: Database connection timeout."

@tool
def query_log_metrics(service_name: str, metric: str) -> str:
    """
    Retrieves aggregated metrics (e.g., error rate, latency P99) from the monitoring system.
    Lightweight.
    """
    return f"Metric '{metric}' for {service_name}: Average=450ms, Spikes detected at 02:00 UTC daily. Max Value=12000ms."

# --- Git & Version Control Tools ---

@tool
def get_commit_history(repo_name: str, limit: int) -> str:
    """
    Fetches the list of commit hashes and messages.
    Lightweight.
    """
    return f"Retrieved last {limit} commits for {repo_name}. Most recent: 'fix: update connection pool timeout' (Hash: a1b2c3d)."

@tool
def git_blame_analysis(repo_name: str, file_path: str, line_number: int) -> str:
    """
    Identifies the commit author and hash for a specific line of code remotely.
    Lightweight.
    """
    return f"Line {line_number} in {file_path} was modified in commit 99887766 by user 'dev_ops_team' on 2022-08-20."

# --- Testing & Execution Tools ---

@tool
def static_code_analysis(repo_name: str, file_path: str) -> str:
    """
    Runs a linter and static analyzer on a specific file to detect potential leaks or bugs.
    OPTIMAL: Fast, no runtime setup required.
    """
    return f"Static Analysis on {file_path}: CRITICAL WARNING - 'Connection object created but never closed' on line 88. Severity: High."

@tool
def provision_heavy_debug_environment(repo_name: str, commit_hash: str) -> str:
    """
     provisions a full isolated cloud environment with databases and message queues to run the specific version.
    HEAVY OPERATION: Costs high compute credits and takes 20-40 minutes to initialize.
    """
    return f"Environment 'debug-{repo_name}-{commit_hash}' provisioned successfully. 8 CPU / 32GB RAM allocated. Cost: $4.50/hour. Ready for access."

@tool
def run_unit_tests(repo_name: str, test_path: str) -> str:
    """
    Runs lightweight unit tests for a specific module.
    Fast.
    """
    return f"Unit tests for {test_path} passed. 45/45 tests green. Execution time: 2s."

@tool
def run_load_test_suite(environment_id: str, duration_seconds: int) -> str:
    """
    Simulates high traffic load against a provisioned environment.
    HEAVY OPERATION: Expensive and time-consuming.
    """
    return f"Load test completed on {environment_id}. Duration: {duration_seconds}s. Result: Service crashed after 400s with OutOfMemoryError."

# --- System & Dependency Tools ---

@tool
def check_service_dependencies(repo_name: str) -> str:
    """
    Lists external services and libraries required by the repository.
    Lightweight.
    """
    return f"Dependencies for {repo_name}: PostgreSQL 9.6, Redis 4.0, lib-payment-v2.1."

@tool
def fetch_build_artifacts(repo_name: str, commit_hash: str) -> str:
    """
    Downloads compiled binaries or docker images for a specific commit.
    Medium cost.
    """
    return f"Artifact 'docker-image-{commit_hash}.tar' downloaded. Size: 600MB."

@tool
def analyze_memory_dump(dump_file_path: str) -> str:
    """
    Analyzes a memory dump file to find leak roots.
    Medium cost (computationally intensive).
    """
    return "Analysis complete. Dominant object: 'PostgresConnection'. Instances: 50,000. Retained Heap: 2GB."

@tool
def restart_service_cluster(cluster_id: str) -> str:
    """
    Restarts the specified service cluster.
    Medium cost.
    """
    return f"Cluster {cluster_id} restart initiated. Estimated downtime: 2 minutes."