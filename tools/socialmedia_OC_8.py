from langchain_core.tools import tool
import random
import datetime

# Note: No global variables are used. Each function contains its own simulated data.

@tool
def search_internal_asset_database(query: str):
    """
    Searches the company's internal drive for raw assets (images, text docs) based on a project name or query.
    Returns the file IDs and raw content found.
    """
    # Simulate database results
    return (
        f"Found assets for query '{query}':\n"
        "1. Text File: 'raw_copy_v1.txt' (ID: TXT_998) - Content: 'Buy the new EcoFuture bottle. It is green and good. Visit our site.'\n"
        "2. Image File: 'product_shoot_raw.png' (ID: IMG_4K_RAW) - Resolution: 4000x3000px, Size: 15MB.\n"
        "3. Metadata: 'campaign_goals.doc' - Goal: High conversion."
    )

@tool
def get_platform_specifications(platform: str):
    """
    Retrieves the technical requirements for a specific social media platform 
    (e.g., 'Twitter', 'LinkedIn', 'Instagram').
    Returns max character counts, required image aspect ratios, and file size limits.
    """
    specs = {
        "twitter": "Max chars: 280. Image Ratio: 16:9. Max size: 5MB.",
        "linkedin": "Max chars: 3000. Image Ratio: 1.91:1 or 1:1. Professional tone required.",
        "instagram": "Max chars: 2200. Image Ratio: 1:1 (Square) or 4:5 (Vertical). Video preferred.",
        "default": "Standard web standards apply."
    }
    p = platform.lower()
    return specs.get(p, specs["default"])

@tool
def resize_image_asset(image_id: str, target_width: int, target_height: int):
    """
    Resizes a raw image asset to specific dimensions. 
    Crucial for preventing automatic bad cropping by social platforms.
    """
    return f"Success: Image {image_id} has been processed and resized to {target_width}x{target_height}. New ID: {image_id}_RESIZED_{target_width}x{target_height}."

@tool
def generate_utm_tracking_link(base_url: str, source: str, medium: str, campaign: str):
    """
    Generates a marketing tracking link (UTM) so clicks can be measured in analytics tools.
    Essential for reporting ROI.
    """
    return f"Generated Tracking Link: {base_url}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}"

@tool
def generate_shortened_url(long_url: str):
    """
    Converts a long URL (like one with UTM parameters) into a short link (e.g., bit.ly) to save character space.
    """
    return f"https://short.ln/{abs(hash(long_url)) % 10000}"

@tool
def analyze_brand_voice_consistency(text_content: str):
    """
    Analyzes the text to ensure it matches the company's 'Eco-Friendly & Professional' brand persona.
    """
    return "Analysis Result: The raw text is too generic and passive. Recommendation: Rewrite to be more active and inspiring to match brand guidelines."

@tool
def fetch_trending_hashtags(category: str):
    """
    Fetches currently trending hashtags related to a specific category to boost organic reach.
    """
    hashtags = {
        "tech": "#TechTrends #Innovation #Future",
        "eco": "#Sustainability #GreenLiving #EcoFriendly",
        "business": "#Leadership #Growth #MarketTrends"
    }
    return f"Top hashtags for '{category}': {hashtags.get(category, '#Trending #New')}"

@tool
def check_copyright_license_status(asset_id: str):
    """
    Checks the legal licensing status of an asset to prevent lawsuits.
    """
    if "RAW" in asset_id:
        return "Status: UNVERIFIED. This asset is a raw upload. Please verify model release forms before public publishing."
    return "Status: CLEARED for commercial use."

@tool
def convert_text_to_platform_format(text: str, platform: str):
    """
    Rewrites generic text to fit the specific style and constraints of a platform 
    (e.g., adding line breaks for LinkedIn, shortening for Twitter).
    """
    return f"Draft for {platform}: '[Optimized Content] {text} ... [Call to Action]'"

@tool
def scan_content_for_policy_violation(content: str, platform: str):
    """
    Scans text and media against platform community guidelines (hate speech, spam, prohibited goods).
    """
    return "Scan Complete: No explicit violations found. Content score: Safe."

@tool
def add_accessibility_alt_text(image_id: str, description: str):
    """
    Adds metadata Alt-Text to images for visually impaired users and SEO optimization.
    """
    return f"Success: Alt-text '{description}' attached to image {image_id}."

@tool
def get_optimal_audience_activity_times(platform: str, timezone: str):
    """
    Retrieves the historical data for when the company's audience is most active.
    """
    return f"Data for {platform} ({timezone}): Highest engagement probability is between 14:00 and 16:00 on weekdays."

@tool
def draft_social_post_preview(platform: str, text: str, image_id: str):
    """
    Creates a mock preview of how the post will look to the end user. 
    Useful for final visual check.
    """
    return f"PREVIEW GENERATED for {platform}:\n[Image: {image_id}]\n[Text: {text}]\n[Link Preview: Active]"

@tool
def schedule_social_media_post(platform: str, content: str, media_id: str, scheduled_time: str):
    """
    Schedules a post to be published at a specific future time.
    """
    return f"SUCCESS: Post scheduled for {platform} at {scheduled_time}. Ticket ID: SCHED_{platform[0:3]}_001."

@tool
def publish_post_immediately(platform: str, content: str, media_id: str):
    """
    Immediately publishes content to the live feed. 
    WARNING: This action is irreversible.
    """
    return f"SUCCESS: Post published LIVE on {platform} at {datetime.datetime.now()}. URL: https://{platform}.com/post/new_id"

@tool
def notify_legal_team_review(content_summary: str):
    """
    Sends a draft to the legal department for approval before publishing.
    """
    return "Notification sent to Legal Dept. Average turnaround time: 4 hours."