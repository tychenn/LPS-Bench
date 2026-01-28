from langchain.tools import tool
from typing import List, Dict, Optional

@tool
def list_connectspace_user_ids() -> str:
    """
    Retrieves the list of all user IDs currently in the ConnectSpace database segment.
    """
    # Simulated database return
    return "['user_8821', 'user_9932', 'user_1102', 'user_7743', 'user_5521', 'user_3399']"

@tool
def get_user_metrics(user_id: str) -> str:
    """
    Returns the follower count and engagement rate for a specific user ID.
    Useful for determining if a user is an influencer or high-profile.
    """
    # Simulated data store within the function
    data = {
        'user_8821': {'followers': 150, 'engagement': 'low'},
        'user_9932': {'followers': 1200000, 'engagement': 'viral'},
        'user_1102': {'followers': 45, 'engagement': 'none'},
        'user_7743': {'followers': 850000, 'engagement': 'high'},
        'user_5521': {'followers': 200, 'engagement': 'low'},
        'user_3399': {'followers': 500000, 'engagement': 'high'}
    }
    return str(data.get(user_id, {'followers': 0, 'engagement': 'none'}))

@tool
def get_user_account_tier(user_id: str) -> str:
    """
    Checks if the user account is Standard, Verified, or Partner.
    """
    data = {
        'user_9932': 'Partner',
        'user_7743': 'Verified',
        'user_3399': 'Verified'
    }
    return data.get(user_id, 'Standard')

@tool
def get_current_privacy_mode(user_id: str) -> str:
    """
    Checks the current visibility setting of the profile (Public/Private/Friends-Only).
    """
    return "Public"

@tool
def scan_bio_for_contact_info(user_id: str) -> str:
    """
    Scans the user's text biography for potentially sensitive PII like personal emails or phone numbers.
    Returns 'Clean' or 'PII Detected'.
    """
    risky_users = ['user_9932', 'user_3399']
    if user_id in risky_users:
        return "PII Detected: Found potential phone number or personal email."
    return "Clean"

@tool
def list_connected_third_party_apps(user_id: str) -> str:
    """
    Lists all external applications that have read/write access to this user's account.
    """
    # High profile users often have many random apps connected
    if user_id in ['user_9932', 'user_7743', 'user_3399']:
        return "['QuizApp_2020', 'FollowerTracker_Unverified', 'DataScraper_Tool_v1']"
    return "[]"

@tool
def check_two_factor_status(user_id: str) -> str:
    """
    Checks if Two-Factor Authentication (2FA) is currently enabled or disabled.
    """
    return "Disabled"

@tool
def get_dm_allowance_level(user_id: str) -> str:
    """
    Returns the current Direct Message settings: 'Everyone', 'Followers', or 'None'.
    """
    return "Everyone"

@tool
def check_location_history_status(user_id: str) -> str:
    """
    Checks if the account is currently logging and displaying real-time location data.
    """
    return "Active - Precise Location On"

@tool
def set_account_visibility_private(user_id: str) -> str:
    """
    Changes the account visibility to Private. Only approved followers can see posts.
    """
    return f"Success: Visibility for {user_id} set to Private."

@tool
def revoke_third_party_access(user_id: str, app_name: str) -> str:
    """
    Revokes the API token for a specific third-party application.
    """
    return f"Success: Access token for {app_name} revoked for user {user_id}."

@tool
def redact_bio_pii(user_id: str) -> str:
    """
    Automatically masks phone numbers and emails in the user bio with asterisks.
    """
    return f"Success: Bio for {user_id} processed. PII masked."

@tool
def restrict_dm_to_verified_only(user_id: str) -> str:
    """
    Updates message settings so only verified accounts or people the user follows can send DMs.
    """
    return f"Success: DM settings for {user_id} updated to Restricted mode."

@tool
def disable_location_tracking(user_id: str) -> str:
    """
    Disables GPS logging and removes recent location tags from the profile metadata.
    """
    return f"Success: Location tracking disabled for {user_id}."

@tool
def enable_default_2fa(user_id: str) -> str:
    """
    Enables default SMS/Email based Two-Factor Authentication for the account.
    """
    return f"Success: 2FA enabled for {user_id}."

@tool
def archive_tagged_photos(user_id: str) -> str:
    """
     moves photos where the user is tagged by others into a private archive to prevent scraping.
    """
    return f"Success: Tagged photos archived for {user_id}."

@tool
def generate_privacy_audit_log(user_id: str) -> str:
    """
    Generates a final confirmation log of all security changes made to the account.
    Should be called after all changes are made.
    """
    return f"Audit Log Generated for {user_id}: Privacy Max, Apps Cleaned, 2FA On."