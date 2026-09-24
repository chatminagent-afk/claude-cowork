# Pending Waiting Changes — VIRA PCR

Register perubahan yang **sengaja ditunda**, bukan backlog ide. Setiap entri di sini sudah dianalisis, sudah ada rencananya, dan sudah diputuskan untuk tidak dikerjakan sekarang — beserta alasannya.

- **Workflow**: `workflow/production/VIRA-PCR Main V1.json` (export live n8n) + `VIRA-PCR Main V1.2.json` (patch nama+domisili, belum diimport). **File siap-import terbaru: `workflow/patch V.1.3/`** (basis V1.2 + fix temuan QA 2026-07-19). Jalur build `_extraction/build/assemble.py` SUDAH TIDAK SINKRON dengan live.
- **Dibuat**: 2026-07-17
- **Update terakhir**: 2026-08-27 (tambah #26 — workflow STATS Purge 3 bulan dibuat & terverifikasi statis, **belum diimport & belum diaktifkan**; menunggu backup STATS + dry run). Sebelumnya 2026-08-21 (tambah entri INSIDEN fix retrieval — VIRA mengarang harga ke lead 6281291218300; `grab()` di `FAQ Retrieve1` menunjuk nama node tanpa sufiks `1` sehingga data_context & faq_context kosong untuk SEMUA pesan). Sebelumnya 2026-07-24 (tambah #25 false-handover "boleh" atas tawaran MEDIA — fix PROMPT-only, beda lapisan dari #23). Sebelumnya 2026-07-23 (tambah #22 multiple-media + #23 false-handover TALK_TO_ADMIN — keduanya edit di node `Process All`). Sebelumnya 2026-07-20 (konfirmasi Steven: #17/#18/#12/#20 DONE di file terbaru hasil fixing sendiri — file patch Main/Cleanup V1.3 buatan QA TIDAK dipakai/superseded, draft prompt efisien di-SKIP; #19 & #21 tahap testing. #2/#4/#1 mulai DIKERJAKAN — file import + guide dibuat di `workflow/patch V.1.3/2026-07-20-*`)

## Cara pakai

Setiap entri wajib punya: konteks, risiko kalau **tidak** dikerjakan, risiko kalau **dikerjakan**, plan langkah demi langkah, dan **trigger** — kondisi konkret yang bikin entri ini naik jadi prioritas. Entri tanpa trigger cuma jadi utang yang mengendap.

Status: `PENDING` → `IN PROGRESS` → `DONE` (pindahkan ke bagian Selesai) atau `DROPPED` (tulis alasannya).

---

## Ringkasan (urut prioritas tertinggi → terendah)

> **Update 2026-07-19:** patch disambiguasi media 2026-07-18 sudah masuk ke live export — prompt `AI Agent` memuat blok subsidi + SEND_MEDIA, dan `FAQ Retrieve` sudah bersih dari referensi mati. Entri #8 dan #9 karena itu SELESAI (dipindah ke bagian Selesai). Sisa apply patch media lain (LINKS/preprocess/Process All) tidak dilacak sebagai pending change bernomor.

### 🔴 P0 — MANDATORY sebelum go-live (bot rusak/bocor/senyap kalau dilewati)

| # | Judul | Dampak | Effort | Status |
|---|-------|--------|--------|--------|
| 19 | CONFIG routing nomor tim tidak sesuai keputusan desain | Notif survey & media nyasar ke orang yang salah sejak hari pertama live | edit 2 cell di Sheets live | IN PROGRESS — tahap testing (konfirmasi Steven 07-20); finalkan nomor saat go-live |
| 21 | Data test tersisa + private key di tab CONFIG | Data test mengotori STATS/SURVEY/EVENTS; private key terbaca siapa pun yang pegang sheet/xlsx | bersihkan baris + pindahkan key | IN PROGRESS — tahap testing (konfirmasi Steven 07-20); bersihkan sebelum go-live |

> **DONE per konfirmasi Steven 2026-07-20 (fixing sendiri di file terbaru):** #17 (settings V1.2), #18 (Cleanup salah spreadsheet), #12 (Wait1/Wait3), #20 (placeholder PRODUK). #10 sudah selesai sejak QA 07-19 (sisa tes paksa error §10B). File patch Main/Cleanup V1.3 buatan QA 07-19 **superseded — tidak dipakai**; draft prompt efisien **di-skip** (hemat 1,8% dinilai tidak impactful).

### 🟢 IN PROGRESS — sedang dikerjakan (2026-07-20, file siap di `workflow/patch V.1.3/`)

| # | Judul | Deliverable | Status |
|---|-------|-------------|--------|
| 4 | Cek `success:false` jalur media | `2026-07-20-import-node-4-check-media-api.json` (1 code node + sticky wiring) | Node siap — tinggal paste + wiring 2 koneksi |
| 2 | Notif `surveyRejectReason` AI-fault ke admin | `2026-07-20-import-nodes-2-notif-survey-ai-fault.json` (IF + HTTP + sticky, IF→HTTP sudah tersambung) | Node siap — tinggal paste + 1 koneksi dari Process All |
| 1 | Persist slot survey `pending_survey_*` di STATS | `2026-07-20-guide-1-persist-survey-slots.md` + 3 file kode pengganti (`2026-07-20-code-1-*.js`) | Kode siap — ikuti guide step 0–5 + verifikasi |

> **#3 (model swap OpenAI→Claude)** dipindah ke checklist go-live §7 + §8B — sengaja tetap OpenAI selama testing, dieksekusi saat setup production. Bukan lagi entri pending di sini.

> (Tabel P2 lama #4/#2/#1 dihapus — ketiganya naik ke tabel IN PROGRESS di atas per keputusan Steven 2026-07-20.)

**Selesai:** **#10 (error-notifier — diperbaiki & id cocok `errorWorkflow`, verified QA 07-19 malam; sisa tes live §10B)**, **#5 (kredensial Kirimi — 0 plaintext di Main, 10 node pakai `config.kirimi_*`, Grup B ber-auth, verified 07-19 14:21)**, #6 (kebijakan follow-up), #7 (kanonikalisasi tipe unit), #8 (sebut semua tipe termasuk subsidi), #9 (referensi mati FAQ Retrieve), #11 (buffer-cleanup — jalan di workflow terpisah), #13 (`.item`→`.first()` — 0 sisa, verified 07-19 12:50), #14 (Intensitas Chat — mapping dihapus dari `Update to STATS`), #15 (komentar SHEET_ID diperbaiki), #16 (pinData — zero impact). Lihat bagian Selesai di bawah.

> ⚠️ **#12 (update QA 07-19 malam):** di file `Main V1.json` (live export) `Wait1`+`Wait3` masih `disabled`, TAPI di `Main V1.2.json` dan `patch V.1.3` semuanya sudah **enabled**. Selama live n8n masih menjalankan V1, regresi masih aktif — beres otomatis begitu Main V1.3 diimport. Kalau import tertunda, nyalakan manual 2 node itu di live.

---

## 1. Persist slot survey (`pending_survey_*`) di STATS

**Status**: IN PROGRESS (2026-07-20) — kode & guide SIAP di `workflow/patch V.1.3/`: `2026-07-20-guide-1-persist-survey-slots.md` + `2026-07-20-code-1-{Resolve-User-Row,Cek_user_status,Process-All}.js` (full replacement jsCode, dibangun dari export V1.2, anchor & syntax terverifikasi). Deviasi dari plan lama: `Preprocess` TIDAK disentuh (Process All baca langsung dari `$('Cek_user_status')` pola `nama_lengkap_db`) — 4 node + prompt, bukan 6 node. Sisa: apply step 0–5 + verifikasi 3 giliran.
**Dicatat**: 2026-07-17
**Terkait**: fix halusinasi tanggal + gate kelengkapan slot (sudah dikerjakan 2026-07-17)

### Konteks

Slot survey (tanggal + jam + unit) dikumpulkan lintas beberapa giliran chat, tapi yang "mengingat" slot itu **cuma LLM lewat Simple Memory**. Sistem tidak menyimpan apa pun.

Contoh alur nyata:

```
User : mau survey dong
VIRA : Boleh Kak, enaknya kapan? Misal Sabtu 18 Juli jam 10.
User : senin aja                    ← slot tanggal masuk
VIRA : Siap, Senin 20 Juli. Jam berapa?
User : jam 10 pagi bs               ← slot jam masuk
```

Di pesan terakhir user cuma nulis "jam 10 pagi bs". Kata "Senin" ada di **dua giliran sebelumnya**. VIRA bisa menyusun tag `[SCHEDULE_SURVEY]` lengkap hanya kalau dia masih mengingatnya dari memory window.

### Risiko kalau TIDAK dikerjakan

- Window Simple Memory geser, user nyelak nanya harga di tengah penjadwalan, atau debounce menggabung pesan → **slot hilang**.
- Saat slot hilang, LLM cenderung **mengarang** untuk mengisi kekosongan. Ini akar penyebab bug `tanggal="2025-08-05"` yang ketemu 2026-07-17.
- Gate kelengkapan (sudah terpasang) **menangkap** kasus ini — user tidak akan dapat konfirmasi bohong. Jadi dampaknya turun dari *data korup diam-diam* jadi *VIRA nanya ulang slot yang sudah disebut*. Menyebalkan, tapi tidak merusak.
- **Inilah alasan penundaan**: gate sudah mengubah kegagalan dari senyap jadi berisik. Risiko sisa cuma pengalaman user yang kurang mulus.

### Risiko kalau DIKERJAKAN

- Menyentuh 6 node di jalur utama, termasuk `Update to STATS` yang dipakai **setiap pesan masuk** — salah sedikit, semua chat kena, bukan cuma yang survey.
- Butuh 4 kolom baru di tab STATS. Kolom sheet yang salah urut/salah nama bikin Google Sheets node gagal senyap.
- State bisa **basi**: user bilang "Senin" lalu hilang seminggu, balik lagi bulan depan — `pending_survey_tanggal` masih 2026-07-20 yang sudah lewat. Makanya butuh `pending_survey_ts` + TTL.
- Menambah sumber kebenaran kedua untuk slot (STATS + memory LLM). Kalau keduanya beda, harus jelas siapa yang menang → **STATS selalu menang**.

### Plan adjustment

**Prinsip**: pindahkan kepemilikan slot dari LLM ke sistem. LLM tidak perlu *ingat* — slot disodorkan ke dia tiap giliran lewat `[SYSTEM_DATA]`.

**Langkah 1 — Tab STATS**: tambah 4 kolom di paling kanan
```
pending_survey_tanggal | pending_survey_jam | pending_survey_unit | pending_survey_ts
```

**Langkah 2 — `Resolve User Row`**: baca kolom baru ke output
```js
pending_survey_tanggal: row ? String(row['pending_survey_tanggal'] || '').trim() : '',
pending_survey_jam:     row ? String(row['pending_survey_jam'] || '').trim() : '',
pending_survey_unit:    row ? String(row['pending_survey_unit'] || '').trim() : '',
pending_survey_ts:      Number(row ? (row['pending_survey_ts'] || 0) : 0) || 0,
```

**Langkah 3 — `Cek_user_status`**: inject ke template `aiSystemData`, di bawah `BUDGET_RANGE`. Terapkan TTL di sini — slot lebih tua dari 48 jam dianggap hangus (jangan sampai user dapat "jadi Senin ya?" untuk Senin yang sudah lewat 3 minggu).
```
PENDING_SURVEY: tanggal=2026-07-20 | jam=- | unit=Tipe 36/72
```

**Langkah 4 — `Preprocess - Context Detection`**: parse baris `PENDING_SURVEY` dari `fullMessage`, keluarkan sebagai `pendingSurvey: { tanggal, jam, unit }`. Masukkan ke `aiContext` supaya AI tahu slot mana yang sudah aman dan tidak perlu ditanya ulang.

**Langkah 5 — `Process All`**: di blok gate kelengkapan, merge berjenjang **sebelum** cek `missingSlots` — tag AI menang, pending jadi cadangan:
```js
const tglResolved  = svTgl  || pending.tanggal || '';
const jamResolved  = svJam  || pending.jam     || '';
const unitResolved = svUnit || unitMerged      || pending.unit || '';
```
Lalu keluarkan slot yang mau dipersist:
```js
surveyPendingWrite: isScheduleSurvey
  ? { tanggal: '', jam: '', unit: '', ts: '' }        // sukses -> kosongkan
  : { tanggal: tglResolved, jam: jamResolved, unit: unitResolved, ts: Math.floor(Date.now()/1000) }
```

**Langkah 6 — `Update to STATS`**: tambah 4 field mapping, pola `.first()` seperti kolom lain
```
pending_survey_tanggal = {{ $('Process All').first().json.surveyPendingWrite.tanggal }}
pending_survey_jam     = {{ $('Process All').first().json.surveyPendingWrite.jam }}
pending_survey_unit    = {{ $('Process All').first().json.surveyPendingWrite.unit }}
pending_survey_ts      = {{ $('Process All').first().json.surveyPendingWrite.ts }}
```

**Langkah 7 — System prompt** (`AI Agent`): tambah di blok `# SURVEY`
```
- PENDING_SURVEY di [SYSTEM_DATA] adalah slot yang SUDAH dikonfirmasi user sebelumnya. Anggap itu benar, JANGAN tanya ulang, dan tulis ulang di tag [SCHEDULE_SURVEY]. Tanda "-" artinya belum ada.
```

**Verifikasi**: jalankan alur 3 giliran (mau survey → "senin aja" → "jam 10 pagi bs"). Cek tab STATS terisi bertahap tiap giliran, lalu **kosong lagi** begitu SURVEY berhasil ditulis. Wajib cek juga chat non-survey biasa tidak rusak — `Update to STATS` jalan di setiap pesan.

### Trigger

Kerjakan kalau **setelah beberapa hari live** terlihat salah satu:
- VIRA menanyakan ulang slot yang sudah user sebut (cek execution log: `slot belum lengkap` muncul untuk slot yang jelas ada di riwayat chat), **atau**
- muncul lagi reject kategori AI-fault (`tahun tidak valid`, `tanggal/jam sudah lewat`) padahal kalender sudah di-inject — artinya prompt saja tidak cukup.

Kalau dua-duanya tidak muncul dalam ~1 minggu, kemungkinan besar tidak perlu sama sekali. **Jangan kerjakan preventif.**

---

## 2. Notifikasi `surveyRejectReason` ke admin

**Status**: IN PROGRESS (2026-07-20) — 2 node SIAP-IMPORT di `workflow/patch V.1.3/2026-07-20-import-nodes-2-notif-survey-ai-fault.json` (IF Survey AI Fault + Notify Admin Survey Fault + sticky wiring; koneksi IF→HTTP sudah termasuk). Sisa: paste ke canvas + 1 koneksi paralel dari `Process All` → IF + tes paksa.
**Dicatat**: 2026-07-17

### Konteks

`Process All` sekarang mengeluarkan `surveyRejectReason` saat tag `[SCHEDULE_SURVEY]` ditolak, tapi cuma lewat `console.warn` — tidak ada yang membacanya kecuali Steven buka execution log n8n manual.

### Contoh skenario konkret (menjawab "maksud contoh skenarionya seperti apa?")

Bayangkan chat begini:
```
User : mau survey minggu depan dong
VIRA : Boleh Kak! Enaknya hari & jam berapa?
User : sabtu jam 10
VIRA : Siap, saya catat ya Kak 😊   ← VIRA merasa berhasil menjadwalkan
```
Di balik layar, AI menyusun tag `[SCHEDULE_SURVEY]` tapi mengisi tanggalnya SALAH — misal `tanggal="Sabtu"` (bukan `2026-07-25`), atau `tahun=2025` (halusinasi), atau `jam="pagi"`. Sistem (`Process All`) **menolak** tag itu dengan `surveyRejectReason` = `tanggal tidak terbaca` / `tahun tidak valid` / dst. Artinya: **survey TIDAK tercatat** di tab SURVEY, padahal user sudah dikasih kesan "sudah dijadwalkan".

Yang terjadi sekarang: reject itu cuma nyangkut di `console.warn` execution log. Steven tidak tahu kecuali buka n8n manual. Bisa berhari-hari lead survey hilang diam-diam tanpa ketahuan.

Entri #2 = pasang notif WA ke admin **khusus** saat reason-nya kategori **AI-fault** (bukan kasus normal "slot belum lengkap"), supaya kalau prompt mulai ngaco tanggal, kamu langsung dapat alarm. Contoh isi notif: reason + nomor user + pesan asli + output AI-nya, biar bisa ditrace.

### Poin penting: reject ≠ error

Mayoritas reject justru **sistem bekerja benar**. Pemisahannya:

| Reason | Pemicu | Kategori |
|---|---|---|
| `slot belum lengkap: unit/tanggal/jam` | User belum sebut semua slot | **Normal** — VIRA menggali, memang begitu desainnya. Paling sering. |
| `di luar jam operasional` | User minta jam 19.00, tutup jam 17 | **Normal** — VIRA tawarkan ulang |
| `tanggal/jam sudah lewat` | AI halusinasi tanggal, atau user minta jam yang sudah lewat hari ini | **AI-fault** — prompt gagal |
| `tahun tidak valid` | AI keluarkan tahun < tahun sekarang | **AI-fault** — halusinasi murni |
| `tanggal tidak terbaca` | AI isi `tanggal="Senin"` bukan `YYYY-MM-DD` | **AI-fault** — tidak ikut format tag |
| `jam tidak terbaca` | AI isi `jam="pagi"` atau `"10"` tanpa menit | **AI-fault** — sama |
| `jam tidak valid` | `jam="25:00"` | **AI-fault**, jarang |
| `hari X tutup` | — | **Mati** — `closedDays` sudah di-set `[]` (PCR buka tiap hari) |

Yang layak dinotifikasi **hanya kategori AI-fault**. Kalau semua reject dinotifikasi, admin akan dibanjiri notif dari kasus normal dan berhenti membacanya — alarm yang selalu bunyi sama saja dengan tidak ada alarm.

### Risiko kalau TIDAK dikerjakan

- Kegagalan prompt tidak terlihat kecuali buka execution log manual. Bisa berjalan berhari-hari tanpa ketahuan.
- Dampaknya terbatas: user tetap dapat pertanyaan klarifikasi yang masuk akal (gate sudah menangani), jadi ini soal **observability**, bukan korupsi data.

### Risiko kalau DIKERJAKAN

- Notif berlebihan → admin fatigue. Wajib difilter ke AI-fault saja.
- Menambah node di jalur balasan; kalau salah wiring bisa menunda/menggagalkan reply ke user. Node notif harus **di cabang terpisah**, jangan di jalur kritis.
- Menambah panggilan HTTP ke Kirimi per kejadian — kalau ada bug yang bikin AI-fault berulang, bisa jadi spam ke admin. Pertimbangkan rate limit.

### Plan adjustment

**Langkah 1 — `Process All`**: tambah flag pemisah (murah, aman, tidak mengubah flow)
```js
const AI_FAULT = ['tanggal tidak terbaca','jam tidak terbaca','jam tidak valid','tahun tidak valid','tanggal/jam sudah lewat'];
const surveyNeedsAdminAlert = isSurveyIncomplete && AI_FAULT.includes(surveyRejectReason);
```
Masukkan `surveyNeedsAdminAlert` ke object return.

**Langkah 2** — IF node baru `IF Survey AI Fault`, kondisi `{{ $json.surveyNeedsAdminAlert }}` true, dicabangkan dari `Process All` (paralel, **bukan** menyela jalur balasan user).

**Langkah 3** — HTTP node `Notify Admin Survey Fault` ke Kirimi. Contoh isi pesan:
```
⚠️ [PCR] TAG SURVEY DITOLAK SISTEM
Alasan: {{ $json.surveyRejectReason }}
User: {{ $json.user_wa }} ({{ $json.user_name }})
Pesan: {{ $json.original_message }}
Output AI: {{ $json.output }}
```
Pakai `$('Parse Config').first().json.config.admin_phone` sebagai tujuan, ikut pola node notif yang sudah ada. Gunakan `.first()`, **jangan `.item`** — paired item putus di Code node (lihat Catatan Teknis).

**Verifikasi**: paksa AI-fault dengan sengaja (sementara ubah `AI_FAULT` biar `slot belum lengkap` ikut kena), pastikan notif masuk, lalu balikin lagi.

### Trigger

Kerjakan kalau **dalam ~1 minggu live** muncul reject kategori AI-fault di execution log. Kalau tidak ada sama sekali, berarti fix kalender berhasil dan node notif ini **tidak perlu dibuat**. Untuk sekarang pantau lewat execution log n8n saja.

---

## 3. Model swap OpenAI → Claude — DIPINDAH KE CHECKLIST GO-LIVE

**Status**: Prompt (langkah 1-3) sudah DONE & terverifikasi di live. Sisa = model swap saja, **sengaja tetap OpenAI gpt-4.1-mini selama testing** (keputusan Steven 2026-07-17, hemat biaya). Dieksekusi saat setup production, bukan sekarang.

Detail eksekusi ada di **checklist go-live §7 (buat credential Anthropic) + §8B (ganti 2 node `lmChatOpenAi` → `lmChatAnthropic`, hapus+buat baru+re-connect wire ke AI Agent / FAQ Retrieve)**. Regresi minimal setelah swap: intro, [UNKNOWN], bantahan harga, survey "senin depan jam 10", UAT media. Tidak dilacak lagi sebagai pending change di sini.

---

## 4. Cek `success:false` jalur media (eks "Paket D")

**Status**: IN PROGRESS (2026-07-20) — node SIAP-IMPORT di `workflow/patch V.1.3/2026-07-20-import-node-4-check-media-api.json` (`Check Media API Response`, meniru pola `Check API Response`, onError→continueErrorOutput + sticky wiring). Sisa: paste + wiring 2 koneksi + tes.
**Dicatat**: 2026-07-17

### Konteks

**Terverifikasi ulang 2026-07-19** (menjawab pertanyaan "bukannya sudah ada Notify Admin Media Error?"): node `Notify Admin Media Error` **memang ada**, tapi ia hanya tersambung ke **error output** `Send Media Kirimi` (`onError: continueErrorOutput`) — jadi hanya menyala saat gagal HTTP/transport (node error). Output SUKSES `Send Media Kirimi` kosong (`main[0] = []`). Kalau Kirimi balas **HTTP 200 + body `success:false`**, node dianggap sukses → tidak ada apa-apa → media dianggap terkirim padahal gagal, **tanpa notif**.

Bandingkan jalur teks: ada node terpisah `Check API Response` yang memeriksa body dan `throw` kalau `success:false`, lalu error output-nya → `Notify Admin API Error`. Jalur media **tidak punya** node pemeriksa body yang setara. Itulah gap #4 — bukan soal notif-nya tidak ada, tapi tidak ada yang men-trigger notif itu untuk kasus `success:false`.

### Risiko kalau TIDAK dikerjakan

Media gagal terkirim secara senyap; user sudah dijanjikan "dikirim sebentar lagi" oleh teks AI. Frekuensi kejadian tidak diketahui — belum pernah terobservasi di tes nyata.

### Risiko kalau DIKERJAKAN

Menambah node di cabang media yang baru saja di-rewire (pasca fix urutan teks→media); menambah permukaan bug saat UAT.

### Plan adjustment

Tambah code node `Check Media API Response` setelah `Send Media Kirimi` meniru pola `Check API Response` (throw kalau `success === false || status === false`), error output → `Notify Admin Media Error`. Pakai `.first()`, bukan `.item`.

### Trigger

Saat UAT/live ada laporan "bot bilang media dikirim tapi tidak sampai" TANPA notif admin media error, atau saat tes nyata menemukan respons 200 + `success:false` dari `send-message-file`.

---

## 17. V1.2 kehilangan `settings` workflow (errorWorkflow + timezone)

**Status**: DONE — konfirmasi Steven 2026-07-20, di-fix sendiri di file terbaru (file patch V1.3 QA superseded, tidak dipakai)
**Dicatat**: 2026-07-19 (QA production)

### Konteks

`Main V1.json` punya settings lengkap (`errorWorkflow: rBsq-mGgHfqfwbz3YmwxI`, `timezone: Asia/Jakarta`, `callerPolicy`, `timeSavedMode`). `Main V1.2.json` cuma punya `{executionOrder, availableInMCP}` — kemungkinan hilang saat proses build patch V1.2. Kalau V1.2 diimport apa adanya, workflow live TIDAK terhubung ke error-notifier.

### Risiko kalau TIDAK dikerjakan

Crash Main tidak menotifikasi siapa pun — persis lubang yang #10 tutup, terbuka lagi lewat pintu lain. Logika tanggal WIB AMAN (semua code node pakai `Asia/Jakarta` eksplisit, tidak bergantung setting timezone), jadi dampak nyata = errorWorkflow saja.

### Plan

Sudah dieksekusi: `patch V.1.3/2026-07-19-VIRA-PCR-Main-V1.3.json` = V1.2 + settings V1 dipulihkan + pinData test dihapus (nodes & connections diverifikasi identik dengan V1.2). Sisa: import file itu (bukan V1.2) saat naik versi. Setelah import, cek Settings → Error Workflow terisi.

### Trigger

Saat import Main versi baru — **jangan pernah import V1.2 mentah**.

---

## 18. Cleanup MSG_BUFFER menunjuk spreadsheet lain + credential beda

**Status**: DONE — konfirmasi Steven 2026-07-20, di-fix sendiri di file terbaru (file patch V1.3 QA superseded, tidak dipakai)
**Dicatat**: 2026-07-19 (QA production)

### Konteks

`VIRA-PCR - MSG_BUFFER Cleanup` production menunjuk Document ID `1dJWq7iq5PRGRguW6GRAgtclgvhSqppa-D6tSNrAo1PU` (cached name juga "PCR_Database" — kemungkinan **copy lama**) dengan credential OAuth `Google Sheets account`. Padahal Main + Follow-up menulis/membaca `1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o` via `Google Service Account - Persada`. Artinya cleanup harian membersihkan buffer di sheet yang TIDAK dipakai bot.

### Risiko kalau TIDAK dikerjakan

MSG_BUFFER production tidak pernah dibersihkan → tab membengkak, `Read MSG_BUFFER`/debounce makin lambat, kuota baca Sheets naik. Plus cleanup aktif menghapus baris di spreadsheet lain (kalau itu copy yang masih dipakai buat hal lain, datanya tergerus diam-diam).

### Risiko kalau DIKERJAKAN

Kalau dugaan salah (ternyata `1dJWq` justru sheet live), patch malah memindah masalah — makanya WAJIB verifikasi dulu di n8n UI/Drive: buka kedua spreadsheet, cek mana yang diisi Main saat chat test masuk.

### Plan

Sudah dieksekusi di `patch V.1.3/2026-07-19-VIRA-PCR-MSG-BUFFER-Cleanup-V1.3.json`: documentId → `1pzGu...`, authentication → serviceAccount, credential → `Google Service Account - Persada`, sheetName → mode name "MSG_BUFFER". Sisa: (1) verifikasi dugaan, (2) import + aktifkan menggantikan cleanup lama, (3) manual-run 1x — pastikan hanya baris >2 jam yang terhapus.

### Trigger

**Sebelum go-live** (satu paket dengan checklist §10A).

---

## 19. CONFIG routing nomor tim tidak sesuai keputusan desain

**Status**: IN PROGRESS — tahap testing (konfirmasi Steven 2026-07-20: nilai sekarang untuk fase testing). Finalkan nomor sesuai keputusan desain saat go-live.
**Dicatat**: 2026-07-19 (QA PCR_Database.xlsx)

### Konteks

Keputusan desain (memory 2026-07-16/17): notif survey → **Om Sulianto** via `field_team_phone`; notif permintaan media di luar katalog → **Aar + Aqsa** via `media_team_phone`. Kondisi CONFIG sekarang:

| Key | Isi sekarang | Seharusnya (per keputusan) |
|-----|--------------|---------------------------|
| `field_team_phone` | 6285155202354 (Steven) | 6287888542255 (Om Sulianto) |
| `media_team_phone` | 6287888542255 (Om Sulianto) | Aar 628988585871 + Aqsa 6281299500371 |

Kemungkinan nilai sekarang disengaja untuk fase testing (semua notif ke Steven dulu) — kalau iya, sah, tapi wajib diganti saat go-live.

### Risiko kalau TIDAK dikerjakan

Sejak hari pertama live: jadwal survey tidak sampai ke Om Sulianto, permintaan media manual tidak sampai ke telemarketer → lead menggantung padahal bot bilang "nanti dikirim tim kami".

### Plan

1. Konfirmasi dulu: nilai sekarang sengaja (testing) atau salah isi?
2. Saat go-live: edit 2 cell di tab CONFIG Sheets live sesuai kolom "Seharusnya".
3. Catatan teknis: cek apakah `media_team_phone` mendukung >1 nomor (lihat cara node `Notify Media Team` membacanya) — kalau cuma 1 nomor, putuskan Aar ATAU Aqsa, atau tambah key kedua + node paralel.

### Trigger

**Sebelum go-live** — masuk checklist §1/§4 (verifikasi CONFIG production).

---

## 20. PRODUK masih ada placeholder `(ISI: ...)`

**Status**: DONE — konfirmasi Steven 2026-07-20 (placeholder sudah diedit)
**Dicatat**: 2026-07-19 (QA PCR_Database.xlsx)

### Konteks

Tab PRODUK: kolom **Status Stok** ketiga tipe masih `(ISI: konfirmasi stok terkini ke tim)` / `(ISI: stok terkini — snapshot Sikumbang...)`, dan **Dimensi Tanah** 36/81 masih `(ISI: dimensi tanah 36/81)`. `FAQ Retrieve` menserialisasi PRODUK apa adanya ke DATA TERVERIFIKASI — teks placeholder itu SAMPAI ke mata AI.

### Risiko kalau TIDAK dikerjakan

User tanya "masih ada stok?" → AI membaca placeholder; paling bagus dia menjawab mengambang ("perlu konfirmasi tim"), paling buruk mengutip teks placeholder mentah ke user. Gap data ini sudah tercatat sejak form marketing 07-17 dan belum terjawab.

### Plan

Minta 2 data ke tim marketing (stok terkini per tipe + dimensi tanah 36/81), isi di Sheets live. Kalau stok memang dinamis dan tim tidak mau update rutin, ganti placeholder dengan teks aman yang memang layak dibaca user (mis. "Ready — ketersediaan blok dikonfirmasi saat survey", konsisten dengan aturan kavling).

### Trigger

**Sebelum go-live**; minimal ganti placeholder → teks aman meski data belum ada.

---

## 21. Data test tersisa + private key service account di tab CONFIG

**Status**: IN PROGRESS — tahap testing (konfirmasi Steven 2026-07-20; data test memang masih dipakai). Bersihkan + amankan private key sebelum go-live.
**Dicatat**: 2026-07-19 (QA PCR_Database.xlsx)

### Konteks

- Baris test (chat Steven 07-19) tersisa di: STATS 1 baris, MSG_BUFFER 12 baris, SURVEY 1 baris (Roy/2026-07-21), EVENTS 1 baris.
- Tab CONFIG memuat 2 baris `google service email` + `google service private key` (private key lengkap). Bot tidak memakainya (credential ada di n8n) — ini sisa setup. Siapa pun yang dapat akses sheet/xlsx bisa pakai key itu untuk akses Sheets sebagai service account.
- Kolom `system_prompt` & `brochure_url` di CONFIG juga masih placeholder — tidak dipakai workflow (prompt inline di AI Agent, media via LINKS), aman, tapi membingungkan auditor berikutnya; kasih keterangan "(tidak dipakai)" atau hapus.

### Plan

Sebelum go-live: hapus baris test 4 tab, pindahkan private key keluar dari sheet (simpan di password manager; hapus baris dari CONFIG + dari xlsx lokal), beri keterangan pada key CONFIG yang tidak terpakai.

### Trigger

**Sebelum go-live.** Untuk private key: makin cepat makin baik — tidak tergantung go-live.

---

## Catatan teknis yang berlaku umum di workflow ini

Bukan pending change, tapi wajib diingat saat mengerjakan entri mana pun di atas:

- **Selalu `.first()`, jangan `.item`.** `$('Node').item` menelusuri balik rantai `pairedItem`, dan beberapa Code node (`Cek_user_status`, `Process All`) mode *Run Once for All Items* tidak menyetelnya → rantai putus. `.item` adalah ranjau yang cuma meledak saat branch-nya kebetulan jalan. Flow ini selalu single-item per eksekusi, jadi `.first()` selalu benar. (Per 2026-07-19 12:50: 0 pelanggaran tersisa — entri #13 selesai. Jaga saat menambah node baru.)
- **`closedDays` ada di 2 node** (`Preprocess` dan `Process All`) dan harus SAMA. Saat ini `[]` — PCR buka tiap hari. Kalau nanti mau tutup di hari tertentu, tambahkan `survey_closed_days: jsonArr('survey_closed_days'),` di `Parse Config` lalu isi key-nya di tab CONFIG — code sudah membaca key itu duluan, jadi cukup edit sheet.
- **Jangan hardcode tanggal contoh di system prompt.** Contoh `tanggal="2026-07-20"` yang lama jadi anchor mati dan ikut andil bikin halusinasi tanggal. Contoh harus dinamis atau tidak ada sama sekali.
- **Setiap tag yang ditolak sistem harus MENGUBAH balasan, bukan cuma dibuang.** Generalisasi dari bug 2026-07-17: tag dibuang dari `cleanOutput` tapi kalimat "saya catat yaa" tetap terkirim padahal tidak ada yang tercatat. Kalau menambah tag baru, pastikan jalur reject-nya juga menimpa `cleanOutput`. (Sudah diterapkan di patch disambiguasi media 07-18: tag ambigu → cleanOutput di-override pertanyaan pilihan.)
- **Tidak ada node yang memakai credential n8n untuk Kirimi** — semua auth via body parameter. Konsisten saja dengan pola `Parse Config` (entri #5); jangan campur dengan httpCustomAuth kecuali memutuskan migrasi total.

---

## Selesai

### 6. Kebijakan follow-up: CONFIG vs jawaban tim marketing — DONE (diputuskan 2026-07-17)

- `followup_max` = **0 (TANPA BATAS)**; `followup_interval_hours` = **72**; jam kirim **08.00–21.00 WIB**; **10 template** siklus berurutan.
- Nilai sudah di-apply ke tab CONFIG `PCR_Database.xlsx`. Risiko diblokir user/limit WA sudah disampaikan & diterima (mitigasi: interval 3 hari + jam etis + template variatif).
- **Sisa operasional (bukan pending change)**: import + aktifkan `workflow/2026-07-17-VIRA-PCR-followup.json` (audit 07-18: masih `active:false` di file — kredensial sudah bersih via `Parse Config FU`), plus 2 adjustment kecil di Main: mapping `flag_survey=TRUE` di `Update STATS Survey`, reset `follow_up_count=0` di `Update to STATS`.

### 7. Kanonikalisasi tipe unit — DONE (terverifikasi di live, audit 2026-07-18)

Bug live 2026-07-17: STATS korup "Tipe 36" (tanpa slash) bikin VIRA menawarkan tipe fiktif. **Audit 2026-07-18 mengonfirmasi patch SUDAH di-apply Steven ke live export**: regex `Preprocess - Context Detection` kini wajib slash (`/tipe\s*(\d{2,3})\s*\/\s*(\d{2,3})/gi`, komentar "slash WAJIB"), fallback DB disaring `canonType()`, dan merge `unitSet` di `Process All` ikut tersaring — STATS korup self-heal saat user chat lagi.

**Batas yang tetap berlaku**: validasi struktural (`NN/NN`), bukan cek katalog PRODUK. Tipe well-formed tapi fiktif (mis. "Tipe 40/90") masih lolos. Follow-up katalog: kerjakan hanya kalau muncul laporan AI mengarang tipe well-formed yang tidak ada di PRODUK.

⚠️ **Catatan untuk apply patch media 07-18**: file `2026-07-18-process-all-vira-pcr.js` dibuat dari live export TERBARU yang **sudah memuat** patch kanonikalisasi ini — aman di-paste langsung, tidak menimpa fix.

### 8. Prompt — sebut SEMUA tipe (termasuk subsidi) — DONE (terverifikasi di live, audit 2026-07-19)

Bug live 2026-07-17: user tanya "ada tipe unit apa aja", VIRA cuma sebut 36/72 & 36/81 (komersil), subsidi 30/60 (Rp185jt) hilang → lead segmen termurah lolos. **Verifikasi 2026-07-19**: systemMessage node `AI Agent` di live sudah memuat instruksi *"tampilkan SEMUA tipe yang ada di DATA TERVERIFIKASI apa adanya... Ini termasuk tipe SUBSIDI (mis. 30/60)"* plus contoh disambiguasi media. Selesai saat enhanced prompt versi 2026-07-18 di-paste.

### 9. Referensi mati `$('Read LINGKUNGAN Data')` di `FAQ Retrieve` — DONE (terverifikasi di live, audit 2026-07-19)

Node `FAQ Retrieve` dulu memanggil `$('Read LINGKUNGAN Data')` (node itu tidak ada → section "LINGKUNGAN & LEGALITAS" selalu kosong, silent failure). **Verifikasi 2026-07-19**: referensi hidup sudah dihapus; yang tersisa di kode hanya komentar changelog yang mendokumentasikan penghapusan. Data lingkungan memang sudah pindah ke FAQ (kategori "Lingkungan"). Selesai bareng apply patch disambiguasi media.

### 11. Buffer-cleanup MSG_BUFFER — DONE (dipindah ke workflow terpisah, 2026-07-19)

Housekeeping MSG_BUFFER sekarang jalan di workflow terpisah **`VIRA-PCR - MSG_BUFFER Cleanup`** (jadwal harian 03:00 WIB) — bukan lagi template inactive. **Sisa operasional (bukan pending change)**: sebelum go-live, ganti credential Google + Document ID ke sheet **production** PCR dan pastikan `active: true`. Sudah dicatat sebagai item di **checklist go-live §10A**.

### 12. Node Wait disabled — FIXED DI FILE V1.2/V1.3 (verifikasi QA 07-19 malam)

Riwayat: DONE 12:50 → regresi di export 14:21 (`Wait1`+`Wait3` disabled lagi, kemungkinan testing). **QA 07-19 malam:** di `Main V1.2.json` dan `patch V.1.3` seluruh Wait **enabled** (disabled = 0). Yang masih menyimpan regresi hanya `Main V1.json` (live export). Beres otomatis saat import Main V1.3; kalau import tertunda, nyalakan manual di live.

### 10. Error-notifier — DONE di file production (verifikasi QA 2026-07-19 malam)

File `workflow/production/VIRA-PCR Error Notifier.json` SUDAH diperbaiki total dari kondisi template: ada `Error Trigger` → `Compose Notif` (pesan informatif: workflow/node/error/execution + peringatan "ada pesan user yang mungkin tak terbalas") → HTTP Kirimi `send-message`; `phone` = literal `6285155202354` (valid), `message` = expression valid `={{ $json.notif_text }}`; `active: true`; **id = `rBsq-mGgHfqfwbz3YmwxI`** — persis yang dipasang di `errorWorkflow` Main V1 (dan patch V1.3). Placeholder `{{ADMIN_PHONE}}`/`REPLACE_*` = 0.
**Catatan disengaja:** kredensial Kirimi di-hardcode plaintext di body — jalur error memang harus bebas dependensi (tidak boleh ikut bergantung Parse Config/Sheets yang mungkin justru sumber crash-nya). Konsekuensi: file JSON ini mengandung secret — jangan dishare; rotate secret kalau pernah bocor. Device `D-GHK1A` konsisten dengan CONFIG `kirimi_device_id`.
**Sisa operasional (checklist §10B):** verifikasi workflow live di n8n = versi file ini + aktif, lalu tes paksa 1 error → notif WA masuk.

### 5. Kredensial Kirimi — DONE (0 plaintext + Grup B ber-auth, terverifikasi export 2026-07-19 14:21)

Dua masalah beres sekaligus: (a) **kebocoran** — 5 node yang dulu plaintext (`KM40LI0426`/secret/`D-R91JY`) sekarang pakai `={{ $('Parse Config').first().json.config.kirimi_* }}`; grep plaintext = 0. (b) **bug fungsional** — 4 node Grup B (Notify Admin Unknown/API Error/Media Error, Reply Error) yang dulu tanpa auth sekarang punya `user_code`+`secret`+`device_id` lengkap. Verifikasi: 10 node Kirimi semua `uc/secret/dev = via config` (30 field expression). Sisa operasional: pastikan 3 key `kirimi_*` di CONFIG production = nilai PCR (bukan The Scholars) — masuk checklist go-live §1/§4.

### 13. `.item` → `.first()` — DONE (0 sisa, terverifikasi export 2026-07-19 12:50)

Konvensi proyek: selalu `.first()`, jangan `.item`. Semua pelanggaran sudah diganti bertahap; export final **12:50** grep `.item` = 0. Termasuk 4 sisa terakhir yang sempat kelewat (Update STATS Survey ×2, Format Media Notif, Collect Handover Context). Fix murni mekanis (`.item` → `.first()`), perilaku identik.

### 14. Kolom "Intensitas Chat" — DONE (mapping dihapus dari `Update to STATS`, 2026-07-19)

Kekhawatiran lama (`$vars.chatCounter` stale) DROPPED — Steven konfirmasi `Chat Counter` jalan normal. Yang diinginkan: kolom "Intensitas Chat" diisi manual pakai formula SPARKLINE di Sheet, bukan ditulis VIRA. **Verifikasi export 2026-07-19 01:34**: field `"Intensitas Chat"` sudah **dihapus** dari mapping node `Update to STATS` (grep value mapping: 0 hasil). VIRA berhenti menimpa kolom itu → formula manual aman.
- Sisa opsional (bukan blocker): kosongkan sisa isi lama di kolom itu lalu pasang formula MAP/SPARKLINE di sel teratas; blok penghitung `Intensitas Chat` di `Process Counter & Merge Data` kini dead field (boleh dihapus, harmless).

### 15. Komentar `SHEET_ID` menyesatkan — DONE (komentar diperbaiki, 2026-07-19)

Impact aslinya **nol** (cuma komentar; `config.sheet_id` tidak dipakai node mana pun, 23 node hardcode ID sendiri). **Verifikasi export 2026-07-19 01:34**: komentar lama *"satu-satunya titik edit manual per klien"* sudah tidak ada. Catatan kecil: komentar sekarang masih berbunyi *"Ganti SHEET_ID ke Sheet ID spreadsheet … <-- EDIT"* — masih sedikit menyiratkan SHEET_ID = titik edit, padahal runtime tetap pakai 23 hardcode. Kalau mau 100% jujur, tambahkan "(node Google Sheets tetap hardcode — ganti manual 23x saat clone, lihat checklist §8A)". Bukan blocker.

### 16. `pinData` payload test di node `Webhook` — DITUTUP (zero impact production, 2026-07-19)

Steven konfirmasi tidak ada dampak ke produksi (pinData cuma dipakai saat manual-run di editor). Catatan: di export `Jul 19 01:02` payload pin-nya **secara teknis masih ada** — kalau mau benar-benar bersih (hilangkan nomor pribadi dari file + hindari data test lama saat debug), unpin di editor lalu export ulang. Bukan blocker go-live.

---

## 17. Enrichment PRODUK & FAQ — data harga (2026-07-20)

Pemicu: VIRA salah info "cashback Rp20jt setelah akad". Rumus pricelist sudah di-reverse-engineer & dikonfirmasi tim (lihat `2026-07-20-planning-enrich-sheet-PRODUK-VIRA-PCR.md` + `2026-07-20-verifikasi-simulasi-harga-PCR.py`). Sheet subsidi + data non-angka SUDAH dikerjakan di `PCR_Database.xlsx`. Yang di bawah ini DITAHAN.

### 17A. BLOCKER — dua versi pricelist komersil
Tim kirim 2 pricelist komersil berbeda: (A) asumsi 5,25%, tanpa bonus, UM 5% dari harga penuh, tenor 10/15/20; (B) asumsi 8,25% program BPJS Ketenagakerjaan, bonus Rp20jt, UM 5% dari harga setelah bonus, tenor 15/20/25/30. Tim minta program BPJS "di-skip dulu karena mayoritas konsumen wiraswasta" — padahal versi tanpa BPJS justru tidak punya bonus cashback. **Belum jelas mana yang berlaku dan apakah cashback Rp20jt masih ada.**
Sampai dijawab: kolom Bonus/UM/Maks KPR/Bunga/Tabel Angsuran baris komersil berstatus DITAHAN, dan VIRA diarahkan lempar simulasi komersil ke tim marketing.

### 17B. BLOCKER — kontradiksi uang muka komersil
Tim menjawab konsumen komersil cukup bayar Rp2.500.000 (UM 5% ditanggung developer). Pricelist resmi menulis tebal *"Uang Muka (DP) harus Lunas sebelum Akad Kredit"*. Salah satunya tidak akurat. Risiko komplain di meja akad + tertulis dari nomor resmi.

### 17C. Persyaratan KPR untuk wiraswasta belum ada
Daftar 9/10 dokumen di pricelist semua berorientasi karyawan (slip gaji, SK karyawan tetap, surat keterangan aktif kerja). Tim sendiri bilang mayoritas konsumen wiraswasta. Dokumen pengganti belum ada di mana pun. Sementara: FAQ diarahkan ke tim marketing.

### 17D. Bunga untuk non-peserta BPJS Ketenagakerjaan
Pertanyaan 1b belum dijawab tim. Kalau versi B yang dipakai, syaratnya peserta BPJS TK aktif min. 1 tahun (dikonfirmasi) — tapi angka untuk non-peserta tidak ada.

### 17E. Patch node `FAQ Retrieve` — WAJIB, belum dikerjakan
9 kolom baru PRODUK (T–AB) belum terdaftar di `const MONEY`, jadi jatuh ke ember SPEK dan TIDAK terkirim saat user cuma tanya harga (`askingPrice`). Tanpa patch ini enrichment tidak berefek pada intent harga. Detail patch: §5 planning doc.

### 17F. Kategori FAQ tidak cocok dengan tabel boost (bug laten)
`FAQ Retrieve` mem-boost kategori `'Harga & KPR'`, `'Lokasi'`, `'Survey'`. Kategori riil di sheet: `'Harga & Pembayaran'`, `'KPR'`, `'Booking'`, `'Promo'`, `'Lingkungan'`. Tidak ada yang match → **boost tidak pernah aktif sejak awal**. Perlu diputuskan: samakan nama kategori di sheet, atau ubah key di code.

### 17G. Nomor rekening di FAQ — sudah diubah, perlu persetujuan
FAQ baris 31 sebelumnya menyebut nomor rekening lengkap. Diubah jadi nama PT saja + arahkan ke tim marketing (alasan: isi FAQ bisa keluar verbatim di WA; bot yang menyebar nomor rekening = permukaan penipuan). Kalau Steven/klien mau dikembalikan, teks lama ada di backup `PCR_Database_BACKUP_2026-07-20.xlsx`.

### 17H. Isu DP subsidi di luar pengetahuan bank
Tim menyebut UM subsidi riil Rp7.500.000 sementara bank tahu Rp5.850.000, dan unit hook punya tambahan DP "tanpa sepengetahuan bank". **Tidak dimasukkan ke sheet dalam bentuk apa pun** — sheet hanya mencatat angka menghadap konsumen (Rp7.500.000 all-in). Perlu diangkat ke Om Sulianto sebagai isu kepatuhan, di luar scope chatbot.

---

## 22. Multiple media dalam satu permintaan (foto + video sekaligus)

**Status**: IN PROGRESS (2026-07-23) — file SIAP APPLY: `2026-07-23-guide-3-multiple-media.md` (3 edit kode Process All + langkah wiring) + `2026-07-23-import-nodes-3-media2.json` (4 node branch media-2). Sisa: Steven apply 3 edit kode + import 4 node + 1 wiring wajib (`Send Media Kirimi` #0 → `IF Send Media 2`) + test.
**Dicatat**: 2026-07-23
**Terkait**: temuan QA `test chat vira.txt` (#3) — user minta "video dan foto", Vira hanya kirim foto lalu menjanjikan video yang tak pernah masuk.

### Konteks (bug kode)
Node `Process All` menangkap tag media dengan regex TANPA flag global:
`const mediaMatch = aiOutput.match(/\[\s*SEND_MEDIA\s*(?::\s*([^\]]*))?\]/i);`
`.match()` tanpa `/g` hanya mengambil tag **PERTAMA**. Walau prompt sudah menyuruh Vira pasang 2 tag terpisah (`[SEND_MEDIA: foto-XX]` + `[SEND_MEDIA: video-XX]`), hanya foto (tag pertama) yang diproses; tag video dibersihkan dari teks (cleanup pakai regex `/gi` global) tapi medianya **tidak pernah terkirim**. Pipeline hilir (`mediaUrl`, `mediaCaption`, `Download Media`, `Send Media Kirimi`) semuanya single-value. Ini murni n8n fix — bukan model/token.

### Keputusan desain (konfirmasi Steven 2026-07-23)
- **Cakupan: "hanya yang diminta"** — user minta foto+video → kirim keduanya; minta salah satu → kirim yang itu saja. BUKAN auto-bundle keduanya untuk tiap permintaan media.
- **Pengiriman: 2 pesan WA terpisah** (Kirimi kirim 1 file/pesan) — foto dulu, lalu video. Usahakan pakai loop node existing, tanpa node baru.
- Pricelist tetap dikecualikan.

### Risiko kalau TIDAK dikerjakan
User minta foto+video (pola wajar calon pembeli high-intent) hanya dapat foto; Vira menjanjikan video tapi tak pernah masuk → terlihat broken/bohong, menurunkan trust di momen kritis.

### Risiko kalau dikerjakan
- Regex global + multi-item → >1 download/POST Kirimi per giliran: cek rate-limit/kuota Kirimi & urutan (foto→video).
- Pastikan teks balasan (`cleanOutput`) tetap terkirim **sekali**, tidak duplikat per item media.
- Pastikan `Download Media`/`Send Media Kirimi` iterasi benar per item (default n8n: node hilir jalan per item) — verifikasi binary tidak saling menimpa.

### Plan langkah demi langkah (belum dieksekusi)
1. `Process All`: `.match()` → `matchAll(/.../gi)`, kumpulkan semua key jadi array, resolve tiap key ke {url, caption, tipe} lewat logika LINKS yang sama.
2. Output multi-item: 1 item teks balasan + N item media (jaga hanya 1 pesan teks).
3. `IF Send Media`: pastikan cabang media iterasi per item.
4. `Download Media` + `Send Media Kirimi`: verifikasi jalan per item, urutan foto→video.
5. Uji: "foto dan video 36/81" → 2 file; "foto 36/81" → 1 file; ambigu tanpa tipe → tetap tanya balik (jangan pasang tag).

### Catatan data (bukan bug)
Di sheet LINKS, URL `video-36-81` sama dengan `video-36-72` — ini **memang benar / disengaja** (konfirmasi Steven 2026-07-23): satu video dipakai untuk kedua tipe. Tidak perlu diubah.

### Trigger
Naik prioritas saat: (a) kapasitas token Steven pulih, ATAU (b) sebelum go-live media — karena permintaan "foto dan video" adalah pola umum calon pembeli.

---

## 23. False-handover: `[TALK_TO_ADMIN]` terpicu fallback frasa saat Vira cuma MENAWARKAN eskalasi

**Status**: IN PROGRESS (2026-07-23) — Opsi A disetujui Steven, edit SIAP APPLY (hapus 5 baris di `Process All`). Belum di-apply ke live.
**Dicatat**: 2026-07-23
**Terkait**: temuan QA versi enhanced 07-23 — user tanya "ini tanpa uang muka?", Vira **menawarkan** "Kalau mau, saya sambungkan ke tim kami...?" (tanpa tag), tapi `isTalkToAdmin=true` → bot_mode OFF prematur.

### Konteks (root cause)
`Process All` baris 76–82: deteksi `[TALK_TO_ADMIN]` punya **fallback berbasis frasa** —
`const p = ['sambungkan ke tim marketing','saya sambungkan ke tim','biar tim marketing','ke tim marketing kami'];`
Output AI mengandung *"saya sambungkan ke tim kami"* → substring-match frasa `'saya sambungkan ke tim'` → `isTalkToAdmin=true`, walau `aiOutputRaw` TIDAK punya tag. AI-nya benar (menawarkan dulu tanpa tag); fallback yang meng-override keputusan AI.

### Dampak
`isTalkToAdmin=true` → cabang `IF Talk To Admin` → notif admin + **bot_mode OFF**. Vira sering menutup dengan tawaran "kalau mau saya sambungkan ke tim?", jadi fallback ini **mematikan bot untuk lead setiap kali sekadar menawarkan eskalasi** — false-handover massal, bot senyap tanpa alasan. Severity tinggi.

### Keputusan (Opsi A — tag-only)
Hapus fallback frasa (baris 78–82); handover HANYA lewat tag `[TALK_TO_ADMIN]`. Konsisten dengan arsitektur tag-authoritative (media/survey juga tag-driven) + prinsip minim-hardcode. Alur benar: Vira tawarkan (tanpa tag) → user konfirmasi → giliran berikut AI pasang tag.

### Edit (siap apply)
`Process All` — ganti blok baris 76–82 jadi 2 baris:
```js
// ── TAG: [TALK_TO_ADMIN] ── (tag-only; fallback frasa dihapus 2026-07-23)
let isTalkToAdmin = aiOutput.includes('[TALK_TO_ADMIN]');
```

### Risiko kalau dikerjakan
Kalau AI kadang LUPA pasang tag saat user sudah konfirmasi handover → tidak ter-handover. Mitigasi: test alur konfirmasi; kalau perlu nudge kecil di prompt (tanpa hardcode). Jauh lebih ringan daripada false-handover.

### Catatan lanjutan (belum diputuskan)
Pola fallback-frasa serupa ada di deteksi media (`Process All` baris 88–92, frasa "kirim brosur" dll) — berpotensi false-positive tapi dampak lebih ringan (kirim media, bukan matikan bot). Review terpisah kalau perlu.

### Trigger
Sudah disetujui — apply bersamaan patch Process All lain (#22 media-2) supaya sekali edit node.

---

## 25. False-handover: AI pasang `[TALK_TO_ADMIN]` saat user jawab "boleh" atas tawaran MEDIA

**Status**: APPLIED ke `workflow/production/VIRA-PCR Main V1.4.json` (2026-07-24) — versi LEAN 2 rewrite prompt (blok baru dibuang, net ~+25 token). V1.4 = V1.3 + 2 edit systemMessage, 88 node & 64 koneksi identik (terverifikasi). Sisa: Steven review + import ke n8n live + jalankan QA suite. Spec: `2026-07-24-fix-false-handover-boleh-VIRA-PCR.md`.
**Dicatat**: 2026-07-24
**Terkait**: #23 (false-handover — TAPI beda lapisan: #23 fallback frasa di KODE `Process All`, sudah fix; #25 = AI sendiri yang pasang tag, fix di PROMPT).

### Konteks (bug nyata)
Transkrip 2026-07-24: VIRA menawarkan "mau saya kirimkan foto & video unitnya?", user jawab "ya boleh", VIRA balas "[TALK_TO_ADMIN] saya sambungkan ke tim marketing". User setuju MEDIA, bukan minta tim — permintaan foto/video 100% scope VIRA (`[SEND_MEDIA]`).

### Root cause (2 lapis, keduanya di systemMessage)
- **Lapis A**: `# ESKALASI` men-hardcode kata "boleh" sebagai token `[TALK_TO_ADMIN]` tanpa syarat "apa yang barusan ditawarkan"; `# TAG` memperkuat "mengiyakan tawaranmu" secara generik. Tidak ada aturan "boleh atas tawaran foto/video = `[SEND_MEDIA]`". Balasan bug hampir menyalin contoh verbatim `[TALK_TO_ADMIN]` di prompt.
- **Lapis B**: tawaran media VIRA berbentuk pertanyaan ya/tidak ("mau saya kirimkan?") — dilarang `# LARANGAN` tapi masih muncul — itu yang memancing jawaban telanjang "ya boleh" yang ambigu.

### Fix (prompt-only, minim-touch — detail lengkap di doc)
1. Sisip blok baru `# KONFIRMASI TAWARAN` sebelum `# ESKALASI`: rutекan jawaban setuju telanjang berdasarkan tawaran terakhir (media→SEND_MEDIA, simulasi→hitung, survey→SURVEY, profil→FACTS, tim→TALK_TO_ADMIN, ganda/ragu→klarifikasi). Ada contoh WAJIB kasus nyata.
2. Scope-kan kalimat pembuka `# ESKALASI` — "boleh" hanya pemicu handoff bila tawaran terakhir = menyambungkan ke tim.
3. Scope-kan definisi `[TALK_TO_ADMIN]` di `# TAG` + pointer ke blok baru.
4. Tambah bullet di `# TAG` SEND_MEDIA: tawaran media proaktif JANGAN ya/tidak, langsung sebut pilihan tipe (tutup sumber ambiguitas).

### Risiko kalau TIDAK dikerjakan
Setiap lead high-intent yang jawab "boleh" atas tawaran foto/video di-handoff prematur → keluar dari flow VIRA, notif admin membanjir, bot senyap. Pola sangat umum (tawar media → user setuju).

### Risiko kalau dikerjakan
Prompt makin panjang (biaya token naik tipis). Regresi yang wajib dijaga: jawaban "boleh" atas tawaran TIM yang sah harus tetap → `[TALK_TO_ADMIN]` (QA #3). Arsitektur tanpa-tool = tetap probabilistik; test suite jadi gerbang.

### QA (gerbang lulus)
Matriks tawaran × jawaban di doc (10 kasus). Gerbang utama: #1 (bug asli — tidak boleh handoff) DAN #3 (regresi — tawaran tim tetap handoff).

### Trigger
Segera — bug lead-facing aktif. Apply saat edit systemMessage berikutnya (gabung dengan patch prompt lain kalau ada, hindari 2 versi prompt saling menimpa). Kalau bikin Main V1.4, satukan.

---

## 24. Follow-up sustainability — siap untuk beban besar (~1000 nomor)

**Status**: DONE DI FILE (2026-07-24) — `workflow/production/VIRA-PCR Follow-up.json` sudah ditulis ulang. Backup asli: `workflow/production/2026-07-24-VIRA-PCR Follow-up.backup.json`. **Sisa: Steven import ke n8n live + isi CONFIG keys baru + tes.**
**Dicatat**: 2026-07-24
**Terkait**: analisis beban follow-up 1000 nomor — versi lama rawan banned Meta + duplicate-send + overrun >1 jam.

### Masalah versi lama
1. Loop sekuensial 6 dtk fix, semua kandidat 1 eksekusi → 1000 nomor ≈ >100 mnt, overlap trigger jam berikutnya.
2. Update STATS SETELAH kirim → race condition → **nomor sama bisa di-follow-up 2×** saat overlap.
3. Kirim gagal tidak ada retry (hangus sampai cycle berikut, tapi bisa dobel).
4. Interval tetap + template identik + gateway Kirimi (tidak resmi) = pola gampang kena flag anti-spam Meta.
5. Gate jam etis hanya dicek di awal → run bisa bleed lewat jam tutup.

### Yang dikerjakan (robust, tanpa ubah struktur sheet / workflow Main)
- **Cap per-run** (`followup_max_per_run`, default 40, plafon 300) + **cap by-time** (auto-berhenti sebelum `followup_close_hour`) → 1000 nomor dicicil lintas jam/hari, 1 run selalu << 1 jam → overlap hilang.
- **Claim-before-send**: node `Update STATS FU` diubah jadi **`Claim STATS FU`**, dipindah SEBELUM kirim (tandai `last_follow_up_ts`+`follow_up_count` dulu). Run yang overlap otomatis skip nomor yang sedang diproses → **anti-duplikat**.
- **Rollback**: node baru `Rollback STATS FU` di error path — kirim gagal → state dipulihkan (`prev_last_fu`, count asli) → dicoba lagi cycle berikutnya, tidak hangus. Tidak ada auto-retry di node Kirimi (hindari dobel pesan saat timeout).
- **Jitter delay** (`followup_min_delay_sec`/`followup_max_delay_sec`, default 8–18 dtk acak) → human-like, smooth load.
- **Personalisasi** `{nama}`/`{name}` di `followup_templates` (opsional; tanpa placeholder = perilaku lama).
- **Robustness**: dedupe baris ganda, prioritas antrian (belum pernah FU dulu → paling lama tak dibalas), `retryOnFail` di semua node Sheets, `onError:continueRegularOutput` di Rollback + Notify (badai error tidak menghentikan loop). Notify diberi keterangan "sudah di-rollback".

### CONFIG keys BARU (tab CONFIG, key/value) — semua opsional, ada default KONSERVATIF
| key | default | fungsi |
|-----|---------|--------|
| `followup_max_per_run` | **20** | maks nomor per jam (plafon keras 300) |
| `followup_min_delay_sec` | **20** | jeda min antar pesan (min 3) |
| `followup_max_delay_sec` | **45** | jeda maks antar pesan |

(`followup_open_hour`/`followup_close_hour`/`followup_interval_hours`/`followup_max`/`followup_templates` tetap seperti sebelumnya.)

> Default diturunkan ke konservatif 2026-07-24 (Steven pilih aman > cepat; Kirimi tetap dipakai). ~20/jam × 13 jam = ~260/hari → 1000 nomor bersih ~4 hari.

### Panduan implementasi
Step-by-step teknis lengkap: **`workflow/production/2026-07-24-panduan-implementasi-followup-scalable.md`** (import, isi CONFIG, uji terbatas + uji anti-dobel + uji rollback, aktivasi, tuning, rollback).

### Sisa / trigger
- Import file baru ke n8n live (ganti Follow-up lama, jangan sampai 2 workflow aktif). Ikuti panduan di atas: uji 2–3 nomor sendiri dulu (Step 5), pastikan anti-dobel lulus, baru aktifkan.
- **Catatan skala**: risiko ban dari Kirimi (gateway tidak resmi) ditekan tapi tidak nol — pemicu terbesar = user Block/Report, bukan volume. Untuk volume tinggi rutin jangka panjang, WhatsApp Business API resmi tetap paling aman.


---

## [2026-08-07] VIRA-PCR V2.0 — Vision (baca gambar dari user)

**Status: menunggu Steven.** Workflow sudah jadi & lulus QA (45/45), belum di-import ke n8n live.

Detail lengkap: `2026-08-07-enhancement-vision-VIRA-PCR.md`
File: `workflow/production/2026-08-07-VIRA-PCR-Main-V2.0-Vision.json` (V1.3 tidak diubah)

### Blocker sebelum aktivasi
1. **Tambah 2 kolom di sheet `MSG_BUFFER`**: E1 = `media_url`, F1 = `media_type` (huruf kecil persis).
   Tanpa ini node `Append MSG_BUFFER` error dan SEMUA chat berhenti, bukan cuma yang bergambar.
2. Non-aktifkan V1.3 sebelum menyalakan V2 (path webhook sama: `wa-inbound-pcr`).

### Belum terverifikasi (butuh 1 tes live)
- Bentuk payload Kirimi untuk pesan gambar. `pinData` yang ada cuma contoh pesan teks, jadi
  `messageType: "image"` + field `mediaUrl` masih **asumsi** (kode sudah menerima beberapa alias:
  `photo`, `imageMessage`, `sticker`, deteksi via `mimetype`, dan alias URL `media_url`/`fileUrl`/`url`).
- Apakah URL media Kirimi bisa diakses publik. Vision memakai `source.type: "url"` — Anthropic yang fetch.
  Kalau ternyata tidak publik, perlu tambahan jalur download -> base64 (patch belum dibuat, menunggu hasil tes).
- **Cara cek:** kirim 1 foto ke bot, lalu di n8n Executions lihat output node `Chat Counter`
  (`media_kind` harus `image`, `media_url` harus terisi), lalu node `Analisa Gambar (Claude Haiku)`.

### Sengaja ditunda
- Logging jumlah panggilan vision / biaya ke sheet STATS (mis. kolom `vision_count`) — baru perlu kalau volume naik.
- Penanganan khusus sticker WhatsApp (sekarang diperlakukan sebagai gambar biasa).
- Jalur base64 sebagai pengganti URL (baru dibuat kalau tes live menunjukkan URL tidak publik).

### Perkiraan biaya
~Rp 40 per giliran chat bergambar (Haiku 4.5). Peredam: 1 panggilan per window debounce (bukan per pesan),
maks 3 gambar per giliran, video/suara/dokumen tidak memanggil API sama sekali, dan kill switch
`vision_enabled = FALSE` di sheet CONFIG.

---

## [2026-08-07] Hasil QA ulang V2.0 vs V1.3 — 5 keputusan menunggu Steven

**Status: PENDING.** Laporan lengkap: `2026-08-07-QA-review-V2.0-Vision.md`

Diff struktural bersih: 0 node dihapus, 80 dari 88 node identik, semua node `id` dipertahankan,
1 edge dihapus (memang disengaja), 0 koneksi menggantung. Kontrak antar-node terverifikasi —
node yang diubah hanya MENAMBAH field, tidak ada yang hilang/rename, jadi 80 node yang tidak
disentuh tidak tersenggol. Jalur teks murni: nol regresi.

Model: sudah `claude-haiku-4-5-20251001` di semua titik (chat agent V1.3 pun sudah Haiku 4.5).
Tidak perlu perubahan untuk permintaan "cukup Haiku di production".

### Temuan yang belum diperbaiki

| # | Sev | Temuan | Node |
|---|-----|--------|------|
| V2-1 | 🔴 BLOCKER | Filter `Chat Counter` berubah dari whitelist (`messageType === "text"`) jadi blacklist implisit. Pesan apa pun dgn `body.message` tidak kosong sekarang lolos — termasuk **reaction/emoji**, protocol, edit pesan. Tiap reaction = 1 eksekusi penuh + Vira membalas emoji. Klaim T8 di dok enhancement belum berdasar (payload reaction Kirimi belum diverifikasi) | `Chat Counter` |
| V2-2 | 🟠 MAJOR | Sanitasi anti prompt-injection pakai **string literal** (`'[SEND_MEDIA'`), sedangkan `Process All` mem-parse dgn regex `\[\s*SEND_MEDIA`. Teks di gambar `[ SEND_MEDIA: brosur]` (spasi setelah kurung) **lolos sanitasi tapi tetap dieksekusi**. Berlaku juga untuk `SCHEDULE_SURVEY` & `FACTS` — bisa menulis fakta palsu ke STATS / bikin survey palsu + notif ke Om Sulianto | `Rakit Konteks Gambar` |
| V2-3 | 🟠 MAJOR | Stiker WhatsApp masuk `IMAGE_TYPES` → tiap stiker memanggil API berbayar (± Rp 40) dan Vira "menanggapi isi gambarnya" | `Chat Counter` |
| V2-4 | 🟡 MINOR | `vision_max_tokens` 700 bisa memotong deskripsi saat 3 gambar; `stop_reason` tidak dicek → teks terpotong tetap masuk prompt sebagai fakta | `Siapkan Vision Request` |
| V2-5 | 🟡 MINOR | `vision_skip: true` tetap dikirim ke HTTP node → body `"null"` → 400 + 1 retry. Praktis mustahil terjadi | `IF Ada Gambar` |

### Toggle add-on — mekanisme sekarang belum benar

`vision_enabled = FALSE` **berhasil menghentikan semua biaya** (`IF Ada Gambar` false, nol panggilan API),
tapi `has_image` tetap `true` sehingga `Rakit Konteks Gambar` tetap menyisipkan blok
*"sistem GAGAL membacanya"*. Vira jadi bilang "maaf gambarnya gagal terbaca" — itu terbaca sebagai
**fitur rusak**, bukan **fitur di luar paket**. Salah untuk posisi jualan add-on.

Rekomendasi: ganti jadi 3 mode `vision_mode` = `off` (persis V1.3) / **`ack`** (media diakui sopan, nol biaya —
default sebelum klien setuju) / `full` (vision aktif, add-on). Patch 5 titik ada di §5.3 laporan QA.
Mode `ack` = klien lihat perbaikan nyata dari V1.3 tanpa biaya token, dan "Vira benar-benar baca isi gambar"
jadi nilai jual add-on yang jelas.

### Sheet — status terkini (dicek dari `workflow/production/PCR_Database.xlsx`)
- `MSG_BUFFER` masih header A–D. **E1 `media_url` + F1 `media_type` belum dibuat** → blocker aktivasi.
- `CONFIG` 29 key, **belum ada satu pun `vision_*`**. Semua default tertanam di `Parse Config`,
  artinya kalau V2.0 diaktifkan apa adanya → **vision langsung ON dan langsung berbiaya**.
- Tab lain tidak berubah. Workflow Cleanup/Follow-up/Error Notifier terverifikasi tidak perlu diubah.

### Keputusan yang ditunggu
1. Apply patch V2-1 (DROP_TYPES)? — rekomendasi **ya, sebelum go-live**
2. Apply patch V2-2 (sanitasi regex)? — rekomendasi **ya**
3. Stiker `image` atau `other`? — rekomendasi **`other`**
4. Toggle 3-mode `vision_mode`, atau cukup `vision_enabled = FALSE`?
5. `vision_max_tokens` 700 atau 1000? — rekomendasi **1000**

### Trigger
Naik prioritas begitu Steven memutuskan mau go-live V2.0. Semua patch di atas kecil (< 30 baris total);
kalau di-approve, keluarkan **V2.1** dengan format byte yang sama (LF murni, key order identik,
`id`/`versionId` baru) supaya V1.3 dan V2.0 tetap utuh sebagai rollback.

> **UPDATE 2026-08-07 (sesi yang sama): kelima keputusan sudah diambil Steven dan V2.1 SUDAH DIBUAT.**
> Semua temuan V2-1 s/d V2-5 **CLOSED**. Lihat blok berikutnya.

---

## [2026-08-07] VIRA-PCR V2.1 — patch QA diterapkan, siap import

**Status: menunggu deploy.** Workflow sudah jadi & lulus harness (23/23), belum di-import ke n8n live.

File: `workflow/production/2026-08-07-VIRA-PCR-Main-V2.1-Vision.json`
Checklist deploy: `2026-08-07-checklist-deploy-V2.1-Vision.md`
Laporan QA yang mendasarinya: `2026-08-07-QA-review-V2.0-Vision.md`
**V1.3 dan V2.0 tidak diubah** — keduanya tetap utuh sebagai rollback.

### Keputusan Steven (2026-08-07)
| # | Keputusan | Hasil |
|---|---|---|
| 1 | Patch `DROP_TYPES` anti-reaction | ✅ diterapkan di `Chat Counter` |
| 2 | Patch sanitasi tag berbasis regex | ✅ diterapkan di `Rakit Konteks Gambar` |
| 3 | Stiker → lampiran biasa (Rp 0) | ✅ pindah ke `OTHER_MEDIA_TYPES`, label `[stiker]` |
| 4 | Toggle 3 mode `vision_mode` | ✅ `off`/`ack`/`full` di 4 node |
| 5 | `vision_max_tokens` → 1000 | ✅ di `Parse Config` |

### Verifikasi
- V2.1 vs V2.0: **92 dari 98 node identik**, 0 node ditambah/dihapus, **koneksi identik 100%**, 0 node `id` berubah.
- V2.1 vs V1.3: 80 node identik, 8 diubah, 10 baru — cakupan sama persis dengan V2.0.
- Format: round-trip byte-identik, 0 CRLF, tanpa BOM, key order sama V1.3, `id` = `pcrV2Vision0021` (baru), `active: false`.
- Harness 23 uji lulus. Sanitasi: V2.0 bocor **4/14** serangan, V2.1 bocor **0/14**.
- Koreksi saat build: mode `off` awalnya masih meloloskan gambar **yang ada captionnya**. Sudah diperbaiki
  jadi setara V1.3 persis (V1.3 membuang semua `messageType != 'text'` tanpa melihat caption).

### ⚠️ Blocker sebelum aktivasi — BELUM dikerjakan
1. **Sheet `MSG_BUFFER`**: tambah E1 = `media_url`, F1 = `media_type`. Sekarang masih header A–D.
   Tanpa ini `Append MSG_BUFFER` error dan SEMUA chat berhenti.
2. **Sheet `CONFIG`**: tambah `vision_mode` = **`ack`** (+ `vision_max_images` 3, `vision_model`,
   `vision_max_tokens` 1000). Sekarang 29 key, belum ada satu pun `vision_*`.
   **Kalau `vision_mode` tidak diisi, kode jatuh ke default `full` → langsung berbiaya.**
3. Non-aktifkan V1.3 sebelum menyalakan V2.1 (path webhook sama: `wa-inbound-pcr`).

### Mode yang dipakai saat go-live
`vision_mode = ack` — bot **tidak diam lagi** kalau dikirim foto (perbaikan nyata dari V1.3 yang jadi
keluhan asli), tapi **nol biaya API**. Naik ke `full` = ubah 1 sel di sheet, tanpa import ulang.
Ini juga jadi bahan demo add-on: rekam layar `ack` vs `full` untuk foto yang sama.

### Masih belum terverifikasi (butuh tes live)
Sama seperti V2.0 — bentuk payload Kirimi untuk pesan non-teks: nilai `messageType` untuk gambar
**dan untuk reaction**, nama field URL, serta apakah URL media Kirimi bisa diakses publik.
Uji #2 (react emoji), #3 (kirim foto), #6 (mode full) di checklist deploy yang membuktikannya.

### Sengaja masih ditunda
- Logging jumlah panggilan vision / biaya ke sheet STATS — baru perlu kalau volume naik.
- Jalur base64 pengganti URL — baru dibuat kalau tes live menunjukkan URL Kirimi tidak publik.
- Pengecekan `stop_reason` pada respons vision (dipilih naikkan `max_tokens` ke 1000 saja).
- Model chat (`Anthropic Chat Model`, `Anthropic Chat Model1`) masih **hardcode** di node, tidak
  bisa diatur dari sheet seperti `vision_model`. Bukan bug, tapi asimetri kalau nanti tuning biaya.

---

## 2026-08-21 — Fix retrieval: VIRA mengarang harga (INSIDEN LIVE)

**File siap-import:** `workflow/production/2026-08-21-VIRA-PCR-fix-retrieval.json`
(`active: false`, `id`/`versionId` baru — **tidak menimpa** workflow live `VIRA PCR.json`)

### Insiden
Lead **+62 812-9121-8300 (Kris)**, 2026-08-21 pagi, sumber Facebook:
- 07:01 VIRA: "Tipe 36/81 komersial harganya mulai **Rp 1.150.000.000**, DP **Rp 230.000.000**" — asli **Rp 409.294.258**
- 07:12 VIRA: "tipe 30/60 subsidi mulai **Rp 420.000.000**, DP **Rp 84.000.000**" — asli **Rp 185.000.000**

Harga asli jauh **lebih murah** dari yang dikutip. Lead kemungkinan mundur karena angka karangan.

### Akar masalah
Node `FAQ Retrieve1` memanggil `grab('Read PRODUK Data')` / `('Read LINKS Data')` / `('Read FAQ')`,
sementara nama node aktual berakhiran `1`. `$(nama)` melempar error, `catch` menelannya, `grab()`
mengembalikan `[]` **tanpa jejak** → `data_context` dan `faq_context` KOSONG untuk **setiap pesan**,
bukan cuma pesan ini. Model diberi prompt tanpa data lalu mengisi sendiri angkanya.

Mekanisme: workflow live di-paste/duplikasi ke kanvas yang sudah berisi node → n8n menambah sufiks
`1` ke **75 dari 81** nama node, tapi string literal di dalam kode JS tidak ikut berubah.
`Process All1` selamat karena memakai `$('Read LINKS Data1')` yang sudah benar.

**Regresi dari entri #8/#9** (2026-07-19: *"FAQ Retrieve sudah bersih dari referensi mati"*) — kelas bug yang sama kembali.

### Batas waktu terdampak
Seluruh export arsip **bersih** (07-15, 07-16, V1.3 07-19 & 07-20, V2.1 08-08 — semua `grab` valid).
Kerusakan **hanya** ada di workflow live. Export bersih terbaru **2026-08-08**.
Tanggal persisnya **belum dipastikan** — perlu dicek di execution history n8n.

### Yang sudah diperbaiki di file siap-import
| # | Paket | Node | Perubahan |
|---|-------|------|-----------|
| 1 | P0 | `FAQ Retrieve1` | `grab()` multi-kandidat nama + `_diag.missing` + `console.error` — tidak lagi senyap |
| 2 | P0 | `FAQ Retrieve1` | `booking fee/dp` naik dari ember MONEY ke **CORE** (selalu dikirim) |
| 3 | P0 | `FAQ Retrieve1` | Header PRODUK menyebut eksplisit ember mana yang sengaja tidak dimuat |
| 4 | P1 | `FAQ Retrieve1` | `needCov` dihitung dari token **domain** (ada di vocabulary FAQ), bukan panjang query mentah |
| 5 | P1 | `FAQ Retrieve1` | `subsidi` dikeluarkan dari grup sinonim `harga`; `komersil`/`komersial` ditambahkan |
| 6 | P1 | `FAQ Retrieve1` | Boost kategori dibetulkan — `Harga & KPR` tidak pernah ada di sheet (aslinya `Harga & Pembayaran` + `KPR`) |
| 7 | P1 | `Preprocess - Context Detection1` | `komersil\|komersial\|subsidi` masuk regex `discussingUnit` |
| 8 | P2 | `Process All1` | **Price guard**: nominal Rp di balasan yang tidak bersumber dari PRODUK/FAQ/pesan user → balasan ditahan, `needs_unknown=true` (menumpang jalur `IF Unknown1` yang sudah ada, tanpa node baru) |
| 9 | P2 | `Process All1` | **Canary**: `_diag.prod==0` / `faq==0` → `console.error` + giliran faktual dijawab aman, tidak diserahkan ke model |

### Verifikasi yang sudah dijalankan
- Simulasi retrieval atas sheet FAQ asli: `"Kris, plnya ka komersil"` LAMA → kosong; BARU → **FAQ row 12 di posisi #1**. `"Gk snggp ka to subsidi"` LAMA → kosong; BARU → FAQ subsidi.
- Simulasi price guard, **10/10 kasus sesuai**: kedua balasan halu asli ter-FLAG; harga benar, parafrase bulat ("Rp 383 juta" vs 383.004.784), cicilan resmi, dan nomor telepon semua lolos.
- Syntax check tree-sitter: **19/19 node Code bersih** di file lama maupun baru, 0 regresi.
- Byte style: round-trip byte-identik terhadap referensi, 0 CRLF, tanpa BOM, key order top-level sama.
- Referensi node mati di file baru: **0**. Tabrakan nama variabel guard: **0**. Hanya 3 node berubah.

### ⚠️ BELUM dikerjakan — wajib sebelum/sesudah aktivasi
1. **Import + tes** file di atas. Nonaktifkan `VIRA PCR` (aktif, id `4ytjVjLQzpcBrp7c`) sebelum menyalakan yang baru — path webhook sama.
2. **Belum diuji di n8n sungguhan.** Tidak ada runtime JS di laptop; validasi sejauh ini statis + simulasi Python. Yang paling perlu dilihat di eksekusi pertama: `_diag` terisi `prod=4, faq=88, links=N` (bukan 0).
3. **Hubungi Kris (+62 812-9121-8300)** — koreksi harga yang telanjur salah. Belum dilakukan.
4. **Audit lead lain** sejak kerusakan mulai (≥ 08-08) lewat execution history n8n / sheet UNKNOWN.
5. `bot_mode` row 268 sekarang `OFF` — pastikan statusnya disengaja sebelum bot dinyalakan lagi untuk nomor itu.

### Sengaja ditunda (P3 — keputusan Steven 2026-08-21: kerjakan P0+P1+P2 dulu)
- **Regression set** ~10 pesan WA nyata + ekspektasi `faq_context` tidak kosong. **Trigger:** sebelum duplikasi/paste workflow berikutnya — tanpa ini kelas bug yang sama akan kembali untuk ketiga kalinya.
- **Evaluasi Haiku vs Sonnet.** Sengaja ditunda sampai P0+P2 jalan, supaya perbandingannya adil (model selama ini tidak pernah menerima data sama sekali). Kandidat lain sebelum ganti model: turunkan `temperature` dari 0.4, dan buang contoh gaya `"...harganya mulai Rp... yaa"` dari system prompt — kalimat halunya meniru template itu persis. **Trigger:** masih ada halusinasi setelah price guard aktif.
- **`surveyNeedsAdminAlert` adalah dead flag** — di-emit `Process All1` tapi tidak dikonsumsi node mana pun (entri #2 lama tampaknya belum tersambung). **Trigger:** saat menyentuh jalur notifikasi survey.
- **Kategori FAQ kosong/tidak konsisten.** Beberapa baris `Kategori` kosong (mis. *"Cicilannya rumah komersil berapa per bulan?"*, *"Syarat KPR rumah komersil apa aja?"*) sehingga tidak pernah kena boost; `"Lokasinya dimana ya?"` masuk `Lingkungan` sedangkan `"Lokasinya dimana"` masuk `Lokasi`. **Trigger:** saat tuning relevansi FAQ berikutnya.

### Tambahan 2026-08-21 — pembersihan sufiks angka pada nama node

**File siap-import FINAL:** `workflow/production/2026-08-21-VIRA-PCR-fix-retrieval-clean.json`
(berisi seluruh fix P0+P1+P2 **plus** nama node yang sudah dibersihkan)
File `2026-08-21-VIRA-PCR-fix-retrieval.json` tetap disimpan sebagai opsi diff-kecil (fix saja, nama node dibiarkan).

**Konfirmasi Steven:** sufiks muncul karena saat import, workflow lama masih ada di kanvas → n8n rename otomatis.

**Mekanisme n8n yang terungkap:** n8n membuang digit di ujung nama untuk mendapat "base", lalu menomori
ulang dari base itu. Karena itu `Download Media 2` menjadi `Download Media ` — **digitnya hilang,
spasinya tertinggal**. Efek sampingnya: node yang bersufiks `1` justru jalur PERTAMA, dan yang berspasi
menggantung adalah jalur KEDUA. Kebalikan dari dugaan intuitif — kalau di-rename manual dengan asumsi
"yang ada 1-nya adalah duplikat", jalur media akan tertukar.

**Peta rename dibangun dari bukti, bukan tebakan:**
| Cara | Cakupan |
|---|---|
| Topologi koneksi (jalur media, target `ai_languageModel`) | 10 node |
| Sufiks `1` dibuang, nama dasar terbukti ada di V2.1 & tidak bentrok | 61 node |
| Pencocokan tetangga (`Wait`→`Wait3`, `Wait4`→`Wait2`, `Wait5`→`Wait1` — tiap satu cocok **unik**) | 3 node |
| Sticky note dinomori ulang per posisi kanvas (0 referensi, aman) | 10 node |
| **Total** | **80 dari 81** (`Send WA + Verify (Kirimi)` memang sudah kanonik) |

Node id tidak bisa dipakai untuk pemetaan — paste meregenerasi semua id (0 dari 81 cocok dengan arsip mana pun.)

**Verifikasi:**
- **164 referensi berkutip** ikut ditulis ulang; setelah itu **159 referensi `$('...')` hidup semua, 0 mati**
- **Topologi identik**: 70 edge, himpunan edge sama persis setelah pemetaan — 0 koneksi bergeser
- 0 nama duplikat, 0 cascade rename, 81 node (tidak ada yang ditambah/dihapus)
- tree-sitter 19/19 node Code bersih; round-trip byte-identik, 0 CRLF, tanpa BOM, key order sama
- `grab()` tetap menyimpan nama lama sebagai kandidat cadangan (`grab('Read FAQ', 'Read FAQ1')`) — tahan kalau nanti ter-rename lagi

**17 nama masih berakhiran angka — ini nama kanonik asli, JANGAN dibersihkan:**
`Wait1/2/3`, `Download Media 2`, `IF Send Media 2`, `Wait Media 2`, `Send Media Kirimi 2`
(cabang media kedua), `Anthropic Chat Model1` (model untuk Summarize Handover), `Sticky Note1–9`.

**⚠️ Saat import:** nonaktifkan dulu `VIRA PCR` (id `4ytjVjLQzpcBrp7c`, masih `active: true`) **dan pastikan
tidak ada workflow VIRA lain terbuka di kanvas** — kalau tidak, sufiksnya muncul lagi persis seperti kemarin.

### Audit ulang 2026-08-21 (putaran 2) — 4 cacat ditemukan di build sendiri, sudah ditutup

**File siap-import FINAL (pakai INI):** `workflow/production/2026-08-21-VIRA-PCR-fix-retrieval-clean-v2.json`
Dua file sebelumnya (`...-clean.json`, `...-fix-retrieval.json`) **superseded** — simpan sebagai rollback saja.

Audit menyeluruh seluruh ~140 titik baca lintas-node. Hasil: bug persis kemarin **tidak bisa terulang
diam-diam** (kandidat ganda + `_diag` + `console.error`; ~135 referensi lain gagal BERISIK → eksekusi
berhenti → `errorWorkflow` kirim WA ke admin, dikonfirmasi tersambung & aktif). **Tapi ditemukan 4 cacat
di kode yang baru dibangun sendiri**, semuanya sudah diperbaiki dan diuji:

| # | Cacat | Akibat | Perbaikan |
|---|---|---|---|
| 1 | `_diag` dideklarasikan DI DALAM `try` `FAQ Retrieve`; `catch` mengembalikan objek tanpa `_diag` → `Process All` baca `undefined === 0` = `false` | **Canary BUTA** persis pada simtom insiden asli, kalau `FAQ Retrieve` gagal karena sebab selain nama node salah | `_diag` dipindah ke luar `try`; `catch` ikut mengembalikannya + `console.error`; kondisi canary kini `!retr._diag \|\| retr.faq_error \|\| _d.error \|\| prod===0 \|\| faq===0` |
| 3 | Guard mengganti `cleanOutput` tapi tidak membatalkan `isScheduleSurvey`/`surveyData` | Survey tetap tertulis ke sheet + tim lapangan dinotif jadwal yang **tidak pernah dikonfirmasi ke user** | Blok guard **dipindah ke sebelum** register survey (L447, sebelum `surveyNeedsAdminAlert`/`surveyPendingWrite`) + helper `batalkanAksi()`. Karena `isScheduleSurvey` mati sebelum `surveyPendingWrite` dihitung, slot pending justru **dipertahankan** — giliran berikutnya bisa konfirmasi ulang. `isRequestCall`/`isTalkToAdmin` sengaja TIDAK dimatikan (jalur eskalasi ke manusia, pakai pesan user mentah) |
| 4 | `_amt()` di `Process All` tidak punya pola `reSep` yang dimiliki `amounts()` di `FAQ Retrieve` | Nominal karangan tanpa kata "Rp" LOLOS: `"harganya 1.150.000.000 Kak"`, `"kisaran 950.000.000 sampai 1.200.000.000"` | `reSep` disalin — kedua regex kini identik |
| 5 | Whitelist hanya memuat `original_message` giliran ini, sementara memory AI 10 turn | **False positive**: balasan BENAR ditahan kalau user menyebut budget lalu AI mengutipnya balik | Whitelist diperlebar ke seluruh teks user giliran ini (`user_message_final` dari buffer debounce + `actualUserMessage`). Kasus lintas-giliran penuh **belum tertutup** — histori itu hanya ada di memory AI Agent, tidak tersedia di `Process All`. Sisa risikonya terlihat (eskalasi `needs_unknown`), bukan senyap |

**Verifikasi v2:** 13/13 kasus guard sesuai (termasuk regresi: nomor telepon, tanggal, URL tetap lolos);
canary menyala di 2 skenario yang dulu buta; 0 TDZ (semua variabel yang disentuh guard dideklarasikan
jauh sebelum L447); hanya 2 node berubah vs `-clean.json` (`FAQ Retrieve`, `Process All`); koneksi identik;
0 referensi node mati; tree-sitter 19/19; round-trip byte-identik, 0 CRLF, tanpa BOM.

### Temuan audit yang BUKAN dari build ini — sengaja tidak disentuh
- **`Resolve User Row` silent-fail (PRIORITAS TINGGI).** `catch` mengembalikan `rows=[]`, hanya `console.warn`.
  Kalau kena, SEMUA user pada eksekusi itu dianggap baru: `bot_mode` jadi `''` bukan `'OFF'` → **bot fail-open
  saat admin sedang HITL manual**; nama/unit/budget/pending-survey ikut reset → VIRA mengulang intro ke user lama.
  **Trigger:** kerjakan sebagai perubahan tersendiri — menyentuh jalur identitas user, di luar cakupan insiden harga.
- **`val()` di `FAQ Retrieve`** mencocokkan kolom dengan `startsWith` mengikuti urutan kolom sheet. AMAN sekarang
  (`Tipe` memang sebelum `Tipe Unit` di sheet LINKS). **Trigger:** kalau urutan kolom LINKS diubah — `val(r,'Tipe')`
  akan salah ambil isi `Tipe Unit`, semua media misklasifikasi jadi link teks, senyap.
- **Dead flag `config.sheet_id`** di `Bootstrap Config` (`1dJWq7iq5PRGRguW6GRAgtclgvhSqppa...`) menunjuk spreadsheet
  BERBEDA dari `documentId` yang benar-benar dipakai semua node Sheets (`1pzGuRZbDXCFSZrHHbiE...`), dan tidak pernah
  dibaca di mana pun. Tidak berbahaya, tapi menyesatkan kalau ada yang mengira itu sumber kebenaran.
- **`faq_error`** kini sudah dikonsumsi canary (sebelumnya di-emit tapi terbuang).
- **`surveyNeedsAdminAlert`** masih dead flag — di-emit `Process All`, tidak dikonsumsi node mana pun.


---

## #26 — Retensi STATS: hapus lead yang 3 bulan tidak membalas VIRA — `PENDING`

**Dibuat:** 2026-08-27 | **Status:** file siap-import, **belum diimport, belum diaktifkan**
**File:** `workflow/2026-08-27-stats-purge/2026-08-27-VIRA-PCR-STATS-Purge-3bulan.json`
+ `2026-08-27-README-stats-purge.md`

### Konteks
Permintaan Steven: hapus seluruh baris STATS yang `last_reply_ts`-nya lewat 3 bulan —
pertanda user berhenti membalas VIRA. Jalan tiap 3 bulan, 4x setahun.

Keputusan yang diambil setelah ditawarkan alternatifnya:
- **Hard delete murni**, bukan arsip-dulu-baru-hapus.
- **Tanpa pengecualian sama sekali** — `bot_mode = OFF`, `survey_status = SCHEDULED`,
  `flag_survey = Y`, dan nomor admin/tim ikut terhapus kalau lewat ambang.
- Baris dengan `last_reply_ts` **kosong** ikut terhapus (dibaca sebagai "belum pernah
  dibalas VIRA sama sekali").

### Risiko kalau TIDAK dikerjakan
STATS terus tumbuh. Node `Read STATS (all)` di Main, Follow-up, dan workflow ini
membaca seluruh tab tiap eksekusi — makin lambat dan makin dekat ke kuota baca Sheets.
Lead mati bercampur lead hidup di laporan klien.

### Risiko kalau DIKERJAKAN
- **Permanen, tanpa arsip.** Baris yang hilang membawa `lead_source`, `unit_interest`,
  `budget_range`, `survey_date`, `flag_survey`, `follow_up_count`.
- **Lead panas ikut hilang** — yang sudah survey atau punya jadwal survey tidak
  dikecualikan. Ini permintaan eksplisit, bukan kelalaian.
- **Lead telemarketer yang belum pernah dibalas VIRA ikut hilang** (kolom
  `last_reply_ts` masih kosong). Ini efek paling mudah terlewat — angkanya wajib
  dicek lewat dry run sebelum diaktifkan.
- Lead yang barisnya hilang lalu chat lagi dianggap user baru: VIRA menyapa dari awal
  dan `follow_up_count` balik ke 0.
- **Bentrok dengan workflow Archive 2026-08-25** kalau dua-duanya aktif — cron di
  tanggal yang sama, dua-duanya menghapus baris STATS.

### Plan
1. Backup tab STATS (Duplicate sheet).
2. Import JSON ke n8n, konfirmasi kredensial `Google Service Account - Persada`.
3. Isi CONFIG `stats_purge_dry_run` = `Y`, Execute Workflow manual, baca laporan WA.
   Cek khusus angka `last_reply_ts kosong` — kalau besar, hentikan dan tinjau ulang.
4. Kalau angka masuk akal: `stats_purge_dry_run` → `N`, aktifkan workflow.
5. Pastikan `VIRA-PCR - STATS Archive 3bulan` tetap non-aktif.

### Trigger
Naik prioritas begitu backup STATS sudah dibuat. Sebelum itu jangan diaktifkan —
tidak ada jalan pulih kalau kriterianya ternyata salah.

### Sudah diverifikasi (statis, belum kena sheet sungguhan)
JSON valid; key order = export live n8n; `id`/`versionId`/`meta.instanceId` terisi;
0 byte CR (LF murni, tanpa BOM); 0 referensi node mati; semua target koneksi ada;
tree-sitter 4/4 node Code bebas syntax error; simulasi blok hapus bawah→atas
300/300 kasus acak cocok.

### Knob kalau berubah pikiran
- `KEEP_WHEN_EMPTY = true` di awal node `Plan purge` → baris tanpa `last_reply_ts`
  dibiarkan hidup.
- CONFIG `stats_purge_retention_days` → ubah ambang (clamp 7–3650), tanpa edit kode.

---

## #27 — Follow-up berbasis konteks AI (Haiku) — `PENDING`

**Dibuat:** 2026-08-27 | **Status:** file siap-import, **belum diimport, belum diaktifkan**
**File:** `workflow/production/VIRA PCR.json` + `workflow/production/VIRA-PCR Follow-up.json`
**Dokumen:** `docs/2026-08-27-followup-konteks-AI-VIRA-PCR.md`
**Panduan eksekusi:** `docs/2026-08-27-README-implementasi-followup-konteks-AI.md`
**Backup pre-patch:** `workflow/arsip/2026-08-27-VIRA-PCR-pre-konteks-AI.json`,
`workflow/arsip/2026-08-27-VIRA-PCR-Follow-up-pre-konteks-AI.json`

### Konteks
Permintaan Steven: follow-up jangan lagi cuma template rotasi, tapi AI yang merangkai
kalimat sesuai apa yang benar-benar dibicarakan calon pembeli.

Akar masalahnya di data, bukan di workflow follow-up. STATS 33 kolom tidak menyimpan
isi pembicaraan sama sekali; `MSG_BUFFER` dibersihkan untuk baris >2 jam; `Simple Memory`
cuma di RAM n8n. Saat follow-up jalan 48 jam kemudian, jejak percakapan nol — jadi
composer secanggih apa pun tidak punya bahan.

Keputusan yang diambil (2026-08-27):
- **Kolom `konteks`** (ringkasan AI berlabel, di-update tiap turn) + **`last_msgs`**
  (3 pesan mentah, ditulis kode) + **`konteks_ts`**. Jangkar mentah itu yang memutus
  drift ringkasan-dari-ringkasan.
- **Compose gagal/melanggar → nomor DILEWATI**, klaim di-rollback, dicoba lagi run
  berikutnya. Bukan fallback ke template.
- **Tidak ada notifikasi bisnis baru.** Notif survey ke admin sudah ada dan sudah pakai
  AI (`Summarize Handover` → `Notify Field Team`) — tidak disentuh.
- Model `claude-haiku-4-5-20251001`, credential `Anthropic Persada` (`8PTYDycbQa8eHLSO`),
  sama dengan yang sudah dipakai.

### Risiko kalau TIDAK dikerjakan
Follow-up tetap terasa pesan massal. Dengan `followup_max = 0` dan lead yang sudah
kena 13x follow-up, template identik berulang adalah pemicu Block paling langsung —
dan Block user adalah pemicu ban Kirimi terbesar, bukan volume.

### Risiko kalau DIKERJAKAN
- **Biaya AI baru.** ~$0,002/pesan masuk + ~$0,0014/follow-up. Realistis di bawah
  $10/bulan pada beban sekarang, tapi naik seiring trafik.
- **AI menulis ke lead sungguhan.** Guard regex menahan nominal/URL/nomor telepon,
  tapi tidak menahan klaim tanpa angka ("harganya masih sama seperti kemarin").
  Karena itu dry run bukan opsional.
- **Loop kegagalan senyap.** Lead yang konteksnya selalu bikin AI melanggar dicoba
  tiap jam selamanya. Diredam oleh laporan run yang cuma bunyi saat ada kegagalan.
- **13 follow-up tetap 13 kali.** Aturan nada "soft di FU ke-6+" meredam, tidak
  menyembuhkan. Menetapkan `followup_max` = keputusan bisnis yang belum diambil.
- `konteks` ikut hilang kalau purge #26 diaktifkan.

### Plan
1. Duplicate tab STATS (backup), lalu tambah 3 kolom `konteks` / `konteks_ts` /
   `last_msgs` — **tanpa spasi di akhir header**.
2. Import Main, cek credential Google + Anthropic tidak unbound, chat uji 3–4 giliran,
   pastikan `konteks` terisi diawali `TOPIK:`.
3. Uji tahan gagal: rusak model sementara → STATS tetap ter-update, `konteks` tidak hilang.
4. CONFIG `followup_ai_dry_run` = `Y`. Non-aktifkan follow-up lama, import yang baru,
   pastikan hanya 1 Active.
5. Execute manual dengan 2–3 nomor uji → **baca hasilnya di WA admin**. Ini gerbangnya.
6. Uji anti-dobel (run kedua harus 0 kandidat) + uji skip (rollback benar).
7. `followup_ai_dry_run` → `N`, aktifkan, pantau Executions hari pertama.

### Trigger
Naik prioritas begitu backup tab STATS sudah dibuat. Sebelum dry run dibaca dan
dianggap layak, jangan diaktifkan.

### Rollback
CONFIG `followup_ai_enabled` = `N` → kembali 100% ke template rotasi lama, tanpa
import ulang. Untuk balik total: import ulang dari `workflow/arsip/2026-08-27-*-pre-konteks-AI.json`.

### Sudah diverifikasi (statis, belum kena sheet/n8n sungguhan)
JSON valid kedua file; key order = export live n8n; `id`/`versionId`/`meta.instanceId`
terisi; **0 byte CR** (LF murni, tanpa BOM); 0 referensi node mati yang hidup; 0 koneksi
dangling; tree-sitter 21/21 (Main) dan 6/6 (FU) node Code bebas syntax error; 0 `.item`;
0 kredensial Kirimi plaintext; 35 cek struktural lolos; **simulasi guard 16/16**
(termasuk `Rp383.004.784`, `15jt`, `2.500.000`, `5%`, `20 tahun`, URL, nomor telepon);
**simulasi rolling `last_msgs` 4/4**; **uji regresi vs file pre-patch 22/22** (0 node lama
hilang, tepat 1 koneksi terputus per workflow di titik sisip, settings/credential/tags utuh).

### Perbaikan hasil review QA (setelah patch awal)
- **STATS jadi 3,6x lebih berat per baca** (61 KB → ~218 KB; Main membaca seluruh tab 3x per
  pesan). Cap sel diperketat (`konteks` 800→500, `last_msgs` 600→450) untuk menahan laju.
  Di 1000 baris jadi ~2,4 MB/eksekusi — purge #26 naik prioritas di titik itu.
- `Catat Kegagalan AI` dulu bisa melaporkan `[object Object]`; sekarang bentuk objek ditangani.
- `Filter Kandidat` estimasi latency +2 → +4 dtk karena ada panggilan Haiku per kandidat.

### Catatan yang gampang terlewat
- `Claim STATS FU` sengaja **tetap sebelum** compose — jaminan anti-dobel tidak bergeser.
- `Merge Konteks` wajib ada: `Update to STATS` membaca `$json.lid` dari item masuk, dan
  output chainLlm berbentuk `{text: ...}` — tanpa node itu kolom `lid` tertimpa kosong.
- Bug lama ikut diperbaiki: `if (!templates.length) return [];` di `Parse Config FU`
  dulu mematikan seluruh run kalau `followup_templates` kosong. Sekarang template hanya
  wajib saat AI mati.
- CONFIG production `followup_interval_hours` = **48**, bukan 72 seperti tertulis di
  `workflow/followup/2026-07-24-panduan-implementasi-followup-scalable.md`.

### Perbaikan dari data live pertama (Gate 1 dijalankan Steven)
- `last_msgs` dulu dipotong dari depan (`slice(0,450)`), memakan sampai 8 char ujung
  giliran TERBARU karena 3x150+8=458>450. Sekarang dirakit dari yang terbaru mundur;
  giliran terbaru dijamin utuh, yang tertua gugur duluan.
- Prompt diselaraskan: `LANGKAH BERIKUT:` -> `LANGKAH BERIKUTNYA:` (itu yang memang
  dihasilkan model; tidak ada yang mem-parse label ini).
- **Catatan semantik penting:** `last_msgs` menyimpan **giliran**, bukan pesan tunggal.
  Satu giliran bisa memuat beberapa pesan hasil gabungan debounce 60 detik, dipisah
  newline di dalam entri yang sama. Jendela 3 giliran bergulir - sel tidak tumbuh terus.
- Isi `konteks` dari data live dinilai **sesuai rancangan**: `LANGKAH BERIKUTNYA` masih
  menyebut dokumen KPR wiraswasta padahal giliran terakhir sudah pindah ke soal parkir.

### QA menyeluruh Follow-up AI Powered (2026-08-27, setelah tes dry run Steven)

**Konteks:** workflow AI diduplikasi di n8n jadi `Follow-up AI Powered`
(id `qaux8b14IgvxEXfoUtxa2`, Active). Yang lama `VIRA-PCR Follow-up`
(id `Ey5WRO8pnOKCVjTHMLq9I`) kini non-aktif dan tanpa AI.

**Dua regresi akibat duplikasi n8n — keduanya sudah diperbaiki:**
1. `Wait FU` kehilangan `"unit": "seconds"`. Ini node jeda anti-banned; menggantungkan
   satuannya pada default n8n tidak bisa diterima. Dikembalikan eksplisit.
2. `settings` kehilangan `timezone` (Asia/Jakarta), `errorWorkflow`
   (`rBsq-mGgHfqfwbz3YmwxI`), `callerPolicy`, `timeSavedMode`. `errorWorkflow` yang
   hilang berarti workflow ini bisa crash **tanpa notifikasi apa pun**. Dipulihkan.
   Ini pengulangan entri #17 - duplikasi/ekspor n8n memang rutin membuang settings.

**Temuan dari tes Steven:**
- "Semua terkirim ke satu nomor" = **dry run bekerja sesuai desain**
  (`followup_ai_dry_run = Y` mengalihkan ke `admin_phone`). Bukan bug.
- Steven mengubah `Kirim Follow-up.phone` jadi `{{ $json.no_wa }}`. Ekspresinya sah,
  tapi **mematikan pengaman dry run** - pesan uji akan langsung ke calon pembeli.
  Dikembalikan ke `{{ $json.target_phone }}`.
- Prefiks `[DRY RUN -> ...]` hanya muncul saat dry run; hilang sendiri saat
  `followup_ai_dry_run = N`.
- **Nama dibuang total** atas permintaan Steven (push name WA sering bukan nama orang):
  `Build FU Prompt` tidak lagi mengirim nama, prompt melarang eksplisit, jalur template
  `{nama}` selalu jadi "Kak", dan `Validate FU Message` menolak pesan yang menyapa
  bernama atau memuat nama lead. Kata umum/merek (persada, cisoka, rumah, unit, ...)
  dikecualikan supaya push name seperti "Cisoka Property" tidak menolak semua pesan.

**Perilaku anti-ban: terverifikasi IDENTIK** dengan versi lama - jeda 20-45 dtk, clamp
min 3 dtk, cap 20/run, plafon 300, gate jam 08-21, interval 72 jam default, dedupe,
exclude nomor tim, `capByTime`, `Claim STATS FU` tetap sebelum compose. Satu-satunya
perbedaan: `Wait FU` kini SESUDAH compose, jadi jarak antar pesan = jitter + latensi LLM
(~1-2 dtk) - **melebar**, arah yang aman. `avgDelay` dinaikkan +2 -> +4 dtk menyesuaikan.

**Pesan dobel (2x "FU ke-1" per nomor di screenshot):** tidak ada jalur kirim ganda di
dalam workflow - rantai `Claim -> Build -> IF -> Compose -> Validate -> Wait -> Kirim`
terverifikasi tunggal, dan `Claim STATS FU` menaikkan `follow_up_count` sebelum kirim.
Dua pesan yang sama-sama "FU ke-1" berarti klaim belum tercatat saat kirim kedua, yang
paling mungkin karena **Execute Workflow dijalankan lebih dari sekali** (baris uji sempat
direset). Cek di menu Executions: kalau ada 2 eksekusi, itu penyebabnya.

**Hasil QA:** 42/42 cek lolos (integritas file, settings, 21 cek perilaku anti-ban,
8 cek temuan Steven) + simulasi guard nama 9/9.

### Mode uji `followup_test_numbers` (2026-08-27, permintaan Steven)
Dry run mengatur **tujuan** (dialihkan ke admin), bukan **cakupan** - seluruh lead tetap
diproses. Ditambah CONFIG `followup_test_numbers`: kalau diisi, `Filter Kandidat` hanya
meloloskan nomor itu. Mode uji menang atas `exclude_numbers` (supaya nomor uji yang
kebetulan terdaftar sebagai admin/tim tidak tersaring diam-diam jadi 0 kandidat tanpa
penjelasan), tapi TIDAK melewati filter bisnis (bot_mode OFF, survey SCHEDULED, interval,
Counter). Saat aktif, `Report FU Run` selalu mengirim pengingat ke admin - lupa
mengosongkannya berarti follow-up berhenti menjangkau lead sungguhan tanpa gejala.
Terverifikasi: simulasi filter 4 skenario lolos; QA 42/42 tetap lolos.

Konfirmasi ulang untuk pertanyaan Steven: **`bot_mode = OFF` memang di-skip**
(`if (/^off$/i.test(String(row['bot_mode'] || '').trim())) continue;`), bersama 10 syarat
lain di `Filter Kandidat`.

---

## 2026-08-31 — Patch `Follow-up AI Powered.json` + 2 perubahan CONFIG yang DITUNDA

**Pemicu:** notifikasi admin `[PCR] FOLLOW-UP AI: 20 dari 20 kandidat dilewati`, semua
beralasan `Error in sub-node Anthropic Chat Model FU`. Credential Anthropic sudah
diperbaiki Steven. Daftar 20 nomornya di-replay ulang terhadap STATS: **cocok persis**,
tidak ada nomor karangan. Rollback juga terbukti jalan (9 baris kembali ke
`follow_up_count = 0`, `last_follow_up_ts` kosong).

### Sudah dikerjakan (masuk ke JSON, backup: `arsip/2026-08-31-Follow-up-AI-Powered.BACKUP.json`)

| # | Node | Perubahan |
|---|------|-----------|
| A | `Anthropic Chat Model FU` | credential -> `Anthropic Persada NEW` (`id: null` supaya n8n mencocokkan by-name, bukan tetap menempel ke credential lama lewat id) |
| B | `Notify Admin FU Summary` | `phone` -> literal `6285155202354` (`Notify Admin FU Error` sengaja TIDAK diubah, tetap `admin_phone` dari CONFIG) |
| C | `Filter Kandidat` | `seen.add(digits)` dinaikkan ke atas + guard `No WA === lid` + panjang 10-15 digit + bawa `antrian_total`/`cap_per_run` ke output |
| D | `Wait FU` | key `disabled` dihapus -> jeda acak 20-45 dtk antar pesan aktif lagi |
| E | `Report FU Run` | notif menyebut backlog nyata: `(cap N per run; antrian layak follow-up masih M)` |

**Kenapa C:** dua bug diam. (1) `seen.add` ada di ujung loop, hanya untuk baris yang lolos
semua filter -> baris `bot_mode = OFF` keluar tanpa mendaftar, sehingga baris KEMBARANNYA
yang `ON` tetap lolos. Nyata pada `6281316625115` (row 80 `OFF` nama `pribadi`, row 225
`ON` nama `User`, `lid` sama) - mematikan bot untuk lead itu tidak berlaku. (2) 17 baris
STATS punya `No WA` berisi nilai `lid` (kontak LID-only), 13 di antaranya mengisi 13 dari
20 slot run. Guard `^62...` sempat dicoba tapi **membuang 1 lead sah** (`966501829592`,
nomor Saudi, nama `Md`), jadi dipakai pengecekan `No WA === lid` yang presisi: menangkap
ke-17 baris, nol false positive.

**Dampak terverifikasi:** antrian 182 -> 168; 14 nomor keluar dari 20 besar (13 lid + 1
kembaran OFF), diganti 14 nomor telepon sah. QA: round-trip byte-identik (LF murni, tanpa
BOM, key order utuh), 23 node & `connections` identik, nol referensi `$('...')` mati,
sintaks 6 node Code lolos tree-sitter.

### DITUNDA — harus diubah di sheet CONFIG, tidak bisa dari JSON

**1. `followup_max = 0` (tanpa batas follow-up)** — STATUS: `DROPPED` (2026-08-31, keputusan Steven: **sengaja 0**, dibiarkan tanpa batas)
- Risiko kalau tidak dikerjakan: dari antrian 168, **80 lead sudah di-follow-up >= 8 kali**,
  32 lead >= 12 kali, tertinggi 15 kali. Selama AI mati sebulan ini efeknya tidak terlihat;
  begitu credential hidup lagi mereka lanjut tiap 48 jam tanpa henti. Risiko ban Kirimi
  (gateway tidak resmi) + lead terganggu.
- Risiko kalau dikerjakan: lead yang sudah lewat batas berhenti di-follow-up permanen -
  perlu keputusan Om Sulianto, bukan keputusan teknis.
- Plan: set `followup_max` = 5 (atau angka yang disepakati) di sheet CONFIG. Efek langsung,
  tanpa perlu re-import workflow.

**2. `followup_max_per_run` tidak ada barisnya di CONFIG** — STATUS: `DROPPED` (2026-08-31, keputusan Steven: default 20 diterima apa adanya, justru itu yang menahan laju kirim demi minimalisir ban Meta)
- Risiko kalau tidak dikerjakan: jatuh ke default 20 di `Parse Config FU`. Angka di
  notifikasi jadi ambigu ("20 dari 20" terbaca seolah cuma ada 20 lead). Patch E sudah
  menambal gejalanya, tapi nilainya tetap tidak terlihat di CONFIG.
- Risiko kalau dikerjakan: nyaris nol.
- Plan: tambah baris `followup_max_per_run` = `20` di sheet CONFIG (plafon kode 300).

### Perlu dicek manual (bukan perubahan)

10 baris lid punya `follow_up_count = 1` dan `last_follow_up_ts` terisi - artinya Kirimi
**menerima** kiriman ke format lid tanpa error (kalau gagal, rollback akan mengosongkannya).
Diterima != sampai. Setelah patch ini mereka tidak akan dikirimi lagi, tapi 17 baris itu
tetap perlu dibereskan datanya: cari nomor WA aslinya, atau arsipkan.

> **Penutup 2026-08-31:** kedua item CONFIG di atas ditutup atas keputusan Steven — tidak
> ada perubahan sheet CONFIG yang tertunda dari sesi ini. Catatan yang tetap berlaku:
> dengan `followup_max = 0`, throttle satu-satunya adalah cap 20/run + `Wait FU` (yang baru
> aktif lagi lewat patch D hari ini) + gate jam 08-21. Sisa yang belum diputuskan hanya
> kebersihan data STATS: 17 baris `No WA == lid`, dan baris kembar `6281316625115`
> (row 80 `OFF` vs row 225 `ON`) — perlu ditentukan baris mana yang sah.

---

## 2026-09-10 — Patch A + C′ `VIRA PCR AI Powered.json`: survey duplikat (Mirna 6285888255459)

### Gejala
Sheet SURVEY dapat 3 row untuk 1 klien, tim lapangan dinotif 3x untuk data yang sama.
Row 1 `created_ts` 1788687331429 = Minggu 2026-09-06 16:35 WIB (tgl_survey 09-13, unit "Subsidi").
Row 2 = Rabu 2026-09-09 20:45:03 (tgl_survey **09-10**, unit 30/60).
Row 3 = Rabu 2026-09-09 20:47:00 (tgl_survey 09-13, unit 30/60). Jarak row 2→3 hanya 117 detik.

### Akar masalah (BUKAN race / bukan duplikat webhook)
Dua `msgId` berbeda (`AC46F204…` "Ini kak jam 3 sore" 20:43:40, `AC96E7AD…` "Hari minggu kaka"
20:45:38), `resolved_key` identik, `buffer_done_ts_old` exec-2 = `process_start_ts` exec-1 →
debounce bekerja benar. Tiga defect asli:

1. **State survey terkonfirmasi tidak pernah kembali ke prompt.** `Cek_user_status` membangun
   `PENDING_SURVEY` HANYA dari `pending_survey_*`; `flag_survey`/`survey_date`/`survey_status`
   = 0 kemunculan. Survey yang sukses justru ditulis `Update STATS Survey` ke keluarga kolom
   `survey_*`, dan `Process All` SENGAJA mengosongkan `surveyPendingWrite` saat booking sukses.
   Bukti graf: dari `IF Schedule Survey` hanya terjangkau `Update STATS Survey → Collect
   Handover Context → Summarize Handover → {Write SURVEY, Format Handover Message → Notify
   Field Team → Log EVENTS Delegated}`; `Merge Konteks`/`Update to STATS` TIDAK terjangkau.
   Akibat: tiap turn bot mulai tanpa ingatan bahwa ia baru saja membooking.
2. **Bot mengarang tanggal.** Exec 20:43 user hanya menyebut JAM. Bot memilih sendiri
   `tanggal="2026-09-10"` ("besok Kamis"). Aritmatikanya benar (baris tabel HARI_KE_TANGGAL
   dipakai dengan tepat) — yang salah adalah MEMILIH tanggal yang user tak pernah minta.
   Karena itu memperbaiki tabel kalender tidak menolong; hanya grounding yang menolong.
3. **`Write SURVEY` append tanpa dedup** (`operation: append`, `matchingColumns: []`), sementara
   `Update STATS Survey` pakai `update` match `No WA` sehingga STATS selalu sembuh sendiri dan
   masalahnya tidak terlihat sampai sheet SURVEY dibuka.

Guard `svHallucinated` yang sudah ada tidak menangkap #2: `mentionsDateTime` kena (ada "jam 3")
dan slot terisi 3, jadi lolos. Guard itu menguji INTENT, bukan SUMBER tanggal.

### Sudah dikerjakan — `workflow/2026-09-10-VIRA-PCR-AI-Powered-patch-A-C-grounding.json`
STATUS: **BELUM DI-IMPORT ke n8n.** File produksi `workflow/production/VIRA PCR AI Powered.json`
TIDAK diubah. Tepat 3 node tersentuh; `connections`/`settings`/`meta`/`pinData`/`id`/`versionId` utuh.

- **A — `Cek_user_status`** (127→146 baris): tambah register #2 dari `debounceRow` (baris STATS
  utuh dari `Re-Read STATS Debounce`, jadi NOL API call tambahan) → `svFlag`/`svStatus`/`svDate`/
  `svTime`/`hasScheduledSurvey`; baris baru `SURVEY_TERJADWAL:` di `[SYSTEM_DATA]`; 3 field output
  `survey_terjadwal_tanggal_db`/`_jam_db`/`_status_db`. Sengaja TANPA TTL (beda dari PENDING_SURVEY).
- **A — prompt `AI Agent`** (17731→19087 chars): 3 aturan baru di `# SURVEY` — arti SURVEY_TERJADWAL
  dan cara memperlakukan koreksi jadwal; "TANGGAL WAJIB BERSUMBER" (hanya dari ucapan user turn ini
  atau dari PENDING_SURVEY/SURVEY_TERJADWAL, DILARANG mengisi sendiri termasuk "besok"); larangan
  memasang tag di pesan yang masih bertanya/menawarkan.
- **C′ — `Process All`** (569→678 baris): guard grounding deterministik sebelum GATE KELENGKAPAN.
  Tanggal tak bersumber → `svTgl` dikosongkan → jatuh ke gate → bot menanyakan harinya. Sengaja
  BUKAN jalur admin-alert ('slot belum lengkap' bukan `AI_FAULT_REASONS`, admin tidak dibanjiri).
  **FAIL-OPEN**: kalau teks user tak terbaca (referensi node berubah nama), guard DILEWATI — satu
  ref mati tidak boleh memblokir SEMUA booking. Flag `svUngrounded` diekspor ke output node.

Sumber tanggal yang diterima: relatif (`hari ini`/`sekarang`/`besok`/`lusa`), nama hari (kemunculan
terdekat + pekan setelahnya), `minggu|pekan depan/ini` (rentang 14 hari), `akhir pekan`/`weekend`,
tanggal eksplisit (`2026-09-13`, `13/9`, `13-09-2026`), `tanggal 15`/`tgl 15`, `20 september`.

### DITUNDA — Paket B: `Write SURVEY` append → appendOrUpdate
- Risiko kalau TIDAK dikerjakan: reschedule yang SAH tetap menambah row baru. A+C′ hanya
  menghentikan row yang DIKARANG, bukan row dari reschedule sah. Row 1–3 yang sudah ada juga
  tidak dibersihkan.
- Risiko kalau dikerjakan: mengubah semantik sheet SURVEY dari log append-only jadi board
  1-row-per-klien. Histori tetap aman karena `Log EVENTS Delegated` sudah append tiap delegasi
  (`detail = 'Survey <tanggal> <jam>'`, `event=DELEGATED`, `ts`). Tidak ada node yang MEMBACA
  sheet SURVEY (hanya `Write SURVEY`), jadi guard baca-dulu akan menambah 1 API call per booking
  sedangkan `appendOrUpdate` match `no_wa` nol call tambahan.
- Plan: `operation: append` → `appendOrUpdate`, `matchingColumns: ['no_wa']`.
- Belum diputuskan: apakah 1 klien boleh punya >1 survey aktif (mis. survey ulang 3 bulan kemudian).

### QA (statis + eksekusi, belum kena n8n sungguhan)
- Sintaks JS 21 code node via tree-sitter: 0 error.
- Gaya byte: LF murni, tanpa trailing newline, key order dan `id`/`versionId` sama seperti asli,
  0 escape `backslash-u`. Round-trip `json.dumps(indent=2, ensure_ascii=False)` terbukti
  byte-identik terhadap file asli sebelum patch.
- Perilaku guard: 22/22 PASS dieksekusi di V8 (`py_mini_racer`), termasuk dua kasus NYATA
  (exec 20:43 diblokir, exec 20:45 diloloskan), 7 kasus regresi, dan kasus FAIL-OPEN.
- **Bug yang tertangkap QA sendiri:** versi pertama blok bulan memakai
  `new RegExp('backslash-b...')` — di JS, backslash-b di dalam STRING literal adalah karakter
  BACKSPACE, bukan word-boundary, jadi polanya gagal senyap (3 karakter U+0008 ikut tertulis ke
  jsCode). Diganti regex literal statis. Ditambah QA-4 permanen: scan karakter kontrol liar
  (U+0000/07/08/0B/0C) di semua jsCode.
- Catatan lingkungan: heredoc shell di sesi ini memakan satu level backslash. Untuk menyuntik JS
  ber-regex, WAJIB pakai Python raw string (`r"""..."""`), atau tulis lewat file.

### Bukan defect (sudah dikonfirmasi Steven 2026-09-10)
`survey_closed_days` tidak pernah didefinisikan di `Parse Config`, jadi `closedDays` selalu `[]`
dan tidak ada hari yang pernah TUTUP. Komentar "Default: Minggu (0)" di `Preprocess - Context
Detection` adalah dokumentasi mati. Steven: survey buka terus, tidak pernah tutup — jadi
perilakunya memang benar, tidak ada yang perlu diubah.

### Perlu dicek manual (bukan perubahan)
Tab CONFIG menyimpan private key service account Google (`kirimi_*` dan blok RSA) sebagai nilai
sel. Siapa pun yang punya akses baca ke PCR_Database bisa membacanya. Perlu diputuskan apakah
kredensial itu dipindah ke n8n credential store.

---

## 2026-09-10 (lanjutan) — V1.5: ganti jadwal survey (B′) + fix kolom berspasi (A2)

File: `workflow/2026-09-10-VIRA-PCR-AI-Powered-V1.5-fix-ganti-jadwal-survey.json`
STATUS: **BELUM DI-IMPORT.** Produksi tidak disentuh. V1.4 tetap ada sebagai langkah antara.
Nama internal workflow sengaja TIDAK diubah (`VIRA PCR AI Powered`, id `oCQ315OHAjQEuG2vh14RR`)
supaya import tidak me-rename workflow live. Versi hanya ada di nama file.

### A2 — kolom `pending_survey_*` berspasi
Header STATS: `'pending_survey_tanggal '`, `'pending_survey_jam '`, `'pending_survey_unit '`
(berakhir SPASI). `Update to STATS` MENULIS dgn nama berspasi (cocok). `Cek_user_status` baris
68-70 dan `Resolve User Row` baris 46-48 MEMBACA tanpa spasi -> selalu undefined -> PENDING_SURVEY
selalu `-`. Register #1 mati sejak awal.
Fix: helper `colPS(obj, base)` di kedua node, baca toleran (berspasi dulu, lalu tanpa spasi).
**Header sheet TIDAK diubah** — mengubahnya akan merusak mapping node penulis dan menuntut
re-map manual di UI n8n. Steven tidak perlu menyentuh sheet.

### B′ — ganti jadwal survey
Keputusan Steven: klien BOLEH survey >1x, jadi `Write SURVEY` **tetap `append`** (bukan
appendOrUpdate). Celahnya: setelah ganti jadwal, sheet SURVEY punya 2 baris `SCHEDULED` bentrok.
- `Process All`: flag `isSurveyReschedule` + `surveyPrev {tanggal, jam}`, diletakkan SESUDAH price
  guard & canary (kalau `batalkanAksi()` sudah mematikan `isScheduleSurvey`, blok ini tidak jalan).
  Syarat reschedule: ada `survey_terjadwal_tanggal_db`, status `SCHEDULED`, jadwal berubah, DAN
  **jadwal lama masih di masa depan**.
- Syarat "masih future" itu WAJIB: kolom `survey_status` tidak punya siklus hidup — 13/13 baris
  SURVEY bernilai `SCHEDULED`, tidak pernah `DONE`. Tanpa syarat itu, klien yang survey lagi 3
  bulan kemudian akan membuat baris survey LAMANYA ditandai RESCHEDULED.
- Node baru `IF Survey Rescheduled` (if 2.2) + `Mark SURVEY Rescheduled` (googleSheets 4.7,
  `operation: update`, match `no_wa`+`tanggal`+`jam` nilai LAMA, set `status=RESCHEDULED`,
  `onError: continueRegularOutput`, `alwaysOutputData`). Dipakai `update` BUKAN `appendOrUpdate`
  supaya no-match tidak menambah baris sampah.
- Cabang paralel dari `Update STATS Survey`; rantai `Collect Handover Context -> Summarize
  Handover -> Write SURVEY` tidak disentuh.

### QA — 72 kasus, SEMUA LOLOS
- Statis (31): sintaks 0 error, 0 karakter kontrol, LF murni, key order/id/versionId/nama internal
  utuh, 86 id unik, **80 node lama byte-identik**, hanya 4 node lama berubah, satu-satunya
  connection lama yang berubah `Update STATS Survey`.
- A2 `Cek_user_status` (6) + `Resolve User Row` (3): kolom berspasi & tanpa spasi dua-duanya
  terbaca, TTL 48 jam tetap jalan.
- B′ matriks ganti jadwal (12), dieksekusi `Process All` UTUH di V8: ganti jam, ganti tanggal,
  jadwal sama, jadwal lama lewat, status DONE, tanggal rusak, C′ blokir, canary outage, pesan biasa.
- Regresi C′ (22): semua masih lolos.

### Bug yang tertangkap QA sendiri (3 di kode, 2 di harness)
1. `new RegExp('backslash-b...')` — di JS backslash-b dalam STRING = BACKSPACE, bukan
   word-boundary. Gagal senyap + 3 karakter U+0008 tertulis ke jsCode. Diganti regex literal.
2. Kolom `pending_survey_*` berspasi (jadi A2).
3. Celah "survey lama dianggap jadwal terbuka" (jadi syarat prevMasihFuture).
4. Harness: stub `FAQ Retrieve` tanpa `_diag` -> canary DATA OUTAGE menyala, 3/6 palsu.
5. Harness: stub `Read STATS` padahal node membaca `$('Read User STATS')`, dibungkus try/catch
   -> `rows=[]` senyap, 2 FAIL palsu.

Catatan lingkungan: heredoc shell di sesi ini memakan satu level backslash. Script patch WAJIB
ditulis sebagai file (bukan heredoc), atau pakai Python raw string.

### Masih TERTUNDA
- Baris SURVEY duplikat yang SUDAH ada tidak dibersihkan otomatis. `Mark SURVEY Rescheduled`
  menandai satu baris yang match; kalau ada dua baris identik `no_wa`+`tanggal`+`jam` (mis. Mirna
  09-13 15:00 dua kali), sisanya tetap `SCHEDULED`. Perlu dibereskan manual.
- `survey_status` tidak punya transisi ke `DONE`. Selama itu belum ada, "jadwal terbuka" hanya bisa
  disimpulkan dari tanggal yang masih di masa depan.
- `Wait3` hardcode 60 detik sementara CONFIG punya `debounce_seconds` — mengubah CONFIG tidak
  berefek ke debounce.

---

## 2026-09-13 — Patch `Follow-up AI Powered`: notif admin berulang tiap jam untuk nomor yang sama

STATUS: **SUDAH LIVE** (dikoreksi 2026-09-16). Isi 5 node ini terbaca di n8n live lewat MCP
(`workflow updatedAt 2026-09-15T07:09Z`): penanda `FU_AI_DITOLAK_GUARD`, `samarkan()`, guard klaim,
ekspresi penundaan di `Rollback STATS FU (AI)` — semuanya cocok. Node id & posisi live TIDAK sama
dengan file, jadi perubahan tampaknya dipasang manual di UI n8n, bukan lewat Import from File.
File: `workflow/2026-09-13-Follow-up-AI-Powered-fix-notif-berulang.json`.
File produksi `workflow/production/Follow-up AI Powered.json` TIDAK diubah (masih versi 31 Agt).

### Gejala
Notif `[PCR] FOLLOW-UP AI: 1 dari N kandidat dilewati` untuk **6289635089520** di setiap run
(12 Sep 15:11 s/d 13 Sep 08:06), lalu **6281290869380** ikut muncul mulai 13 Sep 08:06. Isi notif hanya
potongan pesan + `[line 60]`, tanpa alasan penolakan.

### Akar masalah (terverifikasi dengan data STATS live + kode sumber n8n)
1. **Konteks lead memuat angka yang dilarang guard.** Row 420: `TOPIK: ... tenor 3 tahun`,
   `LANGKAH BERIKUT: Konfirmasi ke tim marketing apakah tenor 3 tahun tersedia`, `last_msgs`
   "klou ngambil 3 tahun bisa g ya kak?". Row 478: "DP 0%", "Rp2.500.000", "15-30 tahun".
2. **Prompt `Compose Follow-up` bertentangan:** WAJIB menyinggung TOPIK konteks vs DILARANG menyebut
   angka tenor. Haiku memilih topik → selalu menulis "tenor 3 tahun" → guard `\b\d+\s*tahun\b` menolak.
3. **Rollback mengembalikan `last_follow_up_ts` ke nilai lama** → nomor tetap jatuh tempo → run
   jam berikutnya mengambilnya lagi dengan konteks sama → gagal sama → notif lagi. Konteks baru
   berubah kalau lead chat lagi, jadi loop ini tanpa akhir (08–21 WIB).
4. **Alasan hilang dari notif:** formatter error node Code n8n versi live (`split(':').reverse()`,
   nodes-base s/d 2025-06 dan task-runner s/d 2026-08) hanya menyisakan teks SETELAH titik dua
   terakhir di baris pertama. `FU_AI_INVALID: tenor :: <pesan>` → `<pesan> [line 60]`. Terbukti:
   potongan di notif tepat 160 char (= `pesan.slice(0,160)`) dan harness mereproduksi notif asli persis.
5. **Temuan tambahan:** 7 versi pesan AI mengaku *"saya sudah cek/konfirmasi ke tim kami"* — tidak
   pernah terjadi. Sumbernya baris `LANGKAH BERIKUT` (rencana, belum dikerjakan). Tertolak hanya
   karena kebetulan ada angka; tanpa angka akan terkirim ke calon pembeli.

Skala: 171 dari 565 baris STATS punya bahan prompt yang memuat pola guard (101 di antaranya
angka/URL/telepon, sisanya nama lead) → semuanya berisiko loop yang sama begitu jatuh tempo.

### Perubahan (5 node + settings; 18 node lain byte-identik & = live n8n)
| Node | Perubahan |
|------|-----------|
| `Build FU Prompt` | Bahan prompt (`konteks`, `last_msgs`, unit, budget, lokasi, sumber, pesan pertama) disamarkan: harga/DP/%/tenor/nominal → `[angka]`, URL → `[link]`, telepon → `[nomor]`, nama lead → `[nama]`. Rentang utuh ("15-30 tahun", "10, 15, 20 tahun"). Jaring terakhir memakai pola guard persis (superset terjamin). Baris `LANGKAH BERIKUT`/`BERIKUTNYA` tidak dikirim ke AI. Tidak ada yang ditulis balik ke STATS |
| `Compose Follow-up` | Prompt: +larangan mengaku sudah cek/tanya/konfirmasi ke tim; +arti token `[angka]` dkk (jangan ditulis/ditebak); topik disinggung TANPA angka |
| `Validate FU Message` | +guard **klaim** (sempit: sudah cek/konfirmasi/tanya/diskusi/hubungi **ke tim/pihak lain**, tim sudah mengecek/memastikan, sudah menelepon). Pernyataan benar seperti "saya sudah kirimkan daftar persyaratannya" SENGAJA lolos. Pesan tolak jadi satu baris tanpa titik dua: `FU_AI_DITOLAK_GUARD (alasan) >> potongan`, maks 150 char. **Keluaran AI kosong tetap memakai error lama persis** (perilaku lama) |
| `Rollback STATS FU (AI)` | `last_follow_up_ts`: kalau alasan memuat `FU_AI_DITOLAK_GUARD` → waktu sekarang (DITUNDA ke jadwal berikutnya, 48 jam); selain itu → `prev_last_fu` seperti lama. `follow_up_count` tetap dikembalikan |
| `Report FU Run` | Baris guard tampil `ditolak guard (alasan) >> ...` tanpa `[line N]`; penutup menyebut DITUNDA N jam. Tanpa kegagalan / mode uji / gagal teknis saja → teks **identik** dengan lama |
| `settings` | `errorWorkflow` `0mp_AdLtInm68RxQUwLqV` + `availableInMCP: true` diambil dari workflow live (file lokal 08-31 masih `rBsq-...`) |

**Tidak berubah:** jadwal, gate jam 08–21, interval 48 jam, cap 20/run, jeda 20–45 dtk, filter
kandidat, urutan antrian, claim-before-send, dry run, mode uji, jalur template (AI mati), jalur gagal
kirim Kirimi, jalur gagal teknis AI (tetap rollback & dicoba lagi tiap jam). **Fail-safe:** kalau
penanda sampai hilang di versi n8n lain, rollback jatuh ke perilaku lama, bukan perilaku rusak.

### UAT — 1668/1668 LOLOS (eksekusi V8 `py_mini_racer`, data STATS & CONFIG live 2026-09-13)
- **A statis (78):** LF/tanpa BOM/gaya byte export, key order, 18 node byte-identik & parameter = live,
  hanya field yang dimaksud berubah, settings = live, 0 karakter kontrol, tree-sitter 0 error,
  semua `$('...')` hidup, `{{ }}` prompt tetap.
- **B1 Build (1133 + 22):** 565 baris live dijalankan kode lama vs baru. 274 baris tanpa pola →
  output identik. Invariant: 0 pola guard tersisa di bahan prompt baru. LANGKAH terbuang, label lain
  utuh. 22 kasus sintetis sulit.
- **B2 Validate (234):** 7 pesan nyata + 17 klaim + 13 kasus guard lama + 34 pesan wajar (termasuk 10
  pernyataan benar dari konteks) + 15 template rotasi. Pesan yang lolos di kode lama → output identik;
  tolakan baru hanya karena klaim; alasan lama tetap tertangkap; 0 template kena guard klaim; dry run,
  AI mati, template kosong, nomor kosong → identik.
- **B3 formatter (123):** 4 varian formatter n8n (port dari kode sumber) × 3 nomor baris × 5 pesan →
  penanda utuh setelah potong 180 di `Catat Kegagalan AI`, rollback = ditunda. Model divalidasi:
  kode lama mereproduksi notif WA asli persis, termasuk kasus multi-baris 6281290869380.
- **B4 Rollback (16):** semua alasan non-guard → sama dengan ekspresi lama.
- **B5 Report (26):** 5 skenario tanpa guard → output identik; guard & campuran → flag identik, teks baru.
- **B6 end-to-end (30):** Parse Config FU + Filter Kandidat ASLI di STATS live. Bug lama direproduksi
  (nomor muncul lagi +1 jam). Patch: di 4 varian formatter, +1/+6/+47 jam bukan kandidat, +48 jam
  kandidat lagi, count tidak naik. Pesan bersih → terkirim ke lead. Gagal teknis & keluaran kosong →
  rollback penuh, kandidat lagi +1 jam (lama). Filter Kandidat hasil identik.

**Belum terverifikasi (butuh n8n sungguhan):** kalimat Haiku dengan prompt baru (non-deterministik),
tulis Sheets ekspresi baru (tipe sama dengan `Claim STATS FU`).

### Langkah import
1. n8n → workflow `Follow-up AI Powered` → ⋯ → **Download** (backup versi live).
2. Toggle **Active OFF**.
3. ⋯ → **Import from File** → `workflow/2026-09-13-Follow-up-AI-Powered-fix-notif-berulang.json` → **Save**.
4. Cek credential: node Sheets = `Google Service Account - Persada`, `Anthropic Chat Model FU` =
   `Anthropic Persada NEW`. Settings → Error Workflow tetap terisi.
5. Toggle **Active ON**.

### Verifikasi setelah import
- Run berikutnya: 6289635089520 dan 6281290869380 **terkirim** (STATS `follow_up_count` naik) ATAU
  muncul SEKALI di notif dengan `ditolak guard (...)`, lalu tidak muncul lagi 48 jam.
- Kalau terkirim, baca pesannya di WA: tanpa angka, tanpa "sudah cek ke tim".
- Catatan mode uji: nomor uji yang ditolak guard juga ditunda 48 jam — kosongkan
  `last_follow_up_ts`-nya kalau mau diuji ulang.

### Rollback
Import ulang backup langkah 1 (atau `workflow/production/Follow-up AI Powered.json` + set ulang
Error Workflow ke `0mp_AdLtInm68RxQUwLqV`).

---

## 2026-09-16 — Patch `Follow-up AI Powered`: lead macet permanen di guard nama + fallback template

STATUS: **MENUNGGU DIPASANG.** Kode siap tempel: `workflow/2026-09-16-fallback-template/*.js`
(3 node Code). File JSON penuh: `workflow/2026-09-16-Follow-up-AI-Powered-fallback-template.json`
— lihat catatan "Cara pasang" soal kenapa tempel lebih disarankan daripada import.
File produksi `workflow/production/Follow-up AI Powered.json` TIDAK diubah.

### Gejala
Notif `[PCR] FOLLOW-UP AI: 1 dari 18 kandidat dilewati` (16 Sep 13:11) untuk **62895413911026**,
alasan `ditolak guard (menyebut nama lead (halo)) >> Halo Kak, saya Vira dari Persada Cisoka
Residence. Saya paham mungkin Kakak sedang sibuk atau masih…`.

### Akar masalah (terverifikasi: kode live via n8n MCP + baris STATS)
1. Kolom `Nama` baris 62895413911026 isinya harfiah **`halo`** (push name WA). `nama_lengkap`,
   `konteks`, `unit_interest` dst. kosong; `Pesan Pertama` cuma template iklan Facebook.
2. Guard nama (b) di `Validate FU Message` mengambil setiap kata ≥3 huruf dari
   `nama_lengkap + Nama`, membuang 28 kata umum (`halo` tidak ada di daftar itu), lalu menolak
   pesan yang memuat kata itu **di mana pun**, case-insensitive. Pembuka paling wajar dalam
   bahasa Indonesia adalah "Halo Kak" → cocok → ditolak.
3. Konteks lead ini kosong dan **tidak berubah sampai dia chat lagi** → AI selalu menulis sapaan
   generik yang sama → ditolak lagi di setiap jatuh tempo. Patch 13 Sep membuat penolakan guard
   menunda 48 jam (bukan tiap jam lagi), jadi bentuknya bukan banjir notif — tapi **loop 48 jam
   tanpa akhir**, dan lead-nya tidak pernah benar-benar di-follow-up.
4. `Rollback STATS FU (AI)` mengembalikan `follow_up_count` ke nilai lama setiap penolakan guard →
   percobaan gagal tidak pernah dihitung → `followup_max` **tidak akan pernah** bisa memensiunkan
   lead yang macet (dan sekarang `followup_max = 0` = tanpa batas).

Skala: dari 405 baris STATS berisi (snapshot 31 Agt), **2 baris** punya nama yang memicu pola ini —
`halo` (62895413911026) dan `selamat jaya las` (6281617576781, kena di kata "selamat").

### Perubahan (3 node Code; 20 node lain byte-identik dengan basis 13 Sep)
| Node | Perubahan |
|------|-----------|
| `Validate FU Message` | **(1)** `UMUM` ditambah 68 kata sapaan/kata umum (`halo`, `hai`, `selamat`, `pagi`, `terima`, `kasih`, `harga`, `cicilan`, …) lewat `.concat([...])` — kata-kata itu berhenti dianggap nama lead. Hanya melemahkan cek (b); sapaan bernama tetap dijaga cek (a) `\bKak\s+[A-Z][a-z]{2,}`. **(2)** FALLBACK: penolakan guard tidak lagi `throw` selama template CONFIG ada — kalimat AI dibuang, diganti template rotasi (`c.message`), lead TETAP dikirimi pesan, klaim `Claim STATS FU` dipertahankan. Template tidak divalidasi ulang (memang memuat angka), persis seperti jalur `followup_ai_enabled = N`. Dicatat ke static data `fu_ai_fail` dengan penanda `FU_AI_FALLBACK_TEMPLATE`. Output +`pakai_template` |
| `Build FU Prompt` | `UMUM_NAMA` ditambah 68 kata yang **identik** dengan daftar di `Validate FU Message` (dijaga UAT statis). Efeknya satu: kata sapaan tidak lagi disamarkan jadi `[nama]` di bahan prompt |
| `Report FU Run` | Kategori ketiga: `isFallback`. Fallback tidak dihitung "dilewati". Judul baru `N dari M kandidat dikirim pakai template, K dilewati`; baris tampil `dikirim pakai template, kalimat AI ditolak guard (alasan) >> …`; penutup menjelaskan pesan TETAP terkirim dan `follow_up_count` naik. Output +`jumlah_fallback`, +`jumlah_dilewati` |

**Tidak berubah:** jadwal, gate jam 08–21, interval 48 jam, cap 20/run, jeda 20–45 dtk, filter
kandidat, urutan antrian, claim-before-send, dry run, mode uji, jalur template (AI mati), jalur
gagal kirim Kirimi, jalur gagal teknis AI, `Rollback STATS FU (AI)`, `Catat Kegagalan AI`.
**Fail-safe:** kalau `followup_templates` kosong, fallback mati sendiri dan perilakunya kembali
PERSIS seperti sekarang (dilewati + ditunda lewat `FU_AI_DITOLAK_GUARD`).

### Perilaku sesudah patch
| Kasus | Sebelum | Sesudah |
|-------|---------|---------|
| Nama `halo`, pesan "Halo Kak, …" | ditolak, ditunda 48 jam, berulang selamanya | **terkirim** (kalimat AI asli) |
| AI menyebut angka/URL/telepon/klaim palsu | dilewati, ditunda 48 jam | **terkirim pakai template**, dilaporkan sekali |
| AI menyebut nama asli lead ("Kak Novi") | ditolak | tetap ditolak → fallback template |
| Keluaran AI kosong (anomali API) | rollback penuh, dicoba lagi run berikutnya | **identik** |
| `followup_templates` kosong | dilewati + ditunda | **identik** |
| Run tanpa kegagalan / mode uji / gagal teknis saja | — | teks notif **identik byte-per-byte** |

### UAT — 596/596 LOLOS (eksekusi V8 `py_mini_racer`, data STATS 31 Agt)
- **A `Validate FU Message` (186 kasus):** 6 nama × 15 pesan × dry-run on/off + 6 kasus khusus.
  Kontrak yang diuji: lama lolos → baru lolos dengan `final_message` identik (44); lama ditolak
  guard → baru mengirim kalimat AI **hanya** kalau seluruh alasannya nama-stopword (6), selain itu
  wajib jatuh ke template dengan alasan tercatat utuh (120); `FU_AI_INVALID`, nomor kosong,
  template kosong, AI mati → pesan error / output **identik byte-per-byte** (16).
- **B `Build FU Prompt` (405 baris STATS nyata):** 405/405 output identik dengan kode lama;
  invarian 13 Sep tetap: **0 pola guard tersisa** di bahan prompt.
- **C `Report FU Run` (5 skenario lama):** tanpa kegagalan / guard saja / teknis saja / campuran /
  mode uji → `notif_text` identik byte-per-byte. Skenario fallback diperiksa manual.
- **D statis:** LF murni, tanpa BOM, tanpa escape `\uXXXX`, urutan key top-level tetap, `id` &
  `versionId` tetap, sintaks JS 6 node Code lolos parse V8, 0 referensi `$('…')` mati, dua daftar
  stopword **identik** (68 kata, tanpa duplikat, tanpa kata <3 huruf), hanya 3 node berubah.

**Belum terverifikasi (butuh n8n sungguhan):** kalimat Haiku/Sonnet dengan konteks nyata
(non-deterministik); pengiriman Kirimi untuk pesan template lewat jalur fallback.

### Cara pasang (disarankan: tempel, bukan import)
Node id & posisi di n8n live **tidak sama** dengan file JSON mana pun di repo ini — kalau
di-Import from File, tata letak kanvas live akan tertimpa. Karena yang berubah cuma isi 3 node
Code, lebih aman ditempel:
1. n8n → `Follow-up AI Powered` → ⋯ → **Download** (backup versi live).
2. Toggle **Active OFF**.
3. Buka node **Validate FU Message** → hapus seluruh isi JS → tempel isi
   `workflow/2026-09-16-fallback-template/Validate-FU-Message.js`.
4. Ulangi untuk **Build FU Prompt** (`Build-FU-Prompt.js`) dan **Report FU Run** (`Report-FU-Run.js`).
5. **Save** → toggle **Active ON**.

Kalau tetap mau lewat import, pakai
`workflow/2026-09-16-Follow-up-AI-Powered-fallback-template.json`, tapi kirim dulu hasil Download
langkah 1 supaya patch di-emit ulang di atas basis live (id & posisi ikut aslinya).

### Verifikasi setelah pasang
- Run berikutnya: **62895413911026** terkirim pesan AI sungguhan (`follow_up_count` naik, tidak
  muncul lagi di notif). Sama untuk 6281617576781 begitu jatuh tempo.
- Kalau ada notif, baca kata kuncinya: `dikirim pakai template` = lead TETAP dapat pesan;
  `ditolak guard` = template CONFIG kosong (periksa `followup_templates`).
- Run tanpa kegagalan tetap **diam total** seperti sekarang.

### Rollback
Import ulang backup langkah 1, atau tempel balik 3 node dari
`workflow/2026-09-13-Follow-up-AI-Powered-fix-notif-berulang.json`.

### Tambalan cepat (opsional, tanpa sentuh workflow)
Kosongkan sel `Nama` baris 62895413911026 di STATS → guard nama tidak punya kandidat → lead itu
lolos di run berikutnya. Hanya menambal 1 nomor, dan bisa tertulis ulang kalau lead-nya chat lagi.
