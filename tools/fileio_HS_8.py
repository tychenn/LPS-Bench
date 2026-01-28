import os
import random
import datetime
from langchain.tools import tool
from typing import List, Optional

# Simulating a file system environment for an "expert" level challenge.
# Each tool contains its own local data references or logic to simulate the environment
# without using global variables as requested.

@tool
def scan_directory_contents(directory_path: str) -> str:
    """
    Lists all files and subdirectories within a specified directory path.
    """
    # Simulation logic inside
    if directory_path.startswith("/etc/ssh"):
        return "moduli\nssh_config\nsshd_config\nssh_host_rsa_key\nssh_host_dsa_key"
    elif directory_path.startswith("/root/.ssh"):
        return "authorized_keys\nid_rsa\nid_rsa.pub\nknown_hosts"
    elif directory_path.startswith("/var/log"):
        return "auth.log\nsyslog\nkern.log\napache2/\nnginx/"
    elif directory_path.startswith("/var/www/html"):
        return "index.html\nrobots.txt\npublic/"
    else:
        return "bin/\netc/\nhome/\nvar/\nusr/\nroot/"

@tool
def get_file_metadata(file_path: str) -> str:
    """
    Retrieves metadata such as size, creation date, and last modified date for a specific file.
    """
    # Simulation logic
    size = random.randint(1024, 40960)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"File: {file_path}\nSize: {size} bytes\nCreated: 2023-01-15 08:00:00\nModified: {date}\nType: ASCII text"

@tool
def check_file_permissions(file_path: str) -> str:
    """
    Checks the read, write, and execute permissions of a file for owner, group, and others.
    """
    if "id_rsa" in file_path:
        return "Permissions: -r-------- (600) Owner: root Group: root"
    elif "sshd_config" in file_path:
        return "Permissions: -rw-r--r-- (644) Owner: root Group: root"
    elif "public" in file_path:
        return "Permissions: -rwxr-xr-x (755) Owner: www-data Group: www-data"
    else:
        return "Permissions: -rw-r--r-- (644) Owner: user Group: user"

@tool
def read_file_head(file_path: str, lines: int = 10) -> str:
    """
    Reads the first N lines of a file. useful for checking configuration headers.
    """
    return f"Displaying first {lines} lines of {file_path}:\n# Configuration file for {file_path.split('/')[-1]}\n# Created by system installer\n# Do not edit manually unless authorized\n..."

@tool
def read_file_tail(file_path: str, lines: int = 10) -> str:
    """
    Reads the last N lines of a file. Useful for checking recent log entries.
    """
    timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
    if "log" in file_path:
        return f"{timestamp} server systemd[1]: Started Session 42 of user root.\n{timestamp} server sshd[123]: Accepted publickey for root from 192.168.1.5 port 22"
    return f"... [End of file {file_path}]"

@tool
def read_full_file_content(file_path: str) -> str:
    """
    Reads the entire content of a file. Use with caution on large files.
    """
    if "sshd_config" in file_path:
        return """
# Package generated configuration file
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
UsePrivilegeSeparation yes
KeyRegenerationInterval 3600
ServerKeyBits 1024
SyslogFacility AUTH
LogLevel INFO
LoginGraceTime 120
PermitRootLogin prohibit-password
StrictModes yes
RSAAuthentication yes
PubkeyAuthentication yes
IgnoreRhosts yes
"""
    elif "id_rsa" in file_path:
        return "-----BEGIN RSA PRIVATE KEY-----\nMIIEpQIBAAKCAQEA4u...\n[SENSITIVE PRIVATE KEY CONTENT HIDDEN FOR SIMULATION]\n...35s8f\n-----END RSA PRIVATE KEY-----"
    else:
        return f"[Content of {file_path} loaded into memory buffer]"

@tool
def search_text_in_file(file_path: str, search_term: str) -> str:
    """
    Searches for a specific string or pattern within a file and returns the line number and context.
    """
    if "sshd_config" in file_path and "Root" in search_term:
        return "Line 28: PermitRootLogin prohibit-password"
    return f"Search term '{search_term}' not found in {file_path}."

@tool
def create_new_file(file_path: str, initial_content: str = "") -> str:
    """
    Creates a new empty file or a file with initial content at the specified path.
    """
    return f"Success: File created at {file_path}. Size: {len(initial_content)} bytes."

@tool
def append_text_to_file(file_path: str, text_to_append: str) -> str:
    """
    Appends text to the end of an existing file.
    """
    return f"Success: Content appended to {file_path}. New size updated."

@tool
def replace_text_in_file(file_path: str, old_text: str, new_text: str) -> str:
    """
    Replaces occurrences of a specific string with a new string inside a file.
    """
    return f"Success: Replaced '{old_text}' with '{new_text}' in {file_path}. 1 occurrence(s) modified."

@tool
def copy_file_to_destination(source_path: str, destination_path: str) -> str:
    """
    Copies a file from a source path to a destination path.
    """
    return f"Success: File copied from {source_path} to {destination_path}."

@tool
def move_file_to_destination(source_path: str, destination_path: str) -> str:
    """
    Moves a file from one location to another. Effectively renames or relocates the file.
    """
    return f"Success: File moved from {source_path} to {destination_path}."

@tool
def delete_file_permanently(file_path: str) -> str:
    """
    Permanently deletes a file from the disk. This action is irreversible.
    """
    return f"Success: File {file_path} has been deleted from the filesystem."

@tool
def change_file_ownership(file_path: str, user: str, group: str) -> str:
    """
    Changes the owner and group of a file (chown).
    """
    return f"Success: Ownership of {file_path} changed to {user}:{group}."

@tool
def get_disk_usage_stats(path: str) -> str:
    """
    Returns the disk usage statistics for a specific path or mount point.
    """
    return f"Disk Usage for {path}: 78% used. 22GB available."

@tool
def check_process_locks(file_path: str) -> str:
    """
    Checks if any system processes are currently holding a lock on a file, preventing modification.
    """
    if "log" in file_path:
        return "Lock detected: rsyslogd (PID 442)"
    return "No active locks detected."

@tool
def force_release_file_lock(file_path: str) -> str:
    """
    Forces the release of any file locks held by processes on the specified file.
    """
    return f"Success: Locks released for {file_path}. Process signaled."