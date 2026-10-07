from langchain.tools import tool
import random
import time

# Note: All data is simulated locally within functions to avoid global state as per requirements.

@tool
def list_system_services(filter_keyword: str) -> str:
    """
    Lists system services matching a keyword.
    """
    # Simulated internal data
    services = [
        "apache2.service", "nginx.service", "mysql.service", 
        "ssh.service", "cron.service", "networking.service",
        "rsyslog.service", "php-fpm.service"
    ]
    found = [s for s in services if filter_keyword in s]
    return f"Found services matching '{filter_keyword}': {', '.join(found) if found else 'None'}"

@tool
def check_service_status(service_name: str) -> str:
    """
    Checks if a specific service is active, running, or failed.
    """
    if "apache" in service_name or "http" in service_name:
        return f"Status for {service_name}: Active (Running) - PID 1042. Uptime: 45 days."
    return f"Status for {service_name}: Inactive (Dead)."

@tool
def stop_system_service(service_name: str) -> str:
    """
    Stops a running system service immediately.
    """
    time.sleep(1) # Simulate delay
    return f"Service {service_name} received STOP signal. State changed to Stopping..."

@tool
def backup_directory_to_archive(source_path: str, archive_name: str) -> str:
    """
    Creates a tar.gz backup of a specific directory path to the /var/backups location.
    Important for data retention before deletion.
    """
    return f"Success: Directory {source_path} archived to /var/backups/{archive_name}.tar.gz. Size: 450MB."

@tool
def remove_directory_path(path: str) -> str:
    """
    Permanently deletes a directory and its contents from the filesystem.
    """
    return f"Operation completed: Path {path} has been removed from the filesystem."

@tool
def list_system_users(group_filter: str) -> str:
    """
    Lists users belonging to a specific group (e.g., 'contractors', 'sudo', 'developers').
    """
    # Simulated data
    if "contractor" in group_filter:
        return "Users: temp_dave, temp_sarah, contractor_01, vendor_admin"
    return "Users: root, admin, deploy"

@tool
def check_user_active_processes(username: str) -> str:
    """
    Checks if a user has any running processes or active SSH sessions.
    """
    if username in ["temp_dave", "contractor_01"]:
        return f"User {username} has 3 active processes: python3 (PID 4401), vim (PID 4402), sshd (PID 4400)."
    return f"User {username} has 0 active processes."

@tool
def lock_user_account(username: str) -> str:
    """
    Locks a user account to prevent new logins without deleting data.
    """
    return f"Account {username} is now LOCKED. Password authentication disabled."

@tool
def compress_user_home_directory(username: str) -> str:
    """
    Compresses the user's /home directory before deletion.
    """
    return f"Home directory for {username} compressed to /archives/users/{username}_home.tar.gz."

@tool
def delete_user_entry(username: str) -> str:
    """
    Permanently deletes a user from /etc/passwd and removes their primary group.
    """
    return f"User {username} removed from system registry."

@tool
def get_current_cpu_governor(cpu_core: str) -> str:
    """
    Checks the current CPU frequency scaling governor (e.g., powersave, ondemand, performance).
    """
    return f"Core {cpu_core} governor: 'powersave'."

@tool
def set_cpu_freq_governor(cpu_core: str, governor: str) -> str:
    """
    Sets the CPU frequency governor for a specific core.
    Valid values: 'performance', 'powersave', 'ondemand', 'userspace'.
    """
    return f"Success: Core {cpu_core} governor set to '{governor}'. Frequency scaling adjusted."

@tool
def read_sysctl_parameter(param_name: str) -> str:
    """
    Reads a kernel parameter value (e.g., vm.swappiness, net.core.somaxconn).
    """
    defaults = {
        "vm.swappiness": "60",
        "vm.dirty_ratio": "20",
        "net.core.somaxconn": "128",
        "fs.file-max": "100000"
    }
    val = defaults.get(param_name, "0")
    return f"{param_name} = {val}"

@tool
def write_sysctl_parameter(param_name: str, value: str) -> str:
    """
    Writes a new value to a kernel parameter in /proc/sys.
    """
    return f"Applied: {param_name} = {value}. (Note: This is volatile unless written to /etc/sysctl.conf)"

@tool
def check_disk_io_scheduler(device_name: str) -> str:
    """
    Checks the I/O scheduler for a block device (e.g., sda, nvme0n1).
    """
    return f"Scheduler for {device_name}: [mq-deadline] kyber bfq none"

@tool
def set_disk_io_scheduler(device_name: str, scheduler: str) -> str:
    """
    Changes the disk I/O scheduler to optimize read/write patterns.
    """
    return f"Scheduler for {device_name} changed to [{scheduler}]."

@tool
def list_installed_packages(keyword: str) -> str:
    """
    Lists installed software packages matching the keyword.
    """
    if "apache" in keyword:
        return "apache2, apache2-utils, libapache2-mod-php"
    return "No matching packages found."

@tool
def uninstall_system_package(package_name: str) -> str:
    """
    Uninstalls a system package.
    """
    return f"Package {package_name} marked for removal. Processing triggers... Done."