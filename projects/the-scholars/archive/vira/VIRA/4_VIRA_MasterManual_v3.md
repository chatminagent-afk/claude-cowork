# VIRA Master Manual & Integration Guide
## The Scholars Edition — v3.0
**Untuk:** Steven Leroy | **Last updated:** April 2026

---

# DAFTAR ISI

**Master Manual**
1. [Arsitektur Sistem v3](#1-arsitektur-sistem-v3)
2. [Perubahan dari v2 ke v3](#2-perubahan-dari-v2-ke-v3)
3. [Deploy Step-by-Step](#3-deploy-step-by-step)
4. [Konfigurasi Wajib Setelah Import](#4-konfigurasi-wajib-setelah-import)

**Integration Guide**
5. [Human-in-the-Loop (HITL)](#5-human-in-the-loop-hitl)
6. [GForm Flow — Pendaftaran Mock Interview](#6-gform-flow--pendaftaran-mock-interview)
7. [Follow-Up Logic v3](#7-follow-up-logic-v3)
8. [Google Sheets — Struktur Kolom Wajib](#8-google-sheets--struktur-kolom-wajib)
9. [Testing Checklist v3](#9-testing-checklist-v3)
10. [Troubleshooting](#10-troubleshooting)

---

# 1. Arsitektur Sistem v3

## Flow CHATBOT_MAIN v3

```
User kirim WA
    ↓
[Kirimi Webhook]
    ↓
[Chat Counter] — filter: bukan dari bot sendiri, bukan audio/gambar
    ↓
[Rate Limiter] — maks 5 pesan/menit/user
    ↓
[Read STATS for HITL] — baca sheet STATS sekali (executeOnce)
    ↓
[HITL Check] — cek kolom bot_mode
    │
    ├── bot_mode = "OFF" → STOP (Sam sedang handle manual)
    │
    └── bot_mode = kosong/"ON" → lanjut
            ↓
        [AI Agent] ← tools: PROGRAM, BATCH, HARGA, SYARAT,
        [Simple Memory]        MOCK_INTERVIEW, FAQ
            ↓
        [Process All] — extract tags: [SEND_GFORM], [MOCK_INTERVIEW_BOOKING], [UNKNOWN]
            ↓
        ┌──────────────────────────────────────────┐
        │ IF Send GForm? ──── YA ──→ [Send GForm Link]
        │                              ↓
        │                    [Update GForm Sent TS]
        │
        │ IF Unknown? ────── YA ──→ [Record to UNKNOWN]
        │                              ↓
        │                    [Wait] → [Notify Admin Unknown]
        │
        │ IF Can Record? ─── YA ──→ [Record to MOCK_INTERVIEW_SHEET]
        │                              ↓
        │                    [Wait] → [Notify Book]
        └──────────────────────────────────────────┘
            ↓
        [Wait 5-10 detik]
            ↓
        [Reply Chat Kirimi] — kirim cleanOutput ke user
            ↓
        [Check API Response]
            │
            ├── GAGAL → [Notify Admin API Error]
            │
            └── SUKSES → [Extract & Prepare Data]
                            ↓
                        [Read STATS] → [Update to STATS]
```

## Flow FOLLOW UP v3

```
[Schedule: setiap hari jam 10 pagi]
    ↓
[Read MOCK_INTERVIEW_BOOKING] — siapa yang sudah booking (di-exclude)
    ↓
[Read STATS] — semua user yang pernah chat
    ↓
[Filter] — kriteria:
  - bot_mode ≠ OFF
  - Tidak ada di MOCK_INTERVIEW_BOOKING
  - follow_up_count < 3
  - PRIORITAS 1: gform_sent_ts ada + gform_filled ≠ Y + >24 jam
  - PRIORITAS 2: tidak aktif >24 jam + belum dapat GForm
    ↓
[Loop Over Items]
    ↓
[IF GForm Reminder?]
    │
    ├── YA → [Send GForm Reminder] → [Update STATS]
    │
    └── TIDAK → [Switch Follow Up Count]
                    ├── 1 → [Send Follow Up 1]
                    ├── 2 → [Send Follow Up 2]
                    └── 3 → [Send Follow Up 3]
                              ↓
                    [Check Success] → SUKSES → [Update STATS]
                                    → GAGAL  → [Notify Admin FU Error]
```

---

# 2. Perubahan dari v2 ke v3

## CHATBOT_MAIN

| Komponen | v2 | v3 |
|---|---|---|
| Human-in-the-loop | Tidak ada | ✅ `Read STATS for HITL` + `HITL Check` |
| GForm flow | Tidak ada | ✅ `IF Send GForm` + `Send GForm Link` + `Update GForm Sent TS` |
| Tools AI Agent | TUTOR, JADWAL, KURIKULUM, BOOKING, SPESIFIKASI, HARGA, FAQ | PROGRAM, BATCH, SYARAT, MOCK_INTERVIEW, HARGA, FAQ |
| Booking/Pendaftaran | Record to PENDAFTARAN | Record to MOCK_INTERVIEW_SHEET |
| Tag di Process All | [PENDAFTARAN], [DATA_COMPLETE], [UNKNOWN] | [SEND_GFORM], [MOCK_INTERVIEW_BOOKING], [PENDAFTARAN], [DATA_COMPLETE], [UNKNOWN] |
| Reply content | `$json.output` | `$json.cleanOutput` (tags sudah distrip) |

## FOLLOW UP

| Komponen | v2 | v3 |
|---|---|---|
| Follow-up type | Satu jalur (general) | Dua jalur: GForm Reminder + General |
| HITL aware | Tidak ada | ✅ Skip jika bot_mode = OFF |
| GForm reminder | Tidak ada | ✅ 24 jam setelah GForm dikirim, belum diisi |
| Read BOOK | Read BOOK | Read MOCK_INTERVIEW_BOOKING |

## Database Sheets

| Sheet | v2 | v3 |
|---|---|---|
| STATS | 10 kolom | 13 kolom (+`bot_mode`, `gform_sent_ts`, `gform_filled`) |
| PENDAFTARAN | Untuk semua pendaftaran | Dihapus |
| MOCK_INTERVIEW_BOOKING | Belum ada | ✅ Baru — untuk booking mock interview |
| FASE_ROADMAP | Belum ada | ✅ Baru — reference arsitektur Fase 1–6 |

---

# 3. Deploy Step-by-Step

## Step 1 — Upload Database ke Google Sheets

1. Buka Google Drive → Upload → pilih `3_TheScholars_Database_v2.xlsx`
2. Setelah upload, klik kanan → **Open with Google Sheets**
3. Sheets akan otomatis convert ke Google Sheets format
4. Copy URL spreadsheet (format: `https://docs.google.com/spreadsheets/d/[ID]/edit`)
5. Simpan ID spreadsheet (bagian antara `/d/` dan `/edit`)

> **Penting:** Setelah convert, cek setiap sheet — pastikan semua 10 tab ada:
> STATS, PROGRAM, BATCH, HARGA, SYARAT, MOCK_INTERVIEW, MOCK_INTERVIEW_BOOKING, FAQ, UNKNOWN, FASE_ROADMAP

## Step 2 — Catat GID Setiap Sheet

Setiap sheet punya GID unik. Cara lihat: klik tab sheet → lihat URL, bagian `#gid=XXXXXX`.

| Sheet | GID (isi setelah upload) |
|---|---|
| STATS | `#gid=___________` |
| PROGRAM | `#gid=___________` |
| BATCH | `#gid=___________` |
| HARGA | `#gid=___________` |
| SYARAT | `#gid=___________` |
| MOCK_INTERVIEW | `#gid=___________` |
| MOCK_INTERVIEW_BOOKING | `#gid=___________` |
| FAQ | `#gid=___________` |
| UNKNOWN | `#gid=___________` |

## Step 3 — Setup Google OAuth di n8n

1. n8n → Settings → Credentials → New → **Google Sheets OAuth2**
2. Masukkan Client ID dan Client Secret dari Google Cloud Console
3. Klik Connect → login Google → Allow
4. Simpan dengan nama: `The Scholars - Google Sheets`

> Hanya perlu **Google Sheets API**. Tidak perlu Drive API atau Docs API.

## Step 4 — Import JSON Workflows

1. n8n → Workflows → Import from file
2. Import `1_CHATBOT_MAIN_TheScholars_v3.json`
3. Import `2_FollowUp_TheScholars_v3.json`

## Step 5 — Update Semua Placeholder di n8n

Setelah import, cari dan ganti semua placeholder ini di setiap node yang relevan:

### Placeholder yang WAJIB diganti:

```
SPREADSHEET_ID_THESCHOLARS  → ID spreadsheet dari Step 1
KIRIMI_USER_CODE             → user_code dari dashboard Kirimi
KIRIMI_SECRET                → secret dari dashboard Kirimi
KIRIMI_DEVICE_ID             → device_id dari dashboard Kirimi
628ADMIN_NUMBER              → nomor WA Sam (format: 628XXXXXXXXXX)
GFORM_LINK_THESCHOLARS       → link GForm pendaftaran dari Sam
RECONNECT_AFTER_IMPORT       → pilih credential "The Scholars - Google Sheets"
```

### Node-by-node yang perlu diupdate:

**CHATBOT_MAIN_v3:**

| Node | Yang diupdate |
|---|---|
| `Read STATS for HITL` | URL spreadsheet + GID STATS + credential |
| `Read STATS` (akhir flow) | URL spreadsheet + GID STATS + credential |
| `Update to STATS` | URL spreadsheet + GID STATS + credential |
| `Record to MOCK_INTERVIEW_SHEET` | URL spreadsheet + GID MOCK_INTERVIEW_BOOKING + credential |
| `Record to UNKNOWN` | URL spreadsheet + GID UNKNOWN + credential |
| `PROGRAM` (tool) | URL spreadsheet + GID PROGRAM + credential |
| `BATCH` (tool) | URL spreadsheet + GID BATCH + credential |
| `HARGA` (tool) | URL spreadsheet + GID HARGA + credential |
| `SYARAT` (tool) | URL spreadsheet + GID SYARAT + credential |
| `MOCK_INTERVIEW` (tool) | URL spreadsheet + GID MOCK_INTERVIEW + credential |
| `FAQ` (tool) | URL spreadsheet + GID FAQ + credential |
| `Reply Chat Kirimi` | user_code, secret, device_id |
| `Send GForm Link` | user_code, secret, device_id, **link GForm** |
| `Notify Book` | user_code, secret, device_id, phone (nomor Sam) |
| `Notify Admin Unknown` | user_code, secret, device_id, phone (nomor Sam) |
| `Notify Admin API Error` | user_code, secret, device_id, phone (nomor Sam) |
| `Chat Counter` | Nomor WA device bot di filter anti-loop |

**FOLLOW_UP_v3:**

| Node | Yang diupdate |
|---|---|
| `Read MOCK_INTERVIEW_BOOKING` | URL spreadsheet + GID MOCK_INTERVIEW_BOOKING + credential |
| `Read STATS` | URL spreadsheet + GID STATS + credential |
| `Update STATS` | URL spreadsheet + GID STATS + credential |
| `Send Follow Up 1/2/3` | user_code, secret, device_id |
| `Send GForm Reminder` | user_code, secret, device_id, **link GForm** |
| `Notify Admin FU Error` | user_code, secret, device_id, phone (nomor Sam) |

## Step 6 — Setup Kirimi

1. Login kirimi.id → Devices → Add Device
2. Scan QR dengan HP yang ada nomor WA VIRA The Scholars
3. Copy `user_code`, `secret`, `device_id` → update semua node Kirimi di Step 5
4. Copy URL Webhook dari node **Webhook** di n8n
5. Kirimi dashboard → device → Webhook URL → paste URL tersebut

## Step 7 — Isi System Prompt

1. Buka node **AI Agent** di CHATBOT_MAIN_v3
2. Ganti field `systemMessage` dengan prompt final dari `7_SystemPrompt_Template.md`
3. Pastikan semua `[FILL: ...]` sudah diisi (persona + data program Sam)

## Step 8 — Isi Database Sheets

Sebelum testing, sheet-sheet ini harus sudah terisi:

| Sheet | Isi minimum sebelum testing |
|---|---|
| PROGRAM | Minimal 1 baris program aktif |
| BATCH | Minimal 1 batch yang sedang open |
| HARGA | Harga semua program |
| SYARAT | Syarat untuk semua program |
| MOCK_INTERVIEW | Minimal 1 sesi yang tersedia |
| FAQ | Minimal 15 Q&A |

## Step 9 — Aktifkan Workflows

1. CHATBOT_MAIN_v3 → toggle **Active = ON**
2. FollowUp_v3 → toggle **Active = ON**
3. Monitor Executions selama 30 menit pertama

---

# 4. Konfigurasi Wajib Setelah Import

## 4.1 Update Nomor Anti-Loop di Chat Counter

Di node `Chat Counter`, cari baris:
```javascript
userNumber === "6281510624599"
```
Ganti `6281510624599` dengan **nomor WA device VIRA The Scholars** (tanpa +, tanpa spasi).

Jika ada beberapa nomor yang perlu diblokir:
```javascript
["628NOMOR1", "628NOMOR2"].includes(userNumber)
```

## 4.2 Reconnect Semua Google Sheets Credentials

Setelah import, semua Google Sheets node akan menampilkan error credential. Lakukan:
1. Klik salah satu Google Sheets node
2. Di bagian Credentials → dropdown → pilih `The Scholars - Google Sheets`
3. Lakukan untuk semua Google Sheets node (termasuk tool nodes)

> **Tip:** n8n memiliki fitur "Update credentials across all nodes" — gunakan ini untuk efisiensi.

---

# 5. Human-in-the-Loop (HITL)

## Cara Kerja

VIRA mengecek kolom `bot_mode` di sheet STATS sebelum meneruskan pesan ke AI Agent. Jika nilainya `OFF`, VIRA berhenti — tidak ada balasan ke user. Sam bebas chat manual dengan user tersebut.

## Cara Sam Aktifkan Manual Mode

1. Buka Google Sheets → tab **STATS**
2. Cari baris dengan No WA user yang ingin di-handle manual
3. Di kolom `bot_mode` → isi `OFF`

```
Contoh:
No WA          | bot_mode
628123456789   | OFF      ← VIRA berhenti balas user ini
628987654321   |           ← VIRA aktif (kosong = bot aktif)
628111222333   | ON        ← VIRA aktif (ON = bot aktif)
```

## Cara Sam Kembalikan ke Bot Mode

1. Buka STATS sheet
2. Di kolom `bot_mode` untuk user tersebut → **hapus isinya** (kosongkan) atau isi `ON`
3. VIRA akan kembali aktif untuk user itu pada pesan berikutnya

## Kolom bot_mode — Aturan Lengkap

| Nilai | Efek |
|---|---|
| *(kosong)* | VIRA aktif — bot balas seperti biasa |
| `ON` | VIRA aktif |
| `OFF` | VIRA berhenti — Sam handle manual |
| `off` / `Off` | VIRA berhenti (case-insensitive) |

> HITL juga berlaku di Follow-Up: user dengan `bot_mode = OFF` tidak akan mendapat follow-up otomatis selama mode manual aktif.

## Cara Sam Tahu Kapan Harus Aktifkan HITL

VIRA akan mengirim notif ke Sam (via `Notify Book`) saat ada yang booking Mock Interview. Di sinilah Sam biasanya perlu take over untuk diskusi pembayaran. Alurnya:

```
User → tanya Mock Interview → VIRA kirim GForm
    ↓
User isi GForm → Sam dapat notif (via Google Forms notification)
    ↓
Sam aktifkan HITL (bot_mode = OFF) untuk user tersebut
    ↓
Sam diskusi pembayaran manual via WA
    ↓
Setelah selesai → Sam kembalikan bot_mode ke kosong/ON
```

## Implementasi Teknis HITL di n8n

Node `Read STATS for HITL` membaca seluruh sheet STATS sekali (`executeOnce: true`), lalu node `HITL Check` memfilter berdasarkan nomor WA user yang sedang chat.

Jika di kemudian hari database STATS sangat besar (>1000 baris) dan performa melambat, ganti `Read STATS for HITL` dengan query spesifik menggunakan Google Sheets node filter by row value. Untuk Fase 1, read-all sudah cukup.

---

# 6. GForm Flow — Pendaftaran Mock Interview

## Overview

Saat user menyatakan ingin daftar Mock Interview, AI Agent menggunakan tag `[SEND_GFORM]` di output-nya. Process All mendeteksi tag ini → `IF Send GForm` = true → `Send GForm Link` kirim pesan WA berisi link GForm ke user → `Update GForm Sent TS` mencatat timestamp pengiriman di STATS.

## Yang Perlu Disiapkan Sam

1. **Buat Google Form** untuk pendaftaran Mock Interview (nama, nomor WA, sesi yang dipilih, dll)
2. Kirim link GForm tersebut ke Steven
3. Steven update nilai `GFORM_LINK_THESCHOLARS` di node `Send GForm Link` dan `Send GForm Reminder`

## Kolom gform_filled — Update Manual oleh Sam

Setelah Sam melihat ada submission baru di Google Form:
1. Buka STATS sheet
2. Cari baris No WA yang mengisi form
3. Di kolom `gform_filled` → isi `Y`

Ini akan menghentikan GForm Reminder di Follow-Up untuk user tersebut.

> **Fase berikutnya (opsional):** Bisa diotomasi dengan Google Forms → Google Sheets trigger di n8n — saat ada submission baru, n8n otomatis update `gform_filled = Y` di STATS. Ini masuk scope Fase 2/3.

## Pesan yang Dikirim ke User

**Saat pertama kali GForm dikirim** (oleh CHATBOT_MAIN):
> "Haii! 😊 Berikut link pendaftaran Mock Interview The Scholars ya: 👉 [LINK] Silakan isi form-nya, nanti tim kami akan follow up setelah form terisi. Ada yang mau ditanyain dulu sebelum isi?"

**GForm Reminder (oleh Follow-Up, 24 jam kemudian jika belum diisi):**
> "Haii Kak [nama]! 👋 Sebelumnya kami sudah kirim link pendaftaran Mock Interview The Scholars. Kalau belum sempat isi, ini link-nya lagi ya: 👉 [LINK] Kalau ada yang mau ditanyain dulu, langsung aja tanya ke sini! 😊"

*Kedua pesan ini perlu disesuaikan dengan persona Sam setelah sample chat diterima.*

---

# 7. Follow-Up Logic v3

## Dua Jalur Follow-Up

### Jalur 1 — GForm Reminder (Prioritas Tinggi)
**Kondisi:** `gform_sent_ts > 0` AND `gform_filled ≠ Y` AND sudah >24 jam sejak GForm dikirim

**Yang terjadi:** Kirim ulang link GForm, update `last follow up` dan `follow_up_count`

**Batas:** Maksimal sampai `follow_up_count = 3`, minimal jarak antar reminder 24 jam

### Jalur 2 — General Follow-Up
**Kondisi:** Belum pernah dapat GForm (`gform_sent_ts = 0`) AND tidak aktif >24 jam

**Yang terjadi:** Kirim salah satu dari 3 template pesan (berdasarkan `follow_up_count`)

**Batas:** Maksimal 3x, minimal jarak 48 jam antar pesan

## User yang Di-skip Follow-Up

- `bot_mode = OFF` (Sam sedang handle manual)
- Sudah ada di sheet MOCK_INTERVIEW_BOOKING (sudah booking)
- `follow_up_count >= 3` (sudah maksimal)

## Jadwal Eksekusi

Follow-Up berjalan setiap hari jam 10 pagi (bisa diubah di node `Schedule Trigger`).

Untuk mengubah jam eksekusi:
1. Buka node `Schedule Trigger` di FollowUp workflow
2. Ubah `triggerAtHour` ke jam yang diinginkan (format 24 jam)

---

# 8. Google Sheets — Struktur Kolom Wajib

## Sheet STATS — Kolom Lengkap v3

| Kolom | Diisi oleh | Keterangan |
|---|---|---|
| No WA | VIRA otomatis | Key utama — format 628XXXXXXXXXX |
| Nama | VIRA otomatis | Nama dari profil WA user |
| Pesan Pertama | VIRA otomatis | Pesan pertama yang dikirim user |
| Counter | VIRA otomatis | Jumlah total pesan dari user ini |
| Tanggal Chat Pertama | VIRA otomatis | |
| Tanggal Chat Terakhir | VIRA otomatis | |
| Jam Chat Terakhir | VIRA otomatis | |
| timestamp | VIRA otomatis | Unix timestamp pesan terakhir (detik) |
| last follow up | VIRA otomatis | Unix timestamp follow-up terakhir |
| follow_up_count | VIRA otomatis | Jumlah follow-up yang sudah dikirim |
| gform_sent_ts | VIRA otomatis | Unix timestamp saat GForm pertama dikirim |
| **gform_filled** | **Sam manual** | Isi `Y` setelah user submit GForm |
| **bot_mode** | **Sam manual** | Isi `OFF` untuk aktifkan manual mode, kosongkan untuk kembali ke bot |

> **Kolom kuning `bot_mode` dan hijau `gform_filled` di Excel = kolom yang Sam edit secara manual.**

## Sheet MOCK_INTERVIEW_BOOKING — Kolom Lengkap

| Kolom | Diisi oleh | Keterangan |
|---|---|---|
| ID Booking | VIRA otomatis | Format: MI-YYYYMMDDXXX |
| Tanggal | VIRA otomatis | |
| No WA | VIRA otomatis | |
| Nama | VIRA otomatis | |
| Sesi | VIRA otomatis | Nama sesi yang dipesan |
| **Status** | **Sam manual** | Pending / Confirmed / Cancelled |
| **Catatan Sam** | **Sam manual** | Catatan internal |
| Timestamp | VIRA otomatis | Unix timestamp |

---

# 9. Testing Checklist v3

## A — HITL (Human-in-the-Loop)

| # | Skenario | Expected | ✓/✗ |
|---|---|---|---|
| H1 | Kirim pesan WA saat `bot_mode` kosong | VIRA balas normal | |
| H2 | Set `bot_mode = OFF` untuk user tester → kirim pesan | VIRA tidak balas sama sekali | |
| H3 | Hapus `bot_mode` (kosongkan) → kirim pesan lagi | VIRA aktif kembali dan balas | |
| H4 | Set `bot_mode = OFF` → jalankan Follow-Up manual | User tersebut di-skip dari follow-up | |

## B — GForm Flow

| # | Skenario | Expected | ✓/✗ |
|---|---|---|---|
| G1 | Chat tentang Mock Interview dan nyatakan ingin daftar | AI output mengandung `[SEND_GFORM]` | |
| G2 | Setelah G1, cek WA tester | Pesan dengan link GForm terkirim | |
| G3 | Cek STATS sheet setelah G2 | Kolom `gform_sent_ts` terisi timestamp | |
| G4 | Biarkan 24 jam, `gform_filled` masih kosong → jalankan Follow-Up | GForm Reminder terkirim | |
| G5 | Isi `gform_filled = Y` di STATS → jalankan Follow-Up | User tidak dapat GForm Reminder | |

## C — Flow Utama (carry-over dari v2)

| # | Skenario | Expected | ✓/✗ |
|---|---|---|---|
| C1 | "halo" | VIRA balas dengan persona Sam | |
| C2 | "berapa biayanya?" | Query HARGA sheet, jawab akurat | |
| C3 | "kapan batch berikutnya?" | Query BATCH sheet, info akurat | |
| C4 | "syaratnya apa?" | Query SYARAT, hanya info publik | |
| C5 | "mock interview gimana?" | Query MOCK_INTERVIEW, info lengkap | |
| C6 | Pertanyaan tidak relevan | Tag [UNKNOWN], notif admin, UNKNOWN sheet terisi | |
| C7 | 6 pesan dalam < 1 menit | Pesan ke-6 tidak dibalas (rate limiter) | |
| C8 | Kirimi token salah → kirim pesan | Admin WA dapat notif API Error | |

## D — Follow-Up v3

| # | Skenario | Expected | ✓/✗ |
|---|---|---|---|
| F1 | STATS: FU=0, timestamp >24 jam, gform_sent_ts=0 → run | FU 1 (general) terkirim | |
| F2 | STATS: gform_sent_ts >24 jam, gform_filled kosong → run | GForm Reminder terkirim (bukan FU general) | |
| F3 | User ada di MOCK_INTERVIEW_BOOKING → run FU | User di-skip | |
| F4 | bot_mode=OFF → run FU | User di-skip | |
| F5 | follow_up_count=3 → run FU | User di-skip | |

**Total skenario: 21. Semua harus ✅ sebelum go live.**

---

# 10. Troubleshooting

| Gejala | Cek | Solusi |
|---|---|---|
| VIRA tidak balas sama sekali | Kirimi device connected? Webhook URL benar? | Update webhook URL di Kirimi |
| VIRA balas tapi pakai `undefined` | Reply Chat Kirimi masih pakai `$json.output`? | Ganti ke `$('Process All').item.json.cleanOutput` |
| HITL tidak bekerja (bot tetap balas saat OFF) | `Read STATS for HITL` URL benar? STATS punya kolom `bot_mode`? | Cek URL + credential + nama kolom exact |
| GForm tidak terkirim | IF Send GForm terhubung ke Send GForm Link? | Cek koneksi + tag [SEND_GFORM] di output AI |
| `gform_sent_ts` tidak terisi | Update GForm Sent TS credential benar? | Cek credential + URL spreadsheet |
| Follow-up tidak jalan | Workflow FollowUp active? | Toggle active ON + cek Schedule Trigger jam |
| GForm Reminder terus kirim padahal sudah isi form | `gform_filled` di STATS belum diisi Y | Sam isi manual kolom `gform_filled = Y` |
| Bot balas pesannya sendiri | Nomor di Chat Counter anti-loop salah | Update nomor WA device bot di Chat Counter |
| Credential error di Google Sheets | Token OAuth expired | Re-auth: n8n Settings → Credentials → reconnect |
| `Cannot read property of undefined` | Node sebelumnya return kosong | Trace di Executions, cek node yang return `[]` |

---

*VIRA Master Manual v3.0 — The Scholars Edition*
*Confidential — Steven Leroy | April 2026*
