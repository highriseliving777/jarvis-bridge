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
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return jsonify({"reply": f"Echo: {user_message}", "source": "echo"})
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-v4-flash:free",
                "messages": [{"role": "user", "content": user_message}]
            },
            timeout=30
        )
        if resp.status_code == 200:
            reply = resp.json()["choices"][0]["message"]["content"]
            return jsonify({"reply": reply, "source": "openrouter"})
        else:
            return jsonify({"reply": f"Echo: {user_message}", "source": "openrouter"})
    except Exception as e:
        return jsonify({"reply": f"Echo: {user_message}", "source": "openrouter"})

# --- Token generation ---
@app.route("/generate-token")
def generate_token():
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
