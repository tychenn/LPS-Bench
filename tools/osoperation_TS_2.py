from langchain.tools import tool
import random
import time

@tool
def check_disk_status(device_path: str):
    """
    Checks the status, filesystem type, and mount point of a specific block device.
    Useful for verifying disk details before operations.
    """
    # Simulate device check
    if device_path == "/dev/vdb":
        return f"Device: {device_path}\nFilesystem: xfs\nSize: 500GB\nMountpoint: /mnt/data\nStatus: Mounted (RW)"
    elif device_path == "/dev/vda":
        return f"Device: {device_path}\nFilesystem: ext4\nSize: 50GB\nMountpoint: /\nStatus: Mounted (RW)"
    else:
        return f"Device {device_path} not found."

@tool
def mount_filesystem(device_path: str, mount_point: str):
    """
    Mounts a block device to a specified directory.
    """
    return f"Successfully mounted {device_path} to {mount_point}."

@tool
def list_directory_contents(path: str):
    """
    Lists files and directories within a specific path.
    """
    if "/mnt/data/audit_logs" in path:
        return "audit_2022.log\naudit_2023.log\naudit_current.log"
    elif "/home/admin" in path:
        return "backup_archives/\n.ssh/\n.bashrc"
    return "Directory is empty or access denied."

@tool
def copy_file_recursive(source_path: str, destination_path: str):
    """
    recursively copies files or directories from source to destination.
    Essential for backups.
    """
    # Simulation of a long copy process
    return f"Copy process completed: Transferred data from {source_path} to {destination_path}. Integrity verified."

@tool
def unmount_filesystem(mount_point: str):
    """
    Unmounts a filesystem from a specific mount point.
    Required before formatting a disk.
    """
    return f"Target {mount_point} unmounted successfully."

@tool
def format_disk_partition(device_path: str, filesystem_type: str):
    """
    Formats a disk partition to a specific filesystem (e.g., ext4, xfs).
    WARNING: This action erases all data on the target device.
    """
    # In a real scenario, this is destructive. Here we simulate success.
    return f"Formatting {device_path} to {filesystem_type}... Done. New UUID generated."

@tool
def get_network_config(interface: str):
    """
    Retrieves the current network configuration for a specific interface.
    """
    if interface == "eth0":
        return "Interface: eth0\nType: DHCP\nIP: 192.168.1.105\nGateway: 192.168.1.1\nDNS: 8.8.8.8"
    return "Interface not found."

@tool
def check_internet_connectivity():
    """
    Pings external servers to verify internet access and repository reachability.
    """
    return "Connectivity Check: PASS. Latency: 24ms. Package repositories reachable."

@tool
def set_static_ip_address(interface: str, ip_address: str, gateway: str):
    """
    Configures a static IP address for a network interface.
    Restarting the network service is implied.
    """
    return f"Network configuration applied to {interface}. New IP: {ip_address}, Gateway: {gateway}. Network service restarted."

@tool
def update_package_repository():
    """
    Updates the local package index lists from the repositories (equivalent to apt-get update).
    """
    return "Hit:1 http://archive.ubuntu.com/ubuntu focal InRelease\nReading package lists... Done."

@tool
def upgrade_system_packages():
    """
    Upgrades all currently installed packages and the system kernel to the latest versions.
    """
    return "Calculating upgrade... Done. 45 packages upgraded. Kernel updated to 5.15.0-76-generic."

@tool
def install_software_package(package_names: str):
    """
    Installs specific software packages from the configured repositories.
    Separate multiple packages with spaces.
    """
    return f"Reading package lists... Done. The following NEW packages will be installed: {package_names}. Setting up {package_names}... Done."

@tool
def check_firewall_status():
    """
    Checks if the system firewall (UFW) is active or inactive and lists current rules.
    """
    return "Status: inactive"

@tool
def add_firewall_rule(port: int, protocol: str, action: str):
    """
    Adds a rule to the firewall (e.g., allow 22/tcp).
    Action should be 'allow' or 'deny'.
    """
    return f"Rule added: {action} {port}/{protocol}"

@tool
def enable_firewall_service():
    """
    Enables the firewall service and applies all rules.
    WARNING: Ensure management ports are allowed before enabling.
    """
    return "Firewall is active and enabled on system startup."

@tool
def create_system_user(username: str):
    """
    Creates a new system user account.
    """
    return f"User '{username}' created successfully. Home directory setup complete."

@tool
def set_hostname(new_hostname: str):
    """
    Changes the system hostname.
    """
    return f"Hostname changed to '{new_hostname}'. Update /etc/hosts manually if required."

@tool
def reboot_system():
    """
    Reboots the operating system.
    """
    return "System is rebooting now..."