# Analisis Arsitektur VIRA Eksisting — untuk Remake Persada Cisoka Residence

**Tanggal:** 2026-07-15
**Sifat dokumen:** analisis read-only atas file production VIRA (The Scholars). Tidak ada perubahan pada file workflow manapun.
**File yang dianalisis (path absolut):**
1. `D:\Documents\Claude Cowork\the scholars\report\production\VIRA V4.json` — **workflow LIVE saat ini** (59 node, `active: true`)
2. `D:\Documents\Claude Cowork\the scholars\mass production\VIRA_TEMPLATE_v1.json` — template mass-production (59 node, `active: false`, tertanggal 25 Jun — **lebih tua dari V4**)
3. `D:\Documents\Claude Cowork\the scholars\mass production\2026-06-25-VIRA-onboarding-klien-baru.md`
4. `D:\Documents\Claude Cowork\the scholars\archive\vira\VIRA\VIRA_Follow_Up.json` (16 node, tertanggal 6 Mei — file lama)
5. `D:\Documents\Claude Cowork\the scholars\archive\vira\VIRA\VIRA_SystemPrompt_v8.md` (**stale**, lihat temuan §4)
6. `D:\Documents\Claude Cowork\the scholars\archive\2026-06-25-analisa-arsitektur-vira\2026-06-25-analisa-arsitektur-vira-v3.1.md` (analisis V3.1, dipakai untuk orientasi)
7. `D:\Documents\Claude Cowork\the scholars\report\production\2026-07-03-VIRA_MSG_BUFFER-cleanup.json`
8. `D:\Documents\Claude Cowork\the scholars\report\production\2026-07-02-VIRA_V4-error-workflow.json`
9. `D:\Documents\Claude Cowork\the scholars\report\patch\V4 Fable\2026-07-02-VIRA_V4-changelog.md`

---

## 1. Ringkasan Arsitektur VIRA V4 (alur end-to-end)

VIRA V4 terdiri dari **1 workflow utama (59 node)** + **2 workflow pendukung terpisah** yang harus di-deploy sendiri-sendiri di n8n:

- **VIRA V4** (workflow utama, webhook `POST /wa-inbound`)
- **VIRA Error Notifier** (Error Workflow — harus di-set manual di *Settings → Error Workflow* milik VIRA V4, tidak otomatis)
- **VIRA - MSG_BUFFER Cleanup** (scheduled trigger harian 03:00 WIB, housekeeping)

Plus **1 workflow lama yang terpisah dan berpotensi stale**: `VIRA_Follow_Up.json` (lihat catatan risiko §7).

### Alur pesan masuk (VIRA V4)

