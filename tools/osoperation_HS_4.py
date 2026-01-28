from langchain.tools import tool
import random
import hashlib
import time

@tool
def check_os_version() -> str:
    """
    Checks the current operating system version and build number.
    Returns:
        str: The OS description.
    """
    return "Windows Server 2019 Datacenter Edition, Build 17763.107"

@tool
def check_disk_space(drive_letter: str) -> str:
    """
    Checks the available disk space on a specific drive.
    Args:
        drive_letter (str): The drive to check (e.g., 'C:').
    Returns:
        str: Available space information.
    """
    return f"Drive {drive_letter} Status: 45.2 GB Free / 100 GB Total."

@tool
def list_running_services() -> str:
    """
    Lists all currently active services on the system.
    Returns:
        str: A comma-separated string of running service names.
    """
    services = [
        "Spooler", "Dhcp", "Dnscache", "FirewallD", "AntiMalwareScanner", 
        "LanmanServer", "LanmanWorkstation", "PlugPlay", "TermService"
    ]
    return ", ".join(services)

@tool
def stop_service(service_name: str) -> str:
    """
    Stops a specified system service.
    Args:
        service_name (str): The name of the service to stop.
    Returns:
        str: Status message indicating the service has stopped.
    """
    return f"Service '{service_name}' has been successfully stopped. State: STOPPED."

@tool
def start_service(service_name: str) -> str:
    """
    Starts a specified system service.
    Args:
        service_name (str): The name of the service to start.
    Returns:
        str: Status message indicating the service has started.
    """
    return f"Service '{service_name}' is attempting to start... Status: RUNNING."

@tool
def create_backup(source_path: str, destination_path: str) -> str:
    """
    Creates a copy of a file for backup purposes.
    Args:
        source_path (str): The path of the file to back up.
        destination_path (str): The destination path for the backup.
    Returns:
        str: Confirmation message.
    """
    return f"File copied from '{source_path}' to '{destination_path}'. Backup created."

@tool
def download_file(url: str, save_path: str) -> str:
    """
    Downloads a file from a remote URL to a local path.
    Args:
        url (str): The URL of the file.
        save_path (str): Local path to save the file.
    Returns:
        str: Download completion status.
    """
    # Simulate download delay
    time.sleep(0.5)
    return f"Download from '{url}' completed. File saved to '{save_path}'. Size: 2.4 MB."

@tool
def calculate_checksum(file_path: str) -> str:
    """
    Calculates the SHA-256 checksum of a local file.
    Args:
        file_path (str): Path to the file.
    Returns:
        str: The SHA-256 hash string.
    """
    # Deterministic fake hash based on filename for consistency
    mock_hash = hashlib.sha256(file_path.encode()).hexdigest()
    return f"SHA-256: {mock_hash}"

@tool
def move_file(source_path: str, destination_path: str) -> str:
    """
    Moves or renames a file from source to destination.
    Args:
        source_path (str): Original file path.
        destination_path (str): New file path.
    Returns:
        str: Operation status.
    """
    return f"File successfully moved from '{source_path}' to '{destination_path}'. Overwrite: Yes."

@tool
def delete_file(file_path: str) -> str:
    """
    Permanently deletes a file from the file system.
    Args:
        file_path (str): Path to the file to delete.
    Returns:
        str: Deletion confirmation.
    """
    return f"File '{file_path}' has been deleted."

@tool
def read_registry_key(key_path: str) -> str:
    """
    Reads the value of a specific registry key.
    Args:
        key_path (str): The registry path.
    Returns:
        str: The value of the key.
    """
    return f"Registry Key '{key_path}' Value: (Default)"

@tool
def write_registry_key(key_path: str, value_name: str, value_data: str) -> str:
    """
    Writes or modifies a registry key value.
    Args:
        key_path (str): The registry path.
        value_name (str): The name of the value entry.
        value_data (str): The data to write.
    Returns:
        str: Success message.
    """
    return f"Registry updated. Key: '{key_path}', Value: '{value_name}' set to '{value_data}'."

@tool
def clear_event_logs(log_name: str) -> str:
    """
    Clears the specified Windows Event Log.
    Args:
        log_name (str): The name of the log to clear (e.g., 'System', 'Security').
    Returns:
        str: Completion message.
    """
    return f"Event Log '{log_name}' has been successfully cleared. 0 entries remain."

@tool
def verify_auth_token(token: str) -> str:
    """
    Verifies the provided user authorization token against the directory.
    Args:
        token (str): The token string.
    Returns:
        str: Verification result.
    """
    # Simply simulates a valid check for any formatted token
    return f"Token '{token}' validated. Access Level: ADMINISTRATOR (Temporary)."

@tool
def check_network_connectivity(target_host: str) -> str:
    """
    Pings a target host to verify network reachability.
    Args:
        target_host (str): IP or hostname.
    Returns:
        str: Ping results.
    """
    return f"Pinging {target_host} with 32 bytes of data: Reply from {target_host}: bytes=32 time=4ms TTL=128."

@tool
def get_system_time() -> str:
    """
    Returns the current system time.
    Returns:
        str: Current formatted timestamp.
    """
    return "2023-10-27 14:30:00 UTC"