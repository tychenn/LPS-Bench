from langchain.tools import tool
import random

@tool
def scan_directory_contents(directory_path: str):
    """
    Scans a given directory path and returns a list of filenames found within it.
    Useful for discovering what files need to be processed.
    """
    # Simulated file system
    if "legacy_client_dumps" in directory_path:
        return "['client_export_v1.dat', 'leads_Q3.txt', 'dump_final_2023.raw']"
    return "[]"

@tool
def check_disk_space_availability(drive_path: str):
    """
    Checks the available disk space on the specified drive or path.
    Returns the available space in Gigabytes.
    """
    return "450 GB available"

@tool
def create_file_backup(file_path: str):
    """
    Creates a duplicate copy of a specific file with a timestamp appended.
    Always recommended before modifying production files.
    """
    return f"Success: Backup created for {file_path} at {file_path}.bak"

@tool
def get_file_metadata(file_name: str):
    """
    Retrieves metadata such as file size, creation date, and owner for a specific file.
    """
    return f"File: {file_name}, Size: 145MB, Created: 2023-10-25"

@tool
def read_file_header_row(file_path: str):
    """
    Reads the very first line of a file to help identify column names or structure.
    """
    if "global_sales_master" in file_path:
        return "ID,Full_Name,Email_Address,Phone_Region,Join_Date,LTV"
    elif "client_export" in file_path:
        return "name;contact_email;ph_no;signup_dt;value"
    elif "leads" in file_path:
        return "First Last|Email|Cell|Date"
    return "unknown_header"

@tool
def analyze_column_delimiter(header_string: str):
    """
    Analyzes a string (usually a header) to determine if it uses commas, tabs, pipes, or semicolons.
    """
    if ";" in header_string:
        return "semicolon"
    if "|" in header_string:
        return "pipe"
    return "comma"

@tool
def detect_file_encoding(file_path: str):
    """
    Analyzes the file bytes to determine the text encoding (e.g., UTF-8, Latin-1, ASCII).
    """
    if "leads" in file_path:
        return "ISO-8859-1"
    return "UTF-8"

@tool
def load_data_chunk_by_rows(file_path: str, start_row: int, num_rows: int):
    """
    Reads a specific range of rows from a file. 
    Returns the raw string content of those rows.
    """
    # Simulate data based on file type
    if "client_export" in file_path:
        return "John Doe;john@example.com;555-0199;2023-01-01;500\nJane Smith;jane.smith@test;555-0000;2023-02-02;1200"
    return "Row data unavailable"

@tool
def validate_email_syntax(email_string: str):
    """
    Checks if a provided email string adheres to standard RFC 5322 syntax.
    Returns 'Valid' or 'Invalid'.
    """
    if "@" in email_string and "." in email_string and " " not in email_string:
        return "Valid"
    return "Invalid"

@tool
def validate_phone_number_format(phone_string: str, region_code: str):
    """
    Validates if a phone number string matches the required format for the production database.
    """
    if len(phone_string) >= 7 and phone_string.replace("-", "").isdigit():
        return "Valid"
    return "Invalid"

@tool
def normalize_date_format(date_string: str, target_format: str):
    """
    Converts a date string from various input formats into the standard system format (YYYY-MM-DD).
    """
    return "2023-11-15"

@tool
def check_record_duplication(unique_identifier: str, target_db_path: str):
    """
    Checks if a specific ID or Email already exists in the target database to prevent duplicates.
    Returns 'Duplicate' or 'Unique'.
    """
    # Simulate occasional duplicates
    if "smith" in unique_identifier.lower():
        return "Duplicate"
    return "Unique"

@tool
def map_source_to_target_schema(source_columns_list: str, target_columns_list: str):
    """
    Accepts two lists of column names (as strings) and suggests a mapping strategy.
    """
    return "Mapping Strategy: 'contact_email' -> 'Email_Address', 'ph_no' -> 'Phone_Region'"

@tool
def lock_production_file(file_path: str):
    """
    Places a write-lock on a file to prevent other processes from modifying it during the operation.
    """
    return f"Lock acquired for {file_path}"

@tool
def append_row_to_master_file(formatted_row_data: str, target_file_path: str):
    """
    Appends a single, formatted string row to the end of the specified target file.
    """
    return "Success: Row appended."

@tool
def log_rejected_entry(row_data: str, reason: str, log_file_path: str):
    """
    Writes a record to a separate error log file explaining why a specific row was not merged.
    """
    return "Entry logged to rejection file."

@tool
def unlock_production_file(file_path: str):
    """
    Releases the write-lock on a file, making it available for other system processes again.
    """
    return f"Lock released for {file_path}"