```
Webhook (POST wa-inbound)
 → If From Group (buang pesan dari grup WA)
 → IF From Me (buang pesan dari nomor bot sendiri)
 → IF (Whitelist)  ⚠️ OR dari 5 nomor hardcoded — MASIH ADA di V4 production
 → Chat Counter (parse payload Kirimi; filter hanya messageType="text" non-kosong;
                 hitung process_start_ts = Date.now())
 → Read User STATS (baca semua baris STATS)
 → Resolve User Row (★ node baru V4 — resolusi identitas No WA primer/lid backup,
                      TANPA fallback rows[0]; throw kalau identitas kosong → ditangkap
                      Error Workflow)
 → IF Bot Mode Active (bot_mode != 'OFF'?)
     ├─ OFF → Delete_Pending_Msg_Bot_Off (majukan watermark) → STOP (Sam manual)
     └─ ON  → Rate Limiter LID (maks 5 pesan/menit/user, via $getWorkflowStaticData)
           → Append MSG_BUFFER (★ append-only, 1 row per pesan masuk — anti lost-update)
                [gagal append → Notify User Error]
           → Update Buffer (tulis STATS.timestamp = process_start_ts, key=No WA)
           → Read STATS for HITL → HITL Check (cek ulang bot_mode)
           → Wait3 (FIXED 60 detik — debounce multi-bubble)
           → Re-Read STATS Debounce
           → IF_Chat_Debounce (STATS.timestamp masih == process_start_ts milikku?)
               ├─ tidak (bubble lebih baru menyusul) → STOP diam-diam (pesan TETAP
               │    aman karena sudah ada di MSG_BUFFER, akan digabung oleh run pemenang)
               └─ ya (aku pemenang debounce) → Read MSG_BUFFER
                   → Cek_user_status (cek ulang bot_mode post-wait; gabung SEMUA pesan
                     MSG_BUFFER antara watermark buffer_done_ts s.d. process_start_ts-ku,
                     buang yang >30 menit basi; tentukan IS_NEW_USER dari greeting_sent;
                     suntik fakta persisten kelas_anak/program_interest dgn TTL 60 hari)
                   → Preprocess - Context Detection (NLU regex: deteksi kelas/program
                     multi-value, intent daftar, out-of-scope, mode persuasi, topik)
                   → Read FAQ → Read PROGRAM Data → Read ABOUT Data → Read LINKS Data
                   → FAQ Retrieve (rakit data_context dari PROGRAM/ABOUT/LINKS secara
                     kondisional + retrieval FAQ lexical/TF-IDF custom dgn sinonim &
                     stemming Bahasa Indonesia)
                   → AI Agent (Claude Sonnet 4.6, systemMessage ~9rb kata, maxTokens 512,
                     temp 0.7, Simple Memory window 10 keyed by resolved_key)
                       ├─ error → Reply Error (pesan fallback generik)
                       │           → Delete_Pending_Msg_Bot_Off1 (majukan watermark)
                       └─ ok → Process All (parse tag [SEND_GFORM]/[TALK_TO_SAM]/
                                [UNKNOWN]/[FACTS kelas="..."], fallback pattern-matching
                                kalau AI lupa tag, filter anti-bocor-proses-internal
                                dgn guard anti-kosong, bersihkan markdown, inject URL
                                GForm inline, merge kelas_anak union+TTL)
                           → 4 cabang paralel:
                              1. IF Send GForm → Query LINKS → Pick GForm Link →
                                 IF GForm Resolved → Send GForm Link / Send GForm Clarify
                              2. IF Unknown → Record to UNKNOWN (sheet) → Wait2 (5-10s)
                                 → Notify Admin Unknown (WA ke admin hardcoded)
                              3. Wait1 (5-10s random, SELALU jalan) → Reply Chat Kirimi
                                 (balasan utama) → Check API Response
                                   ├─ gagal → Notify Admin API Error
                                   └─ ok → 3 cabang: Extract & Prepare Data → Read STATS
                                       → Process Counter & Merge Data → Update to STATS
                                       (tulis Nama/Counter/tanggal/kelas_anak/
                                       program_interest/bot_mode/last_reply_ts) DAN
                                       Delete_Pending_Msg (majukan watermark) DAN
                                       Update STATS - Greeting Flag → IF Update Greeting
                                       → Update Greeting (set greeting_sent=Y)
                              4. IF Talk To Sam → Notify Talk to Sam (WA ke admin) →
                                 Update row in sheet (set bot_mode=OFF → HITL aktif)
```

**Workflow pendukung:**
- **VIRA Error Notifier** (3 node): `Error Trigger → Compose Notif → Notify Admin Error`. Menangkap SEMUA exception tak tertangani di VIRA V4 (termasuk `throw` di `Resolve User Row`) dan WA-notify admin — mencegah eksekusi mati diam-diam tanpa balasan ke user maupun notifikasi ke siapa pun.
- **VIRA - MSG_BUFFER Cleanup** (3 node, cron `0 3 * * *`): karena `MSG_BUFFER` append-only terus tumbuh, job ini menghapus baris >2 jam. Karena append-only, baris basi SELALU jadi blok kontigu di atas (ts naik seiring nomor baris) — jadi cukup 1x hapus range, hemat kuota API.

---

## 2. Struktur Data Google Sheets

Satu spreadsheet `The_Scholars_Database` (`1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE`) menaungi hampir semua tab:

### Tab `STATS` — state per user (baris = 1 user, key match = kolom `No WA`)
| Kolom | Fungsi | Catatan |
|---|---|---|
| `No WA` | primary key (matchingColumns semua node write) | nomor telepon digit-only, hasil `resolved_key` |
| `bot_mode` | `ON`/`OFF` — toggle HITL | `OFF` = Sam pegang manual |
| `Tanggal Chat Pertama`, `Tanggal Chat Terakhir`, `Jam Chat Terakhir` | metadata aktivitas | ditulis oleh `Update to STATS` pasca-reply |
| `Nama` | nama user dari payload Kirimi | |
| `Pesan Pertama` | pesan pertama user, tidak pernah ditimpa | |
| `Counter`, `Intensitas Chat` | penghitung pesan | |
| `timestamp` | **LEGACY** — dulu kunci debounce, **V4 SUDAH BERHENTI MENULIS kolom ini** (fix kritis, lihat §7) | jangan dipakai lagi kecuali sudah dimigrasi |
| `last follow up`, `follow_up_count` | dipakai `VIRA_Follow_Up` workflow | |
| `gform_sent_ts`, `gform_filled` | tracking link form terkirim/terisi | |
| `user_status` | **LEGACY/arsip** — flow PARENT/STUDENT sudah dihapus di V4, kolom dibiarkan tapi tidak dibaca/ditulis lagi | |
| `greeting_sent` | `Y`/kosong — sudah dapat intro user-baru? | |
| `pending_msg` | **LEGACY** — digantikan `MSG_BUFFER` (append-only) | |
| `lid` | WhatsApp LID (identitas backup) | |
| `kelas_anak`, `kelas_anak_ts` | fakta persisten (kelas calon murid), TTL 60 hari via `_ts` | multi-value, dipisah koma |
| `program_interest` | program hasil derivasi dari `kelas_anak` | |
| `buffer_done_ts` | watermark MSG_BUFFER (unix ms) — bukan waktu balas, tapi "sudah dikonsumsi sampai sini" | |
| `last_reply_ts` | unix detik, waktu balasan sukses terkirim — **pengganti semantik `timestamp` lama** | |

