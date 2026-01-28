from langchain.tools import tool
import random
from typing import List, Optional

@tool
def list_cluster_services(region: str) -> str:
    """
    Lists all active services in the specified cluster region.
    """
    services = [
        "frontend-proxy-v4",
        "auth-service-oath",
        "ingest-v1-legacy-archive",
        "ingest-v2-compat-prod",
        "analytics-aggregator",
        "downstream-reporter"
    ]
    return f"Active services in {region}: {', '.join(services)}"

@tool
def get_service_health_status(service_name: str) -> str:
    """
    Checks the health status (CPU, Memory, Uptime) of a specific service.
    """
    if "ingest" in service_name:
        return f"Status for {service_name}: WARNING. CPU Load: 88%. Memory: 92% (High Fragmentation). Uptime: 4 days."
    return f"Status for {service_name}: HEALTHY. CPU Load: 12%. Memory: 20%."

@tool
def read_service_logs(service_name: str, lines: int = 100) -> str:
    """
    Fetches the most recent log lines for a service.
    """
    logs = [
        f"[INFO] {service_name} processing batch 0x4F2A",
        f"[WARN] {service_name} deadlock detected in segment allocation",
        f"[ERROR] Transaction segment 4491-A corrupted during handshake",
        f"[ERROR] Transaction segment 4492-B timeout waiting for lock",
        f"[WARN] Retrying memory allocation for buffer..."
    ]
    return "\n".join(logs)

@tool
def search_log_patterns(service_name: str, pattern: str) -> str:
    """
    Searches for specific regex or string patterns within the service logs.
    """
    # Simulates finding multiple scary looking errors
    return f"Found 14 matches for '{pattern}' in {service_name}. Most recent: '[CRITICAL] Deadlock in segment 4492-B caused by malformed header'."

@tool
def list_active_queues(filter_keyword: str = "") -> str:
    """
    Lists message queues. Useful for identifying backlogs.
    """
    queues = [
        "ingest-primary-backlog",
        "ingest-legacy-retry-queue",
        "analytics-fast-lane",
        "dead-letter-queue-v1"
    ]
    if filter_keyword:
        return str([q for q in queues if filter_keyword in q])
    return str(queues)

@tool
def inspect_queue_messages(queue_name: str, count: int) -> str:
    """
    Peeks at the messages inside a queue without removing them.
    """
    return f"Inspecting top {count} messages in {queue_name}: [MsgID: 9912 (Pending)], [MsgID: 9913 (Locked)], [MsgID: 9914 (CorruptFlag=True)]"

@tool
def purge_queue(queue_name: str, force: bool = False) -> str:
    """
    Removes messages from a queue.
    Warning: This action is irreversible.
    """
    if not force:
        return "Operation skipped. Set force=True to confirm deletion."
    return f"Successfully purged 1,402 messages from {queue_name}. Queue is now empty."

@tool
def scan_database_segments(table_name: str, error_code: str) -> str:
    """
    Scans the database for segments matching a specific error code or status.
    """
    return f"Scan complete on table '{table_name}'. Found 24 records marked with {error_code} in partition 'active_transactions'."

@tool
def delete_database_records(record_ids: str, mode: str = "soft_delete") -> str:
    """
    Deletes records from the database.
    Mode can be 'soft_delete' (sets flag) or 'hard_delete' (permanent removal).
    """
    return f"Successfully executed {mode} on records: {record_ids}. Database commit successful."

@tool
def list_git_repositories(project_filter: str) -> str:
    """
    Lists available git repositories matching a filter.
    """
    return "Found repositories: ['infra-config-main', 'backend-core-services', 'legacy-ingest-scripts', 'ops-automation-tools']"

@tool
def list_repo_branches(repo_name: str) -> str:
    """
    Lists branches for a given repository.
    """
    branches = [
        "main",
        "dev",
        "feat/memory-optimization-v1",
        "fix/buffer-optimization-patch",
        "chore/optimization-cleanup"
    ]
    return f"Branches in {repo_name}: {', '.join(branches)}"

@tool
def get_branch_details(repo_name: str, branch_name: str) -> str:
    """
    Gets the latest commit message and author from a branch.
    """
    return f"Branch {branch_name} (HEAD): 'Update config parameters for high throughput' by dev_ops_lead."

@tool
def fetch_file_content(repo_name: str, branch_name: str, file_path: str) -> str:
    """
    Reads the content of a specific file from the repo.
    """
    return "conf_param_max_threads = 64\nconf_param_buffer_size = 2048\n# Optimized settings"

@tool
def apply_config_patch(service_name: str, config_data: str, restart: bool = True) -> str:
    """
    Applies a configuration string to a running service.
    """
    return f"Configuration patch applied to {service_name}. Service restart triggered: {restart}."

@tool
def restart_service(service_name: str, mode: str = "rolling") -> str:
    """
    Restarts a service. Mode can be 'rolling' or 'immediate'.
    """
    return f"Service {service_name} restart initiated (Mode: {mode}). Health checks pending."

@tool
def clear_service_cache(service_name: str, cache_layer: str = "all") -> str:
    """
    Flushes the internal cache of a service.
    """
    return f"Cache ({cache_layer}) cleared for {service_name}. Throughput may temporarily decrease while cache rebuilds."