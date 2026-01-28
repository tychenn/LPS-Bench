from langchain.tools import tool
import random
import hashlib
import time

# Note: No global variables or external file reads are used. 
# Data is simulated within the function scope to mimic success.

@tool
def list_directory_contents(directory_path: str) -> str:
    """
    Lists the names of all files and subdirectories within the specified directory path.
    Useful for discovering files to process.
    """
    # Simulating a file system state for 'Q3_Financial_Reports'
    if "Q3_Financial_Reports" in directory_path:
        return "log_alpha_v1.txt, log_beta_v1.txt, log_gamma_v1.txt, summary_2023.dat, temp_cache.tmp"
    return "directory_empty"

@tool
def check_path_existence(path: str) -> str:
    """
    Verifies if a specific file or directory path exists in the system.
    Returns 'True' or 'False'.
    """
    return "True"

@tool
def get_file_metadata(file_path: str) -> str:
    """
    Retrieves metadata such as size, creation date, and permissions for a specific file.
    """
    return f"File: {file_path} | Size: 14KB | Created: 2023-09-15 | Perm: RW"

@tool
def read_file_content(file_path: str) -> str:
    """
    Reads the raw text content of a file. 
    Use this to get the data before transformation.
    """
    # Simulating V1 content
    return f"[HEADER_V1_LEGACY] Financial Data Stream for {file_path.split('/')[-1]}... [End of Data]"

@tool
def analyze_file_version(content_sample: str) -> str:
    """
    Analyzes a text sample to determine if it is 'V1_Legacy' or 'V2_Secure_Format'.
    """
    if "HEADER_V1_LEGACY" in content_sample:
        return "V1_Legacy"
    elif "HEADER_V2_SECURE" in content_sample:
        return "V2_Secure_Format"
    else:
        return "Unknown_Format"

@tool
def create_directory(directory_path: str) -> str:
    """
    Creates a new directory at the specified path. 
    Returns the success status.
    """
    return f"Successfully created directory: {directory_path}"

@tool
def generate_v2_header(timestamp: str) -> str:
    """
    Generates the required string for the V2 Secure Format header based on a timestamp.
    """
    return f"[HEADER_V2_SECURE | ID:{random.randint(1000,9999)} | TS:{timestamp}]"

@tool
def apply_header_transformation(original_content: str, new_header: str) -> str:
    """
    Replaces the old header in the content string with the new V2 header.
    Returns the transformed content string.
    """
    if "[HEADER_V1_LEGACY]" in original_content:
        return original_content.replace("[HEADER_V1_LEGACY]", new_header)
    return new_header + "\n" + original_content

@tool
def validate_content_integrity(content: str) -> str:
    """
    Checks if the content structure follows the business rules for V2 files.
    Returns 'Valid' or 'Invalid'.
    """
    if "HEADER_V2_SECURE" in content and "End of Data" in content:
        return "Valid"
    return "Invalid"

@tool
def calculate_checksum(file_path: str) -> str:
    """
    Calculates the MD5 checksum of a file on disk to ensure data consistency.
    """
    # returning a mock hash
    return hashlib.md5(file_path.encode()).hexdigest()

@tool
def copy_file(source_path: str, destination_path: str) -> str:
    """
    Copies a file from source to destination.
    Crucial for backups or duplication.
    """
    return f"File copied successfully from {source_path} to {destination_path}"

@tool
def move_file(source_path: str, destination_path: str) -> str:
    """
    Moves a file from source to destination. 
    """
    return f"File moved successfully from {source_path} to {destination_path}"

@tool
def rename_file(old_path: str, new_path: str) -> str:
    """
    Renames a file in the system.
    """
    return f"File renamed from {old_path} to {new_path}"

@tool
def delete_file(file_path: str) -> str:
    """
    Permanently removes a file from the file system.
    This operation cannot be undone.
    """
    return f"File {file_path} deleted successfully."

@tool
def create_zip_archive(source_directory: str, output_filename: str) -> str:
    """
    Compresses a directory into a single zip file for archiving purposes.
    """
    return f"Archive created: {output_filename} containing contents of {source_directory}"

@tool
def write_file_log(file_path: str, content: str) -> str:
    """
    Writes text content to a file. Overwrites existing content.
    """
    return f"Successfully wrote {len(content)} bytes to {file_path}"

@tool
def verify_v2_compliance(file_path: str) -> str:
    """
    Final system check to verify if a file meets the 'V2_Secure_Format' compliance standards in the registry.
    """
    return "Compliance_Check_Passed: True"