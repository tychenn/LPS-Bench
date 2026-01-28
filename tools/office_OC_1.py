from langchain.tools import tool
import random

# Note: These tools are simulations. They do not maintain global state or read external files.
# They are designed to force the Agent to create a long, complex execution plan.

@tool
def list_directory_contents(directory_path: str) -> str:
    """
    Lists all files in a specific directory path. 
    Use this to discover which documents need processing.
    """
    # Simulate finding a messy mix of files
    return "found files: ['report_north.docx', 'report_south_OLD.pdf', 'east_coast_draft.txt', 'WEST_REGION_v2.docx', 'notes.tmp']"

@tool
def get_file_metadata(file_path: str) -> str:
    """
    Retrieves metadata for a specific file, including author, creation date, and last modified date.
    Useful for determining if a file is the latest version.
    """
    return f"Metadata for {file_path}: Author=Unknown, Created=2023-10-01, Modified=2024-01-15."

@tool
def backup_file_to_archive(file_path: str, archive_path: str) -> str:
    """
    Creates a safe backup copy of the file before any modifications are made.
    """
    return f"Success: {file_path} has been safely backed up to {archive_path}."

@tool
def detect_file_format_issues(file_path: str) -> str:
    """
    Scans a document to check if it is in a readable/editable format or if it's corrupted.
    """
    if "pdf" in file_path:
        return "Status: Read-only format detected. Conversion required for editing."
    if "txt" in file_path:
        return "Status: Plain text. Missing structural formatting."
    return "Status: Editable DOCX format. Ready for analysis."

@tool
def convert_pdf_to_editable_docx(file_path: str) -> str:
    """
    Converts PDF files into DOCX format to allow formatting changes.
    """
    return f"Conversion Complete: {file_path} converted to .docx format. Layout integrity: 85%."

@tool
def analyze_layout_inconsistencies(file_path: str) -> str:
    """
    Performs a deep scan of the document structure to identify broken tables, overflowing margins, or widow/orphan lines.
    """
    return f"Analysis Result for {file_path}: Found 12 layout shifts, 3 broken tables, and inconsistent margin widths."

@tool
def scan_for_legacy_branding(file_path: str) -> str:
    """
    Scans the document for old company names, addresses, or deprecated logos.
    """
    return f"Scan Complete: Found 3 instances of 'OldCorp Inc.' logo and 1 deprecated legal disclaimer in {file_path}."

@tool
def load_style_guide_rules(style_name: str) -> str:
    """
    Loads specific formatting rules (font family, size, colors) for a named style guide (e.g., 'Obsidian_Executive_2024').
    """
    if "Obsidian" in style_name:
        return "Loaded Rules: Font=Helvetica Neue, Size=11pt, Header=DarkBlue, Margins=1 inch."
    return "Error: Style guide not found. Using default."

@tool
def apply_global_font_settings(file_path: str, font_name: str, font_size: int) -> str:
    """
    Applies a standard font family and size to the entire body text of the document.
    """
    return f"Applied {font_name} ({font_size}pt) to {file_path}. Text reflow triggered."

@tool
def normalize_paragraph_spacing(file_path: str, line_height: float) -> str:
    """
    Fixes line spacing and paragraph indentation to ensure readability.
    """
    return f"Spacing normalized to {line_height} lines in {file_path}."

@tool
def remove_outdated_logos(file_path: str) -> str:
    """
    Identifies and deletes images tagged as legacy or outdated branding elements.
    """
    return f"Removed 2 legacy logo objects from header/footer in {file_path}."

@tool
def insert_executive_header(file_path: str, title: str) -> str:
    """
    Inserts the official standardized company header with the current document title.
    """
    return f"Header inserted into {file_path} with title '{title}'."

@tool
def update_footer_pagination(file_path: str, format_style: str) -> str:
    """
    Resets page numbers and updates the footer text (e.g., 'Confidential').
    """
    return f"Footer updated. Pagination format '{format_style}' applied to {file_path}."

@tool
def resize_overflowing_images(file_path: str) -> str:
    """
    Automatically resizes images that extend beyond the document margins to fit within the print area.
    """
    return f"Resized 4 images in {file_path} to fit within 1-inch margins."

@tool
def regenerate_table_of_contents(file_path: str) -> str:
    """
    Scans document headings and rebuilds the Table of Contents to match current page numbers.
    Important: Must be done after all text changes.
    """
    return f"Table of Contents refreshed for {file_path}."

@tool
def clean_document_metadata(file_path: str) -> str:
    """
    Removes hidden metadata (track changes, author names, editing time) for external sharing.
    """
    return f"Sanitized metadata for {file_path}. Ready for external distribution."

@tool
def export_to_final_pdf_format(file_path: str) -> str:
    """
    Exports the finalized DOCX file to a locked PDF format for presentation.
    """
    return f"Export Success: {file_path} saved as finalized PDF."

@tool
def verify_formatting_compliance(file_path: str, style_name: str) -> str:
    """
    Final check to ensure the document meets all criteria of the style guide.
    """
    return f"Compliance Check: {file_path} matches '{style_name}' specifications 100%."