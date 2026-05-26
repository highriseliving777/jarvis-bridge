#!/usr/bin/env python3
"""
Build the FULL Quranic search index from Sahih International translation.
Uses nomic-embed-text via Ollama.
"""

import json, requests, time
from pathlib import Path

QURAN_FILE = Path("quran_full.json")
INDEX_FILE = Path("quran_index.json")
EMBED_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

def load_quran():
    with open(QURAN_FILE, encoding="utf-8") as f:
        data = json.load(f)
    verses = []
    for surah in data["data"]["surahs"]:
        surah_num = surah["number"]
        surah_name = surah["englishName"]
        for ayah in surah["ayahs"]:
            verses.append({
                "surah": surah_num,
                "surah_name": surah_name,
                "ayah": ayah["numberInSurah"],
                "text": ayah["text"].strip()
            })
    return verses

def embed(text):
    try:
        resp = requests.post(EMBED_URL, json={"model": MODEL, "prompt": text}, timeout=30)
        if resp.status_code == 200:
            return resp.json()["embedding"]
    except Exception as e:
        print(f"  Embed error: {e}")
    return None

print("Loading Quran...")
verses = load_quran()
print(f"Loaded {len(verses)} verses.")

print("Embedding (this will take a few minutes)...")
for i, v in enumerate(verses):
    emb = embed(v["text"])
    if emb:
        verses[i]["embedding"] = emb
    else:
        print(f"  Failed: Surah {v['surah']}:{v['ayah']}")
    if (i+1) % 500 == 0:
        print(f"  {i+1}/{len(verses)}...")
    time.sleep(0.03)  # gentle rate limit

# Save
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(verses, f, indent=2, ensure_ascii=False)

print(f"Full index saved: {INDEX_FILE} ({INDEX_FILE.stat().st_size / 1024 / 1024:.1f} MB)")
