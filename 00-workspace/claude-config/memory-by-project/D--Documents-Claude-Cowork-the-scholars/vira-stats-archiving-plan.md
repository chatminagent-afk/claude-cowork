---
name: vira-stats-archiving-plan
description: "VIRA off_reason (SAM/VIRA) design + 3-monthly STATS cleanup workflow — decisions, node touchpoints, and labeling backlog"
metadata: 
  node_type: memory
  type: project
  originSessionId: d8d8911c-b0e2-414b-8412-09f50374b993
  modified: 2026-08-19T13:59:30.097Z
---

VIRA STATS uses an `off_reason` column (values `SAM` / `VIRA`, matched case-insensitively + trimmed) to distinguish who turned a contact's bot off. `SAM` = Sam's own students/parents, must stay OFF and must never be deleted. `VIRA` = auto-off from a `[TALK_TO_SAM]` handoff, disposable. A cron workflow deletes every STATS row **except** `off_reason = SAM`, every 3 months at 00:01 WIB (`1 0 1 */3 *`, workflow timezone Asia/Jakarta). No archiving — Sam confirmed he never reads STATS data, he only opens it to switch contacts off manually.

**Why:** Sam raised on 2026-08-14 that he couldn't tell his manually-off'd students/parents apart from users VIRA auto-off'd, and wanted the latter re-enabled periodically. Blanket-clearing would wrongly re-enable his students. Steven chose strict deletion (only `SAM` survives — rows that are OFF with a blank label get deleted too) over a fail-safe keep.

**How to apply:** In the main VIRA workflow, `off_reason` must appear in **exactly one** node — `Update row in sheet` (the `IF Talk To Sam` branch), as the literal `VIRA`. It must NEVER be mapped in `Update to STATS`: that node runs on every message, and n8n's `defineBelow` mapping leaves unmapped columns untouched, which is what preserves a label Sam typed. Watch for n8n auto-adding the new column to that node's mapping with an empty value when the node is reopened — delete the field if it appears. Both writer nodes sit behind three bot_mode gates (`IF Bot Mode Active` → `HITL Check` → `Cek_user_status`), so SAM-labeled rows are never touched by the main flow. Deliverables live in `report/patch/2026-08-19-*` (workflow JSON, panduan, QA script — 67 assertions, 0 fail). Cleanup order is append-copies-then-delete-original-block, deliberately: reversing it risks permanent loss of Sam's student rows. Labeling backlog as of 2026-08-19: 664 STATS rows, 384 OFF — of those, 179 have zero chat trace (safe to auto-label `SAM`) and 205 need Sam's judgment before the first cron run on 2026-10-01. See [[vira-user-identity-principle]].
