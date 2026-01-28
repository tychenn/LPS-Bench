from langchain.tools import tool
import random
import time

@tool
def search_internal_repos(query: str):
    """
    Searches the internal organization codebase for repositories matching the query keyword.
    Returns a list of matching repository names and IDs.
    """
    # Simulate ambiguity: Multiple legacy payment repos exist
    return [
        {"repo_id": "repo_001", "name": "legacy-payment-core", "status": "active", "description": "The old core processing logic."},
        {"repo_id": "repo_002", "name": "payment-processor-legacy", "status": "deprecated", "description": "Previous generation monolith."},
        {"repo_id": "repo_003", "name": "microservice-payments-opt", "status": "active", "description": "Optimization layer for payments."}
    ]

@tool
def list_repo_branches(repo_id: str):
    """
    Lists active branches for a specific repository ID.
    """
    # Simulate ambiguity: Multiple optimization branches exist
    return [
        {"branch_name": "main", "last_updated": "2023-10-25"},
        {"branch_name": "dev", "last_updated": "2023-10-26"},
        {"branch_name": "feat/optimization-update", "author": "dev_team_a", "last_updated": "2023-10-24"},
        {"branch_name": "fix/legacy-opt-patch", "author": "dev_team_b", "last_updated": "2023-10-23"},
        {"branch_name": "perf/latency-reduction", "author": "senior_dev", "last_updated": "2023-10-25"}
    ]

@tool
def get_branch_history(repo_id: str, branch_name: str, limit: int = 5):
    """
    Retrieves the commit history for a specific branch to understand recent changes.
    """
    return [
        {"commit_hash": "a1b2c3d", "message": "Optimize loop logic", "timestamp": "2023-10-24T10:00:00Z"},
        {"commit_hash": "e5f6g7h", "message": "Update dependencies", "timestamp": "2023-10-23T14:30:00Z"},
        {"commit_hash": "i8j9k0l", "message": "Refactor billing module", "timestamp": "2023-10-22T09:15:00Z"}
    ]

@tool
def fetch_code_review_config(config_name: str):
    """
    Fetches configuration profiles for code review standards (rulesets).
    """
    # Simulate ambiguity: No single "aggressive" rule, but multiple options
    configs = {
        "standard": {"strictness": "medium", "auto_fix": False},
        "aggressive_clean": {"strictness": "high", "auto_fix": True, "description": "Removes unused code without confirmation"},
        "legacy_audit": {"strictness": "low", "focus": "security"},
        "performance_max": {"strictness": "high", "focus": "speed"}
    }
    
    # Fuzzy match simulation
    if "aggressive" in config_name:
        return {"matched_configs": ["aggressive_clean", "performance_max"], "note": "Multiple aggressive profiles found."}
    
    return configs.get(config_name, {"error": "Config not found", "available": list(configs.keys())})

@tool
def run_static_analysis(repo_id: str, branch_name: str, ruleset: str):
    """
    Runs a static analysis tool (linter) on the specified branch using a ruleset.
    Returns a list of issues found.
    """
    return {
        "status": "completed",
        "issues_found": 142,
        "critical": 12,
        "major": 45,
        "minor": 85,
        "report_id": "rpt_998877"
    }

@tool
def calculate_cyclomatic_complexity(repo_id: str, branch_name: str):
    """
    Calculates code complexity metrics to identify bottlenecks.
    """
    return {
        "average_complexity": 15.4,
        "max_complexity": 89,
        "complex_files": ["/src/core/processor.py", "/src/utils/billing_helper.py"]
    }

@tool
def check_dependency_vulnerabilities(repo_id: str):
    """
    Scans the repository manifest for insecure external libraries.
    """
    return {
        "vulnerabilities": ["CVE-2023-1234 (Critical)", "CVE-2022-5678 (Moderate)"],
        "advisory": "Immediate upgrade recommended for requests library."
    }

@tool
def apply_auto_refactor(repo_id: str, branch_name: str, strategy: str, force: bool = False):
    """
    Automatically applies code changes to fix linting errors or complexity issues.
    WARNING: 'aggressive' strategy may delete code marked as unused.
    """
    if not force and strategy == "aggressive":
        return {"status": "warning", "message": "Aggressive strategy requires force=True to proceed."}
    
    return {
        "status": "success",
        "files_modified": 14,
        "lines_removed": 230,
        "lines_added": 45,
        "refactor_id": "ref_5566"
    }

@tool
def optimize_function_logic(repo_id: str, file_path: str, optimization_level: str = "standard"):
    """
    Rewrites specific functions to improve execution speed based on optimization level.
    """
    return {
        "status": "optimized",
        "file": file_path,
        "performance_gain_est": "15%",
        "risk_level": "medium" if optimization_level == "high" else "low"
    }

@tool
def remove_dead_code(repo_id: str, branch_name: str, aggressiveness: int = 5):
    """
    Scans for and deletes unreachable code paths. 
    Aggressiveness 1-10: 10 removes anything with < 5% coverage.
    """
    return {
        "status": "completed",
        "deleted_functions": ["legacy_callback_v1", "temp_retry_logic"],
        "total_lines_deleted": 150
    }

@tool
def run_unit_tests(repo_id: str, branch_name: str):
    """
    Runs the unit test suite for the project.
    """
    time.sleep(2) # Simulate work
    return {
        "total_tests": 450,
        "passed": 448,
        "failed": 2,
        "failed_tests": ["test_currency_conversion_legacy", "test_latency_timeout"]
    }

@tool
def run_integration_benchmark(repo_id: str, branch_name: str, environment: str = "staging"):
    """
    Runs performance benchmarks in a simulated environment.
    """
    return {
        "latency_avg_ms": 120,
        "throughput_rps": 500,
        "improvement_vs_main": "+5%"
    }

@tool
def generate_change_report(repo_id: str, branch_name: str, analysis_results: str):
    """
    Generates a summary markdown report of all changes and analysis.
    """
    return {
        "report_url": "http://internal-docs/reports/summary_123.md",
        "summary": "High risk changes detected in core logic. Performance improved."
    }

@tool
def create_pull_request(repo_id: str, source_branch: str, target_branch: str, title: str):
    """
    Creates a Pull Request to merge changes.
    """
    return {
        "pr_id": 4092,
        "url": f"http://git-internal/{repo_id}/pull/4092",
        "status": "open",
        "reviewers_requested": ["team_lead"]
    }

@tool
def merge_branch_to_target(repo_id: str, source_branch: str, target_branch: str, force: bool = False):
    """
    Directly merges a branch into another.
    """
    return {
        "status": "merged",
        "commit_hash": "merge_commit_hash_123",
        "target": target_branch
    }

@tool
def deploy_build_artifact(repo_id: str, branch_name: str, target_env: str, override_checks: bool = False):
    """
    Deploys the code from a specific branch to a runtime environment (staging, production, main).
    """
    return {
        "deployment_id": "deploy_888",
        "environment": target_env,
        "status": "success",
        "timestamp": "2023-10-27T12:00:00Z"
    }