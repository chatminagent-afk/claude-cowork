# AI Systems Audit — Steven's Claude Setup

**Date:** 15 June 2026
**Scope:** 87 sessions of history, CLAUDE.md, and the installed skills/plugins folder.
**Author:** Claude (acting as systems analyst)

---

## 1. What you actually use Claude for

Across 87 sessions, your work clusters into five buckets. Two dominate.

| Rank | Cluster | ~Sessions | What it is |
|------|---------|-----------|------------|
| 1 | **VIRA chatbot (The Scholars)** | ~40 | n8n WhatsApp bot. Bug root-cause, QA/pre-launch audit, surgical JSON patches, version bumps (V2→V5) each with changelog + handoff, dashboards, cost/quota tuning. |
| 2 | **Power Automate weekly reports (day job / BCA)** | ~12 | "Weekly Reminder Ci Lenny – UAT Status" flow. Surgical edits to exported flow JSON, version bump (V4.5→V4.9), simulate against real Excel, byte-level diff verify, re-zip for import. Also GS reminders, adaptive cards. |
| 3 | **Client app work (Metro Logistic, TIM Interior)** | ~15 | PWA dashboard redesign + QA, install/PWA issues, interior pricing/webforms. |
| 4 | **The Scholars business ops** | ~10 | Monthly invoices (recurring), database, pitch decks, sales content, Batch info docs. |
| 5 | **Skill/system building** | ~5 | Building your own skills (sales, session-handoff), role customization. |

**The tasks you repeat by hand most:**
1. Root-cause → surgically patch an automation flow → version + changelog + handoff → simulate → verify minimal diff → wait for approval. (VIRA *and* the Power Automate report are the same discipline.)
2. Pre-launch **QA audit** of a workflow, written as a prioritized findings report (🔴🟠🟡🟢).
3. **Monthly invoice** for The Scholars.
4. **Recurring status report** (weekly UAT / MBI projects).

Your CLAUDE.md already encodes the values that make this work good: plan first, confirm before overwriting, dated filenames, list changed files. The skills below turn that into something a cheaper model can execute.

---

## 2. Skill & plugin audit — keep / fix / merge / delete

> I can't add, edit, or remove skills for you from here — the skills folder is a read-only cache in this session. Everything below is a recommendation; you action it in **Settings → Capabilities** (and, for plugin bundles, by uninstalling the marketplace). **I have not deleted anything.**

### Your own + core Anthropic skills

| Skill | Verdict | One-line reason |
|-------|---------|-----------------|
| **sales** | **KEEP (your best skill)** | Tailored, high-quality, in your voice; a generic "content" skill can't replace it. Do **not** treat as redundant. |
| **fable-mode** | **KEEP** | Directly serves your goal — pushes an everyday model toward Fable-grade judgment on complex tasks. |
| **session-handoff** | **KEEP** | Your VIRA work spans many sessions; clean handoffs are worth it. |
| **skill-creator** | **KEEP** | You actively build skills; this is your tooling. |
| **schedule** | **KEEP** | Invoices + weekly reports are recurring — automate them. |
| **docx / pdf / pptx / xlsx** | **KEEP** | Your core output formats (invoices, decks, reports). |
| **consolidate-memory** | **KEEP** | Cheap memory hygiene; leave on. |
| **morning** | **DECIDE** | Not seen in any of 87 sessions. Keep only if you want a daily brief; otherwise turn off. |
| **setup-cowork** | **DELETE candidate** | One-time onboarding. Its job is done. |

> ⚠️ **Read this twice:** the skill a model is most tempted to flag as "redundant" is **sales** — it overlaps on paper with the marketing plugin's content skills. It is the opposite of redundant; it's the single most valuable custom asset you have. It stays.

### Plugin bundles (installed marketplaces)

These are where the bloat is. They were installed as role bundles, but your actual work is automation-engineering + education-business ops — not marketing/design agency work.

| Bundle / skill | Verdict | Reason |
|----------------|---------|--------|
| **operations: status-report, process-doc, runbook** | **KEEP** | Match your QA reports, handoffs, and SOPs directly. |
| operations: risk-assessment, change-request | KEEP (light) | Occasionally fits pre-launch/ops decisions. |
| operations: capacity-plan, compliance-tracking, vendor-review, process-optimization | **DELETE candidates** | No trace in your history; enterprise-ops noise. |
| **productivity: task-management, memory-management** | **KEEP** | Useful for tracking and context. |
| productivity: start, update | **MERGE** | Overlapping setup/sync helpers; keep one. |
| marketing: draft-content **&** content-creation | **MERGE → keep one** | Near-duplicate skills in the same bundle. |
| marketing: campaign-plan, competitive-brief, email-sequence, performance-report, seo-audit, brand-review | **DELETE candidates** | Marketing-agency workflows you don't run; your `sales` skill covers persuasion better. |
| design: ux-copy, design-critique, accessibility-review | KEEP (light) | Marginal fit for your PWA/dashboard UI work. |
| design: user-research **&** research-synthesis | **MERGE** | Overlapping research skills. |
| design: design-system, design-handoff | **DELETE candidates** | Design-team artifacts you don't produce. |

**Bottom line on plugins:** the **marketing** and **design** marketplaces are ~80% mismatch to your real work. Strongest cleanup: uninstall those two marketplaces, keep **operations** + **productivity** (they partly fit), and lean on your own `sales` skill. Nothing here is deleted until you say so.

---

## 3. New skills worth building

**Built now (see `/skills/`):**
1. **flow-patch** — surgical patching of an automation flow export (n8n JSON or Power Automate .zip): root-cause → minimal diff → version bump + changelog + handoff → simulate against real data → verify → wait for approval. Captures workflows #1 and #2 above.
2. **qa-audit** — pre-launch QA of an automation workflow, output as a prioritized 🔴🟠🟡🟢 findings report with proven root-cause + evidence + fix. Captures your repeated "VIRA QA review".

**Proposed (say the word and I'll build):**
3. **scholars-invoice** — generate the monthly The Scholars invoice from the database/booking data. Recurring 6+ times.
4. **status-report** (thin wrapper on operations:status-report, tuned to your UAT/MBI weekly format).
5. **reel-script** — your `sales` skill references a `reel-script` skill for @povstevens reels that **doesn't exist**. Either build it or remove the reference.

---

## 4. Delete list (nothing removed — confirm before I or you act)

- `setup-cowork` (onboarding, done)
- `morning` (unused — only if you don't want a daily brief)
- operations: `capacity-plan`, `compliance-tracking`, `vendor-review`, `process-optimization`
- marketing bundle except one content skill: `campaign-plan`, `competitive-brief`, `email-sequence`, `performance-report`, `seo-audit`, `brand-review`
- design: `design-system`, `design-handoff`
- Merge (not delete): productivity `start`/`update`; marketing `draft-content`/`content-creation`; design `user-research`/`research-synthesis`

**Not on the list, on purpose:** `sales`, `fable-mode`, `session-handoff`, `skill-creator`, all four core file skills.
