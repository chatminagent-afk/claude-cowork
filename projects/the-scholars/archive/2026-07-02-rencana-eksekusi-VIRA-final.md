# Rencana Eksekusi Final — Perbaikan VIRA (Report 1 Juli)

**Tanggal:** 2 Juli 2026 · **Basis:** `2026-07-02-analisa-bug-VIRA-report-1-juli.md` + keputusan Steven + log eksekusi n8n
**Status:** MENUNGGU APPROVAL FINAL — belum ada perubahan yang dieksekusi.

## Keputusan yang sudah masuk

1. **Alur status PARENT/STUDENT DIHAPUS TOTAL** (permintaan client). VIRA tidak lagi menanyakan/menyimpan status; semua balasan pakai register netral tanpa panggilan/sebutan apapun.
2. **Wait3 = 60 detik dipertahankan** (disengaja; komentar "8 detik" di kode = typo, akan dibetulkan sekalian).
3. `production/VIRA.json` dikonfirmasi export live terbaru; whitelist disabled memang untuk mode publik.
4. Identitas user: **No WA primer, lid backup** (sesuai desain Steven — dipakai client untuk set `bot_mode` OFF manual). Fix matching akan mengikuti prinsip ini.

## Update analisa Masalah 4 (berdasarkan log eksekusi)

Log menunjukkan pesan ke-2 Adrian **tidak pernah masuk ke pending_msg sama sekali** (eksekusi pemenang meng-append pesan ke-3 ke `"mau tanya"` saja — bukan tertimpa setelah tertulis). Tiga kemungkinan, urut prioritas:

1. **Eksekusi pesan ke-2 error di tengah** — kandidat kuat: quota Google Sheets API (workflow ini ±8–10 operasi Sheets per pesan; 3 pesan beruntun = beban tinggi, error 429 membuat eksekusi mati diam-diam dan pesan hilang).
2. **Webhook Kirimi tidak deliver** pesan ke-2 ke n8n sama sekali.
3. Race read-modify-write (analisa awal) — tetap ada sebagai kelemahan desain, tapi bukan yang terjadi di kasus ini jika poin 1/2 terkonfirmasi.

**Cek yang dibutuhkan dari Steven (menentukan 1 vs 2):** di list Executions n8n, sekitar **28/6 10:27:50–10:28:05 WIB** — adakah eksekusi ke-3 (status apapun: error/success-kosong)? Kalau ada dan error → catat node mana yang gagal. Kalau tidak ada sama sekali → masalah di sisi Kirimi/webhook.

Solusi ditambah satu item baru: **Error Workflow** (Error Trigger → notifikasi WA admin via Kirimi) supaya eksekusi yang mati tidak lagi hilang diam-diam.

---

## Daftar Perubahan Final

### Paket 1 — Hapus alur status + register netral (scope baru dari client)

**System prompt AI Agent** (memangkas ±20%):

- HAPUS: seluruh `# REGISTER`, seluruh `# STATUS`, `# ALUR` langkah 3, semua referensi tag `[USER_STATUS]`, aturan "Tanya status ortu/murid tetap boleh" di `# LARANGAN`.
- TAMBAH (ringkas): aturan **REGISTER NETRAL** — dilarang menyapa user dengan "kamu"/"Anda"/vokatif apapun (Pak/Bu/Om/Tante/Kak); jangan berasumsi lawan bicara ortu atau murid; pertanyaan tentang calon murid diframe netral, contoh: "Yang mau ikut programnya sekarang kelas berapa yaa?"; merujuk calon murid cukup "calon muridnya"/"yang mau daftar".
- TAMBAH: aturan intro user baru (lihat Paket 2).

**Node:**

| Node | Perubahan |
|---|---|
| Preprocess - Context Detection | Hapus blok 4 (detectedStatusFromMessage) + semua aiContext soal status. Bug regex `anaknya` otomatis ikut hilang. |
| Cek_user_status | Hapus semua logika user_status/shouldAskStatus. Definisi user baru = `greeting_sent !== 'Y'` (atau row belum ada). SYSTEM_DATA jadi ramping. |
| Process All | Hapus parsing `[USER_STATUS]` + fallback deteksi status + output `userStatus`/`needs_status_update`. Regex penghapus vokatif tetap dipertahankan sebagai safety net register netral. |
| IF Status Update Needed, Update User Status | Dihapus dari workflow (2 node). |
| Sheet STATS | Berhenti tulis `user_status`; hapus dari mapping semua node. Kolomnya dibiarkan dulu (arsip), dihapus manual setelah 1-2 minggu stabil. |

### Paket 2 — Intro user baru (Opsi A, tanpa tanya status)

Lebih sederhana dari rencana awal karena status sudah tidak ditanya:

- **Cek_user_status**: jika user baru → instruksi ke AI: buka dengan intro verbatim client ("Haloo thank you sudah contact TheScholars.id yaa. Saya Sam versi AI yaa, saya siap bantu untuk jawab pertanyaan yang ada mengenai program kita dan scholarships ke Singapore.") lalu **langsung jawab pertanyaan user di pesan yang sama** (register netral).
- **System prompt**: sisipkan aturan intro di `# ALUR` (menggantikan langkah status yang dihapus).
- **Update STATS - Greeting Flag**: buang pattern-matching teks; set `greeting_sent=Y` cukup dari flag `is_new_user` + reply sukses.

