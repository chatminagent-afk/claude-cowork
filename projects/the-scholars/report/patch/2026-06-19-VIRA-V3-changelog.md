   # VIRA_V3 — Changelog & Catatan Implementasi
Tanggal: 2026-06-19 · Basis: `VIRA.json` (V2, Haiku 4.5) · Model: tetap **Claude Haiku 4.5** (cost murah)
Versi: REVISI — konsolidasi PROGRAM sebagai single source of truth.

Tujuan: persona Sam konsisten, akurasi tinggi, anti-halusinasi, token efisien, bug diperbaiki — tanpa kembali ke Sonnet/V1.

## Ringkasan perubahan

1. **Bug memory reset per jam — DIPERBAIKI** (root cause "muter-muter / ulang tanya kelas / kirim link 2x").
   - `Simple Memory.sessionKey`: `user_wa + '_' + getHours()` → **`user_wa`** (memori stabil, tidak hilang ganti jam).
   - Ditambah `contextWindowLength: 10`.

2. **Data layer dikonsolidasi ke tab PROGRAM (single source of truth).**
   - Tab PROGRAM sudah superset lengkap (Harga, Pembayaran, Nama Batch, Status, Tanggal, Kuota, Deadline, Syarat Umum, Dokumen) → tidak perlu tab BATCH/HARGA/SYARAT terpisah.
   - `FAQ Retrieve` di-upgrade jadi **Context Retrieve**: menyuntik blok **DATA TERVERIFIKASI** (STATUS & BATCH, HARGA, SYARAT, PROGRAM detail) yang SEMUANYA diturunkan dari satu read PROGRAM, plus ABOUT_SAM, LINKS aktif, dan FAQ.
   - Injeksi **kondisional** (hemat token): STATUS/BATCH + pemetaan program selalu ada; HARGA/SYARAT/detail/ABOUT_SAM hanya saat relevan.
   - Read nodes (executeOnce): `Read FAQ → Read PROGRAM Data → Read ABOUT Data → Read LINKS Data → Context Retrieve → AI Agent`. Hanya 3 read tambahan (bukan 6) → lebih ramping, sumber tunggal, anti-bentrok data.

3. **Tool agent dihapus (PROGRAM, LINKS, ABOUT_SAM).**
   - Tanpa tool = tanpa round-trip LLM ekstra, tanpa kegagalan "max iterations", input ringkas, token paling efisien. Semua fakta via injeksi (poin 2).
   - Pengiriman link tetap lewat alur `[SEND_GFORM]` + node `Query LINKS for GForm` (terpisah, tidak terdampak).

4. **System prompt ditulis ulang (fix persona + grounding).**
   - **Register (fix "orangtua tapi pakai aku-kamu"):** ke ORANG TUA dilarang "kamu" untuk merujuk anak → pakai "anaknya"; "kamu" hanya untuk murid.
   - **Anti-halu eksplisit:** ASEAN Scholarship fully funded penuh, **TIDAK ADA "partial scholarship"**; semua fakta wajib dari DATA TERVERIFIKASI/FAQ, kalau tidak ada → `[UNKNOWN]`, dilarang menebak.
   - Gaya Sam, aturan BATCH/HARGA gating, dan tag dipertahankan.

5. **Temperature 0.7 → 0.4.**

## Validasi (semua PASS)
JSON valid; 52 node. Rantai retrieval benar; Preprocess→Read FAQ utuh; AI Agent diumpani Context Retrieve(main)+model+memory; 0 tool tersisa & 0 edge ai_tool; tidak ada referensi menggantung. sessionKey tanpa getHours; contextWindowLength 10; temp 0.4; prompt memuat data_context+faq_context; code baca PROGRAM saja.

## Credentials (siap import + publish)
Semua node yang butuh kredensial sudah terpasang:
- **googleApi** — id `3gTKMbD8lJDLbRqR` ("Google Service Account thescholars") — 19 node (termasuk 3 read baru).
- **anthropicApi** — id `DPNnlN1bTbbMf8ks` ("Anthropic account") — node model.
- **httpRequest** (Reply Chat / Send GForm / Notify / Reply Error) — autentikasi inline via `secret` Kirimi di body, tidak butuh objek credential.

Karena ID kredensial sama dengan instance n8n kamu sekarang, setelah import semuanya langsung ke-resolve — tinggal aktifkan/publish. (Catatan: blok `tags` tidak disertakan karena ekspor V2 asli terpotong di bagian itu; tidak mempengaruhi import.)

## ⚠️ Yang HARUS kamu perbaiki di Google Sheet sebelum publish
Karena PROGRAM jadi satu-satunya sumber, pastikan datanya benar. Saat ini ada satu yang salah:
- **Harga Mock Interview di tab PROGRAM = `to be confirmed by Sam`**, padahal di tab HARGA & MOCK_INTERVIEW sudah `Rp 750.000`. Update kolom Harga Mock Interview di PROGRAM jadi **Rp 750.000** supaya bot tidak menjawab "nanti dikonfirmasi".
- Tab BATCH/HARGA/SYARAT terpisah sebaiknya diarsipkan/diabaikan (bot tidak membacanya lagi) agar tidak ada sumber ganda.
- Saran opsional: tambah 1 baris FAQ "Apakah ada beasiswa partial?" → "ASEAN Scholarship fully funded penuh, gaada partial."

## Belum dilakukan
Belum diuji jalan di n8n live. Disarankan UAT 4 skenario gagal V2: partial scholarship, register orang tua, syarat/portofolio kelas 10, alur daftar lintas jam.
