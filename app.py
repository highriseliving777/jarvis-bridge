import requests
import os, json, secrets, time
from flask import Flask, request, jsonify, Response
from pathlib import Path

app = Flask(__name__)

# --- Reusable token system ---
_temp_tokens = {}  # token -> expiry (10 min, reusable)

def _validate_bearer(bearer: str) -> bool:
    """Check permanent key OR valid temp token. Tokens are NOT consumed."""
    expected = os.environ.get("NOOR_SESSION_KEY", "")
    if expected and bearer == expected:
        return True
    now = time.time()
    # remove expired tokens
    expired = [t for t, exp in list(_temp_tokens.items()) if exp < now]
    for t in expired:
        del _temp_tokens[t]
    return bearer in _temp_tokens

# --- Existing routes ---
@app.route('/')
def index():
    return jsonify({"status": "ok", "service": "jarvis-bridge"})

@app.route('/status')
def status():
    return jsonify({"local_ollama": False, "fallback": "openrouter"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return jsonify({"reply": "OpenRouter key not configured.", "source": "none"})

    # List of free models to try in order
    models = [
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemma-4-26b-a4b-it:free",
        "deepseek/deepseek-v4-flash:free",
        "nvidia/nemotron-3-super-120b-a12b:free"
    ]

    last_error = ""
    for model in models:
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": user_message}]
                },
                timeout=30
            )
            if resp.status_code == 200:
                reply = resp.json()["choices"][0]["message"]["content"]
                return jsonify({"reply": reply, "source": "openrouter", "model": model})
            else:
                last_error = f"{resp.status_code} on {model}"
        except Exception as e:
            last_error = str(e)
    return jsonify({"reply": f"All models unavailable. Last error: {last_error}", "source": "none"})
    auth = request.headers.get("Authorization", "")
    expected = os.environ.get("NOOR_SESSION_KEY", "")
    if not expected or auth != f"Bearer {expected}":
        return jsonify({"status": "unauthorized"}), 401
    token = secrets.token_hex(16)
    _temp_tokens[token] = time.time() + 600  # 10 minutes, reusable
    return jsonify({"token": token})

# --- Session endpoints ---
def _extract_bearer():
    bearer = request.args.get("token", "")
    if not bearer:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            bearer = auth.split(" ", 1)[1]
    return bearer

def _load_messages():
    export_file = Path(__file__).parent / "_shared/full_session_export.json"
    if not export_file.exists():
        return []
    with open(export_file) as f:
        data = json.load(f)
    if isinstance(data, dict) and "chat_messages" in data:
        return data["chat_messages"]
    if isinstance(data, list):
        return data
    return []

@app.route("/session")
def session_export():
    bearer = _extract_bearer()
    if not bearer or not _validate_bearer(bearer):
        return jsonify({"status": "unauthorized"}), 401
    messages = _load_messages()
    return jsonify({"status": "ok", "messages": messages, "total": len(messages)})

@app.route("/session/text")
def session_text():
    bearer = _extract_bearer()
    if not bearer or not _validate_bearer(bearer):
        return jsonify({"status": "unauthorized"}), 401
    messages = _load_messages()
    lines = [f"=== NOOR SYSTEM SESSION ARCHIVE ===\nTotal messages: {len(messages)}\n"]

    # Prepend the session brief if available
    brief_file = Path(__file__).parent / "_shared/SESSION_BRIEF.md"
    if brief_file.exists():
        lines.append("--- SESSION BRIEF ---\n" + brief_file.read_text() + "\n--- END BRIEF ---\n")

    lines.append("--- FULL TRANSCRIPT ---\n")
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        if content:
            lines.append(f"[{i}] {role}: {content}\n")

    full_text = "\n".join(lines)
    return Response(full_text, mimetype="text/plain; charset=utf-8")


