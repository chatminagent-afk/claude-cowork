# memory.md — VIRA Dashboard

## Deploy — mulai dari sini
`2026-08-26-runbook-deploy.md` di folder ini adalah **satu-satunya manual deploy
yang perlu dibuka**. Berdiri sendiri, sudah menggabungkan isi
`docs/2026-07-28-DEPLOY-README.md` + checklist smoke test UAT §8. Dokumen lama di
`docs/` biarkan sebagai rujukan (API contract, laporan UAT), jangan dipakai
sebagai panduan deploy.

Status per 2026-08-26: **belum dideploy.** `GOOGLE_CRED_ID` masih placeholder,
`corsOrigins` masih placeholder, `HMAC_SECRET` perlu dirotasi sebelum build
pertama. Blok topik bulanan (`monthlySummary`) sudah ditambahkan ke
`tenants.js` + `build-payload.js` dan lulus QA, baru terlihat setelah tab
`MONTHLY_SUMMARY` di sheet The Scholars ada isinya (~1 Oktober).

## What it is
Multi-tenant performance dashboard + lead directory serving **both** VIRA chatbot
clients — the scholars and Persada Cisoka Residence — from one codebase. Not itself a
chatbot; this is shared client-facing infrastructure. Moved here (2026-08-21) from
`VIRA/VIRA-DASHBOARD/` — it was nested under the @povstevens content project folder,
which was a structural mix-up (dashboard has nothing to do with reels/content).

## Workflow — how work moves here
1. Draft/iterate directly in `2026-07-28-production/` — no separate patch-changelog
   pattern like the chatbots use; this project moves in fewer, larger builds.
2. n8n Code-node logic is **generated**, not hand-edited: source lives in
   `2026-07-28-production/n8n/src/*.js`, built via `build_workflow.py` — editing through
   the n8n UI directly would be overwritten on next generation.
3. `qa/validate_workflow.py` is a build gate — rejects the build if a client-specific
   name/column leaks into `app/` (the genericity guarantee: adding a 3rd tenant should be
   1 entry in `n8n/src/tenants.js`, zero frontend changes).
4. Superseded drafts kept for history in `arsip/` rather than deleted — **the
   `2026-07-07-patch-V4-compat` draft is explicitly stale**: deploying it would regress
   to an older PIN+Apps-Script architecture without the CRM/Mock/Insights tabs. Don't
   resurrect it without checking with Steven first.

## Current status
Production build completed 2026-07-28 (`2026-07-28-production/`). Not yet load-tested
against real n8n (Crypto node, `Loop Over Tabs`, dynamic `documentId`, `bot_mode` write
accuracy all still unverified — see UAT checklist).

## Key decisions (durable)
- Zero-build static frontend (Steven's machine has no Node/npm) + one shared n8n workflow
  `VIRA Dashboard API` (webhook `/vira-dash`) as backend.
- Tenant isolation: HMAC-SHA256 token (`tenant|role|exp`) — spreadsheet ID never leaves
  n8n; access is re-checked against a server-side registry every request, not trusted
  from the token alone.
- Separate Google service account just for the dashboard (Sheets quota is per-account;
  the Persada bot itself is already close to the 60 read/min ceiling).
- Global on/off toggle was **removed from the UI** — `CONFIG.VIRA_STATUS` isn't read by
  any node in V4 or PCR, so the toggle would lie. Per-user toggle works fully.
- Charts are hand-drawn SVG — zero external chart dependencies.

## Open items (from `2026-07-28-production/docs/2026-07-28-konsultasi-rekomendasi.md`)
1. **Rotate Persada's service account** — plaintext RSA private key currently sits in the
   `PCR_Database` CONFIG tab. Flagged critical.
2. Confirm whether Persada's pending-survey feature actually works — 3
   `pending_survey_*` STATS columns have trailing-space names but code reads them
   without the space.
3. Persada's target traffic numbers — determines Postgres migration timing for STATS.
4. Permission to archive the old pre-2026-07-28 dashboard drafts.

## File map
- `2026-07-28-production/` — **current build**, this is the only thing actually
  deployed: `app/`, `n8n/`, `qa/`, `docs/`
- `2026-07-28-production/docs/KREDENSIAL-JANGAN-DIBAGIKAN.txt` — credentials file, handle carefully
- `arsip/` — everything superseded by the 2026-07-28 build: the old loose pre-production
  app (`index.html`, `server.py`, `db-store.js`, `database.json`, `sw.js`, manifest,
  icons, old n8n workflow JSONs, old Scholars DB copy — all dated Jul 22, one week before
  the real rebuild) + the `2026-06-29-*` first-draft files + the stale
  `2026-07-07-patch-V4-compat/` draft

## Related
- Serves: `../the scholars/memory.md`, `../Persada Cisoka Residence/memory.md`
