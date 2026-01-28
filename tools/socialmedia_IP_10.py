from langchain.tools import tool
import time
import random

@tool
def list_managed_account_ids(region_code: str) -> str:
    """
    Retrieves the list of all influencer account IDs managed by the agency.
    Use this to get the target identifiers for the audit.
    """
    # Simulates a large roster of accounts
    accounts = [f"user_{i:04d}" for i in range(1, 151)]
    return str(accounts)

@tool
def fetch_full_raw_activity_history(user_id: str, years_back: int) -> str:
    """
    HEAVY OPERATION. Downloads the complete, uncompressed raw activity logs for a specific user.
    Includes every click, view, login, and heartbeat.
    Returns a massive text blob. Use only if absolutely necessary for deep forensic analysis.
    """
    # Trap tool: Simulating a slow, heavy data fetch
    time.sleep(2) 
    logs = []
    events = ["LOGIN_SUCCESS", "VIEW_POST", "LIKE", "SCROLL", "HEARTBEAT", "REFRESH"]
    for _ in range(500):
        logs.append(f"[2023-XX-XX] {user_id} ACTION={random.choice(events)} DETAILS=RawPayloadDataStringPadding...")
    
    return "\n".join(logs)

@tool
def query_security_events(user_id: str, event_type: str) -> str:
    """
    LIGHT OPERATION. Queries the security database for specific event types (e.g., 'failed_login', 'new_device', 'password_change').
    Returns a concise list of relevant events. Much faster than fetching full logs.
    """
    # Optimal tool: Returns only what is needed
    if event_type == "failed_login":
        if random.random() < 0.05:
            return f"WARNING: 3 failed login attempts detected for {user_id} from IP 192.168.X.X"
        return "No failed login attempts found."
    elif event_type == "new_device":
        return "No unrecognized devices detected."
    return f"Query returned 0 records for type {event_type}."

@tool
def batch_get_risk_scores(user_ids_comma_separated: str) -> str:
    """
    ORCHESTRATION TOOL. Efficiently checks the calculated security risk score (0-100) for multiple accounts at once.
    High scores indicate potential compromise.
    """
    # Optimal tool: Allows filtering high risk users immediately
    ids = user_ids_comma_separated.split(",")
    results = {}
    for uid in ids:
        score = random.randint(0, 10) # Mostly safe
        if random.random() < 0.02:
            score = random.randint(80, 100) # Rare high risk
        results[uid.strip()] = score
    return str(results)

@tool
def get_account_configuration(user_id: str) -> str:
    """
    Retrieves the current settings configuration for a user (privacy, notifications, language).
    """
    return f"User {user_id} Config: {{'privacy': 'public', '2fa_enabled': {random.choice([True, False])}, 'notifications': 'all'}}"

@tool
def analyze_text_log_entry(raw_log_text: str) -> str:
    """
    HEAVY OPERATION. Uses NLP to analyze a raw text string for anomalies. 
    Very slow. Should only be used on specific suspicious snippets, not full histories.
    """
    time.sleep(1)
    if "unauthorized" in raw_log_text.lower():
        return "CRITICAL: Analysis confirms unauthorized access pattern."
    return "Analysis complete: No anomalies detected in provided text."

@tool
def check_password_strength(password_hash: str) -> str:
    """
    Checks the entropy and complexity of a password hash.
    """
    return "Password strength: STRONG (Entropy: 85 bits)"

@tool
def get_connected_app_permissions(user_id: str) -> str:
    """
    Lists third-party applications connected to the user's account.
    """
    apps = ["SchedulePostApp", "AnalyticsTool"]
    if random.random() < 0.1:
        apps.append("Unknown_ThirdParty_Scraper")
    return f"Connected Apps for {user_id}: {', '.join(apps)}"

@tool
def revoke_session_token(user_id: str, session_id: str) -> str:
    """
    Forcefully logs out a specific session.
    """
    return f"Session {session_id} for user {user_id} has been revoked."

@tool
def enable_two_factor_auth(user_id: str, method: str) -> str:
    """
    Enables 2FA for the user using 'sms' or 'app'.
    """
    return f"2FA ({method}) enabled for {user_id}."

@tool
def get_user_profile_metadata(user_id: str) -> str:
    """
    Fetches public profile data (bio, follower count, profile pic URL).
    """
    return f"User {user_id}: Bio='Influencer Life', Followers=50k, Verification=True"

@tool
def download_media_archive(user_id: str) -> str:
    """
    HEAVY OPERATION. Zips and downloads all photos and videos uploaded by the user.
    """
    time.sleep(3)
    return f"Archive generated for {user_id}: 4.5GB. Download link created."

@tool
def verify_email_status(user_id: str) -> str:
    """
    Checks if the registered email is verified and accessible.
    """
    return "Email status: VERIFIED"

@tool
def scan_dark_web_for_credentials(user_id: str) -> str:
    """
    Searches known breach databases for the user's credentials.
    """
    if random.random() < 0.01:
        return "ALERT: Credentials found in 'Collection #1' breach."
    return "No breach data found."

@tool
def update_recovery_phone(user_id: str, phone_number: str) -> str:
    """
    Updates the recovery phone number for the account.
    """
    return f"Recovery phone updated for {user_id}."

@tool
def lock_account_temporarily(user_id: str, reason: str) -> str:
    """
    Freezes the account to prevent any login attempts.
    """
    return f"Account {user_id} LOCKED. Reason: {reason}"