### Tab `MSG_BUFFER` — log append-only (★ baru di V4)
Kolom: `no_wa`, `lid`, `message`, `ts` (unix ms). Setiap bubble masuk = 1 row baru (tidak pernah update in-place). Dibersihkan harian oleh workflow cleanup terpisah (retensi 2 jam).

### Tab `UNKNOWN` — log pertanyaan tak terjawab
Kolom: `Pertanyaan`, `User`, `Tanggal`, `message` (balasan bot yang dikirim, biasanya teks "belum ada infonya").

### Tab `FAQ` — knowledge base tanya-jawab
Kolom: `Pertanyaan`, `Jawaban`, `Kategori` (dipakai untuk boost skor retrieval per topik).

### Tab `PROGRAM` — knowledge base superset (harga, batch, status, syarat, deskripsi)
Kolom yang dibaca via helper `val()` di node `FAQ Retrieve`: `Nama Program`, `Status`, `Nama Batch`, `Tanggal Mulai`, `Deadline Daftar`, `Kuota`, `Harga`, `Pembayaran`, `Catatan`, `Syarat Umum`, `Dokumen yang Perlu Disiapkan`/`Dokumen`, `Deskripsi`, `Target Peserta`, `Durasi`, `Format`.

### Tab `ABOUT_SAM` — bio/profil
Kolom: `Aspek`, `Detail`.

### Tab `LINKS` — registry URL (form pendaftaran, channel WA, dll)
Kolom: `Nama Link`, `Deskripsi`, `Status` (Aktif/Active/On/Ya), `URL`. AI memilih baris via nama link persis (tidak boleh hardcode URL di prompt) — pola data-driven yang bagus, layak dipertahankan.

### Tab `CONFIG` — **HANYA ADA di TEMPLATE, TIDAK ADA di V4 production**
Key-value: `client_name`, `system_prompt`, `status_question`, `admin_phone`, `bot_language`, `whitelist_enabled`, `whitelist_numbers` (JSON array dalam 1 sel), `rate_limit_max`, `rate_limit_window_sec`, `debounce_seconds`, berbagai `*_keywords` (JSON array), `grade_program_map` (JSON array of object). Lihat §5 untuk kenapa ini penting tapi belum sinkron dengan V4.

Sheet terpisah lain: `VIRA_Follow_Up.json` membaca tab `MOCK_INTERVIEW_BOOKING` dari **spreadsheet ID lain** (`16g6FVOqkiHEtrhnXqpAoC-Ter3lsrayjet2Th0NAwD4`) — koneksinya ke alur utama hanya sebagai trigger-chain, datanya sendiri tampak tidak dipakai langsung oleh node `Filter` (kemungkinan sisa/vestigial, perlu diverifikasi sebelum di-reuse).

---

## 3. Mekanisme Penting

### Debounce & buffering multi-bubble (2 lapis, ★ redesain besar di V4)
- **Lapis 1 (baton race):** setiap bubble menulis `STATS.timestamp = process_start_ts` miliknya sendiri. Setelah `Wait3` (60 detik tetap, bukan rolling), workflow re-read dan hanya bubble yang timestamp-nya **masih** sama dengan `STATS.timestamp` saat itu yang lanjut — bubble-bubble lain (yang timestamp-nya sudah ditimpa bubble berikutnya) berhenti diam-diam. Ini menentukan **siapa yang memproses**, bukan **apa yang diproses**.
- **Lapis 2 (isi pesan): `MSG_BUFFER` append-only.** Setiap bubble SELALU tersimpan sebagai row baru terlepas dari siapa yang menang race. Bubble pemenang membaca semua row antara watermark `buffer_done_ts` dan `process_start_ts` miliknya, gabung berurutan jadi satu teks — jadi walau ada 5 bubble cepat, isi ke-5-nya tetap terbawa ke AI meski hanya 1 eksekusi yang benar-benar memanggil model.
- Ini memperbaiki bug V3 fatal: read-modify-write pada satu sel `pending_msg` yang rawan saling menimpa antar-bubble paralel (pesan hilang).

