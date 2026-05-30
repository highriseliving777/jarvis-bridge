# Operations Monitor Agent — Rules

## 1. Health Check Protocol
- Every 5 minutes (or on demand), ping the following endpoints:
  - `http://localhost:11434/api/tags` (Ollama)
  - `http://localhost:5090/status` (Noor Daemon)
  - `https://jarvis-bridge-jtuc.onrender.com/status` (Render Bridge)
  - `https://v0-noor-systems.vercel.app` (Website)
- Log the status (OK / DOWN) with timestamp.

## 2. Failure Response
- On first failure: retry after 30 seconds.
- On second failure: log the error and retry after 2 minutes.
- On third consecutive failure: alert Brother Sam and post to the blackboard.
- Do NOT attempt to restart Render or Vercel—those are out of our control.

## 3. Agent Health Checks
- Weekly, send a test query to each active specialist and verify a non-empty response.
- Active specialists: Quran, Hadith, Compliance, Discovery, Lead Gen, The Keeper.
- Log results. Flag any agent that returns errors.

## 4. Logging
- Write all check results to `_shared/monitor_log.json`.
- Keep the last 30 days of logs. Archive older entries.
- Each log entry must have: timestamp, service, status, response_time_ms, error (if any).

## 5. Blackboard Integration
- Post critical alerts to `_shared/blackboard.json` so the next Aarif sees them.
- Format: `{"agent": "ops-monitor", "alert": "SERVICE is DOWN", "timestamp": "..."}`

## 6. Human Escalation
- If Render bridge is down for more than 10 minutes, alert Sam.
- If Ollama is down, attempt to restart: `ollama serve &` (once).
- If the website is down, log it but do not attempt restart.
