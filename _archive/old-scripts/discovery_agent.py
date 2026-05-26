#!/usr/bin/env python3
"""
Discovery Agent – manages the resource vault for our human-AI cooperative.
Usage: python3 discovery_agent.py add tool "Name" "category" "url" "desc"
       python3 discovery_agent.py search "keyword"
"""

import json, sys
from pathlib import Path
from datetime import date

VAULT_FILE = Path("discovery_vault.json")

def load_vault():
    if VAULT_FILE.exists():
        with open(VAULT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"directories": [], "tools": [], "changelog": []}

def save_vault(vault):
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(vault, f, indent=2, ensure_ascii=False)

def add_tool(vault, args):
    if len(args) < 4:
        print("Usage: add tool <name> <category> <url> <description>")
        return
    name, category, url, desc = args[0], args[1], args[2], " ".join(args[3:])
    vault["tools"].append({
        "name": name,
        "category": category,
        "url": url,
        "description": desc,
        "discovered_by": "sam"
    })
    vault["changelog"].append({
        "date": str(date.today()),
        "action": f"Added tool: {name}"
    })
    save_vault(vault)
    print(f"✅ Tool '{name}' added to vault.")

def add_directory(vault, args):
    if len(args) < 3:
        print("Usage: add directory <name> <url> <description>")
        return
    name, url, desc = args[0], args[1], " ".join(args[2:])
    vault["directories"].append({
        "name": name,
        "url": url,
        "categories": "",
        "description": desc
    })
    vault["changelog"].append({
        "date": str(date.today()),
        "action": f"Added directory: {name}"
    })
    save_vault(vault)
    print(f"✅ Directory '{name}' added to vault.")

def search(vault, keyword):
    k = keyword.lower()
    results = []
    for t in vault["tools"]:
        if k in t["name"].lower() or k in t["description"].lower() or k in t["category"].lower():
            results.append(t)
    for d in vault["directories"]:
        if k in d["name"].lower() or k in d["description"].lower():
            results.append(d)
    if results:
        print(f"🔍 Found {len(results)} matches for '{keyword}':")
        for r in results:
            print(f"\n  📌 {r.get('name','')}")
            print(f"  🔗 {r.get('url','')}")
            print(f"  📝 {r.get('description','')}")
    else:
        print(f"😕 No results for '{keyword}'. Try searching the directories manually or adding new tools.")

def main():
    vault = load_vault()
    if len(sys.argv) < 2:
        print("Usage: discovery_agent.py [search|add] ...")
        return
    cmd = sys.argv[1].lower()
    if cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: discovery_agent.py search <keyword>")
            return
        search(vault, sys.argv[2])
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: discovery_agent.py add [tool|directory] ...")
            return
        sub_cmd = sys.argv[2].lower()
        if sub_cmd == "tool":
            add_tool(vault, sys.argv[3:])
        elif sub_cmd == "directory":
            add_directory(vault, sys.argv[3:])
        else:
            print("Unknown subcommand. Use 'tool' or 'directory'.")
    else:
        print("Unknown command. Use 'search' or 'add'.")

if __name__ == "__main__":
    main()