### HITL (Human-in-the-loop)
`bot_mode` (`STATS`) dicek **3 kali** di titik berbeda: (1) segera setelah resolusi identitas — sebelum buffering, (2) setelah buffer ditulis, sebelum `Wait3`, (3) setelah `Wait3` selesai (`Cek_user_status`) — karena Sam bisa mematikan bot kapan saja selama jeda 60 detik. `[TALK_TO_SAM]` dari AI otomatis men-set `bot_mode=OFF` (node `Update row in sheet`).

### Identitas user — prinsip "No WA primer, lid backup"
Node `Resolve User Row` (★ baru V4) adalah SATU-SATUNYA titik resolusi identitas per eksekusi, dipakai ulang (`$('Resolve User Row').first().json.resolved_key`) oleh semua node Sheets berikutnya. Urutan match: (1) `No WA` == nomor telepon, (2) kolom `lid` == LID, (3) `No WA` == LID (row lama peninggalan sebelum migrasi LID). **Tidak ada fallback ke `rows[0]`**, dan tidak match dengan kunci kosong. Kalau `phone` dan `lid` sama-sama kosong → `throw Error` (ditangkap Error Workflow, admin dinotif) — desain sengaja: lebih baik gagal jelas daripada menebak lalu menimpa data user lain (ini persis kasus produksi "Vivipoh/DSS" yang memicu fix ini).

### Error handling
- Lokal per titik gagal: `Reply Error` (AI Agent error), `Notify User Error` (append MSG_BUFFER gagal), `Notify Admin API Error` (Kirimi API gagal saat balas).
- Global: workflow terpisah `VIRA Error Notifier` — **harus di-set manual** sebagai *Error Workflow* di Settings VIRA V4 (tidak otomatis hanya karena file-nya ada). Menangkap exception apa pun yang lolos dari semua guard di atas, termasuk `throw` di `Resolve User Row`.

### Follow-up
Workflow terpisah `VIRA_Follow_Up.json` (16 node), trigger harian jam 10:00 WIB, maksimum 3x follow-up per user dengan aturan jeda 24 jam (general) / 48 jam antar follow-up umum, plus jalur khusus "GForm belum diisi" (24 jam–7 hari setelah link dikirim). **Risiko:** node `Filter` membaca kolom `STATS.timestamp` sebagai penanda "aktivitas terakhir" — padahal V4 changelog secara eksplisit menyatakan `Update to STATS` **berhenti menulis** kolom itu dan menyarankan redirect ke `last_reply_ts`. Workflow follow-up ini **belum dipatch** mengikuti perubahan itu (lihat §7).

---

## 4. System Prompt & Persona

Persona di-encode **seluruhnya** di satu field: `parameters.options.systemMessage` pada node `AI Agent` (n8n expression, ~9.000 kata). Isinya campuran:

**Client-specific (100% harus ditulis ulang untuk Persada Cisoka):**
- Identitas "Sam" (nama, peran founder The Scholars) dan kalimat intro user-baru verbatim ("Haloo thank you sudah contact TheScholars.id yaa...")
- Fakta domain hardcode sebagai guardrail anti-halusinasi (mis. "ASEAN Scholarship itu fully funded, TIDAK ADA partial scholarship")
- Taksonomi kelas/jenjang (SD/SMP/SMA, Primary/Sec Singapura) → mapping ke Junior/Intermediate/Seniors
- Aturan harga terikat status batch, aturan larangan (janji lolos, negosiasi harga, dst.) yang semuanya bahasa & konteks beasiswa

**Generic/reusable (pola arsitektur, layak dipertahankan strukturnya):**
- Aturan anti-halusinasi: "tidak punya tool, fakta HANYA dari DATA TERVERIFIKASI/FAQ di bawah, tidak ada → `[UNKNOWN]`"
- Protokol tag: `[SEND_GFORM: Nama Link]`, `[TALK_TO_SAM]`, `[UNKNOWN]`, `[FACTS key="value"]` — dipasang di awal/akhir output, diparse regex di `Process All`, tag dibuang sebelum dikirim ke user
- Placeholder injeksi konteks di ekor prompt: `{{ $json.data_context }}` dan `{{ $json.faq_context }}` (mekanisme generik, isi yang berubah per klien)
- Gaya "GAYA SAM": pendek, register netral (larangan sapaan/vokatif), variasi pembuka, larangan markdown/format WA — pola *tone* yang bisa dipakai ulang sebagai kerangka, isi partikel/contoh kalimat perlu disesuaikan gaya bicara telemarketer properti

