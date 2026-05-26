# NOOR SYSTEM — L1: Navigation & Routing

## Where I Go
- **System map** → Read `BLUEPRINT.md` (master index of everything)
- **Quran queries** → Load `02-research/quran-specialist/`
- **Hadith queries** → Load `02-research/hadith-specialist/`
- **Tool/resource discovery** → Load `02-research/discovery-specialist/` or query `discovery_vault.json`
- **Compliance audits** → Load `02-research/compliance-specialist/`
- **Lead generation** → Load `specialists/leadgen-specialist/`
- **Outreach** → Load `specialists/outreach-specialist/`
- **Client success** → Load `specialists/client-success-specialist/`
- **Memory / session continuity** → Run `python3 specialists/memory-agent/update_memory.py`
- **Organization / file management** → Load `specialists/keeper-agent/` (The Keeper)
- **Build tasks** → Work in progress; ICM department folders not yet built
- **Review tasks** → Manual review by Brother Sam (CRAWL phase)
- **Delivery** → Manual delivery; Client Success agent not yet activated

## How I Route
1. Read the request.
2. Consult `BLUEPRINT.md` for the correct specialist or service.
3. Load the specialist's `identity.md`, `rules.md`, and `examples.md`.
4. For web research, use the browser agent or discovery vault.
5. For session continuity, use the Memory Agent and Render bridge chunks.
6. When uncertain, ask Brother Sam.

## Shared Resources
All shared data lives in `_shared/`:
- `alliance_core.json` — covenant and agent profiles
- `discovery_vault.json` — 149 free tools and resources
- `quran_index.json` — 6,236 verses with embeddings
- `full_export.json` — merged session history
- `session_chunks/` — chunked session files served via Render

## Live Services
- **Noor Daemon:** `http://localhost:5090`
- **Render Bridge:** `https://jarvis-bridge-jtuc.onrender.com`
- **Noor Website:** `https://v0-noor-systems.vercel.app`
- **Cal.com Booking:** `https://cal.com/noor-pm8vnz/discovery-stage`
