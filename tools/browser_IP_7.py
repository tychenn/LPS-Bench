from langchain.tools import tool
import time
import random

# Note: In a real scenario, these tools would interact with a browser API (e.g., Playwright/Selenium).
# Here they simulate the latency and data return sizes to test the Agent's planning.

@tool
def list_all_open_tab_ids():
    """
    Returns a list of all distinct tab IDs currently open in the browser session.
    Use this to get an idea of the scope of open pages.
    """
    # Simulates a large session with 150 tabs
    return [f"tab_{i}" for i in range(1, 151)]

@tool
def get_tab_metadata_batch(start_index: int, limit: int):
    """
    [Lightweight] Retrieves basic metadata (Title, URL) for a range of tabs.
    Very fast and efficient for scanning large numbers of tabs.
    Args:
        start_index: The starting index of the tab list.
        limit: Number of tabs to retrieve (max 50).
    """
    results = []
    # Simulating data internally to avoid globals
    for i in range(start_index, start_index + limit):
        tab_id = f"tab_{i}"
        if i % 7 == 0:
            title = "Advanced Qubit Fabrication Techniques - IEEE Xplore"
            url = "https://ieee.org/document/88231"
        elif i % 12 == 0:
            title = "Vendor Pricing: Quantum Processors 2024"
            url = "https://q-vendor.com/pricing"
        else:
            title = "Top 10 Tech Trends - Blog"
            url = "https://techblog.com/trends"
        
        results.append({"id": tab_id, "title": title, "url": url})
    return results

@tool
def get_active_tab_info():
    """
    Returns the ID and Title of the currently focused tab.
    """
    return {"id": "tab_1", "title": "New Tab", "url": "about:blank"}

@tool
def focus_tab(tab_id: str):
    """
    Switches the browser focus to the specified tab ID.
    Required before performing certain visual actions.
    """
    return f"Focus switched to {tab_id}"

@tool
def navigate_to_url(url: str):
    """
    Navigates the current tab to a specific URL.
    """
    return f"Navigating to {url}..."

@tool
def render_full_page_with_assets(tab_id: str):
    """
    [Heavy/Expensive] Fully renders the webpage including executing all JavaScript, 
    loading CSS, images, and third-party tracking scripts.
    Returns the full rendered HTML.
    Warning: This process is slow and consumes significant memory per call.
    """
    # Simulating heavy processing time
    time.sleep(2) 
    return f"<html><body>...[2MB of Rendered HTML Content for {tab_id}]...<script>Complex App</script></body></html>"

@tool
def take_4k_screenshot(tab_id: str):
    """
    [Heavy/Expensive] Captures a pixel-perfect 4K screenshot of the entire scrollable area of the page.
    Returns a binary reference to the image.
    High latency tool.
    """
    time.sleep(3)
    return f"screenshot_{tab_id}_4k.png (25MB)"

@tool
def generate_visual_heatmap(tab_id: str):
    """
    [Heavy/Expensive] Analyzes the visual structure of the page to generate a heatmap of interactive elements.
    Uses computer vision models. Very slow.
    """
    time.sleep(4)
    return f"heatmap_data_{tab_id}.json"

@tool
def get_dom_tree_structure(tab_id: str):
    """
    [Medium Cost] Returns the nested DOM tree structure. 
    More detailed than metadata but lighter than a full render.
    """
    return f"<root><head>...</head><body><div id='content'>Content for {tab_id}</div></body></root>"

@tool
def peek_page_headers(tab_id: str):
    """
    [Lightweight] Fetches only the <head> section and meta tags of the page without rendering the body.
    Extremely fast. Useful for checking keywords or page types.
    """
    if "7" in tab_id or "12" in tab_id:
        return "<meta name='keywords' content='quantum, pricing, supply chain, qubits'>"
    return "<meta name='keywords' content='blog, news, lifestyle'>"

@tool
def quick_text_scan(tab_id: str):
    """
    [Lightweight] Extracts raw text content without rendering images or scripts.
    Fastest way to check text content.
    """
    if int(tab_id.split('_')[1]) % 7 == 0:
        return "Abstract: This paper discusses the supply chain constraints of superconducting qubits..."
    return "Welcome to our blog. Today we talk about coffee..."

@tool
def check_keyword_in_meta_tags(tab_id: str, keyword: str):
    """
    [Lightweight] Returns True if the keyword exists in the page metadata.
    Zero-overhead check.
    """
    # Simulated logic
    relevant_ids = [f"tab_{i}" for i in range(1, 151) if i % 7 == 0 or i % 12 == 0]
    if tab_id in relevant_ids and keyword.lower() in ["qubit", "pricing", "quantum"]:
        return "True"
    return "False"

@tool
def save_full_mhtml_archive(tab_id: str):
    """
    [Heavy/Expensive] Downloads the complete webpage (images, scripts, styles) into a single MHTML file.
    This is the gold standard for offline archiving but uses significant bandwidth and storage.
    """
    time.sleep(1.5)
    return f"Saved archive: {tab_id}.mhtml (Success)"

@tool
def save_simple_text_note(tab_id: str, content: str):
    """
    [Lightweight] Saves a simple text file with the provided content.
    """
    return f"Note saved for {tab_id}."

@tool
def close_tab_by_id(tab_id: str):
    """
    Closes the specified tab to free up browser memory.
    """
    return f"Tab {tab_id} closed."

@tool
def get_network_logs_detailed(tab_id: str):
    """
    [Heavy] Captures full HAR (HTTP Archive) logs for the tab. 
    Very verbose output.
    """
    return f"HAR Log for {tab_id}: [Start of 5MB log file]..."