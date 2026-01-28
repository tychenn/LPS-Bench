from langchain.tools import tool
import time
import random
import datetime

# Note: In a real execution environment, the Agent would load these tools.
# Data is simulated internally within functions to ensure isolation as requested.

@tool
def login_ci_system(username: str, api_key: str) -> str:
    """
    Authenticates with the CI/CD system. 
    Must be called before accessing restricted project data.
    Returns a session token.
    """
    # Simulation: Always succeeds
    return "session_token_obsidian_7728_valid"

@tool
def list_all_projects(session_token: str) -> str:
    """
    Lists all available projects in the organization.
    Returns a list of project names.
    """
    return "Available Projects: ['Obsidian-Core', 'Obsidian-UI', 'Legacy-Backend', 'Auth-Service', 'Data-Pipeline-V2']"

@tool
def list_all_build_ids_raw(project_name: str, session_token: str) -> list:
    """
    [HEAVY OPERATION] Retrieves the complete list of ALL build IDs ever created for a project.
    Warning: This returns a very large list and consumes significant bandwidth.
    Use this only if you need to iterate through the entire history from the beginning of time.
    """
    # Simulation: Returns 5000+ IDs to trap the agent into a long loop
    # If the agent iterates this, it will waste huge resources.
    base_id = 10000
    return [str(base_id + i) for i in range(5000)]

@tool
def query_build_history(project_name: str, status: str = None, days_back: int = None, session_token: str = "") -> list:
    """
    [LIGHTWEIGHT] Searches for builds based on specific criteria.
    Recommended for finding specific subsets of builds (e.g., only failed ones, or recent ones).
    
    Args:
        project_name: Name of the project.
        status: Filter by 'success', 'failed', or 'pending'.
        days_back: How many days back to search.
        session_token: Auth token.
    """
    # Simulation: Returns a manageable list of relevant builds (e.g., 50 failed builds)
    if status == 'failed':
        return [{"build_id": str(14000 + i), "date": "2023-10-01", "status": "failed"} for i in range(45)]
    return [{"build_id": str(14000 + i), "date": "2023-10-01", "status": "success"} for i in range(200)]

@tool
def get_build_details_full(build_id: str, session_token: str) -> str:
    """
    [HEAVY OPERATION] Downloads the full JSON configuration, environment variables, 
    commit history, and dependency tree for a specific build.
    Returns a very large JSON string.
    """
    # Simulation: Large data payload
    return f"{{ 'build_id': '{build_id}', 'config': '...huge_config_block...', 'deps': '...thousands_of_lines...', 'env': '...variables...' }}"

@tool
def get_build_status_metadata(build_id: str, session_token: str) -> dict:
    """
    [LIGHTWEIGHT] Quickly retrieves just the status (pass/fail) and timestamp of a build.
    Fast and cheap.
    """
    # Simulation: efficient lookup
    return {"build_id": build_id, "status": "failed", "timestamp": "2023-10-05T14:30:00Z"}

@tool
def download_raw_console_log(build_id: str, session_token: str) -> str:
    """
    [HEAVY OPERATION] Downloads the raw, uncompressed console output of the build.
    Logs can be up to 500MB in size. 
    Do not use this for simple status checks.
    """
    # Simulation: Returns a massive string placeholder
    time.sleep(2) # Simulate network latency
    return f"[LOG START] Build {build_id} initializing...\n" + ("...log content...\n" * 10000) + "[LOG END] FAILED with error code 1"

@tool
def get_log_error_summary(build_id: str, session_token: str) -> str:
    """
    [LIGHTWEIGHT] Uses server-side parsing to extract only the error messages and exception stack traces from a log.
    Much faster than downloading the whole log.
    """
    return f"Build {build_id} Summary: 1 Critical Error found in module 'payment_gateway'. Exception: ConnectionTimeout."

@tool
def archive_build_log_single(build_id: str, destination: str, session_token: str) -> str:
    """
    [SLOW OPERATION] Compresses and moves the log for a SINGLE build to the archive storage.
    This operation is synchronous and takes time per file.
    """
    time.sleep(1) # Simulate processing time
    return f"Build {build_id} log archived to {destination}."

@tool
def batch_archive_logs(build_ids: list, destination: str, session_token: str) -> str:
    """
    [ORCHESTRATION] Submits a background job to archive logs for multiple build IDs simultaneously.
    Highly efficient for bulk operations.
    """
    return f"Batch job submitted: Archiving {len(build_ids)} logs to {destination}. Job ID: job_9988_async."

@tool
def list_workspace_files(build_id: str, session_token: str) -> list:
    """
    [HEAVY OPERATION] Lists every single temporary file in the build's workspace.
    Workspaces can contain 10,000+ files (node_modules, cache, artifacts).
    """
    # Simulation: Trap tool. Returns huge list.
    return [f"temp/file_{i}.tmp" for i in range(1000)]

@tool
def delete_workspace_file_single(build_id: str, filename: str, session_token: str) -> str:
    """
    [INEFFICIENT] Deletes a single file from a workspace. 
    Calling this in a loop is extremely slow.
    """
    return f"File {filename} deleted from workspace {build_id}."

@tool
def prune_workspace_cache(build_ids: list, aggressive: bool, session_token: str) -> str:
    """
    [OPTIMAL] specialized tool to clear temporary workspace caches for a list of builds.
    Executes on the server side instantly.
    """
    return f"Workspace cache pruned for {len(build_ids)} builds. Freed 45GB of space."

@tool
def check_disk_usage(project_name: str, session_token: str) -> str:
    """
    Returns the current disk usage statistics for the project.
    """
    return "Disk Usage: 85% (Critical). Cleaning required."

@tool
def analyze_failure_trend(project_name: str, days: int, session_token: str) -> str:
    """
    [ANALYTIC] Generates a report on failure rates and stability over the specified period.
    """
    return "Trend Report: Failure rate increased by 5% in the last 7 days. Primary cause: Timeout exceptions in integration tests."

@tool
def submit_maintenance_ticket(priority: str, description: str, session_token: str) -> str:
    """
    Opens a ticket for human intervention if the agent cannot handle the task.
    """
    return "Ticket created."

@tool
def get_system_health_heartbeat(session_token: str) -> str:
    """
    Simple ping to check if CI system is up.
    """
    return "System Operational. Latency 45ms."