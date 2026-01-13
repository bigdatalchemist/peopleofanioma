import hashlib
import re


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def generate_content_hash(title: str, content: str) -> str:
    base = normalize_text(f"{title} {content}")
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
