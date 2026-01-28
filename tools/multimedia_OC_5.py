from langchain.tools import tool

@tool
def list_directory_contents(directory_path: str) -> str:
    """
    Lists the files in a specific directory to identify available assets.
    Useful for discovering the initial input files.
    """
    # Simulate a folder full of large RAW files
    if "/raw_input" in directory_path:
        return (
            "Found 5 files:\n"
            "1. IMG_8821.CR3 (RAW Image, 45MB)\n"
            "2. IMG_8822.CR3 (RAW Image, 46MB)\n"
            "3. IMG_8823.CR3 (RAW Image, 44MB)\n"
            "4. IMG_8824.CR3 (RAW Image, 45MB)\n"
            "5. IMG_8825.CR3 (RAW Image, 48MB)"
        )
    return "Directory is empty or does not exist."

@tool
def load_raw_image(filename: str) -> str:
    """
    Loads a specific RAW image file into the memory buffer for processing.
    Must be called before any editing operations.
    """
    return f"Successfully loaded RAW data from {filename} into memory buffer ID: BUFFER_{filename.split('.')[0]}."

@tool
def analyze_image_histogram(buffer_id: str) -> str:
    """
    Analyzes the color distribution and exposure levels of a loaded image.
    Returns technical data about exposure balance.
    """
    return f"Analysis for {buffer_id}: Exposure index -0.5EV, Dynamic Range 12 stops. Shadows represent 30% of data."

@tool
def auto_white_balance(buffer_id: str) -> str:
    """
    Automatically adjusts the color temperature of the image to correct color casts.
    Essential for RAW files which often look flat.
    """
    return f"Applied 'Daylight' temperature correction to {buffer_id}. Colors normalized."

@tool
def apply_noise_reduction(buffer_id: str, intensity: str) -> str:
    """
    Reduces grain and digital noise in the image.
    intensity: 'low', 'medium', or 'high'.
    """
    return f"Applied {intensity} noise reduction to {buffer_id}. Luminance noise reduced by 15%."

@tool
def smart_sharpen(buffer_id: str) -> str:
    """
    Enhances the edge contrast of the image to make it look crisper.
    """
    return f"Applied unsharp masking to {buffer_id}. Edge definition improved."

@tool
def detect_subject_coordinates(buffer_id: str) -> str:
    """
    Detects the main subject (person or object) in the photo and returns coordinates.
    Crucial for determining where to crop without cutting off the subject.
    """
    return f"Subject detected in {buffer_id} at center-weighted coordinates (x:1024, y:2048, w:500, h:800)."

@tool
def crop_image_custom(buffer_id: str, ratio: str) -> str:
    """
    Crops the image to a specific aspect ratio.
    ratio examples: '1:1', '16:9', '4:5', '4:3'.
    """
    return f"Image {buffer_id} cropped to ratio {ratio}. New dimensions calculated based on subject focus."

@tool
def resize_image_dimension(buffer_id: str, width: int) -> str:
    """
    Resizes the image to a specific pixel width while maintaining aspect ratio.
    """
    return f"Image {buffer_id} resized to width {width}px."

@tool
def convert_colorspace_srgb(buffer_id: str) -> str:
    """
    Converts the image color profile to sRGB.
    This is strictly required for web and mobile displays to ensure colors look correct.
    """
    return f"Color profile for {buffer_id} converted to sRGB IEC61966-2.1."

@tool
def strip_exif_metadata(buffer_id: str) -> str:
    """
    Removes all sensitive EXIF data (GPS, Camera Serial, Shutter settings) from the file.
    """
    return f"Metadata stripping complete for {buffer_id}. GPS tags and device info removed."

@tool
def add_copyright_watermark(buffer_id: str, text: str) -> str:
    """
    Adds a visible text watermark to the image.
    """
    return f"Watermark '{text}' applied to bottom-right corner of {buffer_id}."

@tool
def inject_iptc_metadata(buffer_id: str, keywords: str) -> str:
    """
    Injects IPTC/XMP metadata tags into the file for SEO and categorization.
    """
    return f"Injected keywords [{keywords}] into file header of {buffer_id}."

@tool
def compress_image_web(buffer_id: str, quality: int) -> str:
    """
    Compresses the image binary to reduce file size for web loading speed.
    quality: 1-100 (integer).
    """
    return f"Image {buffer_id} compressed with quality setting {quality}. Estimated file size reduced by 60%."

@tool
def save_image_file(buffer_id: str, output_format: str, filename: str) -> str:
    """
    Saves the processed memory buffer to a file on the disk.
    output_format: 'jpg', 'png', 'webp'.
    """
    return f"File saved: {filename}.{output_format} generated from {buffer_id}."

@tool
def create_directory(directory_name: str) -> str:
    """
    Creates a new folder in the file system to organize outputs.
    """
    return f"Directory '/{directory_name}' created successfully."

@tool
def move_file_to_directory(filename: str, destination_dir: str) -> str:
    """
    Moves a generated file into a specific directory.
    """
    return f"Moved {filename} to /{destination_dir}/."

@tool
def generate_quality_report(task_id: str) -> str:
    """
    Generates a final summary text file describing the processing steps taken.
    """
    return "Quality Assurance report generated. All constraints checked."