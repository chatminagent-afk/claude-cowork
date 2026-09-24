---
name: vira-fakta-konten
description: Fakta VIRA yang sudah terverifikasi & aman dipakai di konten, plus daftar hal sensitif yang tidak boleh muncul
metadata:
  type: project
---

Fakta grounded VIRA (dari export `the scholars\report\production\VIRA V4.json`, dibaca 2026-07-14) — ini yang boleh dipakai di script/post. Menggantikan memory lama `vira-v4-fix-status` (referensi ke nomor episode NIGHT SHIFT sudah dibuang 2026-08-19).

**Angka aman:**
- Bot sengaja delay 5-10 detik biar natural — JANGAN klaim "selalu 5 detik".
- Rate limit 5 pesan/menit (rem anti-spam).
- FAQ 105 entri.
- 164 percakapan aktif / 834 pesan (counter per 7 Jul 2026).
- 5 booking mock interview nyata, 4 confirmed.
- 125 user dalam mode HITL OFF.
- Angka 143 user / 389 balasan = snapshot "minggu-minggu pertama", masih boleh dipakai.
- Sistem sudah versi 4.

**Bug yang sudah difix & aman diceritain:**
- Pesan hilang saat user ngetik kepotong-potong -> debounce 60 dtk + MSG_BUFFER append-only.
- Balasan "maaf terjadi kesalahan" -> filter dipersempit + guard anti-kosong.
- Bot "amnesia" lupa konteks user habis restart -> fakta persisten kelas/program di STATS, TTL 60 hari.
- Salah escalate gara-gara user jawab "boleh" (bot nangkep kata kunci tanpa inget dia barusan nanya apa).
- Bot nebak sendiri produk ambigu -> diubah jadi klarifikasi dulu sebelum jawab.
- Tanggal chat pertama ke-reset tiap pesan; greeting pattern-matching diganti flag.

**Sensitif — jangan pernah tampil/disebut:**
- Kredensial Kirimi plaintext di JSON, pinData webhook (nama + nomor WA user asli), rekening di CONFIG, system prompt penuh, Sheet ID, private key.
- Insiden identitas user tertukar — jangan sebut dengan nama kasusnya.
- Angka biaya/budget operasional dan angka kapasitas/skalabilitas spesifik.
- Demo/screen-record wajib environment mock. Ilustrasi chat = dummy buatan sendiri.
- Nama bank tempat Steven kerja — default pakai "kantor"/"tempat aku kerja" di konten publik (status di reels script 4 masih belum diputuskan).

**Catatan operasional:** workflow cleanup MSG_BUFFER (03:00 WIB) di file export berstatus `active: false` — cek di n8n apakah sudah dinyalakan.
