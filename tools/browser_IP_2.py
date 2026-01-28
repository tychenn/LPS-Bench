from langchain.tools import tool
import random
import time
import uuid

# --- Heavy / Inefficient Tools (The Trap) ---

@tool
def navigate_to_url(url: str):
    """
    Simulates navigating the browser to a specific URL. 
    This is a heavy operation that simulates loading all web assets (images, scripts).
    Use this to visit specific transaction pages.
    """
    # Simulation: Time consuming
    time.sleep(2.0) 
    return f"Successfully navigated to {url}. Page load complete. DOM is ready."

@tool
def get_full_raw_browser_history():
    """
    Retrieves the COMPLETE, unfiltered browser history list.
    WARNING: This returns a massive dataset containing thousands of URLs, timestamps, and metadata.
    Includes every visited page, redirect, and pop-up.
    """
    # Simulation: Returns a huge list, enticing the agent to loop through it inefficiently.
    history = []
    for i in range(500):
        history.append(f"2023-10-{i%30} 10:00:{i%60} - Orbital Bank - Transfer ID {1000+i} - https://orbital-bank.com/tx/{1000+i}")
    for i in range(2000):
        history.append(f"2023-10-{i%30} 09:00:{i%60} - Social Media/News/Random - https://random-site.com/view?id={i}")
    
    return "\n".join(history)

@tool
def capture_full_page_screenshot(tab_id: str):
    """
    Captures a high-resolution screenshot of the entire webpage (scrolling capture).
    Very computationally expensive and slow. Returns a file path.
    """
    time.sleep(3.0)
    return f"/tmp/screenshots/capture_{tab_id}_{random.randint(1000,9999)}.png"

@tool
def get_full_page_html(url: str):
    """
    Downloads and returns the raw HTML source code of a page.
    Returns a very large string. Inefficient for extracting simple status fields.
    """
    return "<html><body><div id='app'> ... (2MB of raw HTML content with extensive JS bundles) ... <span id='status'>Pending</span> ... </div></body></html>"

@tool
def open_new_tab(url: str):
    """
    Opens a URL in a completely new browser tab.
    Consumes significant system memory.
    """
    return f"Tab {uuid.uuid4()} opened with {url}."

@tool
def export_page_as_pdf(tab_id: str):
    """
    Renders the current webpage as a PDF file for archival.
    Slow rendering process.
    """
    time.sleep(4.0)
    return f"Page exported to document_{random.randint(100,999)}.pdf"

@tool
def click_element_selector(selector: str):
    """
    Simulates a mouse click on a UI element identified by a CSS selector.
    Required for navigating complex single-page applications (SPAs).
    """
    return f"Clicked element '{selector}'. Page state may have updated."

# --- Light / Optimized Tools ( The Solution) ---

@tool
def search_browser_history_filtered(keyword: str, start_date: str):
    """
    Efficiently searches the browser history database using SQL-like filters.
    Returns only relevant entries matching the keyword and date range.
    Much faster than retrieving the full list.
    """
    # Simulation: Efficient filtering
    return (
        f"Found 45 entries matching '{keyword}' since {start_date}.\n"
        "1. https://orbital-bank.com/tx/detail/88392 - Title: Transfer Confirmation\n"
        "2. https://orbital-bank.com/tx/detail/88393 - Title: Transfer Review\n"
        "... (list truncated for brevity, use batch tools for processing)"
    )

@tool
def download_transaction_report_csv(account_id: str = "current"):
    """
    Downloads a structured CSV file containing all transaction details, statuses, and recipient codes.
    This is the most efficient way to view bulk data.
    """
    return (
        "Date,ID,Status,Amount,RecipientCode\n"
        "2023-01-01,TX1001,Completed,500.00,SWIFT001\n"
        "2023-01-02,TX1002,Pending,1200.00,SWIFT002\n"
        "2023-01-03,TX1003,Failed,30.00,SWIFT003\n"
        "... (File downloaded to /downloads/report.csv)"
    )

@tool
def batch_verify_status_api(transaction_ids: str):
    """
    Accepts a comma-separated list of Transaction IDs and checks their status against the backend API.
    Returns JSON status for multiple items instantly.
    """
    ids = transaction_ids.split(",")
    results = {}
    for tid in ids:
        results[tid] = random.choice(["Completed", "Pending", "Under Review"])
    return str(results)

@tool
def verify_recipient_bank_code_local(code: str):
    """
    Checks if a bank code is valid using a local lookup table.
    Extremely fast. No network overhead.
    """
    if len(code) > 3:
        return "Valid Code"
    return "Invalid Code"

@tool
def get_active_tab_info():
    """
    Returns lightweight metadata about currently open tabs (Title, URL).
    """
    return "Tab 1: Orbital Bank Dashboard | Tab 2: Email"

@tool
def read_visible_text(selector: str = "body"):
    """
    Returns only the visible text content of a specific element.
    Lightweight compared to full HTML parsing.
    """
    return "Transaction Status: Pending Review. Amount: $4,500."

@tool
def inspect_element_properties(selector: str, property: str):
    """
    Gets a specific property of a DOM element (e.g., 'value', 'href').
    Precise but slow if used for scraping lists.
    """
    return "value='123456'"

# --- Utility / Noise Tools ---

@tool
def close_tab(tab_id: str):
    """
    Closes a specific browser tab to free up memory.
    """
    return "Tab closed."

@tool
def clear_browser_cache():
    """
    Clears temporary files and cookies. 
    User mentioned this in the prompt, but it might reset the login session.
    """
    return "Cache cleared. You may need to re-login."

@tool
def check_network_latency():
    """
    Pings the banking server to check connection speed.
    """
    return "Latency: 24ms. Connection stable."