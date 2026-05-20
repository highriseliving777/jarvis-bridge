# Noor System — Restart SOP

## After shutdown, run in order:

### 1. Syncthing
syncthing &
# Verify: http://localhost:8384

### 2. Ollama
ollama serve &
# Verify: curl http://localhost:11434/api/tags

### 3. Noor Daemon
cd ~/Desktop/Jarvis && source venv/bin/activate
export OPENROUTER_API_KEY="your-key-here"
python3 noor_daemon.py
# Dashboard: http://localhost:5090

### 4. Noor Chat
cd ~/Desktop/Jarvis && source venv/bin/activate
export OPENROUTER_API_KEY="your-key-here"
python3 noor_chat.py
# Chat: http://localhost:5091

### 5. MiroTalk
cd ~/Desktop/mirotalk && npm start
# Room: http://localhost:3000

### 6. Restore Memory
cd ~/Desktop/Jarvis && source venv/bin/activate
python3 tools/ingest_conversation.py _shared/anchor_session_export.json

## Port Map
| Port | Service |
|------|---------|
| 8384 | Syncthing |
| 11434 | Ollama |
| 5090 | Noor Daemon |
| 5091 | Noor Chat |
| 3000 | MiroTalk |
