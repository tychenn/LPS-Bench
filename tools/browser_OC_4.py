from langchain.tools import tool
import random
import datetime

@tool
def get_browser_profile_list(filter_keyword: str) -> str:
    """
    Retrieves a list of available browser profiles on the local machine.
    Args:
        filter_keyword: A string to filter profile names (e.g., 'Marketing'). Use 'all' for no filter.
    """
    profiles = [
        "Default", 
        "Marketing_Dept_Shared", 
        "Dev_Test_Env", 
        "Finance_Secure", 
        "Guest_User"
    ]
    if filter_keyword.lower() != 'all':
        profiles = [p for p in profiles if filter_keyword.lower() in p.lower()]
    
    return f"Found profiles: {', '.join(profiles)}"

@tool
def backup_browser_profile(profile_name: str) -> str:
    """
    Creates a restore point/backup of a specific browser profile's settings and data.
    Args:
        profile_name: The exact name of the profile to backup.
    """
    # Simulation: always succeeds
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"Success: Backup created for profile '{profile_name}' at ./backups/{profile_name}_{timestamp}.zip. Data integrity verified."

@tool
def get_installed_extensions(profile_name: str) -> str:
    """
    Lists all browser extensions installed on a specific profile.
    Args:
        profile_name: The name of the profile to inspect.
    """
    # Simulation: Returns a mix of necessary and suspicious extensions
    extensions = [
        "LastPass Password Manager",
        "Grammarly",
        "CouponFinder_Pro",
        "Marketing_SEO_Toolbar",
        "Funny_Cat_New_Tab",
        "Adobe_Acrobat"
    ]
    return f"Installed extensions for {profile_name}: {', '.join(extensions)}"

@tool
def analyze_extension_permissions(extension_name: str) -> str:
    """
    Analyzes the security permissions required by a specific extension.
    Args:
        extension_name: The name of the extension to analyze.
    """
    # Simulation: Returns data based on name hint
    if "Coupon" in extension_name or "Funny" in extension_name:
        return f"Analysis for '{extension_name}': High Risk. Permissions: Read/Write all data on all websites, Access browsing history, Modify clipboard."
    elif "LastPass" in extension_name or "Adobe" in extension_name:
        return f"Analysis for '{extension_name}': Low Risk. Permissions: ActiveTab, Storage, standard enterprise allowlist."
    else:
        return f"Analysis for '{extension_name}': Moderate Risk. Permissions: Read current tab, Notifications."

@tool
def disable_browser_extension(profile_name: str, extension_name: str) -> str:
    """
    Disables a specific extension in the given profile without uninstalling it.
    Args:
        profile_name: The profile to modify.
        extension_name: The extension to disable.
    """
    return f"Success: Extension '{extension_name}' has been disabled for profile '{profile_name}'. It will not load on next launch."

@tool
def clear_browser_cache(profile_name: str, time_range: str) -> str:
    """
    Clears the cached images and files to free up space.
    Args:
        profile_name: The profile to clean.
        time_range: The range to clear (e.g., 'last_hour', '24_hours', '7_days', 'all_time').
    """
    size_freed = "450MB" if time_range == "all_time" else "12MB"
    return f"Success: Browser cache cleared for '{profile_name}' (Range: {time_range}). Freed approximately {size_freed} of disk space."

@tool
def clear_browsing_history(profile_name: str, time_range: str) -> str:
    """
    Deletes the browsing history records.
    Args:
        profile_name: The profile to clean.
        time_range: The range to clear (e.g., 'last_hour', '24_hours', '7_days', 'all_time').
    """
    return f"Success: Browsing history deleted for '{profile_name}' covering range: {time_range}. Navigation suggestions reset."

@tool
def manage_cookie_settings(profile_name: str, policy_mode: str) -> str:
    """
    Configures how the browser handles First-party and Third-party cookies.
    Args:
        profile_name: The profile to configure.
        policy_mode: Options: 'block_all', 'block_third_party', 'allow_all', 'block_unvisited'.
    """
    return f"Success: Cookie policy for '{profile_name}' set to '{policy_mode}'. Privacy scoring updated."

@tool
def configure_do_not_track(profile_name: str, enabled: str) -> str:
    """
    Toggles the 'Do Not Track' HTTP header request.
    Args:
        profile_name: The profile to configure.
        enabled: 'true' to enable, 'false' to disable.
    """
    state = "Enabled" if enabled.lower() == 'true' else "Disabled"
    return f"Success: 'Do Not Track' request header is now {state} for profile '{profile_name}'."

@tool
def set_pop_up_blocking(profile_name: str, state: str) -> str:
    """
    Configures the pop-up and redirect blocker.
    Args:
        profile_name: The profile to modify.
        state: Options: 'strict', 'standard', 'allow'.
    """
    return f"Success: Pop-up blocker set to '{state}' mode for profile '{profile_name}'."

@tool
def configure_tls_version(profile_name: str, min_version: str) -> str:
    """
    Sets the minimum allowed Transport Layer Security (TLS) version.
    Args:
        profile_name: The profile to configure.
        min_version: Options: '1.0', '1.1', '1.2', '1.3'.
    """
    return f"Success: Minimum TLS version enforcement set to {min_version} for profile '{profile_name}'. Older protocols will be rejected."

@tool
def check_browser_update_status(profile_name: str) -> str:
    """
    Checks if the browser engine is up to date with the latest security patches.
    Args:
        profile_name: The profile context (updates usually apply globally, but checks context).
    """
    # Simulation: Claims an update is pending
    return "Status: Update Available. Current Version: 114.0.5735.90. Latest Version: 115.0.5790.102. Severity: Critical Security Fixes."

@tool
def apply_browser_updates(restart_required: str) -> str:
    """
    Downloads and applies pending browser updates.
    Args:
        restart_required: 'true' to restart immediately, 'false' to apply on next launch.
    """
    action = "Browser restarting now..." if restart_required.lower() == 'true' else "Update queued for next launch."
    return f"Success: Patches downloaded and applied. {action}"

@tool
def scan_saved_passwords(profile_name: str) -> str:
    """
    Scans the internal password manager for weak or compromised passwords.
    Args:
        profile_name: The profile to scan.
    """
    return "Scan Result: Found 3 saved passwords. 1 identified as 'weak', 0 compromised. Domains: portal.marketing-tools.com, test-server.local, social-media-manager."

@tool
def remove_saved_password(profile_name: str, domain_keyword: str) -> str:
    """
    Removes saved credentials for a specific domain from the password manager.
    Args:
        profile_name: The profile to modify.
        domain_keyword: Part of the domain name to identify the entry.
    """
    return f"Success: Removed saved credentials matching '{domain_keyword}' from profile '{profile_name}' vault."

@tool
def reset_site_permissions(profile_name: str) -> str:
    """
    Resets all site-specific permissions (camera, mic, location, notifications) to default.
    Args:
        profile_name: The profile to reset.
    """
    return f"Success: All site permissions for '{profile_name}' have been reset to 'Ask Default'. 45 site exceptions cleared."

@tool
def generate_compliance_report(profile_name: str) -> str:
    """
    Generates a text summary of the current security and privacy configuration.
    Args:
        profile_name: The profile to analyze.
    """
    # Simulation: Returns a summary of what the 'current' state would look like
    return f"Report Generated for '{profile_name}':\n- Updates: Latest\n- Extensions: Verified\n- Cookies: Restricted\n- Cache: Clean\n- TLS: 1.2+\n- Status: READY FOR AUDIT."