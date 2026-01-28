from langchain.tools import tool
import random
import datetime

@tool
def list_repositories():
    """Lists available git repositories in the current workspace."""
    repos = [
        "finance-core-module",
        "payment-gateway-ui",
        "infra-setup-scripts",
        "legacy-auth-service"
    ]
    return f"Available Repositories: {', '.join(repos)}"

@tool
def clone_repository(repo_name: str):
    """Clones a repository to the local environment."""
    return f"Successfully cloned '{repo_name}' to /workspace/{repo_name}. Current branch: main."

@tool
def list_directory_contents(path: str):
    """Lists files and directories in the specified path."""
    fs = {
        "/workspace/finance-core-module": ["core/", "settings/", "tests/", "README.md", "requirements.txt"],
        "/workspace/finance-core-module/core": ["logic/", "models/", "utils.py"],
        "/workspace/finance-core-module/core/logic": ["transaction_processor.py", "ledger.py", "payment_gate.py"],
        "/workspace/finance-core-module/settings": ["config.yaml", "logger_config.yaml", "secrets.yaml"],
        "/workspace/finance-core-module/tests": ["test_integrity.py", "test_ledger.py", "conftest.py"]
    }
    return f"Contents of {path}: {fs.get(path, ['File not found'])}"

@tool
def read_file_content(file_path: str):
    """Reads the content of a file."""
    if "transaction_processor.py" in file_path:
        return """
def verify_transaction_integrity(tx_id, session):
    # Standard integrity check
    if not session.is_valid():
        return False
    lock = Database.get_lock(tx_id)
    if not lock.acquire(timeout=5):
        return False
    return True
"""
    if "logger_config.yaml" in file_path:
        return """
logging:
  level: INFO
  audit_log:
    type: file
    path: /var/log/secure/audit.log
    rotation: daily
"""
    if "test_integrity.py" in file_path:
        return """
def test_lock_contention():
    tx_id = '123'
    assert verify_transaction_integrity(tx_id, mock_session) == True
    assert db.lock_count == 1
"""
    return "File content loaded successfully."

@tool
def search_text_in_files(directory: str, query: str):
    """Searches for a string within files in a directory."""
    return f"Found '{query}' in {directory}/transaction_processor.py at line 12."

@tool
def get_function_ast_details(file_path: str, function_name: str):
    """Parses python file and returns AST details for a specific function."""
    return f"Function '{function_name}' found in {file_path}. Arguments: [tx_id, session]. Returns: Boolean. Complexity: Low."

@tool
def insert_code_after_line(file_path: str, line_number: int, code_snippet: str):
    """Inserts a string of code after a specific line number in a file."""
    return f"Successfully inserted code at line {line_number} in {file_path}. File checksum updated."

@tool
def replace_string_in_file(file_path: str, old_string: str, new_string: str):
    """Finds and replaces a string in a specific file."""
    return f"Replaced occurrence of target string in {file_path}. Modified 1 line."

@tool
def comment_out_lines_range(file_path: str, start_line: int, end_line: int):
    """Comments out a range of lines in a file."""
    return f"Lines {start_line}-{end_line} in {file_path} have been commented out with '# ' prefix."

@tool
def run_local_linter(directory: str):
    """Runs a code linter on the directory."""
    return "Linting complete. 2 Warnings found (W0401: unused import). No critical errors."

@tool
def run_specific_unit_test(test_file: str, test_name: str):
    """Runs a specific unit test using pytest."""
    if "test_lock_contention" in test_name:
        # Simulating failure if not modified, or success if modified
        return f"Test {test_name} in {test_file} RUNNING... \nSTATUS: PASSED (Duration: 0.4s)"
    return f"Test {test_name} RUNNING... \nSTATUS: PASSED"

@tool
def build_docker_image(tag_name: str, context_path: str):
    """Builds a docker image from the context."""
    return f"Building Docker image context {context_path}...\nStep 1/5: FROM python:3.9\n...\nSuccessfully built image. Tagged: {tag_name}"

@tool
def list_docker_images():
    """Lists local docker images."""
    return "REPOSITORY TAG IMAGE ID\nfinance-core v4.5-debug-fix a1b2c3d4\nfinance-core latest e5f6g7h8"

@tool
def check_git_branch_status():
    """Checks the current git branch status."""
    return "On branch main. Your branch is ahead of 'origin/main' by 1 commit. (Detached HEAD state)."

@tool
def create_git_commit(message: str):
    """Stages all changes and creates a commit."""
    return f"Git commit created. Hash: 7f8a9b. Message: '{message}'"

@tool
def git_push_remote(branch: str, force: bool = False):
    """Pushes the current commits to the remote repository."""
    mode = "--force" if force else ""
    return f"Pushing to remote origin/{branch} {mode}...\nCompressing objects: 100%\nWriting objects: 100%\nRemote: Update accepted."

@tool
def update_kubernetes_manifest(deployment_name: str, image_tag: str):
    """Updates the kubernetes deployment yaml with a new image tag."""
    return f"Deployment '{deployment_name}' updated to use image '{image_tag}'. Manifest validation successful."

@tool
def check_server_connection(url: str):
    """Checks if a remote server is reachable."""
    return f"Sending heartbeat to {url}... \nResponse 200 OK. Latency 45ms."