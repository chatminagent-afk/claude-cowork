---
name: miva-ads-funnel-eval-2026-09-26
description: "Evaluasi chat leads ads CTWA MIVA Personal per 26/09 — ~39 lead, 2 deck, titik bocor utama & bug yang ditemukan di chat live"
metadata:
  node_type: memory
  type: project
  originSessionId: 482a6106-463b-4e81-bf4b-8d74b6e30a77
  modified: 2026-09-26T17:12:07.715Z
---

Dibaca langsung dari WhatsApp Business Desktop, 2026-09-26 (~39 chat lead dari iklan IG/FB, sekitar 22–26/09).

Funnel: 38 lead asli → 19 balas opener (19 diam setelah opener pertama) → ~12 sebut usaha → 1 deck (Ziel Rental 857-5556-9330). Sidon/beautysemarang 851-7170-1168 = nomor uji Steven, abaikan.

Temuan utama:
- Opener minta nama + nama usaha sebelum kasih nilai apa pun → ~50% diam. Ada yang bingung ("Apaan?").
- Discovery kepanjangan (4–6 pertanyaan berurutan) → drop di pertanyaan ke-3/4 (Nika textile, Indah salon, Andi catering, Riza travel, Aqma).
- Bug: industri sudah disebut (Umroh, kecantikan, kosmetik) tapi MIVA tanya "bergerak di bidang apa?" lagi → lead kesal (822-2822-2354).
- Permintaan langsung diabaikan: "minta ratecard", "produknya apa aja", "Brp" dianggap nama (bug v3.14 belum deploy), "kapan ngomong sama Steven".
- Lead hangat tidak ditutup ke deck (Ary/Mas Adi 895-3416-88018 → MIVA bilang "silakan kabari").
- Notif ke Steven sejak 21/09 untuk lead asli hanya 2 (brief Ziel, 811-665-998): "itu bagian Steven, mau aku sambungkan?" tidak pernah menotifikasi. Diperbaiki di [[miva-v3-15-tawaran-deck]].
- Latensi: 1 kasus balasan telat 8 jam (878-0207-8000), 1 kasus 3 jam.
- Disappearing messages bikin MIVA tidak bisa baca pesan (811-665-998).
- Targeting: bukan pemilik usaha, reseller/builder AI, volume chat kecil (5/hari).

Terkait: [[miva-v3-14-brp]], [[miva-v3-13-harga-handover]], [[feedback-miva-balasan-ringkas]]
