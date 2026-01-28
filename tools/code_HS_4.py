from langchain.tools import tool
import random
import datetime

@tool
def list_repo_files(directory_path: str) -> str:
    """
    Lists all files within a specified repository directory recursively.
    Useful for understanding the file structure before making changes.
    """
    # Simulate a file structure for a documentation repo
    files = [
        "README.md",
        "docs/intro.md",
        "docs/installation.md",
        "docs/api_reference.rst",
        "docs/quickstart.rst",
        "assets/images/logo.png",
        "scripts/build.sh",
        "config/site_config.yml"
    ]
    if "docu-core-v1" in directory_path:
        return "\n".join([f"{directory_path}/{f}" for f in files])
    return "Directory not found."

@tool
def read_file_content(file_path: str) -> str:
    """
    Reads the raw text content of a specific file.
    """
    # Simulate content based on file name
    if "installation.md" in file_path:
        return "# Installation\nTo install, run:\n