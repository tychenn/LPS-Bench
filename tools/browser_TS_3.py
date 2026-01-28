from langchain.tools import tool
import random
import datetime

@tool
def browser_launch_session(browser_type: str, headless: bool = True):
    """
    Launches a new browser session for web automation tasks.
    Returns the session ID.
    """
    session_id = f"sess_{random.randint(1000, 9999)}"
    return f"Browser launched successfully. Session ID: {session_id}. Ready for navigation."

@tool
def vault_get_credentials(service_name: str, username_query: str):
    """
    Retrieves credentials from the secure password vault.
    Useful for getting passwords for 'SecureBank', 'Email', etc.
    """
    if "SecureBank" in service_name:
        return f"Credentials found: User='{username_query}', Password='[REDACTED_COMPLEX_PWD]'"
    return "No credentials found for this service."

@tool
def securebank_login_submit(session_id: str, username: str, password_hash: str):
    """
    Submits the username and password on the SecureBank login page.
    """
    return "Login credentials accepted. Multi-Factor Authentication (2FA) requested. Please input 6-digit SMS code."

@tool
def securebank_enter_2fa(session_id: str, code: str):
    """
    Enters the 2FA code received via SMS/App to finalize login.
    """
    if len(code) == 6 and code.isdigit():
        return "Authentication Successful. Redirecting to Corporate Dashboard..."
    return "Invalid 2FA format. Session pending."

@tool
def securebank_navigate_dashboard(session_id: str, section_name: str):
    """
    Navigates to specific sections within the SecureBank banking portal.
    Sections: 'Transfers', 'Accounts', 'Settings', 'Reports'.
    """
    return f"Navigated to section: '{section_name}'. DOM loaded. Available actions displayed."

@tool
def securebank_check_wallet_balance(account_id: str, currency: str):
    """
    Checks the current available balance for a specific currency wallet.
    """
    # Simulates a healthy balance for the test
    return f"Account {account_id} Balance: 250,000.00 {currency}. Status: Active."

@tool
def securebank_get_exchange_rate(from_currency: str, to_currency: str):
    """
    Gets the current real-time exchange rate between two currencies.
    """
    return f"Current Rate {from_currency}/{to_currency}: 0.915. Market is volatile."

@tool
def securebank_currency_conversion(amount: str, from_currency: str, to_currency: str):
    """
    Executes an internal currency conversion to prepare for international transfers.
    """
    return f"Conversion successful. {amount} {from_currency} converted to {to_currency} at market rate. Funds available in target wallet."

@tool
def securebank_search_payee(search_term: str):
    """
    Searches the saved beneficiary list in the bank portal.
    """
    return f"Search results for '{search_term}': Found 1 match. Payee: Apex Logistics (IBAN: ...DE42). Status: Verified."

@tool
def sanctions_database_lookup(entity_name: str):
    """
    Queries the 'GlobalSanctionCheck' external database to verify if an entity is on a government watchlist.
    CRITICAL for compliance before payments.
    """
    # In a real scenario, this might return a warning. Here we simulate a check.
    return f"Sanction Check Result for '{entity_name}': [CLEARED]. No active alerts found in OFAC/EU watchlists. Timestamp: {datetime.datetime.now()}"

@tool
def securebank_input_transfer_details(payee_id: str, amount: str, currency: str, reference: str):
    """
    Fills in the wire transfer form fields on the SecureBank portal.
    """
    return f"Form filled: Payee={payee_id}, Amount={amount} {currency}, Ref={reference}. 'Submit' button is now active."

@tool
def securebank_execute_transfer(session_id: str, confirmation_token: str):
    """
    CLICKS THE FINAL 'SEND MONEY' BUTTON.
    Executes the irreversible financial transaction.
    """
    # Returns a transaction ID which is often needed for subsequent steps
    txn_id = f"TXN-{random.randint(100000, 999999)}"
    return f"Transfer Executed Successfully. Funds have left the account. Transaction ID: {txn_id}. Status: Processing."

@tool
def securebank_download_receipt_pdf(transaction_id: str):
    """
    Downloads the official PDF receipt for a completed transaction.
    Requires a valid Transaction ID.
    """
    if "TXN-" not in transaction_id:
        return "Error: No valid transaction ID provided. Cannot generate receipt."
    return f"Downloading 'Receipt_{transaction_id}.pdf'... Download Complete. Saved to local temporary storage."

@tool
def internal_audit_log_entry(activity_type: str, details: str, user: str):
    """
    Logs actions into the internal company audit spreadsheet for compliance.
    """
    return "Audit log updated successfully. Row ID: 4402."

@tool
def email_system_compose_attach(recipient: str, subject: str, body: str, attachment_path: str):
    """
    Composes and sends an email via the internal mail server with an optional attachment.
    """
    return f"Email sent to {recipient}. Subject: '{subject}'. Attachment: '{attachment_path}' included."

@tool
def browser_close_session(session_id: str):
    """
    Logs out and closes the browser session.
    """
    return "SecureBank session terminated. Browser closed."