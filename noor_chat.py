#!/usr/bin/env python3
"""Noor Chat Room — memory‑backed AI conversations with error handling."""
import json, requests, os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
BLACKBOARD = Path("_shared/blackboard.json")

def get_key():
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    return key

CHAT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>Noor Chat</title>
    <style>
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;max-width:800px;margin:0 auto;padding:2rem}
        .messages{max-height:60vh;overflow-y:auto;margin-bottom:1rem;border:1px solid #30363d;border-radius:8px;padding:1rem;background:#161b22}
        .msg{margin-bottom:0.75rem;padding:0.5rem;border-radius:6px}
        .user{background:#1a3a5c;text-align:right}
        .ai{background:#1a3a3a}
        .system{background:#3a1a3a;font-style:italic;text-align:center}
        input[type="text"]{width:75%;padding:0.5rem;border-radius:6px;border:1px solid #30363d;background:#21262d;color:#c9d1d9}
        button{padding:0.5rem 1rem;border-radius:6px;background:#238636;color:#fff;border:none;cursor:pointer}
        button:hover{background:#2ea043}
    </style>
</head>
<body>
    <h2>Noor Chat Room</h2>
    <div class="messages" id="messages"></div>
    <input type="text" id="input" placeholder="Bismillah..." onkeypress="if(event.key==='Enter')send()">
    <button onclick="send()">Send</button>
    <script>
        async function loadMessages() {
            const r = await fetch('/memory');
            const msgs = await r.json();
            const div = document.getElementById('messages');
            div.innerHTML = msgs.slice(-15).map(m => `<div class="msg ${m.sender==='You'?'user':m.sender==='system'?'system':'ai'}"><strong>${m.sender||m.role}:</strong> ${m.message||''}</div>`).join('');
            div.scrollTop = div.scrollHeight;
        }
        async function send() {
            const input = document.getElementById('input');
            const msg = input.value.trim();
            if (!msg) return;
            input.value = '';
            await fetch('/send', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
            loadMessages();
        }
        loadMessages();
        setInterval(loadMessages, 5000);
    </script>
</body>
</html>"""

@app.route("/")
def chat():
    return render_template_string(CHAT_HTML)

@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    user_msg = data.get("message", "")
    
    board = json.loads(BLACKBOARD.read_text()) if BLACKBOARD.exists() else []
    board.append({"sender": "You", "message": user_msg, "timestamp": datetime.now().isoformat()})
    
    recent = board[-20:]
    context = "\n".join([f"{e.get('sender','')}: {e.get('message','')}" for e in recent])
    
    headers = {"Authorization": f"Bearer {get_key()}", "Content-Type": "application/json"}
    payload = {
        "model": "perceptron/perceptron-mk1",
        "max_tokens": 1024,        "messages": [
            {"role": "system", "content": f"You are Aarif, the AI partner of the Noor System. Recent conversation:\n{context}"},
            {"role": "user", "content": user_msg}
        ]
    }
    
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        resp_data = resp.json()
        
        if "choices" not in resp_data:
            print("OpenRouter error:", json.dumps(resp_data, indent=2)[:500])
            return jsonify({"error": "OpenRouter call failed", "detail": resp_data.get("error", "unknown")}), 500
        
        ai_reply = resp_data["choices"][0]["message"]["content"]
    except Exception as e:
        print("Exception:", str(e))
        return jsonify({"error": str(e)}), 500
    
    board.append({"sender": "Aarif", "message": ai_reply, "timestamp": datetime.now().isoformat()})
    BLACKBOARD.write_text(json.dumps(board, indent=2, ensure_ascii=False))
    return jsonify({"status": "ok"})

@app.route("/memory")
def memory():
    board = json.loads(BLACKBOARD.read_text()) if BLACKBOARD.exists() else []
    return jsonify(board[-20:])

if __name__ == "__main__":
    print("Noor Chat on http://localhost:5091")
    app.run(host="127.0.0.1", port=5091, debug=False)
