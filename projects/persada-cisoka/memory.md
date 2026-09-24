# memory.md — Persada Cisoka Residence (VIRA chatbot)

## What it is
WhatsApp telemarketer chatbot for **Persada Cisoka Residence**, a housing developer
(Cisoka/Tangerang area). Client contact: **Om Sulianto**. Remade from VIRA (the scholars)
production logic + `VIRA_TEMPLATE_v1` config layer — not a fresh build, since the template
alone was missing critical V4 fixes (identity No WA/lid, MSG_BUFFER, 2-layer debounce).

6 core functions: survey scheduling, follow-up automation, call redirection to admin,
traffic-source detection (Google/FB/IG), telemarketer persona (unit/KPR/lingkungan),
scheduled handover to the field team.

## Workflow — how work moves here
1. Early phase (2026-07-15/16/17) was date-folder-per-session: architecture docs,
   blueprints, brainstorms written into `2026-07-15/`, `2026-07-16/`, `2026-07-17/`.
2. From 2026-07-17 onward, work shifted to **dated loose docs** describing a single
   change or investigation each — now sorted into `docs/` (analysis/planning/QA),
   `snippets/` (the actual patched `.js`/`.py` Code-node contents), `data/` (TSV
   pastes for Sheets tabs FAQ/PRODUK).
3. `workflow/production/` holds the live n8n JSON exports (numbered/dated, e.g.
   `2026-08-21-VIRA-PCR-fix-retrieval-clean-v2.json`) + `PCR_Database.xlsx`.
   `workflow/arsip/` holds superseded exports by date. `workflow/followup/` is the
   (separately tracked, partially built) follow-up workflow.
4. Go-live readiness is tracked via dated checklists (`docs/2026-07-18-checklist-go-live…`,
   `…07-21-checklist-go-live…`, `…08-07-checklist-deploy-V2.1-Vision.md`) — each supersedes
   the last rather than being edited in place.
5. Two **root-level living trackers** (not moved into `docs/`, kept visible):
   `pending changes 100x load.md` and `Pending Waiting Changes.md` — check these first,
   they represent current open work, not history.
6. Client-supplied material (chat exports, brochures, price lists, unit photos/videos)
   lands in `data dari telemarketer/`, sorted by contact/media type.

## Current status
V2.1 Vision enhancement shipped (checklist `docs/2026-08-07-checklist-deploy-V2.1-Vision.md`).
**Currently deployed: `workflow/production/2026-08-21-VIRA-PCR-fix-retrieval-clean-v2.json`**
(confirmed by Steven 2026-08-21) — the final of that day's retrieval-fix iteration
chain. The baseline pre-fix export and the two earlier same-day iterations are archived
to `workflow/arsip/`.

## Key decisions (durable)
- Same identity principle as the scholars: No WA primary, `lid` backup, never `rows[0]` fallback.
- Media delivery uses Kirimi's existing `media_url` field on `POST /v1/send-message` — no
  new endpoint needed; brochures hosted at a public URL.
- AI output tag pattern extended from the scholars' `[SEND_GFORM]`/`Talk To Sam`:
  `[SCHEDULE_SURVEY]`, `[SEND_MEDIA: key]`.
- Old `VIRA_Follow_Up.json` was found silently broken (read a `STATS.timestamp` column
  V4 no longer writes) — follow-up was redesigned against the real V4 STATS schema
  (`last_reply_ts`).
- Field name gotcha: Kirimi recipient field = `phone`, not `receiver` (matches public docs'
  wrong claim). `debounce_ts` in STATS is the debounce baton column — must exist.

## Open items
- Follow-up workflow (`workflow/followup/`) still incomplete — columns
  `flag_survey`/`follow_up_count`/`last_follow_up_ts` have no writer yet.
- Waiting on client: Zoom session results with telemarketer team, successful WA chat →
  survey export, full product data (pricing, unit types, KPR banks, admin/field-team numbers).

## File map
- `docs/` — dated analysis, planning, QA, checklist docs
- `snippets/` — patched Code-node `.js`/`.py` source + one import-nodes `.json`
- `data/` — TSV Sheets pastes (FAQ, PRODUK)
- `workflow/production/` — **current deployed** JSON (`…fix-retrieval-clean-v2.json`) +
  the always-on support workflows (MSG_BUFFER Cleanup, Error Notifier, Follow-up) +
  `PCR_Database.xlsx`
- `workflow/arsip/` — superseded workflow exports (pre-fix baseline, earlier same-day
  retrieval-fix iterations, the explicitly-unused V2.1 Main draft)
- `workflow/followup/`, `workflow/_extraction/` — in-progress follow-up build + original
  extraction scripts
- `arsip/` — early planning phase (`2026-07-15/16/17` blueprint/architecture docs) and
  the already-merged `2026-07-25-sesi2-kode-patch/` security patch snippets
- `data dari telemarketer/` — client-supplied chats, media, brochures
- `render ai/` — AI-generated property renders
- `invoice/` — billing records
- Root: `pending changes 100x load.md`, `Pending Waiting Changes.md` (active trackers)

## Related
- Fork source: `../the scholars/memory.md`
- Shared dashboard: `../VIRA Dashboard/memory.md`