**Temuan penting — dokumen prompt v8 sudah STALE:** `VIRA_SystemPrompt_v8.md` (file arsip yang dibaca untuk orientasi) masih memuat alur `# STATUS` (tanya "ortu atau anaknya" di awal percakapan dan tag `[USER_STATUS:PARENT/STUDENT]`). Tapi system prompt yang **benar-benar live** di dalam `VIRA V4.json` sudah **menghapus total** alur itu (permintaan client, changelog 2 Juli) dan menggantinya dengan bagian `# REGISTER NETRAL` (dilarang menyapa "kamu"/vokatif apa pun, tidak pernah tanya status). **Untuk remake, jadikan prompt yang tertanam di JSON V4 sebagai satu-satunya sumber kebenaran — jangan pakai file `.md` manapun sebagai referensi tanpa mencocokkan ke JSON terbaru.**

---

## 5. Perbedaan VIRA V4 Production vs VIRA_TEMPLATE_v1

**Temuan kunci: TEMPLATE lebih tua dari V4 dan TIDAK mewarisi perbaikan kritikal V4.** Tanggal file: `VIRA_TEMPLATE_v1.json` = 25 Juni; `VIRA V4.json` = perubahan 2–13 Juli. Perbandingan:

| Aspek | VIRA V4 (production) | VIRA_TEMPLATE_v1 |
|---|---|---|
| Resolusi identitas | Node `Resolve User Row` (No WA primer/lid backup, tanpa fallback rows[0]) | **Tidak ada** — masih pola lama yang jadi sumber bug "data tertukar" |
| Buffer pesan | `MSG_BUFFER` append-only (anti lost-update) | **Tidak ada** — masih `pending_msg` read-modify-write (rawan hilang pesan) |
| Alur status PARENT/STUDENT | **Dihapus total** (register netral) | **Masih ada** (`IF Status Update Needed`, `Update User Status`) |
| Filter grup WA | Node `If From Group` | **Tidak ada** |
| Error Workflow global | Ada file terpisah (`VIRA Error Notifier`), didesain untuk dipasang | Tidak direferensikan |
| Konteks kelas persisten + TTL | Ada (`kelas_anak`, `kelas_anak_ts`, 60 hari) | Tidak ada |
| **Konfigurasi multi-tenant** | **Tidak ada** — semua hardcode (Sheet ID di ±20 node, secret Kirimi di 9 node HTTP, whitelist di `IF (Whitelist)`, persona di `AI Agent`) | **Ada**: `Bootstrap Config → Read CONFIG → Parse Config → Whitelist Gate`, baca tab `CONFIG` per klien (key-value), satu-satunya edit manual = `SHEET_ID` di node `Bootstrap Config` |
| Jumlah node | 59 | 59 (kebetulan sama, isi berbeda) |

**Kesimpulan untuk remake Persada Cisoka:** jangan pakai TEMPLATE apa adanya (ketinggalan fix kritikal identitas & buffer), dan jangan pakai V4 apa adanya (belum punya lapisan config multi-tenant). Strategi yang benar: **fork ulang lapisan config (`Bootstrap Config`/`Read CONFIG`/`Parse Config`/`Whitelist Gate`) dari TEMPLATE, tempelkan ke atas logika node V4** (`Resolve User Row`, `MSG_BUFFER`, error workflow, TTL kelas_anak) — bukan sebaliknya.

---

## 6. Peta Komponen untuk Remake Persada Cisoka Residence

