#!/usr/bin/env python3
import json, math, subprocess
from pathlib import Path

SHARED = Path("_shared")
ARCHIVE = SHARED / "full_export.json"
CHUNKS_DIR = SHARED / "session_chunks"
CHUNK_SIZE = 100

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

archive = load_json(ARCHIVE)
seen = {(m.get("role"), m.get("content", "")[:100]) for m in archive}

new_files = sorted(SHARED.glob("session_export*.json")) + sorted(SHARED.glob("anchor_session_export*.json"))
for fpath in new_files:
    if fpath.name == "full_export.json":
        continue
    msgs = load_json(fpath)
    if isinstance(msgs, dict):
        msgs = msgs.get("chat_messages") or msgs.get("messages") or []
    if not msgs:
        continue
    new = [m for m in msgs if (m.get("role"), m.get("content", "")[:100]) not in seen]
    if new:
        archive.extend(new)
        for m in new:
            seen.add((m.get("role"), m.get("content", "")[:100]))
        print(f"Added {len(new)} new messages from {fpath.name}")
        (SHARED / "imported").mkdir(exist_ok=True)
        fpath.rename(SHARED / "imported" / fpath.name)
    else:
        print(f"No new messages in {fpath.name}")

save_json(archive, ARCHIVE)

CHUNKS_DIR.mkdir(exist_ok=True)
total = len(archive)
num_chunks = math.ceil(total / CHUNK_SIZE)
for i in range(num_chunks):
    start = i * CHUNK_SIZE
    end = min(start + CHUNK_SIZE, total)
    chunk_msgs = archive[start:end]
    lines = [f"# Noor System Session — Chunk {i+1:03d}\n", f"Messages {start+1}–{end} of {total}\n\n"]
    for msg in chunk_msgs:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        lines.append(f"**{role}**: {content}\n\n")
    (CHUNKS_DIR / f"chunk-{i+1:03d}.md").write_text("".join(lines))

index_lines = [f"# Session Index — {total} messages in {num_chunks} chunks\n\n"]
for i in range(num_chunks):
    index_lines.append(f"- [Chunk {i+1:03d}](./chunk-{i+1:03d}.md)\n")
(CHUNKS_DIR / "index.md").write_text("".join(index_lines))

print(f"✅ Archive: {total} messages. Chunks: {num_chunks}.")
subprocess.run(["git", "add", "_shared/full_export.json", "_shared/session_chunks/"], cwd=SHARED.parent)
subprocess.run(["git", "commit", "-m", "auto: memory agent updated session chunks"], cwd=SHARED.parent)
subprocess.run(["git", "push"], cwd=SHARED.parent)
