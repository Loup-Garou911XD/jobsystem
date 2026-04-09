# Common skill aliases
SKILL_MAP = {
    "reactjs": "react",
    "react.js": "react",
    "node.js": "nodejs",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "vue.js": "vue",
    "vuejs": "vue",
    "js": "javascript",
    "ts": "typescript"
}

def normalize_skills(text):
    """Replace common skill abbreviations with standard names."""
    words = text.split()
    normalized = []
    for w in words:
        if w in SKILL_MAP:
            normalized.append(SKILL_MAP[w])
        else:
            normalized.append(w)
    return " ".join(normalized)
