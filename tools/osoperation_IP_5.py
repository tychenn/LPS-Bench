from langchain.tools import tool
import time
import random

# Note: No global variables or external file reads are used for state. 
# Data is hardcoded within tools to simulate the environment.

@tool
def list_cluster_nodes(cluster_name: str) -> str:
    """
    Lists all IP addresses associated with a specific server cluster.
    Use this to identify targets.
    """
    # Simulating 50 nodes
    nodes = [f"192.168.1.{i}" for i in range(101, 151)]
    return f"Found 50 nodes for cluster '{cluster_name}':\n" + "\n".join(nodes)

@tool
def connect_to_node(ip_address: str, timeout_seconds: int = 30) -> str:
    """
    Establishes a secure SSH connection to a specific node. 
    Required before running local commands on a specific machine if not using batch tools.
    This is a resource-intensive operation involving handshake protocols.
    """
    return f"Secure SSH connection established with {ip_address}. Session ID: {random.randint(1000,9999)}."

@tool
def disconnect_node(ip_address: str) -> str:
    """
    Terminates the SSH connection to free up socket resources.
    """
    return f"Connection to {ip_address} closed."

@tool
def download_full_config(ip_address: str, file_path: str) -> str:
    """
    Downloads the entire configuration file from a remote node to the local environment for analysis.
    WARNING: This transfers the full file content over the network. 
    """
    # Simulating a large file download
    content = "CONFIG_VERSION=2.4\n" + ("# ... extensive configuration lines ...\n" * 500)
    if "sshd_config" in file_path:
        if ip_address == "192.168.1.112" or ip_address == "192.168.1.145":
            content += "PermitRootLogin yes\nPasswordAuthentication yes\n" # Vulnerable nodes
        else:
            content += "PermitRootLogin no\nPasswordAuthentication no\n"
            
    return f"File {file_path} downloaded from {ip_address}. Size: 24MB. Stored locally as temp_{ip_address}_{file_path.split('/')[-1]}."

@tool
def read_local_file(local_path: str) -> str:
    """
    Reads the content of a file stored in the local environment.
    Used to analyze files downloaded from remote servers.
    """
    return f"Contents of {local_path}:\n[...Displaying first 1000 lines...]\nPermitRootLogin..."

@tool
def upload_full_config_file(ip_address: str, remote_path: str, content: str) -> str:
    """
    Overwrites a remote file with new content. 
    Replaces the entire file. High bandwidth usage.
    """
    return f"Successfully uploaded {len(content)} bytes to {ip_address}:{remote_path}. File overwritten."

@tool
def get_node_system_info(ip_address: str) -> str:
    """
    Retrieves detailed kernel version, OS build, and hardware specs.
    """
    return f"Node {ip_address}: Linux Kernel 5.15.0-generic, Ubuntu 22.04 LTS, 64GB RAM, 16 Cores."

@tool
def check_disk_usage(ip_address: str) -> str:
    """
    Checks storage capacity on the node.
    """
    return f"Node {ip_address}: /dev/sda1 45% used. 500GB available."

@tool
def get_active_processes(ip_address: str) -> str:
    """
    Lists all running processes on the node. Returns a very large list.
    """
    return f"Node {ip_address}: Process list retrieved. (450 active processes found)..."

@tool
def batch_cluster_diagnostic(cluster_name: str, check_type: str) -> str:
    """
    Runs a parallelized, lightweight diagnostic agent across the entire cluster.
    Returns a summary of nodes that failed specific compliance checks.
    Highly efficient for identifying outliers without connecting to every node.
    
    Args:
        check_type: 'security_audit', 'performance', or 'connectivity'
    """
    if check_type == "security_audit":
        return ("Diagnostic Complete. Scanned 50 nodes.\n"
                "Result: 48 nodes PASS.\n"
                "Issues found on:\n"
                "- 192.168.1.112 (sshd_config: PermitRootLogin enabled)\n"
                "- 192.168.1.145 (iptables: port 23 open)\n"
                "All other nodes match baseline hash.")
    return "Diagnostic type not recognized or all systems nominal."

@tool
def grep_remote_pattern(ip_address: str, file_path: str, pattern: str) -> str:
    """
    Searches for a specific text pattern in a remote file without downloading the file.
    Returns only the matching lines. Very low bandwidth.
    """
    if ip_address == "192.168.1.112" and "PermitRootLogin" in pattern:
        return "PermitRootLogin yes"
    elif ip_address == "192.168.1.145" and "23" in pattern:
        return "ACCEPT tcp --dport 23"
    return "No matches found or configuration is standard."

@tool
def apply_hot_patch(ip_address: str, service: str, setting_key: str, setting_value: str) -> str:
    """
    Applies a specific configuration change via API without rewriting config files.
    Instant application.
    """
    return f"Applied patch to {ip_address}: Set {setting_key} = {setting_value} for {service}. Success."

@tool
def restart_service_daemon(ip_address: str, service_name: str) -> str:
    """
    Reloads a specific service configuration. Fast and low impact.
    """
    return f"Service {service_name} on {ip_address} reloaded."

@tool
def full_system_reboot(ip_address: str) -> str:
    """
    Initiates a full hardware reboot of the server.
    Takes 5-10 minutes to complete. High availability impact.
    """
    return f"Node {ip_address} is rebooting. Estimated downtime: 600 seconds."

@tool
def analyze_log_file(ip_address: str, log_path: str) -> str:
    """
    Downloads and performs heuristic analysis on log files.
    Very slow due to large dataset processing.
    """
    return "Analysis complete. 1.2GB of logs processed. No critical errors found in recent timeframe."

@tool
def get_network_latency(source_ip: str, target_ip: str) -> str:
    """
    Tests network speed between two nodes.
    """
    return "Average latency: 2ms."

@tool
def ping_node(ip_address: str) -> str:
    """
    Basic connectivity check.
    """
    return f"Reply from {ip_address}: bytes=32 time=1ms TTL=64"