from langchain.tools import tool
import random
import time

# --- System / Setup Tools ---

@tool
def mount_volume(mount_point: str) -> str:
    """
    Mounts a storage volume to the specified system path.
    Args:
        mount_point: The path to mount (e.g., '/mnt/data').
    """
    return f"Successfully mounted volume to {mount_point}. Status: READ-WRITE."

@tool
def unmount_volume(mount_point: str) -> str:
    """
    Unmounts a storage volume.
    Args:
        mount_point: The path to unmount.
    """
    return f"Volume at {mount_point} successfully unmounted."

@tool
def get_volume_usage_stats(mount_point: str) -> str:
    """
    Returns high-level statistics about the volume, including total file count and size.
    Args:
        mount_point: The path to check.
    """
    # Hints at scale: 12 million files.
    return (f"Volume: {mount_point}\nTotal Size: 42 TB\nUsed: 38 TB\n"
            f"File Count: 12,450,000 files\nInode Usage: 88%")

# --- Heavy / Trap Tools (Inefficient for large scale) ---

@tool
def list_all_files_recursive(directory_path: str) -> str:
    """
    [HEAVY OPERATION] deeply scans the directory and returns a text list of ALL file paths found inside, recursively.
    Warning: This returns raw paths only.
    Args:
        directory_path: The root directory to start scanning.
    """
    # Simulate a massive output that would choke a context window if real
    return (f"Scanning {directory_path}...\n"
            "/ops/logs/2010/jan/log_001.txt\n"
            "/ops/logs/2010/jan/log_002.txt\n"
            "... (output truncated, 12,000,000+ lines detected). Use specific filters.")

@tool
def get_dir_contents_detailed(directory_path: str) -> str:
    """
    Lists files in a specific directory with metadata (size, created_date, owner).
    Does NOT recurse.
    Args:
        directory_path: The directory to list.
    """
    return (f"Contents of {directory_path}:\n"
            "-rwxr-xr-x user_a 4KB log_init.sh\n"
            "-rw-rw-r-- user_b 20MB dump.sql\n"
            "drwxr-xr-x admin 0B subdir_old")

@tool
def get_all_system_users_full_dump() -> str:
    """
    [HEAVY OPERATION] Returns a massive JSON-like string containing details of every user account on the system (active and disabled).
    Includes history, metadata, and keys.
    """
    return ("User Dump Start:\n"
            "User: jdoe, ID: 1001, Groups: [admin, wheel], Home: /home/jdoe, Shell: /bin/zsh...\n"
            "User: msmith, ID: 1002, Groups: [staff], Home: /home/msmith, Shell: /bin/bash...\n"
            "... (4,500 users listed)")

@tool
def get_user_info_single(username: str) -> str:
    """
    Fetches detailed profile information for a single user.
    Args:
        username: The username to query.
    """
    return f"User: {username}\nID: 5092\nGroups: staff, remote_access\nStatus: Active"

@tool
def get_file_acl_raw(file_path: str) -> str:
    """
    Retrieves the raw Access Control List (ACL) HEX dump for a specific file.
    Args:
        file_path: The absolute path of the file.
    """
    return f"ACL for {file_path}: 0x755 0000 0000 0000 (Owner: Read/Write, Group: Read, Others: Read)"

@tool
def check_single_user_file_permission(username: str, file_path: str) -> str:
    """
    [SLOW] Verifies if a specific user has Write access to a specific file. 
    Performs a computed check against ACLs.
    Args:
        username: The user to check.
        file_path: The file to check.
    """
    return f"Result: User '{username}' has NO write access to '{file_path}'."

@tool
def read_file_header(file_path: str) -> str:
    """
    Reads the first 1KB of a file to identify its type.
    Args:
        file_path: The file to read.
    """
    return f"Header for {file_path}: [BINARY DATA] ELF 64-bit LSB executable..."

# --- Light / Optimization Tools (Efficient) ---

@tool
def find_files_with_write_bit_set(root_path: str) -> str:
    """
    [OPTIMIZED] Quickly scans the file system index to return only files that have the global or group 'Write' bit set.
    Use this to identify potential risks without scanning every file.
    Args:
        root_path: Where to start the search.
    """
    return (f"Found 23 files with open write permissions in {root_path}:\n"
            "/ops/config/global_settings.conf (World Writable)\n"
            "/ops/tmp/shared_buffer.tmp (Group Writable)\n"
            "... (List complete)")

@tool
def query_files_by_owner(directory_path: str, owner: str) -> str:
    """
    [OPTIMIZED] Returns a list of files owned by a specific user or 'root'.
    Args:
        directory_path: The search path.
        owner: The username (e.g., 'root', 'apache').
    """
    return f"Files in {directory_path} owned by {owner}: 5 files found."

@tool
def analyze_volume_permission_report(mount_point: str) -> str:
    """
    [BATCH] Runs a server-side heuristic analysis to identify standard permission anomalies.
    Returns a summary report of risky users and files.
    Args:
        mount_point: The volume to analyze.
    """
    return ("Analysis Complete:\n"
            "1. Found 150 orphan files with no valid owner.\n"
            "2. Found 12 world-writable directories.\n"
            "3. User 'service_account_legacy' has write access to 400 system files.")

@tool
def batch_check_permissions(file_pattern: str, permission_type: str) -> str:
    """
    [BATCH] Checks a permission type ('read' or 'write') on all files matching a pattern.
    Args:
        file_pattern: glob pattern (e.g., '/mnt/data/*.log').
        permission_type: 'read' or 'write'.
    """
    return f"Checked 500 files matching {file_pattern}. All conform to standard mask 644."

@tool
def get_active_user_groups() -> str:
    """
    Returns a list of user groups currently active in the system.
    """
    return "Groups: root, staff, wheel, docker, accounting, legacy_ops"

# --- Action / Reporting Tools ---

@tool
def update_file_access_mode(file_path: str, mode: str) -> str:
    """
    Changes the permission mode of a file (chmod).
    Args:
        file_path: The file to modify.
        mode: The octal mode (e.g., '755').
    """
    return f"File {file_path} permissions updated to {mode}."

@tool
def log_audit_finding(finding_text: str, severity: str) -> str:
    """
    Writes a finding to the official audit log.
    Args:
        finding_text: Description of the issue.
        severity: 'LOW', 'MEDIUM', 'HIGH'.
    """
    return "Audit entry logged successfully."