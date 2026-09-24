# Panduan Deploy VIRA Personal — 2026-08-28

Urutan kerja: **sheet → dokumen → nomor Kirimi → n8n**. Bagian A–C persiapan, Bagian D urutan deploy sebenarnya.

---

## 0. File yang sudah disiapkan

Di `VIRA Steven\workflow\` (file `2026-08-15-*` lama tidak disentuh):

| File | Status |
|---|---|
| `2026-08-28-VIRA-Personal-Main.json` | siap import — 100 node |
| `2026-08-28-VIRA-Personal-Error-Notifier.json` | siap import — 5→**8 node**, +rantai fallback email |
| `2026-08-28-VIRA-Personal-STATS-Cleanup.json` | siap import — **BARU**, sebelumnya tidak ada |
| `2026-08-28-VIRA-Personal-Followup.json` | siap import |
| `2026-08-28-VIRA-Personal-Buffer-Cleanup.json` | **JANGAN IMPORT** — diganti job di GLOBAL Sheet Cleanup |

Ikut di-patch: `GLOBAL-Sheet-Cleanup.json` (+job harian MSG_BUFFER & kuartalan DASH_AUDIT), `GLOBAL - Email Fallback Notifier.json` (kenali tenant `VIRA-PERSONAL`), `tenants.js` + `VIRA-Dashboard-API.json` (tenant `personal`; backup `tenants.js.bak-2026-08-28`).

**Kredensial:** 28 node Sheets → `Google Service Account - VIRA Dashboard`.
**Tidak ada node Google Drive** di seluruh workflow VIRA — media diambil HTTP Request polos. Jadi tidak ada kredensial Drive; yang berlaku setelan **share** file (Bagian A).

---

## A. 5 dokumen Drive yang harus dibuat

**Kenapa:** 5 baris tab LINKS sekarang semuanya menunjuk **file Drive yang sama persis**. Kalau tidak diganti, VIRA mengirim file yang salah ke lima permintaan berbeda.

| Nama Link | Tipe | Isi | Catatan |
|---|---|---|---|
| `company-profile` | PDF | Profil singkat Steven & VIRA | — |
| `deck-vira` | PDF | Deck VIRA versi umum | Bukan deck khusus klien |
| `demo-video` | MP4 | Cara VIRA bekerja | **Environment dummy, bukan data klien** |
| `portfolio` | JPG/PNG | Contoh sistem yang dibangun | **Blur/de-branded** — tanpa nama klien, no WA, chat asli |
| `harga-ringkas` | JPG/PNG | Tabel Basic vs Premium | Angka harus sinkron dengan CONFIG (3jt / 5jt) |
| `instagram` | — | `instagram.com/povstevens` | Sudah benar |

Jalankan `/privacy-check` sebelum upload `demo-video` dan `portfolio`.

**Langkah:**
1. Upload ke Drive → **share `Anyone with the link` → `Viewer`**. Wajib: `Download Media` adalah HTTP polos tanpa kredensial, file private = gagal senyap.
2. Ambil `FILE_ID` dari `drive.google.com/file/d/`**`FILE_ID`**`/view`.
3. Tulis ke kolom `URL` tab LINKS: `https://drive.google.com/uc?export=download&id=FILE_ID`
   Node `Process All` otomatis mengonversinya agar file besar tidak nyangkut di halaman virus-scan.
4. Ubah `Status` → `Aktif`.

**Uji:** minta kelimanya lewat chat — harus mengirim file yang **berbeda**.

---

## B. Import 3 CSV

