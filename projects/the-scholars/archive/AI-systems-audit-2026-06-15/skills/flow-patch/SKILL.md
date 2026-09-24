---
name: flow-patch
description: >-
  Surgically patch an exported automation flow — n8n workflow JSON or a Power Automate
  flow .zip (definition.json / manifest.json) — without collateral damage. Use this
  whenever Steven wants to fix a bug, add a node, tweak a prompt, or change behaviour in
  VIRA (the n8n WhatsApp bot) or a Power Automate report flow (e.g. "Weekly Reminder Ci
  Lenny – UAT Status", MBI weekly projects report, GS reminders). Trigger on: "fix VIRA",
  "patch the flow", "update the workflow", "bikin V-berikutnya", "add a node", "ubah
  prompt", "bump version", "re-zip flow", or when he hands over a workflow JSON/zip and
  describes a change. Enforces minimal diffs, versioning + changelog + handoff, simulation
  against real data, and approval before shipping. Do NOT use for building a brand-new
  workflow from scratch, or for pure QA with no code change (use qa-audit for that).
---

# flow-patch — change automation flows surgically, ship with a paper trail

This skill turns Steven's most-repeated engineering task into a repeatable procedure: take a live automation flow, change exactly what's needed, prove it's safe, and hand it over so it can be imported and rolled back. It applies equally to **n8n** (VIRA) and **Power Automate** (weekly report flows). The prime directive: **change the minimum, break nothing, leave a trail.**

## Operating stance

- **Root cause before edit.** Never patch a symptom. Find the node/expression actually responsible and say how you know. If you can't prove it, say so and ask for the log/data you need.
- **Smallest possible diff.** Touch only the nodes/expressions that must change. Everything else stays byte-identical. A good patch reads as "4 changes, here they are" — not a rewrite.
- **Approval gate.** Present the planned change list and wait for Steven's "go" before writing the shipped file. (His standing rule: outline plan, confirm before overwriting.)
- **Reversible by design.** Every ship is a new version with a changelog and handoff, so the previous version is always intact to roll back to.

## Inputs to collect first

1. **The flow export** — n8n `.json`, or Power Automate `.zip` (contains `definition.json` + `manifest.json`).
2. **The change request** — the bug or feature, in Steven's words.
3. **Evidence** — execution log, error message, or a chat/data example that reproduces it. If missing and the cause is ambiguous, ask before guessing.
4. **Real data to simulate against** — the actual Excel/Sheet/DB rows or a real chat transcript the flow processes.
5. **Current version number** — to bump correctly (e.g. V4.8 → V4.9; V3.4 → V3.5).

## Procedure

### 1. Map the flow
Unzip if Power Automate (`unzip flow.zip`). Parse the JSON. List the nodes/actions in execution order and identify the one(s) in the change's path. State the current live behaviour in one paragraph so Steven can confirm you understand it.

### 2. Locate root cause (for bug fixes)
Quote the exact node name and the expression/setting responsible. Back it with evidence: simulate the original logic against the failing input and show it produces the observed bad output. Mark each finding **TERBUKTI (proven)** or **HIPOTESIS (needs data)**. Don't propose a fix for an unproven cause — ask for the missing log/row instead.

### 3. Draft the change list (STOP for approval)
Write a numbered **Daftar Perubahan** — for each: node/action touched, exact before → after, and why. Group into packages if there are several. Then **stop and ask for approval.** Do not write the shipped file yet.

### 4. Apply the patch
Edit only the identified spots. Preserve everything else exactly (key order, whitespace, unrelated nodes). For Power Automate, bump the version string in **both** `definition.json` and `manifest.json` displayName (e.g. `... V4.9`). For n8n, bump the version in the filename and any in-workflow version marker.

### 5. Simulate against real data
Re-run the changed logic mentally or in a scratch script against the actual rows/chat provided. Show the concrete output (the card text, the reply, the sheet write). This is non-negotiable — Steven always checks output against real data before shipping.

### 6. Verify a minimal diff
Diff shipped vs previous version. Confirm the only changes are the intended ones ("byte-identical except the N points above"). Validate JSON parses. For Power Automate, make sure the zip repacks cleanly (no 0-byte artifacts — delete any failed zip).

### 7. Ship with a trail
Produce, dated `YYYY-MM-DD-...`:
- The new versioned file (`VIRA_V3.5.json` or `WeeklyMBIProjectsReportV.4.9_<timestamp>.zip`).
- A **changelog** (`...-VX-changelog.md`): what changed, why, and the diff summary.
- A **handoff** (`...-VX-handoff.md`): how to import, how to test, how to roll back.
Keep dev patches and production files in separate folders if that's the existing layout (`report/patch` vs `report/production`).

## Output checklist (before handing over)

1. Root cause proven with evidence (or explicitly flagged as hypothesis + data needed)?
2. Change list approved by Steven before the shipped file was written?
3. Diff is minimal — only the intended nodes changed, rest byte-identical?
4. Output simulated against **real** data and shown?
5. JSON valid / zip repacks with no 0-byte file?
6. New version + changelog + handoff created, dated, previous version intact for rollback?

If any is "no", fix it before delivering. End by listing every file created or modified with its location.