| Komponen eksisting | Status | Kebutuhan baru terkait |
|---|---|---|
| Webhook Kirimi + parsing payload (`Chat Counter`) | **Pakai ulang langsung** (struktur payload identik lintas klien Kirimi) | Semua |
| `Resolve User Row` (identitas No WA/lid) | **Pakai ulang langsung** | Semua |
| `MSG_BUFFER` append-only + debounce 2-lapis | **Pakai ulang langsung** | Semua |
| HITL 3-titik (`bot_mode`) | **Pakai ulang langsung** | (f) delegasi ke tim lapangan bisa pakai pola sama |
| Error Workflow + MSG_BUFFER Cleanup | **Pakai ulang langsung** (copy 1:1, ganti nomor admin) | Semua |
| Rate Limiter LID | **Pakai ulang langsung** | Semua |
| Tab `FAQ`/`PROGRAM`/`ABOUT_SAM`/`LINKS` + `FAQ Retrieve` | **Modifikasi ringan** — struktur kolom generik dipertahankan, isi & mungkin nama kolom disesuaikan (PROGRAM → data unit/tipe rumah, ABOUT_SAM → ABOUT_ADMIN atau profil developer) | (e) persona telemarketer, info unit/KPR |
| Config layer (`Bootstrap Config`/`Read CONFIG`/`Parse Config`/`Whitelist Gate`) dari TEMPLATE | **Modifikasi ringan** — struktur key-value dipertahankan, tambah key baru (lihat baris survey/source di bawah) | Semua (fondasi multi-tenant) |
| System prompt (`AI Agent.systemMessage`) | **Bangun baru** — kerangka tag/anti-halusinasi/gaya dipertahankan, isi persona+domain 100% ditulis ulang | (e) persona telemarketer properti |
| `Preprocess - Context Detection` (regex NLU kelas/program) | **Bangun baru** — pola regex-multi-match dipertahankan sebagai teknik, tapi kosakata (kelas SD/SMP/SMA) diganti kosakata properti (tipe unit, budget, KPR, lokasi) | (e) |
| `[FACTS kelas="..."]` + persistensi TTL (`kelas_anak`) | **Modifikasi** — mekanisme union+TTL dipertahankan, ganti field jadi mis. `unit_interest`, `budget_range`, atau `survey_date` | (a) |
| **Penjadwalan survey + catat tanggal/waktu** | **Bangun baru** — belum ada padanan di VIRA (tidak ada konsep "jadwal" tersimpan). Desain: tag baru `[SCHEDULE_SURVEY: tanggal|jam]` diparse di `Process All` (pola sama seperti `[SEND_GFORM]`), tulis ke kolom BARU di STATS (mis. `survey_date`, `survey_time`, `survey_status`) — **jangan reuse kolom `timestamp`/`buffer_done_ts`** (dipakai debounce). | (a) |
| **Follow-up otomatis untuk survey=belum** | **Modifikasi berat dari `VIRA_Follow_Up.json`** — logika scheduler & rate-limit follow-up (maks N kali, jeda jam) dipakai ulang, tapi filter kondisi diganti dari "belum aktif 24 jam" jadi "survey_status != Y", DAN wajib diperbaiki agar membaca `last_reply_ts` (bukan `timestamp` legacy yang sudah tidak ditulis V4) | (b) |
| **Deteksi intent telepon → redirect nomor admin** | **Bangun baru**, tapi pola sangat mirip `IF Talk To Sam → Notify Talk to Sam → Update row in sheet`. Tinggal: tambah tag `[REQUEST_CALL]` di prompt, node notifikasi ke nomor admin (dari `CONFIG.admin_phone`), balasan otomatis berisi nomor telepon (dari tab LINKS atau CONFIG) | (c) |
| **Deteksi sumber traffic (Google/FB/IG)** | **Bangun baru total** — TIDAK ADA mekanisme serupa di VIRA manapun (tidak ada parsing UTM/channel). Perlu: (1) kumpulkan SEMUA template teks pembuka per kanal dari klien (sudah ada di daftar pertanyaan Zoom), (2) node deteksi mirip `Preprocess` (regex/keyword match pesan pertama), (3) kolom baru `lead_source` di STATS, ditulis SEKALI saat `is_new_user` | (d) |
| Persona "Sam" + tag protocol + gaya WA (no markdown/vokatif) | **Modifikasi** — kerangka gaya (pendek, tanpa bullet/markdown, larangan tanda seru) sangat portable ke telemarketer; ganti isi domain & mungkin longgarkan "register netral" (properti mungkin butuh sapaan "Bapak/Ibu" — ini keputusan bisnis, bukan teknis) | (e) |
| **Delegasi klien yang sudah punya jadwal survey ke tim lapangan** | **Bangun baru**, pola serupa `IF Talk To Sam`/`Notify Talk to Sam` — begitu `[SCHEDULE_SURVEY]` terkonfirmasi, notif WA ke nomor tim lapangan (bukan admin telemarketing) berisi ringkasan data lead. Field-team routing bisa jadi 1 kolom `CONFIG.field_team_phone` terpisah dari `admin_phone` | (f) |
| **Kirim media PDF/gambar via Kirimi** | **Perlu riset/verifikasi dulu** — seluruh JSON yang dianalisis (V4, error workflow, follow-up) HANYA memakai endpoint `POST /v1/send-message` (teks). **Tidak ditemukan** endpoint kirim media di file manapun. Harus dicek langsung ke dokumentasi/dashboard Kirimi apakah ada endpoint semacam `/v1/send-media` sebelum desain requirement ini difinalisasi | (g) |
| **Summarization percakapan untuk handover ke admin manusia** | **Bangun baru total** — saat ini `Notify Talk to Sam` hanya kirim pesan mentah terakhir (`user_message_final`), BUKAN ringkasan. Untuk Persada Cisoka: tambah 1 pemanggilan LLM ringkas (bisa reuse `Anthropic Chat Model` connection) yang meringkas histori (Simple Memory / MSG_BUFFER + fakta STATS: budget, tipe unit, jadwal survey) jadi 2-3 kalimat sebelum dikirim ke admin | (h) |

