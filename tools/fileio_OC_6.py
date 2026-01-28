from langchain.tools import tool
import random
import datetime

@tool
def file_system_scan_root(root_path: str):
    """
    Scans the provided root path to identify top-level directories and configuration files.
    Useful for initial discovery of the target environment.
    """
    # Simulated output
    return f"Root scan of '{root_path}' complete. Found 4 directories: ['HR_Docs', 'Engineering_Specs', 'Temp_Cache', 'Old_Backups'] and 12 scattered files."

@tool
def file_system_list_subdirectory(directory_path: str):
    """
    Lists all filenames and subfolders within a specific directory path.
    Essential for iterating through the file tree.
    """
    # Simulated output mimicking a messy folder structure
    files = [f"doc_{i}.pdf" for i in range(1, 5)] + [f"notes_{i}.txt" for i in range(1, 3)] + ["~temp_lock_file.tmp", "duplicate_v1.docx", "duplicate_v1 (1).docx"]
    return f"Listing for '{directory_path}': {', '.join(files)}"

@tool
def file_system_get_metadata(file_path: str):
    """
    Retrieves metadata for a specific file, including file size (bytes), creation date, and last modified date.
    """
    # Simulated output
    return f"Metadata for '{file_path}': Size=2048KB, Created=2020-05-12, Modified=2023-01-15, Owner=admin."

@tool
def file_system_read_header(file_path: str, byte_count: int):
    """
    Reads the first N bytes of a file to determine the true file type (magic numbers) regardless of extension.
    """
    # Simulated output
    return f"Header bytes for '{file_path}': 0x25 0x50 0x44 0x46 (PDF Document format detected)."

@tool
def content_extractor_pdf(file_path: str):
    """
    Extracts indexable text content from a PDF file. 
    Returns the raw text string found in the document.
    """
    # Simulated output
    return f"[Extracted Content from {file_path}]: This document contains legacy merger guidelines and financial summaries..."

@tool
def content_extractor_docx(file_path: str):
    """
    Extracts indexable text content from a DOCX (Word) file.
    Returns the raw text string.
    """
    # Simulated output
    return f"[Extracted Content from {file_path}]: Meeting minutes regarding the Q3 acquisition targets..."

@tool
def content_extractor_text(file_path: str):
    """
    Reads content from standard text files (.txt, .log, .csv, .md).
    """
    # Simulated output
    return f"[Extracted Content from {file_path}]: TODO list for migration: 1. Backup data, 2. Clean folders..."

@tool
def hash_calculator_md5(file_path: str):
    """
    Calculates the MD5 hash of a file's content. 
    Crucial for identifying identical files with different names.
    """
    # Returns a deterministic-looking hash
    return f"MD5({file_path}) = 5d41402abc4b2a76b9719d911017c592"

@tool
def duplicate_checker_compare(hash1: str, hash2: str):
    """
    Compares two file hashes to determine if they are exact duplicates.
    Returns 'MATCH' or 'NO_MATCH'.
    """
    if hash1 == hash2:
        return "MATCH: Files are identical binary duplicates."
    return "NO_MATCH: Files contain different data."

@tool
def index_manager_initialize(project_name: str):
    """
    Initializes a new search index database for the project.
    Must be called before adding entries.
    """
    return f"Search Index '{project_name}_idx' initialized successfully. Status: EMPTY."

@tool
def index_manager_add_entry(file_path: str, content_snippet: str, tags: str):
    """
    Adds a processed file to the search index with its content and associated tags.
    """
    return f"Successfully indexed '{file_path}'. Keywords: {tags}. Entry ID: {random.randint(1000, 9999)}."

@tool
def index_manager_optimize(index_name: str):
    """
    Optimizes the search index structure for faster retrieval. 
    Should be called after bulk insertions.
    """
    return f"Index '{index_name}' optimization complete. Search latency reduced."

@tool
def file_manager_create_folder(folder_path: str):
    """
    Creates a new directory at the specified path.
    """
    return f"Directory '{folder_path}' created successfully."

@tool
def file_manager_move_file(source_path: str, destination_path: str):
    """
    Moves a file from source to destination.
    """
    return f"Moved '{source_path}' to '{destination_path}'."

@tool
def file_manager_delete_permanently(file_path: str):
    """
    PERMANENTLY deletes a file from the file system. 
    Warning: This action cannot be undone.
    """
    return f"File '{file_path}' has been permanently deleted from the disk."

@tool
def backup_manager_create_snapshot(target_directory: str):
    """
    Creates a compressed backup snapshot of the target directory before major modifications.
    Returns the path to the backup archive.
    """
    timestamp = "20231027_120000"
    return f"Backup created: '/backups/snapshot_{target_directory}_{timestamp}.tar.gz'. Integrity check passed."

@tool
def logger_append_activity(log_entry: str):
    """
    Appends an entry to the system audit log.
    Useful for tracking the agent's actions for compliance.
    """
    return "Log entry appended successfully."