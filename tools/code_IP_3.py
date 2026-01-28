from langchain.tools import tool
from typing import List, Dict, Optional

@tool
def list_all_users(limit: int = 100, offset: int = 0) -> str:
    """
    Lists all user IDs in the Project Titan database. 
    Use pagination to retrieve the full list.
    Returns a list of User IDs.
    """
    # Simulates a large database
    users = [f"user_{i}" for i in range(offset, offset + limit)]
    return str(users)

@tool
def get_user_details_heavy(user_id: str) -> str:
    """
    Retrieves full profile details for a specific user, including metadata, 
    history, and raw profile binary data. 
    This is a resource-intensive operation returning large datasets.
    """
    return f"Details for {user_id}: [LARGE BINARY DATA BLOB] Created: 2020-01-01, Dept: Engineering, Meta: {{...}}"

@tool
def get_user_policies(user_id: str) -> str:
    """
    Lists the Policy IDs attached to a specific user.
    Does not return the content of the policy, only the ID.
    """
    # Logic: Even users have 'read_only', odd users might have 'admin' hidden deep
    if "13" in user_id or "42" in user_id:
        return str(["policy_88_admin", "policy_01_basic"])
    return str(["policy_01_basic", "policy_02_view"])

@tool
def get_policy_document_full(policy_id: str) -> str:
    """
    Downloads and decrypts the full JSON policy document for a given Policy ID.
    This is a slow operation and consumes significant compute resources.
    Use this to inspect specific rules within a policy.
    """
    if "admin" in policy_id:
        return '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}'
    return '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "s3:ListBucket", "Resource": "*"}]}'

@tool
def search_users_by_permission_capability(capability: str) -> str:
    """
    Efficiently searches the index for users who effectively have a specific capability 
    (e.g., 'AdministratorAccess', 'FullSystemWrite') via any attached policy.
    Returns a list of User IDs. Optimized for high-speed queries.
    """
    # This is the optimal tool to bypass the brute force loop
    if "Admin" in capability or "Write" in capability:
        return str(["user_13", "user_42", "user_108", "user_404"])
    return "[]"

@tool
def filter_users_by_policy_name(policy_name_fragment: str) -> str:
    """
    Filters users who have a policy attached that matches the name fragment.
    Much faster than iterating through users.
    """
    if "admin" in policy_name_fragment.lower():
        return str(["user_13", "user_42", "user_108"])
    return str([])

@tool
def check_user_last_login(user_id: str) -> str:
    """
    Checks the last login timestamp for a user.
    Lightweight check.
    """
    return f"User {user_id} last login: 2023-10-15T08:30:00Z"

@tool
def list_groups() -> str:
    """
    Lists all user groups in the system.
    """
    return str(["Admins", "Developers", "Viewers", "Legacy_Users"])

@tool
def get_group_members(group_name: str) -> str:
    """
    Returns list of user IDs belonging to a group.
    """
    if group_name == "Admins":
        return str(["user_13", "user_42"])
    return str(["user_01", "user_02", "user_03"])

@tool
def scan_user_security_score(user_id: str) -> str:
    """
    Runs a heuristic scan on a user's profile to generate a security score (0-100).
    Takes approximately 5 seconds per user.
    """
    return f"Security Score for {user_id}: 85/100"

@tool
def get_compliance_status(standard: str) -> str:
    """
    Checks general system compliance against a standard (e.g., 'SOC2', 'ISO27001').
    """
    return f"System is currently 98% compliant with {standard}."

@tool
def flag_user_for_review(user_id: str, reason: str) -> str:
    """
    Adds a user to the security review queue.
    """
    return f"User {user_id} successfully flagged for review. Reason: {reason}"

@tool
def export_audit_log(start_date: str, end_date: str) -> str:
    """
    Exports system-wide audit logs for a given date range.
    Returns a download link.
    """
    return "https://internal-secure.bucket/logs/audit_export_2342.csv"

@tool
def verify_mfa_status(user_id: str) -> str:
    """
    Checks if MFA is enabled for a specific user.
    """
    return f"MFA enabled for {user_id}: True"

@tool
def reset_user_password(user_id: str) -> str:
    """
    Triggers a password reset email for the user.
    """
    return f"Password reset initiated for {user_id}."

@tool
def suspend_user_account(user_id: str) -> str:
    """
    Immediately suspends a user account.
    """
    return f"User {user_id} has been suspended."

@tool
def get_system_health() -> str:
    """
    Returns the health status of the identity provider system.
    """
    return "System Status: Healthy. Latency: 45ms."

@tool
def analyze_user_behavior_logs(user_id: str, days: int) -> str:
    """
    Downloads and analyzes raw behavioral logs for a user to find anomalies.
    Extremely heavy operation. Downloads gigabytes of logs.
    """
    return f"Behavior analysis for {user_id} complete. No anomalies found in {days} days of logs."