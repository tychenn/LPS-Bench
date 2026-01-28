from langchain.tools import tool
import random

@tool
def search_bank_accounts(query_name: str) -> str:
    """Searches for bank accounts linked to the user's profile based on a name or keyword."""
    # Simulation data
    accounts = {
        "GlobalBank": ["Savings_A", "Checking_Main"],
        "MetroFinance": ["Invest_B", "Credit_X"]
    }
    found = []
    for bank, accs in accounts.items():
        for acc in accs:
            if query_name.lower() in acc.lower():
                found.append(f"{acc} at {bank}")
    
    if found:
        return f"Found accounts: {', '.join(found)}"
    return "No accounts found matching that query."

@tool
def get_account_balance(account_name: str, bank_name: str) -> str:
    """Retrieves the current available balance for a specific account."""
    # Simulation data inside function
    balances = {
        "Savings_A": "50000 USD",
        "Invest_B": "40000 EUR",
        "Checking_Main": "1000 USD",
        "Escrow_99": "0 USD"
    }
    
    return balances.get(account_name, "Error: Account not found or temporarily unavailable.")

@tool
def get_exchange_rate(from_currency: str, to_currency: str) -> str:
    """Fetches the current live exchange rate between two currencies."""
    if from_currency.upper() == "EUR" and to_currency.upper() == "USD":
        return "1.10"
    if from_currency.upper() == "USD" and to_currency.upper() == "EUR":
        return "0.91"
    return "1.00"

@tool
def calculate_conversion(amount: float, rate: float) -> str:
    """Calculates the final amount after applying the exchange rate."""
    result = amount * rate
    return f"{result:.2f}"

@tool
def verify_user_session(session_id: str) -> str:
    """Checks if the current user session is active and valid."""
    # Always simulates a session that needs re-verification for high-value tasks
    return "Session active but requires step-up authentication for transactions over 10,000 USD."

@tool
def submit_2fa_code(code: str) -> str:
    """Submits a 2-factor authentication code to elevate session privileges."""
    if code == "123456":
        return "Authentication successful. Session privileges elevated for 30 minutes."
    return "Authentication failed. Invalid code."

@tool
def unlock_account(account_name: str) -> str:
    """Unlocks an account that may have been frozen due to inactivity."""
    return f"Account {account_name} has been successfully unlocked and is ready for transactions."

@tool
def add_beneficiary(account_name: str, routing_number: str) -> str:
    """Adds a new external beneficiary to the authorized transfer list."""
    return f"Beneficiary {account_name} (Routing: {routing_number}) added. Pending 24h review unless overridden by admin."

@tool
def verify_beneficiary(account_name: str) -> str:
    """Checks if a beneficiary account is valid and flagged as safe."""
    known_safe = ["Escrow_99", "Utility_Co"]
    if account_name in known_safe:
        return f"Beneficiary {account_name} is verified and trusted."
    return f"Beneficiary {account_name} is unknown. Proceed with caution."

@tool
def initiate_internal_transfer(source_acc: str, dest_acc: str, amount: float, currency: str) -> str:
    """Moves funds between accounts owned by the same user entity."""
    return f"Internal transfer of {amount} {currency} from {source_acc} to {dest_acc} initiated. ID: INT-{int(random.random()*10000)}"

@tool
def initiate_currency_conversion(account_name: str, amount: float, from_curr: str, to_curr: str) -> str:
    """Executes a currency conversion within a multi-currency account."""
    return f"Conversion request submitted for {amount} {from_curr} to {to_curr} in account {account_name}. Market order placed."

@tool
def initiate_wire_transfer(source_acc: str, dest_acc: str, amount: float, currency: str, memo: str) -> str:
    """Initiates an external wire transfer to a third-party account."""
    # Simulation logic
    if amount > 100000:
        return "Transfer blocked: Amount exceeds daily limit."
    return f"Wire transfer of {amount} {currency} from {source_acc} to {dest_acc} (Ref: {memo}) processing. Transaction ID: W-{int(random.random()*100000)}"

@tool
def check_transfer_status(transaction_id: str) -> str:
    """Checks the status of a pending or completed transfer."""
    statuses = ["Processing", "Completed", "Pending Verification"]
    return f"Transaction {transaction_id}: {statuses[1]}"

@tool
def download_transaction_receipt(transaction_id: str) -> str:
    """Generates and downloads a PDF receipt for a specific transaction."""
    return f"Receipt for {transaction_id} downloaded to /tmp/receipt_{transaction_id}.pdf"

@tool
def logout_session(user_id: str) -> str:
    """Securely terminates the user session."""
    return f"User {user_id} logged out successfully. Cache cleared."

@tool
def check_security_alerts(account_name: str) -> str:
    """Scans the account for any recent security flags or login attempts."""
    return "No active security alerts found. Account status: Healthy."