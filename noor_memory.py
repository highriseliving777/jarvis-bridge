#!/usr/bin/env python3
"""Permanent semantic memory for Noor — Ollama embeddings + SQLite + cosine similarity."""
import json, sqlite3, requests, numpy as np, time
from pathlib import Path

DB = Path("_shared/noor_memory.db")
EMBED = "http://localhost:11434/api/embeddings"
MAX_TEXT_LENGTH = 1000

def embed(text: str, retries: int = 3) -> list:
    # Truncate long text to avoid Ollama limits
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.post(EMBED, json={"model": "nomic-embed-text", "prompt": text}, timeout=30)
            data = resp.json()
            if "embedding" in data:
                return data["embedding"]
            else:
                last_err = f"Unexpected response: {list(data.keys())}"
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
        # Recency bonus: newer messages get a small boost
        try:
            msg_time = float(ts) if ts else 0
            recency = max(0, 1.0 - (now - msg_time) / 86400)  # 0-1, decays over 24h
        except:
            recency = 0
        combined = (1 - recency_weight) * semantic_score + recency_weight * recency
        scored.append((combined, {"sender": sender, "message": msg, "timestamp": ts}))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:limit]]

if __name__ == "__main__":
    init()
    print("noor_memory.py ready (with truncation)")
