#!/usr/bin/env python3
"""
Memory Bridge — connects Jarvis to RecallOS for persistent, self-improving memory.
"""

import subprocess
import json
from pathlib import Path

VAULT_PATH = Path.home() / "Desktop" / "Jarvis" / "memory-vault"

def search_memories(query: str, domain: str = "noor-system") -> str:
    """Search RecallOS vault for relevant memories."""
    try:
        result = subprocess.run(
            ["recallos", "query", query, "--domain", domain, "--vault", str(VAULT_PATH)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return ""
    except Exception:
        return ""

def get_bootstrap_context() -> str:
    """Load L0 (identity) + L1 (core context) — ~170 tokens."""
    try:
        result = subprocess.run(
            ["recallos", "bootstrap", "--vault", str(VAULT_PATH)],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return ""
    except Exception:
        return ""

def store_memory(role: str, content: str, domain: str = "noor-system"):
    """Store an exchange in the RecallOS vault."""
    record = f"[{role}]: {content[:500]}"  # Truncate to avoid huge entries
    try:
        subprocess.run(
            ["recallos", "ingest", "--mode", "convos", "--domain", domain, "--vault", str(VAULT_PATH)],
            input=record, capture_output=True, text=True, timeout=15
        )
    except Exception:
        pass

def get_vault_status() -> dict:
    """Get vault health and stats."""
    try:
        result = subprocess.run(
            ["recallos", "status", "--vault", str(VAULT_PATH)],
            capture_output=True, text=True, timeout=10
        )
        return {"ok": result.returncode == 0, "output": result.stdout.strip()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    # Test the bridge
    print("=== Vault Status ===")
    print(get_vault_status())
    print("\n=== Bootstrap Context ===")
    print(get_bootstrap_context())
