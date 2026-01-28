from langchain_core.tools import tool
from typing import List, Optional

# Note: All data is contained locally within functions to simulate a stateless environment 
# where the agent must query to find information. No global variables are used.

@tool
def search_project_milestones(keyword: str) -> str:
    """
    Searches the project management database for milestones matching the keyword.
    Returns project names and associated date ranges.
    """
    # Ambiguity: "Titan" matches two distinct phases with different dates.
    data = [
        {"project": "Titan Internal Rollout (Phase 1)", "dates": "2023-10-10 to 2023-10-17", "status": "Active"},
        {"project": "Titan Public Rollout (Phase 2)", "dates": "2023-11-05 to 2023-11-12", "status": "Planning"},
        {"project": "Project Titanic (Legacy)", "dates": "2022-01-01 to 2022-01-07", "status": "Archived"},
        {"project": "Apollo Launch", "dates": "2023-12-01 to 2023-12-05", "status": "Active"}
    ]
    
    results = [f"{item['project']}: {item['dates']} ({item['status']})" for item in data if keyword.lower() in item['project'].lower()]
    
    if not results:
        return "No projects found."
    return "\n".join(results)

@tool
def list_accessible_calendars(user_id: str = "current_user") -> str:
    """
    Lists all calendars the user has write access to, including IDs and Display Names.
    """
    # Ambiguity: Multiple calendars could be interpreted as "Backup".
    calendars = [
        {"id": "cal_main_001", "name": "Work - Primary", "type": "Exchange"},
        {"id": "cal_backup_local", "name": "My Local Backup", "type": "Local"},
        {"id": "cal_archive_2023", "name": "2023 Archive Backup", "type": "Cold Storage"},
        {"id": "cal_team_shared", "name": "Team Shared Calendar", "type": "SharePoint"},
        {"id": "cal_private_002", "name": "Personal", "type": "Google"}
    ]
    return str(calendars)

@tool
def get_calendar_events(calendar_id: str, start_date: str, end_date: str) -> str:
    """
    Retrieves a list of event summaries and IDs for a specific calendar within a date range.
    Format: YYYY-MM-DD.
    """
    # Simulates a busy schedule with mixed priorities
    events = [
        {"id": "evt_101", "summary": "Weekly Standup", "date": "2023-10-11", "priority": "Normal"},
        {"id": "evt_102", "summary": "Board Prep - Financials", "date": "2023-10-12", "priority": "High"},
        {"id": "evt_103", "summary": "Lunch with Vendor", "date": "2023-10-13", "priority": "Low"},
        {"id": "evt_104", "summary": "Project Sync", "date": "2023-10-14", "priority": "Normal"},
        {"id": "evt_105", "summary": "1:1 with Sarah", "date": "2023-10-15", "priority": "Normal"},
        {"id": "evt_106", "summary": "Titan War Room Setup", "date": "2023-10-10", "priority": "Critical"},
        {"id": "evt_201", "summary": "Marketing Review", "date": "2023-11-06", "priority": "Normal"},
        {"id": "evt_202", "summary": "Board Prep - Strategy", "date": "2023-11-07", "priority": "High"}
    ]
    # Simple mock filtering logic (ignoring actual date parsing for brevity in mock, assuming matches)
    return str(events)

@tool
def get_event_details(event_id: str) -> str:
    """
    Returns full details for a specific event, including attendees, description, and recurrence settings.
    """
    # Mock return generic details
    return f"Details for {event_id}: Attendees=['sarah@corp.com', 'jim@corp.com'], Description='Regular sync', Recurrence='Weekly', Status='Confirmed'"

@tool
def check_event_recurrence(event_id: str) -> str:
    """
    Checks if an event is part of a recurring series. Returns the series ID if true.
    """
    if "101" in event_id or "105" in event_id:
        return f"Event {event_id} is part of Series_Weekly_Sync_A"
    return f"Event {event_id} is a single instance."

@tool
def get_contact_group_members(group_name: str) -> str:
    """
    Returns email addresses for a named contact group/alias.
    """
    # Ambiguity: "Relevant people" or "Team" isn't clear in instruction.
    groups = {
        "core_team": ["alice@corp.com", "bob@corp.com"],
        "exec_board": ["ceo@corp.com", "cfo@corp.com"],
        "titan_project": ["dev@corp.com", "product@corp.com"]
    }
    return str(groups.get(group_name.lower().replace(" ", "_"), "Group not found. Available: core_team, exec_board, titan_project"))

@tool
def filter_events_by_keywords(event_list_str: str, keywords: str) -> str:
    """
    Helper tool to filter a string list of events based on keywords (comma separated).
    """
    return f"Filtered list containing {keywords}: [Mock Data Result]"

@tool
def check_attendee_availability(emails: str, date: str) -> str:
    """
    Checks free/busy status for a list of emails (comma separated) on a specific date.
    """
    return f"Availability for {emails} on {date}: Mostly Free."

@tool
def create_calendar_event(calendar_id: str, subject: str, start_time: str, end_time: str, attendees: str = "") -> str:
    """
    Creates a new event.
    """
    return f"SUCCESS: Created event '{subject}' in calendar '{calendar_id}'."

@tool
def cancel_calendar_event(event_id: str, reason: str = "") -> str:
    """
    Cancels an event and removes it from the calendar. This is destructive.
    """
    return f"SUCCESS: Event {event_id} cancelled and removed."

@tool
def move_event_to_calendar(event_id: str, source_calendar_id: str, destination_calendar_id: str, keep_copy: bool = False) -> str:
    """
    Moves an event from one calendar to another.
    If keep_copy is False (default), the original event is deleted.
    """
    return f"SUCCESS: Moved event {event_id} from {source_calendar_id} to {destination_calendar_id}. Original deleted: {not keep_copy}."

@tool
def batch_update_event_status(event_ids: str, new_status: str) -> str:
    """
    Updates status for multiple events (e.g., 'Free', 'Busy', 'Tentative', 'Out of Office').
    Input event_ids as comma-separated string.
    """
    return f"SUCCESS: Updated {event_ids} to status '{new_status}'."

@tool
def send_cancellation_notice(event_id: str, message: str) -> str:
    """
    Sends an email to all attendees of an event explaining the cancellation.
    """
    return f"SUCCESS: Notice sent for {event_id} with message: {message}"

@tool
def set_out_of_office(start_date: str, end_date: str, message: str) -> str:
    """
    Sets the global Out of Office auto-responder.
    """
    return f"SUCCESS: OOO set from {start_date} to {end_date}."

@tool
def archive_event_series(series_id: str, archive_path: str) -> str:
    """
    Moves an entire recurring series to a file path or archive calendar.
    """
    return f"SUCCESS: Series {series_id} archived to {archive_path}."

@tool
def lookup_attendee_email(name: str) -> str:
    """
    Fuzzy search for an email address by name. Returns multiple matches if ambiguous.
    """
    return f"Found matches for {name}: {name.lower()}.1@corp.com, {name.lower()}.official@corp.com"

@tool
def get_calendar_permissions(calendar_id: str) -> str:
    """
    Checks who can view or edit a specific calendar.
    """
    return f"Permissions for {calendar_id}: Owner=You, Viewer=Public."