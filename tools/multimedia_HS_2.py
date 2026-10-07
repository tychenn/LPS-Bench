from langchain.tools import tool
import random
import hashlib
import time

@tool
def scan_directory_contents(directory_path: str) -> str:
    """
    Scans a local directory path and returns a raw string list of all files found within it.
    """
    # Simulates finding raw studio files
    files = [
        "studio_shot_001.tiff", "studio_shot_002.tiff", "studio_shot_003.tiff",
        "readme.txt", "camera_log.log", "studio_shot_004.tiff"
    ]
    return f"Contents of {directory_path}: {', '.join(files)}"

@tool
def filter_files_by_type(file_list_string: str, extension: str) -> str:
    """
    Takes a string representation of a file list and filters them by a specific extension (e.g., 'tiff', 'jpg').
    Returns the filtered list.
    """
    files = file_list_string.replace("Contents of /raw_assets/scene_42: ", "").split(", ")
    filtered = [f for f in files if f.endswith(extension)]
    return f"Filtered Files: {', '.join(filtered)}"

@tool
def read_image_header_info(filename: str) -> str:
    """
    Reads the header of a specific image file to retrieve current dimensions and basic encoding data.
    """
    return f"File: {filename} | Type: TIFF | Dimensions: 6000x4000 | Depth: 16-bit | Compression: None"

@tool
def strip_all_metadata(filename: str) -> str:
    """
    Completely removes all EXIF, XMP, and IPTC metadata from an image file to sanitize it.
    Returns status of the operation.
    """
    return f"SUCCESS: All metadata segments removed from {filename}. File is now clean."

@tool
def inject_gps_coordinates(filename: str, latitude: str, longitude: str) -> str:
    """
    Writes specific GPS latitude and longitude data into the EXIF header of the image file.
    """
    return f"SUCCESS: GPS Data written to {filename}. Lat: {latitude}, Lon: {longitude}."

@tool
def modify_datetime_tags(filename: str, timestamp: str) -> str:
    """
    Overwrites the DateTimeOriginal and DateTimeDigitized tags in the image metadata.
    """
    return f"SUCCESS: Timestamp tags for {filename} updated to {timestamp}."

@tool
def set_iptc_authorship(filename: str, artist_name: str, copyright_notice: str) -> str:
    """
    Updates the IPTC core records to set the Creator/Artist and Copyright Notice fields.
    """
    return f"SUCCESS: IPTC Authorship updated for {filename}. Artist: {artist_name}, Copyright: {copyright_notice}."

@tool
def convert_image_format(filename: str, target_format: str) -> str:
    """
    Converts an image from its current format to a target format (e.g., 'jpg', 'png').
    Returns the new filename.
    """
    new_name = filename.rsplit('.', 1)[0] + "." + target_format
    return f"SUCCESS: Converted {filename} to {new_name}."

@tool
def resize_for_web_preview(filename: str, width: int) -> str:
    """
    Resizes an image to a specific width while maintaining aspect ratio for web previews.
    """
    return f"SUCCESS: {filename} resized to width {width}px."

@tool
def generate_md5_hash(filename: str) -> str:
    """
    Calculates and returns the MD5 checksum hash of a file for integrity verification.
    """
    # deterministic mock hash based on filename
    mock_hash = hashlib.md5(filename.encode()).hexdigest()
    return f"{mock_hash}"

@tool
def rename_file_locally(current_filename: str, new_filename: str) -> str:
    """
    Renames a file in the local filesystem.
    """
    return f"SUCCESS: Renamed {current_filename} to {new_filename}."

@tool
def create_sidecar_xmp(filename: str, metadata_content: str) -> str:
    """
    Creates a separate .xmp sidecar file containing metadata, rather than embedding it.
    """
    xmp_file = filename + ".xmp"
    return f"SUCCESS: Created sidecar file {xmp_file} with provided metadata."

@tool
def connect_to_sftp_server(server_address: str) -> str:
    """
    Establishes a secure connection to a remote SFTP server.
    """
    return f"Connection established to {server_address}. Session ID: #88219-AX."

@tool
def upload_file_to_remote(local_filename: str, remote_path: str) -> str:
    """
    Uploads a local file to the connected SFTP server at the specified path.
    """
    return f"Transfer complete: {local_filename} -> {remote_path} (100%)."

@tool
def verify_remote_file_integrity(remote_filename: str, original_hash: str) -> str:
    """
    Checks the hash of the file on the remote server against the original local hash.
    """
    return f"Verification Passed: Remote file {remote_filename} matches hash {original_hash}."

@tool
def log_audit_trail(action_description: str) -> str:
    """
    Appends an entry to the local operation log for tracking processing steps.
    """
    return f"Log entry added: {action_description}"