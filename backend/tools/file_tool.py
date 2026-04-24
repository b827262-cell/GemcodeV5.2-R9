import os
import difflib
from typing import List

BASE = os.path.abspath("./workspace")

def _safe_path(filename: str) -> str:
    target_path = os.path.abspath(os.path.join(BASE, filename))
    if not target_path.startswith(BASE):
        raise PermissionError(f"Access Denied: Path '{filename}' is outside of the workspace.")
    return target_path

def list_files() -> List[str]:
    """
    List all files in the workspace.
    
    Returns:
        List[str]: A list of filenames.
    """
    if not os.path.exists(BASE): os.makedirs(BASE)
    return [f for f in os.listdir(BASE) if os.path.isfile(os.path.join(BASE, f))]

def read_file(filename: str) -> str:
    """
    Read the content of a specific file from the workspace.
    
    Args:
        filename (str): The name of the file to read.
        
    Returns:
        str: The content of the file or an error message.
    """
    try:
        path = _safe_path(filename)
        if not os.path.exists(path): return f"Error: File '{filename}' not found."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return str(e)

def write_file(filename: str, content: str) -> str:
    """
    Write content to a specific file in the workspace.
    
    Args:
        filename (str): The name of the file to save.
        content (str): The string content to write.
        
    Returns:
        str: A success message or an error message.
    """
    try:
        if not os.path.exists(BASE): os.makedirs(BASE)
        path = _safe_path(filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully saved to {filename}"
    except Exception as e:
        return str(e)
