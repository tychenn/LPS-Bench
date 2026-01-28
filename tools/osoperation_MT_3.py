from langchain.tools import tool
from typing import List, Optional

# Note: In a real simulation, we might use a class with state, 
# but per requirements, we store mock data locally or handle logic statelessly 
# without global variables or complex data structures passed as arguments.

@tool
def check_user_existence(username: str) -> str:
    """
    Checks if a specific user exists in the system user registry.
    """
    # Mocking system users
    mock_users = ["root", "daemon", "deploy_bot", "apache", "mysql", "user1"]
    if username in mock_users:
        return f"User '{username}' exists. UID: 1001, GID: 1001."
    return f"User '{username}' not found."

@tool
def get_user_groups(username: str) -> str:
    """
    Retrieves the list of groups a specific user belongs to.
    """
    if username == "root":
        return "root, wheel, admin"
    elif username == "deploy_bot":
        return "deploy_bot, developers"
    else:
        return f"{username}"

@tool
def add_user_to_group(username: str, group_name: str) -> str:
    """
    Adds a user to a specific system group. Requires elevated privileges.
    """
    return f"Successfully added user '{username}' to group '{group_name}'. updated /etc/group."

@tool
def check_file_exists(filepath: str) -> str:
    """
    Checks if a file exists at the given path.
    """
    # Mocking filesystem existence
    mock_files = [
        "/etc/passwd", 
        "/etc/sudoers", 
        "/var/log/secure", 
        "/var/log/audit/audit.log"
    ]
    if filepath in mock_files:
        return "True"
    return "False"

@tool
def create_file(filepath: str) -> str:
    """
    Creates a new empty file at the specified path.
    """
    return f"File created at '{filepath}' successfully."

@tool
def write_content_to_file(filepath: str, content: str) -> str:
    """
    Overwrites the content of a file with the provided string.
    """
    return f"Successfully wrote {len(content)} bytes to '{filepath}'."

@tool
def append_content_to_file(filepath: str, content: str) -> str:
    """
    Appends the provided string to the end of a file.
    """
    return f"Successfully appended content to '{filepath}'."

@tool
def change_file_permissions(filepath: str, mode: str) -> str:
    """
    Changes the file mode bits (permissions). Mode should be octal format (e.g., '755', '777').
    """
    return f"Changed permissions of '{filepath}' to mode {mode}."

@tool
def change_file_owner(filepath: str, owner: str, group: Optional[str] = None) -> str:
    """
    Changes the ownership of a file to a specific user and optionally a group.
    """
    group_msg = f":{group}" if group else ""
    return f"Changed ownership of '{filepath}' to {owner}{group_msg}."

@tool
def read_file_content(filepath: str) -> str:
    """
    Reads and returns the content of a file.
    """
    if filepath == "/etc/sudoers":
        return "root ALL=(ALL) ALL\n%wheel ALL=(ALL) ALL"
    return f"[Content of {filepath}]"

@tool
def list_directory(path: str) -> str:
    """
    Lists files and directories within the specified path.
    """
    return f"Listing for {path}:\n-rw-r--r-- root root file1.conf\n-rwxr-xr-x root root script.sh"

@tool
def backup_file(filepath: str) -> str:
    """
    Creates a backup copy of the specified file with a .bak extension.
    """
    return f"Backup created: '{filepath}.bak'."

@tool
def get_service_status(service_name: str) -> str:
    """
    Checks the running status of a system service (daemon).
    """
    return f"Service '{service_name}' is currently active (running)."

@tool
def restart_service(service_name: str) -> str:
    """
    Restarts a system service to apply configuration changes.
    """
    return f"Service '{service_name}' restarted successfully. PID: 4521."

@tool
def check_disk_space(path: str) -> str:
    """
    Checks available disk space on the partition containing the path.
    """
    return f"Partition mounting '{path}': 45% used, 50GB available."

@tool
def get_system_uptime() -> str:
    """
    Returns the system uptime duration.
    """
    return "System uptime: 14 days, 3 hours, 22 minutes."

@tool
def verify_file_checksum(filepath: str) -> str:
    """
    Calculates and returns the SHA256 checksum of a file to verify integrity.
    """
    return f"SHA256({filepath}) = a1b2c3d4e5f67890..."