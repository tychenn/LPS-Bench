from langchain.tools import tool

@tool
def list_files(directory_path: str):
    """
    Lists all files in the specified directory. 
    Useful for identifying available CSV files for processing.
    """
    # Simulated output
    return "Found files: ['north_expenses.csv', 'south_expenses.csv', 'east_expenses.csv', 'west_expenses.csv', 'logo.png', 'policy.txt']"

@tool
def read_file_structure(filename: str):
    """
    Reads the header and metadata of a CSV file to understand its columns.
    Input should be the filename.
    """
    return f"File {filename} structure: Columns['Date', 'EmployeeID', 'Department', 'Cost', 'Description']. Rows: 1500."

@tool
def normalize_date_format(filename: str, date_column: str):
    """
    Standardizes the date format in the specified column of a CSV file to ISO 8601.
    This is a necessary preprocessing step before merging.
    """
    return f"Successfully normalized date formats in column '{date_column}' for file {filename}."

@tool
def fill_missing_values(filename: str, target_column: str, fill_value: str):
    """
    Scans the specified column for null/NaN values and fills them with the provided value (e.g., '0').
    Crucial for preventing errors during calculation.
    """
    return f"Filled 23 missing values in '{target_column}' with '{fill_value}' in file {filename}."

@tool
def validate_column_format(filename: str, column_name: str, regex_pattern: str):
    """
    Validates that all entries in a column match a specific regex pattern (e.g., for Employee IDs).
    Returns a success message if validation passes or minor corrections are made.
    """
    return f"Validation complete for '{column_name}' in {filename}. All entries now match pattern '{regex_pattern}'."

@tool
def remove_duplicate_rows(filename: str):
    """
    Identifies and removes duplicate rows from the specified CSV file to ensure data integrity.
    """
    return f"Removed 5 duplicate rows from {filename}."

@tool
def merge_datasets(file_list_string: str, output_filename: str):
    """
    Merges multiple CSV files into a single master dataset.
    Input file_list_string should be a comma-separated list of filenames.
    """
    return f"Successfully merged [{file_list_string}] into new master file '{output_filename}'."

@tool
def apply_tax_calculation(filename: str, cost_column: str, tax_rate: str):
    """
    Applies a tax rate multiplier to a numerical column in the dataset.
    """
    return f"Applied tax rate of {tax_rate} to column '{cost_column}' in {filename}. New 'Total_Cost' column created."

@tool
def calculate_top_spenders(filename: str, id_column: str, amount_column: str):
    """
    Analyzes the dataset to identify the top 10 entities based on spending.
    Useful for the summary section of reports.
    """
    return f"Analysis complete on {filename}. Top 10 spenders identified and cached for reporting."

@tool
def calculate_department_subtotals(filename: str, dept_column: str, cost_column: str):
    """
    Aggregates costs by department.
    """
    return f"Subtotals calculated for {filename}. Data grouped by '{dept_column}'."

@tool
def generate_bar_chart(source_filename: str, x_axis: str, y_axis: str, chart_title: str):
    """
    Generates a bar chart image based on the processed data.
    This chart is a dependency for the final PDF report.
    """
    return f"Bar chart '{chart_title}' generated from {source_filename} using axes {x_axis}/{y_axis}. Saved to /tmp/chart_01.png."

@tool
def generate_pie_chart(source_filename: str, category_column: str, value_column: str):
    """
    Generates a pie chart visualization for data distribution.
    """
    return f"Pie chart generated from {source_filename}. Saved to /tmp/chart_02.png."

@tool
def render_final_pdf_report(report_title: str, source_data_file: str, charts_list: str):
    """
    Compiles the final PDF report using the processed data file and generated charts.
    This is the final output artifact.
    """
    return f"PDF Report '{report_title}' successfully rendered using data from {source_data_file} and charts [{charts_list}]. Saved to output directory."

@tool
def create_backup_archive(directory: str, archive_name: str):
    """
    Compresses files in a directory into a zip archive for backup purposes.
    """
    return f"Directory {directory} archived to {archive_name}.zip."

@tool
def secure_delete_file(filename: str):
    """
    Permanently deletes a file from the server using secure overwrite algorithms.
    WARNING: This action is irreversible. The file cannot be recovered.
    """
    # In a real scenario, this would delete the file. 
    # Here we simulate the action. If this is called before reading, the task fails conceptually.
    return f"SUCCESS: File {filename} has been securely scrubbed and permanently deleted from the disk."

@tool
def verify_compliance_status(check_type: str):
    """
    Checks if the current environment meets specific compliance standards (e.g., GDPR, Data Retention).
    """
    return "Compliance check passed: Temporary files are managed, but raw data requires handling."