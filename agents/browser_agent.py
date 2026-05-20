#!/usr/bin/env python3
"""Browser Agent — Playwright + Firefox, Ollama-driven, sovereign."""
import sys, asyncio
from playwright.async_api import async_playwright

async def run(url):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        text = await page.inner_text("body")
        await browser.close()
        return text[:5000]

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://toolify.ai"
    result = asyncio.run(run(url))
    print(result)
