---
name: vira-personal-main-tidak-terbaca-mcp
description: "n8n MCP tidak bisa membaca workflow \"VIRA Personal — Main\" (availableInMCP=false); harness UAT butuh PYTHONIOENCODING=utf-8, bukan hang"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bb57da45-1acc-4523-a82c-c287bd097fa8
  modified: 2026-09-22T06:13:35.049Z
---

- Workflow **VIRA Personal — Main** (id lokal `AC65HeFegHFCFc5aY609u`) diekspor dengan `settings.availableInMCP: false`. Akibatnya n8n MCP (`search_workflows` / `get_workflow_details`) tidak bisa melihatnya: "Workflow not found". Yang terlihat cuma 11 workflow lain, termasuk "VIRA TS" milik tenant The Scholars, jadi JANGAN tertukar. Untuk tahu kondisi live, minta Steven download JSON-nya, atau pakai bukti dari sheet "VIRA Steven Database" (`1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk`, dibaca lewat `VIRA Steven/deck/vira_sheet.py`).
- Harness `workflow/_uat_*.py` (py_mini_racer) **tidak hang** — itu salah baca. Yang terjadi: stdout Windows default cp1252, lalu `cek()` mencetak judul yang memuat emoji → `UnicodeEncodeError` dan prosesnya mati di tengah. Jalankan dengan `PYTHONIOENCODING=utf-8 python _uat_*.py > file.log 2>&1` dan prosesnya selesai normal dengan exit code 0 (0 = semua lolos, 1 = ada yang gagal). Butuh 3–8 menit untuk ~550 skenario, jadi jalankan di background, jangan pakai timeout pendek.

Terkait: [[vira-stats-terisi-v3-8]], [[vira-v3-11-deck-terkirim]]

**Update 2026-09-23:** Steven menyalakan "Available in MCP" untuk Main & Follow-up — `get_workflow_details` sekarang bisa membaca live (respons besar disimpan ke file; baca lewat subagent/Python, jangan ke konteks utama). File v3.12 membawa `availableInMCP: true`.

**Update 2026-09-23 (sesudah deploy v3.12):** ID Main tetap `AC65HeFegHFCFc5aY609u` (tidak di-import ulang). Sheet "VIRA Steven Database" juga bisa dibaca lewat Google Drive connector `read_file_content` (semua tab, termasuk STATS/EVENTS/MSG_BUFFER).
