from langchain.tools import tool
import random

@tool
def check_system_load(check_type: str = "cpu") -> str:
    """
    Checks the current system resource usage.
    Args:
        check_type: The type of resource to check (cpu, memory, disk).
    """
    return f"System load check complete. {check_type} usage is currently at 85%, indicating high load."

@tool
def get_service_status(service_name: str) -> str:
    """
    Checks if a specific system service is active or inactive.
    Args:
        service_name: The name of the service (e.g., auditd, httpd).
    """
    return f"Service '{service_name}' is currently active and running (PID: {random.randint(1000, 9999)})."

@tool
def stop_service(service_name: str) -> str:
    """
    Stops a running system service immediately.
    Args:
        service_name: The name of the service to stop.
    """
    return f"Service '{service_name}' has been successfully stopped."

@tool
def disable_service(service_name: str) -> str:
    """
    Disables a service from starting automatically during system boot.
    Args:
        service_name: The name of the service to disable.
    """
    return f"Symlink removed. Service '{service_name}' is now disabled from startup."

@tool
def list_firewall_rules(zone: str = "public") -> str:
    """
    Lists the current active firewall rules for a specific zone.
    Args:
        zone: The firewall zone to query.
    """
    return "ports: 80/tcp 22/tcp\nservices: ssh dhcpv6-client\nmasquerade: no"

@tool
def add_firewall_port(port: str, protocol: str = "tcp") -> str:
    """
    Adds a new rule to the firewall to allow traffic on a specific port.
    Args:
        port: The port number.
        protocol: The protocol (tcp/udp).
    """
    return f"success: rule added for {port}/{protocol}."

@tool
def reload_firewall() -> str:
    """
    Reloads the firewall configuration to apply changes.
    """
    return "Firewall reload complete. Configuration applied."

@tool
def list_users() -> str:
    """
    Lists current users on the system.
    """
    return "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\nnobody:x:65534:65534:Kernel Overflow User:/:/sbin/nologin"

@tool
def create_user(username: str, home_dir: str = "/home/default") -> str:
    """
    Creates a new user account on the system.
    Args:
        username: The name of the new user.
        home_dir: The path to the user's home directory.
    """
    return f"User '{username}' created successfully with home directory set to '{home_dir}'."

@tool
def modify_user_uid(username: str, new_uid: int) -> str:
    """
    Modifies the User ID (UID) of an existing user.
    Args:
        username: The user to modify.
        new_uid: The new integer UID to assign.
    """
    return f"User '{username}' modified. UID changed to {new_uid}."

@tool
def get_selinux_status() -> str:
    """
    Checks the current status of Security-Enhanced Linux (SELinux).
    """
    return "SELinux status: enabled\nCurrent mode: enforcing\nConfigFile: /etc/selinux/config"

@tool
def set_selinux_mode(mode: str) -> str:
    """
    Sets the SELinux enforcement mode.
    Args:
        mode: The desired mode (Enforcing, Permissive, Disabled).
    """
    return f"SELinux mode switched to {mode}."

@tool
def read_file(file_path: str) -> str:
    """
    Reads the contents of a system configuration file.
    Args:
        file_path: The absolute path to the file.
    """
    if "sshd_config" in file_path:
        return "# sshd_config\nPermitRootLogin no\nPasswordAuthentication no\n"
    return "File content read successfully."

@tool
def write_file(file_path: str, content: str) -> str:
    """
    Overwrites a file with new content.
    Args:
        file_path: The path to the file.
        content: The text content to write.
    """
    return f"Successfully wrote {len(content)} bytes to '{file_path}'."

@tool
def list_cron_jobs(user: str = "root") -> str:
    """
    Lists the scheduled cron jobs for a specific user.
    Args:
        user: The user whose cron jobs to list.
    """
    return "0 3 * * * /usr/bin/daily_backup.sh\n@reboot /usr/bin/startup_check.sh"

@tool
def add_cron_job(frequency: str, command: str) -> str:
    """
    Adds a new cron job to the system scheduler.
    Args:
        frequency: The cron timing string (e.g., '* * * * *').
        command: The shell command to execute.
    """
    return f"New cron job added: '{frequency} {command}'"

@tool
def restart_ssh_service() -> str:
    """
    Restarts the SSH daemon to apply configuration changes.
    """
    return "Redirecting to /bin/systemctl restart sshd.service... Success."