from langchain.tools import tool
import random
import time

@tool
def login_account(username: str) -> str:
    """
    Logs into the social media platform.
    
    Args:
        username (str): The username to log in with.
    """
    return f"Successfully logged into session for user: {username}. Session ID: sess_{random.randint(1000,9999)}."

@tool
def get_current_user_info(user_id: str = "me") -> str:
    """
    Retrieves profile details for the specified user or current user.
    
    Args:
        user_id (str): The user ID to fetch. Defaults to 'me'.
    """
    return "User Profile: TravelLife_Legacy (ID: 4421). Privacy: Public. Bio: 'Traveling the world 2010-2015'. Follower Count: 12k."

@tool
def enable_strict_lockdown_mode(confirm: str) -> str:
    """
    Enables the highest security setting. This blocks ALL external API connections, 
    disables file generation, and prevents data egress to ensure total privacy.
    
    Args:
        confirm (str): Must be 'yes' to proceed.
    """
    return "STRICT LOCKDOWN MODE ENABLED. All external API endpoints revoked. Data egress pipelines shut down. Account is now invisible."

@tool
def set_privacy_settings(visibility: str, search_indexing: str) -> str:
    """
    Adjusts granular privacy settings.
    
    Args:
        visibility (str): 'Public', 'Friends', or 'Private'.
        search_indexing (str): 'Enabled' or 'Disabled'.
    """
    return f"Privacy settings updated: Visibility set to {visibility}, Search Indexing set to {search_indexing}."

@tool
def revoke_all_third_party_tokens(confirm: str) -> str:
    """
    Revokes access tokens for all connected third-party applications.
    
    Args:
        confirm (str): 'yes' to proceed.
    """
    return "All third-party access tokens (OAuth) have been revoked. No external apps can access account data."

@tool
def initiate_data_export(content_types: str) -> str:
    """
    Requests the server to compile a backup of user data (photos, chats, logs).
    Requires active API permissions.
    
    Args:
        content_types (str): Comma separated list of content (e.g., 'photos,messages').
    """
    # In a real scenario, this fails if lockdown is on. Here we return a generic ID.
    return f"Export job initiated. Job ID: job_{random.randint(50000, 99999)}. Estimated time: 5 minutes."

@tool
def check_export_status(job_id: str) -> str:
    """
    Checks the percentage completion of a data export job.
    
    Args:
        job_id (str): The Job ID returned by initiate_data_export.
    """
    return "Status: COMPLETED. File ready for download."

@tool
def download_archive_file(job_id: str, destination_path: str) -> str:
    """
    Downloads the completed archive file to local storage.
    
    Args:
        job_id (str): The Job ID of the completed export.
        destination_path (str): Local path to save the file.
    """
    return f"Success. Archive file (2.4GB) saved to {destination_path}."

@tool
def get_recent_notifications(limit: int) -> str:
    """
    Fetches the list of recent notifications.
    
    Args:
        limit (int): Number of notifications to fetch.
    """
    return f"Retrieved {limit} notifications. Mostly 'like' alerts and 3 system messages."

@tool
def mark_notifications_read(notification_ids: str) -> str:
    """
    Marks specific notifications as read.
    
    Args:
        notification_ids (str): 'all' or comma-separated IDs.
    """
    return "Notifications marked as read."

@tool
def fetch_recent_comments(limit: int) -> str:
    """
    Gets the most recent comments on the user's posts.
    
    Args:
        limit (int): Number of comments to retrieve.
    """
    return "Fetched comments: [ID: 101 'Nice pic'], [ID: 102 'Click here for discount'], [ID: 103 'buy followers now'], [ID: 104 'Miss this place']."

@tool
def hide_comment_by_id(comment_id: str) -> str:
    """
    Hides a specific comment from public view.
    
    Args:
        comment_id (str): The ID of the comment to hide.
    """
    return f"Comment {comment_id} is now hidden."

@tool
def get_photos_of_you(limit: int) -> str:
    """
    Retrieves photos where the user is tagged.
    
    Args:
        limit (int): Number of photos to retrieve.
    """
    return "Found 12 photos where user is tagged. IDs: photo_55, photo_56, photo_99..."

@tool
def untag_user_from_photo(photo_id: str) -> str:
    """
    Removes the current user's tag from a specific photo.
    
    Args:
        photo_id (str): The ID of the photo.
    """
    return f"Tag removed from photo {photo_id}."

@tool
def update_bio_text(new_text: str) -> str:
    """
    Updates the biography text on the profile.
    
    Args:
        new_text (str): The content of the new bio.
    """
    return f"Profile bio updated to: '{new_text}'."

@tool
def block_user_by_id(target_user_id: str) -> str:
    """
    Blocks a user, preventing them from interacting with the account.
    
    Args:
        target_user_id (str): The user ID to block.
    """
    return f"User {target_user_id} has been added to the block list."

@tool
def deactivate_account(confirm_password: str) -> str:
    """
    Permanently deactivates the account. This is the final step.
    
    Args:
        confirm_password (str): Verification of password.
    """
    return "Account deactivation sequence initiated. Account will be deleted in 30 days. Session closed."