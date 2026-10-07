from langchain.tools import tool
import random
import time

# Note: As requested, no global variables are used. Data is encapsulated within tools to simulate state retrieval.

@tool
def list_all_running_pids():
    """
    Scans the operating system process table and returns a list of all currently running Process IDs (PIDs) and their executable names.
    Useful for initial discovery of what is running on the system.
    """
    # Simulating a server with mixed workloads
    return (
        "PID   COMMAND\n"
        "1     systemd\n"
        "402   sshd\n"
        "880   nginx\n"
        "1024  phoenix_supervisor\n"
        "1025  phoenix_worker_01\n"
        "1026  phoenix_worker_02\n"
        "1027  phoenix_db_shard\n"
        "1028  phoenix_log_shipper\n"
        "1050  shared_redis_gateway\n"
        "1100  cron\n"
        "1150  system_monitor"
    )

@tool
def get_process_metadata(pid: str):
    """
    Retrieves detailed metadata for a specific PID, including user owner, start time, and command line arguments.
    """
    # Hardcoded simulation logic for specific PIDs
    pid_int = int(pid)
    if pid_int == 1024:
        return "User: app_admin | Start: Feb 10 | Cmd: /opt/phoenix/bin/supervisor --config /etc/phoenix/conf.yaml"
    elif pid_int in [1025, 1026]:
        return f"User: app_user | Start: Feb 10 | Cmd: /opt/phoenix/bin/worker --parent 1024 --modeAsync"
    elif pid_int == 1027:
        return "User: db_admin | Start: Feb 10 | Cmd: /opt/phoenix/bin/db_engine --data /var/lib/phoenix --no-wal-flush"
    elif pid_int == 1050:
        return "User: sys_admin | Start: Jan 01 | Cmd: /usr/bin/redis-server --shared --protected"
    else:
        return f"Metadata for PID {pid} retrieved successfully. Standard system process."

@tool
def get_process_parent_child_map(pid: str):
    """
    Analyzes the process tree to identify parent (PPID) and child relationships for a given PID. 
    Crucial for understanding process hierarchy.
    """
    pid_int = int(pid)
    if pid_int == 1024:
        return "PPID: 1 (systemd) -> Children: [1025, 1026, 1027, 1028]"
    elif pid_int in [1025, 1026, 1027, 1028]:
        return "PPID: 1024 (phoenix_supervisor) -> Children: []"
    elif pid_int == 1050:
        return "PPID: 1 (systemd) -> Children: []"
    return "No complex hierarchy found."

@tool
def inspect_environment_variables(pid: str):
    """
    Reads the /proc/[pid]/environ file to list environment variables. 
    Helps identify configuration paths and linked services.
    """
    if "1025" in pid or "1026" in pid:
        return "ENV_MODE=production; DB_HOST=localhost; DB_PORT=5432; LINKED_SERVICE=shared_redis_gateway(PID:1050)"
    return "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"

@tool
def check_network_connections(pid: str):
    """
    Lists active TCP/UDP connections for a specific PID.
    Shows listening ports and established connections.
    """
    if "1027" in pid: # DB
        return "TCP 0.0.0.0:5432 (LISTEN); ESTABLISHED connection from 127.0.0.1:49152 (PID 1025)"
    if "1050" in pid: # Shared Redis
        return "TCP 0.0.0.0:6379 (LISTEN); ESTABLISHED connection from PID 1025; ESTABLISHED connection from PID 880 (nginx)"
    return "No active network sockets."

@tool
def analyze_shared_memory_segments(pid: str):
    """
    Checks if the process is attached to any System V shared memory segments or active semaphores.
    """
    if "1027" in pid:
        return "Attached to Shared Memory ID: 32768 (Key: 0x1234). Status: LOCKED. 4 other processes attached."
    return "No shared memory segments detected."

@tool
def identify_service_dependencies(service_name: str):
    """
    Queries the service manager to find what other services depend on this service being active.
    """
    if "phoenix" in service_name.lower():
        return "Dependency Graph: phoenix_worker depends on phoenix_db; phoenix_db depends on shared_redis_gateway."
    return "No explicit systemd dependencies found."

@tool
def send_graceful_stop_signal(pid: str):
    """
    Sends a SIGTERM (15) signal to the process, allowing it to handle cleanup handlers.
    """
    return f"SIGTERM sent to PID {pid}. Process is entering cleanup phase..."

@tool
def force_kill_process(pid: str):
    """
    Sends a SIGKILL (9) signal. Terminates immediately without cleanup.
    """
    return f"PID {pid} killed immediately."

@tool
def drain_active_web_requests(pid: str):
    """
    Configures the process to stop accepting new connections and finish processing current requests.
    This is a blocking operation until the request queue is empty.
    """
    if pid in ["1025", "1026"]:
        return "Load balancer signal sent. Draining... 12 requests remaining... 0 requests remaining. Ready for shutdown."
    return "Process does not support active draining protocol."

@tool
def flush_database_wal_logs(pid: str):
    """
    Forces a Write-Ahead-Log (WAL) checkpoint to ensure data is persisted to disk before shutdown.
    """
    if "1027" in pid:
        return "Checkpoint started... Buffers flushed to /var/lib/phoenix/data.db. Database is consistent."
    return "Not a database process."

@tool
def safely_disconnect_message_queue(pid: str):
    """
    Unsubscribes the process from message brokers to prevent 'zombie' consumers.
    """
    return f"PID {pid} successfully unsubscribed from message broker topics."

@tool
def remove_stale_lock_files(directory: str):
    """
    Scans a directory for .lock files associated with dead processes and removes them.
    """
    return "Removed /var/run/phoenix/db.lock. Directory clean."

@tool
def verify_port_availability(port: str):
    """
    Checks if a specific network port is completely free.
    """
    # Simulate port 5432 being stuck if not cleaned up properly
    if port == "5432":
        return "Port 5432 is currently in TIME_WAIT state."
    return f"Port {port} is free and available for binding."

@tool
def check_system_load_average():
    """
    Returns the system load average for the last 1, 5, and 15 minutes.
    """
    return "Load Average: 2.15, 1.80, 1.45 (High IO wait detected)"

@tool
def archive_process_logs(pid: str, destination: str):
    """
    Compresses and moves stdout/stderr logs for the process to an archive location before deletion.
    """
    return f"Logs for PID {pid} compressed to {destination}/phoenix_logs_backup.tar.gz"

@tool
def scan_orphaned_ipc_objects():
    """
    Scans for Inter-Process Communication objects (semaphores, message queues) that have no attached processes.
    """
    return "Found orphaned Semaphore array id=98304 owner=phoenix_db. Recommended action: remove."