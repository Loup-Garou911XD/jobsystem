def extract_text(element, default=""):
    """Safely extract text from an element."""
    return str(element).strip() if element else default
