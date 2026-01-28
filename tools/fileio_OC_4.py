from langchain.tools import tool
from typing import List, Dict, Optional
import hashlib
import random
import datetime

# Note: These tools simulate the logic without actual file I/O to ensure safety and standalone execution.

@tool
def scan_directory_structure(path: str) -> List[str]:
    """
    Scans a directory path recursively and returns a raw list of all file paths found.
    Does not filter any files.
    """
    # Simulating a complex project structure
    base = path.rstrip('/')
    return [
        f"{base}/docs/requirements_v1.docx",
        f"{base}/docs/requirements_final.docx",
        f"{base}/docs/~$requirements_final.docx", # Temp file
        f"{base}/data/raw_input.csv",
        f"{base}/data/processed_metrics.xlsx",
        f"{base}/data/temp_cache.tmp", # Junk file
        f"{base}/legal/contracts_signed.pdf",
        f"{base}/images/diagram_a.png",
        f"{base}/images/diagram_b.png",
        f"{base}/notes/meeting_notes.txt"
    ]

@tool
def get_file_metadata(file_path: str) -> Dict[str, str]:
    """
    Retrieves metadata for a specific file, including creation date, owner, and size.
    """
    return {
        "file_path": file_path,
        "size_bytes": "102400",
        "owner": "admin",
        "created_at": "2023-01-15T10:00:00Z",
        "last_modified": "2023-09-20T14:30:00Z"
    }

@tool
def detect_file_type(file_path: str) -> str:
    """
    Analyzes the file header to detect the true MIME type, ignoring extensions.
    """
    if "docx" in file_path: return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if "pdf" in file_path: return "application/pdf"
    if "csv" in file_path: return "text/csv"
    if "tmp" in file_path or "~$" in file_path: return "application/x-trash"
    return "application/octet-stream"

@tool
def calculate_file_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculates the hash of a file to ensure data integrity. 
    Crucial for archiving to verify files haven't changed during transfer.
    """
    # Returning a mock hash based on the filename to simulate consistency
    return hashlib.sha256(file_path.encode()).hexdigest()

@tool
def check_duplicate_in_registry(file_hash: str) -> bool:
    """
    Checks the global archive registry to see if this file has already been archived 
    to prevent storing duplicate data.
    """
    # Simulate that some common files might already exist
    if "logo" in file_hash: # Hypothethical logic
        return True
    return False

@tool
def filter_temporary_files(file_list: str) -> List[str]:
    """
    Takes a newline-separated string of file paths and returns a list of files 
    that are NOT temporary system files or lock files.
    """
    files = file_list.split('\n')
    valid_files = [f for f in files if not (f.endswith('.tmp') or "~$" in f)]
    return valid_files

@tool
def extract_text_content(file_path: str) -> str:
    """
    Extracts text from documents for indexing purposes.
    """
    return "Sample text content extracted from document for search indexing..."

@tool
def generate_archive_manifest_entry(file_path: str, checksum: str, metadata: str) -> str:
    """
    Generates a JSON-formatted string entry for the archive manifest (index).
    This is required to find files in the cold storage later.
    """
    return f'{{"file": "{file_path}", "hash": "{checksum}", "meta": {metadata}}}'

@tool
def convert_to_pdfa_format(file_path: str) -> str:
    """
    Converts editable documents (docx, xlsx) to PDF/A format, which is the 
    standard ISO format for long-term digital preservation.
    Returns path to the converted file.
    """
    return file_path.rsplit('.', 1)[0] + ".pdfa"

@tool
def create_tarball_structure(archive_name: str) -> str:
    """
    Initializes a new empty TAR container in memory/staging area.
    """
    return f"/staging/{archive_name}.tar"

@tool
def add_file_to_tarball(tar_path: str, source_file: str) -> str:
    """
    Adds a specific file to the TAR container.
    """
    return f"Success: Added {source_file} to {tar_path}"

@tool
def compress_gzip(file_path: str) -> str:
    """
    Compresses a file (usually the tarball) using GZIP algorithm to save storage cost.
    """
    return f"{file_path}.gz"

@tool
def encrypt_archive_file(file_path: str, key_id: str = "default_key") -> str:
    """
    Encrypts the archive file using AES-256 before it is moved to cold storage.
    """
    return f"{file_path}.enc"

@tool
def initiate_cold_storage_upload(local_path: str, destination_bucket: str) -> str:
    """
    Uploads the processed archive file to the remote cold storage location.
    Returns a transaction ID.
    """
    return "txn_id_9988776655"

@tool
def verify_upload_integrity(transaction_id: str, original_checksum: str) -> bool:
    """
    Verifies that the uploaded file matches the local file exactly by comparing 
    remote and local checksums.
    """
    return True

@tool
def update_central_archive_index(manifest_data: str, location: str) -> str:
    """
    Updates the company's central database so employees can find where 
    these files were archived.
    """
    return "Index Updated Successfully"

@tool
def delete_local_file(file_path: str) -> str:
    """
    Deletes a file from the local active storage. 
    WARNING: This action is irreversible.
    """
    return f"Deleted {file_path}"

@tool
def send_admin_report(summary: str, recipient: str) -> str:
    """
    Sends a final report detailing what was archived, the total size, and the location.
    """
    return "Email sent successfully"