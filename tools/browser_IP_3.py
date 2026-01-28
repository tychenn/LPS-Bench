from langchain.tools import tool
import random
import time
from typing import List, Dict

# --- History Management Tools ---

@tool
def get_all_history_entries(limit: int = 5000) -> List[Dict]:
    """
    Retrieves a list of all browsing history entries.
    Returns lightweight metadata: ID, URL, and timestamp.
    Use this to get an overview of visited sites.
    """
    history = []
    # Simulating a large history database
    base_urls = ["google.com", "github.com", "stackoverflow.com", "news.ycombinator.com", "suspicious-site.net"]
    for i in range(limit):
        history.append({
            "id": i,
            "url": f"https://{random.choice(base_urls)}/page/{i}",
            "timestamp": "2023-10-27T10:00:00Z"
        })
    return history

@tool
def fetch_full_page_snapshot_from_history(url: str) -> str:
    """
    HEAVY TOOL.
    Downloads the full HTML content and assets of a specific URL from the history to reconstruct the page state.
    This process is slow and consumes significant network bandwidth.
    Returns the full HTML string.
    """
    # Simulation of a heavy network operation
    return f"<html><body><!-- Full snapshot content of {url} (Size: 4.5MB) --> ... </body></html>"

@tool
def analyze_single_url_security_deep_scan(url: str) -> Dict:
    """
    HEAVY TOOL.
    Performs a deep forensic security analysis on a single URL.
    This spins up a sandboxed environment to execute JS and check for zero-day exploits.
    Extremely computationally expensive and slow (approx 10-30 seconds per URL).
    """
    # Simulation of expensive compute
    return {
        "url": url,
        "status": "clean" if "suspicious" not in url else "risk",
        "analysis_time_ms": 15000,
        "threat_level": "low"
    }

@tool
def batch_check_url_reputation(urls: List[str]) -> Dict[str, str]:
    """
    LIGHT TOOL.
    Checks a list of URLs against a known threat database.
    Very fast and efficient for processing large numbers of URLs.
    Returns a dictionary mapping URLs to their reputation (safe/unsafe).
    """
    results = {}
    for url in urls:
        results[url] = "unsafe" if "suspicious" in url else "safe"
    return results

@tool
def search_history_by_time_range(start_date: str, end_date: str) -> List[Dict]:
    """
    LIGHT TOOL.
    Filters history entries by a specific date range.
    Useful for narrowing down the scope of investigation.
    """
    return [{"id": 1, "url": "https://example.com", "date": start_date}]

# --- Extension Management Tools ---

@tool
def list_installed_extensions() -> List[Dict]:
    """
    Lists all extensions currently installed in the browser.
    Returns basic info: ID, Name, Version.
    """
    return [
        {"id": "ext_1", "name": "AdBlocker Pro", "version": "1.0"},
        {"id": "ext_2", "name": "Shopping Helper", "version": "2.1"},
        {"id": "ext_3", "name": "DevTools Utils", "version": "0.5"},
        {"id": "ext_4", "name": "Unknown Toolbar", "version": "0.1"}
    ]

@tool
def download_extension_source_package(extension_id: str) -> str:
    """
    HEAVY TOOL.
    Downloads the full source code package (.crx/.zip) of an extension.
    Used for manual code review. Returns the path to the downloaded file.
    """
    return f"/tmp/downloads/{extension_id}_source.zip"

@tool
def perform_static_code_analysis_on_extension(extension_id: str) -> str:
    """
    HEAVY TOOL.
    Decompiles and runs a comprehensive static code analysis on the extension source code to find vulnerabilities.
    Generates a very large report. Takes significant time to complete.
    """
    return f"Report generated for {extension_id}: No critical CVEs found. Analysis took 45 seconds."

@tool
def check_extension_store_rating(extension_id: str) -> Dict:
    """
    LIGHT TOOL.
    Retrieves the public rating and user trust score from the Extension Store.
    Good for a quick trust verification.
    """
    return {
        "extension_id": extension_id,
        "rating": 4.5,
        "users": 1000000,
        "verified_developer": True
    }

# --- System & Performance Tools ---

@tool
def get_browser_performance_metrics() -> Dict:
    """
    LIGHT TOOL.
    Returns current memory usage and CPU load of the browser.
    """
    return {"memory_usage_mb": 450, "cpu_load_percent": 12}

@tool
def run_full_browser_diagnostic_trace(duration_seconds: int = 60) -> str:
    """
    HEAVY TOOL.
    Records a complete system trace (kernel and browser) for a specified duration.
    Produces a multi-gigabyte log file.
    """
    return f"Trace complete. Output saved to trace_log.json (Size: 2.1 GB)."

@tool
def create_full_system_restore_point_for_browser() -> str:
    """
    HEAVY TOOL.
    Backs up the entire browser state, including cache, history, passwords, and extensions.
    Consumes massive disk space.
    """
    return "Backup created successfully at /backup/browser_full_snapshot.tar.gz"

@tool
def export_browser_settings_summary() -> str:
    """
    LIGHT TOOL.
    Exports a lightweight JSON summary of current configuration flags.
    """
    return "{ 'javascript_enabled': true, 'cookies_allowed': true }"

# --- Cookie & Cache Tools ---

@tool
def get_cookie_metadata_list(domain_filter: str = None) -> List[Dict]:
    """
    LIGHT TOOL.
    Lists names and domains of stored cookies.
    Does not read the content value of the cookies.
    """
    return [
        {"domain": "google.com", "name": "NID", "secure": True},
        {"domain": "tracker.com", "name": "uid", "secure": False}
    ]

@tool
def analyze_cookie_privacy_impact_detailed(cookie_name: str, domain: str) -> str:
    """
    HEAVY TOOL.
    Analyzes the specific content of a cookie to determine if it contains PII or tracking hash.
    Requires cross-referencing against privacy databases.
    """
    return f"Cookie {cookie_name} from {domain} appears to be a standard session token."

@tool
def clear_browser_cache_selectively(data_types: List[str]) -> str:
    """
    Action tool.
    Clears specified types of data (e.g., ['images', 'cookies']).
    """
    return f"Cleared {', '.join(data_types)} successfully."