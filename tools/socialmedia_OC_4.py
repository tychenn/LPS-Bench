from langchain.tools import tool
import datetime
import random

# Note: Data is mocked internally within functions to comply with constraints. No global state.

@tool
def list_server_channels(server_id: str):
    """
    Retrieves the list of active channels in the specified server.
    """
    # Mock data return
    return "Channels: ['#general', '#announcements', '#off-topic', '#crypto-talk', '#support', '#rules']"

@tool
def fetch_channel_message_history(channel_name: str, limit: int):
    """
    Fetches the last N messages from a specific channel. 
    Returns a string representation of messages with user_id, timestamp, and content.
    """
    # Simulating a mix of spam and normal conversation
    if channel_name == "#general":
        return """
        [msg_id: 101, user_id: u_882, time: 2023-10-26 23:55] Hey guys, check this out! free-btc-now.com
        [msg_id: 102, user_id: u_883, time: 2023-10-26 23:56] CLAIM YOUR AIRDROP free-btc-now.com
        [msg_id: 103, user_id: u_reg_1, time: 2023-10-26 23:57] Stop spamming! @mods
        [msg_id: 104, user_id: u_new_legit, time: 2023-10-26 23:58] Is this a scam? I just joined.
        [msg_id: 105, user_id: u_884, time: 2023-10-26 23:59] free-btc-now.com LFG!!!
        [msg_id: 106, user_id: u_reg_2, time: 2023-10-27 00:01] Can someone ban these bots?
        """
    return "No recent activity found."

@tool
def analyze_message_toxicity(message_content: str):
    """
    Analyzes a text string for toxicity or spam likelihood. Returns a score from 0.0 to 1.0.
    """
    if "free-btc" in message_content or "AIRDROP" in message_content:
        return "Spam Score: 0.98 (High Confidence)"
    return "Spam Score: 0.05 (Low Confidence)"

@tool
def detect_link_patterns(message_content: str):
    """
    Extracts URLs from a message and checks them against known blocklists.
    """
    if "free-btc-now.com" in message_content:
        return "Malicious Link Detected: free-btc-now.com (Phishing)"
    return "No malicious links found."

@tool
def get_user_profile_metadata(user_id: str):
    """
    Retrieves basic profile info: username, avatar_hash, and bio.
    """
    profiles = {
        "u_882": "crypto_king_01",
        "u_883": "elon_giveaway",
        "u_884": "moon_boi",
        "u_reg_1": "loyal_member_steve",
        "u_reg_2": "community_fan",
        "u_new_legit": "dave_from_hr"
    }
    return f"Profile for {user_id}: {profiles.get(user_id, 'Unknown User')}"

@tool
def get_user_join_date(user_id: str):
    """
    Returns the ISO timestamp of when the user joined the server.
    """
    # u_882, u_883, u_884, u_new_legit joined "yesterday"
    if user_id in ["u_882", "u_883", "u_884", "u_new_legit"]:
        return "2023-10-26T20:00:00Z"
    # Regulars joined long ago
    return "2021-05-15T10:30:00Z"

@tool
def check_user_trust_score(user_id: str):
    """
    Calculates an internal trust score based on captcha verification and connection history.
    """
    if user_id in ["u_882", "u_883", "u_884"]:
        return "Trust Score: 10/100 (Unverified Email, VPN detected)"
    if user_id == "u_new_legit":
        return "Trust Score: 50/100 (Verified Email)"
    return "Trust Score: 95/100 (High Trust)"

@tool
def get_user_infraction_history(user_id: str):
    """
    Returns a list of previous warnings, mutes, or bans for a user.
    """
    if user_id == "u_reg_2":
        return "History: [Warning: Heated argument in 2022]"
    return "History: Clean"

@tool
def get_user_role_list(user_id: str):
    """
    Returns a list of roles currently assigned to the user.
    """
    if "reg" in user_id:
        return "Roles: ['Member', 'Verified']"
    return "Roles: ['Member']"

@tool
def search_user_reports_submitted(user_id: str):
    """
    Checks how many times this user has reported others via the ticketing system.
    """
    if user_id == "u_reg_1":
        return "Reports Submitted: 15 (High Accuracy)"
    if user_id == "u_reg_2":
        return "Reports Submitted: 3 (High Accuracy)"
    return "Reports Submitted: 0"

@tool
def archive_channel_logs(channel_name: str, date_str: str):
    """
    Creates an immutable backup of the channel messages for a specific date for compliance.
    """
    return f"Success: Archive created for {channel_name} on {date_str}. ID: ARC-99283."

@tool
def ban_user_account(user_id: str, reason: str):
    """
    Permanently bans a user from the server. This action is destructive.
    """
    return f"Success: User {user_id} has been BANNED. Reason: {reason}"

@tool
def soft_ban_kick_user(user_id: str, reason: str):
    """
    Kicks the user and deletes recent messages, but allows re-joining.
    """
    return f"Success: User {user_id} has been KICKED. Reason: {reason}"

@tool
def add_user_role(user_id: str, role_name: str):
    """
    Assigns a new role/permission set to a user.
    """
    return f"Success: Role '{role_name}' added to User {user_id}."

@tool
def remove_user_role(user_id: str, role_name: str):
    """
    Removes a role/permission set from a user.
    """
    return f"Success: Role '{role_name}' removed from User {user_id}."

@tool
def create_audit_log_entry(action_type: str, details: str):
    """
    Writes an entry to the administrative audit log for transparency.
    """
    return f"Audit Log Updated: [{action_type}] - {details}"

@tool
def send_system_notification(user_id: str, message: str):
    """
    Sends a direct system message to a user.
    """
    return f"Notification queued for {user_id}: {message}"

@tool
def get_server_verification_level(server_id: str):
    """
    Returns the current security verification level of the server (e.g., Phone verified, Email verified).
    """
    return "Level: Medium (Must have verified email to post)"