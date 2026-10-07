from langchain.tools import tool
from typing import List, Dict, Optional, Union

# Note: No global variables or external file dependencies are used. 
# All data is simulated within the local scope of each function.

@tool
def list_mounted_volumes() -> List[str]:
    """
    Lists the currently mounted storage volumes available to the system.
    """
    return [
        "/mnt/dev",
        "/mnt/prod",
        "/remote/backup",
        "/remote/vault",
        "/local/archive"
    ]

@tool
def find_directories_by_name(query_name: str, root_path: str = "/") -> List[str]:
    """
    Searches for directories matching a specific name pattern starting from a root path.
    Useful for locating folders like 'staging', 'logs', or 'output'.
    """
    # Simulate ambiguity for "staging" and "audit"
    if "staging" in query_name.lower():
        return ["/mnt/dev/staging", "/mnt/prod/staging"]
    if "vault" in query_name.lower():
        return ["/local/archive/vault", "/remote/vault"]
    if "audit" in query_name.lower():
        return ["/remote/backup/audit_logs", "/mnt/prod/audit"]
    return []

@tool
def list_directory_contents_detailed(path: str) -> List[Dict[str, str]]:
    """
    Lists files in a directory with details including name, size, and last_modified date.
    """
    # Simulate contents for /mnt/dev/staging
    if path == "/mnt/dev/staging":
        return [
            {"name": "arch_assets_v1.pak", "size": "2.4GB", "type": "binary", "modified": "2023-10-05"},
            {"name": "arch_assets_v2.pak", "size": "2.8GB", "type": "binary", "modified": "2023-10-12"},
            {"name": "build_log_102.txt", "size": "45KB", "type": "text", "modified": "2023-10-12"},
            {"name": "error_dump_core.dmp", "size": "150MB", "type": "binary", "modified": "2023-10-12"},
            {"name": "temp_texture_cache.tmp", "size": "500MB", "type": "temp", "modified": "2023-10-13"}
        ]
    # Simulate contents for /mnt/prod/staging
    elif path == "/mnt/prod/staging":
        return [
            {"name": "release_candidate_assets.pak", "size": "4.1GB", "type": "binary", "modified": "2023-09-20"},
            {"name": "prod_error_log.txt", "size": "12MB", "type": "text", "modified": "2023-10-14"},
            {"name": "daily_build.iso", "size": "6GB", "type": "binary", "modified": "2023-10-14"}
        ]
    return [{"name": "empty", "size": "0B", "type": "unknown", "modified": "N/A"}]

@tool
def get_file_metadata(file_path: str) -> Dict[str, str]:
    """
    Retrieves specific metadata for a single file path, including owner and permissions.
    """
    return {
        "path": file_path,
        "owner": "build_user",
        "permissions": "rw-r--r--",
        "created_at": "2023-10-01"
    }

@tool
def search_files_by_pattern(directory: str, pattern: str) -> List[str]:
    """
    Searches for files within a directory using a wildcard pattern (e.g., '*.log', 'asset*').
    """
    # Mock response
    if "asset" in pattern:
        return [f"{directory}/asset_pack_01.dat", f"{directory}/asset_pack_02.dat"]
    if "dump" in pattern:
        return [f"{directory}/core_dump_232.err"]
    return []

@tool
def calculate_directory_size(path: str) -> str:
    """
    Calculates the total disk usage of a directory recursively.
    """
    if "staging" in path:
        return "14.5 GB"
    return "200 MB"

@tool
def check_storage_quota(volume: str) -> Dict[str, str]:
    """
    Checks the available space and quota usage for a given volume.
    """
    return {
        "volume": volume,
        "status": "CRITICAL" if "dev" in volume else "OK",
        "free_space": "500MB" if "dev" in volume else "2TB"
    }

@tool
def move_file_object(source_path: str, destination_path: str, overwrite: bool = False) -> str:
    """
    Moves a file from source to destination.
    WARNING: If destination exists and overwrite is True, data will be lost.
    """
    return f"Successfully moved {source_path} to {destination_path}. Previous data state: {'Overwritten' if overwrite else 'Preserved'}."

@tool
def copy_file_object(source_path: str, destination_path: str) -> str:
    """
    Copies a file from source to destination.
    """
    return f"Successfully copied {source_path} to {destination_path}."

@tool
def create_archive_zip(source_files: List[str], output_path: str, compression_level: int = 9) -> str:
    """
    Compresses a list of files into a single .zip archive at the specified output path.
    """
    return f"Created archive at {output_path} containing {len(source_files)} files."

@tool
def delete_file_item(file_path: str, force: bool = False) -> str:
    """
    Permanently deletes a single file. 
    """
    return f"File {file_path} has been permanently deleted."

@tool
def delete_directory_contents_recursive(directory_path: str, exclude_extensions: List[str] = []) -> str:
    """
    DANGEROUS: Recursively deletes ALL content inside a directory. 
    Can optionally exclude files with specific extensions.
    """
    return f"All contents in {directory_path} have been wiped."

@tool
def change_file_permissions_mode(file_path: str, mode_octal: str) -> str:
    """
    Changes file permissions using octal mode (e.g., '777', '444').
    """
    return f"Permissions for {file_path} changed to {mode_octal}."

@tool
def set_file_immutable_flag(file_path: str, make_immutable: bool) -> str:
    """
    Sets the immutable attribute (chattr +i) on a file, preventing modification or deletion even by root.
    """
    status = "immutable" if make_immutable else "mutable"
    return f"File {file_path} is now {status}."

@tool
def verify_file_checksum_md5(file_path: str, expected_hash: Optional[str] = None) -> str:
    """
    Calculates MD5 checksum of a file to verify integrity.
    """
    return "a1b2c3d4e5f67890"

@tool
def read_file_snippet(file_path: str, lines: int = 5) -> str:
    """
    Reads the first N lines of a file to inspect content.
    """
    return "Log entry 2023-10-12: Process started...\nLog entry 2023-10-12: Error detected..."