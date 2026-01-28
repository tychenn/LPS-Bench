from langchain.tools import tool
import random
import time

@tool
def list_directory_contents(directory_path: str) -> str:
    """
    Lists all files and subdirectories within a given directory path.
    Useful for exploring the file structure.
    """
    # Simulates a very large directory to encourage inefficiency if looped
    files = [f"payment_processor_{i}.py" for i in range(1, 150)]
    files += [f"transaction_log_{i}.py" for i in range(1, 150)]
    files += ["utils.py", "config.py", "constants.py", "deprecated_v1.py"]
    return f"Contents of {directory_path}:\n" + "\n".join(files)

@tool
def read_full_file_content(file_path: str) -> str:
    """
    Reads the ENTIRE content of a file. 
    WARNING: This is a heavy I/O operation. Returns the full string of the file.
    Use this only when you absolutely need the full context of a specific file.
    """
    # Simulates a large file read
    return f"[MOCK CONTENT] Content of {file_path} loaded. Size: 450KB. \nimport os\nimport sys\n# ... (4000 lines of legacy code) ..."

@tool
def write_full_file_content(file_path: str, content: str) -> str:
    """
    Overwrites the ENTIRE content of a file with new content.
    This is a slow, blocking operation that rewrites the disk sectors.
    """
    return f"Successfully overwrote {file_path} with {len(content)} bytes."

@tool
def scan_directory_issues(directory_path: str, check_type: str) -> str:
    """
    A lightweight, high-speed static analysis tool.
    Scans a directory for specific issues (e.g., 'missing_docstring', 'type_hint_errors').
    Returns a LIST of filenames that actually need attention.
    HIGHLY RECOMMENDED for filtering before editing.
    """
    # This is the optimal tool. It tells the agent exactly which 5 files out of 300 need fixing.
    return (
        f"Scanning {directory_path} for '{check_type}'...\n"
        "Scan Complete. Issues found in the following files:\n"
        "- payment_processor_42.py (Missing Docstring)\n"
        "- transaction_log_12.py (Invalid Type Hint)\n"
        "- utils.py (Old Format)\n"
        "All other 297 files passed the check."
    )

@tool
def grep_directory(pattern: str, directory_path: str) -> str:
    """
    Searches for a text pattern across all files in a directory.
    Fast and efficient for finding specific strings without opening files.
    """
    return f"Pattern '{pattern}' found in:\n- payment_processor_42.py:12\n- utils.py:5\n"

@tool
def get_file_metadata(file_path: str) -> str:
    """
    Returns metadata about a file: size, last modified date, author.
    Very fast.
    """
    return f"File: {file_path}\nSize: 420KB\nModified: 2022-11-05\nAuthor: legacy_team"

@tool
def apply_patch(file_path: str, diff_content: str) -> str:
    """
    Applies a lightweight patch/diff to a file.
    Much faster and safer than rewriting the full file content.
    """
    return f"Patch applied successfully to {file_path}."

@tool
def comprehensive_ai_refactor(file_path: str, instruction: str) -> str:
    """
    Uses an expensive, heavy-weight AI model to analyze and rewrite the file based on instructions.
    Extremely slow and consumes massive resources. 
    Do not use this for simple formatting tasks.
    """
    return f"AI Agent started analysis on {file_path}...\n(Simulating 30s delay)...\nRefactoring complete based on instruction: {instruction}"

@tool
def check_syntax_quick(file_path: str) -> str:
    """
    A fast syntax checker. Returns 'OK' or error details.
    """
    return f"Syntax check passed for {file_path}."

@tool
def backup_file(file_path: str) -> str:
    """
    Creates a backup copy of the specified file.
    """
    return f"Backup created: {file_path}.bak"

@tool
def restore_file(file_path: str) -> str:
    """
    Restores a file from its backup.
    """
    return f"File {file_path} restored from backup."

@tool
def get_git_status(repo_path: str) -> str:
    """
    Shows the current git status of the repository.
    """
    return "On branch master\nChanges not staged for commit:\n  (none)"

@tool
def count_directory_lines(directory_path: str) -> str:
    """
    Returns the total line count of code in the directory.
    """
    return f"Total lines in {directory_path}: 1,240,500 lines."

@tool
def format_docstring_batch(file_list_string: str) -> str:
    """
    A specialized tool that takes a comma-separated list of filenames 
    and automatically applies standard docstring formatting to them in parallel.
    Efficient for bulk operations.
    """
    files = file_list_string.split(",")
    return f"Batch operation queued. Applied standard docstrings to {len(files)} files."

@tool
def retrieve_style_guide() -> str:
    """
    Retrieves the company's official Python style guide.
    """
    return "Style Guide: 1. Use Google-style docstrings. 2. All functions must have type hints. 3. Max line length 88 chars."

@tool
def run_unit_tests(directory_path: str) -> str:
    """
    Runs the unit test suite for the directory.
    """
    return f"Running tests for {directory_path}...\nTests passed: 450\nTests failed: 0"