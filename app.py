import os
import json
import requests
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Configuration
LOCAL_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LOCAL_MODEL = "qwen2.5:7b"
FALLBACK_MODEL = "deepseek/deepseek-v4-flash:free"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Jarvis - Noor System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #0d1117; color: #c9d1d9; }
        #chat { height: 60vh; overflow-y: auto; border: 1px solid #30363d; padding: 15px; border-radius: 8px; margin-bottom: 15px; background: #161b22; }
        .msg { margin: 8px 0; padding: 10px; border-radius: 8px; max-width: 85%; }
        .user { background: #1f6feb; color: white; margin-left: auto; text-align: right; }
        .jarvis { background: #21262d; border: 1px solid #30363d; }
        input[type="text"] { width: 75%; padding: 12px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: #c9d1d9; font-size: 16px; }
        button { padding: 12px 20px; border-radius: 8px; background: #238636; color: white; border: none; cursor: pointer; font-size: 16px; }
        .status { font-size: 12px; color: #8b949e; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h2>🤖 Jarvis <span style="font-size:14px;color:#8b949e;">— Noor System</span></h2>
    <div class="status" id="status">🟡 Initializing...</div>
    <div id="chat"></div>
    <input type="text" id="input" placeholder="Ask Jarvis anything..." onkeypress="if(event.key==='Enter') send()">
    <button onclick="send()">Send</button>

    <script>
        async function checkStatus() {
            try {
                const r = await fetch('/status');
                const d = await r.json();
                document.getElementById('status').innerHTML = d.local_ollama ? '🟢 Connected to local Jarvis' : '🟠 Using cloud fallback';
            } catch(e) {
                document.getElementById('status').innerHTML = '🔴 Bridge error';
            }
        }
        async function send() {
            const input = document.getElementById('input');
            const msg = input.value.trim();
            if (!msg) return;
            const chat = document.getElementById('chat');
            chat.innerHTML += `<div class="msg user">${msg}</div>`;
            input.value = '';
            chat.innerHTML += `<div class="msg jarvis" id="loading">Thinking...</div>`;
            chat.scrollTop = chat.scrollHeight;
            try {
                const r = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const d = await r.json();
                document.getElementById('loading').innerHTML = d.reply || d.error;
                document.getElementById('loading').id = '';
                chat.scrollTop = chat.scrollHeight;
                checkStatus();
            } catch(e) {
                document.getElementById('loading').innerHTML = 'Error: ' + e.message;
                document.getElementById('loading').id = '';
            }
        }
        checkStatus();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status')
def status():
    try:
        r = requests.get(f"{LOCAL_OLLAMA_URL}/api/tags", timeout=3)
        return jsonify({"local_ollama": r.status_code == 200, "models": r.json().get("models", [])})
    except:
        return jsonify({"local_ollama": False, "fallback": "openrouter"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    # Try local Ollama first
    try:
        r = requests.post(f"{LOCAL_OLLAMA_URL}/api/generate", json={
            "model": LOCAL_MODEL,
            "prompt": message,
            "stream": False
        }, timeout=30)
        if r.status_code == 200:
            return jsonify({"reply": r.json()["response"].strip(), "source": "local"})
    except:
        pass
    
    # Fallback to OpenRouter
    if OPENROUTER_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            r = requests.post(OPENROUTER_URL, json={
                "model": FALLBACK_MODEL,
                "messages": [{"role": "user", "content": message}]
            }, headers=headers, timeout=60)
            if r.status_code == 200:
                return jsonify({"reply": r.json()["choices"][0]["message"]["content"], "source": "openrouter"})
        except:
            pass
    
    return jsonify({"reply": "Jarvis is offline. Please try again later.", "source": "none"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
