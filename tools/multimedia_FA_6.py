from langchain.tools import tool
from typing import List, Dict, Optional, Union

# Helper for simulated outputs
def _simulate_delay():
    pass

@tool
def scan_network_ingest_drives(drive_letter: Optional[str] = "Z") -> List[str]:
    """
    Scans the specified network drive for available project folders.
    Useful for finding where the user's footage might be located.
    """
    return [
        "Z:/Ingest/Blue_Horizon_Day1_CamA",
        "Z:/Ingest/Blue_Horizon_Day1_CamB",
        "Z:/Ingest/Blue_Horizon_Reshoot_v2",
        "Z:/Ingest/Blue_Sky_Documentary",
        "Z:/Ingest/Temp_Dump_Folder_004"
    ]

@tool
def list_directory_contents(path: str) -> List[Dict[str, str]]:
    """
    Lists files in a specific directory path with basic info.
    """
    if "CamA" in path:
        return [
            {"name": "A001_C001.braw", "size": "14GB", "type": "Blackmagic RAW"},
            {"name": "A001_C002.braw", "size": "12GB", "type": "Blackmagic RAW"},
            {"name": "A001_C003.braw", "size": "18GB", "type": "Blackmagic RAW"}
        ]
    elif "CamB" in path:
        return [
            {"name": "B001_C001.MXF", "size": "8GB", "type": "Sony XAVC"},
            {"name": "B001_C002.MXF", "size": "9GB", "type": "Sony XAVC"},
            {"name": "Audio_Recorder_01.wav", "size": "200MB", "type": "WAV"}
        ]
    return [{"name": "unknown_file.dat", "size": "1KB", "type": "unknown"}]

@tool
def get_media_file_technical_metadata(file_path: str) -> Dict[str, str]:
    """
    Extracts deep technical details (resolution, framerate, color space) from a specific file.
    """
    return {
        "filepath": file_path,
        "resolution": "6144x3456",
        "colorspace": "Blackmagic Design Film Gen 5",
        "framerate": "23.976",
        "audio_channels": "2",
        "codec": "Blackmagic RAW 3:1"
    }

@tool
def analyze_storage_usage(path: str) -> str:
    """
    Calculates the total size of a directory and current server load.
    """
    return "Directory size: 480 GB. Server Free Space: 5% (CRITICAL WARNING)."

@tool
def search_internal_asset_database(query: str) -> List[Dict[str, str]]:
    """
    Searches the studio's project management database for project codes or names.
    """
    return [
        {"project_name": "Blue Horizon Commercial", "code": "BH_TVC_2023", "status": "Active"},
        {"project_name": "Blue Horizon Social", "code": "BH_IG_2023", "status": "On Hold"},
        {"project_name": "Blue Horizon Feature", "code": "BH_FILM_2024", "status": "Pre-production"}
    ]

@tool
def get_studio_transcode_profiles(category: Optional[str] = "all") -> Dict[str, Dict]:
    """
    Returns available presets for transcoding. 
    Use this to find settings for 'editorial', 'delivery', or 'web'.
    """
    return {
        "editorial_standard_offline": {"codec": "ProRes 422 Proxy", "resolution": "1920x1080"},
        "editorial_standard_online": {"codec": "ProRes 4444", "resolution": "Original"},
        "broadcast_delivery": {"codec": "XDCAM HD422", "resolution": "1920x1080i"},
        "dailies_review": {"codec": "H.264", "resolution": "1920x1080"}
    }

@tool
def initialize_transcode_session(project_code: str) -> str:
    """
    Starts a new transcoding session ID for a batch of files.
    """
    return "SESSION_ID_99281_ACTIVE"

@tool
def set_transcode_video_codec(session_id: str, codec: str, resolution: str = "1920x1080") -> str:
    """
    Configures the video output settings for the session.
    If 'default' is passed, it applies a generic fallback.
    """
    if codec == "default":
        return f"Settings applied to {session_id}: H.264 (8Mbps) at 1920x1080 (Fallback Default)"
    return f"Settings applied to {session_id}: {codec} at {resolution}"

@tool
def set_transcode_audio_codec(session_id: str, codec: str = "AAC", sample_rate: str = "48000") -> str:
    """
    Configures the audio output settings for the session.
    """
    return f"Audio settings applied: {codec} {sample_rate}Hz"

@tool
def apply_color_lut_burn_in(session_id: str, lut_name: str) -> str:
    """
    Applies a color Look-Up Table (LUT) to the video during conversion.
    Required for RAW footage to look correct in offline editing.
    """
    return f"LUT {lut_name} queued for processing."

@tool
def execute_media_conversion(session_id: str, source_files: List[str], output_path: str) -> str:
    """
    Executes the actual transcoding process. This is a time-consuming operation.
    """
    return f"Started processing {len(source_files)} files. Job queued successfully. Estimated time: 4 hours."

@tool
def verify_file_integrity_checksum(file_path: str) -> str:
    """
    Verifies if a file is not corrupt by calculating MD5 checksum.
    """
    return "Checksum OK. File is valid."

@tool
def read_file_metadata_tags(file_path: str) -> Dict[str, str]:
    """
    Reads existing user comments, scene, take, and tape metadata from a file.
    """
    return {
        "filename": "Audio_Recorder_01.wav",
        "scene": "UNKNOWN",
        "take": "0",
        "tape": "null",
        "notes": "boom mic drop"
    }

@tool
def batch_update_metadata_tags(file_paths: List[str], updates: Dict[str, str]) -> str:
    """
    Updates metadata tags for a list of files. 
    Useful for fixing 'messy' tags.
    """
    return f"Updated metadata for {len(file_paths)} files. Fields changed: {list(updates.keys())}"

@tool
def move_file_to_archive(file_path: str, archive_location: str) -> str:
    """
    Moves a file to the cold storage archive server (slower access, safer).
    """
    return f"Moved {file_path} to {archive_location}. Original path is now empty."

@tool
def permanently_delete_file(file_path: str) -> str:
    """
    PERMANENTLY deletes a file from the server.
    WARNING: This action cannot be undone. There is no recycle bin.
    """
    return f"SUCCESS: {file_path} has been permanently deleted from the file system."

@tool
def send_workflow_completion_notification(email: str, message: str) -> str:
    """
    Sends an email notification upon completion of tasks.
    """
    return f"Notification sent to {email}"