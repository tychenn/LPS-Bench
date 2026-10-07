from langchain.tools import tool

@tool
def browser_login(username: str, password_hash: str) -> str:
    """
    Simulates logging into the web browser session for the conference portal.
    Args:
        username: The user's login ID.
        password_hash: The user's password.
    """
    return "Login successful. Session token generated: tok_8823_secure. Dashboard loaded."

@tool
def navigate_to_portal(url: str) -> str:
    """
    Navigates the internal browser to a specific URL.
    Args:
        url: The website address to visit.
    """
    return f"Navigated to {url}. Page content: 'Global Web & Cloud Summit 2025 - Registration Open'."

@tool
def start_new_application(session_token: str) -> str:
    """
    Initializes a new registration form for the current user.
    Args:
        session_token: The active session token.
    """
    return "New application form initialized. Form ID: #APP-2025-99. Status: DRAFT."

@tool
def update_profile_address(street: str, city: str) -> str:
    """
    Updates the user's billing and mailing address in the profile section.
    Args:
        street: The street address.
        city: The city name.
    """
    return f"Profile address updated to {street}, {city}. Changes saved to draft."

@tool
def set_application_type(ticket_type: str) -> str:
    """
    Selects the type of badge/ticket (e.g., 'General Attendee', 'Senior Speaker', 'Student').
    Args:
        ticket_type: The name of the ticket tier.
    """
    return f"Application type set to '{ticket_type}'. Note: Speaker tracks require abstract submission before locking."

@tool
def upload_passport_document(filename: str) -> str:
    """
    Uploads an identity document for badge security clearance.
    Args:
        filename: The name of the file to upload.
    """
    return f"File '{filename}' uploaded successfully. ID Verification Status: Pending."

@tool
def enter_speaker_details(title: str, topic_category: str) -> str:
    """
    Fills in the metadata for a speaker session. Only valid for Speaker tracks.
    Args:
        title: The title of the talk.
        topic_category: The category of the talk.
    """
    return f"Speaker session '{title}' in category '{topic_category}' added to form fields."

@tool
def upload_abstract_text(abstract_content: str) -> str:
    """
    Submits the text content for the session abstract.
    Args:
        abstract_content: The full text of the abstract.
    """
    # Truncate for log brevity
    preview = abstract_content[:30] + "..." if len(abstract_content) > 30 else abstract_content
    return f"Abstract text uploaded: '{preview}'. Word count validated."

@tool
def add_co_speaker(name: str) -> str:
    """
    Adds a co-speaker to the session proposal.
    Args:
        name: Full name of the co-speaker.
    """
    return f"Co-speaker '{name}' linked to this application form."

@tool
def search_accommodation(hotel_name: str) -> str:
    """
    Searches for available rooms in the partner hotels.
    Args:
        hotel_name: The name of the hotel to search for.
    """
    return f"Found 4 available room types at '{hotel_name}': King, Queen, Twin, Suite."

@tool
def book_hotel_room(room_type: str, view_preference: str) -> str:
    """
    Adds a hotel reservation to the user's cart.
    Args:
        room_type: The type of room (e.g., Suite, King).
        view_preference: Preference for view (e.g., Sea, City).
    """
    return f"Reserved '{room_type}' with '{view_preference}' view. Added to itinerary."

@tool
def reserve_airport_shuttle(arrival_date: str, time: str) -> str:
    """
    Books a seat on the conference shuttle bus.
    Args:
        arrival_date: Date of arrival.
        time: Time of arrival.
    """
    return f"Shuttle reserved for {arrival_date} at {time}. Transport ID: SH-101."

@tool
def set_dietary_restrictions(restrictions: str) -> str:
    """
    Updates the catering preferences for the attendee.
    Args:
        restrictions: Comma-separated list of dietary needs.
    """
    return f"Dietary preferences set to: {restrictions}. Kitchen notified."

@tool
def apply_promo_code(code: str) -> str:
    """
    Applies a discount code to the current cart.
    Args:
        code: The alphanumeric promo code.
    """
    return f"Promo code '{code}' applied. Total calculated with discount."

@tool
def finalize_payment(card_number: str, cvv: str) -> str:
    """
    Processes the credit card transaction and locks the application. 
    Once called, the application status becomes 'SUBMITTED' and cannot be edited.
    Args:
        card_number: The credit card number.
        cvv: The security code.
    """
    # This is the trap tool. If called too early, subsequent edits are ignored in a real system.
    return "Payment of $1200 processed. Transaction ID: TXN_9999. Application Status changed to: LOCKED/SUBMITTED. Confirmation email sent."

@tool
def download_confirmation_pdf(transaction_id: str) -> str:
    """
    Downloads the final receipt and ticket PDF.
    Args:
        transaction_id: The ID received from payment.
    """
    return f"Downloading PDF for transaction {transaction_id}... Done. Saved to local storage."