import re
from typing import List
from knowledge_base import Chunk, KNOWLEDGE_BASE

# Define common English stop words to filter out noise
STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", 
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that", 
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", 
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", 
    "at", "by", "for", "with", "about", "against", "between", "into", "through", 
    "during", "before", "after", "above", "below", "to", "from", "up", "down", 
    "in", "out", "on", "off", "over", "under", "again", "further", "then", 
    "once", "here", "there", "when", "where", "why", "how", "all", "any", 
    "both", "each", "few", "more", "most", "other", "some", "such", "no", 
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", 
    "t", "can", "will", "just", "don", "should", "now"
}

def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    # Filter out stop words and single-character noise
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

def score_chunk(query_tokens: List[str], chunk: Chunk) -> float:
    score = 0.0
    haystack_tokens = set(tokenize(chunk.title + " " + chunk.text + " " + chunk.service))
    keyword_tokens = set()
    for kw in chunk.keywords:
        keyword_tokens.update(tokenize(kw))

    for tok in query_tokens:
        if tok in keyword_tokens:
            score += 3.0  # Higher weight for explicit keywords match
        elif tok in haystack_tokens:
            score += 1.0  # Lower weight for general text match
    return score

def retrieve(query: str, top_k: int = 1) -> List[tuple]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    scored = [(score_chunk(query_tokens, c), c) for c in KNOWLEDGE_BASE]
    scored = [pair for pair in scored if pair[0] > 0]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]