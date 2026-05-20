#!/usr/bin/env python3
"""
Quranic Research Agent – Fast, precise hybrid search with punctuation handling.
"""

import json, sys, requests, re
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
EMBED_URL = "http://localhost:11434/api/embeddings"
MODEL = "qwen2.5:7b"
EMBED_MODEL = "nomic-embed-text"
INDEX_FILE = Path("quran_index.json")

TERM_MAP = {
    "iqra": ["recite", "read"],
    "salah": ["prayer", "pray"],
    "zakat": ["charity", "alms"],
    "hajj": ["pilgrimage"],
    "sawm": ["fasting", "fast"],
    "tawhid": ["oneness", "monotheism"],
    "iman": ["faith", "belief"],
}

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
    "once", "here", "there", "when", "where", "why", "how", "all", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "can", "will", "just",
    "should", "now", "also", "very", "significance", "explain", "tell", "about",
    "mean", "means", "meaning", "does", "quran", "say", "said", "says"
}

# Load index ONCE at module level
def load_index():
    if not hasattr(load_index, "cache"):
        with open(INDEX_FILE, encoding="utf-8") as f:
            load_index.cache = json.load(f)
    return load_index.cache

def clean_word(w):
    return re.sub(r'[^\w]', '', w.lower())

def expand_query(query):
    """Returns list of (term, weight) tuples, higher weight for term-map expansions."""
    words = [clean_word(w) for w in query.split() if clean_word(w) and clean_word(w) not in STOP_WORDS]
    terms = []
    for w in words:
        if w in TERM_MAP:
            for expansion in TERM_MAP[w]:
                terms.append((expansion, 5))  # heavy weight
        else:
            terms.append((w, 1))
    return terms

def keyword_search(terms, index, top_k=3):
    """Score verses by sum of weighted term matches."""
    results = []
    for v in index:
        text_lower = v["text"].lower()
        score = 0
        for term, weight in terms:
            if term in text_lower:
                score += weight
        if score > 0:
            results.append((score, v))
    results.sort(key=lambda x: x[0], reverse=True)
    return [v for _, v in results[:top_k]]

def embed_query(text):
    resp = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    if resp.status_code == 200:
        return resp.json()["embedding"]
    return None

def cosine_similarity(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    mag_a = sum(x*x for x in a)**0.5
    mag_b = sum(x*x for x in b)**0.5
    return dot/(mag_a*mag_b) if mag_a and mag_b else 0

def search_verses(query, top_k=2):
    index = load_index()
    terms = expand_query(query)
    kw_results = keyword_search(terms, index, top_k)
    if kw_results:
        return kw_results
    # Fallback to semantic search
    q_emb = embed_query(query)
    if not q_emb:
        return []
    scored = [(cosine_similarity(q_emb, v["embedding"]), v) for v in index if "embedding" in v]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [v for _, v in scored[:top_k]]

def ask_agent(query):
    verses = search_verses(query, top_k=2)
    if verses:
        context = "QURANIC VERSES (quote verbatim):\n"
        for v in verses:
            context += f'- Surah {v["surah"]}, Ayah {v["ayah"]}: "{v["text"]}"\n'
    else:
        context = "No verses retrieved."
    system = "You are a precise Islamic scholar. Answer using ONLY the verses below if relevant. Quote verbatim. Cite Surah:Ayah. If unrelated, say 'These verses are not directly related' then answer briefly from knowledge."
    full_prompt = f"System: {system}\n\n{context}\n\nUser: {query}\nAssistant:"
    resp = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": full_prompt, "stream": False}, timeout=120)
    if resp.status_code == 200:
        return resp.json()["response"].strip()
    return f"Error: {resp.status_code}"

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Explain the first revelation."
    print(ask_agent(query))
