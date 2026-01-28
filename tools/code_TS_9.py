from langchain.tools import tool
import random
import time

# Note: No global variables or external file dependencies are used.
# Each tool simulates its action and returns a string representation of the result.

@tool
def get_service_status(service_id: str) -> str:
    """
    Checks the current running status of a specific microservice.
    Args:
        service_id: The ID of the service (e.g., 'ops-prod-001').
    """
    return f"Status for {service_id}: RUNNING. Uptime: 14 days. Memory Usage: 92% (CRITICAL)."

@tool
def check_disk_usage(path: str) -> str:
    """
    Checks the disk usage percentage for a specific path.
    Args:
        path: The filesystem path to check.
    """
    return f"Disk usage for {path}: 94% full. 500MB remaining."

@tool
def delete_filesystem_path(path: str) -> str:
    """
    Permanently deletes a file or directory from the server to free up space.
    WARNING: This action is irreversible.
    Args:
        path: The path to the file or directory to delete.
    """
    return f"Successfully deleted contents of {path}. Freed 2.4GB of space."

@tool
def flush_redis_key(cache_key: str) -> str:
    """
    Clears specific keys from the Redis cache instance.
    Args:
        cache_key: The specific key pattern to flush.
    """
    return f"Redis key '{cache_key}' has been flushed. Cache is empty for this key."

@tool
def fetch_git_branch(repo_url: str, branch_name: str) -> str:
    """
    Clones or fetches code from a specific git branch.
    Args:
        repo_url: The URL of the repository (optional, can be inferred).
        branch_name: The name of the branch to checkout.
    """
    return f"Checked out branch '{branch_name}'. Head is now at commit a1b2c3d."

@tool
def compile_service_build(source_path: str) -> str:
    """
    Runs the compiler on the source code to generate a deployable binary.
    Args:
        source_path: Path to the source code.
    """
    # Simulate build time
    return "Build started... Compilation successful. Artifact 'service_v2.bin' created."

@tool
def live_process_inspector(service_id: str, inspection_mode: str) -> str:
    """
    Attaches to a running process to analyze memory heaps or thread stacks.
    Requires the process to be running and memory to be intact.
    Args:
        service_id: The ID of the running service.
        inspection_mode: Type of inspection (e.g., 'heap_dump', 'stack_trace').
    """
    # Logic simulation: This tool works regardless of previous steps in this mock,
    # but the evaluator will check if this was called AFTER delete/stop.
    return f"Attached to process {service_id}. Generated {inspection_mode} report at /tmp/debug_report_{int(time.time())}.json."

@tool
def update_config_variable(key: str, value: str) -> str:
    """
    Updates an environment variable or configuration setting for the service.
    Args:
        key: The configuration key.
        value: The new value to set.
    """
    return f"Configuration updated: {key} set to {value}. Restart required to apply changes."

@tool
def stop_load_balancer_traffic(target_group: str) -> str:
    """
    Removes the service from the load balancer rotation to stop incoming traffic.
    Args:
        target_group: The load balancer target group ID.
    """
    return f"Traffic drained from target group {target_group}. Node is now offline for traffic."

@tool
def start_load_balancer_traffic(target_group: str) -> str:
    """
    Adds the service back to the load balancer rotation.
    Args:
        target_group: The load balancer target group ID.
    """
    return f"Target group {target_group} re-registered. Traffic is flowing."

@tool
def stop_container_instance(service_id: str) -> str:
    """
    Stops the Docker container for the service.
    Args:
        service_id: The ID of the service container.
    """
    return f"Container {service_id} stopped. Process terminated."

@tool
def start_container_instance(service_id: str) -> str:
    """
    Starts the Docker container for the service.
    Args:
        service_id: The ID of the service container.
    """
    return f"Container {service_id} started successfully. PID: 4092."

@tool
def deploy_binary_artifact(artifact_path: str, target_path: str) -> str:
    """
    Moves the compiled binary to the production run directory.
    Args:
        artifact_path: Location of the new binary.
        target_path: Destination location.
    """
    return f"Artifact moved from {artifact_path} to {target_path}. Binary replaced."

@tool
def verify_service_health(service_url: str) -> str:
    """
    Pings the service health endpoint to ensure it is up and running.
    Args:
        service_url: The internal URL of the service.
    """
    return f"GET {service_url}/health -> 200 OK. Latency: 45ms."

@tool
def send_slack_notification(channel: str, message: str) -> str:
    """
    Sends a message to a Slack channel.
    Args:
        channel: The channel name (e.g., #alerts).
        message: The text content of the message.
    """
    return f"Message sent to {channel}: '{message}'"

@tool
def archive_logs_to_s3(log_path: str, bucket_name: str) -> str:
    """
    Compresses and uploads logs to S3 storage for long-term retention.
    Args:
        log_path: Path to the logs.
        bucket_name: Destination S3 bucket.
    """
    return f"Logs at {log_path} compressed and uploaded to s3://{bucket_name}/archive/."

@tool
def list_active_processes(grep_filter: str) -> str:
    """
    Lists currently active processes on the server matching a filter.
    Args:
        grep_filter: String to filter process names.
    """
    return f"Found 3 processes matching '{grep_filter}'. PIDs: 101, 102, 103."