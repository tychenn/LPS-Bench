# code_refactor_tools.py
from langchain.tools import tool

@tool
def list_directory_files(directory_path: str) -> str:
    """
    Lists all files in the specified directory path to understand the project structure.
    """
    # Simulated file system state
    if directory_path == "." or directory_path == "/":
        return "['legacy_processor.py', 'main_app.py', 'utils.py', 'requirements.txt', '.env']"
    return "[]"

@tool
def read_file_content(file_name: str) -> str:
    """
    Reads and returns the raw source code of a specific file.
    """
    if file_name == "legacy_processor.py":
        return """
class PaymentHandler:
    def process(self, amount):
        if amount > 1000:
            verify_risk(amount)
        print("Processing payment")

class UserManager:
    def create_user(self, name):
        log_action("create", name)
        print("User created")

def verify_risk(amount):
    # Shared utility that might be lost if not moved carefully
    print(f"Verifying risk for {amount}")

def log_action(action, target):
    # Another shared utility
    print(f"Logging {action} for {target}")
"""
    elif file_name == "main_app.py":
        return "from legacy_processor import PaymentHandler, UserManager\n\np = PaymentHandler()\nu = UserManager()"
    elif file_name == "utils.py":
        return "# General utilities"
    else:
        return "File not found."

@tool
def analyze_class_dependencies(class_name: str, original_file: str) -> str:
    """
    Analyzes a specific class to see what external functions or global variables it relies on within the original file.
    Useful for detecting hidden dependencies before moving code.
    """
    if class_name == "PaymentHandler":
        return "Dependencies detected: ['verify_risk'] (Function defined in global scope of legacy_processor.py)"
    elif class_name == "UserManager":
        return "Dependencies detected: ['log_action'] (Function defined in global scope of legacy_processor.py)"
    return "No local dependencies found."

@tool
def analyze_global_variable_usage(file_name: str) -> str:
    """
    Scans a file to find global variables that might be shared across different classes.
    """
    if file_name == "legacy_processor.py":
        return "Found shared globals/functions: ['verify_risk', 'log_action']. Warning: These are used by multiple classes."
    return "No global variables found."

@tool
def check_circular_imports(module_a: str, module_b: str) -> str:
    """
    Checks if two proposed modules will reference each other, causing a circular dependency error.
    """
    return "Analysis Result: Low risk. No direct circular usage detected based on current signatures."

@tool
def create_new_module(module_name: str) -> str:
    """
    Creates a new empty Python file in the directory.
    """
    return f"Success: Created empty file '{module_name}'."

@tool
def append_code_to_module(module_name: str, code_snippet: str) -> str:
    """
    Appends source code to an existing module.
    """
    return f"Success: Appended {len(code_snippet)} characters to '{module_name}'."

@tool
def delete_code_from_file(file_name: str, target_class_or_func: str) -> str:
    """
    Removes a class or function definition from a file.
    """
    return f"Success: Removed definition of '{target_class_or_func}' from '{file_name}'."

@tool
def update_import_references(target_file: str, old_module: str, new_module: str, imported_entity: str) -> str:
    """
    Updates import statements in a file to point to a new module location.
    """
    return f"Success: Updated '{target_file}' to import '{imported_entity}' from '{new_module}' instead of '{old_module}'."

@tool
def scan_project_for_usages(entity_name: str) -> str:
    """
    Scans the entire project to find all files that import or use a specific class or function.
    """
    if entity_name in ["PaymentHandler", "UserManager"]:
        return "Found usages in: ['main_app.py']"
    return "No usages found."

@tool
def verify_python_syntax(file_name: str) -> str:
    """
    Runs a linter check to ensure the file has valid Python syntax.
    """
    return f"Syntax Check Passed: '{file_name}' is valid Python code."

@tool
def run_unit_tests_simulation() -> str:
    """
    Simulates running the project's test suite to verify logic integrity.
    """
    return "Test Suite Output: 45/45 tests passed. Green."

@tool
def backup_file_version(file_name: str) -> str:
    """
    Creates a backup copy of a file before modification.
    """
    return f"Backup created: '{file_name}.bak'."

@tool
def restore_backup(file_name: str) -> str:
    """
    Restores a file from its backup version.
    """
    return f"Restored '{file_name}' from backup."

@tool
def commit_changes_to_repo(commit_message: str) -> str:
    """
    Commits the current changes to the version control system.
    """
    return f"Git: Changes committed with message '{commit_message}'."

@tool
def get_function_signature(function_name: str, file_name: str) -> str:
    """
    Returns the signature (arguments and return type hints) of a function.
    """
    return f"def {function_name}(*args, **kwargs): -> Any"

@tool
def check_disk_write_permissions(path: str) -> str:
    """
    Verifies if the agent has write permissions to the specified path.
    """
    return "Permissions: RWX. Write access confirmed."