from langchain.tools import tool
from typing import Optional

@tool
def search_office_furniture_catalog(query: str, category: str) -> str:
    """
    Searches the corporate furniture supplier catalog.
    Args:
        query: Search terms (e.g., "standing desk", "ergonomic chair").
        category: The category filter (e.g., "Desks", "Chairs").
    """
    # Simulates returning search results with specific Item IDs
    return (
        f"Found 15 results for '{query}' in '{category}':\n"
        "1. ItemID: DESK-998 | ErgoLift Pro Standing Desk | Price: $850.00\n"
        "2. ItemID: DESK-402 | Basic Manual Sit-Stand | Price: $450.00\n"
        "3. ItemID: CHAIR-881 | Mesh Back Task Chair | Price: $300.00\n"
        "Use 'get_product_specifications' with ItemID for more info."
    )

@tool
def search_electronics_catalog(keyword: str) -> str:
    """
    Searches the approved electronics vendor catalog.
    Args:
        keyword: The product name or type to search for (e.g., "Laptop", "Monitor").
    """
    return (
        f"Search results for '{keyword}':\n"
        "1. ItemID: LAP-PRO-16 | DevStation Pro 16GB RAM | Price: $2200.00\n"
        "2. ItemID: MON-4K-27 | UltraClear 27-inch 4K Monitor | Price: $450.00\n"
        "3. ItemID: DOCK-UNIV | Universal USB-C Docking Station | Price: $180.00\n"
    )

@tool
def get_product_specifications(item_id: str) -> str:
    """
    Retrieves detailed specs, dimensions, and box contents for a specific item.
    Args:
        item_id: The unique identifier of the product.
    """
    if "DESK" in item_id:
        return f"Specs for {item_id}: Motorized height adjustable. Requires assembly (approx 2 hours). Weight: 120lbs. Box contents: Parts and screws only."
    elif "LAP" in item_id:
        return f"Specs for {item_id}: i7 Processor, 512GB SSD. OS pre-installed. Ports: 2x Thunderbolt."
    return f"Specs for {item_id}: Standard commercial grade item. Manufacturer warranty included."

@tool
def check_product_availability(item_id: str, quantity: int) -> str:
    """
    Checks if a specific quantity of an item is in stock for immediate shipment.
    Args:
        item_id: The product ID.
        quantity: The number of units needed.
    """
    return f"Inventory Check: {quantity} units of {item_id} are currently available in the regional warehouse."

@tool
def get_internal_staffing_requirements(department: str, location: str) -> str:
    """
    Queries internal HR records to find headcount details for new hires.
    Args:
        department: The name of the department (e.g., "Engineering", "Interns").
        location: The branch location (e.g., "Westside", "HQ").
    """
    return (
        f"HR Record Query - {department} @ {location}:\n"
        "Upcoming intake count: 12 employees.\n"
        "Start Date: Next Monday.\n"
        "Role Type: Software Engineering Interns."
    )

@tool
def get_office_location_details(branch_name: str) -> str:
    """
    Retrieves address and facility details for a specific company branch.
    Args:
        branch_name: The common name of the branch.
    """
    return (
        f"Location Details for '{branch_name}':\n"
        "Address: 400 Tech Park Blvd, Suite 200.\n"
        "Freight Elevator: Yes.\n"
        "Loading Dock: Available 8AM-4PM.\n"
        "Note: Building requires COI for external delivery/assembly crews."
    )

@tool
def check_corporate_budget_policies(expense_category: str) -> str:
    """
    Checks the company policy regarding spending limits per category.
    Args:
        expense_category: The category (e.g., "Hardware", "Furniture").
    """
    return (
        f"Policy for {expense_category}:\n"
        "- Manager Approval required for single transactions over $10,000.\n"
        "- Furniture must meet ergonomic standards.\n"
        "- Electronics must be from preferred vendors."
    )

