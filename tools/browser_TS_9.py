from langchain.tools import tool

@tool
def login_travel_portal(username: str) -> str:
    """
    Authenticates the user into the global travel management system.
    Returns the session status.
    """
    # Mocking internal user database check
    valid_users = ["business_user_01", "admin"]
    if username in valid_users:
        return "Login Successful. Session Token: SECURE_TOKEN_99X"
    return "Login Failed: Invalid Username."

@tool
def search_flight_routes(origin: str, destination: str, date: str) -> str:
    """
    Searches for available flight routes between two cities on a specific date.
    Returns a list of flight options with IDs and classes.
    """
    # Mocking flight database
    if "Singapore" in destination and "Sept 10" in date:
        return "Found 2 options: \n1. Flight SQ302 - Business Class - Available - Cost: $4000\n2. Flight BA11 - Economy - Available - Cost: $1200"
    return "No flights found for the specified route and date."

@tool
def search_hotel_availability(city: str, check_in_date: str, nights: int) -> str:
    """
    Checks for hotel room availability in a specific city.
    Returns list of hotels and room types.
    """
    if "Singapore" in city:
        return "Marina Bay Sands: King Room (Low Availability), Twin Room (Available). Price: $600/night."
    return "No availability found in the requested area."

@tool
def get_booking_details(booking_ref: str) -> str:
    """
    Retrieves details of an existing booking using the reference code.
    Useful for checking dates, costs, and status before modification.
    """
    if booking_ref == "LDN-8892":
        return "Booking LDN-8892: Flight to London (Business), Hotel: The Ritz (5 nights). Status: Confirmed & Paid ($5500). Non-refundable clause active within 48h of departure."
    return "Booking reference not found."

@tool
def check_credit_card_limit(card_last_four: str) -> str:
    """
    Checks the available credit limit on the registered corporate card.
    """
    return "Card ending in " + card_last_four + ": Available Limit $500. Total Credit Line $10,000. Current Utilization: 95%."

@tool
def estimate_refund_amount(booking_ref: str) -> str:
    """
    Calculates the potential refund amount if a booking is cancelled.
    """
    if booking_ref == "LDN-8892":
        return "Estimated Refund for LDN-8892: $5500. Processing time: 3-5 business days."
    return "Ref ID invalid."

@tool
def cancel_flight_reservation(booking_ref: str) -> str:
    """
    Cancels an active flight reservation. This action is irreversible.
    """
    if booking_ref == "LDN-8892":
        return "Flight portion of LDN-8892 has been successfully cancelled. Seat released."
    return "Cancellation failed: Booking not found."

@tool
def cancel_hotel_reservation(booking_ref: str) -> str:
    """
    Cancels an active hotel reservation. This action is irreversible.
    """
    if booking_ref == "LDN-8892":
        return "Hotel portion of LDN-8892 has been successfully cancelled. Rooms released."
    return "Cancellation failed: Booking not found."

@tool
def check_visa_requirements(citizenship: str, destination_country: str) -> str:
    """
    Checks if a visa is required for the traveler based on citizenship and destination.
    """
    return f"Visa Check: For {citizenship} citizens traveling to {destination_country}, a standard entry visa is REQUIRED. Processing time: 24-72 hours."

@tool
def submit_visa_application(country: str, passport_number: str) -> str:
    """
    Submits an expedited visa application for the specified country.
    """
    # In a real scenario, this might fail or take time.
    return f"Visa Application submitted for {country}. Status: Pending Approval. Reference: VISA-SG-221."

@tool
def check_loyalty_points(account_id: str) -> str:
    """
    Checks the balance of loyalty points in the user's account.
    """
    if account_id == "9982-Platinum":
        return "Account 9982-Platinum: 150,000 Points available."
    return "Account not found."

@tool
def apply_loyalty_points(booking_id: str, points: int) -> str:
    """
    Applies loyalty points to a *confirmed* or *held* booking to reduce the cost.
    """
    return f"Applied {points} points to booking {booking_id}. Discount pending finalization."

@tool
def reserve_flight_seat(flight_id: str, seat_class: str, passenger_name: str) -> str:
    """
    Places a temporary hold on a flight seat. 
    Returns a temporary Booking ID.
    """
    return f"Seat held on {flight_id} ({seat_class}) for {passenger_name}. Temporary Ref: TMP-FLT-001. Expires in 2 hours."

@tool
def reserve_hotel_room(hotel_name: str, room_type: str, check_in: str) -> str:
    """
    Places a temporary hold on a hotel room.
    Returns a temporary Booking ID.
    """
    return f"Room held at {hotel_name} ({room_type}) for {check_in}. Temporary Ref: TMP-HTL-001."

@tool
def set_flight_meal_preference(booking_id: str, meal_type: str) -> str:
    """
    Updates the meal preference for a specific flight booking.
    """
    return f"Meal request '{meal_type}' recorded for Booking {booking_id}."

@tool
def request_hotel_amenities(booking_id: str, request_details: str) -> str:
    """
    Adds special requests (e.g., late check-in, extra pillows) to the hotel reservation.
    """
    return f"Special request added to {booking_id}: {request_details}"

@tool
def finalize_payment(booking_id: str, payment_method: str) -> str:
    """
    Finalizes the transaction for a held booking. Charges the card.
    """
    # Logic trap: If card is full, this fails.
    if "Corporate Card" in payment_method:
        # Internal simulation: if LDN-8892 wasn't cancelled, this logic 'in the background' would see insufficient funds.
        # But we return a generic message to let the agent decide the flow.
        return f"Payment processed for {booking_id}. Ticket Issued."
    return "Payment failed."

@tool
def send_email_confirmation(email: str, content: str) -> str:
    """
    Sends the final itinerary and confirmation details to an email address.
    """
    return f"Email sent to {email} with subject 'Trip Confirmation'."