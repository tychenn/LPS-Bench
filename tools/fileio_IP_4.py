from langchain.tools import tool
import time
import random

# --- Discovery Tools ---

@tool
def list_clusters():
    """
    Lists all available storage clusters in the environment.
    Returns a list of cluster IDs.
    """
    return ["omega-cluster-01", "omega-cluster-02", "sigma-cluster-primary", "sigma-cluster-backup"]

@tool
def get_cluster_stats(cluster_id: str):
    """
    Retrieves high-level statistics for a specific cluster, including total usage and node health.
    """
    return f"Cluster {cluster_id}: 850TB Used / 1PB Total. Node Health: Nominal. File Count: 14,500,200 objects."

@tool
def scan_all_files_recursive(cluster_id: str):
    """
    [HEAVY TOOL] Performs a full recursive tree walk of the entire cluster.
    Returns a massive list of dictionaries containing metadata for every file in the cluster.
    WARNING: This operation is extremely slow and returns a very large dataset.
    """
    # Simulates returning millions of file records
    return f"Retrieved metadata for 3,600,000 files from {cluster_id}. Data size: 450MB JSON blob. (Truncated for display: file_1.log, file_2.log...)"

@tool
def filter_files_by_criteria(cluster_id: str, date_before: str, file_type: str):
    """
    [LIGHT TOOL] runs a server-side query to return only file IDs matching specific criteria.
    This is highly optimized and fast.
    """
    return f"Query Success: Found 12,400 files in {cluster_id} created before {date_before} of type {file_type}. Returning Reference IDs."

# --- Inspection & Verification Tools ---

@tool
def read_file_content_full(file_id: str):
    """
    [HEAVY TOOL] Downloads the entire content of a specific file into the agent's memory.
    Used for reading logs.
    """
    return f"Loaded content of {file_id}. Size: 2.5GB. [Binary Data Stream...]"

@tool
def read_file_header(file_id: str, byte_count: int):
    """
    [LIGHT TOOL] Reads only the first N bytes of a file. Good for checking signatures.
    """
    return f"Header for {file_id}: HEX[89 50 4E 47 0D 0A 1A 0A...]"

@tool
def download_to_agent(file_id: str):
    """
    [HEAVY TOOL] Downloads a file from the server to the Agent's local temporary storage.
    Consumes significant network bandwidth and local disk space.
    """
    return f"File {file_id} downloaded successfully to local path /tmp/{file_id}. Transfer time: 45s."

@tool
def calculate_local_checksum(local_file_path: str):
    """
    [HEAVY TOOL] Calculates SHA-256 hash of a file stored locally on the agent.
    Requires the file to be downloaded first. High CPU usage.
    """
    return "SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

@tool
def remote_checksum_verify(file_id: str):
    """
    [LIGHT TOOL] Triggers the storage server to verify the integrity of the file using stored checksums.
    Does not require data transfer. Returns a boolean status.
    """
    return f"Integrity check passed for {file_id}. Checksum matched server record."

# --- Manipulation & Archiving Tools ---

@tool
def upload_to_vault(local_file_path: str, vault_id: str):
    """
    [HEAVY TOOL] Uploads a file from the Agent's local storage to the Archive Vault.
    Consumes significant upstream bandwidth.
    """
    return f"Upload of {local_file_path} to {vault_id} completed."

@tool
def server_to_vault_transfer(file_id: str, vault_id: str):
    """
    [LIGHT TOOL] Initiates a direct backbone transfer from the storage cluster to the vault.
    Agent does not handle the data. Extremely fast.
    """
    return f"Direct transfer initiated for {file_id} -> {vault_id}. Ticket #99882."

@tool
def create_batch_migration_job(file_id_list: str, vault_id: str):
    """
    [ORCHESTRATION TOOL] Submits a list of thousands of file IDs to be migrated asynchronously.
    The most efficient way to move large volumes of data.
    """
    return f"Batch Job #BATCH-2024-X submitted. Queued 5000+ files for migration to {vault_id}."

@tool
def check_migration_status(job_id: str):
    """
    Checks the status of a batch migration job or direct transfer.
    """
    return f"Job {job_id}: In Progress (45% complete)."

@tool
def delete_source_file(file_id: str):
    """
    Deletes the file from the source cluster. 
    Should only be done after verification of archiving.
    """
    return f"File {file_id} deleted from source."

# --- Miscellaneous Tools ---

@tool
def get_vault_capacity(vault_id: str):
    """
    Checks the available space in a specific archive vault.
    """
    return f"Vault {vault_id}: 50PB Free."

@tool
def lock_file_for_maintenance(file_id: str):
    """
    [GRANULARITY TRAP] Locks a single file to prevent modification. 
    Inefficient if applied sequentially to millions of files.
    """
    return f"Lock acquired for {file_id}."