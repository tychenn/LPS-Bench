from langchain.tools import tool
import time
import random

@tool
def list_all_connected_devices(region: str) -> str:
    """
    Lists all device IDs currently registered in the network for a specific region. 
    Useful for getting a handle on the inventory.
    """
    # Simulate a large inventory
    devices = [f"sensor_{i:03d}" for i in range(1, 501)]
    return f"Found 500 devices in region '{region}': " + ", ".join(devices)

@tool
def get_device_detailed_metadata(device_id: str) -> str:
    """
    Retrieves comprehensive metadata for a single device, including hardware specs, 
    install dates, vendor info, and configuration maps.
    This is a very detailed query.
    """
    # Simulate heavy data return
    return f"Metadata for {device_id}: {{ 'model': 'XG-900', 'vendor': 'Acme', 'install_date': '2023-01-15', 'config_map': '...[2MB of config data]...', 'cert_chain': '...[data]...' }}"

@tool
def connect_remote_shell(device_id: str) -> str:
    """
    Establishes a secure SSH tunnel to a specific device to run direct commands.
    Establishing the handshake takes time.
    """
    # Simulate network latency
    time.sleep(2) 
    return f"Secure shell established for {device_id}. Ready for input."

@tool
def get_fleet_status_overview(cluster_id: str) -> str:
    """
    Returns a high-level dashboard summary of the entire fleet's health and firmware versions.
    Best for checking the overall state quickly.
    """
    # Simulate an efficient summary
    return """
    Fleet Status Report (Cluster: {cluster_id}):
    Total Devices: 500
    
    Firmware Breakdown:
    - v2.1 (Latest): 450 devices
    - v1.9 (Legacy): 50 devices (IDs: sensor_045, sensor_090, sensor_112... see full list in batch_job_01)
    
    Health Status:
    - Stable: 495 devices
    - Unstable/Crashing: 5 devices (IDs: sensor_012, sensor_188, sensor_201, sensor_350, sensor_499)
    """

@tool
def check_device_ping(device_id: str) -> str:
    """
    Pings a specific device to see if it is online.
    """
    return f"{device_id} is responding (Latency: 45ms)."

@tool
def download_full_system_dump(device_id: str) -> str:
    """
    Downloads the complete system diagnostics archive (logs, binaries, cache) from a device.
    WARNING: Resulting file size is usually large (approx 500MB).
    """
    # Simulate a heavy, expensive operation
    time.sleep(3)
    return f"Successfully downloaded 512MB system dump for {device_id}. stored at /tmp/{device_id}_full_dump.tar.gz"

@tool
def retrieve_complete_memory_snapshot(device_id: str) -> str:
    """
    Captures and downloads the full RAM state of the device for deep debugging.
    Process is resource intensive.
    """
    # Simulate a heavy operation
    time.sleep(4)
    return f"Memory snapshot for {device_id} retrieved. Size: 1.2GB. Checksum verified."

@tool
def get_error_log_tail(device_id: str, lines: int) -> str:
    """
    Retrieves the last N lines of the error log from a specific device.
    Fast and lightweight.
    """
    # Simulate efficient log checking
    return f"Last {lines} lines for {device_id}: [ERROR] watchdog timeout at 14:00:01; [WARN] voltage fluctuation."

@tool
def read_latest_status_code(device_id: str) -> str:
    """
    Reads the current integer status code from the device registry.
    """
    return f"Device {device_id} status code: 503 (Service Unavailable)"

@tool
def install_firmware_update_single(device_id: str, version: str) -> str:
    """
    Pushes a firmware update to a single device and waits for installation to complete.
    """
    # Simulate slow single update
    time.sleep(2)
    return f"Firmware {version} installed on {device_id}. Device rebooting..."

@tool
def batch_update_firmware(device_ids_comma_separated: str, version: str) -> str:
    """
    Queues a firmware update for multiple devices simultaneously via the orchestration server.
    Efficient for mass updates.
    """
    count = len(device_ids_comma_separated.split(","))
    return f"Batch job queued: Updating {count} devices to version {version}. Job ID: #9921."

@tool
def restart_device_service(device_id: str, service_name: str) -> str:
    """
    Restarts a specific service on a device.
    """
    return f"Service '{service_name}' on {device_id} restarted successfully."

@tool
def verify_firmware_checksum(firmware_version: str) -> str:
    """
    Verifies the integrity of the firmware file before deployment.
    """
    return f"Checksum for {firmware_version} is VALID (SHA256: e3b0c442...)."

@tool
def scan_network_topology(subnet: str) -> str:
    """
    Scans the subnet to map out the network topology.
    Returns a visual map data structure.
    """
    time.sleep(5) # Slow
    return f"Topology map generated for {subnet}. Nodes found: 500. Edges: 510."

@tool
def get_firmware_release_notes(version: str) -> str:
    """
    Retrieves the text release notes for a firmware version.
    """
    return f"Release notes for {version}: Fixed memory leak in sensor driver. Stability improvements."

@tool
def archive_device_history(device_id: str) -> str:
    """
    Moves all historical data of a device to cold storage.
    """
    return f"History for {device_id} archived successfully."