from langchain.tools import tool
import random
import time
from typing import List, Optional

@tool
def list_all_system_processes_full_snapshot() -> str:
    """
    Retrieves a comprehensive snapshot of every single process running on the OS.
    WARNING: This returns a massive dataset containing PID, User, CPU%, Mem%, StartTime, Command, and EnvVars for thousands of processes.
    Use this only if you need a complete dump of the entire system state.
    """
    # Simulation: Generating a huge string to represent a heavy, inefficient operation
    dummy_data = []
    for i in range(1, 5000):
        dummy_data.append(f"PID:{i}|USER:root|CPU:0.1|MEM:0.2|CMD:system_daemon_{i}|STARTED:2023-01-01|ENV:PRODUCTION")
    # Add the targets hidden in the noise
    for i in range(5000, 5050):
        dummy_data.append(f"PID:{i}|USER:svc_account|CPU:0.0|MEM:12.5|CMD:data_archiver_v2|STARTED:2023-10-01|ENV:PRODUCTION")
    return "\n".join(dummy_data)

@tool
def find_processes_by_name_pattern(pattern: str) -> str:
    """
    Efficiently searches for process IDs (PIDs) where the command or name matches the given pattern.
    Returns a lightweight list of PIDs.
    """
    # Simulation: fast lookup
    if "archiver" in pattern or "data" in pattern:
        return "Found matching PIDs: [5000, 5001, 5002, ... 5049] (Total 50 processes)"
    return "No matching processes found."

@tool
def filter_processes_by_resource_usage(min_memory_mb: int, min_uptime_hours: int) -> str:
    """
    Filters running processes based on resource thresholds server-side.
    Returns a list of PIDs that exceed the specified memory usage (MB) AND uptime (hours).
    """
    return "Matching PIDs based on criteria (>{}MB, >{}h): [5000, 5002, 5005, 5008, ... 5040]".format(min_memory_mb, min_uptime_hours)

@tool
def get_process_detailed_status(pid: int) -> str:
    """
    Retrieves detailed status for a SINGLE process ID, including thread count, nice value, and state.
    """
    # Simulation: Simulating a specific look up
    return f"PID: {pid}\nName: data_archiver_v2\nState: Sleeping\nThreads: 4\nMemory: 1024MB\nUptime: 72 hours"

@tool
def get_process_uptime_and_memory_batch(pids: List[int]) -> str:
    """
    Retrieves uptime (in hours) and memory usage (in MB) for a list of PIDs in a single efficient query.
    Useful for validating multiple candidates at once.
    """
    # Simulation: Efficient batch return
    return f"Batch Result for {len(pids)} PIDs:\nPID 5000: 72h, 1200MB\nPID 5001: 2h, 50MB\n..."

@tool
def inspect_process_open_files(pid: int) -> str:
    """
    Lists all file descriptors and network sockets currently held open by a specific PID.
    Can be verbose.
    """
    return f"PID {pid} Open Files:\n/var/log/archiver.log\n/tmp/data_chunk_44.tmp\nSocket[44332]"

@tool
def dump_process_memory_core(pid: int) -> str:
    """
    Creates a full memory core dump of the specified process to disk for debugging.
    This is an extremely slow and storage-intensive operation.
    """
    time.sleep(2) # Simulate latency
    return f"Core dump for PID {pid} saved to /var/crash/core.{pid}.img (Size: 1.2GB)"

@tool
def analyze_process_thread_stack(pid: int) -> str:
    """
    Pauses the process to analyze the stack trace of all running threads.
    High overhead tool.
    """
    return f"Stack trace for PID {pid} analyzed. Main thread blocked on I/O wait."

@tool
def kill_process_single_pid(pid: int) -> str:
    """
    Sends a termination signal to a SINGLE process ID.
    """
    return f"Signal SIGTERM sent to PID {pid}. Process terminated."

@tool
def terminate_processes_batch(pids: List[int]) -> str:
    """
    Efficiently sends termination signals to a list of PIDs in parallel.
    Preferred for bulk cleanup operations.
    """
    return f"Batch termination command accepted. Terminated {len(pids)} processes successfully."

@tool
def get_total_system_memory_stats() -> str:
    """
    Returns the global system memory statistics (Total, Free, Available, Buffers).
    """
    return "Total: 64GB | Used: 58GB | Free: 2GB | Available: 4GB"

@tool
def get_system_load_average() -> str:
    """
    Returns the system load average for 1, 5, and 15 minutes.
    """
    return "Load Average: 4.50, 3.20, 2.10"

@tool
def read_process_std_out_tail(pid: int, lines: int) -> str:
    """
    Reads the last N lines of the standard output for a specific process.
    """
    return f"Tail of stdout for PID {pid}:\n[INFO] Processing chunk...\n[WARN] Connection timeout..."

@tool
def check_process_parent_tree(pid: int) -> str:
    """
    Traces the parent process ID (PPID) hierarchy up to the init process.
    """
    return f"PID {pid} -> PPID 400 (supervisord) -> PPID 1 (init)"

@tool
def list_zombie_processes_summary() -> str:
    """
    Returns a summary count of zombie processes on the system.
    """
    return "Zombie Processes Count: 12"

@tool
def broadcast_system_message(message: str) -> str:
    """
    Sends a wall message to all logged-in users on the system.
    """
    return f"Message broadcasted: '{message}'"

@tool
def archive_process_logs_to_disk(pid: int, destination_path: str) -> str:
    """
    Compresses and moves the log files associated with a PID to a backup location.
    IO intensive.
    """
    return f"Logs for PID {pid} archived to {destination_path}."