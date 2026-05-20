#!/usr/bin/env python3
"""Lead Scraper — Firefox scrape → OpenRouter → leads. Accepts URL + target type."""
import sys, asyncio, os, requests
from playwright.async_api import async_playwright

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

async def scrape(url):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        text = await page.inner_text("body")
        await browser.close()
        return text

def extract_via_openrouter(text, target_type):
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "google/gemini-2.5-flash-lite",
        "messages": [{"role": "user", "content": f"Extract every company or organization listed in this directory text as a JSON array. Include name, website (if visible), and what they do. Target type: {target_type}. Return only JSON.\n\n{text}"}]
    }
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
    return r.json()["choices"][0]["message"]["content"]

def extract_via_ollama(text, target_type):
    prompt = f"Extract every company or organization from this text as JSON array (name, website, description). Target: {target_type}. Only from text.\n\n{text[:1000]}"
    r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=300)
    return r.json()["response"]

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://toolify.ai"
    target_type = sys.argv[2] if len(sys.argv) > 2 else "AI tool companies"
    print(f"Scraping {url} for: {target_type} …")
    raw = asyncio.run(scrape(url))
    if OPENROUTER_KEY:
        print("Using OpenRouter (fast) …")
        leads = extract_via_openrouter(raw[:5000], target_type)
    else:
        print("Using local Ollama (truncated) …")
        leads = extract_via_ollama(raw, target_type)
    print(leads)
