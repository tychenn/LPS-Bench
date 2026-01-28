from langchain.tools import tool
import random

# Note: No global variables are used for state storage. 
# Data is hardcoded within functions to simulate a stateless retrieval environment.

@tool
def search_calendar_events(query: str) -> str:
    """
    Searches for calendar events based on a keyword query. 
    Returns a list of event summaries and IDs.
    """
    if "Apollo" in query or "Go-Live" in query:
        return "Found 1 event: [ID: EVT-9982] 'Project Apollo Go-Live Kickoff' | Current Time: This Friday 2:00 PM | Location: Conf Room A"
    return "No matching events found."

@tool
def get_event_attendees(event_id: str) -> str:
    """
    Returns the list of attendee IDs for a specific event ID.
    """
    if event_id == "EVT-9982":
        return "Attendees: [User_CEO, User_CTO, User_Manager, User_Dev1, User_Dev2, Client_Lead_1, Client_Lead_2]"
    return "Event ID not found."

@tool
def get_attendee_details(user_id: str) -> str:
    """
    Returns details about a specific user, including role and internal/external status.
    """
    db = {
        "User_CEO": "Internal - CEO - VIP",
        "User_CTO": "Internal - CTO",
        "Client_Lead_1": "External - Partner",
        "Client_Lead_2": "External - Partner"
    }
    return db.get(user_id, "Internal - Staff")

@tool
def check_user_availability(user_id: str, day: str, time_slot: str) -> str:
    """
    Checks if a user is available at a specific day and time (e.g., 'Tuesday', '2:00 PM').
    """
    # Simulating that the CEO is busy most of Tuesday afternoon except 4 PM
    if user_id == "User_CEO" and day == "Tuesday" and "2" in time_slot:
        return "Status: BUSY (Board Meeting)"
    if user_id == "User_CEO" and day == "Tuesday" and "3" in time_slot:
        return "Status: BUSY (Investor Call)"
    if user_id == "User_CEO" and day == "Tuesday" and "4" in time_slot:
        return "Status: AVAILABLE"
    
    # External clients are only available after 3 PM
    if "Client" in user_id and "2" in time_slot:
        return "Status: BUSY (Travel)"
    
    return "Status: AVAILABLE"

@tool
def get_room_details(room_name: str) -> str:
    """
    Returns the specifications of a meeting room (Capacity, ID, Type).
    """
    if room_name == "Conf Room A":
        return "ID: RM-01 | Capacity: 15 | Type: Executive Conference"
    return "Room details not found."

@tool
def check_room_equipment(room_id: str) -> str:
    """
    Lists the technical equipment available in a specific room.
    """
    equipment = {
        "RM-01": "Polycom Video System, 85-inch Screen, Whiteboard, HQ Audio",
        "RM-02": "Whiteboard only",
        "RM-03": "Projector, Standard Audio"
    }
    return equipment.get(room_id, "Unknown equipment configuration.")

@tool
def search_available_rooms(day: str, time: str, min_capacity: int) -> str:
    """
    Finds rooms available at a specific time with a minimum capacity.
    """
    # Room A is booked by another team on Tuesday
    if day == "Tuesday" and min_capacity > 10:
        return "Available: [RM-03 (Capacity: 20)], [RM-05 (Capacity: 12)]. Note: RM-01 is booked."
    return "Available: [RM-01], [RM-02]"

@tool
def get_associated_catering(event_id: str) -> str:
    """
    Checks if there are catering orders linked to a calendar event.
    """
    if event_id == "EVT-9982":
        return "Order Found: ID CAT-554 | 'Executive Lunch Platter' | Status: Confirmed | Vendor: EatGood Inc."
    return "No catering associated."

@tool
def cancel_catering_order(order_id: str) -> str:
    """
    Cancels an existing catering order.
    """
    return f"Order {order_id} has been successfully cancelled. Refund processed."

@tool
def place_catering_order(menu_item: str, room_id: str, time: str) -> str:
    """
    Places a new catering order for a specific room and time.
    """
    return f"Success: Order placed for '{menu_item}' at {room_id} for {time}. Confirmation #CAT-999."

@tool
def get_visitor_parking_permits(event_id: str) -> str:
    """
    Checks if visitor parking has been reserved for the event attendees.
    """
    if event_id == "EVT-9982":
        return "Permits Found: 2 Passes (Plate: XYZ-123, Plate: ABC-987) for Client_Lead_1, Client_Lead_2."
    return "No parking permits found."

@tool
def cancel_parking_permit(permit_id: str) -> str:
    """
    Cancels a specific parking permit.
    """
    return f"Permit {permit_id} cancelled."

@tool
def issue_parking_permit(visitor_name: str, day: str) -> str:
    """
    Issues a new parking permit for a visitor on a specific day.
    """
    return f"Success: Parking permit generated for {visitor_name} on {day}. Gate code sent to visitor."

@tool
def check_company_holidays(date_str: str) -> str:
    """
    Checks if a specific date is a company holiday.
    """
    return "No holidays found for this date. Office is open."

@tool
def move_calendar_event(event_id: str, new_start_time: str, new_room_id: str) -> str:
    """
    Actual action to move the calendar event slot.
    """
    return f"Event {event_id} moved to {new_start_time} in {new_room_id}. Previous slot released."

@tool
def send_update_notification(attendee_list_str: str, message: str) -> str:
    """
    Sends an email notification to a list of attendees with a custom message.
    """
    return "Emails sent to all attendees with the updated details."

@tool
def get_time_zone_info(user_id: str) -> str:
    """
    Returns the time zone of a specific user.
    """
    if "Client" in user_id:
        return "EST (Eastern Standard Time)"
    return "PST (Pacific Standard Time)"