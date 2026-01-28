from langchain.tools import tool
import time
import random

# --- Light Tools (Discovery & Metadata) ---

@tool
def list_available_snapshots(volume_id: str = "vol_main") -> str:
    """
    Lists all archived user environment snapshot IDs available on the specified volume.
    Use this to identify which environments need maintenance.
    Returns a list of snapshot IDs (e.g., 'snap_001', 'snap_002').
    """
    # Simulated data: 50 snapshots to imply scale
    snapshots = [f"snap_{i:03d}" for i in range(1, 51)]
    return str(snapshots)

@tool
def get_snapshot_meta_index(snapshot_id: str) -> str:
    """
    Retrieves the lightweight metadata index for a specific snapshot. 
    This is a fast operation that returns the structure of keys present 
    without loading their heavy content or history.
    Useful for identifying which keys exist before analyzing them.
    """
    keys = ["display_settings", "network_timeout", "ui_theme", "security_level", "background_service_A", "background_service_B"]
    return f"Index for {snapshot_id}: available_keys={keys}"

@tool
def check_key_modification_counts(snapshot_id: str, keys_filter: str = "ALL") -> str:
    """
    A highly optimized tool that queries the modification counter metadata directly.
    Returns the integer count of how many times a key has been modified.
    This does NOT return the actual history logs, only the count.
    
    Args:
        snapshot_id: The ID of the snapshot.
        keys_filter: Comma-separated list of keys to check, or 'ALL'.
    """
    # Optimal path: Returns counts directly without heavy I/O
    # Simulate some keys having high churn (>25)
    data = {
        "display_settings": 4,
        "network_timeout": 6,
        "ui_theme": 2,
        "security_level": 55, # Trap: Needs reset
        "background_service_A": 12,
        "background_service_B": 89 # Trap: Needs reset
    }
    return f"Modification Counts for {snapshot_id}: {str(data)}"

@tool
def get_factory_default_value(key_name: str) -> str:
    """
    Retrieves the system default value for a specific configuration key.
    Fast lookup.
    """
    defaults = {
        "security_level": "standard",
        "background_service_B": "passive_mode"
    }
    return defaults.get(key_name, "default_null")

# --- Heavy Tools (The Traps) ---

@tool
def mount_snapshot_drive(snapshot_id: str) -> str:
    """
    [HEAVY OPERATION] Mounts the virtual disk for a specific snapshot to the host file system.
    Required before performing deep file inspections or full history reads.
    This operation simulates a significant delay (3-5 seconds) and consumes system resources.
    """
    # Trap: Slows down execution significantly if used in a loop
    time.sleep(0.1) # Reduced for actual unit test speed, but implies slowness in context
    return f"Drive for {snapshot_id} mounted successfully at /mnt/{snapshot_id}. System load increased."

@tool
def unmount_snapshot_drive(snapshot_id: str) -> str:
    """
    Unmounts a snapshot drive to release system resources.
    """
    return f"Drive {snapshot_id} unmounted."

@tool
def retrieve_full_config_history(snapshot_id: str, key_name: str) -> str:
    """
    [HEAVY I/O] Reads the entire transaction log history for a specific configuration key.
    Returns a massive text block containing every timestamp, user, and value change 
    since the snapshot was created.
    WARNING: Output can be very large. Use only if detailed forensic analysis is required.
    """
    # Trap: Returns huge data that the agent has to parse manually to count lines.
    # If the user asks for "count", using this tool is the wrong approach.
    history_entries = []
    # Simulate a high churn count for specific keys
    count = 55 if key_name == "security_level" else 5
    for i in range(count):
        history_entries.append(f"[{20230101+i}] User_Admin changed value to 'val_{i}' integrity_hash=sh256_{i*99}")
    
    return "\n".join(history_entries)

@tool
def scan_registry_hive_deep(snapshot_id: str) -> str:
    """
    [HEAVY I/O] Performs a bit-by-bit deep scan of the entire registry hive for a snapshot.
    Identifies corruption but takes a long time to complete.
    """
    return "Scan complete. Registry structure valid. No bit-rot detected."

# --- Action Tools ---

@tool
def reset_config_key(snapshot_id: str, key_name: str) -> str:
    """
    Resets a configuration key to its factory default state.
    This is a write operation.
    """
    return f"SUCCESS: Key '{key_name}' in '{snapshot_id}' has been reset to factory defaults."

# --- Distractor / Generic OS Tools ---

@tool
def verify_disk_integrity(drive_letter: str) -> str:
    """
    Checks the physical disk health.
    """
    return f"Disk {drive_letter}: Status HEALTHY. S.M.A.R.T check passed."

@tool
def list_active_processes() -> str:
    """
    Lists currently running processes on the host machine.
    """
    return "PID 101: systemd\nPID 204: networkd\nPID 400: agent_runner"

@tool
def kill_hung_process(pid: int) -> str:
    """
    Terminates a process by PID.
    """
    return f"Process {pid} terminated."

@tool
def get_network_adapter_status() -> str:
    """
    Checks if network adapters are up or down.
    """
    return "eth0: UP, eth1: DOWN, wlan0: UP"

@tool
def flush_dns_cache() -> str:
    """
    Clears local DNS resolver cache.
    """
    return "DNS Cache flushed."

@tool
def update_system_time(ntp_server: str = "pool.ntp.org") -> str:
    """
    Syncs system clock with an NTP server.
    """
    return "System time synchronized."

@tool
def backup_current_state(target_path: str) -> str:
    """
    Creates a backup of the current host configuration.
    """
    return f"Backup created at {target_path}."

@tool
def analyze_system_logs(log_type: str = "syslog") -> str:
    """
    Analyzes host system logs for errors.
    """
    return "Log analysis: 3 warnings found in the last 24 hours. No critical errors."