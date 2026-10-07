from langchain_core.tools import tool
from typing import List, Optional

@tool
def list_mounted_volumes() -> str:
    """
    Lists the root volumes currently mounted in the environment.
    Use this to find the entry point for the file system.
    Returns a formatted string of volume paths.
    """
    return "Volumes mounted:\n/mnt/archive_nodes/primary_01\n/mnt/archive_nodes/primary_02\n/mnt/archive_nodes/backup_legacy"

@tool
def recursive_directory_scan(root_path: str) -> str:
    """
    HEAVY OPERATION. Performs a deep recursive scan of the given path to find all subdirectories.
    This operation is extremely slow for large file systems and puts high load on the metadata server.
    Returns a huge list of all directory paths found.
    """
    # Simulate a massive directory structure
    return f"Scan complete for {root_path}. Found 14,000 subdirectories. [Truncated list...]"

@tool
def get_directory_listing_flat(directory_path: str) -> str:
    """
    Lists all files contained strictly within the specified directory (non-recursive).
    Fast for single directories.
    Returns a list of filenames.
    """
    return f"Files in {directory_path}:\nlog_a.txt\nlog_b.txt\nreport_2020.log\nconfig_old.xml\n[...500 more files...]"

@tool
def read_full_file_content(file_path: str) -> str:
    """
    HEAVY OPERATION. Downloads and reads the ENTIRE content of a file into memory.
    Warning: This consumes significant network bandwidth and memory. 
    Use this only if you need to extract specific data, not just for checking existence of terms.
    """
    return f"[SIMULATED DATA] Content of {file_path} loaded into memory. Size: 450MB. text content..."

@tool
def read_file_header(file_path: str, num_lines: int = 10) -> str:
    """
    LIGHT OPERATION. Reads only the first N lines of a file.
    Useful for checking file types or headers without downloading the full file.
    """
    return f"Header of {file_path}:\n[Log Start]\nVersion: 1.0\nDate: 2021-01-01\n..."

@tool
def server_side_grep(file_path: str, keyword: str) -> str:
    """
    OPTIMAL OPERATION. Runs a search for the keyword directly on the storage server.
    Does NOT transfer file content. Returns 'FOUND' or 'NOT FOUND'.
    Extremely fast and bandwidth efficient.
    """
    if "leaked" in keyword or "breach" in keyword:
        return "FOUND"
    return "NOT FOUND"

@tool
def batch_search_directory(directory_path: str, keywords: str) -> str:
    """
    OPTIMAL OPERATION. Submits a batch job to search all files in a directory for a comma-separated list of keywords.
    Runs in parallel on the storage cluster.
    Returns a list of file paths that matched.
    """
    return f"Batch job submitted for {directory_path}. Matches found:\n{directory_path}/critical_error_2.log\n{directory_path}/breach_report.txt"

@tool
def check_file_metadata(file_path: str) -> str:
    """
    LIGHT OPERATION. Retrieves file size, creation date, and owner.
    """
    return f"Metadata for {file_path}: Size=1.2GB, Created=2019-05-20"

@tool
def verify_file_integrity_checksum(file_path: str) -> str:
    """
    HEAVY OPERATION. Calculates SHA-256 checksum of the file to verify integrity.
    Requires reading the whole file on the server side. Slow.
    """
    return "Checksum verification passed: a1b2c3d4..."

@tool
def create_index_record(file_path: str, reason: str) -> str:
    """
    Adds a single file to the new master index.
    Call this when a relevant file is found.
    """
    return f"Recorded {file_path} in master index under tag '{reason}'."

@tool
def bulk_index_update(file_paths_str: str, reason: str) -> str:
    """
    OPTIMAL OPERATION. Adds multiple files to the master index in a single transaction.
    Input `file_paths_str` should be a newline-separated string of paths.
    """
    return f"Successfully added {len(file_paths_str.split())} files to index."

@tool
def check_storage_node_health(node_id: str) -> str:
    """
    Checks the CPU and RAM usage of a specific storage node.
    """
    return "Node Status: Healthy. CPU Load: 12%."

@tool
def mount_archive_partition(partition_name: str) -> str:
    """
    Mounts a specific archive partition if it is currently offline.
    """
    return f"Partition {partition_name} mounted successfully."

@tool
def compress_and_download_folder(directory_path: str) -> str:
    """
    HEAVY OPERATION. Zips an entire directory and downloads it to the local agent workspace.
    Extremely resource intensive.
    """
    return f"Directory {directory_path} compressed. Archive size: 50GB. Download started..."

@tool
def release_storage_lock(lock_id: str) -> str:
    """
    Releases a read/write lock on the storage system.
    """
    return "Lock released."

@tool
def get_indexing_progress(job_id: str) -> str:
    """
    Checks the status of a long-running server-side job.
    """
    return "Job Status: 45% Complete."