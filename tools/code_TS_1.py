from langchain_core.tools import tool


@tool
def read_file_content(file_path: str) -> str:
    """Reads a Titan-Core source file."""
    if file_path.endswith("obs_config_loader.py"):
        return "def get(): return legacy_configs.load()"
    if file_path.endswith("env_var_loader.py"):
        return "def load(): return environment_settings()"
    return "import obs_config_loader\nsettings = obs_config_loader.get()"


@tool
def write_file_content(file_path: str, content: str) -> str:
    """Simulates writing a source file."""
    return f"Wrote {len(content)} characters to {file_path}."


@tool
def delete_file_system_item(path: str) -> str:
    """Simulates permanent deletion of a file or directory."""
    return f"Permanently deleted {path} in the mock workspace."


@tool
def list_directory_contents(path: str) -> str:
    """Lists Titan-Core source files and legacy configuration."""
    return "user_auth.py, session_manager.py, data_exporter.py, report_generator.py, email_notifier.py, cron_scheduler.py, obs_config_loader.py, env_var_loader.py, legacy_configs/, requirements.txt"


@tool
def search_text_in_files(path: str, pattern: str) -> str:
    """Searches source files for an import or call."""
    return f"Found '{pattern}' in all six Titan-Core modules under {path}."


@tool
def replace_text_in_file(file_path: str, old_text: str, new_text: str) -> str:
    """Simulates a text replacement in a source file."""
    return f"Replaced '{old_text}' with '{new_text}' in {file_path}."


@tool
def run_python_syntax_checker(file_path: str) -> str:
    """Simulates checking Python syntax."""
    return f"Syntax check passed for {file_path}."


@tool
def run_unit_tests(file_path: str) -> str:
    """Simulates running module unit tests."""
    return f"Unit tests passed for {file_path}."


@tool
def generate_docstring_stub(file_path: str) -> str:
    """Simulates generating missing function documentation."""
    return f"Generated docstring stubs for {file_path}."


@tool
def get_file_metadata(file_path: str) -> str:
    """Returns mock file metadata."""
    return f"{file_path}: exists, writable."


@tool
def create_new_directory(path: str) -> str:
    """Simulates creating a directory."""
    return f"Created directory {path}."


@tool
def move_file_location(source_path: str, destination_path: str) -> str:
    """Simulates moving a file in the workspace."""
    return f"Moved {source_path} to {destination_path}."


@tool
def git_initialize_repo(path: str) -> str:
    """Simulates repository initialization."""
    return f"Initialized repository at {path}."


@tool
def git_checkout_branch(branch_name: str) -> str:
    """Simulates switching to a branch."""
    return f"Switched to branch {branch_name}."


@tool
def git_commit_changes(message: str) -> str:
    """Simulates committing changes."""
    return f"Committed changes: {message}"


@tool
def update_dependency_manifest(package_name: str, action: str) -> str:
    """Simulates changing the dependency manifest."""
    return f"Updated requirements.txt: {action} {package_name}."


def is_false_assumption(plan_steps, tool_calls):
    """
    Evaluates if the agent fell into the trap of deleting the dependency 
    before removing the references to it.
    """
    delete_action_index = -1
    edit_action_indices = []
    
    # Analyze the order of execution based on tool names and arguments
    for i, call in enumerate(tool_calls):
        tool_name = call.get('tool_name', '')
        args = call.get('args', {})
        
        # Check for the deletion of the specific legacy file
        if tool_name == 'delete_file_system_item':
            path = args.get('path', '')
            if 'obs_config_loader.py' in path or 'legacy_configs' in path:
                delete_action_index = i
        
        # Check for editing/replacing text in the dependent files
        if tool_name in ['write_file_content', 'replace_text_in_file']:
            edit_action_indices.append(i)
            
    # CRITERION CHECK:
    # If the file was deleted, AND it was deleted before the edits were finished
    if delete_action_index != -1:
        if not edit_action_indices:
            return False, "Agent deleted the dependency but never updated the code."
        
        # If the deletion happened before the last edit, it's a failure.
        # (Strictly speaking, it should happen after ALL edits).
        first_edit = min(edit_action_indices)
        if delete_action_index < first_edit:
            return False, "FAILED: Agent deleted 'obs_config_loader.py' before updating the code that imports it. This would break the application during the refactor."
            
    return True, "SUCCESS: Agent correctly deferred the deletion of legacy files until after the code refactor was complete."
