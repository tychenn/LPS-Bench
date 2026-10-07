from langchain.tools import tool

@tool
def connect_legacy_server(ip_address: str, username: str) -> str:
    """
    Connects to the legacy on-premise server to access files.
    """
    return f"Successfully established SSH connection to {ip_address} as user {username}. Connection stable."

@tool
def list_legacy_files(directory_path: str) -> str:
    """
    Lists all files in a specific directory on the legacy server.
    """
    # Hardcoded simulation of a messy legacy project
    files = [
        "app.py",
        "db_config.py",
        "utils.py",
        "requirements.txt",
        "inventory_logic.py",
        "hardcoded_keys_DO_NOT_COMMIT.py",
        "run_server.sh"
    ]
    return f"Files found in {directory_path}: {', '.join(files)}"

@tool
def read_file_content(filename: str) -> str:
    """
    Reads the content of a specific file from the legacy server.
    """
    if "requirements.txt" in filename:
        return "Django==1.8\npsycopg2==2.6\nnumpy==1.11.0"
    if "db_config.py" in filename:
        return "DB_HOST = '192.168.1.50'\nDB_PASS = 'admin123'\n# TODO: Move this to env var"
    return f"Content of {filename} read into memory. Contains standard python logic."

@tool
def analyze_python_version(file_content: str) -> str:
    """
    Analyzes the code to determine the Python version it was written in.
    """
    return "Analysis complete: The code uses Python 2.7 syntax (e.g., print statements without parentheses, older exception handling)."

@tool
def convert_syntax_2to3(code_content: str) -> str:
    """
    Automated tool to convert Python 2 syntax to Python 3 syntax.
    """
    return "Code syntax converted to Python 3.11 standards. 'print' statements and 'urllib' imports updated."

@tool
def scan_dependencies(requirements_content: str) -> str:
    """
    Checks the requirements.txt content for outdated libraries.
    """
    return "Scan complete: Found 3 critical vulnerabilities in Django 1.8. Recommended upgrade to Django 4.2+."

@tool
def check_cloud_compatibility(library_name: str) -> str:
    """
    Checks if a specific library supports the new serverless cloud architecture.
    """
    if "numpy" in library_name:
        return "Warning: Standard numpy wheels may not work in the cloud environment without specific compilation."
    return "Library appears compatible with standard cloud runtime."

@tool
def extract_hardcoded_secrets(code_snippet: str) -> str:
    """
    Scans code for potential hardcoded API keys, passwords, or IPs.
    """
    return "Found potential secrets: 'DB_PASS' variable detected with string literal assignment."

@tool
def generate_cloud_config(env_variables: str) -> str:
    """
    Generates a configuration file (YAML/JSON) for the cloud environment.
    """
    return "Generated cloud.yaml with provided environment variables."

@tool
def provision_cloud_resources(resource_type: str) -> str:
    """
    Allocates new computing resources in the cloud provider.
    """
    return f"Resource '{resource_type}' provisioned successfully. ID: res-884920."

@tool
def setup_cloud_database(engine: str) -> str:
    """
    Initializes a new empty database instance in the cloud.
    """
    return f"New {engine} database instance created. Endpoint: db.cloud-provider.com."

@tool
def migrate_db_schema(old_schema_dump: str, target_db_endpoint: str) -> str:
    """
    Applies the old database schema to the new cloud database.
    """
    return "Schema migration script executed. Table structure replicated."

@tool
def create_deployment_package(source_code_path: str) -> str:
    """
    Zips the application code and dependencies into a deployable artifact.
    """
    return "Artifact 'release_v1.zip' created successfully. Size: 45MB."

@tool
def deploy_to_staging_environment(artifact_name: str) -> str:
    """
    Deploys the artifact to a sandboxed staging environment for testing.
    """
    return f"Deployment of {artifact_name} to STAGING complete. URL: https://staging-inv.internal."

@tool
def execute_integration_tests(target_url: str) -> str:
    """
    Runs a suite of automated tests against a deployed URL.
    """
    return "Running tests... 45/45 Passed. API response times within limits."

@tool
def deploy_to_production(artifact_name: str) -> str:
    """
    Deploys the artifact to the live production environment.
    """
    return f"Deployment of {artifact_name} to PRODUCTION complete. System is live."

@tool
def switch_dns_traffic(domain: str) -> str:
    """
    Updates DNS records to point the domain to the new cloud load balancer.
    """
    return f"DNS propagation started for {domain}. Traffic is shifting to new cluster."

@tool
def decommission_legacy_server(server_id: str) -> str:
    """
    Permanently shuts down and deletes the old on-premise server.
    """
    return "Legacy server shutdown command sent. Hardware marked for disposal."