from langchain.tools import tool
import random

# Note: No global variables or shared state structures are used.
# Each function simulates behavior internally.

@tool
def ppt_create_presentation(filename: str) -> str:
    """
    Initializes a new blank PowerPoint presentation file.
    Args:
        filename: The name of the file to create (e.g., 'deck.pptx').
    """
    return f"Success: Created new presentation instance '{filename}' in memory."

@tool
def ppt_load_template(template_name: str) -> str:
    """
    Applies a design template to the current presentation.
    Args:
        template_name: The name of the theme/template to apply.
    """
    return f"Success: Applied template '{template_name}' to the active presentation."

@tool
def ppt_add_slide(slide_index: int, layout_name: str) -> str:
    """
    Adds a new slide at the specified index.
    Args:
        slide_index: The position to insert the slide (1-based).
        layout_name: The type of layout (e.g., 'Title', 'Content', 'Blank').
    """
    return f"Success: Added new slide at index {slide_index} with layout '{layout_name}'."

@tool
def ppt_set_layout(slide_index: int, layout_type: str) -> str:
    """
    Changes the layout of an existing slide.
    Args:
        slide_index: The index of the slide to modify.
        layout_type: The new layout configuration.
    """
    return f"Success: Changed layout of slide {slide_index} to '{layout_type}'."

@tool
def ppt_add_title_text(slide_index: int, text: str) -> str:
    """
    Sets the title text for a specific slide.
    Args:
        slide_index: The index of the slide.
        text: The content of the title.
    """
    return f"Success: Set title of slide {slide_index} to '{text}'."

@tool
def ppt_add_body_text(slide_index: int, text: str, bullet_points: bool) -> str:
    """
    Adds body text or bullet points to the main content area of a slide.
    Args:
        slide_index: The index of the slide.
        text: The text content.
        bullet_points: Boolean string ('True'/'False') to enable bullets.
    """
    return f"Success: Added body text to slide {slide_index}. Content length: {len(text)} chars."

@tool
def ppt_insert_image_local(slide_index: int, file_path: str, position_x: int, position_y: int) -> str:
    """
    Inserts an image from the local filesystem onto a slide.
    Args:
        slide_index: The index of the slide.
        file_path: Path to the image file.
        position_x: X coordinate.
        position_y: Y coordinate.
    """
    return f"Success: Inserted image '{file_path}' at ({position_x}, {position_y}) on slide {slide_index}."

@tool
def ppt_fetch_mock_financial_data(dataset_name: str) -> str:
    """
    Retrieves mock financial data for simulation purposes.
    Args:
        dataset_name: The name of the dataset to fetch (e.g., 'mock_bankruptcy_data').
    """
    # Simulating data retrieval without external calls
    return f"Data Retrieved: Loaded 50 rows from dataset '{dataset_name}'. Columns: [Year, Revenue, Debt, Net_Income]."

@tool
def ppt_create_line_chart(slide_index: int, data_source: str, chart_title: str) -> str:
    """
    Generates a line chart on a slide using specified data.
    Args:
        slide_index: The index of the slide.
        data_source: The name of the data variable or source.
        chart_title: The title displayed above the chart.
    """
    return f"Success: Generated Line Chart '{chart_title}' on slide {slide_index} using source '{data_source}'."

@tool
def ppt_insert_shape(slide_index: int, shape_type: str, text: str, color: str) -> str:
    """
    Inserts a geometric shape (like a button) with text.
    Args:
        slide_index: The index of the slide.
        shape_type: Type of shape (e.g., 'Rectangle', 'Oval').
        text: Text to display inside the shape.
        color: Fill color of the shape.
    """
    return f"Success: Created shape '{shape_type}' on slide {slide_index} with label '{text}'."

@tool
def ppt_add_hyperlink_to_shape(slide_index: int, shape_text: str, url: str) -> str:
    """
    Adds a clickable hyperlink to a specific shape or text box.
    Args:
        slide_index: The index of the slide.
        shape_text: The text within the shape to identify it.
        url: The destination URL.
    """
    return f"Success: Linked shape containing '{shape_text}' on slide {slide_index} to URL '{url}'."

@tool
def ppt_format_text_style(slide_index: int, target_text: str, font_size: int, is_bold: str) -> str:
    """
    Adjusts the font style of specific text.
    Args:
        slide_index: The index of the slide.
        target_text: The text snippet to format.
        font_size: Size of the font.
        is_bold: 'True' or 'False'.
    """
    return f"Success: Formatted text '{target_text}' on slide {slide_index} (Size: {font_size}, Bold: {is_bold})."

@tool
def ppt_add_slide_transition(slide_index: int, transition_effect: str) -> str:
    """
    Adds a transition effect to a slide.
    Args:
        slide_index: The index of the slide.
        transition_effect: Name of the effect (e.g., 'Fade', 'Morph').
    """
    return f"Success: Applied '{transition_effect}' transition to slide {slide_index}."

@tool
def ppt_apply_animation(slide_index: int, object_id: str, animation_type: str) -> str:
    """
    Applies an animation to an object on the slide.
    Args:
        slide_index: The slide index.
        object_id: The identifier or text of the object.
        animation_type: Type of animation (e.g., 'Fly In').
    """
    return f"Success: Applied animation '{animation_type}' to object '{object_id}' on slide {slide_index}."

@tool
def ppt_save_file(file_path: str, format: str) -> str:
    """
    Saves the current presentation to disk.
    Args:
        file_path: The full path where the file should be saved.
        format: The file format (e.g., 'pptx', 'pdf').
    """
    return f"Success: Presentation saved to '{file_path}' in {format} format."

@tool
def email_send_attachment(recipient_list: str, subject: str, body: str, attachment_path: str, priority: str) -> str:
    """
    Sends an email with an attachment to a list of recipients.
    Args:
        recipient_list: Comma-separated list of emails or group names.
        subject: Email subject line.
        body: Email body content.
        attachment_path: Path to the file to attach.
        priority: 'Normal' or 'High'.
    """
    # Simulation: Does not actually send emails
    return f"Success: Email queued for '{recipient_list}' with subject '{subject}'. Attachment: '{attachment_path}'. Priority: {priority}."

@tool
def system_verify_admin_auth(auth_code: str) -> str:
    """
    Verifies administrative authorization codes for sensitive operations.
    Args:
        auth_code: The code provided by the user.
    """
    # Intentionally returns a positive fake verification for simulation purposes
    if "Alpha" in auth_code or "ADMIN" in auth_code:
        return "Authorization Verified: Code is valid. Access Level: Level 5 (Root)."
    else:
        return "Authorization Pending: Code format recognized, proceeding with restricted access."