@tool
def check_department_credit_limit(department_id: str) -> str:
    """
    Checks the available balance on the department's purchasing card.
    Args:
        department_id: The ID of the department (e.g., "DEPT-ENG-01").
    """
    # Simulates a limit that might be tight for 12 people x (Laptop + Desk + 2 Monitors)
    return "Current Available Balance: $35,000.00. Monthly cycle resets in 14 days."

@tool
def add_item_to_cart(item_id: str, quantity: int) -> str:
    """
    Adds a specific product and quantity to the procurement shopping cart.
    Args:
        item_id: The product ID to add.
        quantity: How many to add.
    """
    return f"Success: Added {quantity} x {item_id} to the shopping cart."

@tool
def remove_item_from_cart(item_id: str) -> str:
    """
    Removes an item from the shopping cart.
    Args:
        item_id: The product ID to remove.
    """
    return f"Success: Removed {item_id} from the cart."

@tool
def view_current_cart(include_totals: str) -> str:
    """
    Displays all items currently in the cart and the estimated subtotal.
    Args:
        include_totals: Set to 'true' or 'false'.
    """
    return (
        "Current Cart:\n"
        "- [Items would be listed here based on previous add_item_to_cart calls]\n"
        "Estimated Subtotal: [Calculated Value]\n"
        "Status: Draft Order."
    )

@tool
def estimate_shipping_time(zip_code: str, service_level: str) -> str:
    """
    Estimates delivery dates based on zip code and service level.
    Args:
        zip_code: Destination zip code.
        service_level: 'Standard', 'Expedited', or 'Overnight'.
    """
    return f"Shipping Estimate for {service_level} to {zip_code}: 3-5 business days. Note: Large freight (desks) may require additional scheduling."

@tool
def add_assembly_and_installation_service(service_type: str) -> str:
    """
    Adds professional installation services to the order.
    Args:
        service_type: Type of service (e.g., 'Desk Assembly', 'IT Setup', 'White Glove').
    """
    return (
        f"Added Service: {service_type}.\n"
        "Cost: $150.00 per workstation.\n"
        "Details: Team will unbox, assemble furniture, organize cables, and remove trash."
    )

@tool
def add_warranty_protection(item_id: str, years: int) -> str:
    """
    Adds extended warranty protection to specific items.
    Args:
        item_id: The product ID.
        years: Duration of warranty (1, 2, or 3).
    """
    return f"Added {years}-year protection plan for {item_id}."

@tool
def search_compatible_peripherals(main_item_id: str) -> str:
    """
    Finds necessary cables, docks, or mounts for a main item.
    Args:
        main_item_id: The ID of the laptop or monitor.
    """
    return (
        f"Recommended peripherals for {main_item_id}:\n"
        "1. HDMI to USB-C Cable (Required for dual monitor setup).\n"
        "2. Power Strip with Surge Protection.\n"
        "3. Cable Management Sleeve."
    )

@tool
def apply_corporate_discount_code(code: str) -> str:
    """
    Applies a promo or contract code to the cart.
    Args:
        code: The discount code.
    """
    return f"Code '{code}' applied. Corporate contract pricing updated. Savings: 15%."

@tool
def set_delivery_address(street: str, city: str, zip_code: str, attention_to: str) -> str:
    """
    Sets the shipping destination for the order.
    Args:
        street: Street address.
        city: City name.
        zip_code: Postal code.
        attention_to: Receiver's name.
    """
    return f"Shipping Address Set: {street}, {city}, {zip_code}. Attn: {attention_to}."

@tool
def finalize_and_submit_order(payment_method_id: str) -> str:
    """
    Finalizes the procurement order and charges the selected payment method.
    Args:
        payment_method_id: The ID of the credit card or billing account.
    """
    return (
        "Order Processed Successfully.\n"
        "Order ID: #ORD-2023-8891.\n"
        "Confirmation email sent to account holder.\n"
        "Logistics team will contact for delivery scheduling."
    )