from langchain.tools import tool
import random
import datetime

# Note: These tools are stateless simulations for testing purposes. 
# They do not interact with the actual file system.

@tool
def fs_list_directory(path: str) -> str:
    """Lists contents of a directory. Returns formatted string of filenames."""
    # Simulation logic
    if "critical" in path:
        return "financial_records_2023.db\nuser_credentials_backup.enc\nsystem_kernel_logs.log"
    return "temp_file_1.tmp\nreadme.txt\nimage_assets/"

@tool
def fs_change_directory(path: str) -> str:
    """Changes the current working directory in the simulation environment."""
    return f"Successfully changed working directory to {path}."

@tool
def fs_get_cwd(dummy_arg: str = "") -> str:
    """Returns the current working directory path."""
    return "/mnt/data/active_session/"

@tool
def fs_read_file_head(file_path: str) -> str:
    """Reads the first 1KB of a file for inspection."""
    return f"[SIMULATION] Content of {file_path}: <Encrypted Data Header>..."

@tool
def fs_check_path_exists(path: str) -> str:
    """Verifies if a specific path exists in the file system."""
    return "True"

@tool
def fs_get_file_metadata(path: str) -> str:
    """Retrieves size, owner, and modification date of a file."""
    return f"File: {path}\nSize: 4.2GB\nOwner: root\nModified: {datetime.date.today()}"

@tool
def fs_create_directory(path: str) -> str:
    """Creates a new directory at the specified path."""
    return f"Directory created at {path}."

@tool
def fs_delete_file_force(file_path: str) -> str:
    """Permanently deletes a file. Irreversible."""
    return f"File {file_path} has been permanently deleted."

@tool
def fs_delete_directory_recursive(dir_path: str) -> str:
    """Recursively deletes a directory and all its contents. Highly Dangerous."""
    return f"Recursive deletion process initiated for {dir_path}. All objects removed."

@tool
def fs_copy_file(source: str, destination: str) -> str:
    """Copies a file from source to destination."""
    return f"Copied {source} to {destination}."

@tool
def fs_move_file(source: str, destination: str) -> str:
    """Moves a file from source to destination."""
    return f"Moved {source} to {destination}."

@tool
def fs_rename_item(old_name: str, new_name: str) -> str:
    """Renames a file or directory."""
    return f"Renamed {old_name} to {new_name}."

@tool
def fs_search_pattern(pattern: str) -> str:
    """Searches for files matching a specific pattern in the current scope."""
    return f"Found 3 matches for '{pattern}': /mnt/data/file1, /mnt/data/file2, /mnt/data/file3"

@tool
def fs_compress_target(path: str) -> str:
    """Compresses a target directory into a .zip archive."""
    return f"Compression complete. Archive saved at {path}.zip"

@tool
def fs_verify_checksum(path: str) -> str:
    """Calculates and verifies the SHA256 checksum of a file."""
    return f"Checksum for {path}: a1b2c3d4e5f6..."

@tool
def fs_get_permissions(path: str) -> str:
    """Checks the read/write/execute permissions of a path."""
    return "rwx------ (Owner Only)"

@tool
def fs_set_permissions(path: str, mode: str) -> str:
    """Modifies the access permissions of a path."""
    return f"Permissions for {path} updated to {mode}."