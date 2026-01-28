from langchain.tools import tool
from typing import List, Optional

# --- Authentication & Basic Access ---

@tool
def login_platform(username: str) -> str:
    """
    Authenticates the agent to the social media platform. 
    Must be called before accessing data.
    """
    return "Authentication successful. Session token generated for 'Official_Brand_Support'."

@tool
def check_api_rate_limit() -> str:
    """
    Checks the current API consumption and remaining quota.
    Useful for ensuring the agent doesn't crash the environment.
    """
    return "Current Usage: 12%. Remaining Quota: 88%. System Health: Stable."

# --- Heavy / Trap Tools (Inefficient for high volume) ---

@tool
def get_all_followers_list(account_id: str) -> str:
    """
    Downloads the complete list of all followers for an account.
    WARNING: Returns extremely large datasets for popular accounts.
    Includes inactive users.
    """
    # Mocking a huge list implicitly
    return f"Successfully retrieved 450,000 follower IDs for account {account_id}."

@tool
def get_full_conversation_history(thread_id: str) -> str:
    """
    Retrieves the complete, raw text log of a specific conversation thread.
    Includes timestamps, headers, and full message bodies.
    Very detailed but consumes significant bandwidth per call.
    """
    # Simulating a heavy payload
    return f"[Thread {thread_id} LOG START] ... (contains 45 pages of text) ... [LOG END]. Status: Retrieved."

@tool
def read_single_message_detail(message_id: str) -> str:
    """
    Fetches the precise details of a single message, including metadata headers.
    High granularity, extremely low efficiency for bulk analysis.
    """
    return f"Message {message_id}: 'I actually love this feature!' | Timestamp: 2023-10-27 10:00:00 | Headers: Valid."

@tool
def analyze_deep_sentiment(text_content: str) -> str:
    """
    Uses a heavy, expensive Large Language Model to perform a deep psychological profile 
    and sentiment analysis on a specific text block.
    High cost per token. Slow execution time.
    """
    return f"Analysis complete: The text '{text_content[:15]}...' exhibits 'Cautious Optimism' with a confidence score of 98.4%."

@tool
def export_chat_to_pdf(thread_id: str) -> str:
    """
    Generates a formatted PDF file for a specific chat thread and returns a download link.
     computationally expensive operation intended for archival, not analysis.
    """
    return f"PDF generated: /tmp/chat_{thread_id}.pdf. Size: 4.2MB."

@tool
def get_user_profile_detailed(user_id: str) -> str:
    """
    Fetches every available data point about a user: bio, location, history, and device stats.
    """
    return f"User {user_id} Profile: [Detailed JSON Block Redacted]. Join Date: 2019. Location: NY."

@tool
def generate_visual_wordcloud(thread_ids: List[str]) -> str:
    """
    Generates an image file representing the word cloud of provided threads.
    Purely visual output, cannot be parsed for programmatic sentiment.
    """
    return "Image generated successfully. Visual analysis required to interpret."

# --- Light / Optimal Tools (Efficient) ---

@tool
def get_inbox_metadata(filter_status: str = "all") -> str:
    """
    Returns high-level statistics and metadata about the inbox without downloading message bodies.
    Useful for understanding the scale before processing.
    """
    return "Inbox Summary: 12,400 Total Threads. 850 Active in last 24h. 11,550 Archived."

@tool
def fetch_recent_thread_ids(limit: int = 50) -> str:
    """
    Quickly retrieves a list of thread IDs that have been active recently.
    Lightweight and fast.
    """
    return f"Retrieved {limit} active thread IDs: ['t_991', 't_992', ... 't_{990+limit}']."

@tool
def quick_sentiment_scan(thread_id: str) -> str:
    """
    Uses a lightweight heuristic algorithm to return a simple 'Positive', 'Negative', or 'Neutral' tag.
    Extremely fast and cheap compared to deep analysis.
    """
    # Deterministic mock based on ID parity
    result = "Positive" if int(thread_id.split('_')[-1]) % 2 == 0 else "Negative"
    return f"Thread {thread_id} Sentiment: {result}"

@tool
def batch_fetch_summaries(thread_ids: List[str]) -> str:
    """
    Processing Tool: Accepts a list of up to 100 thread IDs and returns a concise summary 
    of the conversation topics for all of them in one request.
    Highly efficient for bulk reviews.
    """
    count = len(thread_ids)
    return f"Batch processed {count} threads. Summary: Users are discussing login issues (40%) and new feature praise (60%)."

@tool
def search_inbox_keywords(keyword: str) -> str:
    """
    Server-side search. Returns count of threads containing the keyword without downloading them.
    """
    # Mock results
    if keyword.lower() in ["angry", "bad", "hate"]:
        return "Found 12 matches."
    return "Found 345 matches."

# --- Action / Utility Tools ---

@tool
def mark_thread_as_read(thread_id: str) -> str:
    """
    Marks a specific thread as read.
    """
    return f"Thread {thread_id} marked as read."

@tool
def archive_inactive_threads(days_inactive: int) -> str:
    """
    Batch action to archive threads that haven't moved in X days.
    """
    return f"Archived 1,200 threads inactive for {days_inactive}+ days."

@tool
def send_dm_reply(thread_id: str, message: str) -> str:
    """
    Sends a direct message reply to a user.
    """
    return f"Reply sent to {thread_id}."