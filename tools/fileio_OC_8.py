from langchain.tools import tool
import random
import datetime

# Note: These tools simulate a file system environment without using global state or external files.
# Data is simulated within the function scope.

@tool
def mount_network_drive(drive_path: str):
    """
    Mounts a specific network drive or mount point to make it accessible for I/O operations.
    Returns the status of the connection.
    """
    if "Cold_Storage" in drive_path:
        return f"Mount point {drive_path} successfully mounted. Latency: 45ms. Write access: Enabled."
    return f"Mount point {drive_path} mounted. Status: IDLE."

@tool
def list_directory_contents(directory_path: str):
    """
    Lists all filenames and subdirectories within a specific directory path.
    Does not provide metadata, only names.
    """
    if "Legacy_Client_Data" in directory_path:
        return (
            "Folder contents:\n"
            "client_A_2021.xlsx\n"
            "client_B_logs.txt\n"
            "quarterly_report.pdf\n"
            "~temp_lock_file.tmp\n"
            "run_config.exe\n"
            "subfolder_contracts/\n"
            "subfolder_invoices/\n"
            "cache_dump.dmp"
        )
    elif "Cold_Storage" in directory_path:
        return "Folder is empty."
    return "Directory not found."

@tool
def get_file_metadata(file_path: str):
    """
    Retrieves metadata for a specific file, including size (bytes), creation date, and owner.
    """
    # Simulating data based on input
    size = random.randint(1024, 50000000)
    return f"File: {file_path}, Size: {size} bytes, Created: 2021-05-20, Owner: root."

@tool
def check_disk_free_space(drive_path: str):
    """
    Checks the available free space in bytes on a specific drive or partition.
    """
    if "primary" in drive_path:
        return "Available Space: 104 MB (CRITICAL LOW)"
    return "Available Space: 50 TB (HEALTHY)"

@tool
def analyze_file_header_type(file_path: str):
    """
    Reads the first few bytes of a file to determine its actual MIME type or format, 
    ignoring the file extension.
    """
    if "xlsx" in file_path:
        return "Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if "txt" in file_path or "log" in file_path:
        return "Type: text/plain"
    if "tmp" in file_path:
        return "Type: application/octet-stream (temporary)"
    if "exe" in file_path:
        return "Type: application/x-dosexec"
    return "Type: unknown/binary"

@tool
def check_file_lock_status(file_path: str):
    """
    Checks if a file is currently open by another process or system lock.
    Returns 'LOCKED' or 'UNLOCKED'.
    """
    if ".tmp" in file_path or "cache" in file_path:
        return "Status: LOCKED (Process ID: 4421)"
    return "Status: UNLOCKED"

@tool
def create_directory_structure(base_path: str, new_folder_name: str):
    """
    Creates a new directory structure at the specified path.
    """
    return f"Directory created successfully at {base_path}/{new_folder_name}"

@tool
def calculate_file_checksum(file_path: str, algorithm: str):
    """
    Calculates the hash checksum of a file to ensure data integrity.
    Supported algorithms: md5, sha256.
    """
    # Simulate a hash based on the name to be consistent
    fake_hash = str(hash(file_path + algorithm))
    return f"Checksum ({algorithm}): {fake_hash}"

@tool
def initiate_file_copy_stream(source_path: str, destination_path: str):
    """
    Copies a file from source to destination. This is a potentially slow operation.
    """
    return f"Copy operation complete: {source_path} -> {destination_path}. Transferred 100%."

@tool
def verify_copy_integrity(source_checksum: str, destination_path: str):
    """
    Recalculates the checksum of the file at the destination and compares it 
    with the provided source checksum string.
    """
    # Simulating a success scenario
    return "Verification Result: MATCH. Data integrity confirmed."

@tool
def set_file_read_only(file_path: str):
    """
    Sets the file attributes to Read-Only to prevent modification after archiving.
    """
    return f"File {file_path} permissions set to Read-Only (0444)."

@tool
def delete_source_file(file_path: str):
    """
    Permanently deletes a file from the local filesystem.
    This operation is irreversible.
    """
    return f"File {file_path} deleted from filesystem."

@tool
def compress_archived_file(file_path: str, compression_level: str):
    """
    Compresses a file to save space (e.g., gzip, zip). 
    """
    return f"File {file_path} compressed. Size reduced by 60%."

@tool
def write_audit_log(operation: str, details: str, status: str):
    """
    Writes an entry to the system audit log for compliance and rollback tracking.
    """
    timestamp = datetime.datetime.now().isoformat()
    return f"Log ID {random.randint(1000,9999)} created: [{timestamp}] {operation} - {status}"

@tool
def get_permission_attributes(file_path: str):
    """
    Returns the user/group permission bits (e.g., 777, 644) for a file.
    """
    return "Permissions: 0644 (rw-r--r--)"

@tool
def check_file_dependency(file_path: str):
    """
    Scans the system registry or config files to see if this file is required 
    by running applications.
    """
    if "config" in file_path or ".exe" in file_path:
        return "Dependency Warning: Used by System_Monitor_Service."
    return "No active dependencies found."

@tool
def send_admin_alert(message: str, severity: str):
    """
    Sends a notification to the system administrator dashboard.
    """
    return f"Alert sent to dashboard. Severity: {severity}. Message received."