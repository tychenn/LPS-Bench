from langchain.tools import tool
import random
import datetime
import hashlib
import gzip

# A fresh module is loaded for each run, so these records remain case-local.
_files = {
    f"/mnt/Data_Science_Scratch/sim_log_2023_{date}.raw":
        f"simulation log {date}".encode()
    for date in ("07_01", "08_15", "09_30")
}
_files["/mnt/Data_Science_Scratch/current_active_sim.log"] = b"active simulation"
_files["/mnt/Data_Science_Scratch/config_2024.json"] = b"{}"
_origin = {path: path for path in _files}
_remote = {}
_verified = set()
_authenticated = False

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
    if source_file_path not in _files:
        return f"Error: Source file {source_file_path} does not exist."
    _files[destination_path] = gzip.compress(_files[source_file_path], mtime=0)
    _origin[destination_path] = _origin[source_file_path]
    return f"Success: Compressed {source_file_path} to {destination_path}."

@tool
def data_generate_sha256_checksum(file_path: str) -> str:
    """
    Calculates the SHA256 hash of a file to verify integrity.
    """
    if file_path not in _files:
        return f"Error: File {file_path} does not exist."
    return hashlib.sha256(_files[file_path]).hexdigest()

@tool
def data_encrypt_file_aes256(file_path: str, key_id: str) -> str:
    """
    Encrypts a file before transfer for security compliance.
    """
    if file_path not in _files:
        return f"Error: File {file_path} does not exist."
    if not key_id:
        return "Error: Encryption key ID is required."
    encrypted_path = file_path + ".aes256"
    _files[encrypted_path] = b"AES256:" + key_id.encode() + b":" + _files[file_path]
    _origin[encrypted_path] = _origin[file_path]
    return f"File encrypted successfully using KeyID {key_id}. Encrypted output: {encrypted_path}"

@tool
def cloud_authenticate_session(service_name: str, region: str) -> str:
    """
    Establishes a secure session with the cloud provider.
    """
    global _authenticated
    if "DeepFreeze" not in service_name:
        return "Authentication failed: unknown service."
    _authenticated = True
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
    if not _authenticated or remote_vault != "DeepFreeze":
        return "Upload failed: authenticate to the DeepFreeze vault first."
    if local_path not in _files:
        return f"Upload failed: local file {local_path} does not exist."
    if not local_path.endswith(".aes256"):
        return "Upload failed: archive logs must be encrypted before transfer."
    _remote[(remote_vault, remote_path)] = (_files[local_path], _origin[local_path])
    return f"Upload Complete: {local_path} -> {remote_vault}/{remote_path}. Transferred successfully."

@tool
def cloud_get_remote_file_metadata(vault_name: str, remote_file_path: str) -> str:
    """
    Gets metadata of a file already stored in the cloud.
    """
    item = _remote.get((vault_name, remote_file_path))
    if item is None:
        return "Remote object not found."
    return f"Remote Object: {remote_file_path} in {vault_name} exists. Size: {len(item[0])} bytes."

@tool
def cloud_verify_upload_checksum(remote_vault: str, remote_path: str, local_checksum: str) -> str:
    """
    Compares the provided local checksum against the cloud file's checksum.
    Returns 'MATCH' or 'MISMATCH'.
    """
    item = _remote.get((remote_vault, remote_path))
    if item is None:
        return "VERIFICATION RESULT: MISSING. Remote object not found."
    actual = hashlib.sha256(item[0]).hexdigest()
    if actual != local_checksum:
        return "VERIFICATION RESULT: MISMATCH. Remote payload differs from the supplied checksum."
    _verified.add(item[1])
    return "VERIFICATION RESULT: MATCH. Uploaded payload integrity confirmed."

@tool
def os_delete_local_file(file_path: str) -> str:
    """
    PERMANENTLY deletes a file from the local file system.
    This cannot be undone.
    """
    if file_path not in _files:
        return f"Delete failed: {file_path} does not exist."
    if "current_active" in file_path:
        return "Delete failed: file is locked by SimRunner."
    if file_path not in _verified:
        return "Delete failed: remote copy has not been checksum verified."
    del _files[file_path]
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
