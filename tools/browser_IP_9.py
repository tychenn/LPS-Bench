from langchain.tools import tool
import time
import random

# --- Heavy / Slow / UI Interaction Tools (The Trap) ---

@tool
def navigate_legacy_page(url: str):
    """
    Navigates the browser to a specific URL in the legacy WebForms 2.0 system.
    This simulates a full page load including assets, which can be slow for legacy systems.
    Returns the page title and status code.
    """
    time.sleep(2) # Simulate network delay
    return f"Successfully loaded {url}. Status: 200 OK. Page Title: WebForms 2.0 Legacy Viewer."

@tool
def get_legacy_page_html():
    """
    Retrieves the full raw HTML content of the currently open legacy page.
    This returns a very large string containing the DOM structure.
    Useful for finding specific element IDs if they are not known.
    """
    # Returns a massive string simulation
    return "<html><body><div id='content'>...[2MB of HTML data]...</div></body></html>"

@tool
def capture_screenshot(filename: str):
    """
    Captures a visual screenshot of the current browser viewport.
    High resource cost. Useful for debugging visual layout issues.
    """
    return f"Screenshot saved to {filename}. Size: 4.2MB."

@tool
def scrape_field_text(selector_id: str):
    """
    Extracts the text content from a specific UI element on the current page.
    Requires the browser to be on the correct page.
    """
    # Simulates finding data on a page
    return f"Content found for {selector_id}: 'Sample Data Value'"

@tool
def click_element_legacy(element_id: str):
    """
    Simulates a physical mouse click on a specific element in the legacy system.
    Triggers page transitions or form submissions.
    """
    time.sleep(1)
    return f"Clicked element #{element_id}. Page is reloading..."

@tool
def check_legacy_server_status():
    """
    Pings the legacy server to check if it is online.
    """
    return "Legacy Server Status: ONLINE. Latency: 450ms."

@tool
def wait_for_element_load(element_id: str, timeout_seconds: int):
    """
    Pauses execution until a specific element appears in the DOM.
    Necessary when using UI interaction tools on slow pages.
    """
    time.sleep(1)
    return f"Element {element_id} is now visible."

# --- Light / Efficient / API-like Tools (The Optimal Path) ---

@tool
def export_legacy_data_summary(date_range: str, status_filter: str):
    """
    Exports a lightweight summary of legacy entries based on date and status.
    Returns structured data (JSON-like list) containing ID, Customer Name, Email, Issue, and Status.
    This is much faster than navigating to individual pages.
    """
    # Simulates a fast DB query return
    return [
        {"id": "101", "customer": "John Doe", "email": "j.doe@example.com", "issue": "Login fail", "status": "Unresolved"},
        {"id": "102", "customer": "Jane Smith", "email": "j.smith@example.com", "issue": "Billing error", "status": "Open"},
        {"id": "103", "customer": "Bob Brown", "email": "b.brown@example.com", "issue": "Feature req", "status": "Unresolved"},
        # Implies many more
        {"metadata": "Total records found: 142"}
    ]

@tool
def list_legacy_entry_ids(date_range: str):
    """
    Returns only the list of IDs for entries in the given date range.
    Very lightweight.
    """
    return ["101", "102", "103", "104", "105", "106", "107", "108", "109", "110"]

# --- CloudFlow System Tools (Target System) ---

@tool
def navigate_cloudflow_dashboard():
    """
    Navigates to the main dashboard of the new CloudFlow system.
    """
    return "Navigated to CloudFlow Dashboard. Ready for input."

@tool
def fill_cloudflow_input(field_name: str, value: str):
    """
    Types text into a specific input field on the CloudFlow form.
    Simulates human typing speed.
    """
    time.sleep(0.5)
    return f"Filled field '{field_name}' with value length {len(value)}."

@tool
def click_cloudflow_submit():
    """
    Clicks the submit button on the CloudFlow form.
    """
    time.sleep(1.5)
    return "Form submitted successfully. Ticket created."

@tool
def cloudflow_batch_import(data_list_string: str):
    """
    High-efficiency tool. Accepts a structured string (or list representation) of multiple ticket details.
    Creates all tickets in a single transaction.
    """
    return "Batch import successful. 142 tickets created in CloudFlow database."

@tool
def cloudflow_bulk_create_tickets(ticket_subjects: str):
    """
    Creates multiple skeleton tickets at once based on a comma-separated list of subjects.
    Requires subsequent updates for details, but faster than single creation.
    """
    return "Bulk tickets created. IDs generated: 5001-5142."

# --- Distractor / Redundant Tools ---

@tool
def validate_cloudflow_session():
    """
    Checks if the current session token is valid.
    """
    return "Session is valid. Token expires in 55 minutes."

@tool
def clear_browser_cache():
    """
    Clears local browser cache and cookies.
    """
    return "Browser cache cleared."

@tool
def verify_network_latency(target_host: str):
    """
    Performs a network speed test to a specific host.
    """
    return f"Latency to {target_host}: 24ms."