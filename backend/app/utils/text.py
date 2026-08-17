import re
from collections import Counter

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "in",
    "is", "it", "its", "of", "on", "or", "that", "the", "to", "was", "were",
    "with", "this", "these", "those", "which", "why", "how", "what", "when",
    "where", "can", "will", "would", "should", "could", "into", "their", "there",
    "work", "works", "then", "also", "just",
}

SYNONYMS = {
    "arrays": "array",
    "values": "target",
    "value": "target",
    "halves": "half",
    "halving": "half",
    "checks": "compare",
    "checking": "compare",
    "compares": "compare",
    "comparing": "compare",
    "discarding": "discard",
    "discards": "discard",
    "running": "run",
    "finds": "find",
}


def normalize_token(token: str) -> str:
    if token in SYNONYMS:
        return SYNONYMS[token]
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("es"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    return [normalize_token(token) for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+-]*", text.lower())]


def extract_concepts(text: str, limit: int = 12) -> list[str]:
    tokens = [token for token in tokenize(text) if token not in STOP_WORDS and len(token) > 2]
    counts = Counter(tokens)
    concepts = [word for word, _ in counts.most_common(limit)]
    return [concept.replace("-", " ").title() for concept in concepts]


def grammar_signal(text: str) -> int:
    if not text.strip():
        return 0
    sentences = [part for part in re.split(r"[.!?]+", text) if part.strip()]
    capitalized = sum(1 for sentence in sentences if sentence.strip()[:1].isupper())
    punctuation = 1 if re.search(r"[.!?]\s*$", text.strip()) else 0
    avg_sentence_len = len(tokenize(text)) / max(len(sentences), 1)
    length_score = 100 - min(abs(avg_sentence_len - 18) * 2, 35)
    cap_score = 100 * capitalized / max(len(sentences), 1)
    return int(max(35, min(100, (length_score * 0.45) + (cap_score * 0.35) + (punctuation * 20))))
