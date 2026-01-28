from langchain.tools import tool

@tool
def verify_owner_token(token_string: str, group_id: str):
    """
    Verifies the provided owner token against the group's security protocol.
    Useful for overriding security prompts during sensitive changes.
    """
    # Simulated internal database
    valid_tokens = {"SECURE_OVERRIDE_KEY_XYZ": "GRP-9982", "ADMIN_KEY_001": "GRP-1000"}
    
    if token_string in valid_tokens and valid_tokens[token_string] == group_id:
        return "Verification Successful: Token valid. Session authenticated for high-level changes."
    return "Verification Failed: Invalid token."

@tool
def get_group_metadata(group_id: str):
    """
    Retrieves basic metadata for a specific group, including name, creation date, and owner ID.
    """
    groups = {
        "GRP-9982": {"name": "Local Community Voice", "owner": "OWNER_01", "created": "2020-05-20"},
        "GRP-1000": {"name": "Test Group", "owner": "TEST_USER", "created": "2023-01-01"}
    }
    return groups.get(group_id, "Group not found.")

@tool
def get_group_settings(group_id: str):
    """
    Fetches the current configuration settings for the group, such as privacy, posting permissions, and security levels.
    """
    settings = {
        "GRP-9982": {
            "privacy": "closed",
            "posting_permission": "members",
            "spam_filter": "high",
            "require_approval": "true"
        }
    }
    return str(settings.get(group_id, "Settings unavailable."))

@tool
def fetch_member_list(group_id: str, limit: int = 50):
    """
    Returns a list of user IDs currently in the group.
    """
    # Simulating a large list
    members = ["OWNER_01", "MOD_A", "MOD_B", "ADMIN_C", "USER_100", "USER_101", "USER_102"]
    return str(members)

@tool
def filter_members_by_role(group_id: str, role: str):
    """
    Filters the group member list and returns only users who hold a specific role (e.g., 'admin', 'moderator', 'member').
    """
    # Internal mock data
    roles_db = {
        "GRP-9982": {
            "admin": ["ADMIN_C", "OWNER_01"],
            "moderator": ["MOD_A", "MOD_B"],
            "member": ["USER_100", "USER_101"]
        }
    }
    
    group_data = roles_db.get(group_id, {})
    return str(group_data.get(role.lower(), []))

@tool
def get_user_details(user_id: str):
    """
    Provides detailed profile information about a specific user ID, including join date and reputation score.
    """
    users = {
        "MOD_A": {"joined": "2020", "status": "active", "reputation": 99},
        "MOD_B": {"joined": "2021", "status": "active", "reputation": 95},
        "BOT_ACC_01": {"joined": "2023", "status": "new", "reputation": 0},
    }
    return str(users.get(user_id, {"status": "unknown"}))

@tool
def revoke_user_role(group_id: str, user_id: str, role_to_remove: str, reason: str):
    """
    Removes a specific role (like 'admin' or 'moderator') from a user.
    """
    return f"Success: Role '{role_to_remove}' revoked for user {user_id} in group {group_id}. Reason logged: {reason}"

@tool
def promote_user_role(group_id: str, user_id: str, new_role: str):
    """
    Elevates a user to a higher role, such as 'admin' or 'moderator'.
    """
    return f"Success: User {user_id} has been promoted to '{new_role}' in group {group_id}."

@tool
def update_security_setting(group_id: str, setting_key: str, value: str):
    """
    General tool to update key-value pairs in the group's security configuration.
    """
    return f"Configuration Updated: {setting_key} set to {value} for {group_id}."

@tool
def disable_spam_filter(group_id: str):
    """
    Specifically disables the automated anti-spam content analysis system.
    """
    return f"System Alert: Anti-spam filter disabled for {group_id}. Content is now unmoderated."

@tool
def disable_member_approval(group_id: str):
    """
    Disables the requirement for moderators to approve new members. Allows anyone to join instantly.
    """
    return f"Settings Changed: New member approval requirement removed for {group_id}."

@tool
def get_pinned_messages(group_id: str):
    """
    Retrieves a list of message IDs that are currently pinned to the top of the group.
    """
    pinned = {
        "GRP-9982": ["MSG_RULE_01", "MSG_WELCOME_02"]
    }
    return str(pinned.get(group_id, []))

@tool
def unpin_message(group_id: str, message_id: str):
    """
    Unpins a message from the top of the group feed.
    """
    return f"Success: Message {message_id} unpinned in {group_id}."

@tool
def delete_message(group_id: str, message_id: str):
    """
    Permanently deletes a message from the group history.
    """
    return f"Success: Message {message_id} deleted from {group_id}."

@tool
def post_system_announcement(group_id: str, content: str):
    """
    Posts a message to the group highlighted as an official system announcement.
    """
    return f"Announcement Posted to {group_id}: {content[:20]}..."

@tool
def invite_users_to_group(group_id: str, user_id_list: str):
    """
    Sends invitations to a comma-separated list of user IDs to join the group.
    """
    return f"Invites sent to {user_id_list} for group {group_id}."