---
name: feedback-deck-field-kosong
description: "Deck VIRA: nama_bisnis/industri/masalah_utama kosong = berhenti & butuh izin Steven per field; field lain cukup peringatan; usulan isi hanya dari fakta tertulis + disetujui"
metadata:
  type: feedback
---

Build deck (`VIRA Steven/deck/buat_deck.py`, skill `deck-request`) **berhenti** kalau `nama_bisnis`, `industri`, atau `masalah_utama` kosong. Lanjut hanya dengan izin eksplisit Steven per field di percakapan itu → `--lanjut-tanpa <field>`; `kirim_deck.py` ke klien memakai gerbang yang sama. Lima penentu slide lain (`deskripsi_bisnis`, `aksi_utama`, `volume_chat_harian`, `pertanyaan_tersering`, `alur_setelah_chat`) hanya PERINGATAN.

Claude **boleh mengusulkan** isi field yang kosong, hanya dari fakta yang sudah tertulis (kolom lain REQUESTS, `kutipan_asli`, STATS, nama akun WA sebagai kandidat) dengan sumbernya; ditulis ke REQUESTS hanya setelah Steven setuju.

**Why:** Steven 2026-09-18 setelah deck uji 17/09 terkirim sebagai `tanpa-nama.pdf` tanpa ada yang menghentikan. Keputusan ini menggantikan 2026-09-06 ("cover generik masih layak kirim"). Steven memilih hanya 3 field yang memblokir (bukan 8).

**How to apply:** tabel tunggal `KELENGKAPAN` di `buat_deck.py`; uji di `uji_konsistensi.py` bagian [7] (87/0). Backup versi lama: `VIRA Steven/arsip/2026-09-18-deck-sebelum-gerbang/`. Skill ada dua salinan identik (`VIRA/skills/deck-request` & `~/.claude/skills/deck-request`) — ubah keduanya.

Terkait: [[vira-v3-10-nama-usaha-ringkas]]
