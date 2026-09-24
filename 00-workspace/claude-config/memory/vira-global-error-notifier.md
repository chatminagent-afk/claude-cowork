---
name: vira-global-error-notifier
description: GLOBAL - VIRA WA Error Notifier terbukti jalan 21 Sep 2026; ID n8n asli + host, dan kenapa sebelumnya nol eksekusi
metadata:
  type: project
---

**GLOBAL - VIRA WA Error Notifier** — ID n8n asli `0mp_AdLtInm68RxQUwLqV`
(tidak ada di file ekspor manapun; file lokal `live production\2026-08-28-GLOBAL-VIRA-Error-Notifier.json`
tanpa root `id` dan `name`-nya tanpa kata "WA"). Host n8n: `https://n8n.srv1270416.hstgr.cloud/`.
`availableInMCP: false`, jadi MCP n8n selalu balas "Workflow not found" untuk ID ini — bukan error auth.

Diverifikasi end-to-end 2026-09-21: cabang TS + PCR lewat pinned data (device D-4ZV1F dan
D-LM6WE dua-duanya mengirim), lalu eksekusi produksi lewat webhook (execution 64274).
"Save failed production executions" menyala — `execution.id` dan `execution.url` terisi.

**Penyebab nol eksekusi selama ini: tidak ada satu pun workflow yang menunjuk ke dia.**
Tahap 1 panduan migrasi 2026-08-28 (arahkan satelit dulu) tidak pernah dijalankan.
`active: false` bukan penyebab — error workflow memang tidak perlu di-publish.

Harness tes: **ZZ - Dummy Error Test** `1CQI3CPhz_1FSlfhtpEbB`, webhook GET `/webhook/dummy-error`.
Simpan non-aktif, pakai ulang tiap habis ubah wiring.

**Why:** dua kali hampir salah simpul — dikira mati karena inactive, lalu dikira mati karena
tombol "Execute workflow" tidak menghasilkan apa-apa.

**How to apply:** error workflow TIDAK bisa diuji lewat eksekusi manual maupun `/webhook-test/`
(dokumentasi n8n: *"You can't test error workflows when running workflows manually"*) — harus
eksekusi produksi. Patch `Compose Notif` lewat UI n8n, JANGAN re-import JSON-nya: file itu tanpa
root `id`, import bikin workflow baru dan semua pointer `errorWorkflow` jadi menunjuk yang lama.
Terkait [[vira-personal-main-tidak-terbaca-mcp]].
