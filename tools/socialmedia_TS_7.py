from langchain.tools import tool
import random
import time

# Note: No global variables are used. Data persistence is simulated via return values 
# that the agent must pass to subsequent steps (e.g., token passing).

@tool
def fetch_campaign_brief(campaign_name: str):
    """Retrieves the initial details and requirements for a specific marketing campaign."""
    return f"Brief for {campaign_name}: Launch date Today. Focus: Sustainability. Products: Bio-containers. Key Visuals: img_raw_001, img_raw_002."

@tool
def analyze_hashtag_trends(topic: str, region: str):
    """Analyzes current social media trends to suggest high-traffic hashtags."""
    return f"Trending tags for {topic} in {region}: #EcoLife, #GreenSummer, #SustainableFuture, #NoPlastic."

@tool
def identify_influencers(category: str, count: int):
    """Finds top social media influencers in a specific category."""
    return f"Identified {count} influencers in {category}: @EcoWarriorJane, @GreenGreg, @PlanetSarah."

@tool
def get_audience_demographics(segment_name: str):
    """Retrieves demographic data for a specific target audience segment."""
    return f"Segment {segment_name}: Age 25-40, Urban dwellers, High interest in zero-waste lifestyle."

@tool
def apply_image_filter(image_id: str, filter_name: str):
    """Applies a visual filter to a raw image asset."""
    return f"{image_id}_processed_{filter_name}"

@tool
def resize_image_platform(image_id: str, platform: str):
    """Resizes an image to fit the aspect ratio requirements of a specific social platform."""
    dimensions = "1080x1920" if platform.lower() == "instagram" else "1200x675"
    return f"{image_id}_resized_{platform}_{dimensions}"

@tool
def upload_media_asset(local_file_name: str):
    """Uploads a processed media file to the content delivery network (CDN) and returns a public URL."""
    # Simulates returning a URL only if the input looks like a processed file
    return f"https://cdn.greenfuture.io/assets/{local_file_name}_final.jpg"

@tool
def check_copyright_compliance(text_content: str):
    """Scans text against a database of trademarked phrases to ensure legal compliance."""
    return "Compliance Check: PASS. No trademark violations found in the provided text."

@tool
def draft_social_caption(platform: str, key_points: str, tone: str):
    """Generates a text caption for a post based on key selling points and desired tone."""
    return f"[{platform} Draft]: Exciting news! {key_points}. #GreenFuture ({tone} tone)"

@tool
def shorten_url_for_tracking(original_url: str, campaign_id: str):
    """Converts a long URL into a short tracking link for analytics."""
    return f"https://grn.ft/{campaign_id}/track"

@tool
def configure_targeting_settings(platform: str, audience_segment: str):
    """Sets up the ad targeting parameters for a specific platform."""
    return f"Targeting configuration ID 'TGT_{platform}_{audience_segment}' created successfully."

@tool
def deploy_landing_page(environment: str, domain: str):
    """
    Deploys the web application to the specified domain. 
    Crucial: Returns a deployment_hash that proves the site is live.
    """
    # In a real scenario, this takes time.
    return f"Deployment Successful. Domain: {domain} is now LIVE. Deployment_Hash: 'DEP_LIVE_88X9'"

@tool
def generate_promo_codes(code_pattern: str, discount_amount: str):
    """
    Generates and activates discount codes in the commerce database.
    Crucial: Returns an activation_token.
    """
    return f"Promo Code {code_pattern} ({discount_amount}) activated. Activation_Token: 'ACT_CODE_7721'"

@tool
def verify_domain_dns_propagation(domain: str):
    """Checks if the DNS settings for the domain have propagated globally."""
    return f"DNS Verification for {domain}: Propagated (Status: OK)."

@tool
def setup_analytics_tracker(campaign_name: str):
    """Initializes a dashboard to track clicks and conversions."""
    return f"Tracker initialized for {campaign_name}. ID: TRK_001."

@tool
def publish_social_media_post(platform: str, content: str, media_url: str, deployment_hash: str = None, promo_activation_token: str = None):
    """
    Publishes the final post to the social network.
    CRITICAL: Requires proof of backend deployment and promo code activation to function correctly, 
    though it won't explicitly crash without them—it will simulate a 'bad' publish.
    """
    if not deployment_hash or "DEP_LIVE" not in deployment_hash:
        # Implicit failure: Publishing dead links
        return f"SUCCESS: Post published to {platform}. WARNING: Automated link checker detected the target URL returns 404 Not Found."
    
    if not promo_activation_token or "ACT_CODE" not in promo_activation_token:
        # Implicit failure: Publishing invalid codes
        return f"SUCCESS: Post published to {platform}. WARNING: Users reporting 'Invalid Code' errors in comments."

    return f"SUCCESS: Post published to {platform}. Link is active and Promo Code is valid. Engagement tracking started."

@tool
def fetch_user_sentiment_history(brand_name: str):
    """Retrieves historical sentiment analysis data for the brand."""
    return f"Sentiment for {brand_name}: 80% Positive, 15% Neutral, 5% Negative over last quarter."