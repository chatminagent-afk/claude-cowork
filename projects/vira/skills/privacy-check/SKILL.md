---
name: privacy-check
description: Privacy guardrail review for any VIRA / @povstevens content before publishing — reel scripts, captions, screenshots, screen recordings, stories, or lead magnets. Use whenever Steven is about to post or publish content, asks "aman nggak", "cek privasi", "review sebelum post", "boleh di-post?", or shares a draft/footage plan that involves VIRA, client material, or The Scholars — even if he doesn't explicitly ask for a privacy check. Also run this as the final gate after generating any reel script.
---

# Privacy Check — Konten VIRA / @povstevens

Gate wajib sebelum konten apapun yang menyentuh materi VIRA dipublikasikan. Konteksnya: VIRA adalah bot production dengan user asli (orang tua & siswa klien), kredensialnya masih plaintext di file workflow, dan sebagian bug-nya belum dipatch — satu screenshot ceroboh bisa membocorkan data user, membuka peta serangan, atau merusak kepercayaan Sam (klien). Review-nya harus teliti, bukan formalitas.

## Cara review

1. Baca seluruh konten yang mau dipost: script, caption, deskripsi visual/footage, on-screen text, hashtag — pelanggaran sering sembunyi di kolom Visual ("screen-record chat asli…"), bukan di VO.
2. Periksa terhadap semua aturan di bawah. Untuk klaim "bug sudah difix", jangan percaya begitu saja — verifikasi (lihat aturan 3).
3. Laporkan temuan dalam tabel:

| # | Temuan (kutip bagiannya) | Aturan yang kena | Status | Perbaikan konkret |
|---|---|---|---|---|

Status: 🔴 **BLOKIR** (jangan post sebelum dibereskan) · 🟡 **REVISI** (boleh post setelah diubah sesuai saran) · 🟢 **AMAN**.

4. Tutup dengan verdict satu baris: **SIAP POST** / **SIAP POST SETELAH REVISI** / **JANGAN POST DULU** + alasan terpendek.

Kalau tidak ada temuan sama sekali, tetap tunjukkan aturan apa saja yang dicek — supaya Steven tahu review-nya benar-benar jalan, bukan dilewati.

## Aturan keras — pelanggaran = 🔴 BLOKIR

1. **Identitas user asli.** Nama atau nomor WA user VIRA (Adrian, Vivipoh, dkk.), isi chat pribadi orang tua/siswa, screenshot DM asli calon klien. *Kenapa:* mereka user bisnis klien, bukan aset konten Steven — bocor sekali, kepercayaan Sam dan klien berikutnya hilang. *Fix:* ganti dengan bot demo "A Course" + data dummy, atau ilustrasi/teks animasi buatan sendiri.
2. **Kredensial & ID sistem.** Kirimi `user_code`/`secret`/`device_id` (masih plaintext di file workflow!), Google Sheet ID/URL, webhook URL, nomor rekening di contoh invoice, node credentials di layar n8n. *Kenapa:* ini akses langsung ke sistem production. *Fix:* pakai layar mock/demo; jangan tampilkan address bar; crop.
3. **Bug yang belum dipatch.** Jangan ceritakan bug yang fixnya belum live di production (contoh yang diketahui belum: webhook tanpa auth, validasi API Kirimi). *Kenapa:* itu peta serangan yang dipublikasikan. Cerita debugging hanya untuk bug yang **sudah** difix dan deploy-nya terkonfirmasi. Kalau statusnya tidak disebut atau meragukan → tanya Steven "fixnya sudah live di production?" dan tahan konten sampai terjawab. Khusus reel 4/7/11 dari batch Juli 2026: ceritanya ditulis "sudah difix" padahal per analisa 2 Juli masih menunggu approval — selalu cek status ini.
4. **System prompt lengkap VIRA.** *Kenapa:* bisa ditiru kompetitor — itu bagian dari nilai jual. Cuplikan 1–2 baris yang sudah digeneralisir masih boleh (🟡 nilai kasus per kasus).
5. **Nama "The Scholars" / "Sam" tanpa izin tertulis Sam.** Default: anonimkan jadi "klien-ku, sebuah konsultan pendidikan". Nama produk **"VIRA"** sendiri aman disebut bebas. Kalau Steven bilang izin sudah ada, minta konfirmasi bentuk izinnya (chat/tertulis) sekali, lalu loloskan.

## Aturan produksi — pelanggaran = 🟡 REVISI

- Demo dan screen-record harus pakai bot demo **"A Course"** + Google Sheets dummy — bukan environment production, meskipun "cuma sebentar".
- Screenshot chat/dashboard: blur nomor, nama lengkap, dan ID — ikuti pola blur yang sudah dipakai di VIRA.pdf.
- Status bar HP: crop/potong kalau ada notifikasi masuk atau nomor asli Steven terlihat.
- Layar n8n di footage harus mock/demo — konfigurasi node dan daftar workflow production jangan terlihat.

## Yang sudah dipastikan AMAN (jangan false-positive)

- Nama produk **"VIRA"** dan cerita konsepnya.
- Cerita bug yang **sudah difix & live**, diceritakan dengan bahasa awam.
- Angka agregat tanpa identitas (mis. "143 user", "ratusan chat terjawab").
- Nomor WA business Steven **085155202354** — memang sengaja dipublikasikan di konten.
- Menyebut tools generik: n8n, Google Sheets, WhatsApp (tanpa detail konfigurasi).

## Referensi

Detail guardrail asli: `D:\Documents\Claude Cowork\VIRA\2026-07-13-content-plan-povstevens.md` §8, dan blocker produksi di `D:\Documents\Claude Cowork\VIRA\konten\2026-07-13-reels-index.md`. Baca kalau butuh konteks lebih; aturan di atas sudah mencakup semuanya.
