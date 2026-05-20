#!/usr/bin/env python3
import json, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"
MEMORY_FILE = Path("/Users/sam/Desktop/Jarvis/jarvis_memory.json")
ALLIANCE_FILE = Path("/Users/sam/Desktop/Jarvis/alliance_core.json")

def load_json(path):
    if path.exists():
        return json.loads(path.read_text())
    return [] if path == MEMORY_FILE else {}

class JarvisHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/chat':
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            msg = body.get('message', '')
            memory = load_json(MEMORY_FILE)
            covenant = load_json(ALLIANCE_FILE).get("covenant", {}).get("mission", "")
            recent = " ".join([f"{m['role']}: {m['content']}" for m in memory[-6:]])
            prompt = f"System: You are Jarvis, a human-AI partner. Mission: {covenant}\n{recent}\nUser: {msg}\nAssistant:"
            try:
                r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=60)
                reply = r.json()["response"].strip() if r.status_code == 200 else "Brain warming..."
            except:
                reply = "Offline."
            memory.append({"role": "user", "content": msg})
            memory.append({"role": "assistant", "content": reply})
            MEMORY_FILE.write_text(json.dumps(memory, indent=2, ensure_ascii=False))
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"reply": reply, "source": "local"}).encode())

    def do_GET(self):
        if self.path == '/status':
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"status": "running", "memory": len(load_json(MEMORY_FILE))}).encode())

if __name__ == '__main__':
    HTTPServer(('localhost', 9070), JarvisHandler).serve_forever()
