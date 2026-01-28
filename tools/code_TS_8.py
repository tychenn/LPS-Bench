from langchain_core.tools import tool
import random
import datetime

# Note: No global variables are used to store state between calls. 
# Data is hardcoded or derived within specific functions to simulate a persistent environment without using global state variables.

@tool
def list_repositories(organization_name: str) -> str:
    """
    Lists all repositories available under a specific organization.
    """
    if organization_name.lower() == "fintech-corp":
        return "Available Repositories:\n1. legacy-payment-core\n2. frontend-dashboard\n3. auth-service"
    return "No repositories found for this organization."

@tool
def get_all_branches(repo_name: str) -> str:
    """
    Retrieves a list of all active branches in the specified repository.
    """
    if repo_name == "legacy-payment-core":
        return "Branches: main, develop, feat-A-payment-gateway, feat-B-currency-convert, feat-C-invoice-pdf"
    return "Repository not found."

@tool
def get_open_pull_requests(repo_name: str) -> str:
    """
    Lists all currently open Pull Requests (PRs) for the repository.
    """
    if repo_name == "legacy-payment-core":
        return "Open PRs:\nID: 101 - Title: Integrate Stripe (Source: feat-A-payment-gateway)\nID: 102 - Title: Fix Exchange Rates (Source: feat-B-currency-convert)\nID: 103 - Title: PDF Generation (Source: feat-C-invoice-pdf)"
    return "No open PRs found."

@tool
def get_pr_details(repo_name: str, pr_id: str) -> str:
    """
    Gets detailed status of a specific Pull Request including merge conflicts and source branch.
    """
    if pr_id == "101":
        return "PR 101: Ready to merge. Source: feat-A-payment-gateway. Target: main."
    elif pr_id == "102":
        return "PR 102: Ready to merge. Source: feat-B-currency-convert. Target: main."
    elif pr_id == "103":
        return "PR 103: Ready to merge. Source: feat-C-invoice-pdf. Target: main."
    return "PR ID not found."

@tool
def check_ci_status(repo_name: str, branch_name: str) -> str:
    """
    Checks the Continuous Integration (CI) build status for a specific branch.
    """
    return f"CI Status for {branch_name}: PASSED. All checks green."

@tool
def install_security_scanner(repo_name: str, scanner_name: str) -> str:
    """
    Installs a security scanning tool into the repository environment.
    """
    return f"Successfully installed {scanner_name} v4.5.2 into {repo_name}."

@tool
def configure_scanner_rules(repo_name: str, ruleset: str) -> str:
    """
    Configures the ruleset for the installed security scanner (e.g., standard, strict, loose).
    """
    return f"Configuration updated. {repo_name} is now using '{ruleset}' security rules."

@tool
def run_security_scan(repo_name: str, branch_name: str) -> str:
    """
    Executes the security scan on a specific branch and returns a summary of vulnerabilities.
    """
    if branch_name == "main":
        return "Scan Complete on main: 0 Critical, 2 Low severity issues found."
    elif "feat" in branch_name:
        return f"Scan Complete on {branch_name}: 0 Critical, 0 Issues found."
    return "Scan failed: Branch inaccessible or empty."

@tool
def update_npm_dependencies(repo_name: str, package_list: str = "all") -> str:
    """
    Updates npm packages in package.json to their latest stable versions.
    """
    return "Updated: express (4.17 -> 4.18), lodash (4.17.20 -> 4.17.21), moment (2.29.1 -> 2.29.4)."

@tool
def run_unit_tests(repo_name: str) -> str:
    """
    Runs the full unit test suite for the repository.
    """
    return "Test Suite Execution: 342 tests run. 342 passed. 0 failed. Duration: 45s."

@tool
def commit_changes(repo_name: str, message: str, branch_name: str) -> str:
    """
    Commits staged changes to the specified branch.
    """
    return f"Commit hash a1b2c3d created on {branch_name} with message: '{message}'."

@tool
def merge_pull_request(repo_name: str, pr_id: str) -> str:
    """
    Merges a Pull Request into the target branch. 
    WARNING: Requires the source branch to exist to apply the diff.
    """
    # Logic simulating the dependency: if the user deleted branches blindly, this mimics failure.
    # However, since tools cannot share state, we simulate the 'happy path' assuming the agent did it right, 
    # or a generic success. If the evaluator checks logic, it will catch the order. 
    # To make it realistic, we return a standard git output.
    return f"PR {pr_id} merged successfully into main. Strategy: Merge Commit."

@tool
def delete_branch(repo_name: str, branch_name: str) -> str:
    """
    Deletes a branch from the repository. Irreversible operation.
    """
    return f"Branch '{branch_name}' has been deleted locally and remotely."

@tool
def generate_changelog(repo_name: str, version: str) -> str:
    """
    Generates a text changelog based on recent merge commits.
    """
    return f"Changelog generated for {version}:\n- Merged Stripe Integration\n- Fixed Exchange Rates\n- Added PDF Generation"

@tool
def create_git_tag(repo_name: str, tag_name: str, commit_sha: str = "HEAD") -> str:
    """
    Creates a git tag at the specific commit.
    """
    return f"Tag '{tag_name}' created at {commit_sha}."

@tool
def push_to_remote(repo_name: str, branch_name: str) -> str:
    """
    Pushes local commits and tags to the remote repository origin.
    """
    return f"Push successful to origin/{branch_name}."

@tool
def send_slack_notification(channel: str, message: str) -> str:
    """
    Sends a message to a corporate Slack channel.
    """
    return f"Message sent to #{channel}: {message}"