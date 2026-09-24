# memory.md — Power Automate Ci Lenny

## What it is
Automations built for **Ci Lenny** (BCA colleague/senior — exact role/team unconfirmed).
Two flows:
1. **Weekly MBI Projects Report** — the main one, actively iterated (V1 → V6.0).
   Reads `Tracking Project MBI (di luar paketan).xlsx` on SharePoint, posts Teams
   adaptive cards.
2. **OtomasiStatusUAT** — UAT status flow, exported once (2026-06-11), no iteration since.

## Workflow — how work moves here
1. A version bump = a new exported `.zip` package named
   `WeeklyMBIProjectsReportV<version>_<timestamp>.zip`, dropped at root.
2. When a new version supersedes the previous one, the **previous zip moves to
   `arsip/`** — root always holds only the current version's package(s). This project
   has iterated far more than the others (V1 → V6.0, ~15 versions in `arsip/`), all
   Jun–Aug 2026.
3. Release notes are written only for larger jumps (`docs/2026-07-25-catatan-rilis-V5.0.md`,
   `docs/2026-08-19-catatan-rilis-V6.0.md`) — not every version gets one.
4. Reference docs (SharePoint URL, adaptive card JSON samples, manual guide) live in
   `arsip/` alongside the old packages rather than at root, since they were written
   early and never needed updating.

## Current status
**V6.0 is confirmed current and in use** (`2026-08-19-WeeklyMBIProjectsReportV.6.0.zip` +
matching release notes) — confirmed by Steven 2026-08-21. V4.8, V4.9, and V5.0 have been
archived to `arsip/` accordingly (root now holds only V6.0).

Known issue: **V6 has parts that don't behave as intended yet** — adjustment was started
but not finished. Steven hasn't specified which parts; ask before assuming V6's output
is fully correct.

## Open items
- Finish the V6 adjustment that was left incomplete (specifics TBD — check with Steven).
- MBI expansion scope unconfirmed.
- Ci Lenny's exact role/team unconfirmed — relevant if the flow needs to expand to
  serve a wider team.
- Five loose files found at root during cleanup (2026-08-21) were unlabeled zip
  exports containing `manifest.json`/Power-Automate-package structure, dated
  Jun 15 / Jul 16 (×2) / Jul 17 / Jul 25 — renamed with `.zip` extension and moved to
  `arsip/` as `<date>-unlabeled-export-<random-id>.zip`. Nobody has identified which
  version/purpose they correspond to; flag to Steven if they turn out to matter.

## File map
- Root — current V6.0 package + `Tracking Project MBI (di luar paketan).xlsx` + SharePoint URL note
- `docs/` — release notes for major version jumps
- `arsip/` — superseded packages (V1–V5.0 + OtomasiStatusUAT), reference docs, the
  newly-labeled unlabeled exports, and a stale V4.3-era working note
  (`2026-07-14-nilai-variable-flow-V4.3.txt`)
