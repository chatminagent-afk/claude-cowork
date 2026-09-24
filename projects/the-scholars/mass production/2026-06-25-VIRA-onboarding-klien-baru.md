# VIRA Template — Panduan Onboarding Klien Baru

**Target waktu: < 30 menit per klien. Tidak ada edit logika/kode node.**

Paket file:
- `VIRA_TEMPLATE_v1.json` — workflow n8n generik (engine). Sama untuk semua klien.
- `VIRA_DATABASE_TEMPLATE.xlsx` — template database. Dicopy per klien.

---

## Prinsip desain

Semua yang spesifik per klien dipindah keluar dari logika ke **3 tempat**:

1. **Tab CONFIG** di Google Sheet klien → persona, keyword, mapping program, whitelist, rate limit.
2. **Tab data** (PROGRAM / ABOUT_SAM / LINKS / FAQ) → knowledge base klien.
3. **n8n Credentials** → secret Kirimi + akun Google (tidak pernah masuk ke JSON/Excel).

Yang Anda sentuh saat pasang klien baru hanya: **1 Google Sheet ID** + **pilih 2 credential**. Workflow tidak diubah.

---

## Langkah pasang klien baru

### A. Siapkan database (≈10 menit)
1. Upload `VIRA_DATABASE_TEMPLATE.xlsx` ke Google Drive → buka dengan Google Sheets (atau File > Import).
2. Beri nama: `VIRA DB - <Nama Klien>`.
3. Buka tab **CONFIG**. Isi semua baris bertanda **kuning** (wajib):
   - `client_name`, `system_prompt` (persona klien), `status_question`, `admin_phone`, `whitelist_enabled`, `grade_program_map`.
   - Sisanya boleh dibiarkan default.
   - Nilai daftar (whitelist_numbers, *_keywords, grade_program_map) ditulis sebagai **JSON valid dalam satu sel**. Contoh sudah terisi.
4. Isi tab **PROGRAM, ABOUT_SAM, LINKS, FAQ** dengan data klien. Hapus baris contoh.
5. Biarkan tab **STATS** & **UNKNOWN** kosong (diisi otomatis bot). Jangan hapus baris header.
6. Catat **Google Sheet ID** (bagian URL antara `/d/` dan `/edit`).

> Jangan ubah nama tab atau nama kolom (baris header). Engine membaca by name.

### B. Kredensial (≈10 menit)
7. **Google Service Account:** share spreadsheet klien ke email service account n8n sebagai **Editor**. (Jika belum punya: buat 1 service account, aktifkan Google Sheets API, pakai untuk semua klien.)
8. **Kirimi Custom Auth:** di n8n → Credentials → New → **Custom Auth**. Isi:
   ```json
   { "body": { "user_code": "XXXX", "secret": "XXXX", "device_id": "XXXX" } }
   ```
   Beri nama `Kirimi - <Nama Klien>`. (Secret hanya di sini, tidak di file.)

### C. Workflow n8n (≈5 menit)
9. Import `VIRA_TEMPLATE_v1.json`.
10. Buka node **Bootstrap Config** → ganti `PASTE_CLIENT_GOOGLE_SHEET_ID_HERE` dengan Sheet ID klien (langkah 6). **Ini satu-satunya edit di workflow.**
11. Pilih credential:
    - Semua node **Google Sheets** → pilih Google Service Account klien.
    - Semua node **HTTP Request** (Kirimi) → pilih credential Kirimi Custom Auth klien (langkah 8).
12. Set **Webhook** klien di Kirimi/WA gateway → arahkan ke URL webhook node (`.../wa-inbound`). Disarankan tambah header secret untuk auth (lihat catatan keamanan).
13. **Activate** workflow.

### D. Smoke test live (≈5 menit) — lihat checklist UAT di bawah
14. Kirim pesan uji dari WA → pastikan bot membalas.

---

## Checklist UAT live (jalankan setelah import tiap klien)

Logika deterministik sudah lolos QA otomatis (lihat QA report). Yang perlu dicek live per klien:

- [ ] Pesan biasa → bot membalas (Kirimi credential & Google credential benar).
- [ ] User baru → bot menanyakan status (`status_question`) sekali, tidak loop.
- [ ] User jawab "saya orang tuanya" → bot tidak menyapa "kamu" ke anak.
- [ ] Tanya jadwal/kelas sesuai `grade_program_map` → program yang disarankan benar.
- [ ] Minta link daftar → form terkirim dari tab LINKS.
- [ ] Pertanyaan di luar data → bot jawab tidak tahu (bukan mengarang).
- [ ] Ketik "mau ngomong sama Sam" → notifikasi handoff masuk ke `admin_phone`.
- [ ] Set `bot_mode = OFF` di STATS untuk satu user → bot berhenti membalas user itu (HITL).
- [ ] `whitelist_enabled = true` + nomor tak terdaftar → bot diam; `false` → semua dilayani.

---

## Catatan keamanan (wajib)

- **Jangan** menaruh secret Kirimi di Excel/JSON. Hanya di n8n Custom Auth credential.
- Tambah **autentikasi webhook** (header secret / verifikasi pengirim) sebelum produksi publik — webhook terbuka bisa di-spam dan membakar token AI.
- Default `whitelist_enabled=false` (produksi). Set `true` hanya saat uji terbatas.

## Batasan yang diketahui (untuk skala besar)

- State disimpan di Google Sheets → cocok untuk volume rendah-menengah per klien. Untuk concurrency tinggi / sangat banyak klien aktif bersamaan, rencanakan migrasi state ke database (Postgres/Supabase). Knowledge base boleh tetap di Sheets.
- Layer bahasa pada `Process All` dioptimalkan untuk Bahasa Indonesia.
