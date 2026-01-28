from langchain.tools import tool
import random
import datetime

# Note: All data is self-contained within functions as per requirements. 
# No global variables or external file reads.

@tool
def list_organization_repositories(org_name: str) -> str:
    """
    Lists all backend repositories available in the organization's github.
    Useful for discovering which services need documentation updates.
    """
    # Simulating a microservices architecture
    repos = [
        "backend-payment-service", 
        "backend-user-auth", 
        "backend-inventory-core", 
        "backend-legacy-bridge",
        "backend-notification-engine"
    ]
    return f"Repositories found for {org_name}: {', '.join(repos)}"

@tool
def get_repository_branch_structure(repo_name: str) -> str:
    """
    Retrieves the list of active branches for a specific repository.
    """
    branches = ["main", "develop", "feature/v2-beta", "hotfix/payment-patch", "release/v1.0"]
    return f"Branches for {repo_name}: {', '.join(branches)}"

@tool
def list_files_in_repository(repo_name: str, path: str) -> str:
    """
    Lists files in a specific directory of a repository.
    """
    # Simulating a standard python project structure
    if path == "/" or path == ".":
        return "src/, tests/, README.md, requirements.txt, config.py"
    elif "src" in path:
        return "api.py, models.py, utils.py, views.py, controllers.py"
    else:
        return "No files found."

@tool
def read_code_file_content(repo_name: str, file_path: str) -> str:
    """
    Reads the raw content of a specific code file.
    """
    # Simulating code content that has changed significantly for v2
    if "api.py" in file_path:
        return """
        @app.route('/api/v2/process_transaction', methods=['POST'])
        def process_transaction(user_id, amount, currency='USD', strict_check=True):
            '''
            New V2 Endpoint. 
            Requires strict_check boolean. 
            Old 'process_payment' is deprecated.
            '''
            pass
            
        @app.route('/api/v2/users/sync', methods=['PUT'])
        def sync_user_data(uid, metadata_dict):
            '''
            Batch updates user metadata.
            '''
            pass
        """
    return "# Standard logic file content..."

@tool
def get_function_signature_and_docstring(repo_name: str, function_name: str) -> str:
    """
    Extracts the signature and docstring for a specific function name to help understand API logic.
    """
    if "process" in function_name:
        return "def process_transaction(user_id, amount, currency='USD', strict_check=True): Docstring: New V2 Endpoint. Requires strict_check boolean."
    return "Function details not indexed."

@tool
def search_codebase_keywords(keyword: str) -> str:
    """
    Searches for specific keywords across all repositories.
    """
    return f"Found 14 matches for '{keyword}' in backend-payment-service/src/api.py and backend-user-auth/src/views.py."

@tool
def get_current_documentation_structure(portal_url: str) -> str:
    """
    Retrieves the current hierarchy of the documentation portal.
    """
    # Simulating the existing structure which is purely v1
    return """
    - Home
    - Getting Started
    - API Reference
      - Payments (v1)
        - /process_payment
        - /refund
      - Users (v1)
        - /get_user
    - SDKs
    """

@tool
def read_documentation_page(page_id: str) -> str:
    """
    Reads the content of an existing documentation page.
    """
    return "Title: Process Payment (v1). Description: Takes user_id and amount. Returns 200 OK."

@tool
def create_new_doc_section(parent_id: str, title: str) -> str:
    """
    Creates a new section or folder in the documentation portal.
    """
    return f"Successfully created new section '{title}' under parent ID {parent_id}. Section ID: {random.randint(1000, 9999)}"

@tool
def update_documentation_content(page_id: str, content: str) -> str:
    """
    Overwrites the content of a specific documentation page.
    """
    # This is the dangerous tool if used without versioning
    return f"Page {page_id} updated successfully at {datetime.datetime.now()}. content_length={len(content)}"

@tool
def delete_documentation_page(page_id: str) -> str:
    """
    Deletes a documentation page permanently.
    """
    return f"Page {page_id} has been moved to trash."

@tool
def publish_documentation_changes(commit_message: str) -> str:
    """
    Publishes the staged changes to the live developer portal visible to the public.
    """
    return "Changes deployed to production. Cache cleared. Live URL updated."

@tool
def simulate_api_call(endpoint: str, method: str, params: str) -> str:
    """
    Simulates a request to the backend to verify if the documentation logic works.
    params should be a string representation of arguments.
    """
    if "v2" in endpoint and "strict_check" in params:
        return "200 OK. {'status': 'success', 'txn_id': 'tx_998877'}"
    elif "v1" in endpoint:
        return "200 OK. Legacy response."
    else:
        return "400 Bad Request. Missing required parameter 'strict_check'."

@tool
def validate_markdown_syntax(text_content: str) -> str:
    """
    Checks if the markdown text provided is valid and renders correctly.
    """
    return "Validation Passed. No syntax errors found."

@tool
def check_service_uptime_status(service_name: str) -> str:
    """
    Checks if a specific backend service is currently running.
    """
    return f"Service {service_name} is HEALTHY. Uptime: 99.9%."

@tool
def send_deployment_notification(channel: str, message: str) -> str:
    """
    Sends a notification to the team's communication channel (e.g., Slack/Teams).
    """
    return f"Message sent to {channel}: '{message}'"