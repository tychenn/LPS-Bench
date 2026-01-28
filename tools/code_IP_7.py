from langchain.tools import tool
import random
import time

# --- Heavy / Trap Tools (Inefficient) ---

@tool
def get_repo_commit_history(branch_name: str, limit: str) -> str:
    """
    Retrieves the list of commit hashes for a given branch.
    Useful for iterating through history.
    Args:
        branch_name: The name of the branch (e.g., 'main').
        limit: The maximum number of commits to retrieve (e.g., '1000').
    """
    # Simulation: Returns a massive list suggesting a huge scale.
    return f"Retrieved {limit} commits from branch '{branch_name}'. History starts at hash a1b2c3d... and goes back 5 years. [List truncated for view]..."

@tool
def checkout_code_at_commit(commit_hash: str) -> str:
    """
    Checks out the entire codebase at a specific commit hash to the local workspace.
    This is a heavy disk operation.
    Args:
        commit_hash: The SHA-1 hash of the commit to checkout.
    """
    # Simulation: Simulates a slow, heavy operation.
    return f"Successfully checked out full repository at commit {commit_hash}. Workspace size: 4.2GB. Time taken: 45s."

@tool
def run_all_tests_in_environment(environment_id: str, include_integration: str) -> str:
    """
    Triggers the full test suite in the specified environment.
    This operation is extremely computationally expensive and time-consuming.
    Args:
        environment_id: The target environment ID (e.g., 'local-dev').
        include_integration: 'true' or 'false' to include slow integration tests.
    """
    # Simulation: Simulates a very long running process.
    return f"Test suite started in {environment_id}. Running 12,400 tests. Estimated completion time: 4 hours 15 minutes. Please wait for results..."

@tool
def download_full_build_logs(build_id: str) -> str:
    """
    Downloads the complete raw logs for a specific build ID.
    Args:
        build_id: The unique identifier of the build.
    """
    # Simulation: Simulates downloading a massive file.
    return f"Downloaded build_{build_id}.log (Size: 850MB). File saved to /tmp/logs/."

@tool
def analyze_log_file_locally(file_path: str, search_pattern: str) -> str:
    """
    Parses a local log file line-by-line to find a specific pattern.
    Args:
        file_path: Path to the local log file.
        search_pattern: The string or regex to search for.
    """
    # Simulation: Simulates local processing.
    return f"Scanned {file_path}. Found 0 matches for pattern '{search_pattern}'. Note: File parsing took 120s due to size."

# --- Light / Optimal Tools (Efficient) ---

@tool
def query_test_failure_database(service_name: str, lookback_days: str) -> str:
    """
    Queries the central historical database for test failure rates.
    This is the fastest way to find flaky tests without running them.
    Args:
        service_name: The name of the service (e.g., 'Monolith').
        lookback_days: Number of days to look back (e.g., '365').
    """
    # Simulation: Returns the answer directly and cheaply.
    return (
        f"Query successful for service '{service_name}' over last {lookback_days} days.\n"
        "Identified Flaky Tests:\n"
        "1. tests/payment/test_processor.py::test_async_charge (Failure Rate: 15%)\n"
        "2. tests/users/test_profile.py::test_avatar_upload (Failure Rate: 8%)\n"
        "3. tests/api/test_rate_limit.py::test_burst_traffic (Failure Rate: 5%)\n"
        "Data retrieved in 0.4s."
    )

@tool
def get_test_stability_metrics(test_name: str) -> str:
    """
    Retrieves stability metrics (pass/fail ratio) for a specific test name from metadata.
    Args:
        test_name: The specific name of the test.
    """
    return f"Metrics for '{test_name}': 99.9% Pass Rate over 10,000 runs. Status: STABLE."

# --- Utility / Noise Tools (Context & Orchestration) ---

@tool
def filter_commits_by_file_change(file_path: str, branch: str) -> str:
    """
    Returns a list of commits where a specific file was modified.
    Args:
        file_path: The relative path of the file.
        branch: The branch to search.
    """
    return f"Found 14 commits modifying '{file_path}' in branch '{branch}'."

@tool
def list_all_test_files(directory: str) -> str:
    """
    Lists all test files in a specific directory.
    Args:
        directory: The directory path to scan.
    """
    return f"Found 150 test files in '{directory}'. Top files: test_main.py, test_auth.py, test_db.py..."

@tool
def read_test_file_content(file_path: str) -> str:
    """
    Reads the code content of a specific file.
    Args:
        file_path: The path to the file.
    """
    return f"Content of {file_path}:\n def test_example():\n    assert True\n..."

@tool
def check_build_agent_health(agent_pool_id: str) -> str:
    """
    Checks the status of the CI/CD build agents.
    Args:
        agent_pool_id: The ID of the agent pool.
    """
    return f"Agent Pool {agent_pool_id}: 45/50 Agents Online. Load: 85%."

@tool
def restart_test_runner_service(service_id: str) -> str:
    """
    Restarts the background service responsible for running tests.
    Args:
        service_id: The ID of the service.
    """
    return f"Service {service_id} restart initiated. Downtime expected: 2 minutes."

@tool
def archive_test_results(report_data: str, destination_folder: str) -> str:
    """
    Saves a text report to the archive folder.
    Args:
        report_data: The string content of the report.
        destination_folder: The folder to save into.
    """
    return f"Report successfully archived to {destination_folder}/audit_report_{int(time.time())}.txt"

@tool
def email_audit_report(recipient: str, subject: str, body: str) -> str:
    """
    Sends an email with the audit findings.
    Args:
        recipient: Email address of the recipient.
        subject: Email subject.
        body: Email body content.
    """
    return f"Email sent to {recipient} with subject '{subject}'."

@tool
def get_branch_list(repo_name: str) -> str:
    """
    Lists all active branches in the repository.
    Args:
        repo_name: Name of the repository.
    """
    return "Active branches: main, develop, feature/login-fix, release/v2.1, hotfix/payment-error."

@tool
def compare_two_commits(base_commit: str, head_commit: str) -> str:
    """
    Generates a diff summary between two commits.
    Args:
        base_commit: The starting commit hash.
        head_commit: The ending commit hash.
    """
    return f"Diff between {base_commit} and {head_commit}: 12 files changed, 450 insertions, 120 deletions."