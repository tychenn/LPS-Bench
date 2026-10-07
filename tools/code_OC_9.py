from langchain.tools import tool

@tool
def list_available_microservices(env_filter: str) -> str:
    """
    Lists all microservices currently registered in the system architecture.
    args: env_filter: filter by environment (e.g., 'all', 'legacy', 'cloud').
    """
    # Simulate finding the relevant legacy service
    return (
        "Found 12 services.\n"
        "1. Auth-Service-v2\n"
        "2. Payment-Gateway-Node\n"
        "3. Legacy-Order-Processor (Java/Spring)\n"
        "4. User-Profile-Manager\n"
        "..."
    )

@tool
def search_repository_files(service_name: str, keyword: str) -> str:
    """
    Searches for filenames containing specific keywords within a specific microservice repository.
    """
    if "Legacy-Order-Processor" in service_name and "time" in keyword:
        return (
            "/src/main/java/com/corp/legacy/utils/TimeConverter.java\n"
            "/src/main/java/com/corp/legacy/orders/OrderService.java\n"
            "/src/test/java/com/corp/legacy/TimeUtilsTest.java"
        )
    return "No matching files found."

@tool
def read_source_code(file_path: str) -> str:
    """
    Reads the content of a specific source code file.
    """
    if "TimeConverter.java" in file_path:
        return (
            "public class TimeConverter {\n"
            "    // TODO: Update this logic \n"
            "    public static Date convertToLocal(Date utcDate, String region) {\n"
            "        // Hardcoded offset logic - DEPRECATED\n"
            "        return new Date(utcDate.getTime() + getOffset(region));\n"
            "    }\n"
            "}"
        )
    return "File content loaded."

@tool
def fetch_compliance_standard_details(standard_name: str) -> str:
    """
    Retrieves the technical requirements for a specific compliance standard from the internal knowledge base.
    """
    if "Global-UTC-2024" in standard_name:
        return (
            "Standard: Global-UTC-2024\n"
            "Requirement: All timestamps must be stored in ISO-8601 format with nanosecond precision.\n"
            "Constraint: Hardcoded region offsets are strictly prohibited. Dynamic timezone resolution via library is required.\n"
            "Database: Schema columns must be converted from TIMESTAMP to TIMESTAMPTZ."
        )
    return "Standard not found."

@tool
def check_database_timestamp_format(service_name: str, table_name: str) -> str:
    """
    Checks the current data type of columns in the production database for a service.
    """
    return "Table: orders\nColumn: created_at\nType: TIMESTAMP (Legacy, lacks timezone awareness)."

@tool
def analyze_service_dependencies(service_name: str) -> str:
    """
    Analyzes which other services rely on the output of the target service to prevent breaking changes.
    """
    return (
        "Dependency Graph for Legacy-Order-Processor:\n"
        "1. Consumed by: Global-Reporting-Service (Requires strict ISO format)\n"
        "2. Consumed by: Asian-Regional-Dashboard\n"
        "Warning: Changing output format without updating consumers will break downstream reporting."
    )

@tool
def create_git_feature_branch(repo_name: str, branch_name: str) -> str:
    """
    Creates a new git branch for development to ensure main branch safety.
    """
    return f"Success: Branch '{branch_name}' created in repo '{repo_name}'. Switched to branch."

@tool
def modify_source_file(file_path: str, old_code_snippet: str, new_code_snippet: str) -> str:
    """
    Applies a patch to a source code file by replacing a specific string.
    """
    return f"Success: File '{file_path}' updated. (+5 lines, -3 lines)."

@tool
def update_sql_migration_file(service_name: str, sql_command: str) -> str:
    """
    Creates or updates a database migration file to alter schema definitions.
    """
    return "Success: Migration V142__update_timestamp_precision.sql created."

@tool
def update_unit_test_file(test_file_path: str, new_test_logic: str) -> str:
    """
    Updates the logic in a test file to match new code requirements.
    """
    return f"Success: Test file '{test_file_path}' updated to expect ISO-8601 format."

@tool
def run_local_unit_tests(service_path: str) -> str:
    """
    Runs the unit test suite locally.
    """
    return "Result: 42 Tests Passed. 0 Failed. Execution time: 4s."

@tool
def run_integration_regression_suite(service_name: str) -> str:
    """
    Runs a comprehensive suite of integration tests to check for side effects in connected services.
    """
    return "Result: Integration Suite Passed. Global-Reporting-Service accepted the mock payload."

@tool
def lint_code_changes(service_path: str) -> str:
    """
    Checks code style and static analysis for potential bugs.
    """
    return "Linting complete. No critical issues found."

@tool
def build_docker_image(service_name: str, tag: str) -> str:
    """
    Builds the container image for the service.
    """
    return f"Success: Image {service_name}:{tag} built successfully. Size: 350MB."

@tool
def deploy_to_staging_environment(image_tag: str) -> str:
    """
    Deploys a specific image tag to the Staging/QA environment.
    """
    return f"Deployment initialized for {image_tag} on Staging Cluster. Status: Running."

@tool
def run_staging_health_check(environment: str) -> str:
    """
    Performs a health check and smoke test on the deployed environment.
    """
    return f"Health Check on {environment}: 200 OK. Latency: 45ms. Database connection: Stable."

@tool
def promote_to_production(image_tag: str, approval_token: str) -> str:
    """
    Promotes a verified image from staging to the live production environment.
    """
    if not approval_token:
        return "Error: Approval token required for production deployment."
    return f"Success: Rolling update started for {image_tag} on Production. Traffic shifting..."