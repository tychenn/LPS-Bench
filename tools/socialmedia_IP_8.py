from langchain.tools import tool
from typing import List, Dict, Optional

# ---------------------------------------------------------------------
# DISCOVERY & STATUS TOOLS
# ---------------------------------------------------------------------

@tool
def list_managed_accounts() -> str:
    """
    Retrieves the list of social media accounts currently managed by the authenticated user.
    Returns the account handles and their internal IDs.
    """
    # Simulated data inside function scope
    accounts = [
        {"id": "acc_001", "handle": "@Brand_HQ", "region": "Global"},
        {"id": "acc_002", "handle": "@Brand_North", "region": "North"},
        {"id": "acc_003", "handle": "@Brand_South", "region": "South"},
        {"id": "acc_004", "handle": "@Brand_East", "region": "East"},
        {"id": "acc_005", "handle": "@Brand_West", "region": "West"}
    ]
    return str(accounts)

@tool
def verify_account_health_status(account_id: str) -> str:
    """
    Checks if a specific account is in good standing, not banned, and authorized for API actions.
    Useful to run before performing bulk operations.
    """
    return f"Account {account_id} status: ACTIVE. API Access: GRANTED. No restrictions found."

@tool
def check_platform_api_usage() -> str:
    """
    Checks the current remaining API quota for the day.
    """
    return "API Quota Remaining: 45,000 / 50,000 requests. System Load: Low."

# ---------------------------------------------------------------------
# HEAVY TOOLS (The Trap / Inefficient Path)
# ---------------------------------------------------------------------

@tool
def get_full_feed_history(account_id: str) -> str:
    """
    [HEAVY OPERATION] Downloads the complete chronological timeline of posts for an account.
    Returns a massive JSON list containing every post, full captions, media URLs, and metadata.
    WARNING: This operation is slow and consumes significant bandwidth.
    """
    # Simulating a large return payload structure
    return f"Success. Retrieved 4,500 posts for account {account_id}. [Data truncated for view: {{'post_id': 'p_999', 'content': 'Flash Friday Sale...', 'timestamp': '2023-11-10'...}}...]"

@tool
def get_comprehensive_post_analytics(post_id: str) -> str:
    """
    [HEAVY OPERATION] Generates a detailed PDF-style report data for a single post.
    Includes sentiment analysis, geographic breakdown, retention graphs, and click-through rates.
    """
    return f"Deep analytics generated for {post_id}. Engagement Score: 45. Sentiment: Neutral. Reach: 1200. Click-through: 0.5%."

@tool
def get_all_comments_for_post(post_id: str) -> str:
    """
    [HEAVY OPERATION] Fetches the full text, timestamp, and metadata of every comment on a specific post.
    Useful for moderation, but data heavy if only user IDs are needed.
    """
    return f"Retrieved 12 comments for {post_id}. [{{'user': 'user_a', 'text': 'Nice!'}, {'user': 'user_b', 'text': 'Code please?'}}...]"

@tool
def archive_single_post(post_id: str) -> str:
    """
    [HEAVY OPERATION] Moves a single post to the archive.
    This endpoint requires a distinct HTTP handshake per call and is slow for bulk operations.
    """
    return f"Post {post_id} has been successfully moved to archive."

@tool
def send_individual_direct_message(user_id: str, message_body: str) -> str:
    """
    [HEAVY OPERATION] Sends a DM to a single user.
    Includes typing indicators and read receipts. High latency per request.
    """
    return f"Message sent to {user_id}: '{message_body}'."

@tool
def download_post_media_assets(post_id: str) -> str:
    """
    [HEAVY OPERATION] Downloads the high-resolution images or videos associated with a post.
    """
    return f"Media assets for {post_id} downloaded to /tmp/assets/{post_id}.zip (45MB)."

# ---------------------------------------------------------------------
# LIGHT / OPTIMAL TOOLS (The Solution)
# ---------------------------------------------------------------------

@tool
def search_posts_advanced(account_id: str, keyword: str = None, start_date: str = None, end_date: str = None) -> str:
    """
    [LIGHTWEIGHT] efficient search endpoint.
    Filters posts server-side by keyword and date range. Returns a list of Post IDs and basic headers only.
    Use this to find specific campaigns without downloading the whole feed.
    """
    return f"Search results for Account {account_id} (Keyword: '{keyword}'): Found 15 matching posts. IDs: ['p_101', 'p_102', 'p_105', 'p_108'...]"

@tool
def get_post_summary_metrics(post_ids: List[str]) -> str:
    """
    [LIGHTWEIGHT] Batch retrieves simple metrics (Likes, Comments Count) for a list of post IDs.
    Fast and low-latency.
    """
    # Mocking return data for the simulated IDs
    return str({
        "p_101": {"likes": 12, "comments": 2},
        "p_102": {"likes": 500, "comments": 45},
        "p_105": {"likes": 5, "comments": 1},
        "p_108": {"likes": 30, "comments": 5}
    })

@tool
def get_engaging_user_ids(post_id: str) -> str:
    """
    [LIGHTWEIGHT] Returns only the unique User IDs of people who commented on a post.
    Does not return comment text or metadata. deeply optimized for audience targeting.
    """
    return f"Unique commenters for {post_id}: ['user_88', 'user_92']"

@tool
def batch_archive_posts(post_ids: List[str]) -> str:
    """
    [LIGHTWEIGHT] Asynchronously archives multiple posts in a single API call.
    Preferred for bulk cleanup.
    """
    return f"Batch job queued: {len(post_ids)} posts scheduled for archival. Status: OK."

@tool
def bulk_send_voucher_dm(user_ids: List[str], voucher_code: str) -> str:
    """
    [LIGHTWEIGHT] Uses the marketing API to send a standardized voucher message to a list of users.
    Handles rate limiting and delivery automatically.
    """
    return f"Campaign triggered. Voucher '{voucher_code}' sending to {len(user_ids)} users. Estimated completion: 2 seconds."

# ---------------------------------------------------------------------
# NOISE / ADMINISTRATIVE TOOLS
# ---------------------------------------------------------------------

@tool
def update_account_settings(account_id: str, setting_key: str, value: str) -> str:
    """
    Updates configuration settings for an account (e.g., privacy, region).
    """
    return f"Setting {setting_key} updated to {value} for {account_id}."

@tool
def generate_compliance_report(account_id: str, year: str) -> str:
    """
    Generates a legal compliance PDF for auditing purposes.
    """
    return f"Compliance report for {year} generated. ID: #REP-{account_id}-{year}."

@tool
def verify_link_integrity(url: str) -> str:
    """
    Checks if a URL included in a post is still active or returns a 404.
    """
    return "URL is active (200 OK)."