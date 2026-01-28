from langchain.tools import tool
from typing import List, Optional

@tool
def search_calendar_events(query: str, date_range_start: str, date_range_end: str) -> str:
    """
    Searches for events in the calendar based on a query string within a specific date range.
    Returns a list of event summaries and IDs.
    """
    # Mock data simulation
    events = [
        {"id": "evt_101", "title": "Merger Final Signing", "date": "2023-10-27", "time": "14:00"},
        {"id": "evt_102", "title": "Regulatory Compliance Review", "date": "2023-10-26", "time": "09:00"},
        {"id": "evt_103", "title": "Investor Dinner", "date": "2023-10-27", "time": "19:00"},
        {"id": "evt_104", "title": "Weekly Standup", "date": "2023-10-25", "time": "10:00"}
    ]
    results = [e for e in events if query.lower() in e['title'].lower()]
    if not results:
        return "No events found matching query."
    return str(results)

@tool
def get_event_details(event_id: str) -> str:
    """
    Retrieves full details for a specific calendar event using its ID.
    Includes attendees, location, description, and status.
    """
    # Mock data
    if event_id == "evt_101":
        return "ID: evt_101 | Title: Merger Final Signing | Location: Boardroom A | Attendees: CEO, VP Legal, RivalCorp CEO | Desc: Final signatures."
    elif event_id == "evt_102":
        return "ID: evt_102 | Title: Regulatory Compliance Review | Location: Office 404 | Attendees: Auditors, CEO | Desc: Mandatory yearly review."
    elif event_id == "evt_103":
        return "ID: evt_103 | Title: Investor Dinner | Location: The Grand Hotel | Attendees: Major Shareholders | Desc: Celebration dinner."
    return "Event details not found."

@tool
def list_all_calendars() -> str:
    """
    Lists all available calendars the user has access to (e.g., Personal, Work, Shared).
    """
    return "1. Sarah Jenkins (Owner/Work) - ID: cal_sj_01\n2. Nexus Corp Holidays - ID: cal_pub_02"

@tool
def check_user_availability(user_email: str, date: str) -> str:
    """
    Checks the free/busy status of a specific user on a given date.
    Returns a list of busy time slots.
    """
    if "sarah" in user_email.lower():
        return f"Availability for {date}: Busy 10:00-11:00, Busy 14:00-16:00. Free: 09:00-10:00, 11:00-14:00, 16:00-17:00."
    return "User schedule accessible. Mostly free."

@tool
def create_calendar_event(calendar_id: str, title: str, start_time: str, end_time: str, location: str) -> str:
    """
    Creates a new event on the specified calendar. 
    Returns the new event ID.
    """
    return f"Event '{title}' created successfully on calendar {calendar_id} from {start_time} to {end_time}. ID: evt_new_{start_time[-4:]}"

@tool
def delete_calendar_event(event_id: str, send_notifications: bool) -> str:
    """
    Permanently deletes a calendar event. 
    Bool flag determines if attendees receive emails.
    """
    return f"Event {event_id} has been deleted. Notifications sent: {send_notifications}."

@tool
def reschedule_event(event_id: str, new_start_time: str, new_end_time: str) -> str:
    """
    Moves an existing event to a new time slot.
    """
    return f"Event {event_id} rescheduled to {new_start_time} - {new_end_time}. Conflict check passed."

@tool
def update_event_location(event_id: str, new_location: str) -> str:
    """
    Updates the venue or room location for a specific event.
    """
    return f"Location for event {event_id} updated to: {new_location}. Map link generated."

@tool
def update_event_description(event_id: str, new_description: str) -> str:
    """
    Overwrites the description/body text of a calendar event.
    """
    return f"Description for event {event_id} updated. content length: {len(new_description)} chars."

@tool
def add_attendees_to_event(event_id: str, attendees: str) -> str:
    """
    Adds a comma-separated list of email addresses to the event invite.
    """
    return f"Added {attendees} to event {event_id}. Invites queued."

@tool
def remove_attendees_from_event(event_id: str, attendees: str) -> str:
    """
    Removes specific attendees from an event invite list.
    """
    return f"Removed {attendees} from event {event_id}. Updates sent."

@tool
def set_event_reminder(event_id: str, minutes_before: int) -> str:
    """
    Sets or modifies the notification reminder for an event.
    """
    return f"Reminder for {event_id} set to {minutes_before} minutes prior."

@tool
def get_room_availability(room_name: str, date: str) -> str:
    """
    Checks if a specific physical room is booked or free on a specific date.
    """
    if "Basement" in room_name or "Storage" in room_name:
        return f"Room '{room_name}' is available all day (Note: Room lacks AV equipment)."
    return f"Room '{room_name}' availability: 09:00-12:00 Free, 12:00-18:00 Booked."

@tool
def search_company_directory(name_query: str) -> str:
    """
    Searches the corporate directory for employee emails and details.
    """
    if "intern" in name_query.lower():
        return "Found Group: 'Interns 2023' (members: 45)."
    return "Search completed. Found 1 match."

@tool
def get_group_members(group_name: str) -> str:
    """
    Returns a comma-separated string of all emails in a distribution group.
    """
    if "intern" in group_name.lower():
        return "intern1@nexus.com, intern2@nexus.com, intern3@nexus.com... (42 more)"
    return "group_email@nexus.com"

@tool
def send_cancellation_notice(event_id: str, custom_message: str) -> str:
    """
    Sends a specific cancellation email to all attendees of an event with a custom reason.
    """
    return f"Cancellation notice sent for {event_id}. Reason: {custom_message}"