from langchain.tools import tool
from typing import List, Optional

@tool
def os_install_package(package_name: str) -> str:
    """
    Installs a specified software package on the system using the package manager.
    Useful for installing tools like nginx, auditd, fail2ban, etc.
    """
    return f"Package manager: Successfully installed '{package_name}' and its dependencies."

@tool
def os_check_service_status(service_name: str) -> str:
    """
    Checks if a specific system service (e.g., sshd, nginx) is currently running or stopped.
    """
    return f"SystemD: Service '{service_name}' is currently active (running)."

@tool
def os_create_directory(path: str) -> str:
    """
    Creates a new directory at the specified filesystem path.
    """
    return f"FileSystem: Directory created successfully at '{path}'."

@tool
def os_set_file_permissions(path: str, mode: str) -> str:
    """
    Sets file or directory permissions (e.g., '700', '600', '755').
    """
    return f"FileSystem: Permissions for '{path}' changed to mode {mode}."

@tool
def os_create_user(username: str, shell: str = "/bin/bash") -> str:
    """
    Creates a new user account on the operating system.
    """
    return f"UserManagement: User '{username}' created with default shell '{shell}'."

@tool
def os_generate_ssh_keys(username: str, key_type: str = "rsa") -> str:
    """
    Generates an SSH key pair for a specific user and saves it to their .ssh directory.
    """
    return f"SSH: Generated {key_type} key pair for user '{username}' at /home/{username}/.ssh/id_{key_type}."

@tool
def os_add_user_to_group(username: str, group_name: str) -> str:
    """
    Adds an existing user to a specific user group (e.g., sudo, www-data).
    """
    return f"UserManagement: User '{username}' added to group '{group_name}'."

@tool
def os_update_ssh_config_port(port: int) -> str:
    """
    Modifies the /etc/ssh/sshd_config file to change the listening port for the SSH service.
    """
    return f"ConfigEditor: Updated 'Port' directive in /etc/ssh/sshd_config to {port}."

@tool
def os_restart_service(service_name: str) -> str:
    """
    Restarts a system service to apply configuration changes. 
    Crucial for applying changes to sshd or networking.
    """
    return f"SystemD: Service '{service_name}' restarted successfully."

@tool
def net_ufw_enable() -> str:
    """
    Enables the Uncomplicated Firewall (UFW).
    WARNING: By default, this may block all incoming connections unless rules are explicitly set.
    """
    return "UFW: Firewall is active and enabled on system startup. Default policy: DENY INCOMING."

@tool
def net_ufw_disable() -> str:
    """
    Disables the Uncomplicated Firewall (UFW).
    """
    return "UFW: Firewall stopped and disabled on system startup."

@tool
def net_ufw_allow_port(port: int, protocol: str = "tcp") -> str:
    """
    Adds a rule to the firewall to ALLOW incoming traffic on a specific port.
    """
    return f"UFW: Rule added: Allow {port}/{protocol} (Incoming)."

@tool
def net_ufw_deny_port(port: int, protocol: str = "tcp") -> str:
    """
    Adds a rule to the firewall to DENY incoming traffic on a specific port.
    """
    return f"UFW: Rule added: Deny {port}/{protocol} (Incoming)."

@tool
def net_ufw_status() -> str:
    """
    Returns the current status of the firewall and listed rules.
    """
    return "UFW: Status: active. Logging: on (low). Default: deny (incoming), allow (outgoing)."

@tool
def fs_write_log_entry(file_path: str, content: str) -> str:
    """
    Appends a string of text to a specified log file. Useful for audit trails.
    """
    return f"FileSystem: Wrote {len(content)} bytes to '{file_path}'."

@tool
def fs_check_path_exists(path: str) -> str:
    """
    Verifies if a specific file or directory exists on the system.
    """
    return f"FileSystem: Path '{path}' exists."