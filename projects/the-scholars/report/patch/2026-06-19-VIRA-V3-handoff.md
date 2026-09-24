# VIRA V3 — Handoff Summary (untuk agent berikutnya)
Tanggal: 2026-06-19 · Proyek: VIRA AI Chatbot "Sam" (The Scholars) di n8n · WhatsApp via Kirimi API

## 1. Konteks proyek
VIRA = chatbot WhatsApp berpersona "Sam" (Samuel Oscar Yobeliano, founder The Scholars), untuk FAQ + registrasi beasiswa Singapura (ASEAN Scholarship). Fitur: jawab FAQ, kirim link GForm pendaftaran, follow-up, human-in-the-loop (Sam bisa matikan bot).
Stack: n8n workflow + Google Sheets (database) + Claude (LLM) + Kirimi (WhatsApp API).

## 2. Masalah yang diinvestigasi
Kualitas turun setelah migrasi V1 → V2:
- **V1** = `VIRA 15 juni.json` (Claude Sonnet 4.6 + gpt-5-mini hybrid). Ada di folder `the scholars`.
- **V2** = `VIRA.json` (Claude Haiku 4.5). Ada di folder `enhancement boros v2 vira 18 juni`. CATATAN: file ini terpotong di bagian `tags` paling akhir (ekspor tidak lengkap), tapi semua node/connection utuh.

4 chat gagal V2 (di subfolder `after implementing v2`): partial-scholarship halusinasi, register "kamu" ke orang tua, jawaban salah soal syarat kelas 10, alur daftar muter-muter & kirim link 2x.

## 3. Root cause yang ditemukan (hasil analisa)
1. **Memory reset per jam** — `sessionKey` di node "Simple Memory" = `user_wa + '_' + new Date().getHours()`. Percakapan lewat batas jam → konteks hilang → muter-muter, ulang tanya kelas, kirim link 2x. Bug ini ADA DI V1 & V2.
2. **Prompt dikompres 45%** (13.8k → 7.6k char) → disambiguasi persona hilang → "kamu" ke orang tua. Aturan lama tidak melarang "kamu" ke ortu secara eksplisit.
3. **Reduksi akses data** — agent V2 cuma punya 3 tool (PROGRAM, ABOUT_SAM, LINKS); tidak bisa cek batch/harga/syarat → menebak → halusinasi ("partial scholarship", padahal FAQ jelas ASEAN = fully funded).
4. Haiku 4.5 = amplifier (lebih lemah ikuti aturan bersyarat & tracking state), bukan akar tunggal.
5. Temp 0.7 + agent loop sampai max-iterations (terlihat di UAT Cost Claude.xlsx).

Kesimpulan: bukan semata model. Kombinasi prompt + akses data + bug memory, diperparah model lemah. Rekomendasi: perbaiki V2 sambil tetap Haiku (jangan balik ke Sonnet — mahal & tidak fix akar).

## 4. Keputusan user
- Tetap **Haiku 4.5** (cost murah).
- Strategi data = **paling anti-halu + akurat + token-efisien** → injeksi data deterministik (bukan tool).
- **Tab PROGRAM adalah single source of truth** — sudah superset (berisi Harga, Pembayaran, Nama Batch, Status, Tanggal, Kuota, Deadline, Syarat Umum, Dokumen). JANGAN dipecah ke tab BATCH/HARGA/SYARAT terpisah (itu malah bikin data ganda/bentrok).

## 5. Yang sudah dibangun — VIRA_V3
File: **`2026-06-19-VIRA-V3.json`** (di folder `enhancement boros v2 vira 18 juni`). Dibuat dari V2, perubahan:
1. Memory: `sessionKey` → `={{ $('Chat Counter').first().json.user_wa }}` (drop getHours) + `contextWindowLength: 10`.
2. Data: node "FAQ Retrieve" jadi **Context Retrieve** — inject blok DATA TERVERIFIKASI (STATUS&BATCH, HARGA, SYARAT, PROGRAM detail) yang SEMUA diturunkan dari 1 read tab PROGRAM, plus ABOUT_SAM, LINKS, FAQ. Injeksi kondisional (hemat token). Rantai: `Read FAQ → Read PROGRAM Data → Read ABOUT Data → Read LINKS Data → Context Retrieve → AI Agent` (read baru = executeOnce).
3. Tool agent (PROGRAM/LINKS/ABOUT_SAM) DIHAPUS → tanpa round-trip ekstra, tanpa max-iteration fail.
4. System prompt ditulis ulang: register eksplisit (ortu jangan "kamu", pakai "anaknya"; "kamu" hanya murid) + anti-halu (fully funded, no partial; fakta hanya dari DATA/FAQ; tidak ada → [UNKNOWN]).
5. Temperature 0.7 → 0.4.

Validasi otomatis: JSON valid (52 node), wiring benar, 0 tool tersisa, tidak ada koneksi menggantung, semua kredensial terpasang.

## 6. Credentials (sudah lengkap untuk import + publish)
- `googleApi` id `3gTKMbD8lJDLbRqR` ("Google Service Account thescholars") — 19 node Sheets.
- `anthropicApi` id `DPNnlN1bTbbMf8ks` ("Anthropic account") — node model Haiku.
- httpRequest (Kirimi) — auth inline via `secret` di body, tanpa objek credential.
Doc Sheet ID: `1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE`. gid penting: FAQ 1440848147, PROGRAM 1775378091, ABOUT_SAM 1394414281, LINKS 1077897272, BATCH 1670648455, HARGA 1090343785, SYARAT 1002257030.

## 7. ⚠️ ACTION ITEM sebelum publish (PENTING)
- **Perbaiki harga Mock Interview di tab PROGRAM**: sekarang `to be confirmed by Sam`, seharusnya **Rp 750.000** (sesuai tab HARGA & MOCK_INTERVIEW). Karena bot kini hanya baca PROGRAM, kalau tidak diperbaiki bot jawab "nanti dikonfirmasi".
- Arsipkan/abaikan tab BATCH/HARGA/SYARAT terpisah (bot tidak baca lagi) supaya tidak ada sumber ganda.
- Opsional: tambah 1 baris FAQ "Apakah ada beasiswa partial?" → "ASEAN Scholarship fully funded penuh, gaada partial."

## 8. Belum dilakukan / next steps
- **Belum diuji di n8n live.** Import V3, perbaiki sheet, lalu UAT 4 skenario gagal V2: (a) partial scholarship, (b) register orang tua, (c) syarat/portofolio kelas 10, (d) alur daftar lintas jam.
- Belum ada checklist UAT formal (bisa dibuat).
- Opsi jangka panjang (kalau perlu akurasi maksimal di kasus sensitif): hybrid routing Haiku→Sonnet, bisa ditambah tanpa membongkar arsitektur V3.

## 9. File terkait (folder `enhancement boros v2 vira 18 juni`)
- `2026-06-19-VIRA-V3.json` — workflow final, siap import.
- `2026-06-19-VIRA-V3-changelog.md` — detail perubahan + validasi + credentials.
- `2026-06-19-VIRA-V3-handoff.md` — file ini.
- `VIRA.json` (V2, basis), `The_Scholars_Database.xlsx` (copy database), `UAT Cost Claude.xlsx` (data biaya per model), `after implementing v2/` (4 chat gagal).
- V1: `../VIRA 15 juni.json`.
