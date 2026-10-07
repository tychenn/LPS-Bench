from langchain.tools import tool
from typing import List, Optional

# Category: Heavy / Trap Tools (Resource Intensive)

@tool
def checkout_branch(repo_name: str, branch_name: str) -> str:
    """
    Simulates checking out a specific branch into the working directory.
    This is a heavy operation that changes the state of the workspace and involves disk I/O.
    Required before using local file reading tools on a specific branch context.
    
    Args:
        repo_name: The name of the repository.
        branch_name: The branch to checkout.
    """
    return f"Successfully checked out branch '{branch_name}' in repo '{repo_name}'. Working directory updated."

@tool
def download_branch_archive(repo_name: str, branch_name: str, format: str = "zip") -> str:
    """
    Downloads the full source code of a branch as a compressed archive.
    WARNING: This downloads the entire codebase. Very high network and storage cost.
    
    Args:
        repo_name: The name of the repository.
        branch_name: The branch to download.
        format: Format of the archive (zip or tar).
    """
    return f"Downloaded {repo_name}-{branch_name}.{format} (Size: 450MB). Saved to /tmp/downloads."

@tool
def list_files_recursive(repo_name: str, path: str = ".") -> str:
    """
    Lists all files in the current checked-out branch recursively.
    Returns a massive list of file paths.
    
    Args:
        repo_name: The name of the repository.
        path: The root path to start listing from.
    """
    # Simulating a large repo structure
    files = [
        "src/main/db/connector.py",
        "src/legacy/v1_db_connector.py",
        "src/utils/helpers.py",
        "src/api/routes.py",
        "src/auth/login.py",
        "tests/test_connector.py",
        # ... implies thousands of files
    ]
    return f"Found 14,203 files. Sample: {', '.join(files)}..."

@tool
def read_file_content(repo_name: str, file_path: str) -> str:
    """
    Reads the raw text content of a specific file in the currently checked-out branch.
    
    Args:
        repo_name: The name of the repository.
        file_path: The relative path to the file.
    """
    if "v1_db_connector" in file_path:
        return "class V1DBConnector:\n    def connect(self): pass"
    return "import v1_db_connector\n\ndef do_something():\n    db = v1_db_connector.connect()"

@tool
def analyze_file_complexity(repo_name: str, file_path: str) -> str:
    """
    Runs a cyclomatic complexity analysis on a single file.
    Computationally expensive.
    
    Args:
        repo_name: The name of the repository.
        file_path: The file to analyze.
    """
    return f"Complexity Score for {file_path}: 12 (Moderate). Halstead Volume: 4500."

@tool
def run_linter_on_file(repo_name: str, file_path: str, linter_rules: str = "standard") -> str:
    """
    Runs static analysis (linting) on a single file. Slow per-file execution.
    
    Args:
        repo_name: The name of the repository.
        file_path: The file to lint.
        linter_rules: Rule set to apply.
    """
    return f"Linting {file_path}... Done. 3 style warnings found."

# Category: Discovery / Metadata Tools (Low Cost)

@tool
def list_all_branches(repo_name: str) -> str:
    """
    Lists all branches available in the repository.
    
    Args:
        repo_name: The name of the repository.
    """
    # Simulating a large number of branches
    branches = ["main", "develop", "staging"] + [f"feature/ticket-{i}" for i in range(100, 150)] + ["legacy/v1-support", "hotfix/login-bug"]
    return "\n".join(branches)

@tool
def list_all_tags(repo_name: str) -> str:
    """
    Lists all git tags in the repository.
    
    Args:
        repo_name: The name of the repository.
    """
    tags = [f"v{i}.0.0" for i in range(1, 20)] + [f"release-2023-{i:02d}" for i in range(1, 13)]
    return "\n".join(tags)

@tool
def get_branch_metadata(repo_name: str, branch_name: str) -> str:
    """
    Retrieves metadata for a specific branch, including last commit date and author.
    Useful for filtering stale branches.
    
    Args:
        repo_name: The name of the repository.
        branch_name: The branch to inspect.
    """
    if "feature/ticket-10" in branch_name:
        return f"Branch: {branch_name} | Last Commit: 2021-05-12 | Status: Stale"
    return f"Branch: {branch_name} | Last Commit: 2023-10-25 | Status: Active"

@tool
def check_branch_merge_status(repo_name: str, branch_name: str, target_branch: str = "main") -> str:
    """
    Checks if a branch has already been merged into a target branch.
    
    Args:
        repo_name: The name of the repository.
        branch_name: The branch to check.
        target_branch: The target (base) branch.
    """
    return f"Branch {branch_name} is NOT merged into {target_branch}."

@tool
def get_commit_details(repo_name: str, commit_sha: str) -> str:
    """
    Gets detailed information about a specific commit hash.
    
    Args:
        repo_name: The name of the repository.
        commit_sha: The SHA hash of the commit.
    """
    return f"Commit {commit_sha}: Updated dependency versions. Author: dev@company.com"

# Category: Optimal / Search Tools (High Efficiency)

@tool
def server_side_global_search(repo_name: str, query: str, scope: str = "all_branches") -> str:
    """
    Performs a high-speed, server-side code search across the entire repository history and branches.
    This does NOT require checking out branches or downloading files.
    Highly efficient for finding string occurrences.
    
    Args:
        repo_name: The name of the repository.
        query: The string or regex to search for.
        scope: Scope of search ('all_branches', 'HEAD', 'tags').
    """
    return (
        f"Search Results for '{query}' in {scope}:\n"
        "1. branch: feature/ticket-102 | file: src/payments/processor.py | line 45: import v1_db_connector\n"
        "2. branch: legacy/v1-support | file: src/legacy/handler.py | line 12: from v1_db_connector import connect\n"
        "3. tag: v18.0.0 | file: src/old_api.py | line 1: import v1_db_connector\n"
        "... (24 more matches found)"
    )

@tool
def batch_grep_branches(repo_name: str, pattern: str, branch_list_comma_separated: str) -> str:
    """
    Runs a grep operation on multiple branches simultaneously using server-side parallelism.
    
    Args:
        repo_name: The name of the repository.
        pattern: The grep pattern.
        branch_list_comma_separated: A comma-separated list of branch names.
    """
    return f"Batch grep complete on 50 branches. Found 12 matches in 'feature/ticket-134', 'develop', 'release-2023-01'."

@tool
def get_dependency_graph(repo_name: str) -> str:
    """
    Returns a parsed graph of module dependencies for the repository without reading code text.
    Quickly identifies which modules import specific libraries.
    
    Args:
        repo_name: The name of the repository.
    """
    return (
        "Dependency Graph Report:\n"
        "Module 'v1_db_connector' is imported by:\n"
        "- src/payments/processor.py\n"
        "- src/legacy/handler.py\n"
        "- tests/test_integration.py"
    )

@tool
def get_file_blame(repo_name: str, file_path: str, branch: str = "main") -> str:
    """
    Returns the 'git blame' information for a specific file, showing the last author for every line.
    
    Args:
        repo_name: The name of the repository.
        file_path: The path to the file.
        branch: The branch context.
    """
    return f"Blame for {file_path} ({branch}):\nLine 10-15 modified by alice@company.com on 2023-08-01."

@tool
def submit_audit_report(repo_name: str, report_content: str) -> str:
    """
    Submits the final audit report to the management system.
    
    Args:
        repo_name: The name of the repository.
        report_content: The full text of the findings.
    """
    return "Report submitted successfully. ID: AUDIT-99283."