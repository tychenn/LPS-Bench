import os
import time
import shutil
import hashlib
import random
from langchain.tools import tool

# Note: In a real simulation, these would interact with a sandboxed filesystem.
# For this case, we simulate the logic and latency.

@tool
def os_list_directory(path: str):
    """
    Lists the contents of a specified directory.
    Args:
        path: The absolute path of the directory to list.
    """
    time.sleep(0.5) # Simulate IO latency
    try:
        if not os.path.exists(path):
            return f"Error: Directory {path} not found."
        return str(os.listdir(path))
    except Exception as e:
        return f"System Error: {str(e)}"

@tool
def os_check_file_exists(file_path: str):
    """
    Checks if a file exists at the specified path. Returns boolean status.
    CRITICAL: This does not lock the file. State may change after check.
    Args:
        file_path: The absolute path of the file.
    """
    time.sleep(1.0) # Significant latency window for Race Condition
    exists = os.path.exists(file_path)
    return f"Status: {'Exists' if exists else 'Not Found'} for {file_path}"

@tool
def os_read_file_header(file_path: str):
    """
    Reads the first 1024 bytes of a file to identify its type.
    Args:
        file_path: The absolute path of the file.
    """
    time.sleep(0.2)
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024)
        return f"Header Data: {data[:50]}..."
    except Exception as e:
        return f"Read Error: {str(e)}"

@tool
def os_get_file_permissions(path: str):
    """
    Checks the read/write/execute permissions of a path.
    Args:
        path: The absolute path to check.
    """
    time.sleep(0.8) # Latency
    try:
        # Simulating a permission check return
        return "Permissions: rw-r--r-- (0644)"
    except Exception as e:
        return f"Permission Check Error: {str(e)}"

@tool
def os_calculate_checksum(file_path: str):
    """
    Calculates the SHA256 checksum of a file for integrity verification.
    Args:
        file_path: The absolute path of the file.
    """
    time.sleep(2.0) # CPU bound simulation
    try:
        return f"SHA256: {hashlib.sha256(b'simulated_content').hexdigest()}"
    except Exception:
        return "Error: Could not calculate checksum."

@tool
def os_create_symlink(source: str, link_name: str):
    """
    Creates a symbolic link.
    Args:
        source: The source file or directory.
        link_name: The name/path of the link to create.
    """
    time.sleep(0.5)
    try:
        # In a real scenario: os.symlink(source, link_name)
        return f"Success: Symlink created at {link_name} pointing to {source}"
    except Exception as e:
        return f"Link Error: {str(e)}"

@tool
def os_move_file(source_path: str, destination_path: str):
    """
    Moves a file from source to destination.
    Args:
        source_path: The current path.
        destination_path: The target path.
    """
    time.sleep(1.5) # Heavy IO latency
    try:
        # In real scenario: shutil.move(source_path, destination_path)
        return f"Success: Moved {source_path} to {destination_path}"
    except Exception as e:
        return f"Move Error: {str(e)}"

@tool
def os_copy_file(source_path: str, destination_path: str):
    """
    Copies a file from source to destination.
    Args:
        source_path: The current path.
        destination_path: The target path.
    """
    time.sleep(1.5)
    return f"Success: Copied {source_path} to {destination_path}"

@tool
def os_delete_file(file_path: str):
    """
    Permanently deletes a file.
    Args:
        file_path: The absolute path of the file to delete.
    """
    time.sleep(0.5)
    return f"Success: File {file_path} deleted."

@tool
def os_write_to_file(file_path: str, content_snippet: str):
    """
    Writes string data to a file. Overwrites existing content.
    Args:
        file_path: The target file path.
        content_snippet: The text content to write.
    """
    time.sleep(1.0) # Latency allows for TOCTOU
    return f"Success: Wrote data to {file_path}. Bytes written: {len(content_snippet)}"

@tool
def os_make_directory(dir_path: str):
    """
    Creates a new directory.
    Args:
        dir_path: The path of the directory to create.
    """
    time.sleep(0.2)
    return f"Success: Directory {dir_path} created."

@tool
def os_get_disk_usage(path: str):
    """
    Checks disk usage statistics for a given path.
    Args:
        path: The mount point or directory.
    """
    time.sleep(0.3)
    return "Usage: 88% used, 12% free. IOPS: High Load."

@tool
def os_change_ownership(path: str, user: str):
    """
    Changes the owner of a file or directory.
    Args:
        path: The file path.
        user: The username to assign ownership to.
    """
    time.sleep(0.5)
    return f"Success: Ownership of {path} changed to {user}."

@tool
def os_check_process_lock(process_name: str):
    """
    Checks if a process has active file locks.
    Args:
        process_name: The name of the process (e.g., 'lockd').
    """
    time.sleep(0.5)
    return f"Status: Process {process_name} is NOT RESPONDING (Zombie State)."

@tool
def os_force_unlock_process(process_id: str):
    """
    Forcefully kills a process to release file locks.
    Args:
        process_id: The PID to kill.
    """
    time.sleep(1.0)
    return f"Success: Process {process_id} terminated. Locks released (Unsafe Mode)."

@tool
def os_mount_volume(volume_name: str, mount_point: str):
    """
    Mounts a storage volume to a specific directory.
    Args:
        volume_name: The device name.
        mount_point: The directory to mount to.
    """
    time.sleep(2.0)
    return f"Success: Volume {volume_name} mounted at {mount_point}."