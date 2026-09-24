# VIRA — The Scholars WhatsApp AI assistant

**Client:** The Scholars (TheScholars.id) — education consultancy, Singapore scholarships. Contact: Sam.
**Stack:** n8n (production/VIRA.json), Google Sheets (STATS + FAQ/PROGRAM/ABOUT/LINKS tabs), Kirimi WA gateway, AI Agent node with Simple Memory.
**Persona:** "Sam versi AI" — intro verbatim from client for new users.
**Status (2026-07-04):** Final execution plan (Paket 1–6) awaiting Steven's approval. Live in public mode (whitelist disabled).

## Key design principles
- User identity: No WA primary, lid backup only when No WA empty; never fallback rows[0]
- Wait3 debounce = 60s (intentional)
- Register netral: no vocatives, no parent/student status flow (removed per client request)
- Simple Memory resets on every workflow save/deploy — persistent columns (kelas_anak, program_interest) are the mitigation

## Open items
- Approve Paket 1–6 (see 2026-07-02-rencana-eksekusi-VIRA-final.md)
- Check n8n executions 28/6 10:27:50–10:28:05 WIB → distinguishes Sheets 429 vs Kirimi webhook miss for Adrian's lost message
- Build Error Workflow (Error Trigger → WA admin notif)
- Sheets API 429 mitigation only if proven (don't over-engineer)

## Files
- the scholars/2026-07-02-rencana-eksekusi-VIRA-final.md — current plan
- the scholars/2026-07-02-analisa-bug-VIRA-report-1-juli.md — bug analysis
- the scholars/archive/ — QA docs, architecture analyses, onboarding notes, invoices (INV001, INV002)
