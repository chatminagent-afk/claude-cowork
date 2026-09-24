---
name: vira-v3-10-nama-usaha-ringkas
description: "VIRA Personal v3.10 (2026-09-18) — nama usaha ditanya di perkenalan + balasan ringkas; UAT 491/0, menunggu deploy"
metadata:
  type: project
---

v3.10 dibangun 2026-09-18 dari export live 16/09 (`workflow/_patch_2026-09-18.py`, UAT `_uat_2026-09-18.py` 491 lolos/0 gagal, panduan `VIRA Steven/docs/2026-09-18-panduan-deploy-v3.10.md`). Status: **belum di-deploy**. Setelah Steven deploy, patch berikutnya berbasis v3.10.

**Why:** uji Steven 17/09 (berperan "Nadia", katering) — nama usaha baru ditanya SESUDAH deck disetujui (by design sejak 14/09: nama_bisnis dikeluarkan dari GALIAN, "ditanya di kalimat tawaran deck"), deck terkirim `tanpa-nama.pdf`; "Salam kenal Nadia" bocor karena perkenalan menanyakan 2 slot sehingga penangkap deterministik tidak jalan; balasan membuka dengan mengulang jawaban prospek.

**Keputusan Steven 2026-09-18:**
- Pesan 1 = nama + nama usaha dalam SATU kalimat; pesan 2 = bidang usaha + cerita singkat; sisanya mundur satu.
- Nama usaha belum dijawab → tanya ulang SEKALI di pesan 2 (bidang mundur ke 3).
- "Apa yang bikin tertarik cari AI CS" dibuang.
- Balasan: target 2 kalimat ±20–35 kata, maks 3; lihat [[feedback-vira-balasan-ringkas]].

**How to apply:** Rakit Konteks menyusun galian SEBELUM jawaban giliran itu tersimpan (Process All) — baris tanya ulang nama usaha karena itu bersyarat ("kalau sudah disebut, jangan ditanyakan"). n8n tidak mengekspor parameter bernilai default (model DeepSeek Summary = default paket `deepseek-v4-flash`), jadi field hilang di export bukan berarti berubah. Harness UAT tidak exit di Windows: jalankan lewat subprocess, bunuh sesudah "UAT MANUAL" tercetak.

Terkait: [[vira-stats-terisi-v3-8]], [[feedback-vira-nama-tidak-menyapa]]
