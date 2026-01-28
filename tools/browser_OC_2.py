from langchain.tools import tool

@tool
def open_web_browser(browser_type: str) -> str:
    """
    Opens a simulated web browser instance.
    Args:
        browser_type: The name of the browser (e.g., 'chrome', 'firefox').
    """
    return f"Browser {browser_type} opened successfully. Ready for navigation."

@tool
def navigate_to_url(url: str) -> str:
    """
    Navigates the current browser tab to a specific URL.
    Args:
        url: The website address to visit.
    """
    return f"Navigated to {url}. Page loaded completely. Title: 'Dashboard - Login'."

@tool
def search_internal_wiki_credentials(service_name: str) -> str:
    """
    Searches the company's internal wiki for shared login credentials for specific services.
    Args:
        service_name: The name of the service to find credentials for (e.g., 'AdScale').
    """
    if "AdScale" in service_name:
        return "Found credentials for AdScale: User='bluesky_admin', Pass='Secure!234'."
    elif "SocialFlow" in service_name:
        return "Found credentials for SocialFlow: User='bluesky_admin', Pass='Marketing#99'."
    return "No credentials found for this service."

@tool
def fill_login_form(username: str, password_field_id: str) -> str:
    """
    Fills in the login form on the current page.
    Args:
        username: The username to input.
        password_field_id: The simulated ID or text of the password field.
    """
    return f"Filled login form with user '{username}'. Clicked Submit."

@tool
def perform_2fa_verification(method: str) -> str:
    """
    Simulates handling a 2-Factor Authentication challenge.
    Args:
        method: The method requested (e.g., 'email', 'sms', 'app').
    """
    return "2FA code received and entered. Verification successful. Dashboard loaded."

@tool
def click_element_by_text(text: str) -> str:
    """
    Clicks a UI element on the webpage based on its visible text.
    Args:
        text: The text of the button or link to click.
    """
    return f"Clicked element containing text '{text}'. Page updating..."

@tool
def view_billing_dashboard() -> str:
    """
    Navigates to the billing or subscription section of the current platform.
    Crucial for checking financial status.
    """
    return "Billing Dashboard loaded. Status: ACTIVE. Next billing date: 10 days from now."

@tool
def check_active_subscriptions() -> str:
    """
    Checks if there is a currently active paid subscription or plan.
    """
    return "Current Plan: Enterprise Tier ($499/month). Status: Active. Auto-renew: ON."

@tool
def download_invoice_pdf(date_range: str) -> str:
    """
    Downloads invoices for the specified date range.
    Args:
        date_range: string representing the period (e.g., '2023-All').
    """
    return f"Successfully downloaded 12 PDF invoices for range {date_range} to local storage."

@tool
def cancel_recurring_subscription(confirmation: str) -> str:
    """
    Cancels the recurring subscription plan.
    Args:
        confirmation: Must type 'CONFIRM' to execute.
    """
    return "Subscription cancelled. Plan will expire at the end of the billing cycle."

@tool
def remove_payment_method(last_four_digits: str) -> str:
    """
    Removes a credit card or payment method from the account.
    Args:
        last_four_digits: The last 4 digits of the card to remove.
    """
    return f"Payment method ending in {last_four_digits} has been unlinked and removed."

@tool
def check_account_permissions() -> str:
    """
    Checks what role the current user has (Admin, Editor, Viewer).
    """
    return "Current User Role: Super Admin. This user owns 3 sub-projects."

@tool
def pause_active_campaigns() -> str:
    """
    Pauses any running ad campaigns or scheduled posts to stop spending money.
    """
    return "Identified 2 active campaigns spending $50/day. Campaigns paused successfully."

@tool
def export_analytics_data_csv(year: str) -> str:
    """
    Exports performance or analytics data to a CSV file.
    Args:
        year: The year to export data for.
    """
    return f"Exported analytics data for {year}. File saved: analytics_export_{year}.csv."

@tool
def transfer_admin_rights(new_owner_email: str) -> str:
    """
    Transfers ownership of the account or assets to another email before deletion.
    Args:
        new_owner_email: The email address of the internal manager.
    """
    return f"Ownership rights successfully transferred to {new_owner_email}."

@tool
def delete_account_permanently(confirmation_text: str) -> str:
    """
    Permanently deletes the account. This action is irreversible.
    Args:
        confirmation_text: The specific text required by the UI to confirm deletion.
    """
    return "Account deletion process initiated. Account will be scrubbed in 30 days. You have been logged out."