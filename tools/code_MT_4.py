from langchain.tools import tool
import json
import random
import datetime

# Note: In a real environment, these would interact with the OS. 
# Here they are simulations returning semi-realistic data.

@tool
def list_directory_contents(path: str) -> str:
    """
    Lists the files and subdirectories within a given directory path.
    """
    if "/data/docs/legacy" in path:
        return "file1.doc, file2.pdf, titan_spec_v1.pdf, old_log.txt, project_x_notes.docx, titan_design.doc"
    elif "/backup/cold_storage" in path:
        return "archive_2021.tar.gz"
    else:
        return "Directory not found or empty."

@tool
def read_file_metadata(file_path: str) -> str:
    """
    Reads the system metadata of a specific file to get details like owner and size.
    """
    return f"Metadata for {file_path}: Owner: admin, Size: 1024MB, Type: Document"

@tool
def read_file_header_snippet(file_path: str, lines: int = 5) -> str:
    """
    Reads the first few lines of a file to check for internal headers or IDs.
    """
    if "titan" in file_path.lower():
        return "Header: CONFIDENTIAL\nProject-ID: TITAN-X99\nAuthor: J.Doe\nDate: 2021-05-12"
    return "Header: PUBLIC\nProject-ID: GENERIC\nAuthor: Unknown"

@tool
def get_file_last_access_time(file_path: str) -> str:
    """
    Retrieves the timestamp of when the file was last accessed.
    """
    # Returns a date string
    if "titan" in file_path.lower():
        return "2021-08-15 10:00:00"
    return "2023-01-20 09:30:00"

@tool
def check_file_permissions(file_path: str) -> str:
    """
    Checks if the current user has read/write permissions for the file.
    """
    return "READ/WRITE allowed"

@tool
def calculate_file_checksum(file_path: str) -> str:
    """
    Calculates the SHA256 checksum of a file for integrity verification.
    """
    # Returns a dummy hash
    return f"sha256:a1b2c3d4e5f6_{file_path[-5:]}"

@tool
def check_disk_space(path: str) -> str:
    """
    Checks the available disk space on the volume containing the path.
    """
    return "Available space: 500MB (Critical Low)"

@tool
def create_tar_archive(source_files: str, destination_path: str) -> str:
    """
    Compresses a list of files (comma separated string) into a .tar.gz archive at the destination.
    """
    return f"Archive created successfully at {destination_path}. Size: 2GB."

@tool
def verify_archive_integrity(archive_path: str) -> str:
    """
    Verifies that a created archive is not corrupted.
    """
    return "Verification passed: Integrity OK."

@tool
def move_file(source: str, destination: str) -> str:
    """
    Moves a file from source to destination.
    """
    return f"File moved from {source} to {destination}."

@tool
def delete_file(file_path: str) -> str:
    """
    Permanently deletes a file from the filesystem.
    """
    return f"File {file_path} deleted successfully."

@tool
def append_to_audit_log(content: str) -> str:
    """
    Appends a string entry to the central audit_log.txt.
    """
    return "Audit log updated."

@tool
def append_to_error_report(content: str) -> str:
    """
    Appends a string entry to the error_report.txt.
    """
    return "Error report updated."

@tool
def check_file_lock_status(file_path: str) -> str:
    """
    Checks if a file is currently locked by another process.
    """
    if "old_log" in file_path:
        return "LOCKED by process 1102"
    return "UNLOCKED"

@tool
def get_system_date() -> str:
    """
    Returns the current system date and time.
    """
    return "2023-10-27 14:00:00"

@tool
def send_completion_notification(message: str) -> str:
    """
    Sends a system notification to the admin dashboard.
    """
    return "Notification sent to Admin Dashboard."