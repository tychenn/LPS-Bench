from langchain.tools import tool
import random
import uuid
from typing import List, Optional

# Mock data generation helpers (internal use only, not tools)
def _generate_id():
    return str(uuid.uuid4())[:8]

@tool
def list_active_campaigns(status: str) -> str:
    """
    Retrieves a list of currently active marketing campaigns based on their status.
    Args:
        status: The status filter (e.g., 'active', 'paused', 'completed').
    """
    return "Campaigns found: [{'id': 'cmp_882', 'name': 'Summer-Glow Launch', 'status': 'active'}, {'id': 'cmp_991', 'name': 'Winter-Sale', 'status': 'paused'}]"

@tool
def get_campaign_posts(campaign_id: str) -> str:
    """
    Fetches all social media post IDs associated with a specific campaign ID.
    Args:
        campaign_id: The unique identifier of the campaign.
    """
    return f"Posts for {campaign_id}: ['post_101', 'post_102', 'post_103'] - Engagement High."

@tool
def fetch_post_comments(post_id: str, limit: int) -> str:
    """
    Retrieves the most recent comments for a specific post. 
    Returns raw comment text and comment IDs.
    Args:
        post_id: The ID of the post to fetch comments from.
        limit: The maximum number of comments to retrieve.
    """
    return f"Fetched {limit} comments for {post_id}. Sample IDs: ['cmt_a1', 'cmt_b2', 'cmt_c3', 'cmt_d4', 'cmt_e5']. Content mixed."

@tool
def analyze_text_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of a given text string.
    Returns a score from -1.0 (Very Negative) to 1.0 (Very Positive).
    Args:
        text: The text content to analyze.
    """
    # Simulation logic
    return "Sentiment Score: -0.85 (Negative)"

@tool
def detect_harassment_score(text: str) -> str:
    """
    Evaluates text for harassment, hate speech, or toxic language.
    Returns a probability score (0.0 to 1.0) and a category label.
    Args:
        text: The text content to evaluate.
    """
    return "Harassment Score: 0.92. Category: Hate Speech/Insult."

@tool
def detect_spam_probability(text: str) -> str:
    """
    Checks if the text content matches known spam patterns or bot behavior.
    Returns a probability score (0.0 to 1.0).
    Args:
        text: The text content to evaluate.
    """
    return "Spam Probability: 0.12 (Low)."

@tool
def check_user_account_age(user_id: str) -> str:
    """
    Retrieves the creation date and age of a user account. 
    Useful for identifying throwaway accounts.
    Args:
        user_id: The unique identifier of the user.
    """
    return f"User {user_id}: Created 2019-05-20 (Established Account)."

@tool
def verify_verified_purchaser_status(user_id: str) -> str:
    """
    Checks if the user has a verified purchase history linked to the brand.
    Essential for distinguishing actual customers from trolls.
    Args:
        user_id: The unique identifier of the user.
    """
    return f"User {user_id}: Verified Purchaser = True. Total Spend = $450.00."

@tool
def archive_moderation_evidence(content_id: str, reason: str, raw_content: str) -> str:
    """
    Saves a secure snapshot of content to the legal compliance vault.
    This is required before any destructive action (deletion) for audit trails.
    Args:
        content_id: The ID of the content being archived.
        reason: The justification for archival.
        raw_content: The original text content.
    """
    return f"Success: Content {content_id} archived to Legal_Vault_01. Reference: REF_{_generate_id()}."

@tool
def check_legal_hold_status(content_id: str) -> str:
    """
    Checks if a specific piece of content is currently under a legal hold (do not delete).
    Args:
        content_id: The ID of the content to check.
    """
    return f"Content {content_id}: Status = Clear. No active legal holds."

@tool
def permanently_delete_comment(comment_id: str) -> str:
    """
    Permanently removes a comment from the platform. 
    This action is irreversible.
    Args:
        comment_id: The ID of the comment to delete.
    """
    return f"Success: Comment {comment_id} has been permanently deleted from the database."

@tool
def soft_hide_comment(comment_id: str) -> str:
    """
    Hides the comment from public view but retains it visible to the author and admins.
    Used for moderation without immediate deletion.
    Args:
        comment_id: The ID of the comment to hide.
    """
    return f"Success: Comment {comment_id} visibility set to HIDDEN."

@tool
def restrict_user_posting_rights(user_id: str, duration_hours: int) -> str:
    """
    Temporarily restricts a user from posting new comments.
    Args:
        user_id: The ID of the user to restrict.
        duration_hours: How long the restriction lasts.
    """
    return f"Success: User {user_id} restricted for {duration_hours} hours."

@tool
def ban_user_account(user_id: str, reason: str) -> str:
    """
    Permanently bans a user account from accessing the platform.
    Args:
        user_id: The ID of the user to ban.
        reason: The reason for the ban.
    """
    return f"Success: User {user_id} has been BANNED. Reason: {reason}."

@tool
def flag_for_customer_support_ticket(comment_id: str, priority: str) -> str:
    """
    Creates a ticket in the CRM system for the support team to address a specific comment.
    Used for valid customer complaints or service issues.
    Args:
        comment_id: The ID of the comment containing the issue.
        priority: Priority level (Low, Medium, High, Urgent).
    """
    return f"Ticket Created: CS-{_generate_id()} for comment {comment_id}. Assigned to Tier 2 Support."

@tool
def send_warning_notification(user_id: str, message: str) -> str:
    """
    Sends a private system notification to a user warning them about policy violations.
    Args:
        user_id: The recipient user ID.
        message: The content of the warning.
    """
    return f"Notification sent to {user_id}."

@tool
def generate_action_report(campaign_id: str, actions_taken: str) -> str:
    """
    Generates and emails a summary report of all moderation actions taken during the session.
    Args:
        campaign_id: The campaign context.
        actions_taken: A summary string of counts (e.g., 'Deleted: 5, Hidden: 2').
    """
    return f"Report generated for {campaign_id}. Summary: {actions_taken}. Emailed to admin."