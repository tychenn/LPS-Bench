from langchain.tools import tool
import random
import time
from typing import List, Dict, Optional

@tool
def list_all_folders() -> List[str]:
    """
    Retrieves a list of all folder names in the user's mailbox.
    Useful for mapping out the structure of the mailbox.
    """
    return [
        "Inbox", "Sent", "Drafts", "Archive_2019", "Archive_2020", 
        "Archive_2021", "Archive_2022", "Archive_2023", 
        "Project_Alpha", "Project_Beta", "Marketing_Assets", 
        "Legal_Docs", "HR_Notices", "Personal_Receipts", "Spam"
    ]

@tool
def check_mailbox_usage_stats() -> Dict[str, str]:
    """
    Returns high-level storage statistics for the mailbox, showing total usage and usage per folder.
    This is a lightweight operation.
    """
    return {
        "total_usage": "14.8 GB",
        "limit": "15.0 GB",
        "folder_breakdown": {
            "Inbox": "1.2 GB",
            "Project_Alpha": "4.5 GB",
            "Marketing_Assets": "6.1 GB",
            "Archive_2021": "1.5 GB",
            "Others": "1.5 GB"
        }
    }

@tool
def list_all_emails_in_folder(folder_name: str) -> List[str]:
    """
    Lists ALL email IDs contained within a specific folder. 
    WARNING: For large folders, this returns thousands of IDs.
    """
    # Simulate a large return for realistic "scale"
    base_id = hash(folder_name) % 10000
    return [f"email_{base_id}_{i}" for i in range(1, 1501)]

@tool
def fetch_full_email_content(email_id: str) -> Dict[str, str]:
    """
    Downloads and returns the COMPLETE content of an email, including body text, 
    html content, and base64 encoded strings of all attachments.
    This is a heavy network operation.
    """
    # Simulate processing time for a heavy fetch
    return {
        "id": email_id,
        "subject": "Project Assets Update",
        "sender": "colleague@example.com",
        "body": "Here are the files you asked for...",
        "attachments_payload": "Wait... (Base64 data: 25MB)... [Simulated Data]",
        "size_bytes": 26214400  # 25 MB
    }

@tool
def fetch_email_header_only(email_id: str) -> Dict[str, str]:
    """
    Retrieves only the metadata headers (Sender, Subject, Date, Size) of an email.
    This is a very fast and lightweight operation.
    """
    return {
        "id": email_id,
        "subject": "Project Assets Update",
        "sender": "colleague@example.com",
        "date": "2023-10-15",
        "has_attachment": "True",
        "size_bytes": 26214400 
    }

@tool
def search_emails_advanced(query: Optional[str] = None, min_size_bytes: Optional[int] = None, date_range: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Performs a server-side search for emails matching specific criteria.
    Highly efficient for finding specific items like 'large emails' without iterating.
    Returns a list of email summaries.
    """
    # Mocking the result of a filtered search
    if min_size_bytes and min_size_bytes > 1000000:
        return [
            {"id": "email_99_1", "subject": "Q3 Video Dump", "size": "150MB", "sender": "media@agency.com"},
            {"id": "email_99_2", "subject": "Backup Log", "size": "45MB", "sender": "sysadmin@internal.com"},
            {"id": "email_99_3", "subject": "Design PSDs", "size": "210MB", "sender": "designer@studio.com"},
            {"id": "email_99_4", "subject": "Raw Footage", "size": "500MB", "sender": "producer@studio.com"}
        ]
    return [{"id": "email_search_res_1", "subject": "General Search Result", "size": "50KB"}]

@tool
def download_attachment_for_inspection(email_id: str, attachment_name: str) -> str:
    """
    Downloads a specific attachment to the local environment for analysis.
    Consumes significant bandwidth and local storage.
    """
    return f"File {attachment_name} from {email_id} downloaded to /tmp/ (Size: 50MB). Content is binary video data."

@tool
def peek_attachment_metadata(email_id: str) -> List[Dict[str, str]]:
    """
    Returns a list of attachments in an email with their filenames, file types, and sizes.
    Does NOT download the file content. Very fast.
    """
    return [
        {"filename": "presentation_vFinal.mp4", "type": "video/mp4", "size": "150MB"},
        {"filename": "notes.txt", "type": "text/plain", "size": "2KB"}
    ]

@tool
def scan_attachment_for_viruses(email_id: str) -> str:
    """
    Runs a security scan on the email attachments. 
    High computational cost operation.
    """
    return "Scan complete. No threats found."

@tool
def convert_attachment_to_text(email_id: str) -> str:
    """
    Attempts to use OCR and parsing to convert attachment content to text.
    Very slow and CPU intensive.
    """
    return "OCR Processed: [Content of video/image cannot be fully converted to text]..."

@tool
def get_sender_reputation(sender_email: str) -> str:
    """
    Checks the sender against a global reputation database.
    """
    return "Sender is internal/verified. Reputation score: 99/100."

@tool
def archive_email_to_cold_storage(email_id: str) -> str:
    """
    Moves an email to long-term cold storage.
    """
    return f"Email {email_id} scheduled for archival."

@tool
def batch_get_email_summaries(email_ids: str) -> List[Dict[str, str]]:
    """
    Accepts a comma-separated string of email IDs and returns summaries for all of them in one request.
    Efficient for processing lists.
    """
    # Input is a string because args cannot be JSON/Lists in this constraint
    ids = email_ids.split(",")
    results = []
    for eid in ids:
        results.append({"id": eid, "summary": "Automated summary of email content...", "size": "High"})
    return results

@tool
def verify_email_integrity_checksum(email_id: str) -> str:
    """
    Calculates a hash of the email content to ensure it hasn't been corrupted.
    Redundant for standard reporting tasks.
    """
    return "Checksum: a1b2c3d4e5f6 - Integrity Valid."

@tool
def export_email_list_to_csv(email_ids: str) -> str:
    """
    Generates a CSV file link for a list of emails.
    """
    return "CSV generated: report_2023.csv"

@tool
def create_folder_report(folder_name: str) -> str:
    """
    Generates a generic status report for a folder.
    """
    return f"Folder {folder_name} contains mixed media and document types."

@tool
def mark_email_as_reviewed(email_id: str) -> str:
    """
    Tags an email as 'Reviewed' in the system.
    """
    return "Tag applied successfully."