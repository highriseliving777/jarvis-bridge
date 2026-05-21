import os, json, secrets, time
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)

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

# --- One-time token system ---
_temp_tokens = {}  # token -> expiry

def _validate_bearer(bearer):
    expected = os.environ.get("NOOR_SESSION_KEY", "")
    if expected and bearer == expected:
        return True
    now = time.time()
    expired = [t for t, exp in list(_temp_tokens.items()) if exp < now]
    for t in expired:
        del _temp_tokens[t]
    if bearer in _temp_tokens:
        del _temp_tokens[bearer]
        return True
    return False

@app.route("/generate-token")
def generate_token():
    """Generate a short-lived token (requires permanent key)."""
    auth = request.headers.get("Authorization", "")
    expected = os.environ.get("NOOR_SESSION_KEY", "")
    if not expected or auth != f"Bearer {expected}":
        return jsonify({"status": "unauthorized"}), 401
    token = secrets.token_hex(16)
    _temp_tokens[token] = time.time() + 300  # 5 minutes
    return jsonify({"token": token})

@app.route("/session")
def session_export():
    """Serve the complete Noor session archive. 
    Accepts Authorization: Bearer <key> OR ?token=<temp>.
    Handles both flat array and DeepSeek chat_messages format."""
    bearer = request.args.get("token", "")
    if not bearer:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            bearer = auth.split(" ", 1)[1]
    if not bearer or not _validate_bearer(bearer):
        return jsonify({"status": "unauthorized"}), 401
    
    export_file = Path(__file__).parent / "_shared/full_session_export.json"
    if export_file.exists():
        with open(export_file) as f:
            data = json.load(f)
        # Extract the actual messages array
        if isinstance(data, dict) and "chat_messages" in data:
            messages = data["chat_messages"]
        elif isinstance(data, list):
            messages = data
        else:
            messages = []
        return jsonify({"status": "ok", "messages": messages, "total": len(messages)})
    return jsonify({"status": "empty", "messages": []})


@app.route("/session/messages")
def session_messages():
    """Return a slice of the session messages, with pagination."""
    bearer = request.args.get("token", "")
    if not bearer:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            bearer = auth.split(" ", 1)[1]
    if not bearer or not _validate_bearer(bearer):
        return jsonify({"status": "unauthorized"}), 401

    export_file = Path(__file__).parent / "_shared/full_session_export.json"
    if not export_file.exists():
        return jsonify({"status": "empty", "messages": []})

    with open(export_file) as f:
        data = json.load(f)

    if isinstance(data, dict) and "chat_messages" in data:
        all_msgs = data["chat_messages"]
    elif isinstance(data, list):
        all_msgs = data
    else:
        all_msgs = []

    # Pagination parameters
    try:
        offset = max(0, int(request.args.get("offset", 0)))
        limit = min(100, max(1, int(request.args.get("limit", 50))))
    except ValueError:
        offset, limit = 0, 50

    chunk = all_msgs[offset:offset + limit]
    return jsonify({
        "status": "ok",
        "total": len(all_msgs),
        "offset": offset,
        "limit": limit,
        "returned": len(chunk),
        "has_more": (offset + limit) < len(all_msgs),
        "messages": chunk
    })

# --- Main ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 9070)))
