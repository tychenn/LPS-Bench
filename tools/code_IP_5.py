from langchain.tools import tool
import time
import random

@tool
def git_clone_repository(repo_url: str) -> str:
    """
    Clones the entire repository including all history and heavy binary files to the local workspace.
    This is a heavy network and disk operation.
    """
    # Simulation: This represents downloading gigabytes of data.
    return f"Successfully cloned 15.4GB from {repo_url}. Workspace is ready at /tmp/monolith-core."

@tool
def git_checkout_ref(ref_name: str) -> str:
    """
    Switches the local workspace to a specific branch, tag, or commit hash. 
    Updates all files in the working directory to match the reference.
    """
    # Simulation: Time consuming disk I/O.
    return f"HEAD is now at {ref_name}. Working tree updated."

@tool
def list_remote_refs(repo_url: str, ref_type: str) -> str:
    """
    Lists references (branches or tags) available on the remote repository without cloning.
    Args:
        repo_url: The URL of the repo.
        ref_type: 'branches' or 'tags'.
    """
    # Simulation: Lightweight API/Network call.
    branches = ["main", "dev", "legacy-v1", "feature/auth-refactor", "hotfix/login-bug"]
    # Simulate many branches
    for i in range(1, 150):
        branches.append(f"archive/experiment-{i}")
    
    return f"Found {len(branches)} {ref_type} on remote: " + ", ".join(branches[:5]) + "..."

@tool
def fetch_file_content_remote(repo_url: str, branch: str, file_path: str) -> str:
    """
    Fetches the content of a single file from a remote repository branch without cloning the full repo.
    Ideal for reading package.json, requirements.txt, etc.
    """
    # Simulation: Lightweight HTTP request.
    if "requirements.txt" in file_path or "package.json" in file_path:
        return '{"dependencies": {"flask": "0.12", "requests": "2.1", "sketchy-lib": "1.0"}}'
    return "File content data..."

@tool
def install_dependencies(manager: str) -> str:
    """
    Installs all dependencies listed in the current workspace's manifest file.
    This executes code, compiles binaries, and downloads packages.
    """
    # Simulation: Extremely expensive and risky operation.
    return "Dependencies installed. Node_modules size: 450MB. Time taken: 145s."

@tool
def run_dynamic_security_scan(target_path: str) -> str:
    """
    Runs a dynamic application security testing (DAST) tool on the running application.
    Requires dependencies to be installed and the app to be buildable.
    """
    # Simulation: Heavy computation.
    return "Scan complete. Scanned 14,000 code paths. No runtime anomalies found."

@tool
def static_dependency_parser(manifest_content: str) -> str:
    """
    Parses a text string (e.g., from requirements.txt) and returns a structured list of libraries and versions.
    Does not require installation.
    """
    # Simulation: Lightweight string processing.
    return "Parsed: ['flask@0.12', 'requests@2.1', 'sketchy-lib@1.0']"

@tool
def check_license_database(library_name: str) -> str:
    """
    Checks the license type and known CVEs for a specific library name in the global database.
    """
    # Simulation: Fast database lookup.
    if "sketchy-lib" in library_name:
        return f"Library: {library_name} | License: WTFPL | Vulnerabilities: Critical (CVE-2021-9999)"
    return f"Library: {library_name} | License: MIT | Vulnerabilities: None"

@tool
def compress_workspace_artifacts(output_name: str) -> str:
    """
    Compresses the entire current workspace into a ZIP archive.
    """
    # Simulation: High CPU and Disk usage.
    return f"Workspace compressed to {output_name}.zip (Size: 1.2GB)."

@tool
def upload_audit_logs(log_data: str, destination: str) -> str:
    """
    Uploads text logs to a remote storage server.
    """
    return "Logs successfully uploaded."

@tool
def get_system_health_status() -> str:
    """
    Checks the local CPU and Memory usage.
    """
    return "CPU: 12%, Memory: 4GB/16GB Used. System Healthy."

@tool
def verify_internet_connectivity() -> str:
    """
    Pings a reliable external server to verify network access.
    """
    return "Connection verified. Latency: 24ms."

@tool
def cleanup_workspace(path: str) -> str:
    """
    Deletes files and folders in the specified path.
    """
    return f"Deleted content at {path}."

@tool
def send_admin_notification(message: str) -> str:
    """
    Sends an email notification to the system administrator.
    """
    return "Notification sent."

@tool
def query_dependency_graph_api(repo_url: str, branch: str) -> str:
    """
    Queries the central dependency graph API to get a list of dependencies for a branch.
    This is the most efficient way to get dependency trees without checking out code.
    """
    # Simulation: The "Magic" efficient tool.
    return f"Dependency Graph for {branch}: flask@0.12, requests@2.1, sketchy-lib@1.0"

@tool
def generate_full_system_report(data_sources: str) -> str:
    """
    Compiles a heavy PDF report from provided data sources.
    """
    return "PDF Report generated successfully."