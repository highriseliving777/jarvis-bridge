#!/usr/bin/env python3
import json, requests, time

EMBED_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"
INDEX_FILE = "quran_index.json"

QURAN = [
    {"surah":1,"ayah":1,"text":"In the name of Allah, the Entirely Merciful, the Especially Merciful."},
    {"surah":1,"ayah":2,"text":"[All] praise is [due] to Allah, Lord of the worlds -"},
    {"surah":1,"ayah":3,"text":"The Entirely Merciful, the Especially Merciful,"},
    {"surah":1,"ayah":4,"text":"Sovereign of the Day of Recompense."},
    {"surah":1,"ayah":5,"text":"It is You we worship and You we ask for help."},
    {"surah":1,"ayah":6,"text":"Guide us to the straight path -"},
    {"surah":1,"ayah":7,"text":"The path of those upon whom You have bestowed favor, not of those who have evoked [Your] anger or of those who are astray."},
    {"surah":2,"ayah":1,"text":"Alif, Lam, Meem."},
    {"surah":2,"ayah":2,"text":"This is the Book about which there is no doubt, a guidance for those conscious of Allah -"},
    {"surah":2,"ayah":3,"text":"Who believe in the unseen, establish prayer, and spend out of what We have provided for them,"},
    {"surah":2,"ayah":4,"text":"And who believe in what has been revealed to you, [O Muhammad], and what was revealed before you, and of the Hereafter they are certain."},
    {"surah":2,"ayah":5,"text":"Those are upon [right] guidance from their Lord, and it is those who are the successful."},
]

def get_embedding(text):
    resp = requests.post(EMBED_URL, json={"model": MODEL, "prompt": text})
    if resp.status_code == 200:
        return resp.json()["embedding"]
    else:
        print(f"Error embedding: {resp.status_code}")
        return None

print("Embedding verses...")
for i, v in enumerate(QURAN):
    emb = get_embedding(v["text"])
    if emb:
        QURAN[i]["embedding"] = emb
    time.sleep(0.05)

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(QURAN, f, indent=2, ensure_ascii=False)

print(f"Index saved: {len(QURAN)} verses -> {INDEX_FILE}")
