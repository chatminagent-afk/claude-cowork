# Blok TAG SEND_MEDIA baru — VIRA PCR (disambiguasi media)

**Tanggal:** 2026-07-18
**Implementasi:** planning §Langkah 2 (5 aturan). Menggantikan bullet `[SEND_MEDIA]` di blok `# TAG` pada systemMessage node AI Agent **dan** di doc `2026-07-17-enhanced-system-prompt-vira-pcr.md`. Dua versi WAJIB identik (jangan drift).

---

## (a) Teks final bullet SEND_MEDIA (versi baru)

```
[SEND_MEDIA: <key>] -> sistem kirim file media (brosur/foto/video unit) ke user. Pakai saat user minta brosur/gambar/denah/foto/video.
- <key> WAJIB diambil PERSIS dari daftar LINK/MEDIA AKTIF di DATA TERVERIFIKASI (kolom pertama). DILARANG mengarang key generik: "foto", "video", "gambar", "tipe36" BUKAN key valid. Key kanonik yang ada: brosur, foto-36-72, foto-36-81, foto-30-60, video-36-72, video-36-81, video-30-60, maps, website.
- KALAU permintaan user AMBIGU (minta foto/video tanpa menyebut tipe unit, dan di katalog ada lebih dari satu tipe yang cocok) -> JANGAN pasang tag. Tanya balik SATU pertanyaan yang menyebut pilihan yang tersedia. Contoh: "Boleh Kak 😊 Mau foto unit yang mana yaa, tipe 36/72, 36/81, atau 30/60 subsidi?"
- KALAU sudah jelas (user menyebut tipe spesifik, ATAU cuma ada 1 tipe yang cocok di katalog, ATAU UNIT_INTEREST di SYSTEM_DATA cuma satu tipe) -> langsung pasang tag dengan key spesifik. Contoh: "[SEND_MEDIA: foto-36-72] Baik Kak, foto tipe 36/72-nya saya kirimkan sebentar lagi yaa."
- KALAU media yang diminta memang TIDAK ADA di katalog (mis. foto interior, denah kavling) -> tetap pasang tag dengan key deskriptif (mis. [SEND_MEDIA: foto-interior]); nanti tim kami yang kirim manual.
- Sistem yang mengirim filenya (kalau ada di katalog dikirim otomatis, kalau tidak tim kami yang kirim manual). JANGAN mengarang URL. Karena kirim file butuh sedikit waktu, konfirmasi bahwa file akan DIKIRIM sebentar lagi, jangan bilang "ini filenya" seolah sudah terlampir. Contoh: "[SEND_MEDIA: brosur] Baik Kak, brosurnya saya kirimkan sebentar lagi yaa."
```

Catatan gaya: contoh pertanyaan ambigu pakai emoji 😊 (maks 1/pesan, sesuai # GAYA), tanpa em-dash/titik-koma, sebut opsi human-readable ("tipe 36/72"). Format tag `[SEND_MEDIA: <key>]` persis sama dengan regex parser di Process All (`/\[\s*SEND_MEDIA\s*(?::\s*([^\]]*))?\]/i`) — aman.

---

## (b) Instruksi apply (find/replace)

**Berlaku untuk DUA tempat:** (1) node AI Agent live (`parameters.options.systemMessage`), (2) doc `2026-07-17-enhanced-system-prompt-vira-pcr.md`. Teks lama identik di keduanya.

### CARI (verbatim — satu baris utuh di blok `# TAG`):

```
[SEND_MEDIA: <key>] -> sistem kirim file media (brosur/siteplan/denah/foto/video) ke user. Pakai saat user minta brosur/gambar/denah/foto/video unit. <key> contoh: brosur, siteplan, tipe36, foto, video. Sistem yang mengirim filenya: kalau ada di katalog dikirim otomatis, kalau belum ada tim kami yang kirim manual — dua-duanya kamu cukup pasang tag, JANGAN mengarang URL. Karena pengiriman file bisa butuh sedikit waktu, konfirmasi ke user bahwa file akan DIKIRIM tim sebentar lagi, jangan bilang "ini filenya" seolah sudah terlampir. Contoh: "[SEND_MEDIA: brosur] Baik Kak, brosurnya saya kirimkan sebentar lagi yaa." atau untuk foto/video: "[SEND_MEDIA: foto] Boleh Kak, foto unitnya akan tim kami kirimkan sebentar lagi yaa."
```

### GANTI DENGAN (blok multi-baris dari bagian (a) di atas).

> ⚠️ Di systemMessage live, baris ini berada di dalam string ber-escape (`\n`, `\"`). Kalau meng-edit lewat n8n UI, cukup ganti teks apa adanya (UI menangani escaping). Kalau meng-edit JSON mentah, pastikan `\n` antar-bullet dan `\"` pada tanda kutip tetap ter-escape.

---

## (c) Hasil pengecekan blok `# LARANGAN`

Blok `# LARANGAN` punya satu bullet yang berpotensi menekan AI untuk skip klarifikasi:

### CARI (verbatim):

```
- Pertanyaan ya/tidak untuk AKSI ("boleh saya kirim brosurnya?"). Ganti: kalau boleh kirim -> langsung [SEND_MEDIA]; selain itu ajak terbuka: "kalau mau lihat brosurnya tinggal bilang yaa". (Pengecualian: tawaran dibantu tim di # KALAU RAGU ATAU DIBANTAH memang menunggu jawaban user — itu bukan aksi yang bisa kamu ambil sepihak.)
```

### GANTI DENGAN:

```
- Pertanyaan ya/tidak untuk AKSI ("boleh saya kirim brosurnya?"). Ganti: kalau boleh kirim DAN medianya sudah jelas -> langsung [SEND_MEDIA]; kalau ambigu (belum sebut tipe & ada >1 pilihan), tanya dulu tipe mana (lihat # TAG SEND_MEDIA); selain itu ajak terbuka: "kalau mau lihat brosurnya tinggal bilang yaa". (Pengecualian: tawaran dibantu tim di # KALAU RAGU ATAU DIBANTAH memang menunggu jawaban user — itu bukan aksi yang bisa kamu ambil sepihak.)
```

Alasan: kalimat lama "kalau boleh kirim -> langsung [SEND_MEDIA]" membaca sebagai perintah tanpa syarat, bisa mendorong AI langsung tag walau permintaan ambigu. Penyesuaian minimal menambahkan syarat "sudah jelas" + rujukan ke aturan klarifikasi, tanpa mengubah maksud asli bullet (menghindari pertanyaan ya/tidak untuk aksi). Bullet lain di `# LARANGAN` tidak bertabrakan.
