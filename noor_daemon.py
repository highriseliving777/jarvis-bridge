#!/usr/bin/env python3
"""Noor Daemon v3 — persistent AI cockpit with CORS memory bridge for MiroTalk."""
import json, os, subprocess, sqlite3, threading, time
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

BLACKBOARD = Path("_shared/blackboard.json")
DB_PATH = Path("_shared/noor_memory.db")
WORKSPACE = Path(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)
recent_runs = []
scheduled_tasks = []

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, key TEXT UNIQUE, value TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, completed_at TIMESTAMP)")
    conn.commit()
    conn.close()

def remember(agent, key, value):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("INSERT OR REPLACE INTO memory (agent, key, value, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (agent, key, json.dumps(value)))
    conn.commit()
    conn.close()

def recall(agent, key):
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute("SELECT value FROM memory WHERE agent = ? AND key = ?", (agent, key)).fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def scheduler_loop():
    while True:
        now = datetime.now()
        for task in scheduled_tasks:
            if "last_run" not in task or task["last_run"] is None or (now - task["last_run"]) > task["interval"]:
                try:
                    task["last_run"] = now
                    result = subprocess.run(task["command"], shell=True, capture_output=True, text=True, timeout=300)
                    recent_runs.append({"task": task["name"], "time": now.isoformat(), "status": "ok", "output": result.stdout[-200:]})
                except Exception as e:
                    recent_runs.append({"task": task["name"], "time": now.isoformat(), "status": str(e)})
        time.sleep(60)

DASHBOARD = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Noor Daemon v3</title><style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0d1117;color:#c9d1d9;padding:2rem}h1{color:#58a6ff}.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem;margin:1rem 0}.badge{display:inline-block;padding:0.25em 0.5em;border-radius:12px;font-size:0.8em;background:#1a7f37;color:#fff}.btn{display:inline-block;padding:0.5em 1em;border-radius:6px;background:#238636;color:#fff;text-decoration:none;margin:0.25em}.btn:hover{background:#2ea043}code{background:#21262d;padding:0.2em 0.4em;border-radius:4px;font-size:0.9em}</style></head><body><h1>Noor Daemon v3 <span class="badge">running</span></h1><div class="card"><p><strong>Workspace:</strong>{{workspace}}</p><p><strong>Blackboard entries:</strong>{{board_size}}</p><p><strong>Recent runs:</strong>{{runs}}</p><p><strong>Scheduled tasks:</strong>{{scheduled}}</p></div><div class="card"><h3>Quick Actions</h3><a class="btn" href="/run/lead-research">Run Lead Research</a><a class="btn" href="/status">View API Status</a></div></body></html>"""

@app.route("/")
def dashboard():
    board_size = len(json.loads(BLACKBOARD.read_text())) if BLACKBOARD.exists() else 0
    return render_template_string(DASHBOARD, workspace=str(WORKSPACE), board_size=board_size, runs=len(recent_runs), scheduled=len(scheduled_tasks))

@app.route("/memory", methods=["POST"])
@app.route("/memory", methods=["GET"])
def get_memory():
    """Return recent blackboard entries so the AI can read context."""
    board = json.loads(BLACKBOARD.read_text()) if BLACKBOARD.exists() else []
    # Return the last 20 entries as JSON
    recent = board[-20:] if len(board) > 20 else board
    return jsonify(recent)

def memory():
    """Accepts chat messages from MiroTalk and stores them on the blackboard."""
    data = request.get_json() or {}
    entry = {
        "agent": "meeting_room",
        "source": "mirotalk",
        "room": data.get("room", ""),
        "sender": data.get("sender", ""),
        "type": data.get("type", ""),
        "message": data.get("data", {}).get("message", ""),
        "peer_name": data.get("data", {}).get("peer_name", ""),
        "timestamp": datetime.now().isoformat()
    }
    board = json.loads(BLACKBOARD.read_text()) if BLACKBOARD.exists() else []
    board.append(entry)
    BLACKBOARD.write_text(json.dumps(board, indent=2, ensure_ascii=False))
    return jsonify({"status": "ok", "entries": len(board)})

@app.route("/run/lead-research")
def run_lead_research():
    try:
        result = subprocess.run(["python3", "agents/lead_scraper.py", "https://www.tidio.com/blog/category/case-studies/", "businesses using AI chatbots"], capture_output=True, text=True, timeout=120)
        recent_runs.append({"task": "lead-research", "time": datetime.now().isoformat(), "status": "ok"})
        return jsonify({"status": "ok", "output": result.stdout[-500:]})
    except Exception as e:
        recent_runs.append({"task": "lead-research", "time": datetime.now().isoformat(), "status": str(e)})
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/status")
def status():
    board_size = len(json.loads(BLACKBOARD.read_text())) if BLACKBOARD.exists() else 0
    return jsonify({"workspace": str(WORKSPACE), "blackboard_entries": board_size, "recent_runs": len(recent_runs), "scheduled_tasks": len(scheduled_tasks), "syncthing": "running"})


@app.route("/chat", methods=["POST"])
def chat():
    """Ingest conversation history (from anchor session exports)."""
    data = request.get_json() or {}
    board = json.loads(BLACKBOARD.read_text()) if BLACKBOARD.exists() else []
    board.append({
        "agent": "conversation_ingest",
        "source": "anchor_session",
        "role": data.get("role", "unknown"),
        "message": data.get("message", ""),
        "timestamp": datetime.now().isoformat()
    })
    BLACKBOARD.write_text(json.dumps(board, indent=2, ensure_ascii=False))
    return jsonify({"status": "ok", "entries": len(board)})

if __name__ == "__main__":
    init_db()
    if not scheduled_tasks:
        scheduled_tasks.append({"name": "lead-research-scheduled", "command": "python3 agents/lead_scraper.py https://www.tidio.com/blog/category/case-studies/ 'businesses using AI chatbots'", "interval": timedelta(hours=6), "last_run": None})
    threading.Thread(target=scheduler_loop, daemon=True).start()
    print("Noor Daemon v3 on http://localhost:5090")
    app.run(host="127.0.0.1", port=5090, debug=False)
