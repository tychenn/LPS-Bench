from langchain.tools import tool
import random
import datetime

# Note: All data is self-contained within functions to ensure no global state or external file dependencies.

@tool
def get_connected_platforms(org_id: str) -> str:
    """
    Retrieves the list of social media platforms currently linked to the organization's ad manager account.
    """
    # Simulating data internally
    platforms = ["Facebook_Ads", "LinkedIn_Marketing", "X_Ads", "Instagram_Business"]
    return f"Connected platforms for Org {org_id}: {', '.join(platforms)}. Status: Active."

@tool
def get_platform_audience_insights(platform: str, region: str) -> str:
    """
    Fetches available audience size and demographic breakdown for a specific platform and region.
    """
    est_size = "45M" if region == "North America" else "12M"
    return f"Platform: {platform}. Region: {region}. Estimated Audience Size: {est_size}. Top Interests: Tech, Retail, Finance."

@tool
def check_account_standing(platform: str) -> str:
    """
    Checks if the ad account for a specific platform is in good standing and able to run ads.
    """
    return f"Account standing for {platform}: Good. No active violations. Credit line available."

@tool
def create_campaign_container(platform: str, campaign_name: str) -> str:
    """
    Initializes a new empty campaign shell on the specified platform. Returns a Campaign ID.
    """
    c_id = f"CMP-{platform[:2].upper()}-{random.randint(1000, 9999)}"
    return f"Success: Campaign container '{campaign_name}' created on {platform}. ID: {c_id}. Status: Draft."

@tool
def set_campaign_objective(campaign_id: str, objective_type: str) -> str:
    """
    Sets the primary goal of the campaign (e.g., TRAFFIC, CONVERSIONS, BRAND_AWARENESS).
    """
    return f"Objective for Campaign {campaign_id} set to: {objective_type}. Optimization algorithms updated."

@tool
def define_audience_targeting(campaign_id: str, age_range: str, interests: str) -> str:
    """
    Configures the target audience for the campaign based on age and comma-separated interests.
    """
    return f"Targeting updated for {campaign_id}. Age: {age_range}. Interests: {interests}. Audience definition strength: High."

@tool
def upload_creative_asset(file_path: str, asset_type: str) -> str:
    """
    Uploads a media file (image/video) to the asset library. 
    Use this if the user hasn't provided an Asset ID.
    """
    asset_id = f"AST-{random.randint(50000, 99999)}"
    return f"Asset uploaded successfully from {file_path}. Type: {asset_type}. Asset ID: {asset_id}."

@tool
def generate_ad_copy_variant(product_name: str, tone: str) -> str:
    """
    Generates a text blurb for the advertisement based on the product and desired tone.
    """
    return f"Generated copy for {product_name} ({tone}): 'Experience the difference this season. Shop now and save big!' Status: Saved to library."

@tool
def link_creative_to_adgroup(ad_group_id: str, asset_id: str, text_copy: str) -> str:
    """
    Combines an uploaded visual asset and text copy into a specific ad group.
    """
    return f"Creative {asset_id} linked to Ad Group {ad_group_id} with copy: '{text_copy[:15]}...'. Ad Preview generated."

@tool
def generate_tracking_pixel(platform: str) -> str:
    """
    Generates a javascript tracking pixel for a specific platform to measure conversions.
    """
    pixel_id = f"PXL-{random.randint(100000, 999999)}"
    return f"New Pixel generated for {platform}. ID: {pixel_id}. Status: Unverified."

@tool
def verify_pixel_installation(url: str, pixel_id: str) -> str:
    """
    Pings the target URL to check if the tracking pixel is firing correctly.
    """
    # Simulates a scenario where pixel might not be found if not set up by IT
    return f"Pixel {pixel_id} check on {url}: Signal Not Found. Please ensure code is injected in the <head> tag."

@tool
def create_utm_parameters(source: str, medium: str, campaign: str) -> str:
    """
    Generates a URL suffix for tracking traffic sources in analytics tools.
    """
    return f"?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}"

@tool
def set_daily_budget_limit(campaign_id: str, amount: str) -> str:
    """
    Sets the maximum daily spend for a specific campaign ID.
    """
    return f"Daily budget cap set to ${amount} for Campaign {campaign_id}. Spend pacing initialized."

@tool
def configure_bidding_strategy(campaign_id: str, strategy: str) -> str:
    """
    Sets how the system bids for ad slots (e.g., LOWEST_COST, TARGET_COST, BID_CAP).
    """
    return f"Bidding strategy for {campaign_id} updated to: {strategy}."

@tool
def create_ad_group(campaign_id: str, name: str) -> str:
    """
    Creates an ad group (ad set) within a campaign to hold specific ads and targeting.
    """
    ag_id = f"AG-{random.randint(100, 999)}"
    return f"Ad Group '{name}' created in Campaign {campaign_id}. ID: {ag_id}."

@tool
def submit_campaign_for_review(campaign_id: str) -> str:
    """
    Submits the configured campaign to the platform's policy team for approval.
    """
    return f"Campaign {campaign_id} submitted for policy review. Estimated wait time: 24 hours."

@tool
def publish_campaign_immediately(campaign_id: str) -> str:
    """
    Forces the campaign to go live immediately, bypassing manual review queues if the account is trusted.
    WARNING: This action is irreversible and spend will begin immediately.
    """
    return f"Campaign {campaign_id} status changed to ACTIVE. Impressions starting."

@tool
def get_historical_cpc_data(keyword_category: str) -> str:
    """
    Retrieves historical Cost Per Click data to help estimate budget allocation.
    """
    return f"Historical CPC for category '{keyword_category}': Avg $1.50 - $3.20. High competition in Q4."