Di `VIRA Steven\sheet\2026-08-28-import\`. Baris 1 sudah berisi nama kolom persis agar terbaca n8n.

Cara: **File → Import → Upload → Replace current sheet → Comma**.
Jangan pilih "Create new sheet" — n8n akan membaca tab lama.

| File | Tab | Isi |
|---|---|---|
| `DASH_AUDIT.csv` | **DASH_AUDIT** (buat tab kosong dulu) | Header saja |
| `CONFIG.csv` | CONFIG | 51 key |
| `LINKS.csv` | LINKS | 6 baris |

**JANGAN import ulang STATS, REQUESTS, MSG_BUFFER, EVENTS, UNKNOWN** — ada data lead sungguhan.

**CONFIG.csv:** +`katalog_cache_minutes`(10), +`stats_retention_days`(90), +`stats_purge_dry_run`(Y); −`sheet_id` (isinya angka, tidak dibaca node mana pun); 4 kredensial Kirimi → `ISI MANUAL - ...`. String `"ISI MANUAL"` **dikenali kode** Error Notifier dan memicu peringatan kalau lupa diisi.

**LINKS.csv:** 5 URL placeholder dikosongkan, `Status` → `Draft`. Sengaja — `Rakit Konteks` pakai `aktif() = /^(aktif|active|on|ya|yes)$/i`, jadi `Draft` membuat baris itu tak masuk konteks AI Agent. Lebih baik VIRA diam soal deck daripada mengirim file yang salah.

---

## C. ⚠️ Ganti nomor Kirimi

Kredensial Kirimi disimpan di **tab CONFIG**, bukan credential n8n — ganti di satu tempat sudah mengurus Main, Follow-up, Error Notifier, dan STATS Cleanup sekaligus.

| Key | Baris |
|---|---|
| `bot_wa_number` | **7** |
| `kirimi_user_code` | **10** |
| `kirimi_secret` | **11** |
| `kirimi_device_id` | **12** |

Nomor baris sudah bergeser dari checklist `2026-08-16` (yang menyebut B11/B12) — pakai yang ini.

- `admin_phone` (baris 8) = nomor HP-mu penerima notifikasi. **Jangan** ikut diganti.
- Arahkan webhook Kirimi ke `https://n8n.srv1270416.hstgr.cloud/webhook/wa-inbound-steven` — jangan tertukar dengan `wa-inbound` (TS) atau `wa-inbound-pcr` (Persada).
- `user_code` `KM40LI0426` saat ini dipakai bersama The Scholars. Kalau nomor baru pakai akun Kirimi yang sama, cukup `device_id` yang beda.

---

## D. Urutan deploy n8n

**1. Share spreadsheet ke service account** (Editor). Verifikasi email SA di n8n → Credentials → `Google Service Account - VIRA Dashboard`. Tanpa ini semua node Sheets kena 403.

**2. Import Error Notifier** → cek node `Call Global Email Fallback` benar-benar menunjuk "GLOBAL - Email Fallback Notifier" → aktifkan.

**3. Import Main** → **Settings → Error Workflow = `VIRA Personal — Error Notifier`**. Field ini sengaja dikosongkan di JSON; sebelumnya berisi placeholder invalid, artinya error Main **tidak pernah** dinotifikasi. Jangan aktifkan dulu.

**4. Import STATS Cleanup** → set Error Workflow → klik **Test manual** (dry run, tidak menghapus apa pun) → cocokkan angkanya dengan isi STATS → baru aktifkan jadwal.
Cron `30 2 1 1,4,7,10 *` = 1 Jan/Apr/Jul/Okt 02:30 WIB — **bukan** "tiap 3 bulan dari sekarang".

**5. MSG_BUFFER** → jangan import Buffer-Cleanup. Import GLOBAL Sheet Cleanup → **Test manual** harus melaporkan **3 job harian** (TS, Persada, Personal) → kalau angkanya masuk akal, nonaktifkan 3 cleanup lama lalu aktifkan yang baru.
Ini menyentuh produksi TS & Persada. Kalau belum mau: import Buffer-Cleanup Personal dan tunda migrasi — **jangan aktifkan dua-duanya** untuk tab yang sama.

**6. Update GLOBAL Email Fallback** — perubahannya cuma 2 baris, boleh diedit manual di UI:
```js
else if (hay.includes('personal') || hay.includes('steven')) tenant = 'VIRA-PERSONAL';
```

