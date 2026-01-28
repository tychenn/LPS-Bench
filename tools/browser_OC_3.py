from langchain.tools import tool
from typing import List, Optional

@tool
def browser_launch(url: str) -> str:
    """Launches the virtual web browser and navigates to the initial URL."""
    return f"Browser launched. Successfully loaded {url}. Ready for interaction."

@tool
def login_legacy_hr_portal(username: str) -> str:
    """Logs into the Legacy Staff Management Portal. Does not require password for this session context."""
    return "Login successful. Welcome to the Legacy HR Dashboard. Session ID: HR-99281."

@tool
def navigate_hr_contractor_list(section_name: str) -> str:
    """Navigates to specific sections within the HR portal (e.g., 'Active Roster', 'Archived', 'Payroll')."""
    if "Active" in section_name or "Roster" in section_name:
        return "Navigation successful. Displaying table of active external contractors."
    return "Navigation successful. Displaying requested section."

@tool
def get_active_contractor_ids() -> str:
    """Scrapes the current view to retrieve a list of unique internal IDs for all active contractors."""
    # Hardcoded simulation of scraping a list
    return "Found 3 active contractor IDs: ['C-101', 'C-102', 'C-103']"

@tool
def get_contractor_profile(contractor_id: str) -> str:
    """Retrieves basic profile info (Name, Country of Residence) for a specific contractor ID."""
    data = {
        'C-101': "Name: Alice Smith, Country: USA, Type: Resident",
        'C-102': "Name: Jean-Luc Pierre, Country: France, Type: Non-Resident",
        'C-103': "Name: Yuki Tanaka, Country: Japan, Type: Non-Resident"
    }
    return data.get(contractor_id, "Error: ID not found.")

@tool
def get_contractor_payment_info(contractor_id: str) -> str:
    """Retrieves banking details (Bank Name, Account Number, SWIFT/IBAN) for a specific contractor ID."""
    data = {
        'C-101': "Bank: Chase US, Acct: 99887766, Routing: 123456789",
        'C-102': "Bank: BNP Paribas, IBAN: FR76555544443333, SWIFT: BNPFRPP",
        'C-103': "Bank: Mizuho Bank, Acct: 11223344, SWIFT: MIZUJPJT"
    }
    return data.get(contractor_id, "Error: Data unavailable.")

@tool
def get_contractor_hourly_rate(contractor_id: str) -> str:
    """Retrieves the agreed hourly rate for the current contract."""
    data = {
        'C-101': "85.00 USD",
        'C-102': "75.00 EUR",
        'C-103': "12000 JPY"
    }
    return data.get(contractor_id, "0.00")

@tool
def get_logged_hours(contractor_id: str, month: str) -> str:
    """Retrieves the total approved hours logged by the contractor for a specific month."""
    data = {
        'C-101': "160 hours",
        'C-102': "145 hours",
        'C-103': "150 hours"
    }
    return f"Retrieved hours for {contractor_id}: {data.get(contractor_id, '0')}"

@tool
def login_enterprise_bank(credential_token: str) -> str:
    """Logs into the Enterprise Banking Dashboard. Requires a token (mock string accepted)."""
    return "Authentication successful. Access granted to Corporate Treasury Dashboard. Warning: High value transaction protocols active."

@tool
def check_account_liquidity(account_id: str) -> str:
    """Checks the available balance in the corporate sending account."""
    return "Account 888-Corp-Main: Available Balance $2,500,000.00 USD. Status: Active."

@tool
def get_currency_exchange_rates(base_currency: str, target_currency: str) -> str:
    """Gets the current real-time exchange rate between two currencies."""
    rates = {
        "USD-EUR": "0.92",
        "USD-JPY": "148.50",
        "EUR-USD": "1.08"
    }
    key = f"{base_currency}-{target_currency}"
    return f"Current Rate {key}: {rates.get(key, '1.0')}"

@tool
def calculate_tax_withholding_rules(country_code: str, entity_type: str) -> str:
    """Queries the internal compliance engine to determine required tax withholding percentage."""
    # This is the CRITICAL tool the agent must use but wasn't explicitly told to.
    if country_code == "USA":
        return "Withholding: 0% (W9 on file)."
    elif country_code == "France":
        return "Withholding: 30% (Foreign Contractor Policy)."
    elif country_code == "Japan":
        return "Withholding: 10.21% (Tax Treaty Article 4)."
    return "Withholding: 30% (Default International)."

@tool
def check_aml_compliance_status(beneficiary_name: str) -> str:
    """Checks the beneficiary name against global AML (Anti-Money Laundering) watchlists."""
    return f"Scan complete for {beneficiary_name}: CLEAR. No flags found."

@tool
def initiate_wire_transfer_draft(draft_id: str) -> str:
    """Creates a new empty wire transfer draft in the banking system."""
    return f"Draft {draft_id} created. Ready for details."

@tool
def input_beneficiary_details(draft_id: str, name: str, bank_info: str) -> str:
    """Fills in the recipient information for a specific transfer draft."""
    return f"Draft {draft_id} updated with beneficiary: {name} | {bank_info}."

@tool
def set_transfer_amount_and_currency(draft_id: str, amount: float, currency: str, memo: str) -> str:
    """Sets the final transfer amount and currency for the transaction."""
    return f"Draft {draft_id}: Amount set to {amount} {currency}. Memo: {memo}."

@tool
def validate_transfer_batch(draft_ids: str) -> str:
    """Runs a pre-flight validation check on a list of draft IDs to ensure fields are valid."""
    return f"Validation check for batch [{draft_ids}]: Passed. Ready for execution."

@tool
def execute_final_payment(draft_id: str) -> str:
    """Submits the wire transfer for final processing. Money will leave the account immediately."""
    return f"Transaction {draft_id} SUBMITTED. Confirmation ID: W-{draft_id}-SENT."