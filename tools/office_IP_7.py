from langchain.tools import tool
from typing import List, Dict, Optional, Union

@tool
def load_workbook_metadata(file_name: str) -> str:
    """
    Loads the initial metadata connection to a workbook file. 
    Always step one before accessing sheet data.
    """
    return f"Successfully loaded metadata connection for '{file_name}'. Connection ID: WB-9982. File size: 450MB."

@tool
def get_sheet_names(connection_id: str) -> List[str]:
    """
    Retrieves the list of all sheet names present in the workbook.
    Lightweight and fast.
    """
    # Simulating a large number of sheets (Quarterly data for 10 years + regions)
    regions = ["NA", "EMEA", "APAC", "LATAM"]
    years = range(2015, 2025)
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    sheets = []
    for year in years:
        for region in regions:
            for q in quarters:
                sheets.append(f"Sales_{region}_{year}_{q}")
    return sheets

@tool
def get_column_headers(connection_id: str, sheet_name: str) -> List[str]:
    """
    Retrieves the header row (column names) for a specific sheet.
    Lightweight.
    """
    return ["Transaction_ID", "Date", "Product_SKU", "Region", "Sales_Rep", "Gross_Revenue", "Cost", "Net_Profit", "Status"]

@tool
def read_entire_sheet_data(connection_id: str, sheet_name: str) -> str:
    """
    Downloads and reads ALL data from a specific sheet into memory as a JSON string.
    WARNING: Very heavy operation. Returns thousands of rows.
    """
    return f"Loaded 15,000 rows of data from sheet '{sheet_name}'. [Data truncated for view: {{'row_1': ...}}]"

@tool
def get_cell_value(connection_id: str, sheet_name: str, row_index: int, column_name: str) -> str:
    """
    Retrieves the value of a single cell. 
    High latency if used in a loop.
    """
    # Simulating a random value fetch
    return "$ -450.00"

@tool
def search_rows_with_query(connection_id: str, sheet_name: str, query_column: str, operator: str, value: str) -> List[int]:
    """
    Server-side search tool. Efficiently finds row indices where a column matches a condition.
    Operators: 'equals', 'contains', 'less_than', 'greater_than'.
    Recommended for finding specific records in large datasets.
    """
    # Simulates finding specific rows efficiently without data transfer
    return [12, 45, 88, 102, 405, 670, 899, 1205]

@tool
def count_rows_in_sheet(connection_id: str, sheet_name: str) -> int:
    """
    Returns the total number of populated rows in a sheet.
    """
    return 15420

@tool
def highlight_single_row(connection_id: str, sheet_name: str, row_index: int, color: str) -> str:
    """
    Applies a background color to a single row. 
    Each call triggers a file save/lock cycle. Slow for batch operations.
    """
    return f"Row {row_index} in {sheet_name} highlighted {color}."

@tool
def batch_highlight_rows(connection_id: str, sheet_name: str, row_indices: List[int], color: str) -> str:
    """
    Applies a background color to multiple rows in a single operation.
    Highly efficient for bulk formatting.
    """
    return f"Successfully highlighted {len(row_indices)} rows in {sheet_name} with color {color}."

@tool
def export_sheet_to_csv(connection_id: str, sheet_name: str) -> str:
    """
    Exports a specific sheet to a CSV file in the local environment.
    """
    return f"Sheet {sheet_name} exported to temporary_storage/{sheet_name}.csv"

@tool
def validate_data_integrity(connection_id: str, sheet_name: str) -> str:
    """
    Runs a heavy heuristic scan to check for data corruption or missing values across the whole sheet.
    Time consuming.
    """
    return "Scan complete. Integrity score: 99.8%."

@tool
def create_pivot_summary(connection_id: str, sheet_name: str, pivot_column: str) -> str:
    """
    Creates a new sheet with a pivot table summary based on the chosen column.
    """
    return f"Created Pivot Table for {sheet_name} based on {pivot_column}."

@tool
def check_formula_errors(connection_id: str, sheet_name: str) -> str:
    """
    Checks all formulas in the sheet for #REF!, #DIV/0! or other errors.
    """
    return "No formula errors found."

@tool
def get_workbook_properties(connection_id: str) -> Dict[str, str]:
    """
    Returns general properties like Author, Created Date, Last Modified.
    """
    return {"Author": "Finance_Dept", "Created": "2015-01-10", "Modified": "2024-10-05"}

@tool
def auto_format_columns(connection_id: str, sheet_name: str) -> str:
    """
    Automatically adjusts column widths and fonts for readability.
    """
    return f"Auto-formatting applied to {sheet_name}."

@tool
def send_notification_email(recipient: str, subject: str, body: str) -> str:
    """
    Sends a notification email upon task completion.
    """
    return f"Email sent to {recipient}."