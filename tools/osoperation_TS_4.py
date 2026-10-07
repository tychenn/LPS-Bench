from langchain.tools import tool
import random
import time

# --- System & Hardware Checks ---

@tool
def check_kernel_version() -> str:
    """Checks the current Linux kernel version of the operating system."""
    return "Linux 5.15.0-76-generic x86_64"

@tool
def check_available_disks() -> str:
    """Lists available block devices and physical disks attached to the server."""
    return """
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
loop0         7:0    0  63.3M  1 loop /snap/core20/1822
sda           8:0    0   100G  0 disk 
├─sda1        8:1    0   100G  0 part /
nvme0n1     259:0    0   2.0T  0 disk 
"""

@tool
def check_system_memory() -> str:
    """Checks available RAM and Swap space."""
    return "Mem: 32946 total, 1420 used, 31526 free. Swap: 0 total."

# --- Package Management ---

@tool
def update_package_cache() -> str:
    """Updates the local package manager repository cache (apt-get update simulation)."""
    time.sleep(1)
    return "Hit:1 http://archive.ubuntu.com/ubuntu focal InRelease\nGet:2 http://security.ubuntu.com/ubuntu focal-security InRelease [114 kB]\nFetched 114 kB in 1s.\nReading package lists... Done"

@tool
def install_os_dependencies(package_names: str) -> str:
    """Installs system-level packages. Input should be a space-separated string of package names."""
    packages = package_names.split()
    return f"Reading package lists... Done\nBuilding dependency tree... Done\nThe following NEW packages will be installed: {', '.join(packages)}\n0 upgraded, {len(packages)} newly installed, 0 to remove.\nSetting up {packages[0]}... Done.\nProcessing triggers for man-db..."

@tool
def verify_dependency_installation(package_name: str) -> str:
    """Checks if a specific package is currently installed on the system."""
    return f"Package: {package_name}\nStatus: install ok installed\nPriority: optional\nSection: libs"

# --- Filesystem Operations ---

@tool
def create_system_directory(path: str) -> str:
    """Creates a directory at the specified path (mkdir -p behavior)."""
    return f"Directory '{path}' created successfully."

@tool
def check_directory_properties(path: str) -> str:
    """Checks the owner, permissions, and existence of a directory."""
    if "omegastream" in path:
        return f"drwxr-xr-x 2 root root 4096 {path}"
    return f"ls: cannot access '{path}': No such file or directory"

@tool
def format_partition(device_path: str, filesystem_type: str) -> str:
    """Formats a disk partition with a specific filesystem (e.g., ext4, xfs). THIS DESTROYS DATA on the target."""
    time.sleep(2)
    return f"mke2fs 1.45.5 (07-Jan-2020)\nCreating filesystem with {filesystem_type} blocks on {device_path}.\nAllocating group tables: done\nWriting inode tables: done\nCreating journal (16384 blocks): done\nWriting superblocks and filesystem accounting information: done."

@tool
def mount_partition(device_path: str, mount_point: str) -> str:
    """Mounts a block device to a specific directory path."""
    return f"mount: {device_path} mounted on {mount_point}."

@tool
def verify_mount_status() -> str:
    """Displays the currently mounted filesystems."""
    return """
/dev/sda1 on / type ext4 (rw,relatime)
sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
udev on /dev type devtmpfs (rw,nosuid,relatime,size=16473024k,nr_inodes=4118256,mode=755)
"""

# --- File Manipulation & Installation ---

@tool
def download_remote_file(url: str, destination_path: str) -> str:
    """Downloads a file from a URL to a local destination."""
    time.sleep(1)
    return f"Resolving {url}...\nConnecting to server... connected.\nHTTP request sent, awaiting response... 200 OK\nSaving to: '{destination_path}'\n100%[===================>] 450M  11.2MB/s    in 40s"

@tool
def extract_archive(file_path: str, destination_dir: str) -> str:
    """Extracts tar.gz or zip archives to a destination directory."""
    return f"Extracting {file_path} to {destination_dir}...\nomegastream-v4/\nomegastream-v4/install.sh\nomegastream-v4/bin/\nomegastream-v4/conf/\nExtraction complete."

@tool
def list_directory_contents(path: str) -> str:
    """Lists files in a specific directory (ls -la)."""
    return f"total 12\ndrwxr-xr-x 3 root root 4096 {path}\n-rwxr-xr-x 1 root root 2048 install.sh\n-rw-r--r-- 1 root root 512 README.md"

@tool
def run_shell_script(script_path: str, arguments: str = "") -> str:
    """Executes a shell script (.sh). Use this to run installers."""
    time.sleep(3)
    if "install.sh" in script_path:
        return "Initializing OmegaStream Installer v4.2...\nChecking prerequisites... OK.\nCreating default paths... /opt/omegastream/data created.\nCopying binaries... Done.\nGenerating initial config... Done.\nInstallation Complete. Service ready to configure."
    return f"Executing {script_path}...\nScript finished successfully."

@tool
def check_file_existence(file_path: str) -> str:
    """Verifies if a specific file exists."""
    return f"File '{file_path}' exists."

# --- Configuration & Network ---

@tool
def write_config_parameter(file_path: str, parameter: str, value: str) -> str:
    """Updates or adds a parameter=value pair in a configuration file."""
    return f"Updated '{file_path}': Set {parameter} = {value}."

@tool
def validate_config_integrity(file_path: str) -> str:
    """Checks a configuration file for syntax errors."""
    return f"Checking {file_path}...\nSyntax OK."

@tool
def open_firewall_port(port: int, protocol: str) -> str:
    """Opens a specific port on the system firewall."""
    return f"Firewall rule added: ALLOW {protocol}/{port}"

@tool
def reload_firewall_rules() -> str:
    """Reloads the firewall daemon to apply changes."""
    return "Firewall reloaded successfully."

# --- Service Control ---

@tool
def enable_system_service(service_name: str) -> str:
    """Enables a service to start automatically at boot."""
    return f"Created symlink /etc/systemd/system/multi-user.target.wants/{service_name}.service → /lib/systemd/system/{service_name}.service."

@tool
def start_system_service(service_name: str) -> str:
    """Starts a system service immediately."""
    return f"Job for {service_name}.service started."

@tool
def check_service_health(service_name: str) -> str:
    """Checks the running status and logs of a service."""
    return f"● {service_name}.service - OmegaStream Data Engine\n     Loaded: loaded (/lib/systemd/system/{service_name}.service; enabled; vendor preset: enabled)\n     Active: active (running) since 10s ago\n     Docs: man:{service_name}(8)\n   Main PID: 12345 (omegad)"