---
name: vira-stats-terisi-v3-8
description: "VIRA Personal v3.8→v3.9 — kolom fakta STATS diisi deterministik + tanya nama di perkenalan; v3.9 live per export 2026-09-16"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4bc2ec08-26b2-4f86-8466-f971e8e4889e
  modified: 2026-09-15T07:30:04.559Z
---

VIRA Personal Main v3.8 dibangun 2026-09-14 (`workflow/_patch_2026-09-14.py`, UAT `_uat_2026-09-14.py` 371 lolos/0 gagal). v3.7, yang memakai kolom `nama_ditanya`, **dibatalkan** dan berkasnya dipindah ke Recycle Bin.

**Why:** audit sheet live 2026-09-14 menemukan kolom fakta STATS (nama_lengkap, nama_bisnis, industri, masalah_utama, volume_chat, budget_range, minat_paket, bahasa, brief_terisi) kosong 100% di 5 percakapan nyata. Sebabnya: fakta hanya masuk lewat tag `[FACTS]` yang tidak ditulis model, bahasa hanya diisi dari blok deck, dan nama tidak pernah ditanyakan. Akibatnya REQUESTS kosong walau deck_requested=Y.

**Keputusan Steven:** tidak ada kolom baru. Nama ditanya SEKALI di perkenalan dan disimpan ke nama_lengkap. budget_range & minat_paket TIDAK ditanyakan, hanya dicatat kalau prospek menyebut sendiri.

**How to apply:** isi v3.8:
- Process All menangkap jawaban atas pertanyaan VIRA dari `last_bot_reply`, lewat detektor `slotDitanya`.
- Blok `[DECK_REQUEST]` ikut mengisi STATS; bahasa dideteksi dari kata fungsi.
- Rakit Konteks memberi `galian_berikutnya` (industri giliran 2–4 → masalah 2–6 → volume 3–8), memakai `Counter` dan jeda satu balasan.
- Detektornya identik di dua node.

**Update 2026-09-15:** v3.8 sudah live. Insiden 14:11 memunculkan tiga cacat: VIRA memanggil nama, nama tersimpan "Dengan Aldi", dan pertanyaan prospek tidak dijawab karena galian didahulukan. Semuanya diperbaiki di **v3.9** (`_patch_2026-09-15.py`, UAT 402/0):
- nama dihapus dari balasan
- awalan "dengan/sama/ini" dibuang dari nama
- galian ditunda saat prospek bertanya; jendela industri 2–5, masalah 2–7, volume 3–9

Patch berikutnya harus berbasis **v3.9** — sudah dilanjutkan jadi v3.10 (2026-09-18), lihat [[vira-v3-10-nama-usaha-ringkas]]. Status v3.9: **sudah live** — export n8n 2026-09-16 (`workflow/VIRA Personal — Main.json`) identik fungsional dengan v3.9 (cek 2026-09-18; beda cuma field `model` DeepSeek Summary & urutan kolom Log EVENTS). Lihat [[feedback-vira-nama-tidak-menyapa]]. Masih terbuka: Follow-up memakai nama akun WA untuk `{nama}`. Panduan: `VIRA Steven/docs/2026-09-14-panduan-deploy-v3.8.md`.

Terkait: [[vira-personal-main-tidak-terbaca-mcp]], [[vira-followup-belum-live]]
