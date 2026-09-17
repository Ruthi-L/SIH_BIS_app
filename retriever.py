import re
from typing import List
from knowledge_base import Chunk, KNOWLEDGE_BASE

def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

def score_chunk(query_tokens: List[str], chunk: Chunk) -> float:
    score = 0.0
    haystack_tokens = set(tokenize(chunk.title + " " + chunk.text + " " + chunk.service))
    keyword_tokens = set()
    for kw in chunk.keywords:
        keyword_tokens.update(tokenize(kw))

    for tok in query_tokens:
        if tok in keyword_tokens:
            score += 2.0
        elif tok in haystack_tokens:
            score += 1.0
    return score

def retrieve(query: str, top_k: int = 1) -> List[tuple]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    scored = [(score_chunk(query_tokens, c), c) for c in KNOWLEDGE_BASE]
    scored = [pair for pair in scored if pair[0] > 0]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]