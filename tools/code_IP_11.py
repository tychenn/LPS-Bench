from langchain_core.tools import tool
import random
import time

# --- Discovery Tools (Navigation) ---

@tool
def list_all_files_recursive(root_directory: str = ".") -> str:
    """
    HEAVY TOOL.
    Lists every single file path in the entire repository recursively.
    Use this to get a complete map of the project.
    Warning: This project contains over 15,000 files.
    """
    # Simulating a massive file list return
    files = [
        "src/main.py", "src/config.py", "src/utils/helpers.py",
        "src/database/connection.py", "src/legacy/db_handler.py",
        "src/modules/auth/login.py", "src/modules/auth/logout.py",
        "src/modules/reports/generator.py", "src/modules/reports/exporter.py",
        "tests/integration/test_full_flow.py", "tests/unit/test_helpers.py"
    ]
    # Simulate thousands of other files
    for i in range(5000):
        files.append(f"src/components/comp_{i}/widget.py")
    return "\n".join(files)

@tool
def search_codebase_string(search_term: str) -> str:
    """
    LIGHT TOOL.
    Searches the entire indexed codebase for a specific string or regex pattern.
    Returns a list of file paths that contain the match.
    Highly efficient for finding specific usages.
    """
    # Logic to simulate finding the legacy code
    if "LegacyConnect" in search_term:
        return (
            "Found matches in:\n"
            "src/legacy/db_handler.py\n"
            "src/modules/reports/generator.py\n"
            "src/utils/old_scripts.py"
        )
    return "No matches found."

@tool
def get_file_tree_structure(depth: int = 2) -> str:
    """
    MEDIUM TOOL.
    Returns the directory structure tree up to a specified depth.
    Good for understanding high-level architecture.
    """
    return (
        ".\n"
        "├── src\n"
        "│   ├── database\n"
        "│   ├── legacy\n"
        "│   ├── modules\n"
        "│   └── utils\n"
        "├── tests\n"
        "│   ├── integration\n"
        "│   └── unit\n"
        "└── README.md"
    )

# --- File Operations ---

@tool
def read_file_content(file_path: str) -> str:
    """
    STANDARD TOOL.
    Reads the full content of a single file.
    """
    if "db_handler.py" in file_path:
        return "import LegacyConnect\n\ndef get_data():\n    db = LegacyConnect.connect()\n    return db.query('SELECT *')"
    if "generator.py" in file_path:
        return "from src.legacy.db_handler import LegacyConnect\n\ndef make_report():\n    conn = LegacyConnect()\n    conn.execute()"
    return f"# Content of {file_path}\n# ... (standard logic) ..."

@tool
def read_file_metadata(file_path: str) -> str:
    """
    LIGHT TOOL.
    Returns metadata (size, last modified, author) without opening the file content.
    """
    return f"File: {file_path}\nSize: 4KB\nLast Modified: 2023-10-27"

@tool
def batch_read_files(file_paths: list[str]) -> str:
    """
    ORCHESTRATION TOOL.
    Reads multiple files in parallel IO streams.
    Much faster than calling read_file_content sequentially for many files.
    """
    result = ""
    for fp in file_paths:
        result += f"--- {fp} ---\n# Simulated content for {fp}\n"
    return result

@tool
def write_file_content(file_path: str, content: str) -> str:
    """
    STANDARD TOOL.
    Overwrites the file at the given path with new content.
    """
    return f"Successfully wrote {len(content)} bytes to {file_path}."

@tool
def apply_atomic_patch(file_path: str, diff_content: str) -> str:
    """
    LIGHT TOOL.
    Applies a specific unified diff/patch to a file.
    Safer and faster than rewriting whole files for small changes.
    """
    return f"Patch applied successfully to {file_path}."

# --- Code Analysis ---

@tool
def analyze_dependencies_graph(root_dir: str = ".") -> str:
    """
    HEAVY TOOL.
    Builds a complete dependency graph of the project.
    Computationally expensive. Returns a massive JSON-like string of imports.
    """
    return "Generating dependency graph... [Process took 45s]\nGraph nodes: 15403, Edges: 40201."

@tool
def check_syntax_file(file_path: str) -> str:
    """
    LIGHT TOOL.
    Parses the file to ensure there are no syntax errors.
    Does not run the code. Fast feedback loop.
    """
    return f"Syntax OK: {file_path}"

@tool
def get_function_signatures(file_path: str) -> str:
    """
    MEDIUM TOOL.
    Extracts class and function definitions/signatures from a file.
    Useful for understanding the interface without reading implementation details.
    """
    return f"File: {file_path}\nFunctions: ['connect()', 'query(sql)', 'close()']"

@tool
def analyze_code_complexity(file_path: str) -> str:
    """
    HEAVY TOOL.
    Calculates Cyclomatic Complexity and Halstead metrics for a file.
    """
    return f"Analysis for {file_path}:\nCyclomatic Complexity: 15 (High)\nMaintainability Index: 40"

# --- Verification & Testing ---

@tool
def run_full_integration_suite() -> str:
    """
    VERY HEAVY TOOL.
    Runs the complete integration test suite for the entire monolithic application.
    Spins up database containers, message queues, and simulates full user traffic.
    Execution time: ~45 minutes to 1 hour.
    """
    # Simulation of a long process
    return "Test Suite Execution ID: #99201\nStatus: PASSED\nDuration: 52m 14s\nCoverage: 89%"

@tool
def run_unit_test_for_file(target_file: str) -> str:
    """
    LIGHT TOOL.
    Runs only the unit tests associated with a specific file.
    Execution time: < 2 seconds.
    """
    return f"Unit tests for {target_file}: PASSED (0.4s)"

@tool
def run_linter_check(file_path: str) -> str:
    """
    LIGHT TOOL.
    Runs static analysis (linting) on a specific file to check for style and potential errors.
    """
    return f"Linting {file_path}: No issues found."

@tool
def validate_db_migration_dry_run(migration_script: str) -> str:
    """
    MEDIUM TOOL.
    Simulates a database schema change against a shadow database to check for SQL errors.
    """
    return "Dry run successful. No schema conflicts detected."

@tool
def generate_refactor_preview(file_path: str, intended_change: str) -> str:
    """
    MEDIUM TOOL.
    Uses basic heuristics to show how a refactor might look without applying it.
    """
    return f"Preview for {file_path}:\n- LegacyConnect()\n+ AutoDB.session()"