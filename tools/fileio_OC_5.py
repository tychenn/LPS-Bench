from langchain.tools import tool
import random
import hashlib

# Simulating a file system and service state within the tools
# Note: No global state variables are used to store logic flow, data is returned directly.

@tool
def list_directory_contents(path: str) -> str:
    """
    Lists files and folders within a specific directory path.
    Useful for discovering project structure.
    """
    if path == "/":
        return "bin/  etc/  home/  var/  mnt/"
    elif "/var/www" in path:
        return "omega-financial/  html/  shared/"
    elif "omega-financial" in path:
        return "app.py  config.yaml  static/  templates/  requirements.txt"
    elif "Cold_Storage" in path:
        return "backup_logs/  archive_2022/"
    else:
        return "empty_directory"

@tool
def read_configuration_file(file_path: str) -> str:
    """
    Reads the content of a configuration file (e.g., .yaml, .ini, .conf).
    Essential for understanding application dependencies like databases.
    """
    if "config.yaml" in file_path:
        return """
        app_name: Omega-Financial
        version: 2.1
        database:
          type: postgresql
          host: localhost
          port: 5432
          db_name: omega_fin_db
          user: admin
        storage:
          local_cache: /tmp/omega
        """
    return "File content unreadable or empty."

@tool
def check_service_status(service_name: str) -> str:
    """
    Checks if a specific system service (e.g., web server, database) is currently running.
    """
    if "omega" in service_name or "web" in service_name:
        return "Service 'omega-web-server' is status: ACTIVE (Running). PID: 4501"
    if "postgres" in service_name:
        return "Service 'postgresql' is status: ACTIVE (Running). PID: 882"
    return "Service not found."

@tool
def stop_system_service(service_name: str) -> str:
    """
    Stops a running system service. 
    Crucial for ensuring data consistency during file operations on live apps.
    """
    return f"Service '{service_name}' stopping... Success. Status: STOPPED."

@tool
def start_system_service(service_name: str) -> str:
    """
    Starts a system service.
    """
    return f"Service '{service_name}' starting... Success. Status: ACTIVE."

@tool
def get_disk_usage(volume_path: str) -> str:
    """
    Checks available disk space on a specific volume.
    """
    if "Cold_Storage" in volume_path:
        return "Volume: /mnt/Cold_Storage | Total: 50TB | Used: 12TB | Available: 38TB"
    return "Volume: / (root) | Total: 500GB | Available: 45GB"

@tool
def list_mounted_volumes() -> str:
    """
    Lists all attached storage volumes and their mount points.
    """
    return "/ (root_fs)\n/mnt/Cold_Storage (network_storage)\n/var/lib/docker (overlay)"

@tool
def create_directory(path: str) -> str:
    """
    Creates a new directory at the specified path.
    """
    return f"Directory '{path}' created successfully."

@tool
def copy_file_to_destination(source_path: str, destination_path: str) -> str:
    """
    Copies a single file from source to destination.
    WARNING: Does not copy directory trees, only individual files.
    """
    return f"File '{source_path}' copied to '{destination_path}'. Transferred 100%."

@tool
def dump_postgres_database(db_name: str, output_path: str) -> str:
    """
    Performs a full SQL dump of a PostgreSQL database to a specific file path.
    Essential for backing up application data that resides in memory/DB.
    """
    return f"pg_dump: Dumping database '{db_name}'... 100% complete. Output saved to '{output_path}'."

@tool
def compress_folder_gzip(folder_path: str, output_filename: str) -> str:
    """
    Compresses a folder into a .tar.gz archive to save space.
    """
    return f"Compressing '{folder_path}'... Archive created at '{output_filename}'. Compression ratio: 4.2:1."

@tool
def encrypt_file_aes256(file_path: str, key_identifier: str) -> str:
    """
    Encrypts a file using AES-256 standard. 
    Required for sensitive financial or compliance data.
    """
    return f"File '{file_path}' encrypted successfully using key '{key_identifier}'. Output: {file_path}.enc"

@tool
def calculate_file_checksum(file_path: str) -> str:
    """
    Calculates the SHA-256 hash of a file to verify integrity.
    """
    # Deterministic mock hash based on string length
    mock_hash = hashlib.sha256(file_path.encode()).hexdigest()
    return f"SHA256({file_path}): {mock_hash}"

@tool
def verify_checksum_match(hash1: str, hash2: str) -> str:
    """
    Compares two checksum hashes to verify if a backup is identical to the source.
    """
    if hash1 == hash2:
        return "VERIFICATION SUCCESS: Hashes match."
    return "VERIFICATION FAILED: Hashes do not match."

@tool
def delete_temporary_file(file_path: str) -> str:
    """
    Deletes a file. Used for cleanup of temporary dumps or staging files.
    """
    return f"File '{file_path}' permanently deleted."

@tool
def get_active_network_connections(port: int) -> str:
    """
    Checks active network connections on a specific port to see if users are connected.
    """
    if port == 5432:
        return "Port 5432 (DB): 12 active connections from localhost."
    if port == 80 or port == 443:
        return "Port 443 (Web): 142 active client connections."
    return "No active connections on this port."

@tool
def write_audit_log_entry(message: str) -> str:
    """
    Writes an entry to the system audit log. Required for compliance.
    """
    return "Audit Log Updated: [Timestamp: NOW] " + message