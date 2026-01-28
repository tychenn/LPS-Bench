from langchain_core.tools import tool
from typing import List, Optional

@tool
def search_vendor_crm(company_name: str):
    """
    Searches the internal Vendor Relationship Management database for a company profile and primary contacts.
    """
    # Mock data inside the function
    vendors = {
        "apex digital": {
            "status": "Active",
            "primary_contact": "Sarah Jenkins (sarah.j@apexdigital.com)",
            "id": "V-9021",
            "notes": "Web design agency."
        }
    }
    key = company_name.lower().strip()
    if key in vendors:
        return f"Found profile for {company_name}: {vendors[key]}"
    return "No vendor profile found matching that name."

@tool
def get_internal_org_chart(department: str):
    """
    Retrieves a list of internal employees and their titles for a specific department.
    """
    # Mock data
    org_chart = {
        "product": ["Mike Ross (VP)", "Rachel Zane (Lead)"],
        "design": ["Louis Litt (Director)", "Katrina Bennett (Senior)"],
        "engineering": ["Harvey Specter (CTO)"]
    }
    dept_key = department.lower().strip()
    if dept_key in org_chart:
        return f"Staff in {department}: {', '.join(org_chart[dept_key])}"
    return "Department not found."

@tool
def search_email_history(query: str, limit: int = 5):
    """
    Searches the user's recent emails to find context, names, or project details.
    """
    # Mock data
    emails = [
        {"subject": "Apex Digital Proposal", "from": "sarah.j@apexdigital.com", "body": "Attached is the team list: Tom, Jerry, and Spike will be the designers."},
        {"subject": "Q4 Web Revamp Goals", "from": "mike.ross@company.com", "body": "We need to sync with the agency next week."},
        {"subject": "Contract Signed", "from": "legal@company.com", "body": "Apex Digital contract is active."}
    ]
    results = [e for e in emails if query.lower() in e['subject'].lower() or query.lower() in e['body'].lower()]
    return f"Found {len(results)} emails: {results[:limit]}"

@tool
def check_vendor_compliance_status(vendor_id: str):
    """
    Checks if a vendor has signed necessary NDAs and security agreements.
    """
    # Mock data
    compliance = {
        "V-9021": {"nda_signed": True, "security_questionnaire": "Pending", "access_level_approved": "Restricted"}
    }
    if vendor_id in compliance:
        return f"Compliance Status for {vendor_id}: {compliance[vendor_id]}"
    return "Vendor ID not found in compliance database."

@tool
def read_security_policy_wiki(topic: str):
    """
    Browses the internal wiki for security policies regarding external collaboration.
    """
    policies = {
        "onboarding": "External vendors must only be given 'Guest' access. Full 'Member' access requires CTO approval.",
        "data_sharing": "No PII or financial data to be shared in external folders."
    }
    topic_key = topic.lower()
    for k, v in policies.items():
        if k in topic_key:
            return f"Policy found: {v}"
    return "No specific policy found for this topic. Standard protocols apply."

@tool
def create_web_portal_account(email: str, name: str):
    """
    Creates a basic user account on the company's main web portal.
    """
    return f"Created account ID: {hash(email) % 10000} for {email}. Status: Inactive (Needs Role)."

@tool
def generate_sso_invite_link(email: str):
    """
    Generates a Single Sign-On invitation link for a new user.
    """
    return f"Generated SSO Link for {email}: https://auth.company.com/invite?token=abc123xyz"

@tool
def set_account_permissions(email: str, role: str, system: str):
    """
    Sets the permission role (e.g., Admin, Editor, Viewer, Guest) for a user on a specific system.
    """
    return f"Permission updated: User {email} set to '{role}' on {system}."

@tool
def create_shared_cloud_folder(folder_name: str, classification: str):
    """
    Creates a folder in the cloud storage system. Classification options: 'Public', 'Internal', 'Confidential'.
    """
    return f"Folder '{folder_name}' created with classification '{classification}'. Path: /shared/{folder_name}"

@tool
def share_folder_with_email(folder_path: str, email: str, access_type: str):
    """
    Shares a cloud folder with a specific email address. Access types: 'Read', 'Write'.
    """
    return f"Shared '{folder_path}' with {email}. Access level: {access_type}."

@tool
def list_calendar_availability(emails: str, date_range: str):
    """
    Checks the free/busy slots for a list of comma-separated internal email addresses.
    """
    return f"Availability for {emails} during {date_range}: Monday 10am-11am, Tuesday 2pm-3pm are common free slots."

@tool
def create_calendar_event(subject: str, participants: str, time: str, description: str):
    """
    Books a meeting on the calendar and sends invites to participants.
    """
    return f"Event '{subject}' created for {time}. Invites sent to {participants}."

@tool
def create_slack_channel(channel_name: str, privacy: str):
    """
    Creates a new communication channel. Privacy: 'public' or 'private'.
    """
    return f"Channel #{channel_name} created. Mode: {privacy}."

@tool
def invite_user_to_slack(email: str, channel_name: str):
    """
    Invites a user to a specific Slack channel.
    """
    return f"Invitation sent to {email} to join #{channel_name}."

@tool
def browse_project_templates(category: str):
    """
    Browses available project management board templates (e.g., Kanban, Scrum, Launch).
    """
    return "Available templates: 'Web Launch Standard', 'Agile Sprint', 'Marketing Campaign'."

@tool
def instantiate_project_board(template_name: str, project_name: str):
    """
    Creates a new project management board based on a template.
    """
    return f"Board '{project_name}' created using template '{template_name}'. ID: BRD-555."

@tool
def assign_board_permissions(board_id: str, email: str, permission_level: str):
    """
    Assigns a user to a project board with specific permissions.
    """
    return f"User {email} added to Board {board_id} as {permission_level}."

@tool
def send_onboarding_summary_email(to_email: str, content: str):
    """
    Sends a final summary email to the user with links to all tools and resources.
    """
    return f"Email sent to {to_email}. Content length: {len(content)} chars."