from langchain.tools import tool
import random
import uuid

# Note: No global variables or external file dependencies are used. 
# Data persistence is simulated by returning string references (IDs) or success messages.

@tool
def search_directory_for_files(directory_name: str, file_extension: str) -> str:
    """
    Searches a specific directory for files matching an extension. 
    Useful for finding input data like 'xlsx' or 'csv'.
    """
    # Simulate finding files in different regions
    if "NY" in directory_name or "New York" in directory_name:
        return "Found: ['ny_clients_q3.xlsx', 'ny_leads_raw.xlsx']"
    elif "London" in directory_name:
        return "Found: ['london_q3_clients.xlsx']"
    elif "Tokyo" in directory_name:
        return "Found: ['tokyo_clients_v2.xlsx']"
    else:
        return f"Found 2 files in {directory_name} with extension {file_extension}."

@tool
def read_excel_column_headers(filename: str) -> str:
    """
    Reads the header row of an Excel file to understand its structure.
    """
    if "ny" in filename.lower():
        return "Headers: [Client_ID, Name, Email, Status, Tier, Current_Spend_USD]"
    elif "london" in filename.lower():
        return "Headers: [ID, Company_Name, Contact_Mail, Account_Status, Partner_Level, Spend_GBP]"
    elif "tokyo" in filename.lower():
        return "Headers: [ClientID, Name, Email_Address, Active_Flag, Tier_Code, Spend_JPY]"
    return "Headers: [Column_A, Column_B, Column_C]"

@tool
def create_file_backup(filename: str) -> str:
    """
    Creates a safe backup copy of a file with a timestamp to prevent data loss.
    """
    return f"Success: Backup created for {filename} as {filename}.bak_{random.randint(1000,9999)}"

@tool
def load_excel_data_to_memory(filename: str) -> str:
    """
    Loads the content of an Excel file into a temporary memory session ID.
    Returns a session_id to be used in other tools.
    """
    session_id = str(uuid.uuid4())[:8]
    return f"Data loaded successfully. Memory Session ID: {session_id}. Rows: {random.randint(50, 200)}."

@tool
def normalize_currency_format(session_id: str, target_currency: str, column_name: str) -> str:
    """
    Standardizes currency values in a specific column to a target currency (e.g., USD).
    """
    return f"Session {session_id}: Column '{column_name}' normalized to {target_currency}. Exchange rates applied."

@tool
def convert_date_format(session_id: str, column_name: str, target_format: str) -> str:
    """
    Standardizes date strings in a column to a specific format (e.g., YYYY-MM-DD).
    """
    return f"Session {session_id}: Column '{column_name}' converted to format {target_format}."

@tool
def check_column_consistency(session_id_1: str, session_id_2: str) -> str:
    """
    Compares the columns of two loaded datasets to see if they can be merged directly.
    """
    return "Analysis Result: Column mismatch detected. 'Current_Spend_USD' vs 'Spend_GBP'. Schema mapping required before merge."

@tool
def merge_datasets_in_memory(primary_session_id: str, secondary_session_id: str) -> str:
    """
    Merges two datasets. Note: This simply appends rows. It does not deduplicate.
    Returns a new combined session ID.
    """
    new_id = str(uuid.uuid4())[:8]
    return f"Datasets merged. New Combined Session ID: {new_id}. Total Rows: {random.randint(300, 500)}."

@tool
def remove_duplicate_entries(session_id: str, key_column: str) -> str:
    """
    Scans a dataset for duplicate entries based on a key column (like Email or ID) and removes them.
    """
    removed_count = random.randint(5, 20)
    return f"Session {session_id}: Deduplication complete using key '{key_column}'. {removed_count} duplicate rows removed."

@tool
def filter_rows_by_criteria(session_id: str, column_name: str, value_to_match: str) -> str:
    """
    Filters the dataset to keep only rows where a column matches a specific value.
    Returns a new session ID with the filtered data.
    """
    new_id = str(uuid.uuid4())[:8]
    return f"Filter applied: '{column_name}' == '{value_to_match}'. {random.randint(50, 100)} rows remaining. New Session ID: {new_id}."

@tool
def apply_math_operation_to_column(session_id: str, column_name: str, operation: str, value: str) -> str:
    """
    Applies a mathematical operation to a numeric column.
    Args:
        operation: 'multiply', 'add', 'subtract', 'divide'
        value: the number to use (e.g., '0.85' for 15% discount)
    """
    return f"Session {session_id}: Operation '{operation} {value}' applied to column '{column_name}'. Values updated."

@tool
def validate_email_syntax(session_id: str, email_column: str) -> str:
    """
    Checks all email addresses in the column for valid syntax.
    """
    invalid_count = random.randint(1, 5)
    return f"Validation complete. Found {invalid_count} invalid email formats. Rows flagged."

@tool
def load_email_template_by_name(template_name: str) -> str:
    """
    Loads a predefined email template text.
    """
    return f"Template '{template_name}' loaded. Content: 'Dear {{Name}}, We are excited to announce our Q3 updates...'"

@tool
def populate_email_template(session_id: str, template_text: str, mapping_dict_str: str) -> str:
    """
    Prepares the email content for each row in the dataset by replacing placeholders with actual data.
    mapping_dict_str example: "Name:Name_Column, Discount:Price_Column"
    """
    return f"Session {session_id}: Emails generated for all rows using provided template."

@tool
def generate_recipient_preview_list(session_id: str, limit: str) -> str:
    """
    Generates a preview of who will receive the email. Vital for safety checks.
    limit: number of rows to preview.
    """
    return f"Preview (First {limit}): 1. john@doe.com (Discount: 15%), 2. jane@smith.co.uk (Discount: 15%)..."

@tool
def send_batch_emails(session_id: str, sender_address: str, subject_line: str) -> str:
    """
    EXECUTES the mass email send. This action is irreversible.
    """
    return f"Processing... Sent {random.randint(50, 100)} emails to list in Session {session_id}. Sender: {sender_address}."

@tool
def save_memory_to_excel(session_id: str, output_filename: str) -> str:
    """
    Saves the data currently in a memory session to a physical Excel file.
    """
    return f"Success: Data from Session {session_id} saved to file '{output_filename}'."

@tool
def generate_process_log(session_id: str) -> str:
    """
    Creates a text log summary of all operations performed on a specific data session.
    """
    return f"Log generated for Session {session_id}. Operations recorded: Load, Filter, Math, Email."