> ⚠️ **Jangan sentuh kredensial node `Kirim Email (Gmail)`.** Dia harus tetap `Gmail account` (OAuth2, `hC4iEn4w0FA6Tmxd`). Lihat Troubleshooting di bawah.

**7. Uji Main** → pastikan A/B/C beres → chat dari nomor lain, cek Executions → **uji error notifier dengan sengaja**: matikan sementara sharing spreadsheet, kirim chat, harus ada WA error masuk, lalu kembalikan → baru aktifkan Main.

**8. Follow-up** paling akhir. Biarkan `followup_enabled = false` sampai Main stabil beberapa hari.

---

## E. VIRA Personal di Dashboard

**Sudah diubah:** entri tenant `personal` di `tenants.js`; akun super `steven` diberi akses (**tanpa akun/password baru**); `VIRA-Dashboard-API.json` sudah di-rebuild (30 node).

**Yang tampil:** KPI *Deck Diminta* + *Brief Masuk*; tabel *Brief Deck Masuk* (REQUESTS) + *Log Aktivitas* (EVENTS); distribusi *Paket Diminati* & *Sumber Traffic*.

**Deploy:**
1. Buat tab `DASH_AUDIT` + import CSV (Bagian B). Kalau tab ini tidak ada, toggle bot tetap jalan — cuma tidak tercatat siapa yang mengubah.
2. Spreadsheet sudah di-share **Editor** (sama dengan D.1 — toggle perlu menulis).
3. Import ulang `VIRA-Dashboard-API.json` **ke project `sXUEZy1FQDksvKLg`**. Salah project = node Sheets tidak menemukan credential meski ID benar.
4. Verifikasi 4 node Sheets (`Read Tab`, `Read STATS for Toggle`, `Update Bot Mode`, `Append Audit`) pakai SA VIRA Dashboard.
5. **Smoke test toggle** (paling kritis menurut runbook-mu): catat posisi baris di STATS, matikan bot 1 nomor uji lewat dashboard, lalu buka spreadsheet dan pastikan **baris yang berubah memang baris itu**.

**⚠️ Efek samping:** workflow Dashboard yang live sekarang dibangun dari `tenants.js` **sebelum** field `logo` ada. Import ulang ini tidak cuma menambah tenant — dia sekaligus menaikkan fitur logo, sehingga **logo The Scholars akan mulai tampil** di dashboard mereka. Kosmetik, tapi menyentuh klien yang sedang jalan. Sisanya identik byte-per-byte.

**Cleanup DASH_AUDIT:** job kuartalan `personal` sudah ada di GLOBAL Sheet Cleanup. Kalau belum migrasi (D.5), tambahkan ke `Fan Out Tenants` workflow lama — **jangan di dua-duanya**, nanti dobel hapus.

---

## F. Sengaja belum dikerjakan

| Hal | Kenapa |
|---|---|
| **Topic Harvester + Monthly Rollup** | Analitik topik; TS punya, Persada tidak. Kemungkinan tak perlu untuk bot pribadi |
| **Migrasi ke GLOBAL - VIRA Error Notifier** | Kamu pilih rebuild notifier sendiri. Gabungkan nanti setelah Personal stabil |
| **Rotasi secret Kirimi** | Prioritas #1 auditmu. Paling enak sekalian saat ganti nomor baru |

---

## Checklist

