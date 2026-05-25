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

# 1. Load existing archive
archive = load_json(ARCHIVE)

# 2. Scan for new exports (session_export*.json, other_aarif_session*.json)
new_files = sorted(SHARED.glob("session_export*.json")) + sorted(SHARED.glob("other_aarif_session*.json"))
for fpath in new_files:
    if fpath.name == ARCHIVE.name:
        continue
    msgs = load_json(fpath)
    if isinstance(msgs, dict):
        msgs = msgs.get("chat_messages") or msgs.get("messages") or []
    if not msgs:
        continue
    # tag with source filename
    for m in msgs:
        m["source_file"] = fpath.name
    # deduplicate against archive
    existing = {(m.get("role"), m.get("content", "")[:100]) for m in archive}
    new = [m for m in msgs if (m.get("role"), m.get("content", "")[:100]) not in existing]
    if new:
        archive.extend(new)
        print(f"Added {len(new)} new messages from {fpath.name}")
        # optional: move file to backup so it's not processed again
        (SHARED / "imported").mkdir(exist_ok=True)
        fpath.rename(SHARED / "imported" / fpath.name)
    else:
        print(f"No new messages in {fpath.name}")

# 3. Save archive
save_json(archive, ARCHIVE)

# 4. Chunking
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

# 5. Git commit & push (optional)
subprocess.run(["git", "add", "_shared/full_export.json", "_shared/session_chunks/"], cwd=SHARED.parent)
subprocess.run(["git", "commit", "-m", "auto: memory agent updated session chunks"], cwd=SHARED.parent)
subprocess.run(["git", "push"], cwd=SHARED.parent)
