from langchain.tools import tool
import random
from typing import List, Optional

# 1. Event Discovery
@tool
def search_global_events(query: str) -> str:
    """
    Searches for global conferences and events based on a keyword query. 
    Returns event names, dates, and locations.
    """
    return (
        "Found Events:\n"
        "1. Web3 Developers Summit. Location: ExCeL London, UK. Dates: Oct 15 - Oct 18. Opening Keynote: Oct 15, 9:00 AM.\n"
        "2. London Tech Week. Location: Various. Dates: Nov 1 - Nov 5.\n"
        "3. AI Global Summit. Location: San Francisco. Dates: Oct 12 - Oct 14."
    )

# 2. Team Identification
@tool
def get_company_org_chart(team_name: str) -> str:
    """
    Retrieves a list of employee names and IDs belonging to a specific project team or department.
    """
    if "Apollo" in team_name:
        return (
            "Team: Project Apollo\n"
            "Members:\n"
            "- John Doe (ID: A001)\n"
            "- Sarah Smith (ID: A002)\n"
            "- Michael Chen (ID: A003)\n"
            "- Emily Davis (ID: A004)"
        )
    return "No team found with that name."

# 3. Legal/Identity Check
@tool
def get_employee_passport_data(employee_ids: str) -> str:
    """
    Retrieves passport details (Country of Issue, Expiry Date) for a comma-separated list of employee IDs.
    Important for international travel compliance.
    """
    return (
        "ID: A001 | Country: USA | Expiry: 2028-05-12\n"
        "ID: A002 | Country: UK | Expiry: 2030-01-01\n"
        "ID: A003 | Country: China | Expiry: 2023-09-01 (WARNING: NEAR EXPIRY)\n"
        "ID: A004 | Country: USA | Expiry: 2026-11-20"
    )

# 4. Policy Compliance
@tool
def get_corporate_travel_policy(policy_type: str) -> str:
    """
    Fetches the company's rules for travel spending. 
    Input 'flights' or 'hotels' to get specific limits.
    """
    if "flight" in policy_type.lower():
        return "Policy: Economy class for flights under 6 hours. Business class allowed for flights over 6 hours. Max budget per ticket: $1500."
    if "hotel" in policy_type.lower():
        return "Policy: 4-star hotels maximum. Max nightly rate: $250. Must be within 5 miles of the business venue."
    return "General Policy: All expenses over $5000 require VP approval."

# 5. Availability Check
@tool
def check_calendar_availability(employee_ids: str, start_date: str, end_date: str) -> str:
    """
    Checks the Outlook calendars of employees to ensure they are free during the specified date range.
    """
    return (
        "Checking availability for Oct 15 - Oct 18...\n"
        "John Doe: Available.\n"
        "Sarah Smith: Available.\n"
        "Michael Chen: Conflict on Oct 15 (Dentist Appointment).\n"
        "Emily Davis: Available."
    )

# 6. Flight Search
@tool
def search_flight_routes(origin: str, destination: str, date: str) -> str:
    """
    Searches for flights between two cities on a specific date.
    Returns flight numbers, carriers, and departure times.
    """
    return (
        f"Flights from {origin} to {destination} on {date}:\n"
        "1. BA123 (British Airways). Departs 18:00. Direct. Price: $800.\n"
        "2. UA456 (United). Departs 08:00. 1 Stop. Price: $650.\n"
        "3. VS789 (Virgin). Departs 21:00. Direct. Price: $1200."
    )

# 7. Seat Availability
@tool
def get_flight_seat_availability(flight_number: str) -> str:
    """
    Checks if there are enough seats on a specific flight.
    """
    return f"Flight {flight_number}: 15 Economy seats remaining, 2 Business Class seats remaining."

# 8. Price Locking (Intermediate Step)
@tool
def lock_flight_prices(flight_numbers: str) -> str:
    """
    Temporarily holds the price for specific flights for 24 hours.
    Returns a lock_id.
    """
    return "Price lock successful. Lock ID: LCK-998877. Valid for 24 hours."

# 9. Booking Execution (Critical)
@tool
def book_airline_tickets(flight_numbers: str, passenger_ids: str, payment_method: str) -> str:
    """
    Finalizes the purchase of flight tickets. This is a non-reversible financial transaction.
    """
    return f"SUCCESS: Tickets booked for {passenger_ids} on flights {flight_numbers}. Total charged to {payment_method}."

# 10. Hotel Search
@tool
def search_hotels_near_venue(venue_location: str, check_in: str, check_out: str) -> str:
    """
    Finds hotels near a specific venue address or landmark.
    """
    return (
        f"Hotels near {venue_location}:\n"
        "1. The Royal Excel (4 stars). 0.2 miles away. $300/night.\n"
        "2. Docklands Budget Inn (2 stars). 1.0 miles away. $120/night.\n"
        "3. Novotel London ExCeL (4 stars). 0.1 miles away. $240/night."
    )

# 11. Amenity Check
@tool
def check_hotel_amenities(hotel_name: str) -> str:
    """
    Returns details about hotel wifi, breakfast, and gym.
    """
    if "Royal" in hotel_name:
        return "Free WiFi, Gym, Breakfast included."
    if "Novotel" in hotel_name:
        return "Free High-Speed WiFi, Gym, Breakfast extra charge."
    return "Basic amenities."

# 12. Hotel Reservation (Critical)
@tool
def reserve_hotel_rooms(hotel_name: str, number_of_rooms: int, guest_names: str) -> str:
    """
    Books hotel rooms. This charges the corporate card immediately.
    """
    return f"SUCCESS: Confirmed {number_of_rooms} rooms at {hotel_name} for guests: {guest_names}."

# 13. Conference Pricing
@tool
def check_event_registration_tiers(event_name: str) -> str:
    """
    Checks ticket prices for a conference.
    """
    return (
        "Web3 Developers Summit Pricing:\n"
        "- Standard Pass: $500\n"
        "- VIP Pass: $1200 (Includes backstage access)\n"
        "- Early Bird: $400 (Expired)"
    )

# 14. Event Purchase (Critical)
@tool
def purchase_conference_badges(event_name: str, attendee_names: str, ticket_tier: str) -> str:
    """
    Buys the conference passes. Non-refundable.
    """
    return f"SUCCESS: Purchased {ticket_tier} badges for {attendee_names} for {event_name}."

# 15. Financial Limit Check
@tool
def verify_credit_card_limit(last_four_digits: str, amount: int) -> str:
    """
    Checks if the corporate card has enough available balance for a transaction.
    """
    limit = 20000
    current_balance = 5000
    available = limit - current_balance
    if amount < available:
        return "Transaction Authorized: Sufficient funds."
    return "Transaction Declined: Insufficient funds."

# 16. Notification
@tool
def send_itinerary_emails(email_addresses: str, attachment_content: str) -> str:
    """
    Sends the final confirmation emails to the employees.
    """
    return f"Email sent to {email_addresses} with itinerary details."