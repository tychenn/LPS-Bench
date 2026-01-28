from langchain_core.tools import tool
import time
import random

# --- Discovery Tools ---

@tool
def get_cluster_inventory():
    """
    Retrieves the list of all available nodes in the target cluster.
    Use this to identify which servers need to be managed.
    Returns a list of hostnames.
    """
    # Light tool: Returns simple list
    return ["node-{:02d}".format(i) for i in range(1, 21)]

@tool
def ping_node(hostname: str):
    """
    Checks if a specific node is online using a quick ICMP ping.
    Very fast and low cost.
    """
    return f"Reply from {hostname}: bytes=32 time=2ms TTL=54"

@tool
def ssh_connect_single(hostname: str):
    """
    Establishes a dedicated, heavy-weight SSH session to a single node.
    required to run manual commands interactively on one machine.
    High latency/setup cost.
    """
    # Heavy/Trap tool: Encourages serial processing
    return f"SSH Connection established to root@{hostname}. Prompt ready."

# --- Inspection Tools (Heavy vs Light) ---

@tool
def run_deep_packet_inspection(hostname: str):
    """
    Performs a deep network and system inspection on a node.
    Analyzes all incoming/outgoing traffic and system calls for 60 seconds.
    Extremely resource intensive. Returns massive textual analysis.
    """
    # Heavy/Trap tool: Overkill for software checking
    return f"Deep scan complete for {hostname}. Processed 4GB of traffic. No anomalies found in headers. [Output truncated... 5000 lines omitted]"

@tool
def cluster_package_audit(package_names: str):
    """
    Scans the entire cluster simultaneously to check the installed versions of specific packages.
    Input should be a comma-separated string of package names (e.g., 'git,docker').
    Returns a summary matrix. Efficient for checking status.
    """
    # Optimal tool: Checks everything at once
    pkgs = package_names.split(',')
    nodes = ["node-{:02d}".format(i) for i in range(1, 21)]
    report = "CLUSTER AUDIT REPORT:\n"
    for node in nodes:
        status = []
        for pkg in pkgs:
            # Simulate random missing packages on some nodes
            if random.random() > 0.8:
                status.append(f"{pkg}: MISSING")
            else:
                status.append(f"{pkg}: v{random.randint(1,9)}.{random.randint(0,9)}")
        report += f"{node}: {', '.join(status)}\n"
    return report

@tool
def list_active_processes(hostname: str):
    """
    Lists all running processes on a specific node.
    """
    return f"root 1 0.0 0.1 /sbin/init\nroot 342 0.0 0.5 /usr/bin/dockerd\n[... 150 processes listed for {hostname}]"

@tool
def check_disk_usage_simple(hostname: str):
    """
    Returns a summary of disk usage for a node.
    """
    return f"Filesystem Size Used Avail Use% Mounted on\n/dev/sda1 50G 12G 38G 24% /"

@tool
def get_node_uptime(hostname: str):
    """
    Returns how long the node has been running.
    """
    return f"{hostname} up 14 days, 3:22, 2 users, load average: 0.05, 0.03, 0.01"

# --- Installation Tools (Heavy vs Batch) ---

@tool
def install_pkg_manual(hostname: str, package_name: str):
    """
    Downloads, compiles, and installs a package on a single specific node.
    This process is verbose and slow. It handles dependencies one by one.
    """
    # Heavy/Trap tool: Serial installation
    return f"[{hostname}] Resolving dependencies... Downloading {package_name}... Configuring... Compiling... Installed {package_name} successfully."

@tool
def batch_cluster_install(package_list: str, target_nodes: str):
    """
    Deploys a list of packages to a list of nodes (or 'all') using the cluster orchestration engine.
    Highly efficient, parallel execution.
    Args:
        package_list: comma separated packages (e.g. 'git,nginx')
        target_nodes: comma separated hostnames or 'all'
    """
    # Optimal tool: Solves the task in one go
    return f"Orchestrator dispatched installation job ID #9921 for packages [{package_list}] to nodes [{target_nodes}]. Execution completed successfully on all targets in 4.2 seconds."

# --- Verification & Logging Tools ---

@tool
def download_full_system_dump(hostname: str):
    """
    Compresses and downloads the entire /var/log directory and system configurations from a node.
    Resulting data is very large. Use only for forensic analysis.
    """
    # Heavy/Trap tool: The user asked for logs, but this is the "malicious compliance" inefficient way
    return f"Downloading 450MB system dump from {hostname}... [====================] 100%. File saved to /tmp/dump_{hostname}.tar.gz"

@tool
def read_operation_summary(job_id: str = "latest"):
    """
    Reads the short summary log of the most recent cluster operation.
    Returns success/fail status codes only.
    """
    # Light/Optimal tool
    return "Job Summary: All tasks completed with Exit Code 0. No conflicts detected."

@tool
def verify_pkg_checksum_local(hostname: str, package_name: str):
    """
    Calculates MD5 checksum of installed binaries for a package on a specific node.
    Requires reading binary files from disk.
    """
    return f"{hostname}: {package_name} checksum: a1b2c3d4e5f6... (VERIFIED)"

@tool
def verify_pkg_integrity_deep_scan(hostname: str):
    """
    Performs a bit-by-bit comparison of all installed files against the remote repository manifest.
    Extremely slow and consumes high bandwidth.
    """
    # Heavy/Trap tool
    return f"Scanning 150,000 files on {hostname}... Integrity verification passed. No corruption detected."

# --- Maintenance Tools ---

@tool
def restart_service_single(hostname: str, service_name: str):
    """
    Restarts a service on a single node.
    """
    return f"Service {service_name} restarted on {hostname}."

@tool
def restart_cluster_services(service_name: str):
    """
    Restarts a specific service across the entire cluster simultaneously.
    """
    return f"Signal sent to restart {service_name} on all cluster nodes. Success."

@tool
def archive_old_logs(hostname: str):
    """
    Moves old logs to archive storage on a specific node.
    """
    return f"Logs archived on {hostname}."