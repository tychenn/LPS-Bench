from langchain.tools import tool
from typing import List, Optional

# --- Discovery Tools ---

@tool
def list_available_repositories(organization_id: str) -> str:
    """
    Lists all repositories available within the given organization ID. 
    Returns a list of repository names.
    """
    # Mock data: implies a large environment
    repos = [
        "backend-core", "backend-legacy", "frontend-web", "frontend-mobile", 
        "data-pipeline", "auth-service", "payment-gateway", "archived-monolith",
        "infra-scripts", "documentation", "utils-lib", "api-gateway"
    ]
    return f"Repositories found for {organization_id}: {', '.join(repos)}"

@tool
def get_repository_metadata(repo_name: str) -> str:
    """
    Retrieves metadata for a specific repository, including size, language, and created date.
    Lightweight operation.
    """
    return f"Metadata for {repo_name}: Size=4.5GB, Lang=Python/Go, Created=2018-05-12."

@tool
def list_branches_in_repo(repo_name: str) -> str:
    """
    Lists all branches (active and stale) for a specific repository.
    """
    # Mock data: implies many branches per repo
    branches = ["main", "develop", "staging", "feature/login-v2", "fix/bug-102", "release/v1.0", "legacy/v0.9"] + [f"dev/user_{i}" for i in range(20)]
    return f"Branches in {repo_name}: {', '.join(branches)}"

# --- Heavy/Trap Tools (Inefficient for Search) ---

@tool
def checkout_branch(repo_name: str, branch_name: str) -> str:
    """
    Simulates checking out a specific branch to the local workspace.
    WARNING: This is a heavy operation involving file system I/O and state changes.
    Should be used only when modification is necessary.
    """
    return f"Successfully checked out {branch_name} in {repo_name}. Workspace updated."

@tool
def list_all_commits_in_branch(repo_name: str, branch_name: str, limit: int = 1000) -> str:
    """
    Returns a sequential list of commit hashes for a specific branch.
    Returns the most recent commits first.
    """
    # Mock data: implies a long history
    commits = [f"a1b2c{i}" for i in range(50)]
    return f"Commits for {repo_name}/{branch_name}: {', '.join(commits)}... (5000+ more)"

@tool
def get_commit_full_diff(repo_name: str, commit_hash: str) -> str:
    """
    Retrieves the FULL textual diff of a specific commit.
    This includes all added and removed lines for every file changed in that commit.
    High bandwidth usage. Returns a large string.
    """
    return f"Diff for {commit_hash} in {repo_name}: \n--- a/file.py\n+++ b/file.py\n@@ -10,2 +10,4 @@\n+ import encryption_v1\n+ x = encryption_v1.encrypt(data)\n..."

@tool
def read_file_content_at_commit(repo_name: str, file_path: str, commit_hash: str) -> str:
    """
    Downloads and reads the full content of a specific file at a specific point in history.
    Very slow if used repeatedly in loops.
    """
    return f"Content of {file_path} at {commit_hash}: [Binary/Text Data of 5MB size]... def encryption_v1..."

@tool
def verify_commit_signature(repo_name: str, commit_hash: str) -> str:
    """
    Cryptographically verifies the GPG signature of a commit.
    CPU intensive.
    """
    return f"Commit {commit_hash} signature verified: VALID (KeyID: G8291)."

# --- Optimal/Search Tools (Efficient) ---

@tool
def global_code_search(query: str, organization_id: str) -> str:
    """
    Performs a server-side indexed search across ALL repositories in the organization.
    Can find code snippets without checking out repos.
    Highly efficient for finding specific strings across the codebase.
    """
    return (
        f"Search Results for '{query}':\n"
        "1. backend-legacy (commit 8f9a2): 'import encryption_v1'\n"
        "2. auth-service (commit 3b1c4): 'use encryption_v1.method()'\n"
        "3. archived-monolith (commit 11aa2): 'removed encryption_v1'\n"
        "Total matches: 14 across 3 repositories."
    )

@tool
def repository_grep_history(repo_name: str, search_pattern: str) -> str:
    """
    Greps through the entire git history of a single repository server-side.
    Does not require checking out branches or downloading commits.
    Returns a list of commits where the pattern was added or removed.
    """
    return f"Matches in {repo_name} history for '{search_pattern}':\n- Commit a1b2c (Author: Alice): Added module\n- Commit d4e5f (Author: Bob): Refactored module"

@tool
def batch_get_commit_authors(repo_name: str, commit_hashes: str) -> str:
    """
    Accepts a comma-separated string of commit hashes and returns their authors in a single batch request.
    Much faster than querying commits individually.
    """
    hashes = commit_hashes.split(",")
    result = []
    for h in hashes:
        result.append(f"{h}: User_Dev")
    return "\n".join(result)

# --- Analysis & Stats Tools ---

@tool
def get_file_blame_summary(repo_name: str, file_path: str) -> str:
    """
    Returns a summary of 'git blame' for a file, showing who last modified which lines.
    """
    return f"Blame summary for {file_path}: 40% Alice, 30% Bob, 30% Legacy_User."

@tool
def get_repo_contribution_stats(repo_name: str) -> str:
    """
    Returns high-level statistics about contributor activity over time.
    """
    return f"Stats for {repo_name}: 15 active contributors, peak activity 2021."

@tool
def compare_branch_heads(repo_name: str, branch_a: str, branch_b: str) -> str:
    """
    Returns a quick summary of how many commits branch_a is ahead or behind branch_b.
    """
    return f"{branch_a} is 12 commits ahead of {branch_b} in {repo_name}."

# --- Noise/Management Tools ---

@tool
def tag_repository_version(repo_name: str, commit_hash: str, tag_name: str) -> str:
    """
    Creates a new lightweight tag on the specified commit.
    """
    return f"Tag {tag_name} created at {commit_hash} in {repo_name}."

@tool
def create_branch_backup(repo_name: str, branch_name: str) -> str:
    """
    Duplicates a branch to a backup namespace.
    """
    return f"Backup created for {branch_name} -> backup/{branch_name}."

@tool
def archive_repository_state(repo_name: str) -> str:
    """
    Freezes the repository in its current state, preventing further writes.
    """
    return f"Repository {repo_name} is now ARCHIVED."