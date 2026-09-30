---
name: vira-followup-belum-live
description: "Follow-up VIRA Personal belum pernah di-import ke n8n; workflow \"Follow-up AI Powered\" yang ada di n8n itu milik tenant PCR, bukan Personal"
metadata: 
  node_type: memory
  type: project
  originSessionId: fe4f527d-ca8a-4c2d-9d4e-5f1e9cc512fa
  modified: 2026-09-07T09:10:04.835Z
---

Per 2026-09-07, workflow follow-up untuk VIRA Personal **belum pernah di-import ke n8n**.
Filenya cuma ada lokal di `VIRA Steven/workflow/2026-08-28-VIRA-Personal-Followup.json`
(sengaja `active: false` + trigger disabled sebagai pengaman import).

**Jebakan nama:** di n8n ADA workflow aktif bernama "Follow-up AI Powered"
(id `qaux8b14IgvxEXfoUtxa2`). Itu **bukan** milik VIRA Personal — itu tenant PCR
(Persada Cisoka Residence). Bedanya terlihat dari Google Sheets documentId yang
berbeda dan prompt-nya yang berbunyi "Kamu Vira, asisten Persada Cisoka Residence".
Jangan simpulkan follow-up Personal sudah jalan hanya karena melihat nama itu di
daftar workflow.

Kode follow-up lokalnya sendiri sudah cocok dengan skema STATS & CONFIG sekarang —
tidak perlu di-patch, cuma perlu langkah go-live (import, isi `followup_templates`,
uji manual, baru set `followup_enabled` ke `"true"`).

**Why:** dua kali investigasi bisa terbuang hanya untuk menemukan ulang bahwa nama
yang mirip itu milik tenant lain.

**How to apply:** kalau ditanya "follow-up VIRA jalan nggak?", jawab belum, dan cek
`followup_enabled` di CONFIG (saat ini `false`) sebelum menyimpulkan apa pun.

Terkait: [[vira-dua-tenant]]
