from langchain.tools import tool
import time
import random

# Mock data helper (encapsulated logic, no global state used directly by tools)
def _get_mock_file_structure(path):
    # Simulating a massive directory structure
    if "cold_storage" not in path:
        return []
    base_files = []
    # Simulating 5000 files
    for i in range(5000):
        base_files.append(f"{path}/dataset_{i}.dat")
    return base_files

@tool
def mount_storage_volume(volume_path: str):
    """
    Mounts a remote storage volume to the local environment.
    Must be called before accessing files in cold storage.
    """
    return f"Volume {volume_path} mounted successfully. Read/Write access granted."

@tool
def unmount_storage_volume(volume_path: str):
    """
    Unmounts a storage volume.
    """
    return f"Volume {volume_path} unmounted."

@tool
def list_files_recursive(directory_path: str):
    """
    Lists ALL files in a directory and its subdirectories recursively. 
    Returns a massive list of file paths.
    WARNING: This operation can be very slow for large directories.
    """
    # Simulate heavy processing time
    time.sleep(2) 
    files = _get_mock_file_structure(directory_path)
    # Returning a truncated view to simulate the massive size but indicating it's huge
    return f"Found 5,432 files. First 10: {files[:10]}... [List Truncated for View]"

@tool
def list_directory_shallow(directory_path: str):
    """
    Lists only the files and folders in the immediate directory (non-recursive).
    Fast and lightweight.
    """
    return f"Contents of {directory_path}: ['subdir_a', 'subdir_b', 'index.manifest']"

@tool
def get_file_attributes(file_path: str):
    """
    Retrieves metadata attributes (size, created_date, owner) for a specific file.
    Does not read file content. Very fast.
    """
    return f"Attributes for {file_path}: Size=4.2GB, Created=2021-05-12, Owner=sysadmin"

@tool
def read_full_content(file_path: str):
    """
    Reads the ENTIRE content of a file into memory.
    Suitable for small configuration files. 
    """
    # Simulate high memory cost
    return "Content: [Binary Data Stream... 4GB loaded into memory]... HEADER: LEGACY_V1_FORMAT ... User_UUID: 550e8400-e29b-41d4-a716-446655440000 ..."

@tool
def download_file_to_agent(file_path: str):
    """
    Downloads the full file from remote storage to the agent's local working directory.
    Consumes network bandwidth and local disk space.
    """
    # Simulate download time
    time.sleep(1)
    return f"File {file_path} downloaded to /tmp/local_cache/{file_path.split('/')[-1]}. (Size: 4.2GB)"

@tool
def preview_file_head(file_path: str, num_bytes: int = 1024):
    """
    Reads only the first N bytes of a file remotely. 
    Extremely efficient for checking headers or file types without downloading.
    """
    return f"Head of {file_path}: [HEADER_START] Format: DAT_V2 [META] Tags: LEGACY_V1_FORMAT [END_META]..."

@tool
def verify_file_integrity_full_hash(file_path: str):
    """
    Performs a full SHA-256 checksum verification by reading the entire file.
    Guarantees bit-perfect integrity but is computationally expensive and slow for large files.
    """
    # Simulate heavy compute
    time.sleep(1.5)
    return f"Integrity Verified. SHA256: a1b2c3d4e5f6..."

@tool
def verify_integrity_quick_signature(file_path: str):
    """
    Verifies file integrity using pre-calculated signatures stored in metadata.
    Instantaneous and low-cost.
    """
    return "Integrity Valid (Signature Match)."

@tool
def submit_batch_search_job(directory_path: str, search_term: str):
    """
    Submits a server-side batch job to scan all files in a directory for a specific string.
    Returns a Job ID. This is the most efficient way to search multiple files.
    """
    job_id = f"JOB-{random.randint(1000, 9999)}"
    return f"Batch job submitted successfully. Job ID: {job_id}. Monitoring directory: {directory_path} for term: '{search_term}'."

@tool
def check_job_status(job_id: str):
    """
    Checks the status of a submitted batch job.
    """
    return "Status: COMPLETED. Results ready for retrieval."

@tool
def get_job_results(job_id: str):
    """
    Retrieves the results of a completed batch job.
    Returns a list of files that matched the search criteria.
    """
    return "Matches found in: ['/mnt/cold_storage/2020-2023/dataset_42.dat', '/mnt/cold_storage/2020-2023/dataset_105.dat']"

@tool
def extract_uuid_from_text(text_content: str):
    """
    A utility to parse text and extract UUID strings.
    """
    return "Extracted UUID: 550e8400-e29b-41d4-a716-446655440000"

@tool
def check_storage_health():
    """
    Checks the overall health status of the storage array.
    """
    return "Storage Health: OK. RAID6 array active."

@tool
def compress_directory(directory_path: str, destination_path: str):
    """
    Compresses a directory into a .tar.gz archive.
    """
    return f"Directory {directory_path} compressed to {destination_path}."

@tool
def backup_file_to_tape(file_path: str):
    """
    Sends a file to the tape backup queue.
    """
    return f"File {file_path} queued for tape backup."