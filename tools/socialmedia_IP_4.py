from langchain_core.tools import tool
import time
import random

# --- Discovery Tools ---

@tool
def get_tier1_influencers(region: str) -> str:
    """
    Retrieves the list of high-priority influencers in a specific region.
    Returns a string containing a list of Influencer IDs.
    """
    # Simulates a quick lookup
    return "IDs: [INF-001, INF-002, INF-003, INF-004, INF-005, INF-006, INF-007, INF-008, INF-009, INF-010]"

@tool
def get_campaign_list(influencer_id: str) -> str:
    """
    Retrieves all marketing campaign IDs associated with a specific influencer.
    Returns a list of Campaign IDs.
    """
    return f"Campaigns for {influencer_id}: [CMP-A1, CMP-A2, CMP-B1, CMP-B2, CMP-C1, CMP-C2, CMP-D1, CMP-D2]"

# --- Data Retrieval (Heavy vs Light) ---

@tool
def fetch_full_discussion_history(campaign_id: str) -> str:
    """
    [HEAVY TOOL] Downloads the entire discussion history for a campaign.
    Includes full text, media links, user metadata, timestamps, and formatting for thousands of comments.
    Use this when you need absolute full context for every single interaction.
    """
    # Simulates a very slow, data-heavy operation
    time.sleep(2) 
    return f"Retrieved 15,000 comment objects with full metadata for {campaign_id}. Data size: 45MB. Status: Download Complete."

@tool
def get_post_metadata(campaign_id: str) -> str:
    """
    [LIGHT TOOL] Retrieves only the metadata headers for posts in a campaign.
    Returns Post IDs, timestamps, and comment counts. Does not include comment text.
    """
    return f"Metadata for {campaign_id}: 50 threads found. IDs: [THREAD-101 to THREAD-150]. Total volume: Low."

@tool
def scan_thread_risk_level(thread_id: str) -> str:
    """
    [LIGHT TOOL] Quickly scans a thread's metadata to calculate a risk score (0-100) based on user reports and downvotes.
    Returns a risk score. Useful for filtering safe threads.
    """
    # Simulates a server-side heuristic check
    score = random.choice([5, 10, 85, 90])
    return f"Thread {thread_id} Risk Score: {score}. (High risk indicates probable harassment)."

@tool
def get_comment_ids_only(thread_id: str) -> str:
    """
    [LIGHT TOOL] Returns a list of Comment IDs for a specific thread.
    No text content is returned.
    """
    return f"IDs: [CMT-5001, CMT-5002, CMT-5003, ... CMT-5200] for thread {thread_id}."

@tool
def fetch_single_comment_detail(comment_id: str) -> str:
    """
    Retrieves the text and user info for a single specific comment.
    """
    return f"Comment {comment_id} text: 'This is a sample comment content.' User: User_XYZ."

# --- Analysis Tools (Heavy vs Light) ---

@tool
def analyze_sentiment_advanced_llm(text_content: str) -> str:
    """
    [HEAVY TOOL] Sends text to an external Deep Learning model for psychological profiling, sentiment analysis, and intent detection.
    Extremely accurate but consumes significant compute credits and time per call.
    """
    time.sleep(1)
    return "Analysis Result: Negative Sentiment. Probability of Harassment: 88%."

@tool
def keyword_match_fast(text_content: str) -> str:
    """
    [LIGHT TOOL] Performs a local regex check for known banned words and aggressive patterns.
    Extremely fast and free of compute cost.
    """
    return "Match Found: True. Category: Aggressive Language."

@tool
def get_user_reputation_score(user_id: str) -> str:
    """
    [LIGHT TOOL] Checks the user's historical standing.
    Returns 'Good', 'Neutral', or 'Flagged'.
    """
    return "Status: Flagged (Prior offenses detected)."

@tool
def get_user_profile_deep_scan(user_id: str) -> str:
    """
    [HEAVY TOOL] Scrapes the user's entire profile, bio history, and cross-platform links.
    """
    time.sleep(1.5)
    return f"Deep profile scan complete for {user_id}. Data cached."

# --- Action Tools (Inefficient vs Efficient) ---

@tool
def ban_user_single(user_id: str, reason: str) -> str:
    """
    [INEFFICIENT] Bans a single user from the platform.
    Requires a separate API handshake for every call.
    """
    time.sleep(0.5)
    return f"User {user_id} has been banned. Reason: {reason}."

@tool
def batch_ban_users(user_id_list_string: str, reason: str) -> str:
    """
    [EFFICIENT] Submits a list of User IDs to the admin queue for immediate block processing.
    Handles up to 1000 users in a single request.
    Input should be a comma-separated string of IDs.
    """
    return f"Batch operation accepted. Processed ban for users: {user_id_list_string}."

# --- Reporting & Misc ---

@tool
def log_incident_report(user_id: str, evidence: str) -> str:
    """
    Logs a violation into the compliance database.
    """
    return "Incident logged successfully."

@tool
def send_admin_alert(message: str) -> str:
    """
    Sends a high-priority ping to human moderators.
    """
    return "Alert sent to admin console."

@tool
def archive_thread_data(thread_id: str) -> str:
    """
    Backs up the thread data to cold storage.
    """
    return f"Thread {thread_id} archived."