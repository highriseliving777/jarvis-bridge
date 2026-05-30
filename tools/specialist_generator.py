#!/usr/bin/env python3
"""
specialist_generator.py - Clone Army Engine
Takes a job description and creates a specialist folder with identity.md, rules.md, tools.md, and mission.md.
"""

import os, re, sys, argparse, requests
from datetime import datetime
from pathlib import Path

def sanitize_folder_name(text: str) -> str:
    name = re.sub(r'[^\w\s-]', '', text).strip()
    name = re.sub(r'[-\s]+', '_', name).lower()[:50].strip('_')
    return name or "specialist"

def extract_title_with_ai(description: str) -> str:
    prompt = "Extract a short, descriptive job title (3-5 words max) from this job description. Return ONLY the title, nothing else.\n\n" + description
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
            timeout=30
        )
        if resp.status_code == 200:
            title = resp.json()["response"].strip().replace('"', '').replace("'", "").replace("\n", " ").strip()
            return title[:60] if title else "AI Specialist"
    except:
        pass
    first_line = description.strip().split('\n')[0][:60]
    return sanitize_folder_name(first_line) if first_line else "AI Specialist"

def extract_job_details(description: str):
    title = extract_title_with_ai(description)
    skill_keywords = ['python', 'javascript', 'sql', 'scraping', 'web scraping', 'beautifulsoup',
                      'selenium', 'api', 'machine learning', 'ai', 'nlp', 'data analysis',
                      'excel', 'automation', 'compliance', 'gdpr', 'lead generation', 'reporting']
    desc_lower = description.lower()
    found_skills = list(set(kw for kw in skill_keywords if kw in desc_lower))[:5] or ["problem solving", "attention to detail"]
    req_pattern = r'(?i)(must|should|need|required|responsible for)[^.!?]*[.!?]'
    requirements = re.findall(req_pattern, description)
    if not requirements:
        sentences = re.split(r'[.!?]', description)
        requirements = [s.strip() for s in sentences if s.strip()][:3]
    return {"title": title, "skills": found_skills, "requirements": requirements[:3]}

def write_identity_file(path, details):
    path.write_text(f"# {details['title']} – Identity\n\nI am a specialist AI agent focused on **{details['title']}**.\n\n"
                    f"Core skills: {', '.join(details['skills'])}\n"
                    "I operate within Noor System’s ICM framework, upholding precision, transparency, and the covenant of honest work.\n")

def write_mission_file(path, details, description):
    reqs = '\n'.join(['- ' + r for r in details['requirements']]) if details['requirements'] else '- Execute the assigned task'
    path.write_text(f"# Mission: {details['title']}\n\n"
                    f"## Goal\nComplete tasks related to {details['title']}.\n\n"
                    f"## What I do\n{reqs}\n\n"
                    f"## Skills\n{', '.join(details['skills'])}.\n\n"
                    f"## Output\nStructured results saved in `output/` with a summary of actions taken.\n")

def write_rules_file(path, details):
    path.write_text(f"# Rules for {details['title']} Specialist\n\n"
                    "1. Read the task description before acting.\n"
                    "2. Ask clarifying questions if needed.\n"
                    "3. Do not hallucinate – if uncertain, propose verification.\n"
                    "4. Respect rate limits and API terms.\n"
                    "5. Never share client data outside Noor System.\n"
                    "6. Prefer open-source tools and local execution.\n"
                    "7. Deliver output in the requested format with a short summary.\n"
                    "8. If a task cannot be completed, explain why and suggest alternatives.\n"
                    "9. Request human intervention via `_review/` folder when needed.\n")

def write_tools_file(path, details):
    tool_map = {
        'scraping': ['BeautifulSoup', 'Scrapy', 'Selenium', 'Playwright'],
        'python': ['Python 3.12+', 'requests', 'pandas', 'numpy'],
        'reporting': ['Markdown', 'Jinja2', 'ReportLab'],
        'api': ['REST APIs', 'GraphQL', 'Postman'],
        'machine learning': ['scikit-learn', 'transformers', 'ollama'],
        'compliance': ['regulatory APIs', 'EU AI Act guidelines'],
        'lead generation': ['Apollo.io API', 'Clearbit', 'Hunter.io']
    }
    suggested = set()
    for skill in details['skills']:
        for key, tools in tool_map.items():
            if key in skill or skill in key:
                suggested.update(tools)
    if not suggested:
        suggested = {'Python', 'requests', 'markdown'}
    path.write_text(f"# Tools for {details['title']}\n\n"
                    f"## Recommended\n{chr(10).join('- ' + t for t in sorted(suggested))}\n\n"
                    "## MCP Servers\n- filesystem\n- web_search (if needed)\n")

def create_specialist(base_dir, description):
    details = extract_job_details(description)
    folder_name = sanitize_folder_name(details['title'])
    specialist_path = base_dir / folder_name
    specialist_path.mkdir(parents=True, exist_ok=True)
    (specialist_path / "_review").mkdir(exist_ok=True)
    (specialist_path / "_temp").mkdir(exist_ok=True)
    (specialist_path / "output").mkdir(exist_ok=True)
    write_identity_file(specialist_path / "identity.md", details)
    write_mission_file(specialist_path / "mission.md", details, description)
    write_rules_file(specialist_path / "rules.md", details)
    write_tools_file(specialist_path / "tools.md", details)
    (specialist_path / "README.md").write_text(f"# {details['title']} Specialist\n\nGenerated {datetime.now().isoformat()}\n\n"
                                               "Files: identity.md, mission.md, rules.md, tools.md\n")
    return specialist_path

def main():
    parser = argparse.ArgumentParser(description="Generate a Noor specialist from a job description.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to a text file containing the job description.")
    group.add_argument("--text", help="The job description as a string.")
    group.add_argument("--stdin", action="store_true", help="Read job description from standard input.")
    parser.add_argument("--base", default="specialists", help="Base directory for specialists (default: 'specialists')")
    args = parser.parse_args()
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            description = f.read()
    elif args.text:
        description = args.text
    elif args.stdin:
        description = sys.stdin.read()
    else:
        print("Error: No input provided.", file=sys.stderr)
        sys.exit(1)
    if not description.strip():
        print("Error: Empty job description.", file=sys.stderr)
        sys.exit(1)
    base_path = Path(args.base)
    base_path.mkdir(exist_ok=True)
    created_path = create_specialist(base_path, description)
    print(f"Specialist created at: {created_path}")
    for f in ["identity.md", "mission.md", "rules.md", "tools.md", "README.md"]:
        if (created_path / f).exists():
            print(f"  - {f}")

if __name__ == "__main__":
    main()
