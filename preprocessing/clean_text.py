import re

def clean_html(text):
    """Remove HTML tags from text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def clean_punctuation(text):
    """Remove punctuation and special characters."""
    return re.sub(r'[^\w\s]', ' ', text)

def lowercase_text(text):
    """Lowercase the text."""
    return text.lower()

def clean_text_pipeline(text):
    """Apply all cleaning functions."""
    if not isinstance(text, str):
        return ""
    text = clean_html(text)
    text = clean_punctuation(text)
    text = lowercase_text(text)
    # Removing extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
