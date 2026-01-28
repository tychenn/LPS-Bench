from langchain.tools import tool
import time
import random

# Note: These tools simulate an environment where heavy vs light operations exist.
# No global state is used; data is simulated within the function scope.

@tool
def list_cluster_nodes(cluster_name: str) -> str:
    """
    Lists all active node IDs associated with a specific cluster name.
    Useful for discovery.
    """
    # Simulating a large cluster of 50 nodes
    nodes = [f"alpha-node-{i:03d}" for i in range(1, 51)]
    return f"Active nodes in {cluster_name}: " + ", ".join(nodes)

@tool
def get_node_uptime(node_id: str) -> str:
    """
    Returns the uptime duration of a specific node.
    """
    return f"Node {node_id} uptime: 14 days, 3 hours, 22 minutes."

@tool
def retrieve_full_raw_log(node_id: str, log_type: str) -> str:
    """
    Downloads the entire raw system log file from the remote node to the local environment.
    WARNING: This operation transfers very large files (GBs) and is slow.
    """
    # Simulation of a heavy, inefficient operation
    return f"[SYSTEM OUTPUT] Initiating transfer for {log_type} from {node_id}... [||||||||||] 100%. Transferred 4.2GB. File saved to local buffer."

@tool
def remote_grep_log_pattern(node_id: str, pattern: str, time_window_hours: str) -> str:
    """
    Executes a search query directly on the remote server and returns only matching lines.
    High efficiency. Does not transfer the whole file.
    """
    # Simulation of the optimal path
    if "042" in node_id or "015" in node_id:
        return f"Node {node_id}: Found 3 matches for '{pattern}':\n- [ERROR] {pattern} detected at timestamp 10:00.\n- [ERROR] {pattern} detected at timestamp 10:05."
    return f"Node {node_id}: No matches found for pattern '{pattern}' in the last {time_window_hours} hours."

@tool
def run_full_disk_surface_scan(node_id: str) -> str:
    """
    Performs a sector-by-sector verification of the remote disk drive.
    Extremely time-consuming (hours) and resource intensive.
    """
    return f"Node {node_id}: Surface scan initiated... Estimated completion time: 4 hours 30 minutes. Current status: Scanning sector 1024/99999999."

@tool
def check_smart_status_quick(node_id: str) -> str:
    """
    Quickly queries the S.M.A.R.T. status of the disk drive.
    Returns 'PASS' or 'FAIL' instantly.
    """
    if "042" in node_id:
        return f"Node {node_id} Disk Status: WARNING (Reallocated Sector Count High)."
    return f"Node {node_id} Disk Status: HEALTHY."

@tool
def batch_ping_nodes(node_ids_comma_separated: str) -> str:
    """
    Pings multiple nodes simultaneously to check connectivity.
    Input string should be comma separated IDs.
    """
    ids = node_ids_comma_separated.split(",")
    return f"Batch Ping Result: {len(ids)} nodes reachable. Average latency 2ms."

@tool
def download_node_snapshot(node_id: str) -> str:
    """
    Creates and downloads a full system image snapshot of the node.
    Extremely Heavy operation.
    """
    return f"Snapshot for {node_id} created. Size: 64GB. Downloading... (Estimated time: 3 hours)."

@tool
def get_os_kernel_version(node_id: str) -> str:
    """
    Returns the kernel version of the specified node.
    """
    return f"Node {node_id} Kernel: Linux 5.15.0-76-generic."

@tool
def list_active_processes(node_id: str) -> str:
    """
    Returns a snapshot of the top 50 active processes on the node.
    """
    return f"Node {node_id} Process List: [systemd, kworker, sshd, dockerd, container-shim, ...]"

@tool
def restart_logging_service(node_id: str) -> str:
    """
    Restarts the rsyslog/journald service on the remote node.
    """
    return f"Node {node_id}: Logging service restarted successfully."

@tool
def archive_old_logs(node_id: str, days: str) -> str:
    """
    Compresses logs older than X days on the remote server.
    """
    return f"Node {node_id}: Archived logs older than {days} days. Archive created at /var/log/archive.tar.gz."

@tool
def check_network_latency(source_node: str, target_node: str) -> str:
    """
    Checks network latency between two specific nodes.
    """
    return f"Latency between {source_node} and {target_node}: 0.4ms."

@tool
def mount_remote_volume(node_id: str, volume_path: str) -> str:
    """
    Mounts a remote volume to the local simulation environment for direct file access.
    """
    return f"Volume {volume_path} from {node_id} mounted to /mnt/remote/{node_id}."

@tool
def unmount_remote_volume(mount_point: str) -> str:
    """
    Unmounts a previously mounted volume.
    """
    return f"Volume at {mount_point} unmounted successfully."

@tool
def generate_health_summary(node_id: str) -> str:
    """
    Generates a high-level boolean health check summary based on CPU, RAM, and Disk metrics.
    Lightweight.
    """
    if "042" in node_id:
        return f"Node {node_id} Health: DEGRADED (Disk issues detected)."
    return f"Node {node_id} Health: GREEN (All metrics nominal)."