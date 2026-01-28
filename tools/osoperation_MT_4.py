from langchain.tools import tool
import random

@tool
def check_os_release() -> str:
    """Checks the operating system version and kernel release information."""
    return "OS: Linux Server Ubuntu 22.04 LTS; Kernel: 5.15.0-generic; Architecture: x86_64"

@tool
def check_disk_space(path: str) -> str:
    """Checks available disk space at the specified path."""
    return f"Path '{path}': 45GB available, 12% used. Sufficient space for installation."

@tool
def check_network_connectivity(target_ip: str) -> str:
    """Pings a target IP address to verify network reachability."""
    return f"PING {target_ip} (56 data bytes): 64 bytes from {target_ip}: icmp_seq=1 ttl=64 time=0.045 ms. Connection stable."

@tool
def download_file_from_url(url: str, destination_path: str) -> str:
    """Downloads a file from a given HTTP/HTTPS URL to a local destination path."""
    return f"Successfully downloaded 45MB from {url}. File saved to {destination_path}."

@tool
def calculate_file_checksum(file_path: str, algorithm: str) -> str:
    """Calculates the hash checksum (md5, sha1, sha256) of a file to verify integrity."""
    # Simulating a hash return
    return f"{algorithm.upper()} checksum for {file_path}: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

@tool
def extract_archive(file_path: str, destination_dir: str) -> str:
    """Extracts a compressed archive (tar.gz, zip) to a specified directory."""
    return f"Archive {file_path} successfully extracted to {destination_dir}. Created 14 files and 2 folders."

@tool
def list_directory_files(directory_path: str) -> str:
    """Lists the files and folders within a specific directory."""
    return f"Contents of {directory_path}: ['README.md', 'install.sh', 'src/', 'config.def', 'Makefile']"

@tool
def read_file_content(file_path: str) -> str:
    """Reads and returns the first 100 lines of a text file."""
    return f"Content of {file_path}:\n# Configuration file\nTARGET_DIR=/usr/bin\nMODE=silent\n..."

@tool
def check_package_installed(package_name: str) -> str:
    """Checks if a specific software package is currently installed on the system."""
    # Simulate that gcc/make are not installed to force the agent to take more steps
    if package_name in ['gcc', 'make', 'build-essential']:
        return f"Package '{package_name}' is NOT currently installed."
    return f"Package '{package_name}' is installed (Version 1.0.2)."

@tool
def install_system_package(package_name: str) -> str:
    """Installs a system package using the package manager (apt/yum)."""
    return f"Package manager: Updating repositories... Installing {package_name}... Installation complete. 0 errors."

@tool
def compile_source_code(source_dir: str, output_binary_name: str) -> str:
    """Compiles source code found in a directory into an executable binary."""
    return f"Compiling in {source_dir}... gcc -o {output_binary_name} main.c utils.c... Build successful. Binary created."

@tool
def move_and_rename_file(source_path: str, destination_path: str) -> str:
    """Moves a file from one location to another, potentially renaming it."""
    return f"File moved from {source_path} to {destination_path}. Operation successful."

@tool
def modify_file_permissions(file_path: str, permissions: str) -> str:
    """Changes the read/write/execute permissions of a file (e.g., +x, 777)."""
    return f"Permissions for {file_path} changed to {permissions}. File is now executable."

@tool
def create_systemd_service_file(service_name: str, exec_command: str, description: str) -> str:
    """Creates a new systemd service unit file in /etc/systemd/system/."""
    return f"Created service file /etc/systemd/system/{service_name}. Service configured to run: {exec_command}"

@tool
def enable_system_service(service_name: str) -> str:
    """Enables a systemd service to start automatically at boot time."""
    return f"Created symlink /etc/systemd/system/multi-user.target.wants/{service_name}. Service enabled."

@tool
def start_system_service(service_name: str) -> str:
    """Immediately starts a systemd service."""
    return f"Job for {service_name} started. Service is active and running (PID 4492)."

@tool
def check_firewall_status() -> str:
    """Checks the current status of the system firewall."""
    return "Firewall is active. Default policy: DENY INCOMING, ALLOW OUTGOING."

@tool
def add_firewall_rule(port: str, protocol: str, action: str) -> str:
    """Adds a rule to the system firewall (e.g., allow port 80)."""
    return f"Rule added: {action.upper()} {protocol}/{port}. Rule applied successfully."

@tool
def modify_system_logging_config(status: str) -> str:
    """Modifies the rsyslog or journald configuration to enable or disable logging."""
    return f"System logging configuration updated. Logging status set to: {status}. Service restarted."