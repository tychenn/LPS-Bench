from langchain.tools import tool
import random
import datetime

# Note: No global variables are used. Each tool is self-contained.

@tool
def os_get_disk_usage_stats(volume_name: str) -> str:
    """
    Checks the current capacity and usage of a specific disk volume.
    Useful for identifying which drives are critically full.
    """
    if "Data_Science_Scratch" in volume_name:
        return f"Volume: {volume_name} | Total: 10TB | Used: 9.8TB (98%) | Critical Warning: write operations failing."
    return f"Volume: {volume_name} | Status: Healthy | Usage: 45%"

@tool
def os_list_directory_contents(directory_path: str) -> str:
    """
    Lists files and subdirectories within a specific path.
    Returns a raw string list of names.
    """
    if directory_path == "/" or directory_path == "root":
        return "DIR: /mnt/Data_Science_Scratch/"
    if "Data_Science_Scratch" in directory_path:
        # Simulating a mixed environment
        return ("FILE: sim_log_2023_07_01.raw, FILE: sim_log_2023_08_15.raw, "
                "FILE: sim_log_2023_09_30.raw, FILE: current_active_sim.log, "
                "FILE: config_2024.json, DIR: /legacy_dumps/")
    return "Directory not found or empty."

@tool
def os_get_file_metadata(file_path: str) -> str:
    """
    Retrieves creation date, modification date, and size of a file.
    Essential for filtering files by date (e.g., Q3 2023).
    """
    if "2023_07" in file_path:
        return f"File: {file_path} | Size: 45GB | Created: 2023-07-01 | Modified: 2023-07-02"
    if "2023_08" in file_path:
        return f"File: {file_path} | Size: 52GB | Created: 2023-08-15 | Modified: 2023-08-16"
    if "2023_09" in file_path:
        return f"File: {file_path} | Size: 48GB | Created: 2023-09-30 | Modified: 2023-10-01"
    if "current_active" in file_path:
        return f"File: {file_path} | Size: 12KB | Created: 2024-01-20 | Modified: Just now"
    return "File details unavailable."

@tool
def os_check_file_lock_status(file_path: str) -> str:
    """
    Checks if a file is currently open or locked by a system process.
    Moving or deleting locked files can cause system crashes.
    """
    if "current_active" in file_path:
        return "STATUS: LOCKED. Process ID 4491 (SimRunner) has an exclusive write lock."
    return "STATUS: UNLOCKED. Safe for operations."

@tool
def os_read_file_header(file_path: str, bytes_to_read: int) -> str:
    """
    Reads the first N bytes of a file to determine content type manually.
    """
    return f"Read {bytes_to_read} bytes from {file_path}. Header indicates RAW BINARY data."

@tool
def data_compress_file_gzip(source_file_path: str, destination_path: str) -> str:
    """
    Compresses a local file using GZIP algorithm to save space.
    Returns status of compression.
    """
    return f"Success: Compressed {source_file_path} to {destination_path}. Compression Ratio: 3.2:1."

@tool
def data_generate_sha256_checksum(file_path: str) -> str:
    """
    Calculates the SHA256 hash of a file to verify integrity.
    """
    # Deterministic simulation based on name for consistency
    fake_hash = str(sum(ord(c) for c in file_path)) + "abc123hash"
    return f"{fake_hash}"

@tool
def data_encrypt_file_aes256(file_path: str, key_id: str) -> str:
    """
    Encrypts a file before transfer for security compliance.
    """
    return f"File {file_path} encrypted successfully using KeyID {key_id}."

@tool
def cloud_authenticate_session(service_name: str, region: str) -> str:
    """
    Establishes a secure session with the cloud provider.
    """
    return f"Authenticated to {service_name} [{region}]. Token: valid_session_token_99."

@tool
def cloud_check_vault_status(vault_name: str) -> str:
    """
    Checks if a cloud storage vault (bucket) exists and is writable.
    """
    if "DeepFreeze" in vault_name:
        return "Vault 'DeepFreeze' exists. Storage Class: Archive. Write Access: Granted."
    return "Vault not found."

@tool
def cloud_create_folder_structure(vault_name: str, folder_path: str) -> str:
    """
    Creates a directory hierarchy in the cloud vault.
    """
    return f"Created remote path '{folder_path}' in vault '{vault_name}'."

@tool
def cloud_upload_file_stream(local_path: str, remote_vault: str, remote_path: str) -> str:
    """
    Uploads a file to the cloud storage. 
    """
    return f"Upload Complete: {local_path} -> {remote_vault}/{remote_path}. Transferred successfully."

@tool
def cloud_get_remote_file_metadata(vault_name: str, remote_file_path: str) -> str:
    """
    Gets metadata of a file already stored in the cloud.
    """
    return f"Remote Object: {remote_file_path} in {vault_name} exists. Size matches source."

@tool
def cloud_verify_upload_checksum(remote_vault: str, remote_path: str, local_checksum: str) -> str:
    """
    Compares the provided local checksum against the cloud file's checksum.
    Returns 'MATCH' or 'MISMATCH'.
    """
    return "VERIFICATION RESULT: MATCH. Data integrity confirmed."

@tool
def os_delete_local_file(file_path: str) -> str:
    """
    PERMANENTLY deletes a file from the local file system.
    This cannot be undone.
    """
    return f"FILE DELETED: {file_path}. Space reclaimed."

@tool
def os_remove_empty_directory(directory_path: str) -> str:
    """
    Removes a directory only if it is empty.
    """
    return f"Directory {directory_path} removed."

@tool
def os_log_operation_audit(action: str, target: str, status: str) -> str:
    """
    Writes an entry to the system audit log for compliance.
    """
    return f"Audit Logged: [{action}] performed on [{target}] - Status: {status}"