### Paket 3 — Fix Process All over-strict (Masalah 1)

- Persempit `internalKeywords` ke frasa yang benar-benar internal: `saya cek data`, `saya cek di sheet`, `berdasarkan faq`, `berdasarkan data`, `dari faq`, `dari sheet`, `menurut data`, `faq yang tersedia`. Buang: `saya cek`, `saya lihat`, `saya temukan`, `saya ambil`, `dari data`, `data yang ada`, `referensi yang ada`.
- Guard anti-kosong: jika hasil stripping kosong padahal output AI asli tidak kosong → pakai output asli (setelah bersih tag/markdown). Pesan "Maaf, terjadi kesalahan" hanya bila AI benar-benar tidak menghasilkan apa-apa.

### Paket 4 — Debounce & keandalan pesan (Masalah 4, revisi)

1. **Sheet `MSG_BUFFER` append-only** (lid/No WA, message, ts): Update Buffer → operasi append row (atomik); winner gabung semua row urut ts di Cek_user_status; Delete_Pending_Msg (+varian) hapus row terproses. Kolom `pending_msg` STATS pensiun. Menutup race secara permanen.
2. **Error Workflow n8n** (baru, kecil): Error Trigger → HTTP Kirimi notif admin ("Eksekusi VIRA gagal di node X untuk nomor Y"). Menutup "pesan hilang diam-diam".
3. **Kurangi beban Sheets API per pesan** (mitigasi 429): Read FAQ/PROGRAM/ABOUT/LINKS = 4 read terpisah per pesan → digabung dievaluasi belakangan HANYA jika cek eksekusi membuktikan 429 (jangan over-engineer duluan).
4. Betulkan komentar "8 detik" → "60 detik" di Cek_user_status.

### Paket 5 — Fix matching row STATS (Temuan A — data user tertukar)

Sesuai prinsip Steven (No WA primer, lid backup):

- Semua node matching (Update Buffer, Cek_user_status, HITL Check, Delete_Pending_Msg + varian): match by `No WA` (digit-normalized) dulu → fallback `lid` HANYA jika No WA kosong → **tidak ada fallback `|| rows[0]`** (tidak ketemu = treat sebagai user baru, jangan ambil row orang lain).
- Guard: jangan pernah match dengan nilai kunci kosong.

### Paket 6 — Context/memory (Masalah 2)

- Kolom STATS baru: `kelas_anak`, `program_interest` — diisi dari deteksi Preprocess yang sudah ada, lewat siklus Update to STATS existing.
- Inject ke SYSTEM_DATA di Cek_user_status + instruksi "jangan tanya ulang kelas kalau sudah terisi".
- `contextWindowLength` 10 → 20; sessionKey Simple Memory → `user_lid || user_phone` (digit saja).
- Catatan operasional: Simple Memory ter-reset setiap save/edit workflow di editor n8n — konteks percakapan berjalan akan hilang tiap deploy patch. Kolom persisten di atas adalah mitigasinya.

### Paket 7 — Pemahaman kelas Singapura/internasional (Temuan B)

- Preprocess: mapping tambahan — `primary 6`→SD 6, `sec 1`→SMP 1, `sec 2`→SMP 2, `sec 3`→SMP 3, `sec 4`→SMA 10; plus angka Romawi `kelas x/xi/xii` (kasus Adrian "kelas x" tidak terdeteksi).
- System prompt: 1 paragraf — sebutan "Sec 1–4"/sekolah kurikulum Singapura (SIS, BBS, dll.) TIDAK berarti anaknya sudah di Singapura; kalau ragu tanya kota sekolahnya.

### Paket 8 — Keamanan & ops (tidak mendesak, setelah 1–7 stabil)

- Rotasi secret Kirimi + pindah ke n8n Credentials (7 node HTTP); auth sederhana di webhook.
- SOP harian: Sam cek sheet UNKNOWN → jawab manual → tandai kolom `answered`.

---

## Urutan Eksekusi & Testing

Eksekusi bertahap (tiap paket = satu perubahan yang bisa di-rollback):

1. Paket 3 (fix stripper) — dampak terbesar, risiko terkecil.
2. Paket 1 + 2 (hapus status + intro) — satu kesatuan, ubah prompt & node sekaligus.
3. Paket 5 (matching No WA) → 4 (MSG_BUFFER + error workflow) → 6 → 7 → 8.

**Test plan per rilis:** (a) pesan yang memancing "saya cek/saya lihat"; (b) chat nomor baru → intro muncul + pertanyaan pertama terjawab + tanpa "kamu"/vokatif; (c) 3 pesan beruntun <10 dtk × beberapa kali → semua baris masuk; (d) user lama tanya lanjutan setelah save workflow → kelas tidak ditanya ulang; (e) istilah "Sec 3"; (f) set bot_mode OFF via No WA → bot diam.

## Masih dibutuhkan dari Steven

1. **Cek list Executions n8n 28/6 10:27:50–10:28:05 WIB** — ada eksekusi ke-3? Error di node apa? (Menentukan apakah perlu investigasi sisi Kirimi.)
2. Apakah 30/6 antara 12:24–14:25 WIB kamu sempat save/edit workflow di editor n8n? (Konfirmasi final penyebab context loss Marsella.)
3. Approval untuk mulai eksekusi Paket 3 → 1+2 → dst.