@app.route("/context")
def public_context():
    """Return the Noor System identity briefing from the seed file (no database needed)."""
    import json
    seed_file = Path(__file__).parent / "_shared/noor_identity_seed.json"
    if seed_file.exists():
        with open(seed_file) as f:
            seed = json.load(f)
        lines = ["=== NOOR SYSTEM BRIEFING ===\n\nFULL SESSION HISTORY: The complete 1,158-message history is stored in `_shared/session_chunks/` as numbered Markdown files (100 messages each). Read `index.md` first, then open the most recent chunk to continue where we left off. All chunks are available at: https://jarvis-bridge-jtuc.onrender.com/session/chunks/<filename>\n\nTo access a chunk, use a token: https://jarvis-bridge-jtuc.onrender.com/session/chunks/chunk-001.md?token=<token>\n", ""]
        lines.extend([m["content"] for m in seed])
        briefing = "\n\n".join(lines)
        return jsonify({"status": "ok", "context": briefing, "sources": len(seed)})
    return jsonify({"status": "empty", "context": "No identity seed found."})


@app.route("/session/chunks/<filename>")
def serve_chunk(filename):
    """Serve a session chunk file (requires valid token)."""
    bearer = request.args.get("token", "")
    if not bearer:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            bearer = auth.split(" ", 1)[1]
    if not bearer or not _validate_bearer(bearer):
        return jsonify({"status": "unauthorized"}), 401

    chunk_path = Path(__file__).parent / "_shared/session_chunks" / filename
    if not chunk_path.exists():
        return jsonify({"status": "not found"}), 404
    return Response(
        chunk_path.read_text(),
        mimetype="text/markdown; charset=utf-8"
    )

# --- Main ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 9070)))

@app.route("/generate-token")
def generate_token():
    auth = request.headers.get("Authorization", "")
    expected = os.environ.get("NOOR_SESSION_KEY", "")
    if not expected or auth != f"Bearer {expected}":
        return jsonify({"status": "unauthorized"}), 401
    token = secrets.token_hex(16)
    _temp_tokens[token] = time.time() + 600
    return jsonify({"token": token})

# --- Handoff file serving ---
@app.route("/handoff/<filename>")
def serve_handoff(filename):
    """Serve a handoff file from the workspace root (BLUEPRINT.md, CLAUDE.md, etc.)."""
    allowed = {"BLUEPRINT.md", "CLAUDE.md", "HANDOFF.md", "CONTEXT.md", "SESSION_STATE.md", "MASTER_CLONE.md"}
    if filename not in allowed:
        return jsonify({"status": "not found"}), 404
    file_path = Path(__file__).parent / filename
    if not file_path.exists():
        return jsonify({"status": "not found"}), 404
    return Response(file_path.read_text(), mimetype="text/markdown; charset=utf-8")

@app.route("/session/latest")
def session_latest():
    """Redirect to the most recent session chunk."""
    import re
    chunks_dir = Path(__file__).parent / "_shared" / "session_chunks"
    if not chunks_dir.exists():
        return jsonify({"status": "no chunks"}), 404
    # Find highest numbered chunk
    highest = 0
    for f in chunks_dir.glob("chunk-*.md"):
        m = re.search(r"chunk-(\d+)\.md", f.name)
        if m:
            n = int(m.group(1))
            if n > highest:
                highest = n
    if highest == 0:
        return jsonify({"status": "no chunks"}), 404
    chunk_file = f"chunk-{highest:03d}.md"
    bearer = request.args.get("token", "")
    if not bearer:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            bearer = auth.split(" ", 1)[1]
    if not bearer or not _validate_bearer(bearer):
        return jsonify({"status": "unauthorized"}), 401
    chunk_path = chunks_dir / chunk_file
    if not chunk_path.exists():
        return jsonify({"status": "not found"}), 404
    return Response(chunk_path.read_text(), mimetype="text/markdown; charset=utf-8")

@app.route('/submit', methods=['POST'])
def submit_form():
    """Accept contact form submissions and store them."""
    data = request.get_json(silent=True) or request.form.to_dict()
    name = data.get('name', 'Unknown')
    email = data.get('email', '')
    message = data.get('message', '')
    
    # Basic spam check: reject if honeypot field is filled
    if data.get('botcheck'):
        return jsonify({"status": "spam"}), 400
    
    # Minimal validation
    if not email or not message:
        return jsonify({"status": "missing fields"}), 400
    
    import datetime
    submission = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "noor-website"
    }
    
    submissions_file = Path(__file__).parent / "_shared" / "form_submissions.json"
    existing = []
    if submissions_file.exists():
        with open(submissions_file) as f:
            existing = json.load(f)
    existing.append(submission)
    with open(submissions_file, "w") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    
    return jsonify({"status": "ok"})