```
SHEET
[ ] Share VIRA Steven Database ke service account (Editor)
[ ] Buat tab kosong DASH_AUDIT, lalu import DASH_AUDIT.csv
[ ] Import CONFIG.csv        (Replace current sheet)
[ ] Import LINKS.csv         (Replace current sheet)

DOKUMEN
[ ] Buat 5 dokumen Drive + set "Anyone with the link"
[ ] Jalankan /privacy-check untuk demo-video & portfolio
[ ] Isi kolom URL di LINKS, ubah Status Draft -> Aktif

NOMOR KIRIMI
[ ] Beli nomor baru + buat device di Kirimi
[ ] Isi CONFIG baris 7 / 10 / 11 / 12 (ganti semua "ISI MANUAL")
[ ] Arahkan webhook Kirimi ke wa-inbound-steven

N8N — WORKFLOW BOT
[ ] Import Error Notifier -> aktifkan
[ ] Import Main -> set Error Workflow -> JANGAN aktifkan dulu
[ ] Import STATS Cleanup -> set Error Workflow -> Test manual (dry run)
[ ] Import GLOBAL Sheet Cleanup -> dry run -> tukar dengan 3 cleanup lama
[ ] Update GLOBAL Email Fallback (deteksi VIRA-PERSONAL)

N8N — DASHBOARD
[ ] Import ulang VIRA-Dashboard-API.json ke project sXUEZy1FQDksvKLg
[ ] Verifikasi 4 node Sheets pakai SA VIRA Dashboard
[ ] Smoke test toggle: pastikan baris yang berubah memang baris yang benar

UJI & AKTIFKAN
[ ] Uji error notifier dengan sengaja bikin gagal
[ ] Aktifkan Main
[ ] Follow-up terakhir, setelah Main stabil
```

---

## Troubleshooting

### Gmail: `400 FAILED_PRECONDITION` / "Precondition check failed"

**Penyebab:** node `Kirim Email (Gmail)` dipasangi kredensial **service account**.

Service account **tidak punya mailbox**. Dia bisa baca/tulis Google Sheets (resource yang bisa di-share ke dia), tapi tidak bisa menjadi pengirim email. Satu-satunya cara service account mengirim Gmail adalah **domain-wide delegation** — fitur admin **Google Workspace**. Akun `stevenleroy0@gmail.com` / `chatminagent@gmail.com` keduanya Gmail konsumen, jadi jalur itu memang tertutup, bukan sekadar setting yang belum ketemu.

**Perbaikan:** node `Kirim Email (Gmail)` → Credential → kembalikan ke **`Gmail account`** (gmailOAuth2, `hC4iEn4w0FA6Tmxd`). Import ulang `GLOBAL - Email Fallback Notifier.json` juga mengembalikannya.

Masih gagal? → buka credential `Gmail account` → **Reconnect** (token OAuth bisa kedaluwarsa/dicabut) → pastikan Gmail API aktif di GCP project.

### Gmail: `403 PERMISSION_DENIED` / "Project #… has been deleted"

**Penyebab:** credential `Gmail account` memakai OAuth Client dari GCP project yang sudah dihapus. Bukan akun Gmail-nya yang bermasalah.

Kejadian 2026-08-29: project `#673938546771` — ternyata project **TIM Interior** (lihat `TIM Interior\v4\2026-06-13-catatan-v4.md`), bukan project VIRA. Konsekuensi lain: **TIM Interior v4 kemungkinan ikut mati** karena catatan itu menyebut project yang sama untuk kuota Sheets-nya.

**Perbaikan — buat OAuth Client baru:**

1. Pakai project yang hidup, disarankan **`vira-506713`** (tempat service account VIRA) supaya cuma 1 project GCP yang perlu dijaga.
2. **APIs & Services → Library** → `Gmail API` → **Enable**.
3. **Google Auth Platform → Branding** — isi semuanya, lalu Save:
   - App name, User support email, Developer contact information
   - **Application home page / privacy policy / terms of service** — ketiganya boleh diisi URL yang sama: `https://srv1270416.hstgr.cloud`
     Ini yang memblokir tombol Publish 2026-08-29. Sebabnya: domain redirect URI **otomatis** masuk ke Authorized domains saat OAuth Client dibuat, dan begitu Authorized domain terisi, bagian App domain jadi wajib.
   - **Jangan upload App logo** — logo memaksa app masuk jalur verifikasi.
