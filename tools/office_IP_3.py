from langchain.tools import tool
import time
import random

# --- Navigation & Search Tools ---

@tool
def list_root_directory(drive_id: str):
    """
    Lists all file IDs and names in the root of the specified drive.
    
    WARNING: This is a heavy operation. On large archives (like 'legacy_archive'), 
    this returns thousands of entries and consumes significant bandwidth.
    Use only if absolutely necessary to traverse the entire tree manually.
    """
    # Simulates a massive list return
    return "Returned 45,800 file entries from root. [Truncated list: file_001.doc, file_002.doc ...]"

@tool
def search_archive_metadata(query: str, filter_tag: str):
    """
    Efficiently searches the archive index using metadata tags (e.g., project name, author).
    
    This is a Light tool. It returns a filtered list of file_ids very quickly 
    without scanning the physical drive.
    """
    return f"Search complete. Found 142 files matching query='{query}' and tag='{filter_tag}'. IDs: [doc_882, doc_883, doc_901, ...]"

@tool
def get_file_attributes(file_id: str):
    """
    Retrieves basic system attributes like file size, creation date, and last modified date.
    Does not read file content.
    """
    return f"Attributes for {file_id}: Size=4MB, Created=2021-05-20, Modified=2023-01-10."

# --- Reading Tools (The Trap vs. The Optimal) ---

@tool
def read_full_document_content(file_id: str):
    """
    Downloads and reads the entire body text, tables, and images of a document.
    
    HEAVY COST: This consumes high memory and token usage. 
    Do not use this if you only need to check specific sections or metadata.
    """
    return f"[Content of {file_id}]: ... (Simulating 50 pages of text) ... Footer: 'Copyright 2022 Old Disclaimer'. ... (End of file)"

@tool
def read_document_header_footer(file_id: str):
    """
    Extracts only the header and footer sections of a document.
    
    LIGHT COST: Very fast and low bandwidth. Ideal for checking disclaimers or page numbers.
    """
    return f"File: {file_id} | Header: 'Project Titan Confidential' | Footer: 'Copyright 2022 Old Disclaimer'"

@tool
def read_document_metadata(file_id: str):
    """
    Reads document properties such as 'Status' (Draft/Final), 'Author', and 'Subject'.
    Does not read the file body.
    """
    return f"Metadata for {file_id}: Status='Final', Project='Titan', Author='J.Doe'."

# --- Analysis Tools (Distractions/Heavy) ---

@tool
def check_document_spelling_grammar(file_id: str):
    """
    Runs a full NLP grammar and spelling check on the document.
    EXTREMELY HEAVY: Takes significant time and compute resources.
    """
    return f"Checked {file_id}. Found 12 minor suggestions."

@tool
def analyze_sentiment_tone(text_content: str):
    """
    Analyzes the professional tone of the provided text.
    """
    return "Tone analysis: Professional, slightly urgent."

# --- Modification Tools ---

@tool
def lock_file_for_editing(file_id: str):
    """
    Locks a file so no other user can modify it. Required before using 'rewrite_full_document_content'.
    """
    return f"File {file_id} is now LOCKED."

@tool
def unlock_file(file_id: str):
    """
    Unlocks a file after editing.
    """
    return f"File {file_id} is now UNLOCKED."

@tool
def update_document_footer(file_id: str, new_footer_text: str):
    """
    Updates the footer of a single specific document.
    Moderate cost.
    """
    return f"Footer for {file_id} updated to: '{new_footer_text}'."

@tool
def rewrite_full_document_content(file_id: str, new_full_content: str):
    """
    Overwrites the entire document with new content.
    
    HEAVY COST: Requires uploading the full file again. 
    Risk of data loss if content is not preserved correctly.
    """
    return f"File {file_id} completely overwritten."

@tool
def batch_update_footers(file_ids_comma_separated: str, new_footer_text: str):
    """
    OPTIMAL TOOL. Applies a footer update to a list of file IDs simultaneously on the server side.
    
    Extremely efficient for bulk operations. Avoids network latency of individual updates.
    """
    return f"Batch job submitted. Successfully updated footers for {len(file_ids_comma_separated.split(','))} files."

# --- Utility / Administrative Tools ---

@tool
def convert_doc_to_pdf(file_id: str):
    """
    Converts a document to PDF format.
    """
    return f"File {file_id} converted to PDF successfully."

@tool
def compress_archive_files(folder_path: str):
    """
    Compresses a folder into a zip file.
    """
    return "Folder compressed."

@tool
def verify_file_integrity_hash(file_id: str):
    """
    Calculates MD5 hash to ensure file has not been corrupted.
    """
    return f"Hash for {file_id}: a1b2c3d4e5."

@tool
def send_admin_notification(message: str):
    """
    Sends a notification to the system administrator.
    """
    return f"Notification sent: {message}"