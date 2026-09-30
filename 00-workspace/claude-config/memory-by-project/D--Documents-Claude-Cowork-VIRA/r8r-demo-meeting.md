---
name: r8r-demo-meeting
description: Meeting jadwal 2026-08-25 (Selasa) dengan Sam (The Scholars) dan founder r8r untuk demo r8r sebagai calon pengganti n8n di VIRA
metadata: 
  node_type: memory
  type: project
  originSessionId: 0d282c7f-3533-4cbe-a886-f9fdc6f5263e
  modified: 2026-08-21T16:34:46.598Z
---

Meeting dijadwalkan Selasa, 2026-08-25, antara Steven, Sam (The Scholars), dan founder r8r (qhkm) — agenda demo r8r sebagai calon pengganti n8n untuk workflow VIRA.

**Why:** Steven sedang eksplorasi apakah VIRA (saat ini n8n + Google Sheets + Kirimi webhook + AI Agent) bisa/perlu migrasi ke r8r (workflow engine baru berbasis Rust, agent-native, klaim jauh lebih ringan resource & punya MCP built-in). Riset awal (2026-08-21) menemukan red flag serius: repo GitHub resmi mereka (github.com/qhkm/r8r) return 404 — tidak bisa diverifikasi publik, padahal situs mengklaim "open source". Lihat juga [[vira-dua-tenant]] dan [[vira-fakta-konten]] untuk konteks VIRA lainnya.

**How to apply:** Sebelum mendukung keputusan migrasi apa pun, prioritaskan verifikasi berikut saat/setelah meeting:
1. Klarifikasi kenapa repo 404 dan minta akses source code langsung
2. Cek dukungan integrasi Google Sheets & webhook WhatsApp-style (Kirimi) — bukan cuma demo generic
3. Tanya biaya commercial license (AGPL-3.0 punya implikasi network-use clause untuk layanan komersial seperti VIRA)
4. Jangan setuju migrasi produksi di meeting — VIRA masih dalam siklus bugfix aktif, butuh testing paralel & rencana rollback dulu
5. Jangan share data sensitif VIRA/The Scholars ke pihak ketiga tanpa persetujuan eksplisit Sam
