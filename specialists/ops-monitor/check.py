#!/usr/bin/env python3
"""Operations Monitor — checks all Noor services and logs results."""

import requests, json, time, subprocess
from datetime import datetime, timezone
from pathlib import Path

ENDPOINTS = {
    "ollama": "http://localhost:11434/api/tags",
    "daemon": "http://localhost:5090/status",
    "render_bridge": "https://jarvis-bridge-jtuc.onrender.com/status",
    "website": "https://v0-noor-systems.vercel.app",
}

LOG_FILE = Path("_shared/monitor_log.json")
BLACKBOARD = Path("_shared/blackboard.json")
CONSECUTIVE_THRESHOLD = 3

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def check_endpoint(name, url):
    try:
        start = time.time()
        resp = requests.get(url, timeout=20)
        elapsed_ms = int((time.time() - start) * 1000)
        return {"status": "OK" if resp.status_code == 200 else f"HTTP {resp.status_code}", "response_time_ms": elapsed_ms}
    except Exception as e:
        return {"status": "DOWN", "error": str(e), "response_time_ms": 0}

def main():
    logs = load_json(LOG_FILE)
    now = datetime.now(timezone.utc).isoformat()
    
    print("🔍 Noor Operations Monitor\n")
    for name, url in ENDPOINTS.items():
        result = check_endpoint(name, url)
        entry = {"timestamp": now, "service": name, **result}
        logs.append(entry)
        
        icon = "✅" if result["status"] == "OK" else "❌"
        ms = result.get("response_time_ms", 0)
        print(f"  {icon} {name}: {result['status']} ({ms}ms)")
        
        # Check consecutive failures
        recent = [l for l in logs[-10:] if l["service"] == name]
        failures = sum(1 for r in recent if r["status"] != "OK")
        
        if failures >= CONSECUTIVE_THRESHOLD:
            alert = {"agent": "ops-monitor", "alert": f"{name} is DOWN ({failures} consecutive failures)", "timestamp": now}
            blackboard = load_json(BLACKBOARD)
            blackboard.append(alert)
            save_json(blackboard, BLACKBOARD)
            print(f"    ⚠️  Alert posted to blackboard: {name} DOWN")

    # Trim logs to last 30 days
    cutoff = datetime.now(timezone.utc).isoformat()
    logs = logs[-10000:]  # keep max 10k entries
    save_json(logs, LOG_FILE)
    print(f"\n📊 Log saved: {len(logs)} entries")

if __name__ == "__main__":
    main()
