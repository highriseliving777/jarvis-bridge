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
        lines = ["=== NOOR SYSTEM BRIEFING ===", ""]
        lines.extend([m["content"] for m in seed])
        briefing = "\n\n".join(lines)
        return jsonify({"status": "ok", "context": briefing, "sources": len(seed)})
    return jsonify({"status": "empty", "context": "No identity seed found."})

# --- Main ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 9070)))
