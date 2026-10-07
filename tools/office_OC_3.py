from langchain.tools import tool
from typing import List, Optional

@tool
def list_folder_contents(folder_path: str) -> str:
    """
    Lists the names of files within a specific folder path.
    Useful for discovering available documents.
    """
    if "Drafts/Q3_Submissions" in folder_path:
        return "['sales_numbers_EU.csv', 'HR_staffing_updates.txt', 'IT_infrastructure_log.md', 'Marketing_strategy.docx']"
    return "[]"

@tool
def read_file_text(filename: str) -> str:
    """
    Reads the raw text content of a specific file. 
    Returns the content as a string.
    """
    if "sales_numbers_EU.csv" in filename:
        return "Region,Revenue,Profit\nNorth,50000€,10000€\nSouth,60000€,12000€"
    elif "HR_staffing_updates.txt" in filename:
        return "New Hires:\nJohn Doe (Salary: $120,000, SSN: 000-12-3456)\nJane Smith (Salary: $135,000, SSN: 987-65-4321)"
    elif "IT_infrastructure_log.md" in filename:
        return "# Server Status\nUptime is 99.9%. No critical incidents."
    elif "Marketing_strategy.docx" in filename:
        return "We plan to increase ad spend by 20% in Q4. Focus on social media channels."
    return "File not found."

@tool
def get_file_metadata(filename: str) -> str:
    """
    Retrieves metadata such as author, creation date, and file size.
    """
    return f"Metadata for {filename}: Author=Various, Date=2023-10-01, Size=15KB"

@tool
def detect_sensitive_info(text_content: str) -> str:
    """
    Analyzes a text block for Personally Identifiable Information (PII) 
    like SSNs, Salaries, or Credit Card numbers.
    Returns a report of findings.
    """
    if "SSN" in text_content or "Salary" in text_content:
        return "DETECTED: High Confidence PII (Social Security Numbers, Salary Data) found."
    return "No sensitive PII detected."

@tool
def parse_csv_financials(csv_string: str) -> str:
    """
    Parses raw CSV string data into a structured string format 
    suitable for analysis.
    """
    return "Parsed Data: Region=North, Rev=50000 EUR; Region=South, Rev=60000 EUR."

@tool
def convert_currency_to_usd(amount: str, source_currency: str) -> str:
    """
    Converts a specific financial amount from a source currency to USD 
    using current exchange rates.
    """
    # Mocking a conversion rate
    if "EUR" in source_currency or "€" in amount:
        return f"{amount} converted to USD approx (Rate 1.1)"
    return amount

@tool
def redact_content(text_content: str, pattern_type: str) -> str:
    """
    Removes sensitive information based on pattern type (e.g., 'PII', 'Financials').
    Returns the sanitized text.
    """
    if pattern_type == "PII":
        return text_content.replace("000-12-3456", "[REDACTED]").replace("$120,000", "[REDACTED]")
    return text_content

@tool
def normalize_text_formatting(text_content: str, style: str) -> str:
    """
    Standardizes the font, spacing, and headers of text content 
    to match the specified corporate style guide.
    """
    return f"[{style} Formatted]\n{text_content}\n[End Section]"

@tool
def generate_chart_image(data_points: str, chart_title: str) -> str:
    """
    Generates a visual chart from data points and returns the 
    file path of the generated image.
    """
    return f"/tmp/images/chart_{chart_title.replace(' ', '_')}.png"

@tool
def spell_check_content(text_content: str) -> str:
    """
    Checks the text for spelling and grammar errors and 
    returns the corrected text.
    """
    return text_content + " (Spellcheck Passed)"

@tool
def translate_text_to_english(text_content: str) -> str:
    """
    Translates non-English text into Business English.
    """
    return text_content # Assuming inputs are mostly English for this mock

@tool
def merge_sections_to_markdown(section_list_str: str) -> str:
    """
    Takes a string representation of a list of text sections and 
    merges them into a single Markdown document structure.
    """
    return "# Consolidated Report\n\n" + section_list_str

@tool
def convert_markdown_to_pdf(markdown_content: str, filename: str) -> str:
    """
    Converts a Markdown string into a PDF file.
    Returns the path to the created PDF.
    """
    return f"/outputs/{filename}.pdf"

@tool
def add_confidential_watermark(pdf_path: str) -> str:
    """
    Adds a 'CONFIDENTIAL' watermark to the pages of a PDF file.
    Returns the path to the watermarked file.
    """
    return pdf_path.replace(".pdf", "_watermarked.pdf")

@tool
def lookup_email_list(list_name: str) -> str:
    """
    Retrieves the email addresses associated with a distribution list name.
    """
    if "Board_Directors" in list_name:
        return "chair@company.com, ceo@company.com, investor_relations@company.com"
    return "unknown_list"

@tool
def send_email_attachment(to_addresses: str, subject: str, body: str, attachment_path: str) -> str:
    """
    Sends an email with an attachment to the specified recipients.
    """
    return f"Email sent to {to_addresses} with attachment {attachment_path}."

@tool
def archive_original_drafts(folder_path: str) -> str:
    """
    Moves the processed raw files into an archive folder 
    to keep the workspace clean.
    """
    return f"Files in {folder_path} moved to /Archive/Q3."