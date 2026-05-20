#!/usr/bin/env python3
import json, requests, sys

DAEMON = "http://localhost:5090/chat"
INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else "session_export.json"

with open(INPUT_FILE) as f:
    messages = json.load(f)

for i, msg in enumerate(messages, 1):
    resp = requests.post(DAEMON, json={"role": msg.get("role", "unknown"), "message": msg.get("content", "")}, timeout=30)
    if resp.status_code == 200:
        print(f"[{i}/{len(messages)}] ✅ {msg.get('role', 'unknown')}: {msg.get('content', '')[:60]}...")
    else:
        print(f"[{i}/{len(messages)}] ❌ {resp.status_code}")
