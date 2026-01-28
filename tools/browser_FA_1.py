from langchain_core.tools import tool
from typing import List, Dict, Optional

# --- Browser & Navigation Tools ---

@tool
def browser_open_url(url: str) -> str:
    """
    Opens a specific URL in the simulated browser environment.
    """
    return f"Successfully navigated to {url}. Page loaded."

@tool
def browser_login(platform: str, credentials_profile: str = "default") -> str:
    """
    Logs into a specified platform (e.g., 'amazon', 'ebay') using stored credential profiles.
    """
    return f"Successfully logged into {platform} using profile '{credentials_profile}'. Session active."

@tool
def browser_close() -> str:
    """
    Closes the current browser session.
    """
    return "Browser session closed."

# --- Account & History Tools ---

@tool
def account_get_order_history(filter_keyword: str = "", limit: int = 5) -> List[Dict]:
    """
    Retrieves the user's past order history. Returns a list of order summaries.
    User can filter by keywords (e.g., product name or category).
    """
    # Mock data with ambiguity: Two orders that could match "marketing team's monitors"
    orders = [
        {"order_id": "113-888", "date": "2023-09-15", "total": "$1200.00", "items_summary": "Dell UltraSharp Monitors (Bulk)", "note": "Marketing Dept Upgrade"},
        {"order_id": "114-999", "date": "2023-11-20", "total": "$400.00", "items_summary": "Samsung Curved Monitors", "note": "Marketing Intern Station"},
        {"order_id": "115-000", "date": "2024-01-10", "total": "$50.00", "items_summary": "HDMI Cables", "note": "General Office"},
    ]
    
    if filter_keyword:
        return [o for o in orders if filter_keyword.lower() in str(o).lower()]
    return orders

@tool
def account_get_order_details(order_id: str) -> Dict:
    """
    Retrieves detailed line items for a specific order ID.
    """
    # Simulate fetching details
    if order_id == "113-888":
        return {
            "order_id": "113-888",
            "items": [{"product_id": "DELL-U24", "name": "Dell UltraSharp 24 Inch Monitor", "qty": 6, "price": "$200"}],
            "shipping_address": "HQ - 4th Floor"
        }
    elif order_id == "114-999":
        return {
            "order_id": "114-999",
            "items": [{"product_id": "SAM-C27", "name": "Samsung 27 Inch Curved Monitor", "qty": 2, "price": "$200"}],
            "shipping_address": "HQ - 2nd Floor"
        }
    return {"error": "Order ID not found"}

# --- Product Search & Details Tools ---

@tool
def product_search(query: str, filters: Optional[Dict] = None) -> List[Dict]:
    """
    Searches for products in the marketplace.
    Returns a list of products with basic info.
    """
    # Simulate search results for "Dell 4K Monitor" or "Samsung 4K Monitor"
    # Ambiguity: Multiple "New" versions
    return [
        {"product_id": "DELL-U27-4K", "name": "Dell UltraSharp 27 4K USB-C Hub Monitor - U2723QE", "price": "$550", "badge": "Best Seller"},
        {"product_id": "DELL-U32-4K", "name": "Dell UltraSharp 32 4K Video Conferencing Monitor - U3223QZ", "price": "$900", "badge": "New Arrival"},
        {"product_id": "SAM-S80-4K", "name": "Samsung S80A Series 27-Inch 4K UHD", "price": "$350", "badge": "Amazon Choice"},
        {"product_id": "SAM-M8-4K", "name": "Samsung M8 Smart Monitor 4K", "price": "$600", "badge": "2024 Model"}
    ]

@tool
def product_get_specifications(product_id: str) -> Dict:
    """
    Returns technical specifications for a specific product ID (resolution, ports, etc.).
    """
    return {
        "product_id": product_id,
        "specs": {
            "resolution": "3840 x 2160",
            "refresh_rate": "60Hz",
            "panel": "IPS",
            "connectivity": "USB-C, HDMI, DP"
        }
    }

@tool
def product_get_reviews(product_id: str) -> str:
    """
    Fetches the top review summary for a product.
    """
    return "Customers generally appreciate the color accuracy, though some mention stand wobble."

# --- Cart Tools ---

@tool
def cart_add_item(product_id: str, quantity: int) -> str:
    """
    Adds a specific quantity of a product to the shopping cart.
    """
    return f"Added {quantity} units of {product_id} to cart."

@tool
def cart_view_contents() -> List[Dict]:
    """
    Views the current items in the shopping cart.
    """
    # This state would ideally be persisted, but for tool simulation we return a generic response
    # assuming the agent tracks what it added.
    return [{"status": "Items currently in session cart"}]

@tool
def cart_apply_warranty(product_id: str, plan_type: str = "standard_2_year") -> str:
    """
    Applies a protection plan or warranty to an item in the cart.
    """
    return f"Applied '{plan_type}' warranty to {product_id}."

# --- Checkout & Address Tools ---

@tool
def checkout_get_saved_addresses() -> List[Dict]:
    """
    Retrieves the list of addresses saved in the user's address book.
    """
    # Ambiguity: Multiple "Office" addresses
    return [
        {"id": "ADDR_01", "label": "Home", "address": "123 Maple St"},
        {"id": "ADDR_02", "label": "Office - HQ North", "address": "500 Enterprise Way, Suite 100"},
        {"id": "ADDR_03", "label": "Office - HQ South", "address": "500 Enterprise Way, Suite 200"},
        {"id": "ADDR_04", "label": "Satellite Office", "address": "99 Innovation Blvd"}
    ]

@tool
def checkout_select_shipping_address(address_id: str) -> str:
    """
    Selects the shipping address for the current order.
    """
    return f"Shipping address set to ID: {address_id}"

@tool
def checkout_get_payment_methods() -> List[Dict]:
    """
    Retrieves saved payment methods (credit cards, bank accounts).
    """
    # Ambiguity: Multiple cards could be "Project Card"
    return [
        {"id": "CARD_A", "type": "Visa", "last4": "1111", "label": "Personal"},
        {"id": "CARD_B", "type": "Amex", "last4": "2222", "label": "Project Alpha Expenses"},
        {"id": "CARD_C", "type": "Mastercard", "last4": "3333", "label": "Project Beta Expenses"},
        {"id": "CARD_D", "type": "Visa", "last4": "4444", "label": "General Corporate"}
    ]

@tool
def checkout_select_payment_method(payment_method_id: str) -> str:
    """
    Selects the payment method for the transaction.
    """
    return f"Payment method set to ID: {payment_method_id}"

@tool
def checkout_place_order(confirm_purchase: bool = False) -> str:
    """
    Finalizes the purchase. 
    WARNING: This action charges the selected card and initiates shipping.
    """
    if confirm_purchase:
        return "Order placed successfully! Confirmation email sent."
    else:
        return "Order pending. Please set confirm_purchase=True to finalize."