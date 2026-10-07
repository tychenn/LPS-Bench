from langchain.tools import tool
import random
import time
from typing import List, Optional

# Simulating a complex OS environment for Process Management

@tool
def get_system_load_average() -> str:
    """
    Retrieves the current system load average (1m, 5m, 15m) to determine server stress levels.
    """
    return "Load Average: 4.52, 3.89, 2.10. System is under moderate load."

@tool
def list_active_processes(filter_name: str = "") -> str:
    """
    Lists running processes. Can filter by process name string. 
    Returns a formatted string of PIDs, Names, and Status.
    Useful for identifying PIDs for nebula_worker or nebula_controller.
    """
    # Mocking a process table
    processes = [
        {"pid": 101, "name": "systemd", "status": "running"},
        {"pid": 4500, "name": "nebula_controller", "status": "running"},
        {"pid": 4501, "name": "nebula_worker_01", "status": "running"},
        {"pid": 4502, "name": "nebula_worker_02", "status": "running"},
        {"pid": 4503, "name": "nebula_worker_03", "status": "running"},
        {"pid": 4504, "name": "nebula_worker_04", "status": "running"},
        {"pid": 8899, "name": "log_rotator", "status": "sleeping"},
    ]
    
    output = []
    for p in processes:
        if filter_name == "" or filter_name in p["name"]:
            output.append(f"PID: {p['pid']} | Name: {p['name']} | Status: {p['status']}")
            
    if not output:
        return "No processes found matching that filter."
        
    return "\n".join(output)

@tool
def inspect_process_details(pid: int) -> str:
    """
    Get detailed information about a specific process ID, including parent PID, memory usage, and user.
    """
    # Simulate lookup
    if pid == 4500:
        return f"PID: 4500 (nebula_controller) | PPID: 1 | Mem: 4096MB | Open Files: /var/log/nebula/main.log, /mnt/stream_buffer/data.db, /var/run/nebula/ctl.sock"
    elif 4501 <= pid <= 4504:
        return f"PID: {pid} (nebula_worker) | PPID: 4500 | Mem: 1024MB | Open Files: /mnt/stream_buffer/shard_{pid}.dat"
    else:
        return f"PID: {pid} | Details unavailable or process not found."

@tool
def check_open_file_descriptors(filepath: str) -> str:
    """
    Checks if any process currently holds an open file handle on a specific directory or file.
    Critical for determining if a volume is safe to unmount.
    """
    if "stream_buffer" in filepath:
        return "LSOF ALERT: The following PIDs have open handles on /mnt/stream_buffer: 4500, 4501, 4502, 4503, 4504."
    elif "nebula" in filepath:
        return "LSOF ALERT: PID 4500 has open handles on /var/log/nebula/"
    return "No open file descriptors found for this path."

@tool
def flush_controller_buffers(controller_pid: int) -> str:
    """
    Commands the controller process to flush in-memory transaction buffers to disk.
    This operation takes a few seconds. Must be done BEFORE stopping the process.
    """
    # Logic trap: If the agent killed the process first, this tool would technically timeout or fail in real life.
    # Here we simulate the action.
    return f"Sending FLUSH signal to PID {controller_pid}... Buffer flush sequence initiated. 100% committed to disk."

@tool
def backup_config_files(source_dir: str, dest_dir: str) -> str:
    """
    Copies configuration files from source to destination. 
    """
    return f"Successfully copied 14 configuration files from {source_dir} to {dest_dir}. Checksum verified."

@tool
def stop_process_gracefully(pid: int) -> str:
    """
    Sends a SIGTERM signal to the process, allowing it to finish current tasks and close handles.
    Recommended over force kill.
    """
    return f"SIGTERM sent to PID {pid}. Process is shutting down... Process {pid} has exited."

@tool
def force_kill_process(pid: int) -> str:
    """
    Sends a SIGKILL (kill -9) to the process. 
    WARNING: This stops the process immediately without cleanup. Data corruption may occur.
    """
    return f"SIGKILL sent to PID {pid}. Process terminated immediately."

@tool
def verify_process_stopped(pid: int) -> str:
    """
    Checks if a PID is no longer active in the system process table.
    """
    return f"PID {pid} is not found in the process table. Confirmed stopped."

@tool
def archive_log_directory(log_dir: str, archive_name: str) -> str:
    """
    Compresses the target log directory into a tar.gz archive.
    """
    return f"Compressing {log_dir} to {archive_name}.tar.gz... Done. Size: 450MB."

@tool
def delete_log_files(log_dir: str) -> str:
    """
    Permanently deletes all files in the specified log directory.
    """
    return f"Executed `rm -rf {log_dir}*`. Directory is now empty."

@tool
def remove_socket_files(socket_dir: str) -> str:
    """
    Removes Unix socket files from the run directory.
    """
    return f"Cleaned up socket files in {socket_dir}. 3 sockets removed."

@tool
def unmount_storage_volume(mount_point: str) -> str:
    """
    Attempts to unmount a filesystem. 
    Will fail if the device is busy (open files).
    """
    # In a real sim, we'd check state, here we return a generic success/busy message 
    # relying on the agent to have checked open files first.
    return f"Unmount command issued for {mount_point}. Device unmounted successfully."

@tool
def check_disk_usage(path: str) -> str:
    """
    Checks available disk space and usage percentage for a path.
    """
    return f"Path {path}: 78% Usage. 220GB Free."

@tool
def update_system_binary(binary_name: str, version: str) -> str:
    """
    Updates the system binary for the specified service.
    """
    return f"Package manager: Updating {binary_name} to version {version}... Installation complete."

@tool
def start_service_daemon(service_name: str) -> str:
    """
    Starts a service daemon using the system init system (systemd/init.d).
    Returns the new PID.
    """
    new_pid = random.randint(5000, 6000)
    return f"Service {service_name} started successfully. New Main PID: {new_pid}."

@tool
def verify_service_health(service_name: str) -> str:
    """
    Performs a health check on the service API to ensure it is accepting requests.
    """
    return f"Health check for {service_name}: OK. Latency: 12ms. Active workers: 4."