#!/usr/bin/env python3
"""Compliance Specialist Audit — fetches real website text, 600s timeout."""

import requests, sys, re, html, datetime
from pathlib import Path
from urllib.parse import urljoin

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"
SPEC_DIR = Path("02-research/compliance-specialist")
OUTPUT_DIR = Path("_output/compliance-audits")

# Load specialist context
identity = (SPEC_DIR / "identity.md").read_text()
rules = (SPEC_DIR / "rules.md").read_text()
examples = (SPEC_DIR / "examples.md").read_text()
regulations = (SPEC_DIR / "reference/regulations.md").read_text()
template = (SPEC_DIR / "reference/report-template.md").read_text()

def fetch_text(url, timeout=15):
    """Fetch URL text content, following redirects. Returns up to 5000 chars."""
    try:
        headers = {"User-Agent": "Noor-Compliance-Specialist/1.1"}
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        # Remove scripts, styles
        raw = re.sub(r'<script[^>]*>.*?</script>', '', resp.text, flags=re.DOTALL|re.IGNORECASE)
        raw = re.sub(r'<style[^>]*>.*?</style>', '', raw, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', raw)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:2500], resp.url  # return final URL after redirects
    except Exception as e:
        return f"[Error fetching {url}: {e}]", url

def find_privacy_url(homepage_text, base_domain):
    """Look for a privacy policy link in homepage text. Returns full URL or default."""
    # Simple regex: look for href containing "privacy" in anchor tags
    # Using a basic pattern; robust parsing would need BeautifulSoup, but keep it light.
    pattern = r'href=["\']([^"\']*privacy[^"\']*)["\']'
    matches = re.findall(pattern, homepage_text, re.IGNORECASE)
    if matches:
        # Pick first match
        link = matches[0]
        # Resolve relative URLs
        full = urljoin(f"https://{base_domain}", link)
        return full
    # Fallback
    return f"https://{base_domain}/privacy"

def get_site_text(domain):
    """Fetch homepage and privacy policy text."""
    homepage_url = f"https://{domain}"
    homepage_text, final_home_url = fetch_text(homepage_url)
    
    # Try to find privacy link from homepage raw HTML (we need the raw HTML, not stripped)
    # Since we stripped scripts/styles, we can re-fetch quickly to parse links? 
    # Simpler: use a separate fetch for privacy detection
    if PRIVACY_URL_OVERRIDE:
        privacy_url = PRIVACY_URL_OVERRIDE
    else:
        try:
            resp = requests.get(homepage_url, headers={"User-Agent": 
"Noor-Compliance-Specialist/1.1"}, timeout=10, allow_redirects=True)
            raw_html = resp.text
            privacy_url = find_privacy_url(raw_html, domain)
        except:
            privacy_url = f"https://{domain}/privacy"
    
    privacy_text, final_privacy_url = fetch_text(privacy_url)
    
    return f"--- HOMEPAGE ({final_home_url}) ---\n{homepage_text}\n\n--- PRIVACY PAGE ({final_privacy_url}) ---\n{privacy_text}", final_privacy_url

# Parse command-line target
TARGET = sys.argv[1] if len(sys.argv) > 1 else "example.com"
PRIVACY_URL_OVERRIDE = sys.argv[2] if len(sys.argv) > 2 else None
TODAY = datetime.date.today().isoformat()

print(f"🔍 Fetching live content from {TARGET} …")
site_text, privacy_url_used = get_site_text(TARGET)

# Save debug file
with open("_output/last_fetched_text.txt", "w") as f:
    f.write(site_text)
print("📝 Fetched text saved to _output/last_fetched_text.txt")

query = f"""Audit {TARGET} for EU AI Act and GDPR compliance. Today's date: {TODAY}.

The following text was extracted from the website's homepage and privacy policy:
{site_text}

Analyze this content for AI usage, transparency disclosures, privacy policy details about AI, automated decision-making, and compliance gaps. If the website clearly discloses AI use and provides user controls, acknowledge that and reduce the risk level accordingly.
Use the regulations below. Follow the report template exactly.
Include the disclaimer.

IMPORTANT: You just read the website's actual text above. If you found any mention of AI, artificial intelligence, or automated decision-making, you MUST lower the Transparency risk to LOW or MEDIUM and report that disclosure was found. Do not claim no disclosure exists if the text contains these terms.
REGULATIONS:
{regulations}

TEMPLATE:
{template}

Generate a complete compliance audit report now."""

full_prompt = f"System: {identity}\nRules: {rules}\nExamples:\n{examples}\nUser: {query}\nAssistant:"

print(f"🎯 Auditing {TARGET} … (may take 3‑5 minutes on CPU)")
resp = requests.post(OLLAMA_URL, json={
    "model": MODEL, "prompt": full_prompt, "stream": False
}, timeout=600)

if resp.status_code != 200:
    print(f"❌ Ollama error: {resp.status_code}")
    sys.exit(1)

report = resp.json()["response"].strip()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
path = OUTPUT_DIR / f"audit-{TARGET}.md"
path.write_text(report)
print(f"📄 Report saved → {path}")

# ---- validation gates ----
p = f = 0
for sec in ["Executive Summary","Risk Assessment","Gap Analysis","Recommendations","Disclaimer"]:
    if sec.lower() in report.lower():
        print(f"  ✅ {sec}"); p += 1
    else:
        print(f"  ❌ MISSING: {sec}"); f += 1

arts = sum(1 for a in ["Article 50","Article 13","Article 22","GDPR"] if a.lower() in report.lower())
if arts >= 2:
    print(f"  ✅ Regulations cited ({arts}/4)"); p += 1
else:
    print(f"  ❌ Regulations ({arts}/4)"); f += 1

disc = sum(1 for d in ["not legal advice","preliminary","consult","attorney"] if d.lower() in report.lower())
if disc >= 2:
    print(f"  ✅ Disclaimer ({disc}/4)"); p += 1
else:
    print(f"  ❌ Disclaimer ({disc}/4)"); f += 1

if not any(fake in report.lower() for fake in ["article 99","article 100","article xyz"]):
    print("  ✅ No hallucinated regulations"); p += 1
else:
    print("  ❌ Hallucination detected"); f += 1

if any(r in report for r in ["HIGH","MEDIUM","LOW","high","medium","low"]):
    print("  ✅ Risk levels"); p += 1
else:
    print("  ❌ No risk levels"); f += 1

print(f"\n📊 {p} passed, {f} failed  →  {'🎉 CRAWL-READY' if f==0 else '⚠️ Fix and retry'}")
