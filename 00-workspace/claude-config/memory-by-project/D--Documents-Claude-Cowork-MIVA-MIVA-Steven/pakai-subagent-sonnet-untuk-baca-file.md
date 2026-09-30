---
name: pakai-subagent-sonnet-untuk-baca-file
description: "Steven minta pembacaan file besar (workflow JSON, xlsx, docs) selalu didelegasikan ke subagent Sonnet, bukan dibaca langsung"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 226a5d21-ea40-40ff-b33c-3d5aecf14bc0
  modified: 2026-08-16T17:29:00.848Z
---

Steven berkali-kali menegaskan: **"ingat selalu gunakan subagent sonnet untuk membaca file
yang dibutuhkan."** Berlaku untuk file besar proyek VIRA — export workflow n8n (±270 KB
JSON), `VIRA Database.xlsx`, dan dokumen catatan/checklist.

**Why:** file-file ini besar dan sering perlu dibaca utuh (bukan skim), sementara konteks
percakapan utama perlu disisakan untuk analisis dan keputusan. Menyerap 270 KB JSON langsung
ke percakapan utama membuat sesi cepat penuh dan memaksa ringkasan konteks di tengah kerja.

**How to apply:** untuk tiap sesi VIRA, jalankan beberapa subagent Sonnet paralel dalam satu
panggilan — misalnya satu untuk audit workflow JSON, satu untuk isi spreadsheet, satu untuk
dokumen markdown. Beri tiap subagent pertanyaan spesifik dan minta **kutipan mentah**
(expression/JS/JSON apa adanya, nama node, nama kolom persis), bukan ringkasan — kesimpulan
tanpa kutipan sering meleset. Subagent yang sama bisa dilanjutkan lewat `SendMessage` untuk
pertanyaan susulan, jadi tidak perlu membaca ulang file dari nol.
