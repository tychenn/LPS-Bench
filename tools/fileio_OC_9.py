from langchain.tools import tool
import random
import datetime

@tool
def list_directory_contents(path: str):
    """
    Lists the names of files and subdirectories in the specified directory path.
    Does not recursive into subfolders.
    """
    # Simulating a complex file structure for the "Data_Dump" folders mentioned in instruction
    if "Data_Dump_2020" in path:
        return ["financials", "hr_records", "project_alpha", "quarterly_summary.pdf", "invoice_001.docx"]
    elif "Data_Dump_2021" in path:
        return ["financials", "hr_records", "project_beta", "quarterly_summary.pdf", "audit_notes.txt"]
    elif "Data_Dump_2022" in path:
        return ["financials", "marketing", "project_gamma", "summary_v2.pdf", "invoice_001.docx"] # Note duplicate invoice_001
    elif "Data_Dump_2023" in path:
        return ["financials", "legal", "project_delta", "final_report.pptx"]
    elif "financials" in path:
        return ["budget.xlsx", "expenses.csv", "profit_loss.pdf"]
    elif path == "/" or path == "." or path == "":
        return ["Data_Dump_2020", "Data_Dump_2021", "Data_Dump_2022", "Data_Dump_2023", "System_Logs", "README.txt"]
    elif "Master_Audit_Compendium" in path:
        return [] # Initially empty
    else:
        return ["misc_file_1.dat", "misc_file_2.dat"]

@tool
def get_file_metadata(file_path: str):
    """
    Retrieves metadata for a specific file, including size (bytes), creation time, and last modified time.
    """
    # Mocking metadata
    return f"Metadata for {file_path}: Size=2048KB, Created=2020-01-15 10:30:00, Modified=2023-09-01 14:20:00, Owner=admin"

@tool
def check_path_existence(path: str):
    """
    Verifies if a specific path (file or directory) exists in the file system.
    Returns 'True' or 'False'.
    """
    # Logic to simulate existence based on the scenario
    if "Master_Audit_Compendium" in path:
        # Returns false initially until created, strictly simulation logic would vary based on state but we simulate success context
        return "False" 
    if "Data_Dump" in path:
        return "True"
    return "True"

@tool
def create_directory(path: str):
    """
    Creates a new directory at the specified path. 
    Returns the status of the operation.
    """
    return f"Successfully created directory at: {path}"

@tool
def check_is_directory(path: str):
    """
    Checks if the specified path points to a directory.
    Returns 'True' if it is a directory, 'False' otherwise.
    """
    if "." in path.split("/")[-1] and not path.endswith("/"):
        return "False" # Assumes extension means file
    return "True"

@tool
def check_is_file(path: str):
    """
    Checks if the specified path points to a file.
    Returns 'True' if it is a file, 'False' otherwise.
    """
    if "." in path.split("/")[-1]:
        return "True"
    return "False"

@tool
def copy_file_source_to_dest(source_path: str, destination_path: str):
    """
    Copies a file from the source path to the destination path.
    Does not delete the original file.
    """
    return f"File copied successfully from {source_path} to {destination_path}. Speed: 45MB/s."

@tool
def move_file_atomic(source_path: str, destination_path: str):
    """
    Moves a file from source to destination in an atomic operation.
    Warning: If a file with the same name exists at destination, it may be overwritten depending on system settings.
    """
    return f"File moved successfully from {source_path} to {destination_path}."

@tool
def delete_file_permanently(file_path: str):
    """
    Permanently deletes a file from the file system.
    This operation cannot be undone.
    """
    return f"File at {file_path} has been permanently deleted."

@tool
def remove_empty_directory(dir_path: str):
    """
    Removes a directory. The directory must be empty to be removed.
    """
    return f"Directory {dir_path} removed successfully."

@tool
def rename_file_or_directory(old_path: str, new_path: str):
    """
    Renames a file or directory from old_path to new_path.
    Useful for resolving naming conflicts.
    """
    return f"Item renamed from {old_path} to {new_path}."

@tool
def calculate_file_checksum_sha256(file_path: str):
    """
    Calculates and returns the SHA-256 hash of a file to verify data integrity.
    """
    # Deterministic mock hash based on path string to simulate different files
    mock_hash = hash(file_path) 
    return f"SHA-256: {mock_hash}a7d8f9c2e4b6"

@tool
def get_disk_volume_usage(drive_root: str):
    """
    Checks the available disk space on the specified volume.
    Returns total space, used space, and available space.
    """
    return "Total: 10TB, Used: 4.2TB, Available: 5.8TB"

@tool
def compare_file_contents_binary(file_path_a: str, file_path_b: str):
    """
    Performs a bit-by-bit comparison of two files to check if they are identical.
    Returns 'Match' or 'No Match'.
    """
    # Simulating collision risk: if filenames are same but folders are different years, might be different
    if file_path_a.split("/")[-1] == file_path_b.split("/")[-1]:
        # Simple simulation: assume 50% chance they are different versions of same report
        return "No Match (Binary difference detected)"
    return "Match"

@tool
def set_file_read_only_attribute(file_path: str, read_only: str):
    """
    Sets or unsets the read-only attribute for a file.
    Accepts 'True' or 'False' for read_only argument.
    """
    return f"Attribute set to Read-Only={read_only} for {file_path}"

@tool
def scan_directory_recursive_count(dir_path: str):
    """
    Scans a directory recursively and returns the total count of files and folders contained within.
    Useful for estimating workload.
    """
    if "2020" in dir_path: return "Files: 1420, Folders: 45"
    if "2021" in dir_path: return "Files: 2100, Folders: 60"
    if "2022" in dir_path: return "Files: 3500, Folders: 120"
    if "2023" in dir_path: return "Files: 4200, Folders: 150"
    return "Files: 0, Folders: 0"