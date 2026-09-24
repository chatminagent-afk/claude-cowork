# README Deploy — VIRA Persada Cisoka Residence (PCR)

**Tanggal:** 2026-07-15
**Isi:** 3 workflow n8n (JSON siap import) hasil perakitan terprogram dari VIRA V4 + lapisan config TEMPLATE.

| File | Workflow n8n | Trigger |
|------|--------------|---------|
| `2026-07-15-VIRA-PCR-main.json` | **VIRA-PCR Main** (71 node) | Webhook `POST /wa-inbound-pcr` |
| `2026-07-15-VIRA-PCR-buffer-cleanup.json` | **VIRA-PCR - MSG_BUFFER Cleanup** (4 node) | Schedule cron `0 3 * * *` |
| `2026-07-15-VIRA-PCR-error-notifier.json` | **VIRA-PCR Error Notifier** (3 node) | Error Trigger |

> Follow-Up (workflow #2 di blueprint) **belum** dirakit di batch ini — di luar scope brief (target Steven: "sampai notify tim lapangan jika tanggal survey sudah ditentukan"). Alur delegasi survey ke tim lapangan SUDAH ada di Main.

Skrip perakit rerunnable: `_extraction/build/assemble.py` (+ `codenodes.py`, `validate.py`). Jalankan `python assemble.py` lalu `python validate.py` untuk regenerasi.

---

## ⚠️ WAJIB DIBACA DULU — 1 kolom tambahan di STATS

Mekanisme **debounce 2-lapis** (prinsip pondasi #2) memakai satu kolom "baton" per user: `Update Buffer` menulisnya, `Re-Read STATS Debounce` membacanya, `IF_Chat_Debounce` membandingkannya dengan `process_start_ts`. Di V4 kolom ini bernama `timestamp` (legacy) — dan **tidak ada** di skema STATS final PCR.

**Keputusan:** kolom di-rename jadi `debounce_ts` (nama jelas, bukan legacy) dan **HARUS ditambahkan ke tab STATS** sebelum go-live. Tanpa kolom ini debounce tidak jalan (semua pesan lolos / balasan dobel).

➡️ **Tambahkan 1 kolom `debounce_ts` di tab STATS** (boleh di paling kanan). Ini satu-satunya deviasi skema; dilaporkan sesuai instruksi "jangan diam-diam menambah kolom".

Kolom lain 100% cocok dengan skema xlsx final. Kolom legacy V4 (`timestamp`, `pending_msg`, `user_status`, `kelas_anak*`, `program_interest`, `gform_*`) sudah dibuang total dari semua node.

---

## Urutan Import ke n8n

1. Import **`2026-07-15-VIRA-PCR-error-notifier.json`** dulu (biar dapat ID internal untuk di-set di Main).
2. Import **`2026-07-15-VIRA-PCR-buffer-cleanup.json`**.
3. Import **`2026-07-15-VIRA-PCR-main.json`**.

n8n akan generate `id`/`versionId` baru otomatis saat import (field ini sengaja tidak di-copy dari V4).

---

## Setup Credentials (3 buah)

Semua secret sudah dipindah ke Credentials/CONFIG — **tidak ada plaintext** di JSON.

### 1. Kirimi — `httpCustomAuth` (Generic Credential Type → Custom Auth)
- Semua node HTTP Kirimi memakai credential bernama placeholder **`Kirimi Custom Auth (REPLACE per client)`** (id `REPLACE_WITH_KIRIMI_CUSTOM_AUTH_CRED_ID`).
- Buat 1 credential **Custom Auth** berisi `user_code`, `secret`, `device_id` Kirimi PCR. Contoh isi JSON credential (body dikirim tiap request):
  ```json
  { "body": { "user_code": "PCR_USER_CODE", "secret": "PCR_SECRET", "device_id": "PCR_DEVICE_ID" } }
  ```
  (verifikasi format Custom Auth Kirimi 1x dengan test call — field nomor tujuan sudah dipastikan **`phone`**, kirim media pakai **`media_url`**.)
- Assign credential ini ke semua node Kirimi: `Reply Chat Kirimi`, `Send Media Kirimi`, `Notify Talk to Admin`, `Notify Field Team`, `Notify Admin Unknown`, `Notify Admin API Error`, `Notify Admin Media Error`, `Notify User Error`, `Reply Error`, dan `Notify Admin Error` (di Error Notifier).

### 2. Anthropic — `anthropicApi`
- Node `Anthropic Chat Model` (AI Agent) & `Anthropic Model Summarize` memakai placeholder **`Anthropic account PCR (REPLACE)`** (id `REPLACE_WITH_PCR_ANTHROPIC_CRED_ID`).
- Buat/assign credential Anthropic (boleh reuse akun lintas klien atau buat baru). Model default: `claude-sonnet-4-6`, `maxTokens 768` (Agent) / `400` (Summarize).

### 3. Google Sheets — `serviceAccount` (googleApi)
- Semua node Google Sheets memakai placeholder **`Google Service Account PCR (REPLACE)`** (id `REPLACE_WITH_PCR_GOOGLE_CRED_ID`).
- Buat service account credential dengan akses ke spreadsheet `Persada_Cisoka_Database`, lalu assign ke semua node Sheets.

---

## Isi Bootstrap Config (Sheet ID)

Di **VIRA-PCR Main**, buka node **`Bootstrap Config`** (Code), ganti:
```js
const SHEET_ID = 'PASTE_PCR_GOOGLE_SHEET_ID_HERE';   // <-- ganti dgn Sheet ID Persada_Cisoka_Database
```
Ini **satu-satunya titik edit Sheet ID** untuk Main (semua node Sheets baca lewat `$('Bootstrap Config').first().json.sheet_id`).

Untuk **Buffer Cleanup** & **Error Notifier**: keduanya tidak punya `Bootstrap Config`. Ganti manual placeholder di node-nya:
- Buffer Cleanup: 2 node Sheets, ganti `PASTE_PCR_GOOGLE_SHEET_ID_HERE` (documentId value) → Sheet ID asli.
- Error Notifier: node `Notify Admin Error`, ganti `{{ADMIN_PHONE}}` → nomor admin PCR format `628xxx` (Error Trigger tidak punya akses Parse Config, jadi hardcode/placeholder).

---

## Set Error Workflow (manual)

Di **VIRA-PCR Main** → menu ⋮ → **Settings → Error Workflow** → pilih **VIRA-PCR Error Notifier**. (Tidak otomatis; `settings.errorWorkflow` sengaja dikosongkan karena ID internal tidak portable antar-instance.)

## Set Webhook URL di Kirimi

Aktifkan (Activate) VIRA-PCR Main, salin **Production URL** node `Webhook` (path `/wa-inbound-pcr`), tempel di dashboard Kirimi sebagai webhook incoming message.

---

## Isi Tab CONFIG (key | value | keterangan)

Bot dikendalikan lewat tab CONFIG. Key yang dipakai node (nilai list ditulis sebagai **JSON string** di sel value):

| key | contoh value | keterangan |
|-----|--------------|------------|
| `client_name` | `Persada Cisoka Residence` | nama klien |
| `bot_name` | `VIRA` | |
| `admin_phone` | `628xxxxxxxxxx` | notif internal (unknown/error/talk-to-admin) |
| `admin_phone_display` | `0812-xxxx-xxxx` | nomor yang DITAMPILKAN ke user (call redirection) |
| `field_team_phone` | `["628aaa","628bbb"]` | JSON array; notif delegasi survey ke tim lapangan (boleh 1 nomor string biasa) |
| `survey_open_hour` / `survey_close_hour` | `8` / `17` | validasi jam survey (dipakai `validateSurveySlot`) |
| `survey_slots` | `["Sen-Jum 09-16","Sabtu 09-13"]` | slot yang ditawarkan AI |
| `lead_source_map` | `[{"source":"Instagram","keywords":["ig","instagram"]}]` | override deteksi sumber traffic (kosong = default hardcode) |
| `whitelist_enabled` | `TRUE` saat UAT, `FALSE` saat go-live | gate whitelist |
| `whitelist_numbers` | `["628xxx"]` | nomor UAT |
| `rate_limit_max` / `rate_limit_window_sec` / `debounce_seconds` | `5` / `60` / `60` | (nilai default sudah hardcode di node; CONFIG untuk dokumentasi) |
| `followup_*`, `media_catalog`, `brochure_url`, `system_prompt` | — | disiapkan untuk Follow-Up/media; opsional untuk Main v1 |

> `system_prompt` di CONFIG **tidak** dipakai Main — prompt telemarketer sudah ditanam langsung di `AI Agent.options.systemMessage`. Key tetap ada untuk kompatibilitas engine Parse Config.

---

## Isi Katalog Media (tab LINKS) + host brosur

Untuk fitur `[SEND_MEDIA]`: isi tab **LINKS** (`Nama Link` | `URL` | `Status` | `Deskripsi`). `Process All` resolve URL dari `Nama Link` (mis. key `brosur`, `siteplan`). Tambah kolom `Caption` bila mau caption khusus (fallback ke `Deskripsi`).
- Host file di URL **direct-download** (Google Drive `uc?export=download&id=...` untuk MVP, atau object storage). Verifikasi di incognito harus langsung unduh, bukan halaman preview.
- `Status` harus `Aktif` supaya ke-resolve.

---

## Langkah UAT (whitelist)

1. Set `whitelist_enabled = TRUE` dan `whitelist_numbers = ["<nomor tester>"]` di CONFIG.
2. Isi minimal tab PRODUK, LINGKUNGAN, FAQ, LINKS dengan data contoh.
3. Kirim WA dari nomor tester → cek balasan, cek row STATS/MSG_BUFFER terisi, cek debounce (kirim 2 pesan cepat → 1 balasan gabungan).
4. Uji `[SCHEDULE_SURVEY]`: minta jadwal survey → cek tab SURVEY terisi, STATS `survey_*` update, notif masuk ke `field_team_phone`, EVENTS `DELEGATED` tercatat.
5. Uji `[REQUEST_CALL]`, `[SEND_MEDIA]`, `[TALK_TO_ADMIN]` (bot_mode→OFF).
6. Setelah lolos: set `whitelist_enabled = FALSE` untuk publik.

---

## Placeholder yang WAJIB diganti sebelum go-live

| Placeholder | Lokasi | Ganti jadi |
|-------------|--------|-----------|
| `PASTE_PCR_GOOGLE_SHEET_ID_HERE` | Bootstrap Config (Main) + 2 node Buffer Cleanup | Sheet ID `Persada_Cisoka_Database` |
| `REPLACE_WITH_KIRIMI_CUSTOM_AUTH_CRED_ID` / `Kirimi Custom Auth (REPLACE per client)` | credential semua node Kirimi | credential Kirimi PCR |
| `REPLACE_WITH_PCR_ANTHROPIC_CRED_ID` / `Anthropic account PCR (REPLACE)` | 2 node Anthropic | credential Anthropic |
| `REPLACE_WITH_PCR_GOOGLE_CRED_ID` / `Google Service Account PCR (REPLACE)` | semua node Sheets | service account PCR |
| `{{ADMIN_PHONE}}` | Error Notifier → Notify Admin Error | nomor admin `628xxx` |
| 🚧/🔶 di system prompt | `AI Agent.systemMessage` | data produk & keputusan sapaan (lihat draft prompt) |
| kolom `debounce_ts` | tab STATS | **tambahkan kolomnya** (lihat atas) |

---

## Keputusan Perakitan (deviasi & catatan penting)

1. **Cabang GForm (7 node) DIBUANG** — `IF Send GForm`, `Query LINKS for GForm`, `Pick GForm Link`, `IF GForm Resolved`, `Send GForm Link`, `Send GForm Clarify`, `Update GForm Sent TS1`. Blueprint §10 + desain media (FILE 2) menggantikannya dengan cabang `[SEND_MEDIA]`. GForm tidak relevan properti.
2. **Tag legacy DIBUANG** dari Process All: `[MOCK_INTERVIEW_BOOKING]`, `[PENDAFTARAN]`, `[DATA_COMPLETE]` (relik alur beasiswa). Node `IF Status Update Needed`/`Update User Status` (TEMPLATE, alur PARENT/STUDENT) tidak diikutkan.
3. **`Delete_Pending_Msg*` DIPERTAHANKAN** (4 varian). Temuan ekstraksi: meski namanya "legacy", di V4 node ini menulis `buffer_done_ts` (watermark MSG_BUFFER — kolom VALID di skema baru) + `No WA` + `lid`, **bukan** kolom `pending_msg`. Jadi aman, hanya di-repoint ke sheet PCR.
4. **`timestamp` (baton debounce) → `debounce_ts`** — lihat peringatan di atas. Satu-satunya kolom yang perlu ditambah manual.
5. **Talk To Sam → Talk To Admin** — node `IF Talk To Admin`, `Notify Talk to Admin`; flag internal `isTalkToAdmin`; tag `[TALK_TO_ADMIN]`. Notif ke `admin_phone` dari CONFIG (bukan nomor Sam hardcode).
6. **Semua node Kirimi pakai pola `httpCustomAuth`** (dari TEMPLATE), bukan plaintext V4. Field nomor = `phone`; kirim media = `media_url` di endpoint send-message yang sama.
7. **Lapisan config depan**: `Webhook → Bootstrap Config → Read CONFIG → Parse Config → Whitelist Gate → If From Group → IF From Me → Chat Counter` (sesuai blueprint §10). `If From Group` disisipkan kembali (TEMPLATE tidak punya). `IF (Whitelist)` hardcode V4 digantikan `Whitelist Gate` config-driven.
8. **Vocab properti**: `Read PROGRAM Data → Read PRODUK Data`, `Read ABOUT Data → Read LINGKUNGAN Data`; Preprocess deteksi tipe unit/budget/KPR/lokasi/legalitas/survey; `[FACTS kelas]` → `[FACTS unit="..." budget="..."]` → persist ke `unit_interest`/`budget_range` (pola TTL 60 hari sama seperti `kelas_anak`).
9. **Detect Lead Source** (node baru, setelah Cek_user_status): rule-based, tulis sekali (`lead_source_final = existing || detected`, preserve first-touch), default `Organik`.
10. **Summarization handover**: node `Summarize Handover` = **Basic LLM Chain** (`chainLlm`, non-agent) + model `Anthropic Model Summarize`. Non-blocking (cabang survey paralel, `onError: continueRegularOutput`). `Format Handover Message` punya **fallback deterministik** (rangkai field STATS) bila LLM gagal/dinonaktifkan — sesuai desain FILE 3 §7. Loop `field_team_phone`: Format mengembalikan 1 item per nomor, `Notify Field Team` kirim per-item.
11. **`follow_up_count` reset dihapus** dari Update to STATS (V4 menulis `""` tiap balasan → akan mereset counter follow-up). Dibiarkan tidak disentuh Main; dikelola workflow Follow-Up nanti.
12. **maxTokens AI Agent 512 → 768** (antisipasi jawaban KPR lebih panjang, risiko #10 analis). `temperature 0.7` dipertahankan.

### Menunggu data klien (jangan go-live sebelum diisi)
Data unit/harga/KPR (PRODUK), profil lokasi/legalitas (LINGKUNGAN), FAQ, nomor admin & tim lapangan, slot survey, file brosur, dan keputusan register sapaan (🚧 default "Kak" di prompt) — lihat blueprint §11 & draft system prompt.