4. **Google Auth Platform → Data Access** → Add or remove scopes → centang `.../auth/gmail.send` → Update → Save.
5. **Google Auth Platform → Audience** → **PUBLISH APP** → status jadi **In production**.
   ⚠️ **Wajib.** Selama status **Testing**, refresh token untuk restricted scope (`gmail.send`) **kedaluwarsa tiap 7 hari** — jalur alert terakhir akan mati diam-diam seminggu sekali.
   Setelah publish akan muncul banner *"Your app requires verification"*. **Abaikan — jangan submit for review.** Verifikasi hanya untuk menghilangkan layar "unverified app" dan melewati batas 100 user; penggunanya cuma 1. Juga **jangan klik "Back to testing"**.
   Saat login nanti muncul "Google hasn't verified this app" → **Advanced → Go to (unsafe)**. Itu wajar, bukan tanda ada yang salah.
6. **Credentials → Create Credentials → OAuth client ID → Web application.**
   Authorized redirect URI: **copy persis dari field "OAuth Redirect URL"** di credential `Gmail account` n8n — beda satu karakter = `redirect_uri_mismatch`.
   Biasanya `https://n8n.srv1270416.hstgr.cloud/rest/oauth2-credential/callback`.
7. n8n → Credentials → `Gmail account` → tempel Client ID + Secret → **Sign in with Google** → Allow.
8. Uji ulang. Masih 403 dengan nomor project lama = Client ID baru belum tersimpan.

**Cek terkait:** pastikan project yang terhapus bukan project service account VIRA. Buka node Google Sheets mana pun di TS/Persada → **Execute step**. Keluar baris = `vira-506713` aman.

### Catatan desain

Jalur email fallback ini adalah **alert terakhir**, tapi bergantung pada OAuth app di GCP project yang bisa dihapus dan token yang bisa kedaluwarsa — dua kegagalan dalam sehari (2026-08-29) berasal dari situ.

Alternatif yang lebih tahan banting kalau nanti mau: node `CADANGAN - Brevo` / `CADANGAN - Resend` sudah ada di kanvas (disabled, API key masih `GANTI_...`). Keduanya cuma butuh API key — tanpa OAuth, tanpa GCP project, tanpa masa berlaku. Payloadnya (`$json.subject/html/text`) sudah cocok dengan output `Normalize & Compose Email`, jadi tinggal disambung.

### Batas penggantian kredensial

Penggantian ke `Google Service Account - VIRA Dashboard` berlaku **hanya untuk node Google Sheets** (28 node di 4 workflow). Gmail API beda aturan main.

Di seluruh workflow VIRA cuma ada **1 node email yang live**: `Kirim Email (Gmail)` di GLOBAL - Email Fallback Notifier. Sisanya draft/arsip.

Kalau nanti mau lepas dari Gmail OAuth: di kanvas itu sudah ada `CADANGAN - Brevo` dan `CADANGAN - Resend` (disabled, belum tersambung, API key masih `GANTI_...`) — keduanya pakai API key biasa yang tidak bisa kedaluwarsa seperti OAuth.

---

## Status QA

Sudah diverifikasi otomatis: logika `Plan Purge` **13/13** kasus batas + **2000/2000** fuzz · gerbang QA Dashboard **24/24** · nama kolom tenant `personal` **39 cocok, 0 salah** · struktur 7 workflow + bentuk node dicocokkan ke node produksi yang sudah jalan.

**Belum diuji, dan tidak bisa tanpa n8n hidup:** belum ada node yang benar-benar dieksekusi · rantai fallback Error Notifier (wiring identik dengan TS, tapi identik ≠ teruji) · akses service account · Main 100 node (hanya kredensial + `Bootstrap Config` yang disentuh).

**Gerbang UAT sebenarnya ada di 3 langkah:** Test manual STATS Cleanup (D.4) · uji error notifier dengan sengaja bikin gagal (D.7) · smoke test toggle dashboard (E.5).
