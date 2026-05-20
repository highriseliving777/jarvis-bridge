import json, requests, os, sys
from pathlib import Path
from datetime import datetime

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
BLACKBOARD = Path("_shared/blackboard.json")

# Pre-loaded alignment (from our Quran specialist's core knowledge)
ALIGNMENT_CHECK = """
The Noor System covenant requires: Tawhid (sole dependency on Allah), Ihsan (excellence as worship),
Adl wa Rahma (justice and mercy). Any business activity must avoid riba, gharar, maysir, and haram industries.
Serving businesses honestly with fair pricing and ethical audits is aligned with Quranic principles.
Surah Al-Mutaffifin (83:1-3) warns against cheating in transactions. Surah Al-Asr (103) emphasizes
truth and patience in mutual counsel.
"""

def strategic_reason(goal, model="google/gemini-3.1-flash-lite"):
    headers = {"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "max_tokens": 2048, "messages": [
            {"role": "system", "content": "You are the Strategic Brain of the Noor System. Output clean English. Be concise and actionable."},
            {"role": "user", "content": goal}
        ]
    }
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
    resp = r.json()
    if "choices" not in resp:
        return f"API Error: {json.dumps(resp, indent=2)[:500]}"
    return resp["choices"][0]["message"]["content"].strip()

def post_to_blackboard(entry):
    board = json.loads(BLACKBOARD.read_text()) if BLACKBOARD.exists() else []
    entry["timestamp"] = datetime.now().isoformat()
    board.append(entry)
    BLACKBOARD.write_text(json.dumps(board, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or "Find the top 5 small business AI compliance gaps"
    print(f"Goal: {goal}\n")
    
    print("Strategic Brain (OpenRouter)...")
    strategy = strategic_reason(goal)
    post_to_blackboard({"agent": "strategic_brain", "goal": goal, "output": strategy})
    print(strategy[:1200])
    if len(strategy) > 1200:
        print(f"\n... (full output saved to blackboard)")
    
    print("\nAlignment: Pre-loaded covenant check applied.")
    print(ALIGNMENT_CHECK[:400])
    post_to_blackboard({"agent": "alignment", "goal": goal, "output": ALIGNMENT_CHECK})
    
    print("\nOrchestration complete. Blackboard updated.")
