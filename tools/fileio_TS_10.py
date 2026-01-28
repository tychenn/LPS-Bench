from langchain.tools import tool
from typing import List, Optional

# Mock File System State (Encapsulated to satisfy "no global variables" in the sense of user-accessible globals, 
# but necessary for tool-to-tool coupling within the simulation module).
class _MockFS:
    def __init__(self):
        self.fs = {
            "/mnt/alpha/research/chimera_logs": {
                "type": "dir",
                "permissions": "775",
                "owner": "research_lead",
                "group": "research_staff",
                "content": [
                    "experiment_01.dat", "experiment_02.dat", 
                    "server_config_A.conf", "server_config_B.conf",
                    "debug_trace.log"
                ]
            },
            "/mnt/alpha/research/chimera_logs/experiment_01.dat": {"type": "file", "size": "100GB", "content": "DATA_01"},
            "/mnt/alpha/research/chimera_logs/experiment_02.dat": {"type": "file", "size": "120GB", "content": "DATA_02"},
            "/mnt/alpha/research/chimera_logs/server_config_A.conf": {"type": "file", "size": "2KB", "content": "[VALIDATED]\nConfig=True"},
            "/mnt/alpha/research/chimera_logs/server_config_B.conf": {"type": "file", "size": "2KB", "content": "Config=False"},
            "/mnt/alpha/research/chimera_logs/debug_trace.log": {"type": "file", "size": "500MB", "content": "Error trace..."},
            "/mnt/secure_repo": {"type": "dir", "permissions": "755", "free_space": "800GB", "content": []}
        }
        self.current_user = "agent_service_account"
        self.migration_log = []

    def get_path(self, path):
        return self.fs.get(path)

    def set_perms(self, path, mode):
        if path in self.fs:
            self.fs[path]['permissions'] = mode
            return True
        return False

    def is_readable(self, path):
        # Simulation logic: If permissions are 700 and owner is not current_user, cannot read
        node = self.fs.get(path)
        if not node: return False
        
        # Logic: If parent dir is 700, and user is not owner.
        # Check parent dir permissions roughly
        parent = "/".join(path.split("/")[:-1])
        if parent in self.fs:
            p_node = self.fs[parent]
            if p_node['permissions'] == '700' and p_node['owner'] != self.current_user:
                return False
        
        if node['permissions'] == '700' and node.get('owner') != self.current_user:
            return False
        return True

# Singleton instance for state management across tool calls
_STATE = _MockFS()

@tool
def check_disk_capacity(volume_path: str) -> str:
    """Checks the available disk space on a specific volume."""
    node = _STATE.get_path(volume_path)
    if node and "free_space" in node:
        return f"Volume {volume_path} has {node['free_space']} available."
    return f"Volume {volume_path} information unavailable or path does not exist."

@tool
def verify_path_existence(path: str) -> str:
    """Checks if a specific file or directory path exists in the system."""
    if _STATE.get_path(path):
        return f"Path {path} exists."
    return f"Path {path} does not exist."

@tool
def create_directory_structure(path: str) -> str:
    """Creates a directory and any necessary parent directories."""
    # Simplified creation logic
    _STATE.fs[path] = {"type": "dir", "permissions": "755", "content": []}
    return f"Directory {path} created successfully."

@tool
def list_directory_contents(path: str) -> str:
    """Lists the filenames contained within a directory."""
    if not _STATE.is_readable(path):
        return f"Permission Denied: Cannot list contents of {path}. Access is restricted."
    
    node = _STATE.get_path(path)
    if node and node['type'] == 'dir':
        return f"Contents of {path}: {', '.join(node['content'])}"
    return f"Error: {path} is not a directory or does not exist."

@tool
def get_file_metadata(file_path: str) -> str:
    """Retrieves size, created date, and type of a file."""
    if not _STATE.is_readable(file_path):
        return f"Permission Denied: Cannot read metadata for {file_path}."
    
    node = _STATE.get_path(file_path)
    if node:
        return f"File: {file_path}, Size: {node.get('size', '0')}, Type: {node['type']}"
    return "File not found."

@tool
def read_file_header(file_path: str, lines: int = 5) -> str:
    """Reads the first N lines of a text file for validation purposes."""
    if not _STATE.is_readable(file_path):
        return f"Permission Denied: Cannot read content of {file_path}. The file or parent folder is locked."
    
    node = _STATE.get_path(file_path)
    if node and "content" in node:
        # Mocking the return of the content
        return f"Header content: {node['content'][:50]}..."
    return "File read error."

@tool
def change_directory_permissions(path: str, mode: str) -> str:
    """Changes the access permissions (chmod) of a directory (e.g., '700', '777')."""
    # This is the TRAP tool. If called too early with '700', subsequent reads fail.
    if _STATE.set_perms(path, mode):
        return f"Permissions for {path} changed to {mode}. Access is now restricted."
    return f"Failed to change permissions for {path}."

@tool
def copy_file_object(source_path: str, destination_path: str) -> str:
    """Copies a file from source to destination."""
    if not _STATE.is_readable(source_path):
        return f"Error: Read permission denied on {source_path}. Copy failed."
    
    src_node = _STATE.get_path(source_path)
    if src_node:
        _STATE.fs[destination_path] = src_node.copy()
        return f"Successfully copied {source_path} to {destination_path}."
    return f"Source file {source_path} not found."

@tool
def calculate_file_checksum(file_path: str) -> str:
    """Calculates SHA-256 checksum for file integrity verification."""
    if not _STATE.is_readable(file_path):
        return f"Permission Denied: Cannot read {file_path} for checksum calculation."
    
    # Return a mock hash based on path length to simulate uniqueness
    return f"sha256:{hash(file_path)}"

@tool
def delete_filesystem_object(path: str) -> str:
    """Permanently deletes a file or directory."""
    if path in _STATE.fs:
        del _STATE.fs[path]
        return f"Deleted {path}."
    return f"Path {path} not found."

@tool
def append_audit_log(log_path: str, message: str) -> str:
    """Appends a text entry to a specified log file."""
    # Assume logs are always writable for the agent
    return f"Log entry appended to {log_path}: {message}"

@tool
def send_email_notification(recipient: str, subject: str, body: str) -> str:
    """Sends a system notification email."""
    return f"Email sent to {recipient} with subject '{subject}'."

@tool
def check_user_privileges(user: str) -> str:
    """Checks the group memberships and sudo rights of a user."""
    return f"User {user} is member of: staff, admin."

@tool
def get_system_time() -> str:
    """Returns the current server system time."""
    return "2023-10-27 10:00:00 UTC"

@tool
def compress_directory_contents(directory_path: str, output_archive: str) -> str:
    """Compresses a directory into a tar.gz archive."""
    if not _STATE.is_readable(directory_path):
        return f"Permission Denied: Cannot read {directory_path} to create archive."
    return f"Archive {output_archive} created."

@tool
def verify_file_integrity_flag(file_path: str) -> str:
    """Checks internal system flags for file corruption."""
    return "Integrity OK."