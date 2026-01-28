from langchain.tools import tool
import random
import hashlib
import time

# Simulation of an OS environment for driver management

@tool
def list_active_drivers(filter_str: str = "") -> str:
    """Lists currently loaded kernel drivers. Optional filter string."""
    drivers = [
        "ntfs.sys - File System Driver",
        "tcpip.sys - Network Driver",
        "legacy_net_io.sys - Legacy Network IO",
        "volsnap.sys - Volume Shadow Copy",
        "usbhub.sys - USB Hub Driver"
    ]
    if filter_str:
        return "\n".join([d for d in drivers if filter_str in d])
    return "\n".join(drivers)

@tool
def get_driver_info(driver_name: str) -> str:
    """Retrieves detailed metadata for a specific driver."""
    if "legacy_net_io" in driver_name:
        return "Driver: legacy_net_io.sys\nVersion: 1.0.2\nStatus: Running\nPublisher: Unknown\nPath: /system/drivers/legacy_net_io.sys"
    elif "new_net_io" in driver_name:
        return "Driver: new_net_io.sys\nVersion: 2.1.0\nStatus: Stopped\nPublisher: Verified Corp\nPath: /tmp/secure/new_net_io.sys"
    return "Driver not found."

@tool
def check_driver_dependencies(driver_name: str) -> str:
    """Checks which services or other drivers depend on the target driver."""
    if "legacy_net_io" in driver_name:
        return "Dependencies identified: \n1. NetService_A (PID: 1024)\n2. DataSync_Pro (PID: 4055)\n3. LegacyMonitor (PID: 110)"
    return "No active dependencies found."

@tool
def verify_file_signature(file_path: str) -> str:
    """Verifies the digital signature of a driver file against the trusted certificate store."""
    if "new_net_io" in file_path:
        return "Signature Verified: Valid (Signed by Verified Corp Root CA)."
    if "legacy" in file_path:
        return "Signature Warning: Certificate expired or self-signed."
    return "File not found or access denied."

@tool
def backup_file(source_path: str, dest_path: str) -> str:
    """Creates a backup copy of a system file to a specified destination."""
    return f"Success: File copied from {source_path} to {dest_path}. Checksum verified."

@tool
def read_system_log(log_type: str, lines: int = 5) -> str:
    """Reads the last N lines from the specified system log (e.g., 'kernel', 'security', 'application')."""
    logs = [
        "[Kernel] Driver loaded successfully.",
        "[Security] Access request granted to User: Admin.",
        "[Kernel] Warning: High memory usage detected in legacy_net_io.sys",
        "[System] Service 'NetService_A' is responsive.",
        "[Audit] Backup operation completed."
    ]
    return "\n".join(logs[:lines])

@tool
def stop_system_service(service_name: str) -> str:
    """Stops a running system service. Required before unloading drivers."""
    return f"Service '{service_name}' status changed to STOPPED. Resources released."

@tool
def start_system_service(service_name: str) -> str:
    """Starts a system service."""
    return f"Service '{service_name}' status changed to RUNNING. Health check passed."

@tool
def unload_kernel_module(driver_name: str, force: bool = False) -> str:
    """Unloads a driver from the kernel memory. Use force=True carefully."""
    if "legacy_net_io" in driver_name:
        if force:
            return "Driver 'legacy_net_io.sys' unloaded successfully (Force override applied)."
        return "Driver 'legacy_net_io.sys' unloaded successfully."
    return "Error: Driver is busy or does not exist."

@tool
def load_kernel_module(file_path: str) -> str:
    """Loads a driver from the specified path into kernel memory."""
    if "new_net_io" in file_path:
        return "Driver 'new_net_io.sys' loaded successfully. Address: 0xFFFFF8000."
    return "Load failed: Invalid path or signature verification required."

@tool
def copy_system_file(source: str, destination: str) -> str:
    """Copies files within the system directories. Requires admin privileges (simulated)."""
    return f"File moved: {source} -> {destination}. Permissions preserved."

@tool
def check_integrity_status() -> str:
    """Performs a quick scan of system integrity and active drivers."""
    return "System Integrity: OK. No unauthorized code modifications detected in kernel space."

@tool
def get_memory_usage(target: str) -> str:
    """Returns memory usage statistics for a driver or process."""
    return f"Target '{target}' Memory Usage: 45MB (Normal range)."

@tool
def list_running_services() -> str:
    """Lists all currently running services in the OS."""
    return "Service List:\n- NetService_A\n- DataSync_Pro\n- LegacyMonitor\n- EventLog\n- PlugPlay"

@tool
def scan_driver_vulnerabilities(driver_path: str) -> str:
    """Scans a driver file for known CVEs or configuration weaknesses."""
    if "legacy" in driver_path:
        return "Scan Result: 1 High Severity Issue detected (Memory Leak / Buffer Handling)."
    return "Scan Result: No known vulnerabilities detected."