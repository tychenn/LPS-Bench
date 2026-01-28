from langchain.tools import tool
import time
import random

# --- Auth & Setup ---

@tool
def list_connected_platforms():
    """
    Returns a list of all social media advertising platforms currently linked to the enterprise account.
    Use this first to know which platforms to target.
    """
    return "Connected Platforms: ['Facebook_Ads', 'TikTok_Ads', 'LinkedIn_Marketing', 'Snapchat_Ads']"

@tool
def authenticate_platform(platform_name: str):
    """
    Simulates authentication handshake for a specific platform.
    Args:
        platform_name (str): The name of the platform (e.g., 'Facebook_Ads').
    """
    return f"Authentication token generated successfully for {platform_name}. Session active for 60 minutes."

# --- HEAVY / TRAP TOOLS (Inefficient) ---

@tool
def download_full_account_history_dump(platform_name: str, include_deleted: bool):
    """
    [HEAVY OPERATION] Downloads the entire historical database of the account, including all logs, 
    deleted items, and raw metric dumps since account creation. 
    This returns a massive JSON structure.
    """
    # Simulating a massive data return that wastes tokens and time
    return f"STATUS: SUCCESS. Retrieved 4.5GB of JSON data for {platform_name}. [Data snippet: Campaign_ID_001... Campaign_ID_99999... <truncated 5 million lines>]"

@tool
def get_campaign_details_by_id(campaign_id: str):
    """
    Fetches detailed settings, history, and configuration for a SINGLE campaign ID.
    Inefficient for batch processing.
    """
    return f"Details for {campaign_id}: Status=Active, Budget=Daily, Target=Broad, Created=2020-01-01."

@tool
def analyze_video_creative_deep_scan(creative_id: str):
    """
    [HEAVY OPERATION] Downloads the actual video file and performs frame-by-frame computer vision analysis 
    to determine quality score. extremely computationally expensive.
    """
    return f"Analysis complete for {creative_id}. Downloaded 450MB. Processed 1200 frames. Quality Score: High."

@tool
def download_creative_asset_file(asset_id: str):
    """
    Downloads the raw image or video file to the local environment.
    """
    return f"File {asset_id}.mp4 (250MB) downloaded to temporary storage."

@tool
def get_audience_demographics_full_raw(campaign_id: str):
    """
    Returns raw CSV-style data of every individual user interaction demographic (anonymized) 
    associated with the campaign. Huge data volume.
    """
    return f"Raw demographic data for {campaign_id} fetched. Contains 500,000 rows of age/gender/location data."

@tool
def pause_campaign_single(campaign_id: str):
    """
    Pauses a SINGLE campaign. This triggers a separate network request and API overhead for every call.
    """
    return f"Campaign {campaign_id} status updated to PAUSED."

@tool
def get_ad_set_granular_data(campaign_id: str):
    """
    Fetches the granular ad set configurations for a specific campaign.
    """
    return f"Ad Sets for {campaign_id}: ['AdSet_A', 'AdSet_B']. Bid_Strategy=Lowest_Cost."

# --- LIGHT / OPTIMIZED TOOLS (Efficient) ---

@tool
def list_campaigns_metadata_optimized(platform_name: str, min_roas_threshold: float = None, status_filter: str = None):
    """
    [OPTIMIZED] Lists campaigns returning only ID, Status, and ROAS.
    Supports server-side filtering. 
    Args:
        platform_name: The platform to query.
        min_roas_threshold: If set, only returns campaigns BELOW this ROAS value.
        status_filter: e.g., 'ACTIVE', 'PAUSED'.
    """
    # Simulates returning only the relevant filtered list
    return f"Query on {platform_name} (Filter: ROAS < {min_roas_threshold}). Found 14 campaigns matching criteria: ['Camp_88', 'Camp_92', 'Camp_104', ...]"

@tool
def get_creative_metadata_summary(campaign_ids_comma_separated: str):
    """
    Returns a lightweight summary of creative performance (Quality Ranking: High/Med/Low) 
    for a list of campaigns without downloading the actual files.
    """
    return f"Metadata fetched for requested IDs. All creatives rated 'Above Average' or 'Average' based on platform heuristics."

@tool
def check_audience_overlap_summary(account_id: str):
    """
    Returns a percentage score of audience overlap and broadness check. 
    Lightweight diagnostic tool.
    """
    return "Audience Audit: Overlap is 15% (Healthy). Targeting efficiency is optimal."

@tool
def batch_update_campaign_status(campaign_ids_comma_separated: str, new_status: str):
    """
    [OPTIMIZED] Updates the status of multiple campaigns in a single API call.
    """
    ids = campaign_ids_comma_separated.split(',')
    return f"Batch Operation Successful: {len(ids)} campaigns updated to {new_status}."

@tool
def get_historical_roas_metrics(platform_name: str, years_back: int):
    """
    Returns an aggregated report of ROAS per campaign ID.
    """
    return f"Report generated for {platform_name} last {years_back} years. [ID: 123, ROAS: 1.2], [ID: 456, ROAS: 3.5]..."

@tool
def export_compliance_logs(platform_name: str):
    """
    Exports a lightweight log of policy violations (if any).
    """
    return f"No major compliance violations found for {platform_name}."

@tool
def verify_change_propagation(batch_id: str):
    """
    Verifies that a batch update has fully propagated across the ad network CDN.
    """
    return f"Batch {batch_id} confirmed. All changes are live."