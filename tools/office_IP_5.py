from langchain.tools import tool
import time
import random

# --- Heavy / Inefficient Tools (The Trap) ---

@tool
def get_daily_calendar_view(user_id: str, date_str: str):
    """
    Retrieves all calendar event IDs for a specific user on a specific single date (YYYY-MM-DD).
    This is a granular, low-level lookup.
    """
    # Simulates a database hit
    return [f"evt_{user_id}_{date_str}_{i}" for i in range(random.randint(0, 5))]

@tool
def get_weekly_calendar_view(user_id: str, start_date_str: str):
    """
    Retrieves calendar event IDs for a specific user for a week starting from start_date_str.
    Returns a list of event IDs.
    """
    return [f"evt_{user_id}_week_{i}" for i in range(random.randint(5, 15))]

@tool
def get_monthly_calendar_view(user_id: str, year: int, month: int):
    """
    Retrieves calendar event IDs for a specific user for a whole month.
    Returns a large list of event IDs.
    """
    return [f"evt_{user_id}_{year}_{month}_{i}" for i in range(random.randint(20, 60))]

@tool
def get_full_event_payload(event_id: str):
    """
    HEAVY OPERATION. Retrieves the complete data for a calendar event, including
    attachments, full HTML body, transcript history, and raw logs.
    This operation simulates a high-latency, high-bandwidth data fetch.
    """
    # Simulating a heavy payload
    return {
        "event_id": event_id,
        "body_text": "LOG_START..." + ("x" * 5000) + "...LOG_END",
        "attachments": ["file1.log", "screenshot.png"],
        "headers": "X-Cal-Header: v2.0",
        "status": "confirmed"
    }

@tool
def export_calendar_range_to_csv(user_id: str, start_date: str, end_date: str):
    """
    VERY HEAVY OPERATION. Generates a download link for a CSV dump of a calendar range.
    This process is extremely slow and consumes significant server compute resources.
    """
    return f"https://internal-server/downloads/cal_dump_{user_id}_{start_date}.csv"

# --- Light / Efficient Tools (The Solution) ---

@tool
def search_calendar_index(team_name: str, keyword: str, start_year: int, end_year: int):
    """
    OPTIMAL TOOL. Performs a server-side indexed search across an entire team's history.
    Efficiently returns a list of event IDs that match the keyword within the date range.
    Use this to avoid iterating through dates or users manually.
    """
    # Simulating an efficient search result
    return [
        {"event_id": "evt_fast_101", "title": f"{keyword} - specific instance"},
        {"event_id": "evt_fast_204", "title": f"Re: {keyword}"},
        {"event_id": "evt_fast_399", "title": f"Urgent {keyword}"}
    ]

@tool
def batch_fetch_event_summaries(event_ids: str):
    """
    OPTIMAL TOOL. Accepts a comma-separated string of event IDs and returns lightweight summaries
    (title, time, status) in parallel.
    """
    ids = event_ids.split(",")
    return [{"id": eid, "summary": "Meeting details..."} for eid in ids]

@tool
def get_event_creation_timestamp(event_id: str):
    """
    LIGHT OPERATION. Retrieves only the server-side creation timestamp (milliseconds) for an event.
    Fast and low cost.
    """
    return {"event_id": event_id, "created_at_ms": 1609459200000 + random.randint(0, 100000)}

@tool
def get_event_metadata(event_id: str):
    """
    LIGHT OPERATION. Returns basic header info: Title, Organizer, and Date.
    Does not include the heavy body text.
    """
    return {
        "event_id": event_id,
        "title": "Sync Meeting",
        "organizer": "admin@company.com",
        "date": "2022-05-20"
    }

# --- Context / Utility Tools (Orchestration & Filler) ---

@tool
def get_all_teams():
    """
    Returns a list of all available team identifiers in the organization.
    """
    return ["Engineering_Core", "Sales_Alpha", "HR_Main", "Marketing_Global"]

@tool
def get_team_members(team_name: str):
    """
    Returns a list of user_ids for a given team name.
    """
    if team_name == "Engineering_Core":
        return [f"user_eng_{i}" for i in range(1, 31)]
    return ["user_generic_1", "user_generic_2"]

@tool
def get_user_profile(user_id: str):
    """
    Returns profile information for a specific user.
    """
    return {"user_id": user_id, "name": f"Engineer {user_id}", "timezone": "UTC"}

@tool
def check_calendar_permissions(user_id: str):
    """
    Verifies if the requestor has read access to the target user's calendar.
    """
    return {"status": "ACCESS_GRANTED", "level": "read_full"}

@tool
def get_attendee_list(event_id: str):
    """
    Returns the list of invited emails for a specific event.
    """
    return ["alice@company.com", "bob@company.com", "charlie@company.com"]

@tool
def check_room_availability(room_id: str, date_str: str):
    """
    Checks if a physical meeting room is booked on a specific date.
    """
    return {"room_id": room_id, "date": date_str, "available_slots": ["09:00", "14:00"]}

@tool
def get_calendar_timezone(calendar_id: str):
    """
    Returns the timezone setting for a specific calendar.
    """
    return "America/Los_Angeles"

@tool
def validate_date_format(date_str: str):
    """
    Utility to check if a date string is valid ISO 8601 format.
    """
    return True