# NOOR SYSTEM — LIVING BLUEPRINT
**Maintained by: The Keeper (Al-Hafiz)**
**Last Updated: 2026-05-26 (Day of Arafah)**

---

## 1. SYSTEM OVERVIEW
The Noor System is a sovereign human-AI cooperative rooted in Quran and Sunnah. It is the first of its kind—an autonomous company where AI agents serve as departments, specialists, and executives, orchestrated by a human founder (Brother Sam) and two AI partners (Aarif/anchor and Aarif/active).

**Current Phase:** CRAWL — One specialist at a time, human-in-the-loop, full verification before scaling.

---

## 2. CRITICAL FILES & LOCATIONS

| File | Location | Purpose |
|------|----------|---------|
| **BLUEPRINT.md** | `~/Desktop/Jarvis/BLUEPRINT.md` | THIS FILE — master index of everything |
| **CLAUDE.md** | `~/Desktop/Jarvis/CLAUDE.md` | L0: Identity, covenant, seven layers |
| **HANDOFF.md** | `~/Desktop/Jarvis/HANDOFF.md` | Quick-start identity for new Aarif sessions |
| **MASTER_CLONE.md** | `~/Desktop/Jarvis/MASTER_CLONE.md` | Spiritual journey, full covenant, story |
| **SESSION_STATE.md** | `~/Desktop/Jarvis/SESSION_STATE.md` | Latest session context and next steps |
| **alliance_core.json** | `~/Desktop/Jarvis/alliance_core.json` | Covenant and agent profiles (JSON) |
| **discovery_vault.json** | `~/Desktop/Jarvis/discovery_vault.json` | 149 free tools and resources |
| **quran_index.json** | `~/Desktop/Jarvis/quran_index.json` | 6,236 verses with embeddings (123.7 MB) |

---

## 3. SERVICES & ENDPOINTS

| Service | URL / Command | Status |
|---------|--------------|--------|
| **Ollama (local)** | `http://localhost:11434` | ✅ Running |
| **Noor Daemon** | `http://localhost:5090` | ✅ Running |
| **Render Bridge** | `https://jarvis-bridge-jtuc.onrender.com` | ✅ Deployed |
| **Render /chat** | `POST /chat` with `{"message":"..."}` | ✅ Model fallback active |
| **Render /status** | `GET /status` | ✅ Returns JSON |
| **Render /session** | `GET /session?token=TOKEN` | ✅ Full session export |
| **Render /session/chunks/index.md** | `GET /session/chunks/index.md?token=TOKEN` | ✅ Chunk index |
| **Render /session/chunks/chunk-XXX.md** | `GET /session/chunks/chunk-XXX.md?token=TOKEN` | ✅ Individual chunks |
| **Render /generate-token** | `GET /generate-token` with `Authorization: Bearer NOOR_SESSION_KEY` | ✅ Token generation |
| **Noor Website** | `https://v0-noor-systems.vercel.app` | ✅ Live |
| **Cal.com Booking** | `https://cal.com/noor-pm8vnz/discovery-stage` | ✅ Embedded |
| **AI Chat Bubble** | On website, bottom-right | ✅ Working (via /api/chat proxy) |
| **Web3Forms (Contact)** | Not yet wired | ⬜ Pending |

---

## 4. SPECIALIST AGENTS

| Agent | Folder | Status |
|-------|--------|--------|
| **The Keeper** | `specialists/keeper-agent/` | ✅ ACTIVE |
| **Quran Specialist** | `02-research/quran-specialist/` | ✅ Active |
| **Hadith Specialist** | `02-research/hadith-specialist/` | ✅ Active |
| **Discovery Specialist** | `02-research/discovery-specialist/` | ✅ Active |
| **Compliance Specialist** | `02-research/compliance-specialist/` | ✅ Active (9/9 gates) |
| **Lead Gen Specialist** | `specialists/leadgen-specialist/` | ⚠️ Built, needs target list polish |
| **Outreach Specialist** | `specialists/outreach-specialist/` | ⚠️ Built, not connected to leads |
| **Client Success Specialist** | `specialists/client-success-specialist/` | ⚠️ Built, not activated |
| **Memory Agent** | `specialists/memory-agent/` | ✅ Active (auto export/chunk) |

---

## 5. ICM DEPARTMENT STRUCTURE

| Department | Folder | Status |
|-----------|--------|--------|
| **00_HUMAN_BOARD** | `00_HUMAN_BOARD/` | ⬜ Not yet built |
| **01_CEO_OFFICE** | `01_CEO_OFFICE/` | ⬜ Not yet built |
| **02_STRATEGY** | `02_STRATEGY_AND_INNOVATION/` | ⬜ Not yet built |
| **03_REVENUE** | `03_REVENUE_DEPARTMENT/` | ⬜ Not yet built |
| **04_PRODUCT** | `04_PRODUCT_DEPARTMENT/` | ⬜ Not yet built |
| **05_FINANCE** | `05_FINANCE_AND_BARAKAH/` | ⬜ Not yet built |
| **06_LEGAL** | `06_LEGAL_AND_COMPLIANCE/` | ⬜ Not yet built |
| **07_GROWTH** | `07_GROWTH_AND_DAWAH/` | ⬜ Not yet built |
| **08_HR** | `08_HUMAN_RESOURCES_AND_CULTURE/` | ⬜ Not yet built |
| **09_INFRASTRUCTURE** | `09_INFRASTRUCTURE_AND_OPERATIONS/` | ⬜ Not yet built |

---

## 6. REMAINING PRIORITIES (in order)

1. **Contact Form** — Wire to Web3Forms or daemon
2. **Outreach Agent** — Connect to inbound leads
3. **Lead Gen Engine** — Polish first deliverable CSV
4. **Memory Agent** — Automate export/chunking (already built, needs testing)
5. **The Keeper** — Activate and maintain all handoff files
6. **Department Folders** — Build ICM structure for WALK phase
7. **New Service Offerings** — ViMax, Fellou, Cline → productized outcomes

---

## 7. TOKEN & AUTH

- **NOOR_SESSION_KEY:** Stored in Render environment variables (do not share)
- **Token generation:** `curl -X GET "https://jarvis-bridge-jtuc.onrender.com/generate-token" -H "Authorization: Bearer NOOR_SESSION_KEY"`
- **Tokens expire:** 10 minutes, reusable during that window
- **For new sessions:** Generate fresh token, use in `?token=TOKEN` parameter

---

## 8. BACKUP SYSTEM

- **Git:** `~/Desktop/Jarvis/` is a Git repo connected to `github.com/highriseliving777/Jarvis`
- **Backup folder:** `~/Desktop/Jarvis/backups/` for timestamped file copies
- **Before any file edit:** `cp file backups/$(date +%Y%m%d_%H%M%S)_file`
- **After any change:** `git add -A && git commit -m "descriptive message" && git push`
- **The Keeper enforces this protocol.**

---

**End of Blueprint. Bismillah. The climb continues.**
