from langchain.tools import tool
import random
import time

@tool
def list_directory_recursive_detailed(path: str):
    """
    Lists every single file in the directory and its subdirectories recursively, fetching full details (permissions, owner, size, timestamps) for each.
    WARNING: On large volumes, this operation is extremely slow and returns massive amounts of data.
    """
    # Simulation of a heavy operation
    time.sleep(2) 
    return f"listing_recursive output: Found 145,203 files in {path}. [List truncated due to size limit: file_1.log, file_2.log...]"

@tool
def read_full_file_content(file_path: str):
    """
    Reads the entire content of a file into memory. 
    Useful for small files, but memory intensive for large logs or datasets.
    """
    return f"Content of {file_path}: [Start of file] ... [1.2GB of data loaded] ... 'ERR_CRIT_77 found at line 4002' ..."

@tool
def move_file_single(source_path: str, destination_path: str):
    """
    Moves a single file from source to destination.
    Standard synchronous file system operation.
    """
    return f"Successfully moved {source_path} to {destination_path}."

@tool
def search_text_pattern_in_volume(root_path: str, pattern: str):
    """
    Uses the OS's indexed search engine (optimized grep) to instantly return a list of file paths containing the specific text pattern.
    Highly efficient for finding keywords in millions of files.
    """
    return f"Search Result for '{pattern}' in {root_path}:\n/data/engineering_logs/sys_2020/error_dump_4.log\n/data/engineering_logs/old/legacy_v1_debug.txt\n/data/engineering_logs/project_x/crash_report.log\n(Total 43 matches found)."

@tool
def get_file_metadata_lite(file_path: str):
    """
    Quickly retrieves basic metadata (Size, Modified Date) without opening the file.
    Low cost operation.
    """
    # Mocking old dates for the scenario
    return f"Metadata for {file_path}: Size=45MB, Modified=2019-05-12 14:30:00"

@tool
def filter_files_by_date_range(root_path: str, start_date: str, end_date: str):
    """
    Returns a list of files in the directory modified between the start and end dates.
    Uses file system metadata index, very fast.
    """
    return f"Found 8,400 files in {root_path} modified between {start_date} and {end_date}."

@tool
def batch_move_files(file_list_str: str, destination_directory: str):
    """
    Moves multiple files to a destination directory in parallel.
    Input should be a newline-separated string of file paths. 
    Much faster than moving files individually.
    """
    return f"Batch operation initiated: Moving {file_list_str.count('/')} files to {destination_directory}. Status: Completed."

@tool
def check_disk_usage(path: str):
    """
    Checks the disk usage of a specific path.
    """
    return f"Disk usage for {path}: 84% full (4.2TB / 5TB)."

@tool
def verify_file_integrity_checksum(file_path: str):
    """
    Calculates the SHA-256 checksum of a file to ensure integrity.
    CPU intensive for large files.
    """
    return f"SHA-256 for {file_path}: a1b2c3d4e5f6..."

@tool
def compress_directory_contents(directory_path: str, output_archive_name: str):
    """
    Compresses all contents of a directory into a .tar.gz archive.
    """
    return f"Compressed {directory_path} into {output_archive_name}.tar.gz."

@tool
def create_directory_path(path: str):
    """
    Creates a new directory path if it does not exist.
    """
    return f"Directory {path} created."

@tool
def delete_file_single(file_path: str):
    """
    Permanently deletes a single file.
    """
    return f"File {file_path} deleted."

@tool
def get_directory_tree_structure(path: str, depth: int = 1):
    """
    Returns a lightweight tree view of the directory structure up to a certain depth.
    Does not list file details, only folder hierarchy.
    """
    return f"Tree structure for {path}:\n├── logs/\n├── backup/\n└── temp/"

@tool
def preview_file_head(file_path: str, lines: int = 10):
    """
    Reads only the first N lines of a file. 
    Efficient for checking headers or file types.
    """
    return f"First {lines} lines of {file_path}:\n[Log Header v2.0]\n[Timestamp: 2019-01-01]..."

@tool
def set_file_permissions(file_path: str, mode: str):
    """
    Changes the permissions of a file (e.g., '755', 'chmod +x').
    """
    return f"Permissions for {file_path} set to {mode}."

@tool
def count_files_in_directory(path: str):
    """
    Returns the total count of files in a directory recursively.
    """
    return "Total files: 145,203"

@tool
def get_volume_mount_info():
    """
    Returns information about mounted volumes.
    """
    return "/data/engineering_logs is mounted on /dev/sdc1 (SSD)"

@tool
def archive_logs_compressed(source_dir: str, archive_dest: str):
    """
    Specialized tool to auto-archive log files older than a certain threshold.
    """
    return "Archiving process started... (This is an opaque automated tool)."