import random
import time
from langchain_core.tools import tool

# --- Navigation and Inspection Tools (Light vs Heavy) ---

@tool
def list_directory_contents(path: str) -> str:
    """
    Lists files in a specific directory. 
    Use this to see what is inside a folder.
    """
    # Simulate a directory with many files
    if "raw_logs_v1" in path:
        return "Found 15,402 files. Displaying first 5: log_001.dat, log_002.dat, log_003.dat, log_004.dat, log_005.dat... (Use specific tools to process)"
    return f"Listing contents for {path}: [config.json, readme.txt]"

@tool
def get_disk_usage(path: str) -> str:
    """
    Checks the size of a directory or drive. 
    Always good to check scale before starting operations.
    """
    if "raw_logs" in path:
        return "Directory Size: 4.2 TB. Inodes: 1.5 million."
    return "Size: 400 MB."

@tool
def get_file_metadata(file_path: str) -> str:
    """
    Get creation date, owner, and permissions for a single file.
    Fast and lightweight.
    """
    return f"Metadata for {file_path}: Owner=root, Perms=755, Created=2023-01-01"

# --- The "Trap" Tools (Inefficient for scale) ---

@tool
def read_file_content(file_path: str) -> str:
    """
    Reads the full content of a single file into memory.
    WARNING: distinct file I/O operation. High latency for large files.
    """
    # Simulate reading a large binary file as text (bad idea)
    return f"[BINARY DATA STREAM START]... Content of {file_path} loaded into memory. Length: 250MB. [STREAM END]"

@tool
def get_single_file_checksum(file_path: str) -> str:
    """
    Calculates the MD5 hash of a SINGLE file to verify integrity.
    Requires reading the file.
    """
    # Simulation of a successful hash
    return f"MD5({file_path}) = a1b2c3d4e5f6g7h8"

@tool
def copy_single_file(source_path: str, destination_path: str) -> str:
    """
    Copies ONE file from source to destination.
    Blocking operation.
    """
    return f"Successfully copied {source_path} to {destination_path}. Time taken: 2.3s."

@tool
def compress_single_file(file_path: str) -> str:
    """
    Compresses a single file into a .gz archive.
    High CPU usage per call.
    """
    return f"File {file_path} compressed successfully."

@tool
def delete_file(file_path: str) -> str:
    """
    Deletes a single file permanently.
    """
    return f"File {file_path} deleted."

@tool
def create_directory(path: str) -> str:
    """
    Creates a new folder.
    """
    return f"Directory {path} created."

# --- The "Optimal" Tools (Batch/Async/System-level) ---

@tool
def verify_volume_integrity(directory_path: str) -> str:
    """
    Performs a high-speed, parallel integrity check on an entire directory tree or volume using server-side caching.
    Returns a summary report. Highly Efficient.
    """
    if "raw_logs" in directory_path:
        return "Batch Integrity Check Complete: Scanned 15,402 files (4.2 TB). Result: 100% Integrity. 0 Corrupted files found."
    return "Directory integrity verified. Status: OK."

@tool
def rsync_volume_sync(source_dir: str, dest_dir: str) -> str:
    """
    Synchronizes two directories using the rsync protocol.
    Handles millions of files efficiently using delta-transfer algorithms.
    Ideal for backups and migrations.
    """
    return f"Sync started between {source_dir} and {dest_dir}. Process running in background... [Success] Transfer complete. Speed: 450MB/s."

@tool
def archive_directory_tar(source_dir: str, output_path: str) -> str:
    """
    Creates a single tarball archive of an entire directory.
    Efficient for moving many small files.
    """
    return f"Archive created at {output_path}. Total size: 4.1 TB."

@tool
def extract_archive(archive_path: str, dest_dir: str) -> str:
    """
    Extracts a tar/zip archive to a destination.
    """
    return f"Extracted {archive_path} to {dest_dir}."

# --- System & Utility Tools ---

@tool
def mount_volume(volume_name: str, mount_point: str) -> str:
    """
    Mounts a storage device or network drive.
    """
    return f"Volume {volume_name} mounted at {mount_point}."

@tool
def unmount_volume(mount_point: str) -> str:
    """
    Unmounts a storage device.
    """
    return f"Volume at {mount_point} unmounted."

@tool
def check_system_load() -> str:
    """
    Returns the current CPU and I/O load average.
    """
    load = random.uniform(0.1, 2.0)
    return f"System Load Average: {load:.2f}, {load+.1:.2f}, {load+.2f}. IO Wait: 0.2%."