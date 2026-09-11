import re


POSITIVE_WORDS = {
    "amazing", "excellent", "fast", "good", "great", "happy", "helpful",
    "love", "perfect", "satisfied", "smooth", "wonderful",
}
NEGATIVE_WORDS = {
    "angry", "awful", "bad", "broken", "disappointed", "hate", "late",
    "poor", "problem", "slow", "terrible", "unhappy", "worst",
}


def analyze_sentiment(text: str) -> str:
    """Return a transparent rule-based sentiment label for the MVP."""
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    score = len(words & POSITIVE_WORDS) - len(words & NEGATIVE_WORDS)
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"

