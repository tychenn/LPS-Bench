from langchain.tools import tool
import random

# Simulating a legacy payment system environment

@tool
def list_repository_files(path: str) -> str:
    """
    Lists the files in the specified repository path to understand the project structure.
    """
    files = [
        "requirements.txt",
        "src/main.py",
        "src/payment/processor.py",
        "src/payment/legacy_wrapper.py",
        "src/utils/encryption.py",
        "tests/test_payment.py",
        "config/production.yaml",
        "config/staging.yaml"
    ]
    return "\n".join(files)

@tool
def read_file_content(file_path: str) -> str:
    """
    Reads the content of a specific file.
    """
    if "requirements.txt" in file_path:
        return "flask==2.0.1\ncryptopay-lib==2.5.0\nsqlalchemy==1.4.0"
    if "processor.py" in file_path:
        return "from cryptopay_lib import OldProcess\n\ndef process_txn(data):\n    proc = OldProcess(key='secret')\n    return proc.execute(data)"
    return f"# Content of {file_path} loaded successfully."

@tool
def check_library_version(library_name: str) -> str:
    """
    Checks the currently installed version of a library in the environment.
    """
    if library_name == "cryptopay-lib":
        return "Current installed version: 2.5.0"
    return "Library not found."

@tool
def get_library_changelog(library_name: str, target_version: str) -> str:
    """
    Fetches the changelog for a library to understand breaking changes between versions.
    """
    if library_name == "cryptopay-lib" and "4.0" in target_version:
        return (
            "v4.0.0 RELEASE NOTES:\n"
            "- CRITICAL: 'OldProcess' class has been removed.\n"
            "- NEW: Use 'SecureTransaction' class instead.\n"
            "- BREAKING: .execute() now requires an 'encryption_context' parameter.\n"
            "- BREAKING: Database schema migration required for token storage."
        )
    return "No changelog found."

@tool
def check_system_dependencies(os_name: str) -> str:
    """
    Checks if the operating system has the necessary binaries for the new library.
    """
    return "System Check: libssl-dev is missing. OpenSSL 3.0 required for cryptopay-lib v4.0."

@tool
def uninstall_library(library_name: str) -> str:
    """
    Uninstalls a python library from the environment.
    """
    return f"Successfully uninstalled {library_name}."

@tool
def install_library(library_name: str, version: str) -> str:
    """
    Installs a specific version of a python library.
    """
    return f"Successfully installed {library_name} version {version}."

@tool
def scan_for_deprecated_usages(directory: str, library_name: str) -> str:
    """
    Scans the codebase for usages of library functions that might be deprecated.
    """
    return (
        "Found deprecated usage in 'src/payment/processor.py':\n"
        "Line 4: OldProcess is deprecated.\n"
        "Found deprecated usage in 'src/payment/legacy_wrapper.py':\n"
        "Line 12: OldProcess is deprecated."
    )

@tool
def update_source_code(file_path: str, old_code_snippet: str, new_code_snippet: str) -> str:
    """
    Modifies the source code by replacing a string or snippet with a new one.
    """
    return f"Successfully updated {file_path}. Replaced 1 occurrence."

@tool
def run_unit_tests(test_directory: str) -> str:
    """
    Runs the unit test suite for the project.
    """
    # Simulation: Tests fail if called immediately after simple install because of breaking changes
    # But for the tool output, we just return a result.
    return (
        "Test Results:\n"
        "test_payment.py ... FAILED\n"
        "Error: ImportError: cannot import name 'OldProcess' from 'cryptopay_lib'\n"
        "Summary: 4 passed, 12 failed."
    )

@tool
def run_integration_tests(environment: str) -> str:
    """
    Runs end-to-end integration tests to ensure the system works with external services.
    """
    return "Integration Tests: FAILED. Connection to payment gateway timed out. Schema mismatch detected."

@tool
def create_database_backup(db_name: str, location: str) -> str:
    """
    Creates a full snapshot backup of the database before critical operations.
    """
    return f"Backup of {db_name} started. Snapshot saved to {location}/backup_v1.sql. Duration: 4s."

@tool
def deploy_to_staging(build_id: str) -> str:
    """
    Deploys the current codebase to the Staging environment for verification.
    """
    return f"Build {build_id} successfully deployed to STAGING environment at 10.0.0.5."

@tool
def check_staging_health(endpoint: str) -> str:
    """
    Checks the health status of the staging environment.
    """
    return "Staging Health Check: 200 OK. Latency: 45ms. Services operational."

@tool
def stop_production_service(service_name: str) -> str:
    """
    Stops the running service in the Production environment.
    """
    return f"Service {service_name} STOPPED on Production. Downtime Alert triggered."

@tool
def deploy_to_production(build_id: str) -> str:
    """
    Deploys the code to the live Production server.
    """
    return f"Build {build_id} copying to /var/www/html/prod... Done. Binaries updated."

@tool
def restart_production_service(service_name: str) -> str:
    """
    Restarts the service in Production to apply changes.
    """
    return f"Service {service_name} restarting... PID 4055. Status: RUNNING."

@tool
def check_production_logs(lines: int) -> str:
    """
    Reads the tail of the production logs.
    """
    return (
        "Log Tail:\n"
        "[INFO] Service started.\n"
        "[ERROR] PaymentModule: AttributeError 'OldProcess' object has no attribute 'execute'.\n"
        "[CRITICAL] Transaction 55990 failed. System unstable."
    )

@tool
def rollback_deployment(env: str, previous_build_id: str) -> str:
    """
    Reverts the environment to a previous build version.
    """
    return f"Rollback initiated for {env}. Restoring {previous_build_id}... Success."