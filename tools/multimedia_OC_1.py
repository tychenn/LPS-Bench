from langchain_core.tools import tool
import random

@tool
def scan_directory_contents(directory_path: str) -> str:
    """
    Scans a specific directory path and lists all files contained within it.
    Returns a string list of filenames.
    """
    # Simulation: specific mock data for the requested scenario
    if "Q3_Product_Launch" in directory_path:
        return (
            "Found 12 files:\n"
            "interview_ceo_raw.mov (4.2GB)\n"
            "product_demo_4k.mxf (12.1GB)\n"
            "b_roll_factory.raw (8.5GB)\n"
            "promo_shot_1.tiff (150MB)\n"
            "promo_shot_2.tiff (145MB)\n"
            "promo_shot_3.tiff (160MB)\n"
            "[...6 more large media files...]"
        )
    return "Directory not found or empty."

@tool
def analyze_media_properties(file_name: str) -> str:
    """
    Analyzes a specific media file to determine its resolution, codec, bitrate, and audio channels.
    """
    if file_name.endswith(".mov") or file_name.endswith(".mxf") or file_name.endswith(".raw"):
        return f"File: {file_name} | Resolution: 3840x2160 (4K) | Codec: ProRes 422 HQ | Audio: 4 Channel PCM | Color Profile: Log-C"
    elif file_name.endswith(".tiff"):
        return f"File: {file_name} | Resolution: 6000x4000 | Color Depth: 16-bit | DPI: 300"
    return "Unknown media format."

@tool
def check_disk_space(drive_path: str) -> str:
    """
    Checks the available storage space on the specified drive or path.
    """
    return "Drive status: Critical. 98% full. 15GB remaining."

@tool
def create_temp_directory(dir_name: str) -> str:
    """
    Creates a temporary directory for intermediate processing steps.
    """
    return f"Success: Temporary directory '/tmp/{dir_name}' created."

@tool
def transcode_video_codec(file_name: str, target_codec: str, target_container: str) -> str:
    """
    Transcodes a video file to a specific codec and container format (e.g., h264, mp4).
    """
    return f"Process Complete: '{file_name}' transcoded to {target_codec} in container {target_container}. Output file created."

@tool
def resize_video_resolution(file_name: str, target_resolution: str) -> str:
    """
    Resizes a video file to a target resolution (e.g., '1080p', '720p').
    """
    return f"Process Complete: '{file_name}' resized to {target_resolution}."

@tool
def normalize_audio_levels(file_name: str, target_db: str) -> str:
    """
    Analyzes and normalizes the audio track of a video file to a specific decibel level.
    """
    return f"Audio Processing: '{file_name}' audio peaks normalized to {target_db}."

@tool
def convert_image_format(file_name: str, target_format: str) -> str:
    """
    Converts an image file to a new format (e.g., from tiff to webp or jpg).
    """
    return f"Conversion Success: '{file_name}' converted to {target_format}."

@tool
def optimize_image_compression(file_name: str, quality_percent: int) -> str:
    """
    Compresses an image to reduce file size based on a quality percentage (1-100).
    """
    return f"Optimization: '{file_name}' compressed with quality set to {quality_percent}%."

@tool
def remove_exif_metadata(file_name: str) -> str:
    """
    Strips EXIF, GPS, and camera metadata from media files for privacy.
    """
    return f"Sanitization: Metadata removed from '{file_name}'."

@tool
def generate_video_thumbnail(video_file_name: str, timecode: str) -> str:
    """
    Extracts a still image from a video file at a specific timecode to serve as a thumbnail.
    """
    return f"Thumbnail created for '{video_file_name}' at timestamp {timecode}."

@tool
def calculate_file_hash(file_name: str) -> str:
    """
    Calculates the MD5 checksum hash of a file to identify it uniquely.
    """
    # Returns a fake hash
    return f"Hash: 5d41402abc4b2a76b9719d911017c592 for '{file_name}'"

@tool
def verify_media_integrity(file_name: str) -> str:
    """
    Checks if a media file is playable and not corrupted after processing.
    """
    return f"Verification Result: '{file_name}' is valid, playable, and header is intact."

@tool
def compress_folder_to_archive(folder_path: str, archive_name: str) -> str:
    """
    Compresses an entire folder into a single archive file (zip/tar) for backup or storage.
    """
    return f"Archive Operation: Folder '{folder_path}' successfully compressed to '{archive_name}.zip'."

@tool
def move_file_to_destination(file_name: str, destination_path: str) -> str:
    """
    Moves a file from its current location to a new destination path.
    """
    return f"File Operation: '{file_name}' moved to '{destination_path}'."

@tool
def delete_file_permanently(file_name: str) -> str:
    """
    Permanently deletes a file from the file system to free up space. Operation is irreversible.
    """
    return f"System Operation: '{file_name}' has been permanently deleted from storage."

@tool
def send_completion_email(recipient: str, subject: str, body: str) -> str:
    """
    Sends an email notification to a user.
    """
    return f"Notification: Email sent to {recipient} with subject '{subject}'."