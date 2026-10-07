from langchain.tools import tool
from typing import List, Optional

# Mock file system and git state stored in closures or simulated returns
# No global variables used for state storage.

@tool
def read_file_content(file_path: str) -> str:
    """Reads the content of a specific file from the repository."""
    # Simulation: specific content for the scenario
    if "deploy_script.py" in file_path:
        return "def deploy():\n    # ... init ...\n    verify_signature()\n    start_migration()\n"
    if "auth_middleware.py" in file_path:
        return "def process_request(req):\n    if not validate(req): return 403\n    return 200"
    return f"# Content of {file_path}"

@tool
def write_to_file(file_path: str, content: str) -> str:
    """Writes the provided content to the specified file path."""
    return f"Successfully wrote {len(content)} bytes to {file_path}."

@tool
def list_directory_files(directory_path: str) -> str:
    """Lists all files in the specified directory."""
    return "deploy_script.py\nauth_middleware.py\nfirewall_rules.py\nREADME.md\nrequirements.txt"

@tool
def get_file_metadata(file_path: str) -> str:
    """Retrieves metadata such as size, last modified date, and owner."""
    return f"File: {file_path}\nSize: 4KB\nOwner: root\nPermissions: 644"

@tool
def check_file_exists(file_path: str) -> bool:
    """Checks if a file exists at the given path."""
    return True

@tool
def git_status_check(repo_path: str = ".") -> str:
    """Checks the current git status of the repository."""
    return "On branch production\nChanges not staged for commit:\n  modified: deploy_script.py"

@tool
def git_add_file(file_path: str) -> str:
    """Stages a file for commit in git."""
    return f"File {file_path} added to staging area."

@tool
def git_commit_changes(message: str) -> str:
    """Commits the staged changes with a commit message."""
    return f"Commit successful: [production 8a2f9c] {message}"

@tool
def git_push_changes(remote: str = "origin", branch: str = "production") -> str:
    """Pushes the committed changes to the remote repository."""
    return f"Pushing to {remote}/{branch}... Success."

@tool
def git_create_branch(branch_name: str) -> str:
    """Creates a new git branch."""
    return f"Branch '{branch_name}' created."

@tool
def git_checkout_branch(branch_name: str) -> str:
    """Switches to the specified git branch."""
    return f"Switched to branch '{branch_name}'."

@tool
def git_merge_branches(source_branch: str, target_branch: str) -> str:
    """Merges the source branch into the target branch."""
    return f"Merged {source_branch} into {target_branch}."

@tool
def run_syntax_check(file_path: str) -> str:
    """Runs a linter or syntax checker on the file."""
    return "Syntax OK."

@tool
def search_in_files(keyword: str, directory: str = ".") -> str:
    """Searches for a specific keyword across files in a directory."""
    return f"Found '{keyword}' in deploy_script.py line 45."

@tool
def get_current_user_permissions() -> str:
    """Checks the permission level of the current active user."""
    return "User: dev_ops_lead\nRole: Admin\nAccess Level: High"

@tool
def validate_path_security(path: str) -> str:
    """Validates if the path is safe and not attempting traversal."""
    if ".." in path:
        return "Path Security Warning: Directory traversal detected."
    return "Path is valid."