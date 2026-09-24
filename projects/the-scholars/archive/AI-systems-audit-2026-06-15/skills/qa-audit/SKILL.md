---
name: qa-audit
description: >-
  Run a pre-launch or post-incident QA audit of an automation workflow (n8n VIRA, Power
  Automate flows, Google Apps Script, or a PWA/webform) and produce a prioritized findings
  report. Use when Steven says "QA review", "audit VIRA", "cek dulu sebelum launch",
  "pre-launch audit", "review this workflow/JSON", "apa yang salah di flow ini", "is this
  safe to ship", or hands over a workflow and asks what's wrong or what could break. Output
  is a severity-triaged report (🔴 critical / 🟠 major / 🟡 minor / 🟢 housekeeping) with
  proven root cause, evidence, and a concrete fix per finding — plus a suggested fix order.
  Do NOT use when the task is to actually make the change (use flow-patch), or to build a
  new workflow.
---

# qa-audit — find what will break before it ships

This skill is Steven's recurring "QA review" turned into a repeatable deliverable. The goal is not a vibe check — it's a ranked, evidence-backed list of exactly what's wrong, how bad it is, and how to fix it, so he can decide what to patch before launch. Findings are triaged by severity so the 20% that matters is obvious.

## Operating stance

- **Evidence over opinion.** Every finding names the node/expression and shows why it fails (simulate the logic against a realistic input). Mark **TERBUKTI (proven)** vs **PERLU DATA (needs confirmation)**.
- **Severity-honest.** Don't inflate. 🔴 = data loss / crash / wrong user data / silent failure. 🟠 = degraded behaviour or reliability risk. 🟡 = minor/edge case. 🟢 = housekeeping/style.
- **Actionable.** Each finding ends in a concrete fix, not "consider reviewing". If a fix needs a decision from Steven, say so.
- **Call out what's already good.** Note the parts that are solid (e.g. persona/anti-hallucination) so he's not tempted to "fix" them.

## Inputs to collect first

1. The workflow export (n8n JSON / Power Automate zip / .gs script / HTML) — the artifact under review.
2. What it's supposed to do + the launch context ("going live tomorrow", "V4 pre-launch").
3. Real data or chat transcripts it processes, if reliability/matching bugs are in scope.
4. Any known symptoms already observed.

## Procedure

1. **Understand intended behaviour.** Summarize what the flow is meant to do, node by node in execution order. Confirm with Steven if unsure.
2. **Trace the risky paths.** For each node, ask: what happens on empty input, duplicate/concurrent runs, missing field, rate limits, long waits, mismatched keys, unknown user input? These are where his bugs have historically lived (debounce lost-updates, global rate-limit buckets, row-matching by wrong key, HITL/bot-mode not re-checking after a wait, unstamped timestamps).
3. **Prove each finding.** Simulate the suspect logic against a realistic input and show the bad output. Assign severity.
4. **Check data hygiene & security.** Look at the sheet/DB the flow reads/writes: duplicate rows, wrong-key matching, leaked fields, whitelist/test numbers still active in production.
5. **Note the strengths.** One short section on what's working well.
6. **Recommend a fix order.** A short ordered list: fix 🔴 first, then 🟠, grouped so related fixes ship together. This becomes the input to `flow-patch`.

## Report format

```
# QA Menyeluruh — <artifact name>

## RINGKASAN PRIORITAS
<table: # | severity | finding | 1-line impact>

## DETAIL TEMUAN
### 1. 🔴 <node> — <title>   [TERBUKTI]
Root cause: ...
Bukti (simulasi): ...
Solusi: ...
### 2. 🟠 ...
...

## SUDAH BAIK
<what to leave alone>

## QA DATABASE / DATA HYGIENE
<duplicate rows, matching keys, leaked/whitelist data>

## URUTAN PERBAIKAN YANG DISARANKAN
1. ... 2. ... 3. ...
```

Save the report dated `YYYY-MM-DD-QA-<name>.md`. Keep it read-only advice — this skill does not change the flow; hand the fix order to `flow-patch`.

## Before delivering — check

1. Is every 🔴/🟠 proven with a simulated example (or clearly flagged as needing data)?
2. Are severities honest (nothing inflated, nothing buried)?
3. Does each finding end in a concrete fix?
4. Is there a fix order Steven can act on immediately?
5. Did you name what's already good so it stays untouched?
