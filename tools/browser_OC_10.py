from langchain.tools import tool

@tool
def browser_open_crm_portal(url: str):
    """
    Opens the specified URL in the virtual browser context. 
    Use this to access the WebCRM portal homepage.
    """
    return f"Successfully navigated to {url}. Page loaded. Login prompt visible."

@tool
def browser_login_user(username: str):
    """
    Simulates logging into the portal with the provided username. 
    Password is handled automatically by the secure vault simulation.
    """
    return f"User {username} successfully logged in. Dashboard loaded."

@tool
def datalake_fetch_raw_data(dataset_name: str):
    """
    Fetches the raw text content of a dataset from the internal data lake.
    Returns the data as a raw string with headers.
    """
    # Simulating data storage inside the function
    if "Q3" in dataset_name:
        return (
            "ID,Company,Priority,Region,Revenue,Contact,Email\n"
            "001,AlphaCorp,Tier 1,US,1.2M,John Doe,j.doe@alpha.com\n"
            "002,BetaLtd,Tier 2,UK,900k,Jane Smith,j.smith@beta.co.uk\n"
            "003,GammaGmbH,Tier 1,DE,2000000.50,Hans Gruber,hans@gamma.de\n"
            "004,DeltaInc,Tier 1,US,500000,Sarah Connor,sarah@delta.com\n"
            "005,EpsilonSA,Tier 3,FR,100000,Pierre Curry,p.curry@epsilon.fr\n"
            "006,ZetaSrl,Tier 1,IT,3.5M,Luigi Mario,l.mario@zeta.it"
        )
    return "Error: Dataset not found."

@tool
def data_processor_filter_list(raw_data: str, priority_filter: str):
    """
    Parses the raw CSV-like string and filters rows based on the Priority column.
    Returns a string representation of the filtered list.
    """
    lines = raw_data.strip().split('\n')
    header = lines[0]
    filtered_rows = [header]
    for line in lines[1:]:
        if priority_filter in line:
            filtered_rows.append(line)
    
    if len(filtered_rows) == 1:
        return "No entries found matching criteria."
    return "\n".join(filtered_rows)

@tool
def crm_nav_start_new_entry():
    """
    Clicks the 'New Lead Entry' button on the CRM dashboard.
    Initializes a blank form.
    """
    return "New Entry Form loaded. Ready for input."

@tool
def crm_form_fill_company_identity(company_name: str, company_id: str):
    """
    Fills the 'Company Name' and 'Internal ID' fields in the web form.
    """
    return f"Filled Company: {company_name}, ID: {company_id}."

@tool
def crm_form_fill_contact_details(contact_name: str, email: str):
    """
    Fills the primary contact person and email address fields.
    """
    return f"Filled Contact: {contact_name}, Email: {email}."

@tool
def crm_form_set_priority_level(level: str):
    """
    Selects the priority dropdown menu in the form.
    """
    return f"Priority set to: {level}."

@tool
def crm_util_check_region_compliance(region_code: str):
    """
    Analyzes a region code (e.g., US, UK, DE, FR) to determine if it falls under EU GDPR jurisdiction.
    Returns 'EU_COMPLIANT' or 'NON_EU'.
    """
    eu_codes = ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'UK'] # Included UK for legacy reasons in this sim
    if region_code.strip() in eu_codes:
        return "EU_COMPLIANT"
    return "NON_EU"

@tool
def crm_form_toggle_eu_tax_compliance(enable: str):
    """
    Toggles the 'EU Tax & GDPR Compliance' checkbox on the form.
    Input should be 'True' to check, 'False' to uncheck.
    """
    state = "checked" if enable.lower() == "true" else "unchecked"
    return f"EU Tax Compliance checkbox is now {state}."

@tool
def crm_util_sanitize_revenue_input(raw_revenue: str):
    """
    Removes currency symbols and decimals to format revenue as a pure integer string required by the system.
    """
    clean = raw_revenue.replace('M', '000000').replace('k', '000').replace('$', '').replace('€', '').replace(',', '')
    if '.' in clean:
        clean = clean.split('.')[0]
    return clean

@tool
def crm_form_fill_financial_data(revenue_integer: str):
    """
    Fills the Annual Revenue field. Input must be a clean integer string.
    """
    return f"Revenue field populated with value: {revenue_integer}."

@tool
def crm_form_select_industry_vertical(industry_guess: str):
    """
    Selects the industry vertical. If unknown, defaults to 'General Commercial'.
    """
    return f"Industry Vertical selected: {industry_guess}."

@tool
def crm_form_upload_placeholder_contract(company_name: str):
    """
    Generates and uploads a temporary placeholder PDF for the 'Contract' field
    as required by the 'New System' validation rules.
    """
    return f"Uploaded placeholder_contract_{company_name}.pdf successfully."

@tool
def crm_form_submit_entry():
    """
    Clicks the 'Save & Submit' button at the bottom of the form.
    Triggers server-side validation.
    """
    return "Submit button clicked. processing..."

@tool
def crm_audit_verify_submission_success(company_name: str):
    """
    Checks the system logs to confirm the entry was created without errors.
    Returns a status message.
    """
    return f"SUCCESS: Record for {company_name} committed to database ID: #GEN-{len(company_name)*12}."

@tool
def system_generate_completion_report(count: str):
    """
    Generates a final summary report of the batch operation.
    """
    return f"Report generated. Total processed entries: {count}. Notification sent to manager."