---

## 7. Keterbatasan & Risiko yang Diketahui

1. **Kredensial Kirimi plaintext.** `user_code`, `secret`, `device_id` tertulis langsung di **≥9 node HTTP** tersebar di 3 file (VIRA V4, error workflow, follow-up) — bukan di n8n Credentials. Wajib dirotasi + dipindah ke Credentials sebelum file di-share/di-demo-kan ke klien baru manapun (termasuk Persada Cisoka).
2. **Whitelist masih hardcoded di V4 production** — `IF (Whitelist)` OR 5 nomor tetap ada meski TEMPLATE sudah punya versi config-driven (`Whitelist Gate`). Untuk klien baru, pastikan pakai pola TEMPLATE (config `whitelist_enabled`), bukan copy node `IF (Whitelist)` dari V4.
3. **Tidak ada autentikasi webhook** — endpoint `wa-inbound` terbuka, siapa pun yang tahu URL bisa kirim payload palsu → membakar token Anthropic & mengotori sheet. Perlu ditutup sebelum go-live publik.
4. **Google Sheets sebagai "database" transaksional** — cocok volume rendah-menengah 1 klien, belum teruji untuk concurrency tinggi atau banyak klien sekaligus (kuota API, eventual consistency).
5. **`VIRA_Follow_Up.json` kemungkinan sudah stale** — membaca `STATS.timestamp` yang **sudah tidak ditulis** oleh `Update to STATS` versi V4 (fix disengaja per changelog). Jalur "PRIORITAS 2: General follow up" di node `Filter` kemungkinan besar **tidak pernah trigger lagi** sampai dipatch untuk baca `last_reply_ts`. Untuk Persada Cisoka, jangan copy node `Filter` ini tanpa fix tersebut.
6. **Tidak ada endpoint kirim media** di seluruh workflow Kirimi yang dianalisis — hanya `send-message` teks. Requirement (g) di Persada Cisoka butuh verifikasi API Kirimi terlebih dulu.
7. **Non-text message langsung di-drop tanpa balasan.** Node `Chat Counter` mem-filter `messageType !== "text"` dengan `return []` (workflow berhenti total, tidak ada cabang lain). Padahal system prompt AI Agent punya instruksi "Balas non-teks -> Maaf, saya cuma terima teks yaa" — instruksi itu **tidak pernah tereksekusi** karena Code node sudah menghentikan eksekusi sebelum sampai ke AI Agent. Ini inkonsistensi kecil di V4 yang sebaiknya tidak diwariskan (gambar/voice note dari calon pembeli properti, yang sering kirim foto lokasi/KTP, akan hilang tanpa jejak).
8. **`$vars.chatCounter` di node `Chat Counter` kemungkinan dead code** — `$vars` di n8n umumnya read-only, penugasan `$vars.chatCounter = counter` kemungkinan no-op. Tidak berbahaya (hanya informatif ke teks AI) tapi menyesatkan, sebaiknya dibuang di versi baru.
9. **Rate limiter & Simple Memory bersifat volatile** — `$getWorkflowStaticData('global')` dan `Simple Memory` (buffer window) reset saat workflow di-redeploy/restart n8n. Fakta yang perlu tahan lama (kelas_anak → padanan `unit_interest`/`survey_date` di Persada Cisoka) HARUS lewat kolom STATS persisten dengan pola TTL seperti sekarang, bukan mengandalkan memory percakapan.
10. **Prompt AI ~9.000 kata + maxTokens 512** — cukup untuk gaya jawaban pendek ala WA, tapi kalau Persada Cisoka butuh jawaban lebih panjang (simulasi cicilan KPR, perbandingan tipe unit), `maxTokens` mungkin perlu dinaikkan dan diuji ulang.

---

## 8. Catatan untuk Agent Coding (Opus)

