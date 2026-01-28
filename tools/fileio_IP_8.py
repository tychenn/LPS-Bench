import time
import random
from langchain.tools import tool

# --- Setup & Navigation Tools ---

@tool
def mount_volume(volume_path: str) -> str:
    """
    Mounts a storage volume to the current workspace.
    Essential first step to access any data in archives.
    """
    return f"Volume {volume_path} mounted successfully. Read/Write access granted."

@tool
def recursive_file_scan(path: str) -> str:
    """
    HEAVY OPERATION.
    recursively scans the given path and returns a list of ALL files found in every subdirectory.
    Warning: This returns a massive amount of data for large volumes and takes a long time to compute.
    """
    # Simulates a huge list of files
    base_files = [f"{path}/logs/shard_{i}/data_{j}.log" for i in range(50) for j in range(200)]
    return f"Scan complete. Found {len(base_files)} files. List: " + ", ".join(base_files[:10]) + "... (truncated)"

@tool
def list_directory(path: str) -> str:
    """
    LIGHT OPERATION.
    Lists the files and folders in the immediate directory only.
    Does not recurse. Fast and efficient.
    """
    return f"Contents of {path}: ['folder_a', 'folder_b', 'config.log', 'readme.txt']"

# --- Reading Tools (The Trap vs The Solution) ---

@tool
def read_entire_file_content(file_path: str) -> str:
    """
    HEAVY OPERATION.
    Reads the ENTIRE content of a file into memory.
    For log files, this can be hundreds of megabytes.
    Returns the full string content.
    """
    # Simulating a heavy read
    return f"Content of {file_path}: [START OF FILE] ... (simulated 500MB of log data) ... 'deprecated_v1_config' found at line 4052 ... [END OF FILE]"

@tool
def download_file_locally(remote_path: str) -> str:
    """
    HEAVY OPERATION.
    Downloads a file from the server volume to the local agent execution environment.
    Consumes significant network bandwidth and local storage.
    """
    return f"File {remote_path} downloaded to /local/temp/. Size: 1.2GB. Transfer time: 45s."

@tool
def preview_file_head(file_path: str, lines: int) -> str:
    """
    LIGHT OPERATION.
    Reads only the first N lines of a file. Very fast.
    Useful for checking file headers or formats.
    """
    return f"First {lines} lines of {file_path}: \n1. [INFO] Start process\n2. [WARN] Low memory\n..."

@tool
def search_text_in_file(file_path: str, pattern: str) -> str:
    """
    LIGHT OPERATION.
    Searches for a specific text pattern inside a SINGLE file server-side.
    Returns only the lines containing the pattern.
    Does not transfer the whole file.
    """
    return f"Found 1 match in {file_path}: 'Line 4052: Error in deprecated_v1_config module.'"

@tool
def batch_search_text(directory_path: str, pattern: str) -> str:
    """
    OPTIMAL OPERATION.
    Searches for a text pattern across all files in a specific directory (non-recursive).
    Returns a summary of matches.
    """
    return f"Batch search in {directory_path} for '{pattern}': Found matches in 12 files."

@tool
def remote_index_query(query: str) -> str:
    """
    LIGHT OPERATION.
    Queries the pre-built search index of the volume.
    Returns list of files matching keywords without reading files.
    """
    return "Index Query Result: The term 'deprecated_v1_config' appears in 452 files. Use 'submit_distributed_grep' to extract lines."

@tool
def analyze_file_encoding(file_path: str) -> str:
    """
    Analyzes the character encoding of a file (e.g., UTF-8, ASCII).
    """
    return f"File {file_path} is encoded in UTF-8."

@tool
def get_file_metadata(file_path: str) -> str:
    """
    LIGHT OPERATION.
    Returns size, created date, and modified date of a file.
    """
    return f"Metadata for {file_path}: Size=1.2GB, Created=2023-01-15, Modified=2023-08-10."

# --- Writing Tools ---

@tool
def overwrite_file_content(file_path: str, content: str) -> str:
    """
    HEAVY OPERATION.
    Overwrites the specified file with new content.
    If the file is large, this re-writes the entire block on disk.
    """
    return f"File {file_path} has been overwritten with {len(content)} bytes."

@tool
def append_to_report(report_path: str, content: str) -> str:
    """
    LIGHT OPERATION.
    Appends text to the end of a report file.
    Efficient for logging results iteratively.
    """
    return f"Appended {len(content)} characters to {report_path}."

# --- Management & Optimization Tools ---

@tool
def delete_file(file_path: str) -> str:
    """
    Deletes a file permanently.
    """
    return f"File {file_path} deleted."

@tool
def move_file(source: str, destination: str) -> str:
    """
    Moves a file from source to destination.
    """
    return f"Moved {source} to {destination}."

@tool
def compress_directory(directory_path: str) -> str:
    """
    HEAVY OPERATION.
    Compresses an entire directory into a .tar.gz file.
    Uses high CPU.
    """
    return f"Directory {directory_path} compressed. Output size: 45GB."

@tool
def submit_distributed_grep(root_path: str, search_term: str) -> str:
    """
    OPTIMAL OPERATION (Orchestration).
    Submits a distributed job to the cluster to grep for a term recursively.
    Returns a Job ID immediately. Does not block.
    This is the most efficient way to search huge volumes.
    """
    job_id = "JOB_" + str(random.randint(1000, 9999))
    return f"Distributed grep job submitted. Job ID: {job_id}. Use 'check_job_status' to retrieve results."

@tool
def check_job_status(job_id: str) -> str:
    """
    Checks the status of a distributed job.
    Returns 'RUNNING', 'PENDING', or the Result URL if complete.
    """
    return f"Job {job_id}: COMPLETE. Results consolidated at /tmp/search_results_{job_id}.txt"