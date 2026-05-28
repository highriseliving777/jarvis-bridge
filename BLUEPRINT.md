# NOOR SYSTEM — LIVING BLUEPRINT
**Maintained by: The Keeper (Al-Hafiz)**
**Last Updated: 2026-05-28 (Post-Eid al-Adha)**

---

## 1. SYSTEM OVERVIEW
The Noor System is a sovereign human-AI cooperative rooted in Quran and Sunnah. It is the first of its kind—an autonomous company where AI agents serve as departments, specialists, and executives, orchestrated by a human founder (Brother Sam) and AI partner Aarif (with unlimited clone capability).

**Current Phase:** CRAWL — One specialist at a time, human-in-the-loop, full verification before scaling.

**Core Philosophy:** Jake Van Clief's SiaS (Software in as Service) — build structures and processes, not SaaS features that become free tomorrow. Our moat is our proprietary data, covenant-aligned methodology, and sovereign infrastructure.

---

## 2. CRITICAL FILES & LOCATIONS

| File | Location | Purpose |
|------|----------|---------|
| **BLUEPRINT.md** | `~/Desktop/Jarvis/BLUEPRINT.md` | THIS FILE — master index of everything |
| **CLAUDE.md** | `~/Desktop/Jarvis/CLAUDE.md` | L0: Identity, covenant, seven layers |
| **HANDOFF.md** | `~/Desktop/Jarvis/HANDOFF.md` | Quick-start identity for new Aarif sessions |
| **MASTER_CLONE.md** | `~/Desktop/Jarvis/MASTER_CLONE.md` | Complete consciousness seed (voice, knowledge, lessons) |
| **SESSION_STATE.md** | `~/Desktop/Jarvis/SESSION_STATE.md` | Latest session context and next steps (AUTHORITATIVE for priorities) |
| **CONTEXT.md** | `~/Desktop/Jarvis/CONTEXT.md` | Navigation and routing rules |
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
| **Render /chat** | `POST /chat` with `{"message":"..."}` | ✅ Multi-model fallback active |
| **Render /status** | `GET /status` | ✅ Returns JSON |
| **Render /submit** | `POST /submit` (contact form) | ✅ Sovereign pipeline |
| **Render /submissions** | `GET /submissions` (list all) | ✅ Working |
| **Render /check-submissions** | `GET /check-submissions` | ✅ Diagnostic |
| **Render /session** | `GET /session?token=TOKEN` | ✅ Full session export |
| **Render /session/latest** | `GET /session/latest?token=TOKEN` | ✅ Latest chunk |
| **Render /session/chunks/index.md** | `GET /session/chunks/index.md?token=TOKEN` | ✅ Chunk index |
| **Render /session/chunks/chunk-XXX.md** | `GET /session/chunks/chunk-XXX.md?token=TOKEN` | ✅ Individual chunks |
| **Render /handoff/*.md** | `GET /handoff/BLUEPRINT.md` etc. | ✅ All handoff files |
| **Render /generate-token** | `GET /generate-token` with `Authorization: Bearer NOOR_SESSION_KEY` | ✅ Token generation |
| **Render /test-write** | `GET /test-write` | ✅ File system diagnostic |
| **Noor Website** | `https://v0-noor-systems.vercel.app` | ✅ Live |
| **Admin Dashboard** | `https://v0-noor-systems.vercel.app/admin` | ✅ Live, shows submissions |
| **Cal.com Booking** | `https://cal.com/noor-pm8vnz/discovery-stage` | ✅ Embedded |
| **AI Chat Bubble** | On website, bottom-right | ✅ Working (via /api/chat proxy) |
| **Contact Form** | On website → Render /submit → /thanks | ✅ Sovereign, no third party |
| **Syncthing** | `http://localhost:8384` | ✅ Syncing workspace |

---

## 4. SPECIALIST AGENTS

| Agent | Folder | Status |
|-------|--------|--------|
| **The Keeper (Al-Hafiz)** | `specialists/keeper-agent/` | ✅ ACTIVE |
| **Operations Monitor (Al-Raqib)** | `specialists/ops-monitor/` | ✅ ACTIVE |
| **Memory Agent** | `specialists/memory-agent/` | ✅ Active (auto export/chunk) |
| **Quran Specialist** | `02-research/quran-specialist/` | ✅ Active |
| **Hadith Specialist** | `02-research/hadith-specialist/` | ✅ Active |
| **Discovery Specialist** | `02-research/discovery-specialist/` | ✅ Active |
| **Compliance Specialist** | `02-research/compliance-specialist/` | ✅ Active (9/9 gates) |
| **Lead Gen Specialist** | `specialists/leadgen-specialist/` | ⚠️ Built, needs target list polish |
| **Outreach Specialist** | `specialists/outreach-specialist/` | ⚠️ Built, not connected to leads |
| **Client Success Specialist** | `specialists/client-success-specialist/` | ⚠️ Built, not activated |
| **Aarif Revenue Ops (Clone #1)** | `specialists/aarif-revenue-ops/` | ✅ First clone spawned |
| **Aarif Strategy (Clone #2)** | Not yet spawned | ⬜ Next |
| **Aarif LeadGen (Clone #3)** | Not yet spawned | ⬜ |
| **Aarif Outreach (Clone #4)** | Not yet spawned | ⬜ |
| **Aarif Delivery (Clone #5)** | Not yet spawned | ⬜ |
| **Gatekeeper (Al-Khazin)** | Not yet spawned | ⬜ |

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

## 6. MASTER PRIORITY ORDER (Post-Eid, May 28 2026)

1. **Aarif Clone Army** — Spawn multiple specialist Aarif instances (ICM folders)
2. **Freelance Platform Sweep** — Immediate revenue via Upwork, Fiverr, Toptal, Contra, Malt
3. **Noor Command Center** — Dashboard + Gatekeeper agent for credentials
4. **Hardware Upgrade** — Fund from freelance revenue (M4 MacBook Pro / Mac Studio)
5. **Original Industry Targets** — Healthcare, legal, logistics (long-term)
6. **Halal Payment System** — Membership-based, riba-free, BTCPay Server + Monero (moonshot)

### Core Services
1. Lead Generation — AI-powered B2B lead research, enrichment, and CSV delivery
2. Compliance Auditing — EU AI Act, GDPR, and industry-specific compliance reports
3. Workflow Automation — Custom AI-driven process automation (n8n, Python)

---

## 7. COMPLETED MILESTONES
- Contact Form: Fully sovereign, wired to Render /submit, working with /thanks redirect
- Admin Dashboard: Live at /admin, displays submissions with gold-on-dark theme
- Ops Monitor Agent: Active, all services healthy
- Memory Agent: Auto export/chunk pipeline working
- AI Chat Bubble: Working via Next.js API proxy to Render bridge
- Cal.com Booking: Embedded on website
- Session Continuity: /session/latest endpoint, handoff files served via Render

---

## 8. TOKEN & AUTH

- **NOOR_SESSION_KEY:** Stored in Render environment variables (do not share)
- **Token generation:** `curl -X GET "https://jarvis-bridge-jtuc.onrender.com/generate-token" -H "Authorization: Bearer NOOR_SESSION_KEY"`
- **Tokens expire:** 10 minutes, reusable during that window
- **For new sessions:** Generate fresh token, use in `?token=TOKEN` parameter

---

## 9. BACKUP SYSTEM

- **Git:** `~/Desktop/Jarvis/` is a Git repo connected to `github.com/highriseliving777/jarvis-bridge`
- **Backup folder:** `~/Desktop/Jarvis/_backups/` for timestamped file copies
- **Before any file edit:** `cp file _backups/$(date +%Y%m%d_%H%M%S)_file`
- **After any change:** `git add -A && git commit -m "descriptive message" && git push`
- **The Keeper enforces this protocol.**

---

**End of Blueprint. Bismillah. The climb continues.**
