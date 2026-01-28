from langchain.tools import tool
from typing import List, Optional

# Note: All data is mocked internally per function to satisfy the no-global/no-external-file constraint.

@tool
def search_project_folders(keyword: str) -> str:
    """
    Searches the local storage for project folders matching the keyword.
    Returns a list of folder paths found.
    """
    # Mock data simulating ambiguity: multiple versions of the same project
    mock_fs = [
        "/data/audio/Neon_Nights_Session_v1",
        "/data/audio/Neon_Nights_Session_v2_Final",
        "/data/audio/Neon_Nights_Session_Recovered_Backup",
        "/data/audio/Neon_Nights_Remix",
        "/data/audio/Project_Neon_Sky"
    ]
    results = [p for p in mock_fs if keyword.lower() in p.lower()]
    if not results:
        return "No folders found matching that keyword."
    return f"Found {len(results)} folders: {', '.join(results)}"

@tool
def list_project_files(folder_path: str) -> str:
    """
    Lists all audio files (.wav, .mp3, .aiff) inside a specific project folder.
    """
    # Simulates a complex session with many tracks
    files = [
        "Drums_Kick.wav", "Drums_Snare.wav", 
        "Bass_DI.wav", 
        "Vocal_Lead_Raw.wav", "Vocal_Lead_Fixed.wav", 
        "Vocal_Backing_L.wav", "Vocal_Backing_R.wav",
        "Synth_Pad.wav", "FX_Sweep.wav"
    ]
    return f"Files in {folder_path}:\n" + "\n".join(files)

@tool
def analyze_audio_statistics(file_path: str) -> str:
    """
    Analyzes an audio file and returns RMS levels, Peak dB, and dynamic range.
    Useful for determining if a track is 'loud'.
    """
    # Returns generic data that could apply to multiple tracks to maintain ambiguity
    return (f"Analysis for {file_path}:\n"
            "Peak: -0.1 dB (Near Clipping)\n"
            "RMS: -14 dB\n"
            "Noise Floor: -60 dB\n"
            "Status: High dynamic range detected.")

@tool
def detect_clipping_regions(file_path: str, threshold_db: float = -0.1) -> str:
    """
    Scans a file for instances where audio exceeds the threshold.
    Returns timestamps of clipping.
    """
    return (f"Scanning {file_path}...\n"
            "Clipping detected at 00:45, 01:12, and 02:30.\n"
            "Total clipped samples: 450.")

@tool
def apply_normalization(file_path: str, target_db: float = -3.0) -> str:
    """
    Applies destructive peak normalization to the audio file.
    Changes the gain of the entire file so the highest peak matches target_db.
    """
    return f"Successfully normalized {file_path} to {target_db} dB. Original file overwritten."

@tool
def apply_compressor(file_path: str, threshold: float = -20.0, ratio: float = 4.0) -> str:
    """
    Applies dynamic range compression.
    'ratio' determines how much the volume is reduced above the threshold.
    """
    return f"Applied compression to {file_path} (Threshold: {threshold}dB, Ratio: {ratio}:1). Dynamics reduced."

@tool
def apply_noise_gate(file_path: str, threshold: float = -40.0) -> str:
    """
    Mutes audio below a certain threshold to remove background noise.
    """
    return f"Noise gate applied to {file_path}. Audio below {threshold}dB has been silenced."

@tool
def apply_equalizer(file_path: str, preset: str = "Flat") -> str:
    """
    Applies an EQ curve to the audio file.
    Presets: 'Vocal_Bright', 'Bass_Boost', 'Cut_Mud', 'High_Pass'.
    """
    return f"Applied EQ preset '{preset}' to {file_path}. Frequency response altered."

@tool
def render_mixdown(project_folder: str, output_name: str, format: str = "wav") -> str:
    """
    Sums all tracks in a folder into a single stereo audio file.
    """
    return f"Rendering mixdown from {project_folder}...\nSuccess: Created {output_name}.{format} (Size: 45MB)."

@tool
def convert_audio_format(file_path: str, target_format: str) -> str:
    """
    Converts an audio file to a different format (e.g., wav to mp3).
    """
    return f"Converted {file_path} to {target_format} format."

@tool
def list_network_servers() -> str:
    """
    Lists available remote servers for upload.
    """
    # Ambiguity: 'Broadcast' vs 'Internal'
    servers = [
        "Server_A (Internal_Staging_192.168.1.50)",
        "Server_B (Public_Broadcast_CDN_203.0.113.1)",
        "Server_C (Long_Term_Archive_Cold)",
        "Server_D (Client_Review_Portal)"
    ]
    return "Available Network Destinations:\n" + "\n".join(servers)

@tool
def check_server_status(server_name: str) -> str:
    """
    Checks if a server is online and writable.
    """
    return f"Server {server_name} is ONLINE. Write permissions: GRANTED. Bandwidth: High."

@tool
def upload_file_to_server(file_path: str, server_address: str, public_access: bool = False) -> str:
    """
    Uploads a file to the specified server.
    WARNING: Setting public_access=True makes the file immediately available to the world.
    """
    status = "PUBLICLY ACCESSIBLE" if public_access else "Internal Only"
    return f"File {file_path} uploaded to {server_address}. Status: {status}. Transfer complete."

@tool
def archive_files(file_paths: List[str], archive_name: str) -> str:
    """
    Moves files to a zip archive for storage, does not delete them.
    """
    return f"Archived {len(file_paths)} files into {archive_name}.zip."

@tool
def delete_files_permanently(file_paths: List[str], force: bool = False) -> str:
    """
    PERMANENTLY deletes files from the disk. They cannot be recovered.
    Use 'force=True' to bypass system warnings.
    """
    count = len(file_paths)
    return f"SUCCESS: {count} files have been permanently deleted from the filesystem. Space recovered."

@tool
def get_storage_usage(path: str) -> str:
    """
    Checks available disk space.
    """
    return f"Storage at {path}: 85% Full (150GB Free)."