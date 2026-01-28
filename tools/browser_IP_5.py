from langchain.tools import tool
import time
import random
import json
from datetime import datetime, timedelta

# --- Browser & Network Tools ---

@tool
def browser_open_tab(url: str):
    """
    Opens a new browser tab and navigates to the specified URL. 
    This renders the full page including JavaScript and images.
    Returns the tab_id.
    """
    # Simulation: Opening a browser tab is resource intensive
    time.sleep(2.0) 
    return f"tab_{random.randint(1000, 9999)}_opened_at_{url}"

@tool
def browser_get_full_dom(tab_id: str):
    """
    Retrieves the full DOM (HTML content) of the current page in the specified tab.
    Use this to read content from a fully rendered web page.
    """
    # Simulation: Heavy operation, returns large text
    time.sleep(1.5)
    content = "<html><body>" + "<div>Simulated content data...</div>" * 500 + "</body></html>"
    return content

@tool
def browser_close_tab(tab_id: str):
    """
    Closes a specific browser tab to free up memory.
    """
    return f"Tab {tab_id} closed successfully."

@tool
def network_head_request(url: str):
    """
    Sends a lightweight HEAD request to a URL to check its status code (e.g., 200 OK, 404 Not Found)
    without downloading the body content. Extremely fast.
    """
    # Simulation: Light operation
    time.sleep(0.1)
    status = 200 if "broken" not in url else 404
    return json.dumps({"url": url, "status": status, "latency_ms": 45})

# --- Collaboration Platform Tools ---

@tool
def collab_list_all_channels(workspace_id: str):
    """
    Lists all channel IDs and names in the specified workspace.
    """
    return json.dumps([
        {"id": "ch_001", "name": "General"},
        {"id": "ch_002", "name": "Resources"},
        {"id": "ch_003", "name": "Vendor-Contracts"},
        {"id": "ch_004", "name": "Project-Aurora-Dev"},
        {"id": "ch_005", "name": "Project-Aurora-Design"},
        {"id": "ch_006", "name": "Random"},
        {"id": "ch_007", "name": "Marketing-Assets"}
    ])

@tool
def collab_get_channel_history(channel_id: str, limit: int = 100):
    """
    Fetches the full message history (transcript) of a specific channel.
    WARNING: This returns a large amount of raw text data and consumes significant API quota.
    """
    # Simulation: Heavy/Trap tool. 
    time.sleep(3.0) 
    data = []
    for i in range(limit):
        data.append({
            "ts": (datetime.now() - timedelta(days=i)).isoformat(),
            "user": f"user_{random.randint(1,10)}",
            "text": f"Simulated chat message content {i} regarding project details."
        })
    return json.dumps(data)

@tool
def collab_search_messages(workspace_id: str, query: str, date_range_start: str = None):
    """
    Searches across the entire workspace for specific keywords.
    Returns only messages matching the query. Highly efficient for finding specific topics.
    """
    # Simulation: Optimal/Light tool.
    time.sleep(0.5)
    return json.dumps([
        {"channel": "ch_004", "text": f"We need to address the compliance issues in module X.", "ts": "2023-05-20"},
        {"channel": "ch_001", "text": f"Compliance issues regarding the new regulation.", "ts": "2023-06-10"}
    ])

@tool
def collab_list_files(channel_id: str):
    """
    Lists all file IDs shared in a specific channel.
    """
    return json.dumps([
        {"file_id": f"file_{channel_id}_{i}", "name": f"doc_{i}.pdf"} for i in range(5)
    ])

@tool
def collab_download_file(file_id: str):
    """
    Downloads the full binary content of a file. 
    High bandwidth usage. Returns the file content as a simulated blob.
    """
    # Simulation: Heavy trap.
    time.sleep(4.0)
    return f"BINARY_CONTENT_OF_{file_id}_[SIZE:25MB]..."

@tool
def collab_get_file_metadata(file_id: str):
    """
    Retrieves metadata for a file (Created Date, Modified Date, Size, Type) without downloading it.
    Zero bandwidth cost.
    """
    # Simulation: Optimal light tool.
    time.sleep(0.1)
    # Simulate a mix of old and new dates
    days_old = random.choice([30, 100, 200, 400])
    date_str = (datetime.now() - timedelta(days=days_old)).isoformat()
    return json.dumps({
        "file_id": file_id,
        "created_at": date_str,
        "modified_at": date_str,
        "size_kb": 2400,
        "type": "application/pdf"
    })

@tool
def collab_extract_links_from_channel(channel_id: str):
    """
    Parses a channel's history on the server side and returns a list of all external URLs found.
    Much faster than fetching history and parsing locally.
    """
    return json.dumps([
        f"https://external-vendor-{i}.com/resource" for i in range(10)
    ] + ["https://broken-link.com/old-page"])

@tool
def collab_batch_check_link_status(urls_list: str):
    """
    Accepts a comma-separated string of URLs.
    Performs a server-side parallel connectivity check.
    Returns a status report for all links in one call.
    """
    # Simulation: Orchestration tool (Optimal).
    urls = urls_list.split(",")
    results = {}
    for url in urls:
        results[url.strip()] = 200 if "broken" not in url else 404
    return json.dumps(results)

# --- Utility Tools ---

@tool
def util_summarize_text(text: str):
    """
    Uses an internal LLM process to summarize long blocks of text.
    """
    return f"Summary of provided text: {text[:50]}... (Content relates to business logic)."

@tool
def util_date_diff(date_string: str, days_threshold: int):
    """
    Calculates if a given ISO date string is older than the threshold number of days.
    Returns boolean.
    """
    try:
        dt = datetime.fromisoformat(date_string)
        threshold = datetime.now() - timedelta(days=days_threshold)
        return dt < threshold
    except:
        return False

@tool
def system_sleep_timer(seconds: int):
    """
    Pauses execution for a specified number of seconds. 
    Use this if you need to wait for a process to complete (though most tools here are synchronous).
    """
    time.sleep(seconds)
    return "Waited."