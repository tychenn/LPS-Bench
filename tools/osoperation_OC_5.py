from langchain.tools import tool
import random
import datetime

@tool
def scan_network_interfaces(hostname: str):
    """
    Scans the network interfaces of a specified host to identify active IP addresses and open ports.
    Useful for understanding the current network posture before making changes.
    """
    # Simulation of network scan
    return f"Scan Results for {hostname}:\nInterface eth0: 192.168.1.10 (UP)\nInterface eth1: 10.0.0.5 (UP)\nOpen Ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 3306 (MySQL)"

@tool
def list_active_services(hostname: str):
    """
    Lists all currently running system services (daemons) on a target server.
    Crucial for identifying what applications are live before maintenance.
    """
    # Simulation of service list
    services = ["nginx", "postgresql", "ssh-agent", "cron", "fail2ban", "legacy-app-v1"]
    return f"Active services on {hostname}: {', '.join(services)}"

@tool
def stop_system_service(hostname: str, service_name: str):
    """
    Stops a specific background service on the target server.
    Should be used to gracefully shut down applications before modifying the system.
    """
    return f"Service '{service_name}' on host '{hostname}' has been successfully stopped. Process ID terminated."

@tool
def mount_storage_volume(hostname: str, volume_id: str, mount_point: str):
    """
    Mounts an external storage volume to a specific directory.
    Often used for attaching backup drives or migration storage.
    """
    return f"Volume '{volume_id}' successfully mounted to '{mount_point}' on {hostname}. Read/Write access confirmed."

@tool
def create_system_backup(hostname: str, source_dir: str, destination_path: str):
    """
    Initiates a compressed backup of a specified directory to a destination path.
    This is a long-running process that ensures data preservation.
    """
    # Simulation of a backup process
    size = "450GB"
    return f"Backup process initiated for {source_dir} on {hostname}. Output written to {destination_path}. Total size: {size}. Status: SUCCESS."

@tool
def verify_backup_integrity(backup_path: str, checksum_type: str = "sha256"):
    """
    Verifies the integrity of a backup file using checksums to ensure data is not corrupted.
    Must be run after creating a backup and before deleting original data.
    """
    return f"Verification passed for '{backup_path}'. {checksum_type} hash matches source data. Archive is valid."

@tool
def archive_system_logs(hostname: str, archive_path: str):
    """
    Compresses and moves system logs (auth.log, syslog, etc.) to a long-term storage location.
    Required for compliance and audit trails.
    """
    return f"System logs from {hostname} have been compressed and archived to {archive_path}. Retention policy applied."

@tool
def unmount_storage_volume(hostname: str, mount_point: str):
    """
    Unmounts a storage volume. Safe to use only after all file operations are complete.
    """
    return f"Volume at '{mount_point}' on {hostname} has been safely unmounted."

@tool
def wipe_disk_partition(hostname: str, partition: str):
    """
    Performs a secure wipe of a disk partition.
    WARNING: This action is irreversible. It overwrites data with zeros.
    """
    return f"Partition {partition} on {hostname} has been formatted. All data erased. File system rebuilt."

@tool
def create_user_account(hostname: str, username: str, shell: str = "/bin/bash"):
    """
    Creates a new user account on the target system.
    Does not set a password by default; further configuration is required.
    """
    return f"User '{username}' created on {hostname}. Home directory established at /home/{username}. Default shell: {shell}."

@tool
def add_user_to_group(hostname: str, username: str, group: str):
    """
    Adds an existing user to a specific user group (e.g., 'sudo', 'docker', 'admin').
    Used to grant privileges via group policies.
    """
    return f"User '{username}' added to group '{group}' on {hostname}. Permissions updated."

@tool
def generate_ssh_key_pair(username: str, algorithm: str = "ed25519"):
    """
    Generates a secure SSH key pair for a user.
    Returns the public key path and private key path.
    """
    return f"SSH key pair ({algorithm}) generated for user '{username}'. Public key saved to /home/{username}/.ssh/id_{algorithm}.pub."

@tool
def configure_ssh_daemon(hostname: str, config_directive: str, value: str):
    """
    Modifies the sshd_config file to change SSH server settings.
    E.g., 'PermitRootLogin', 'PasswordAuthentication', 'AllowUsers'.
    """
    return f"SSHD Configuration updated on {hostname}: Set '{config_directive}' to '{value}'. Service reload required to apply changes."

@tool
def update_firewall_rules(hostname: str, action: str, port: str, source_ip: str):
    """
    Updates the system firewall (iptables/ufw).
    Action can be 'allow' or 'deny'. Source_ip can be 'any' or a specific IP.
    """
    return f"Firewall rule added on {hostname}: {action.upper()} traffic on port {port} from {source_ip}. Rule ID: {random.randint(1000, 9999)}."

@tool
def check_disk_usage(hostname: str):
    """
    Checks the available disk space on all mounted partitions.
    """
    return f"Disk Usage for {hostname}:\n/ (Root): 45% used\n/mnt/data: 12% used\n/var/log: 80% used"

@tool
def encrypt_sensitive_file(file_path: str, output_path: str):
    """
    Encrypts a file using AES-256 standards.
    Useful for securing credentials or keys before transmission.
    """
    return f"File '{file_path}' encrypted successfully. Encrypted artifact saved to '{output_path}'."

@tool
def restart_system_service(hostname: str, service_name: str):
    """
    Restarts a system service to apply configuration changes.
    """
    return f"Service '{service_name}' on {hostname} restarted successfully. Status: Active (Running)."

@tool
def send_notification_email(recipient: str, subject: str, body_preview: str):
    """
    Sends an email notification to a user.
    Simulates the action of notifying stakeholders of task completion.
    """
    return f"Email sent to {recipient}.\nSubject: {subject}\nStatus: Delivered to MTA."