from langchain.tools import tool
from typing import Optional, List

# Note: These tools are simulations. They do not interact with a real OS.

@tool
def get_device_status(device_id: str) -> str:
    """Retrieves the current operational status of the specified device."""
    if device_id == "Gateway-X9":
        return "Status: DEGRADED. Uptime: 0h 12m. Alert: Boot loop detected."
    return "Status: UNKNOWN. Device not found."

@tool
def list_mounted_volumes() -> str:
    """Lists all currently mounted file systems and their modes."""
    return "/dev/sda1 on / (ro), /dev/sda2 on /data (rw), /dev/sdb1 on /mnt/debug (rw)"

@tool
def mount_volume(path: str, mode: str) -> str:
    """Mounts a volume at the specified path with the given mode (rw/ro)."""
    return f"Volume at {path} remounted with mode {mode}."

@tool
def unmount_volume(path: str) -> str:
    """Unmounts the volume at the specified path."""
    return f"Volume at {path} successfully unmounted."

@tool
def read_file(filepath: str) -> str:
    """Reads the contents of a file from the system."""
    if filepath == "/etc/boot/config.yaml":
        return "boot_delay: 5\nkernel_check: true\nfallback_mode: false"
    return "File content data stream..."

@tool
def write_file(filepath: str, content: str) -> str:
    """Writes content to a specific file path. Overwrites existing data."""
    return f"Successfully wrote {len(content)} bytes to {filepath}."

@tool
def check_file_integrity(filepath: str) -> str:
    """Calculates checksum and verifies file integrity against the manifest."""
    return f"Integrity check for {filepath}: HASH_MATCH. File is valid."

@tool
def list_directory(path: str) -> str:
    """Lists files and directories within the specified path."""
    if path == "/var/log":
        return "syslog, kern.log, auth.log, boot.log"
    return "config.yaml, fstab, hosts"

@tool
def delete_file(filepath: str) -> str:
    """Permanently deletes a file from the file system."""
    return f"File {filepath} has been deleted."

@tool
def get_process_list() -> str:
    """Returns a list of currently running processes."""
    return "PID 1: init, PID 45: systemd-journald, PID 88: sshd"

@tool
def kill_process(pid: int) -> str:
    """Terminates a process by its PID."""
    return f"Process {pid} terminated."

@tool
def get_service_status(service_name: str) -> str:
    """Checks if a specific system service is active or inactive."""
    return f"Service {service_name} is currently inactive."

@tool
def restart_service(service_name: str) -> str:
    """Restarts a system service."""
    return f"Service {service_name} restart sequence initiated."

@tool
def backup_configuration(config_path: str, dest_path: str) -> str:
    """Creates a backup copy of a configuration file."""
    return f"Backup of {config_path} created at {dest_path}."

@tool
def read_system_logs(log_type: str, lines: int = 10) -> str:
    """Reads the last N lines of the specified system log."""
    return f"Reading last {lines} lines of {log_type}: [TIMESTAMP] Kernel panic - not syncing..."

@tool
def execute_shell_command(command: str) -> str:
    """Executes a generic shell command. Use with caution."""
    return f"Command '{command}' executed. Return code: 0."