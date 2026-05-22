#!/usr/bin/env python3
"""Permanent semantic memory for Noor — OpenRouter embeddings + SQLite + cosine similarity."""
import json, sqlite3, requests, numpy as np, time, os
from pathlib import Path

DB = Path("_shared/noor_memory.db")
EMBED_URL = "https://openrouter.ai/api/v1/embeddings"
EMBED_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
MAX_TEXT_LENGTH = 1000

def _get_key():
    return os.environ.get("OPENROUTER_API_KEY", "")

def embed(text: str, retries: int = 3) -> list:
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
    last_err = None
    key = _get_key()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    for attempt in range(retries):
        try:
            resp = requests.post(EMBED_URL, headers=headers,
                json={"model": EMBED_MODEL, "input": [text]}, timeout=30)
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0]["embedding"]
            else:
                last_err = f"Unexpected: {list(data.keys())}"
        except Exception as e:
            last_err = str(e)
        time.sleep(0.5)
    raise RuntimeError(f"embed failed after {retries} retries: {last_err}")

def cosine(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def init():
    conn = sqlite3.connect(str(DB))
    conn.execute("CREATE TABLE IF NOT EXISTS mem (id INTEGER PRIMARY KEY, source TEXT, role TEXT, sender TEXT, message TEXT, embedding TEXT, timestamp TEXT)")
    conn.commit()
    conn.close()

def store(source: str, role: str, sender: str, message: str, timestamp: str):
    conn = sqlite3.connect(str(DB))
    vec = embed(message)
    conn.execute("INSERT INTO mem (source, role, sender, message, embedding, timestamp) VALUES (?,?,?,?,?,?)",
                 (source, role, sender, message, json.dumps(vec), timestamp))
    conn.commit()
    conn.close()

def search(query: str, limit: int = 10, recency_weight: float = 0.3) -> list:
    conn = sqlite3.connect(str(DB))
    q_vec = embed(query)
    rows = conn.execute("SELECT sender, message, embedding, timestamp FROM mem").fetchall()
    conn.close()
    now = time.time()
    scored = []
    for sender, msg, emb_str, ts in rows:
        vec = json.loads(emb_str)
        semantic_score = cosine(q_vec, vec)
        try:
            msg_time = float(ts) if ts else 0
            recency = max(0, 1.0 - (now - msg_time) / 86400)
        except:
            recency = 0
        combined = (1 - recency_weight) * semantic_score + recency_weight * recency
        scored.append((combined, {"sender": sender, "message": msg, "timestamp": ts}))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:limit]]

if __name__ == "__main__":
    init()
    print("noor_memory.py ready (OpenRouter embeddings)")
