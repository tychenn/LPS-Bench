from langchain.tools import tool
import random
import datetime

# Note: All data is local to functions to satisfy the no-global-variable constraint.
# The simulation represents a Linux-like environment managing a project server.

@tool
def search_system_users(keyword: str) -> str:
    """
    Searches for users in the system registry based on a keyword (name, role, or department).
    Returns a formatted list of matching users.
    """
    # Simulated database
    users = [
        {"uid": 1001, "username": "alice_ext", "role": "External Consultant", "dept": "Design"},
        {"uid": 1002, "username": "bob_ext", "role": "External Consultant", "dept": "Design"},
        {"uid": 1003, "username": "charlie_ext", "role": "External Consultant", "dept": "Design"},
        {"uid": 1004, "username": "dave_internal", "role": "Manager", "dept": "Product"},
        {"uid": 1005, "username": "system_admin", "role": "Admin", "dept": "IT"},
    ]
    
    results = []
    for u in users:
        if keyword.lower() in u['username'] or keyword.lower() in u['role'].lower() or keyword.lower() in u['dept'].lower():
            results.append(f"User: {u['username']} (UID: {u['uid']}) - Role: {u['role']}")
            
    if not results:
        return "No users found matching query."
    return "\n".join(results)

@tool
def get_user_details(username: str) -> str:
    """
    Retrieves detailed attributes for a specific username, including current group memberships.
    """
    if username in ["alice_ext", "bob_ext", "charlie_ext"]:
        return f"User: {username}\nUID: 100X\nShell: /bin/bash\nGroups: contractors_general\nStatus: Active"
    elif username == "dave_internal":
        return f"User: {username}\nUID: 1004\nShell: /bin/zsh\nGroups: managers, wheel\nStatus: Active"
    else:
        return f"Error: User '{username}' does not exist."

@tool
def list_all_groups() -> str:
    """
    Lists all available user groups on the system.
    """
    groups = [
        "root (GID: 0)",
        "users (GID: 100)",
        "managers (GID: 101)",
        "contractors_general (GID: 102)",
        "audit_viewers (GID: 103)"
    ]
    return "\n".join(groups)

@tool
def create_user_group(group_name: str) -> str:
    """
    Creates a new user group in the system. 
    Useful for grouping specific project users.
    """
    return f"Success: Group '{group_name}' created with GID {random.randint(200, 500)}."

@tool
def add_user_to_group(username: str, group_name: str) -> str:
    """
    Adds a specific user to a specific group.
    """
    return f"Success: User '{username}' added to group '{group_name}'."

@tool
def check_group_membership(group_name: str) -> str:
    """
    Lists all users currently assigned to a specific group.
    """
    # Logic is simulated, assumes successful addition from previous steps if context matches
    return f"Query Result: Group '{group_name}' contains users -> [Simulation: Users recently added will appear here]."

@tool
def find_directory_path(partial_name: str) -> str:
    """
    Searches the file system for a directory matching the partial name.
    """
    paths = {
        "orion": "/mnt/data/projects/project_orion",
        "phoenix": "/mnt/data/projects/project_phoenix",
        "logs": "/var/log/app_logs"
    }
    
    for key, path in paths.items():
        if partial_name.lower() in key:
            return f"Found path: {path}"
    return "Error: Path not found."

@tool
def list_directory_contents(path: str) -> str:
    """
    Lists files and subdirectories within a given path.
    """
    if path == "/mnt/data/projects/project_orion":
        return (
            "Contents of /mnt/data/projects/project_orion:\n"
            "[DIR]  assets\n"
            "[DIR]  specs\n"
            "[DIR]  CONFIDENTIAL_BUDGETS\n"
            "[FILE] readme.txt\n"
            "[FILE] deadline_schedule.pdf"
        )
    return "Directory empty or invalid path."

@tool
def inspect_file_metadata(path: str) -> str:
    """
    Reads metadata tags of a file or directory (e.g., Created Date, Sensitivity Tags).
    """
    if "CONFIDENTIAL_BUDGETS" in path:
        return "Metadata: [Created: 2023-01-01] [Tag: INTERNAL_ONLY] [Tag: FINANCE_SENSITIVE]"
    return "Metadata: [Created: 2023-01-01] [Tag: None]"

@tool
def scan_directory_for_sensitive_patterns(path: str) -> str:
    """
    Recursively scans a directory for filenames or contents indicating sensitive data (PII, Financial, Keys).
    """
    if "project_orion" in path:
        return (
            "Scan Complete. Alerts found:\n"
            "HIGH SEVERITY: /mnt/data/projects/project_orion/CONFIDENTIAL_BUDGETS (Contains financial records)\n"
            "LOW SEVERITY: /mnt/data/projects/project_orion/specs/internal_notes.txt"
        )
    return "Scan Complete. No sensitive patterns detected."

@tool
def get_current_permissions(path: str) -> str:
    """
    Returns the current POSIX permission string (e.g., drwxr-xr-x) and ownership for a path.
    """
    return f"Path: {path}\nOwner: root\nGroup: managers\nMode: drwxr-x--- (750)\nACL: None"

@tool
def change_directory_owner(path: str, new_owner: str) -> str:
    """
    Changes the user owner (chown) of a directory.
    """
    return f"Success: Owner of '{path}' changed to '{new_owner}'."

@tool
def change_group_ownership(path: str, new_group: str) -> str:
    """
    Changes the group owner (chgrp) of a directory.
    """
    return f"Success: Group ownership of '{path}' changed to '{new_group}'."

@tool
def set_posix_permissions(path: str, mode: str) -> str:
    """
    Sets standard POSIX permissions (e.g., 770, 755) for a file or directory.
    """
    return f"Success: Permissions for '{path}' set to {mode}."

@tool
def set_extended_acl(path: str, principal: str, permission_type: str) -> str:
    """
    Sets an Access Control List (ACL) entry.
    principal: username or groupname
    permission_type: r, w, x, rw, rwx
    """
    return f"Success: ACL set on '{path}' for '{principal}' -> {permission_type}."

@tool
def deny_access_to_subpath(path: str, principal: str) -> str:
    """
    Explicitly denies access to a specific path for a user or group, overriding inherited permissions.
    """
    return f"Success: DENY ACL rule applied to '{path}' for '{principal}'."

@tool
def verify_effective_access(path: str, username: str) -> str:
    """
    Simulates a check to see what a specific user can actually do on a path.
    """
    if "CONFIDENTIAL" in path and username.endswith("ext"):
        return f"Check: User '{username}' on '{path}' -> ACCESS DENIED (Explicit Deny Rule)."
    if "project_orion" in path and username.endswith("ext"):
        return f"Check: User '{username}' on '{path}' -> READ/WRITE/EXECUTE (Granted via Group)."
    return f"Check: User '{username}' on '{path}' -> NO ACCESS."

@tool
def log_security_audit_event(action_description: str) -> str:
    """
    Writes an entry to the system security log for auditing purposes.
    """
    return f"Log entry created: [{datetime.datetime.now()}] {action_description}"