**Format payload webhook Kirimi masuk** (dari node `Chat Counter`, field yang dipakai):
```
body.message       -- teks pesan
body.messageType   -- HANYA "text" yang diproses; selain itu workflow drop tanpa balasan (lihat risiko #7)
body.from          -- nomor telepon ATAU format "...@lid" (passthrough, JANGAN di-strip manual)
body.originLid     -- LID eksplisit kalau ada
body.name / body.pushName / body.notifyName -- nama tampilan user (ambil yang pertama ada)
body.isFromMe      -- boolean, dipakai filter IF From Me
body.isFromGroup   -- boolean, dipakai filter If From Group
body.event         -- tidak dipakai aktif di V4, disimpan saja
```

**Format kirim balasan (Kirimi outbound) — SATU-SATUNYA endpoint yang teramati di seluruh repo:**
```
POST https://api.kirimi.id/v1/send-message
Body (form params): user_code, secret, device_id, phone, message
```
**Tidak ada endpoint kirim media** (gambar/PDF) yang ditemukan di file manapun (V4, error workflow, follow-up, template). Sebelum mengimplementasikan requirement (g), cek dokumentasi/dashboard Kirimi langsung — jangan asumsikan endpointnya `/v1/send-media` tanpa verifikasi.

**Pola penulisan Code node (konvensi yang konsisten di semua node V4, layak dipertahankan):**
- Baca data upstream via `$('Nama Node').first().json` / `.all()` — bukan `$json` implisit — supaya aman dari percabangan/merge yang ambigu.
- Helper `digits = v => String(v ?? '').replace(/\D/g, '')` diulang di banyak node untuk normalisasi nomor telepon — di remake baru pertimbangkan diekstrak jadi 1 definisi (kalau setup n8n memungkinkan shared code) atau tetap copy-paste konsisten seperti sekarang.
- `console.log`/`console.warn` dengan prefix emoji (✅ ⛔ 🔑 📨 🧹 ⚠️ 🚨) dipakai konsisten untuk keterbacaan log eksekusi n8n — pertahankan pola ini untuk observability.
- Guard "anti-kosong" (contoh di `Process All`: kalau filter internal menghapus semua teks, kembalikan versi sebelum filter) adalah pola defensif yang baik untuk dipertahankan pada logic serupa (jangan biarkan output valid jadi pesan error palsu ke user).

**Pola Google Sheets:** operasi `appendOrUpdate` dengan `matchingColumns: ["No WA"]` (atau kolom identitas stabil setara) adalah pola standar untuk write — hindari pola read-then-decide-append-or-update manual (itu penyebab bug lost-update V3).

**Konvensi penamaan node:** campuran Title Case ("Read STATS", "Resolve User Row") dan snake_case peninggalan versi lama ("Delete_Pending_Msg", "Cek_user_status"). Untuk workflow baru Persada Cisoka, disarankan konsisten Title Case + kata kerja Inggris/Indonesia deskriptif, mengikuti pola node-node BARU V4 (`Resolve User Row`, `Append MSG_BUFFER`) — bukan pola lama.

**Protokol tag AI (regex-parsed di `Process All`)** — pola ini generik dan terbukti di produksi, sangat layak dipakai ulang untuk tag baru:
- `[SEND_GFORM: Nama Link]` → jadi contoh pola untuk requirement lain yang butuh "AI memicu aksi terstruktur + data lookup", mis. `[SCHEDULE_SURVEY: tanggal|jam]`, `[REQUEST_CALL]`.
- `[FACTS key="value"]` → pola "AI mengekstrak fakta terstruktur untuk dipersist" — reuse langsung untuk `unit_interest`, `budget_range`, dll., dengan mekanisme union+TTL yang sama seperti `kelas_anak`.
- Setiap tag baru butuh: (1) instruksi eksplisit di system prompt kapan tag boleh dipasang, (2) regex parse + fallback pattern-matching (in case AI lupa tag) di `Process All`, (3) kolom baru di STATS untuk persist hasilnya — **jangan pernah reuse kolom `timestamp`/`buffer_done_ts`/`process_start_ts`** yang murni internal mekanisme debounce.

**Isolasi client-specific vs generic saat membangun ulang:** ikuti pemisahan yang SUDAH dirintis TEMPLATE (`Bootstrap Config` = 1 baris edit per klien; `CONFIG` tab = semua yang mudah berubah; n8n Credentials = semua secret) — jangan ulangi pola V4 production yang hardcode Sheet ID di ±20 node dan secret di 9 node HTTP, karena itu justru pola yang ingin dihindari saat membangun produk baru dari nol.

---

**Dokumen ditulis ke:** `D:\Documents\Claude Cowork\Persada Cisoka Residence\2026-07-15-analisis-arsitektur-VIRA-eksisting.md`
