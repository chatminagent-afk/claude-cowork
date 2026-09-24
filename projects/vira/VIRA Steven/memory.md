# memory.md — VIRA Steven

## What it is
Steven's own WhatsApp sales/demo bot — **"Steven versi AI"**. Unlike the client
instances (the scholars, Persada Cisoka), Steven is both builder and owner: this bot
**is** the product demo for selling VIRA as a service, not a service delivered to
someone else. Forked from Persada Cisoka's `2026-08-08-VIRA-PCR-Main-V2.1` (91 nodes)
via an idempotent transform script.

Runs on Steven's own mixed-use personal number (`6285155202354`) — colleagues, family,
and other personal chats share the same number as the bot. This is the single biggest
constraint on the project and shapes every gating decision.

## Workflow — how work moves here
1. Each work session gets logged as a numbered section in the detailed memory doc
   (`docs/2026-08-17-memory-proyek-VIRA-Steven.md`) — build changes, live-test results,
   and root-cause findings, in order. That doc is the actual project brain; this file is
   just the fast-orientation summary.
2. Cadence so far: build → write `catatan-build-workflow` + `checklist-deploy` →
   live-test via WhatsApp from the admin number → audit findings → next session's fixes.
   Older `catatan-build-workflow`/`checklist-deploy` versions are marked KEDALUWARSA
   (expired) in-place rather than deleted, once a newer version supersedes them.
3. Deep audits (like Sesi 5's three-subagent parallel read of workflow JSON + database +
   docs) happen when symptoms don't match earlier hypotheses — read large files via
   parallel subagents, ask for raw quotes not summaries.

## Current status (as of Sesi 5, 2026-08-17 — verify freshness before relying on this)
Four workflows live: Main (active), Error Notifier (built, ID not yet wired into Main),
Buffer Cleanup (active, daily 03:00 WIB), Follow-up (deliberately inactive until bot
behavior stabilizes).

**Open bugs, most urgent first** — full detail + root causes in the linked doc:
- 🔴🔴 **B-3**: number gating is default-ALLOW — blocklist config is silently never read
  (parsed in one node, checked in another that never receives it). Anyone who messages
  the bot number gets a reply right now.
- 🔴 **B-1**: media never actually sends (3 stacked causes: AI hallucinates "sudah
  kirim" without the send tag; 5 of 6 LINKS URLs point to the same wrong file; failures
  only notify admin, user is never corrected).
- 🔴 **B-2**: deck-request admin notification fails silently — a `Wait` node breaks
  access to upstream node data, so the notify step fires with empty phone/message.
- 🔴 **B-2b**: the Tier-1 data gate blocks *saving* captured data, not just notifying —
  should only gate the notification.
- 🔴 **B-2c**: reply model is hardcoded to Haiku, not the Sonnet every doc/config claims.

## Key decisions (durable)
- Same identity principle as other VIRA instances: No WA primary, `lid` backup, never
  `rows[0]` fallback.
- 3-tier brief extraction (mandatory / actively-dug / mentioned-only) — empty fields are
  a call-list for Steven, not a failure.
- Bot persona never names Steven's actual clients or employer by name — generic
  descriptions only ("salah satu klienku platform edukasi", "bank swasta nasional").
- Follow-up intentionally OFF until behavior is stable; `deck_requested=Y` prospects
  are excluded from that pause.

## File map
- `docs/2026-08-17-memory-proyek-VIRA-Steven.md` — full session history + bug detail (this file's source)
- `docs/2026-08-16-checklist-deploy-VIRA-Steven.md` — current deploy checklist
- `docs/2026-08-16-desain-brief-deck-request.md` — deck-request feature spec
- `sheet/` — live sheet header reference + database export
- `workflow/` — current n8n JSON exports (Main/Buffer-Cleanup/Error-Notifier/Followup,
  all dated 2026-08-15 and edited in place since), system prompt, latest build notes,
  validation scripts (`_cek_js.py`, `_transform.py`, `_uji_parser.py`, `_validasi.py`)
- `arsip/` — superseded v1 checklist + v1 build notes (explicitly marked KEDALUWARSA),
  and the pre-fix Main workflow snapshot taken just before Sesi 3's 25-step transformation

## Related
- Fork source: `../Persada Cisoka Residence/memory.md`
- Content about this project: `../VIRA/memory.md`
