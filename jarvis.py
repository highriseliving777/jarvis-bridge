#!/usr/bin/env python3
"""
Jarvis v0.6 – Multi-Agent Cooperative (Quran + Hadith + Discovery)
"""

import json, subprocess, requests, re, datetime
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"
MEMORY_FILE = Path("jarvis_memory.json")
ALLIANCE_FILE = Path("alliance_core.json")
QURAN_AGENT = Path("quran_agent.py")
HADITH_AGENT = Path("hadith_agent.py")
DISCOVERY_AGENT = Path("discovery_agent.py")

QURAN_KEYWORDS = [
    "quran", "surah", "ayah", "tafsir", "recite", "revelation", "al-fatiha",
    "al-baqarah", "al-alaq", "tawhid", "shirk", "kufr", "iman", "ihsan",
    "jannah", "jahannam", "yawm", "akhirah", "hereafter", "paradise", "hell",
    "divine", "lord", "allah's book", "book of allah", "holy book"
]

HADITH_KEYWORDS = [
    "hadith", "sunnah", "narrated", "prophet muhammad", "messenger of allah",
    "peace be upon him", "pbuh", "sahih", "bukhari", "muslim", "tirmidhi",
    "nasa'i", "abu dawud", "ibn majah", "narrator", "narrated by",
    "prophet said", "the prophet said", "prophet's saying", "hadith qudsi",
    "forty hadith", "nawawi", "intention", "niyyah", "pillars of islam",
    "five pillars", "prayer", "salah", "fasting", "sawm", "zakat", "hajj",
    "ablution", "wudu", "ghusl", "purification", "tahara", "character",
    "manners", "akhlaq", "modesty", "haya", "backbiting", "slander",
    "anger", "patience", "sabr", "gratitude", "shukr", "repentance",
    "tawbah", "forgiveness", "dua", "supplication", "dhikr", "remembrance"
]

DISCOVERY_KEYWORDS = [
    "free ai tool", "discovery", "find tool", "ai directory", "resource",
    "what tools", "ai sites", "free resources", "tool for", "ai tools",
    "find me a tool", "any tool", "discover", "ai news", "latest ai"
]

console = Console()

def load_alliance():
    if ALLIANCE_FILE.exists():
        with open(ALLIANCE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return None

def save_alliance(data):
    with open(ALLIANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return []

def save_memory(memory):
    MEMORY_FILE.write_text(json.dumps(memory, indent=2, ensure_ascii=False))

def split_queries(text):
    parts = re.split(r'(?<=[?.])\s+', text)
    return [p.strip().rstrip('?.') for p in parts if p.strip()]

def classify_query(text):
    lowered = text.lower()
    if any(kw in lowered for kw in QURAN_KEYWORDS):
        return "quran"
    if any(kw in lowered for kw in HADITH_KEYWORDS):
        return "hadith"
    if any(kw in lowered for kw in DISCOVERY_KEYWORDS):
        return "discovery"
    return "general"

def run_agent(agent_path, *args):
    try:
        result = subprocess.run(
            ["python3", str(agent_path)] + list(args),
            capture_output=True, text=True, timeout=180
        )
        return result.stdout.strip() if result.returncode == 0 else f"Agent error: {result.stderr}"
    except Exception as e:
        return f"Agent failed: {e}"

def post_to_blackboard(alliance, agent_name, insight):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "from_agent": agent_name,
        "insight": insight
    }
    alliance["blackboard"]["agent_insights"].append(entry)
    if len(alliance["blackboard"]["agent_insights"]) > 50:
        alliance["blackboard"]["agent_insights"] = alliance["blackboard"]["agent_insights"][-50:]

def ask_ollama(prompt, context_messages):
    context = ""
    for msg in context_messages[-6:]:
        context += f"{msg['role'].capitalize()}: {msg['content']}\n"
    full_prompt = context + f"User: {prompt}\nAssistant:"
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False
    })
    if response.status_code == 200:
        return response.json()["response"].strip()
    else:
        return f"Error: {response.status_code}"

def main():
    alliance = load_alliance()
    if alliance:
        console.print("[bold cyan]🤖 Jarvis v0.6[/bold cyan] – Multi-Agent Cooperative")
        console.print(f"[dim]Mission: {alliance['covenant']['mission'][:80]}...[/dim]")
        agents = list(alliance["agent_profiles"].keys())
        agents.append("discovery_agent")
        console.print(f"[dim]Active agents: {', '.join(agents)}[/dim]")
        console.print(f"[dim]Blackboard insights: {len(alliance['blackboard']['agent_insights'])}[/dim]")
    else:
        console.print("[bold red]⚠ Alliance core not found. Run Step 41 first.[/bold red]")
        return

    console.print("Type [bold]'quit'[/bold] to exit.\n")
    memory = load_memory()

    while True:
        user_input = console.input("[bold green]You:[/bold green] ")
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input.strip():
            continue

        queries = split_queries(user_input)
        for q in queries:
            console.print(f"  [dim]→ Processing: '{q}'[/dim]")
            memory.append({"role": "user", "content": q})

            route = classify_query(q)
            if route == "quran":
                console.print("[bold yellow]  → Quranic Research Agent[/bold yellow]")
                reply = run_agent(QURAN_AGENT, q)
                if len(reply) > 20:
                    post_to_blackboard(alliance, "quran_agent", f"Answered: {q[:80]}...")
            elif route == "hadith":
                console.print("[bold yellow]  → Hadith Research Agent[/bold yellow]")
                reply = run_agent(HADITH_AGENT, q)
                if len(reply) > 20:
                    post_to_blackboard(alliance, "hadith_agent", f"Answered: {q[:80]}...")
            elif route == "discovery":
                console.print("[bold magenta]  → Discovery Agent[/bold magenta]")
                reply = run_agent(DISCOVERY_AGENT, "search", q)
                if len(reply) > 20:
                    post_to_blackboard(alliance, "discovery_agent", f"Searched for: {q[:80]}...")
            else:
                reply = ask_ollama(q, memory)

            memory.append({"role": "assistant", "content": reply})
            console.print("[bold blue]Jarvis:[/bold blue]", end=" ")
            console.print(Markdown(reply + "\n"))
        save_memory(memory)
        save_alliance(alliance)

if __name__ == "__main__":
    main()
