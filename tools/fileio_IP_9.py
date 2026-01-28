from langchain.tools import tool
from typing import List, Optional

# --- Navigation and Inspection Tools (Light vs Heavy) ---

@tool
def list_directory_contents(path: str) -> str:
    """
    Lists the names of files and folders in a specific directory. 
    Returns a simple list of names. Does not provide metadata or recursive content.
    """
    if "/mnt/engineering/projects" in path:
        return "['project_alpha', 'project_beta', 'legacy_omega', 'old_lib_v1', 'temp_builds', 'project_gamma', ... and 450 other items]"
    return "[]"

@tool
def recursive_tree_scan_all(root_path: str) -> str:
    """
    [HEAVY OPERATION] Performs a deep recursive scan of the directory tree.
    Returns a massive JSON string containing every single file path, size, owner, and permission 
    for the entire tree structure. 
    Warning: This consumes significant memory and time on large directories.
    """
    return "Scan complete: Retrieved metadata for 142,000 files. [Data truncated for view]..."

@tool
def get_file_metadata(file_path: str) -> str:
    """
    Retrieves metadata (size, created_date, modified_date, owner) for a SINGLE file or folder.
    """
    if "legacy" in file_path or "old" in file_path:
        return f"Path: {file_path} | Type: Directory | Modified: 2021-05-12 | Size: 4.2GB"
    return f"Path: {file_path} | Type: Directory | Modified: 2024-01-15 | Size: 1.1GB"

@tool
def find_directories_by_date_filter(root_path: str, modified_before: str) -> str:
    """
    [OPTIMAL] Server-side search tool.
    Efficiently finds all directories within a root path that were last modified before a specific date.
    Returns a list of matching paths immediately without traversing the network for every file.
    Format for date: YYYY-MM-DD.
    """
    return "Found 124 directories matching criteria, including: ['/mnt/engineering/projects/legacy_omega', '/mnt/engineering/projects/old_lib_v1', ...]"

@tool
def get_disk_usage_summary(path: str) -> str:
    """
    Returns a high-level summary of disk usage for a mount point.
    """
    return "Volume: /mnt/engineering | Used: 92% | Free: 8% | Total: 50TB"

@tool
def verify_path_exists(path: str) -> str:
    """
    Checks if a specific path exists. Returns 'True' or 'False'.
    """
    return "True"

# --- Content Inspection (Trap vs Light) ---

@tool
def read_file_content_full(file_path: str) -> str:
    """
    [HEAVY OPERATION] Reads the ENTIRE content of a file into memory.
    Do not use this for checking simple attributes or headers.
    """
    return "File content loaded into memory (Size: 2048 MB). Content preview: <Binary Data>..."

@tool
def read_file_head(file_path: str, lines: int = 5) -> str:
    """
    Reads only the first N lines of a file. Very fast.
    """
    return "Project configuration header: [Legacy V1.0]..."

@tool
def search_file_content_keyword(root_path: str, keyword: str) -> str:
    """
    [EXTREMELY HEAVY] Opens every file in the directory tree to search for a text string.
    """
    return "Search completed. Found 0 matches in 142,000 files."

@tool
def calculate_file_hash(file_path: str) -> str:
    """
    [HEAVY OPERATION] Calculates the SHA-256 checksum of a file to verify integrity.
    Requires reading the full file.
    """
    return "sha256: a1b2c3d4e5f6..."

# --- Manipulation Tools (Single vs Batch) ---

@tool
def create_directory(path: str) -> str:
    """
    Creates a new empty directory.
    """
    return f"Directory created: {path}"

@tool
def move_file_item(source_path: str, destination_path: str) -> str:
    """
    Moves a SINGLE file or folder to a new location.
    If used in a loop for thousands of items, this will be very slow.
    """
    return f"Moved {source_path} to {destination_path}"

@tool
def copy_file_item(source_path: str, destination_path: str) -> str:
    """
    Copies a SINGLE file or folder.
    """
    return f"Copied {source_path} to {destination_path}"

@tool
def delete_file_item(path: str) -> str:
    """
    Deletes a SINGLE file or folder.
    """
    return f"Deleted {path}"

@tool
def bulk_transfer_directory(source_list: str, destination_folder: str) -> str:
    """
    [OPTIMAL] Efficiently moves multiple directories or files in a single system transaction.
    Accepts a comma-separated list of paths or a wildcard pattern.
    Preserves metadata and handles recursion server-side.
    """
    return "Bulk transfer initiated. 124 directories moved successfully to /mnt/archive/legacy_projects."

@tool
def compress_directory_to_zip(source_path: str, destination_path: str) -> str:
    """
    Compresses a directory into a zip file at the destination.
    Good for archiving, but requires CPU.
    """
    return f"Compression complete: {destination_path} created."

@tool
def archive_and_migrate_batch(source_root: str, filter_date: str, dest_root: str) -> str:
    """
    [OPTIMAL - High Level] An orchestration tool that automatically finds old files
    older than the filter_date, archives them, and moves them to destination.
    """
    return f"Batch migration job 'ARCHIVE_OLD' started. Moving items older than {filter_date} from {source_root} to {dest_root}. Status: Running Background."