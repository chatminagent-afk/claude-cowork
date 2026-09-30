---
name: kuota-google-sheets-lintas-klien
description: "Semua workflow VIRA (Steven, The Scholars, Persada) berbagi jatah kuota Google Sheets 60 read/menit yang sama"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2243cf77-d506-4f16-90e8-8485d8a07c59
  modified: 2026-08-16T03:39:00.579Z
---

Kuota Google Sheets API adalah **60 read/menit dan 60 write/menit per user per project**
(bukan per workflow, bukan per spreadsheet). Selama VIRA Steven, The Scholars, dan Persada
memakai akun Google / kredensial OAuth yang sama, ketiganya berebut jatah 60 yang sama —
inilah penyebab "max hit google service 60 detik" yang dialami Steven di The Scholars dan
Persada (dilaporkan 2026-08-16).

Perhitungan biaya per pesan yang perlu diingat: node n8n `appendOrUpdate` dan `update`
masing-masing memakai **2 unit kuota** (1 read untuk mencari baris + 1 write), bukan 1.
VIRA Steven sebelum dioptimasi: 14 read + 5 write per pesan ≈ 4 pesan/menit sampai mentok.

**Why:** batasnya per akun, jadi menghitung beban satu workflow saja selalu menghasilkan
angka yang terlalu optimis; masalahnya baru muncul saat klien lain sedang ramai.

**How to apply:** saat menghitung kapasitas atau mendiagnosis error 429/quota di workflow
VIRA mana pun, jumlahkan beban SEMUA klien yang memakai kredensial Google yang sama, bukan
cuma workflow yang sedang dilihat. Perbaikan struktural paling murah: service account
terpisah per klien (tiap-tiap dapat 60/menit sendiri, tanpa mengubah kode). Detail
optimasi VIRA Steven ada di `VIRA Steven/workflow/2026-08-16-catatan-build-workflow.md`.
