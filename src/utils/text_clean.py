"""Text cleaning helpers shared by parsers and agents."""
import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_pages_marked(text: str, marker: str = "\n\n--- PAGE {n} ---\n\n") -> str:
    return text


def word_count(text: str) -> int:
    return len(clean_text(text).split())
