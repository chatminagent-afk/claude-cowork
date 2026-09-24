# Referensi Ekstraksi Node V4 — untuk Perakitan Workflow n8n Persada Cisoka Residence

**Tanggal:** 2026-07-15
**Sifat dokumen:** referensi teknis mentah untuk agent coding (Opus) yang merakit workflow n8n PCR lewat transformasi terprogram. Bukan desain baru — murni ekstraksi verbatim dari file production, disilangkan dengan kategori reuse/modifikasi/baru dari blueprint.
**Basis:** `2026-07-15-blueprint-VIRA-persada-cisoka.md` §9–10, `2026-07-15-analisis-arsitektur-VIRA-eksisting.md`.

**Folder dump mentah (baca langsung per node):** `D:\Documents\Claude Cowork\Persada Cisoka Residence\draft workflow\_extraction\`
```
_extraction\
  V4\
    V4-top-level.txt              -- top-level keys, settings, meta VIRA V4.json
    V4-node-inventory.txt         -- semua 59 node: name|type|typeVersion|position|flags
    V4-connections.txt            -- adjacency connections lengkap (semua cabang)
    V4-node-params\<Nama Node>.json   -- dump JSON UTUH per node (59 file)
    V4-code-nodes\<Nama Node>.js       -- jsCode UTUH per Code node (13 file)
  TEMPLATE\
    TEMPLATE-top-level.txt / -node-inventory.txt / -connections.txt
    TEMPLATE-node-params\<Nama Node>.json  (59 file)
    TEMPLATE-code-nodes\<Nama Node>.js     (15 file)
```
Semua file di atas dihasilkan oleh parsing terprogram (PowerShell `ConvertFrom-Json`/`ConvertTo-Json`) langsung dari `VIRA V4.json` dan `VIRA_TEMPLATE_v1.json` — isinya identik byte-untuk-struktur dengan JSON asli (bukan ringkasan manual), aman dipakai sebagai sumber copy-paste terprogram.

---

## 1. Inventaris Node V4 Lengkap (59 node)

Kategori mengikuti blueprint §9. **"Tidak disebut eksplisit"** = blueprint tidak menyebut node ini secara spesifik di §9; keputusan reuse/buang perlu dikonfirmasi Opus/Steven (lihat catatan di bawah tabel).

| Nama Node (verbatim) | Type | typeVersion | Kategori (blueprint §9) |
|---|---|---|---|
| Webhook | n8n-nodes-base.webhook | 2.1 | Reuse langsung |
| If From Group | n8n-nodes-base.if | 2.3 | Reuse langsung |
| IF From Me | n8n-nodes-base.if | 2.3 | Reuse langsung |
| IF (Whitelist) | n8n-nodes-base.if | 2.3 (disabled di V4) | **Diganti** oleh `Whitelist Gate` (TEMPLATE) |
| Chat Counter | n8n-nodes-base.code | 2 | Reuse langsung |
| Read User STATS | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung |
| Resolve User Row | n8n-nodes-base.code | 2 | Reuse langsung (★ fondasi identitas) |
| IF Bot Mode Active | n8n-nodes-base.if | 2.2 | Reuse langsung |
| Delete_Pending_Msg_Bot_Off | n8n-nodes-base.googleSheets | 4.7 | Tidak disebut eksplisit — pola sama dgn Delete_Pending_Msg (reuse), disarankan **reuse** |
| Rate Limiter LID | n8n-nodes-base.code | 2 | Reuse langsung |
| Append MSG_BUFFER | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung (★ append-only) |
| Notify User Error | n8n-nodes-base.httpRequest | 4.3 | Tidak disebut eksplisit — pasangan Append MSG_BUFFER gagal, disarankan **reuse** |
| Update Buffer | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung |
| Read STATS for HITL | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung |
| HITL Check | n8n-nodes-base.code | 2 | Reuse langsung |
| Wait3 | n8n-nodes-base.wait | 1.1 | Reuse langsung (60s fixed) |
| Re-Read STATS Debounce | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung |
| IF_Chat_Debounce | n8n-nodes-base.if | 2.3 | Reuse langsung |
| Read MSG_BUFFER | n8n-nodes-base.googleSheets | 4.7 | Tidak disebut eksplisit — bagian inti alur buffer, disarankan **reuse** |
| Cek_user_status | n8n-nodes-base.code | 2 | Reuse langsung |
| Preprocess - Context Detection | n8n-nodes-base.code | 2 | **Modifikasi** (kosakata kelas → properti) |
| Read FAQ | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung |
| Read PROGRAM Data | n8n-nodes-base.googleSheets | 4.7 | **Modifikasi** → `Read PRODUK Data` |
| Read ABOUT Data | n8n-nodes-base.googleSheets | 4.7 | **Modifikasi** → `Read LINGKUNGAN Data` |
| Read LINKS Data | n8n-nodes-base.googleSheets | 4.7 | Tidak disebut eksplisit — tab LINKS di-reuse per §7, disarankan **reuse** |
| FAQ Retrieve | n8n-nodes-base.code | 2 | Reuse langsung |
| Anthropic Chat Model | @n8n/n8n-nodes-langchain.lmChatAnthropic | 1.3 | Reuse langsung (kredensial → Credentials) |
| Simple Memory | @n8n/n8n-nodes-langchain.memoryBufferWindow | 1.3 | Reuse langsung |
| AI Agent | @n8n/n8n-nodes-langchain.agent | 3 | Reuse struktur; **systemMessage ditulis ulang total** |
| Process All | n8n-nodes-base.code | 2 | **Modifikasi** (tambah blok tag baru) |
| IF Send GForm | n8n-nodes-base.if | 2.2 | Tidak disebut eksplisit — cabang GForm **kemungkinan digantikan** oleh "IF Send Brosur/Media" (blueprint §10 diagram B1); GForm tidak relevan untuk properti. **Perlu keputusan Opus/Steven**, jangan asumsikan reuse. |
| Query LINKS for GForm | n8n-nodes-base.googleSheets | 4.7 (disabled di V4) | Sama seperti di atas — bagian cabang GForm, sudah disabled di V4 production |
| Pick GForm Link | n8n-nodes-base.code | 2 (disabled) | Sama seperti di atas |
| IF GForm Resolved | n8n-nodes-base.if | 2.2 (disabled) | Sama seperti di atas |
| Send GForm Link | n8n-nodes-base.httpRequest | 4.3 (disabled) | Sama seperti di atas |
| Send GForm Clarify | n8n-nodes-base.httpRequest | 4.3 (disabled) | Sama seperti di atas |
| Update GForm Sent TS1 | n8n-nodes-base.googleSheets | 4.7 | Sama seperti di atas |
| IF Unknown | n8n-nodes-base.if | 2.2 | Tidak disebut eksplisit — pola [UNKNOWN] dipertahankan per blueprint §alur, disarankan **reuse** |
| Record to UNKNOWN | n8n-nodes-base.googleSheets | 4.7 | Tidak disebut eksplisit — tab UNKNOWN direuse per §7, disarankan **reuse** |
| Wait2 | n8n-nodes-base.wait | 1.1 | Tidak disebut eksplisit — pasangan Record to UNKNOWN, disarankan **reuse** |
| Notify Admin Unknown | n8n-nodes-base.httpRequest | 4.3 | Tidak disebut eksplisit — disarankan **reuse** (ganti nomor admin) |
| Wait1 | n8n-nodes-base.wait | 1.1 | Reuse langsung (5-10s random) |
| Reply Chat Kirimi | n8n-nodes-base.httpRequest | 4.3 | Reuse langsung (★ field `phone`, bukan `receiver`) |
| Check API Response | n8n-nodes-base.code | 2 | Reuse langsung |
| Notify Admin API Error | n8n-nodes-base.httpRequest | 4.3 | Tidak disebut eksplisit — disarankan **reuse** |
| Delete_Pending_Msg_Error | n8n-nodes-base.googleSheets | 4.7 | Tidak disebut eksplisit — disarankan **reuse** |
| Extract & Prepare Data | n8n-nodes-base.code | 2 | Reuse langsung |
| Read STATS | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung |
| Process Counter & Merge Data | n8n-nodes-base.code | 2 | Reuse langsung |
| Update to STATS | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung (kolom STATS bertambah, lihat blueprint §7) |
| Delete_Pending_Msg | n8n-nodes-base.googleSheets | 4.7 | Reuse langsung |
| Update STATS - Greeting Flag | n8n-nodes-base.code | 2 | Tidak disebut eksplisit — disarankan **reuse** |
| IF Update Greeting | n8n-nodes-base.if | 2.3 | Tidak disebut eksplisit — disarankan **reuse** |
| Update Greeting | n8n-nodes-base.googleSheets | 4.7 | Tidak disebut eksplisit — disarankan **reuse** |
| IF Talk To Sam | n8n-nodes-base.if | 2.3 | Tidak disebut eksplisit — pola dipakai ulang utk `[REQUEST_CALL]` (§3), node aslinya (Talk To Sam / HITL manual) disarankan **reuse** juga (fitur HITL tetap ada) |
| Notify Talk to Sam | n8n-nodes-base.httpRequest | 4.3 | Sama seperti di atas — reuse, field `phone` bukan `receiver` |
| Update row in sheet | n8n-nodes-base.googleSheets | 4.7 | Sama seperti di atas — set `bot_mode=OFF` |
| Reply Error | n8n-nodes-base.httpRequest | 4.3 | Reuse langsung |
| Delete_Pending_Msg_Bot_Off1 | n8n-nodes-base.googleSheets | 4.7 | Tidak disebut eksplisit — pasangan Reply Error, disarankan **reuse** |

**Catatan penting soal kategori "tidak disebut eksplisit":** blueprint §9 hanya mendaftar node yang jadi fokus perubahan; node housekeeping (Wait2, Notify Admin Unknown, greeting flag, delete-pending variants) tidak disebut satu-satu tapi jelas termasuk arsitektur inti yang "dipertahankan utuh" per prinsip pondasi blueprint. Cabang **GForm (7 node, sebagian besar sudah `disabled` di V4 production)** adalah satu-satunya area abu-abu nyata — blueprint §10 mengusulkan cabang baru "IF Send Brosur/Media" yang kemungkinan menggantikannya, tapi §9 tidak secara eksplisit bilang "buang node GForm". **Jangan asumsikan** — konfirmasi ke Steven/blueprint FILE 2 (media sending) sebelum reuse/buang cabang ini.

Node dari lapisan **TEMPLATE** (config, fork terpisah — lihat §6 di bawah): `Bootstrap Config`, `Read CONFIG`, `Parse Config`, `Whitelist Gate`.

Node **baru total** (belum ada di V4/TEMPLATE, lihat blueprint §1–6 untuk spesifikasi lengkap): `Detect Lead Source`, `Validate Survey Slot`, node tulis tab `SURVEY`, `IF Schedule Survey`, `Notify Field Team`, `Log Call Request`, `Log EVENTS`, node Summarize (FILE 3), node kirim media (FILE 2), seluruh workflow Follow-Up.

---

## 2. Struktur Connections V4 (adjacency lengkap)

Dump lengkap (semua node, semua cabang termasuk IF true/false): **`_extraction\V4\V4-connections.txt`** (59 baris).

Ringkasan alur utama (bentuk linear, HITL/error branch dipisah):

```
Webhook -> If From Group -[true]-> IF From Me -[true]-> IF (Whitelist) -[true]-> Chat Counter
Chat Counter -> Read User STATS -> Resolve User Row -> IF Bot Mode Active
  IF Bot Mode Active [true/ON]  -> Rate Limiter LID -> Append MSG_BUFFER
  IF Bot Mode Active [false/OFF]-> Delete_Pending_Msg_Bot_Off  (STOP)
Append MSG_BUFFER [out0 ok] -> Update Buffer -> Read STATS for HITL -> HITL Check -> Wait3
Append MSG_BUFFER [out1 gagal] -> Notify User Error
Wait3 -> Re-Read STATS Debounce -> IF_Chat_Debounce
  IF_Chat_Debounce [true/menang] -> Read MSG_BUFFER -> Cek_user_status
  IF_Chat_Debounce [false/kalah] -> (tidak terhubung -> STOP diam-diam)
Cek_user_status -> Preprocess - Context Detection -> Read FAQ -> Read PROGRAM Data
  -> Read ABOUT Data -> Read LINKS Data -> FAQ Retrieve -> AI Agent
AI Agent [main, ok]    -> Process All
AI Agent [error output]-> Reply Error -> Delete_Pending_Msg_Bot_Off1

Process All -> (4 cabang paralel, semua dari output yang sama)
  1) IF Send GForm [true] -> Query LINKS for GForm -> Pick GForm Link -> IF GForm Resolved
       [true]  -> Send GForm Link -> Update GForm Sent TS1
       [false] -> Send GForm Clarify
     (seluruh cabang GForm berstatus disabled di V4 production)
  2) IF Unknown [true] -> Record to UNKNOWN -> Wait2 -> Notify Admin Unknown
  3) Wait1 (SELALU jalan, tanpa IF) -> Reply Chat Kirimi
       [out0 ok]   -> Check API Response
                        [out0 ok]   -> Extract & Prepare Data -> Read STATS
                                       -> Process Counter & Merge Data -> Update to STATS
                                     -> Delete_Pending_Msg
                                     -> Update STATS - Greeting Flag -> IF Update Greeting [true] -> Update Greeting
                        [out1 gagal]-> Notify Admin API Error -> Delete_Pending_Msg_Error
       [out1 gagal]-> Notify Admin API Error (juga)
  4) IF Talk To Sam [true] -> Notify Talk to Sam -> Update row in sheet (bot_mode=OFF)
```

**Titik penting untuk Opus:**
- `Reply Chat Kirimi` (httpRequest v4.3) punya **2 output** (`onError: continueErrorOutput`): out0 = respons apapun (termasuk yang nanti divalidasi `Check API Response`), out1 = exception jaringan → langsung `Notify Admin API Error`.
- `Check API Response` (Code) yang benar-benar menentukan sukses/gagal dari isi body respons Kirimi, throw kalau gagal → ditangkap `onError` di node itu sendiri (harus disetel `continueErrorOutput` juga di versi baru).
- Semua cabang IF yang branch **false**-nya tidak muncul di `V4-connections.txt` berarti **silent stop** by design (drop pesan tanpa balasan) — ini pola sengaja untuk: bukan-teks-dari-luar-grup-non-whitelist (filter awal), debounce loser, talk-to-sam=false, gform=false, unknown=false, update-greeting=false. Pertahankan pola ini kecuali blueprint secara eksplisit minta diubah.

Struktur TEMPLATE (config layer) berbeda hanya di titik ini: `Webhook -> IF From Me -> Bootstrap Config -> Read CONFIG -> Parse Config -> Whitelist Gate -> Chat Counter` (menggantikan `If From Group -> IF From Me -> IF (Whitelist) -> Chat Counter` versi V4 — **perhatikan TEMPLATE bahkan tidak punya node "If From Group"**, jadi filter grup WA harus disisipkan manual saat forking config layer TEMPLATE ke atas logika V4). Dump lengkap: `_extraction\TEMPLATE\TEMPLATE-connections.txt`.

---

## 3. Isi Verbatim Code Node Kunci

Semua jsCode node V4 tersimpan utuh di `_extraction\V4\V4-code-nodes\<Nama Node>.js` (13 file, total 1244 baris). Isi node yang diminta eksplisit oleh brief:

### Resolve User Row (60 baris) — reuse langsung, fondasi identitas
File: `_extraction\V4\V4-code-nodes\Resolve User Row.js`
```js
// ====================================================================
// NODE: Resolve User Row (BARU di V4)
// Identitas user: No WA (phone) = kunci PRIMER, lid = backup.
// Menghilangkan bug fallback rows[0] / match dengan kunci kosong
// yang menyebabkan data user tertukar antar row (kasus Vivipoh/DSS).
// ====================================================================
const cc = $('Chat Counter').first().json;
const digits = v => String(v ?? '').replace(/\D/g, '');
const phone = digits(cc.user_phone);
const lid = digits(cc.user_lid);

if (!phone && !lid) {
  throw new Error('Identitas user kosong (phone & lid tidak ada) - payload webhook tidak dikenal: ' + JSON.stringify(cc.body?.from ?? null));
}

let rows = [];
try {
  rows = $('Read User STATS').all()
    .map(i => i.json)
    .filter(r => r && Object.keys(r).length > 0);
} catch (e) {
  console.warn('⚠️ Read User STATS tidak terbaca:', e.message);
}

// Primer: No WA == phone. Backup: kolom lid == lid.
// Terakhir: No WA == lid (row lama yang tersimpan pakai identitas lid).
let row = null;
if (phone) {
  row = rows.find(r => digits(r['No WA']) === phone) || null;
}
if (!row && lid) {
  row = rows.find(r => digits(r['lid']) === lid)
     || rows.find(r => digits(r['No WA']) === lid)
     || null;
}
// PENTING: tidak ada fallback rows[0]. Tidak ketemu = user baru.

const resolvedKey = row ? String(row['No WA']).trim() : (phone || lid);
const greetingSent = row ? String(row['greeting_sent'] || '').trim().toUpperCase() : '';

console.log(`🔑 resolved_key=${resolvedKey} | row_found=${!!row} | greeting=${greetingSent}`);

return [{
  json: {
    ...cc,
    resolved_key: resolvedKey,
    row_found: !!row,
    bot_mode: row ? String(row['bot_mode'] || '').trim().toUpperCase() : '',
    greeting_sent: greetingSent,
    is_new_user: !row || greetingSent !== 'Y',
    buffer_done_ts: Number(row ? (row['buffer_done_ts'] || 0) : 0) || 0,
    kelas_anak: row ? String(row['kelas_anak'] || '').trim() : '',
    kelas_anak_ts: Number(row ? (row['kelas_anak_ts'] || 0) : 0) || 0,
    program_interest: row ? String(row['program_interest'] || '').trim() : '',
    counter_db: Number(row ? (row['Counter'] || 0) : 0) || 0
  }
}];
```
Untuk PCR: field `kelas_anak`/`kelas_anak_ts`/`program_interest` diganti padanan properti (`unit_interest`/`unit_interest_ts`/`budget_range` — lihat blueprint §7). Struktur resolusi (No WA primer/lid backup, no fallback rows[0], throw kalau kosong) **jangan diubah sama sekali**.

### Chat Counter (70 baris) — reuse langsung
File: `_extraction\V4\V4-code-nodes\Chat Counter.js`. Poin kunci: parsing payload webhook Kirimi (lihat §5 di bawah), filter `messageType !== "text"` → `return []` (drop tanpa balasan — **risiko #7 di analisis arsitektur**, blueprint belum eksplisit memutuskan apakah PCR memperbaikinya), `$vars.chatCounter` kemungkinan dead code (no-op, lihat risiko #8 analisis arsitektur), `process_start_ts = Date.now()` adalah kunci baton-race debounce.

### Cek_user_status (87 baris) — reuse langsung
File: `_extraction\V4\V4-code-nodes\Cek_user_status.js`. Poin kunci: cek ulang `bot_mode` post-Wait3 (HITL titik ke-3), gabung `MSG_BUFFER` antara `buffer_done_ts` (watermark) dan `process_start_ts` sendiri (buang >30 menit basi via `MAX_AGE_MS`), TTL 60 hari untuk `kelas_anak`/`program_interest` (untuk PCR: ganti field jadi `unit_interest`/`budget_range`, TTL bisa dipertahankan atau disesuaikan bisnis properti), intro user-baru hardcode string `INTRO` (untuk PCR: ganti isi kalimat, mekanisme `IS_NEW_USER` dipertahankan).

### Preprocess - Context Detection (247 baris) — **MODIFIKASI**
File: `_extraction\V4\V4-code-nodes\Preprocess - Context Detection.js`. Struktur regex-multi-match dipertahankan sebagai teknik (lihat blueprint §9), tapi seluruh kosakata harus diganti:
- `GRADE_PATTERNS` (kelas SD/SMP/SMA/Primary/Sec + angka romawi) → ganti jadi pattern tipe unit/budget/lokasi.
- `PROGRAM_OF` mapping kelas→Junior/Intermediate/Seniors → ganti mapping unit→tipe rekomendasi (atau dibuang kalau PCR tidak butuh derivasi otomatis).
- `outOfScope` (deteksi "mahasiswa/kerja/dst" di luar jenjang) → ganti logika out-of-scope properti (kalau ada).
- `persuasionMode` (INTERESTED/DEFER/PAYMENT) → generik, bisa dipertahankan strukturnya.
- Blok `aiContext` (pembentukan `[CONTEXT: ...]`) → isi kalimat perlu ditulis ulang sesuai domain properti tapi mekanismenya (suntik context block sebelum `[USER QUERY]`) dipertahankan.

### Process All (382 baris) — **MODIFIKASI** (tambah blok tag baru)
File: `_extraction\V4\V4-code-nodes\Process All.js`. Struktur blok yang ADA di V4 (dipertahankan sebagai pola untuk tag baru):
1. Ekstrak `aiOutput` dari `item.json.content[0].text` (fallback `.output`/`.text`).
2. Tag `[SEND_GFORM: Nama Link]` — regex match + fallback pattern-matching (daftar `forgotTagPatterns` kalau AI lupa tag/nyebut `forms.gle`). **Analog** untuk `[SCHEDULE_SURVEY]`/`[REQUEST_CALL]` (blueprint §1.2, §3.2).
3. Tag `[TALK_TO_SAM]` — regex + fallback pattern list.
4. Tag `[MOCK_INTERVIEW_BOOKING]...[/MOCK_INTERVIEW_BOOKING]` (parser key:value dipisah `|`) — legacy, tidak relevan PCR, boleh dibuang.
5. Tag `[UNKNOWN]`.
6. Tag `[FACTS kelas="..."]` + **merge union+TTL** (`KELAS_WL` whitelist label kanonik, gabung `aiFactsKelas` + `regexGrades` (dari Preprocess) + `existingFresh` (dari DB) → dedup → urut kanonik). **Pola ini di-reuse langsung** untuk `unit_interest`/`budget_range` (blueprint §7), ganti `KELAS_WL`/`KELAS_PROG` jadi whitelist tipe unit.
7. Tag `[PENDAFTARAN]...[/PENDAFTARAN]` dan `[DATA_COMPLETE]...[/DATA_COMPLETE]` — legacy, kemungkinan tidak relevan PCR.
8. **Clean output**: strip semua tag dari teks balasan user, lalu hapus kalimat yang membocorkan proses internal (`internalKeywords` list eksplisit — **jangan** ditambah frasa percakapan wajar, lihat komentar V4 FIX di kode), lalu **guard anti-kosong** (`preInternalStrip` — kalau filter menghapus semua, kembalikan versi sebelum filter atau coba "rescue" isi setelah titik dua).
9. Clean markdown (bold/italic/strikethrough/code → plain, dash/semicolon → koma), mask-unmask URL supaya tidak ikut ke-strip.
10. Safety net register netral (buang vokatif "Om/Tante/Bapak/Ibu/Pak/Bu/Ayah/Bunda" yang lolos dari prompt) — **untuk PCR ini mungkin dibalik** kalau persona properti pakai sapaan (keputusan bisnis, lihat blueprint §11).
11. Fallback pesan kalau `cleanOutput` tetap kosong.
12. **Resolve & inject GForm link inline** dari `Read LINKS Data` (match nama link case-insensitive + substring, default ke "pendaftaran batch" kalau AI tidak sebut nama) — pola data-driven ini **layak ditiru** untuk resolve slot/link lain di PCR.
13. Return object: spread `chatCounter` + `preprocess` + `item.json`, plus semua flag tag (`isSendGForm`, `isTalkToSam`, `isUnknown`, dst) dan `kelas_anak_merged`/`program_interest_merged`/`kelas_changed` — field terakhir ini yang dibaca `Update to STATS`. Untuk PCR, field baru (`isScheduleSurvey`, `surveyData`, `isRequestCall`, dst — lihat blueprint §1.2/§3.2) ditambahkan ke object return yang sama, DAN node `Update to STATS`/node baru (`Write tab SURVEY`, dst) harus dibuat untuk membaca field-field baru itu.

### Extract & Prepare Data (27 baris) — reuse langsung
File: `_extraction\V4\V4-code-nodes\Extract & Prepare Data.js`. Sederhana: re-extract `user_wa`/`user_name`/`user_message` dari `Chat Counter` untuk kebutuhan re-read STATS pasca-reply (siklus `Update to STATS`).

### Process Counter & Merge Data (98 baris) — reuse langsung
File: `_extraction\V4\V4-code-nodes\Process Counter & Merge Data.js`. Menghitung `Counter`/`Intensitas Chat` increment, cari `existingRow` dengan pola matching sama seperti `Resolve User Row` (No WA primer/lid backup — **konsisten**, catatan di komentar kode: "V4 FIX: matching row No WA primer/lid backup"), pertahankan `Tanggal Chat Pertama` lama (bug lama: field itu ke-reset tiap pesan karena baca kolom salah — sudah difix di V4), error → `return []` (bukan tulis row "ERROR" ke sheet, V4 FIX lain).

### FAQ Retrieve (126 baris) — reuse langsung
File: `_extraction\V4\V4-code-nodes\FAQ Retrieve.js`. Struktur: baca `Read PROGRAM Data` (→ `Read PRODUK Data` di PCR) untuk blok `STATUS & BATCH` (selalu tampil) + blok `HARGA`/`SYARAT`/`PROGRAM detail` (kondisional berdasar flag dari Preprocess: `askingPrice`, `askingSyarat` regex lokal, dst), blok `TENTANG SAM` dari `Read ABOUT Data` (→ `Read LINGKUNGAN Data`), blok `LINK AKTIF` dari `Read LINKS Data` (filter `Status` match `aktif|active|on|ya`). Lalu **retrieval FAQ lexical/TF-IDF custom**: tokenizer Bahasa Indonesia dengan stemmer sufiks/prefiks manual (`stem()`), kamus sinonim per grup topik (`GROUPS`/`SYN`), skor IDF + boost per kategori FAQ, threshold `FLOOR=2.5` + `needCov` (minimal token match) sebelum FAQ context disertakan. Helper `val(row, ...keys)` melakukan fuzzy column-name match (case-insensitive, prefix match) — berguna kalau nama kolom sheet PCR sedikit berbeda casing. **Seluruh mesin retrieval ini generic**, hanya nama-nama kolom sumber (`Nama Program`→misal `Tipe Unit`, dst) dan kamus `GROUPS` sinonim yang perlu disesuaikan domain properti.

---

## 4. Konfigurasi Node Non-Code Penting

### Webhook
```json
{ "httpMethod": "POST", "path": "=wa-inbound", "options": {} }
```
`typeVersion: 2.1`. PCR pakai path baru (blueprint §0): `wa-inbound-pcr`.

### AI Agent
- `type: @n8n/n8n-nodes-langchain.agent`, `typeVersion: 3`.
- `parameters.promptType: "define"`, `parameters.text: "={{ $input.item.json.ai_input_text }}"` — **AI Agent membaca field `ai_input_text`** yang disiapkan node upstream (`Cek_user_status` → `Preprocess` override). Pastikan node baru PCR tetap mengisi field ini dengan nama persis sama.
- `parameters.options.systemMessage` (~9.000 kata, dump utuh di `_extraction\V4\V4-node-params\AI Agent.json`) — struktur blok: `# SAM` (identitas) → `# IDENTITAS` (meta-pertanyaan) → `# SUMBER FAKTA` (anti-halusinasi) → `# ALUR` → `# INTRO USER BARU` → `# REGISTER NETRAL` → `# GAYA SAM` → `# REKOMENDASI PROGRAM` → `# BATCH` → `# HARGA` → `# TAG` → `# LARANGAN` → ekor `# DATA TERVERIFIKASI` (`{{ $json.data_context || '(tidak ada data terlampir)' }}`) → `# FAQ RELEVAN` (`{{ $json.faq_context || '...' }}`). **Ekor dua variabel ini (`data_context`, `faq_context`) WAJIB dipertahankan persis** — itu yang diisi `FAQ Retrieve`.
- `onError: "continueErrorOutput"`, `retryOnFail: false`, `maxTries: 2` — output error terhubung ke `Reply Error`.

### Anthropic Chat Model
```json
{
  "model": { "value": "claude-sonnet-4-6", "mode": "list", "cachedResultName": "Claude Sonnet 4.6" },
  "options": { "maxTokensToSample": 512, "temperature": 0.7 }
}
```
`typeVersion: 1.3`. Kredensial `anthropicApi` (id `DPNnlN1bTbbMf8ks`, name "Anthropic account") — untuk PCR harus dibuat credential baru terpisah atau reuse (tergantung apakah 1 akun Anthropic dipakai lintas klien). Catatan analisis: `maxTokens 512` mungkin perlu dinaikkan untuk PCR (simulasi KPR bisa lebih panjang, lihat risiko #10).

### Simple Memory
```json
{ "sessionIdType": "customKey", "sessionKey": "={{ $('Resolve User Row').first().json.resolved_key }}", "contextWindowLength": 10 }
```
`typeVersion: 1.3`. Session key = `resolved_key` dari `Resolve User Row` — **pertahankan referensi node ini persis** (kalau nama node `Resolve User Row` diganti di PCR, expression ini harus ikut diupdate).

### Reply Chat Kirimi (V4 production — hardcode)
```json
{
  "method": "POST",
  "url": "https://api.kirimi.id/v1/send-message",
  "bodyParameters": { "parameters": [
    { "name": "user_code", "value": "KM40LI0426" },
    { "name": "secret", "value": "REDACTED" },
    { "name": "device_id", "value": "D-4ZV1F" },
    { "name": "phone", "value": "={{ $('Chat Counter').first().json.user_wa }}" },
    { "name": "message", "value": "={{ $('Process All').item.json.cleanOutput }}" }
  ]},
  "options": { "timeout": 60000 }
}
```
**★ Field penerima bernama `phone`, BUKAN `receiver`.** Berlaku sama persis di semua node HTTP Kirimi (Reply Chat Kirimi, Notify Talk to Sam, Notify Admin Unknown, Notify Admin API Error, Notify User Error, Reply Error, error-workflow, Send GForm Link). `alwaysOutputData: true`, `continueOnFail: true`, `onError: "continueErrorOutput"` — output kedua (gagal) terhubung ke `Notify Admin API Error`.

### Reply Chat Kirimi (TEMPLATE — pola credential-based, DIREKOMENDASIKAN untuk PCR)
```json
{
  "bodyParameters": { "parameters": [
    { "name": "phone", "value": "={{ $('Chat Counter').item.json.user_wa }}" },
    { "name": "message", "value": "={{ $('Process All').item.json.cleanOutput }}" }
  ]},
  "authentication": "genericCredentialType",
  "genericAuthType": "httpCustomAuth",
  "credentials": { "httpCustomAuth": { "id": "REPLACE_WITH_KIRIMI_CUSTOM_AUTH_CRED_ID", "name": "Kirimi Custom Auth (REPLACE per client)" } }
}
```
TEMPLATE sudah memindahkan `user_code`/`secret`/`device_id` ke **n8n Custom Auth Credential** (bukan `bodyParameters` plaintext) — hanya `phone`/`message` yang tetap jadi body params dinamis. **Ini pola yang harus dipakai PCR** sesuai prinsip pondasi blueprint #4 (semua secret Kirimi → Credentials). Semua 8 node HTTP Kirimi lain (Notify Talk to Sam, Notify Admin Unknown, dst) di TEMPLATE mengikuti pola credential yang sama — cek `_extraction\TEMPLATE\TEMPLATE-node-params\Notify*.json` dsb untuk verbatim per node.

### Notify Talk to Sam (V4, contoh notif internal)
```json
{ "name": "message", "value": "={{ \"🙋 [VIRA] MAU NGOMONG LANGSUNG SAMA SAM :\\n\" + $('Chat Counter').first().json.user_wa + \"\\n\" + $('Chat Counter').first().json.user_name + \"\\nPesan: \" + $('Cek_user_status').first().json.user_message_final }}" }
```
Nomor tujuan hardcode `6596110395` (Sam) di V4 — untuk PCR ganti jadi expression `{{ $('Parse Config').first().json.config.admin_phone }}` (atau `field_team_phone` untuk delegasi survey, per blueprint §6).

### Google Sheets — pola umum (semua 20+ node googleSheets V4)
- `authentication: "serviceAccount"`, credential `googleApi` id `3gTKMbD8lJDLbRqR` name "Google Service Account thescholars" — **untuk PCR ganti ke service account/credential baru** kalau spreadsheet beda akun, atau reuse kalau sama akun Google.
- `documentId.value` = Sheet ID hardcode `1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE` (mode `list`) di **V4 production**; di **TEMPLATE** memakai expression `={{ $('Bootstrap Config').first().json.sheet_id }}` (mode `id`) — **PCR wajib pakai pola TEMPLATE ini**.
- `sheetName.value` kadang berupa **gid numerik** (`56867128` utk STATS dsb, mode `list`) di V4, kadang **nama string** (`"MSG_BUFFER"`, mode `name`) di node lain — tidak konsisten. Untuk PCR sheet baru, pakai mode `name` konsisten (gid akan berubah otomatis kalau sheet di-duplicate/rebuild).
- Operasi yang dipakai: `append` (default, MSG_BUFFER/UNKNOWN — append-only), `appendOrUpdate` + `matchingColumns:["No WA"]` (STATS — **pola standar write, hindari read-then-decide-append manual**), `update` + `matchingColumns:["No WA"]` + `row_number:0` (Update row in sheet/Update Greeting/Delete_Pending_* — update in-place tanpa append), plain read tanpa operation (Read STATS/Read FAQ/dst — baca semua baris), read dengan `filtersUI.values[].lookupColumn/lookupValue` (Read MSG_BUFFER, Re-Read STATS Debounce — baca baris terfilter server-side, lebih hemat kuota daripada baca semua lalu filter di Code).
- Contoh field mapping `Append MSG_BUFFER` (operation `append`, `matchingColumns: []` — kosong karena append selalu insert baru):
  ```
  no_wa: {{ $('Resolve User Row').first().json.resolved_key }}
  lid:   {{ $('Chat Counter').first().json.user_lid }}
  message: {{ $('Chat Counter').first().json.original_message }}
  ts:    {{ $('Chat Counter').first().json.process_start_ts }}
  ```
- Dump JSON lengkap (termasuk `schema` array kolom penuh, berguna untuk generate node baru dengan kolom PCR) ada di tiap `_extraction\V4\V4-node-params\<Nama Node>.json`, contoh yang sudah diverifikasi: `Read User STATS.json`, `Append MSG_BUFFER.json`, `Update Buffer.json`, `Update to STATS.json`, `Read FAQ.json`, `Read PROGRAM Data.json`, `Read ABOUT Data.json`, `Read LINKS Data.json`, `Update row in sheet.json`, `Update Greeting.json`, `Delete_Pending_Msg.json`, `Record to UNKNOWN.json`, `Read MSG_BUFFER.json`, `Read STATS.json`, `Re-Read STATS Debounce.json`, `Read STATS for HITL.json`.

### Wait nodes
| Node | amount (parameter) | Catatan |
|---|---|---|
| Wait1 | `={{ Math.floor(Math.random()*(10-5+1))+5}}` (detik, default unit) | jeda acak 5-10 detik sebelum `Reply Chat Kirimi` — anti-terlihat-bot |
| Wait3 | `60` (angka literal) | debounce fixed 60 detik — **jangan diubah ke rolling/relatif** tanpa alasan kuat, ini kunci mekanisme baton-race |
| Wait2 | tidak dibaca detail di ekstraksi ini tapi pola sama Wait1 (jeda sebelum Notify Admin Unknown) — cek `_extraction\V4\V4-node-params\Wait2.json` |

### IF nodes — kondisi kunci (verbatim expression)
| Node | Kondisi |
|---|---|
| If From Group | `{{ $json.body.isFromGroup }}` equals `false` |
| IF From Me | `{{ $json.body.isFromMe }}` equals `false` |
| IF (Whitelist) [disabled] | `{{ $json.body.from }}` equals salah satu dari 5 nomor hardcode (OR) |
| IF Bot Mode Active | `{{ $('Resolve User Row').item.json.bot_mode }}` **notEquals** `"OFF"` |
| IF_Chat_Debounce | `{{ $('Re-Read STATS Debounce').first().json.timestamp }}` equals `{{ $('Chat Counter').first().json.process_start_ts }}` — **inilah baton-race**: hanya eksekusi yang timestamp-nya masih sama dgn saat re-read yang lolos |
| IF Talk To Sam | `{{ $json.isTalkToSam }}` is true (boolean singleValue) |
| IF Send GForm | `{{ $json.isSendGForm === true }}` equals `true` |
| IF Unknown | `{{ $json.needs_unknown }}` equals string `"true"` (bukan boolean — hasil dari `Process All` yang set `needs_unknown: isUnknown ? 'true' : 'false'`) |

### Notify Talk to Sam / Update row in sheet
Trigger dari `IF Talk To Sam` (true). `Notify Talk to Sam` kirim WA ke nomor hardcode Sam (`6596110395` di V4). `Update row in sheet`: operation `update`, set `bot_mode: "OFF"` (matchingColumns `No WA`) — inilah yang mengaktifkan HITL manual. Untuk PCR pola sama dipakai untuk cabang B6 (`IF Talk To Admin`) di diagram blueprint §10.

---

## 5. Payload Webhook Kirimi (kontrak input persis)

Dari `Chat Counter.js` (satu-satunya titik parsing body webhook) dan referensi `$json.body.*` di IF nodes:

| Field | Dipakai di | Catatan |
|---|---|---|
| `body.message` | Chat Counter → `userMessage` | teks pesan |
| `body.messageType` | Chat Counter (filter) | **HANYA `"text"` diproses**; selain itu `return []` (drop total, tanpa balasan — lihat risiko #7 analisis arsitektur) |
| `body.from` | Chat Counter → `userNumber`; juga dibaca langsung `$json.body.from` di `If From Group`/`IF From Me`/`IF (Whitelist)` (tapi 2 IF pertama pakai `isFromGroup`/`isFromMe`, bukan `from`) | bisa berupa nomor telepon polos ATAU format `...@lid` — **passthrough, jangan di-strip manual** |
| `body.originLid` | Chat Counter → `userLid` (kalau ada, atau diturunkan dari `from` kalau `from` mengandung `@lid`) | LID eksplisit |
| `body.name` / `body.pushName` / `body.notifyName` | Chat Counter → `userName` (ambil yang pertama ada, fallback `"User"`) | nama tampilan |
| `body.isFromMe` | Chat Counter → `isFromMe`; juga `$json.body.isFromMe` langsung di node `IF From Me` | boolean |
| `body.isFromGroup` | `$json.body.isFromGroup` di node `If From Group` | boolean |
| `body.event` | Chat Counter → `eventType` (disimpan, tidak dipakai aktif) | — |

Logika turunan penting di `Chat Counter.js`:
```js
const _isLid    = String(userNumber).toLowerCase().includes('@lid');
const userLid   = String(body.originLid || (_isLid ? userNumber : '')).replace(/\D/g, '');
const userPhone = _isLid ? '' : String(userNumber).replace(/\D/g, '');
```
Kalau `from` mengandung `@lid`, `userPhone` dikosongkan dan `userLid` diisi dari `from` itu sendiri (atau `originLid` kalau ada) — ini alasan `Resolve User Row` butuh 2 jalur pencarian (phone lalu lid).

---

## 6. Lapisan Config TEMPLATE (fork untuk PCR)

Dump lengkap: `_extraction\TEMPLATE\TEMPLATE-code-nodes\{Bootstrap Config,Parse Config,Whitelist Gate}.js` dan `_extraction\TEMPLATE\TEMPLATE-node-params\{Bootstrap Config,Read CONFIG,Parse Config,Whitelist Gate}.json`.

### Bootstrap Config (Code)
```js
const SHEET_ID = 'PASTE_CLIENT_GOOGLE_SHEET_ID_HERE';   // <-- EDIT INI per klien
const wh = $input.first() ? $input.first().json : {};
return [{ json: { ...wh, sheet_id: SHEET_ID } }];
```
**Satu-satunya titik edit manual per klien** — untuk PCR ganti `SHEET_ID` ke Sheet ID `Persada_Cisoka_Database` (blueprint §7).

### Read CONFIG (Google Sheets)
```json
{
  "authentication": "serviceAccount",
  "documentId": { "value": "={{ $('Bootstrap Config').first().json.sheet_id }}", "mode": "id" },
  "sheetName": { "value": "CONFIG", "mode": "name" }
}
```

### Parse Config (Code)
Baca semua baris tab `CONFIG` (kolom `key`/`value`, case-insensitive), bangun objek `config` dengan helper `str()`/`num()`/`bool()`/`jsonArr()` (semua punya default aman). Key warisan (lihat blueprint §8 untuk daftar key PCR baru yang perlu ditambahkan ke helper ini): `client_name`, `system_prompt`, `status_question` (**buang untuk PCR**, relik PARENT/STUDENT), `admin_phone`, `bot_language`, `whitelist_enabled`, `whitelist_numbers`, `rate_limit_max`, `rate_limit_window_sec`, `debounce_seconds`, `status_parent_keywords`, `status_student_keywords`, `out_of_scope_keywords`, `register_keywords`, `price_keywords`, `batch_keywords`, `program_keywords`, `grade_program_map` (**buang untuk PCR**, taksonomi beasiswa). Return: `{ ...passthrough, config }` — passthrough membawa `body` webhook dari `Bootstrap Config` upstream.

### Whitelist Gate (Code)
```js
const cfg = $('Parse Config').first().json.config || {};
const body = ($input.first().json.body) || ($('Parse Config').first().json.body) || {};
if (!cfg.whitelist_enabled) { return [$input.first()]; }
const list = (cfg.whitelist_numbers || []).map(x => String(x).replace(/\D/g, '')).filter(Boolean);
const fromDigits = String(body.from || '').replace(/\D/g, '');
const lidDigits  = String(body.originLid || '').replace(/\D/g, '');
const allowed = list.some(w => w && (w === fromDigits || w === lidDigits ||
  (fromDigits && fromDigits.endsWith(w)) || (w.endsWith(fromDigits) && fromDigits.length >= 6)));
if (!allowed) { return []; }
return [$input.first()];
```
Menggantikan `IF (Whitelist)` hardcode V4 — config-driven via `cfg.whitelist_enabled`/`cfg.whitelist_numbers`.

### Pola referensi config di node hilir
`Whitelist Gate` mencontohkan pola akses: `$('Parse Config').first().json.config.xxx`. **Pola ini yang harus dipakai semua node PCR baru** yang butuh baca CONFIG (contoh dari blueprint: `cfg.followup_max`, `cfg.admin_phone_display`, `cfg.field_team_phone`, dst — lihat blueprint §2.3, §3.2).

### Perbedaan struktural connections TEMPLATE vs V4 (penting saat forking)
TEMPLATE: `Webhook → IF From Me → Bootstrap Config → Read CONFIG → Parse Config → Whitelist Gate → Chat Counter`.
V4: `Webhook → If From Group → IF From Me → IF (Whitelist) → Chat Counter`.
**TEMPLATE tidak punya node `If From Group`** — saat fork config layer TEMPLATE ke atas logika V4 (rekomendasi analisis arsitektur §5), Opus harus **menyisipkan kembali `If From Group`** dari V4 (letakkan sebelum `IF From Me`, atau setelah `Whitelist Gate` — keputusan urutan tidak dispesifikasi blueprint, tapi filter grup sebaiknya paling awal untuk hemat resource).

Juga: TEMPLATE punya node `IF Status Update Needed`/`Update User Status` (alur PARENT/STUDENT) yang **tidak ada di V4** dan **tidak dipakai PCR** (blueprint §9 tidak menyebutnya reuse) — jangan ikut di-fork.

---

## 7. Error Workflow & Buffer Cleanup

Kedua file source kecil (2.7KB dan 5.4KB) — **sudah dibaca utuh**, isi lengkap ada di file asal:
- `D:\Documents\Claude Cowork\the scholars\report\production\2026-07-02-VIRA_V4-error-workflow.json` (3 node: `Error Trigger` → `Compose Notif` (Code) → `Notify Admin Error` (HTTP Kirimi))
- `D:\Documents\Claude Cowork\the scholars\report\production\2026-07-03-VIRA_MSG_BUFFER-cleanup.json` (3 node: `Every day 03:00 WIB` (Schedule cron `0 3 * * *`) → `Read MSG_BUFFER (all)` → `Pick expired block (>2h)` (Code) → `Delete expired rows`)

**Field yang harus diganti untuk PCR:**

| File | Field | Nilai V4 | Ganti jadi |
|---|---|---|---|
| error-workflow.json | `Notify Admin Error` → `bodyParameters.phone` | `"=6285155202354"` | nomor admin PCR (atau credential-based per §4 di atas) |
| error-workflow.json | `Notify Admin Error` → `user_code`/`secret`/`device_id` | hardcode Kirimi The Scholars | **pindah ke Credentials**, jangan copy plaintext |
| error-workflow.json | `name` (top-level workflow) | `"VIRA Error Notifier"` | `"VIRA-PCR Error Notifier"` (blueprint §0) |
| MSG_BUFFER-cleanup.json | `documentId.value` (2 node googleSheets) | `1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE` | Sheet ID `Persada_Cisoka_Database` |
| MSG_BUFFER-cleanup.json | `credentials.googleApi` (2 node) | `3gTKMbD8lJDLbRqR` / "Google Service Account thescholars" | credential Google service account PCR |
| MSG_BUFFER-cleanup.json | `name` (top-level) | `"VIRA - MSG_BUFFER Cleanup (harian 03:00 WIB)"` | `"VIRA-PCR - MSG_BUFFER Cleanup (harian 03:00 WIB)"` |
| MSG_BUFFER-cleanup.json | `RETENTION_MS` (2 jam) di `Pick expired block` | `2 * 60 * 60 * 1000` | pertahankan (harus > `MAX_AGE_MS` 30 menit di `Cek_user_status`) — **jangan ubah tanpa cek konsistensi** |

Struktur logika kedua workflow **1:1 copy**, tidak ada bagian yang perlu dimodifikasi selain field di atas. Catatan desain `Pick expired block (>2h)`: karena `MSG_BUFFER` append-only, baris kadaluarsa SELALU jadi blok kontigu di atas (ts naik seiring row number) — cukup 1x hitung `startRow`+`count` lalu 1x delete range, hemat kuota API Sheets.

Workflow #3 (Error Notifier) **harus di-set manual** di *Settings → Error Workflow* milik VIRA-PCR Main setelah keduanya di-import ke n8n (tidak otomatis hanya karena filenya ada) — ini instruksi operasional untuk Steven, bukan sesuatu yang bisa dikerjakan lewat JSON.

---

## 8. Settings Workflow & Struktur Top-Level

### VIRA V4.json — top-level keys & settings
```json
{
  "name": "VIRA V4",
  "active": true,
  "id": "TW-E4ZbJgEzRSbsUcST5W",
  "versionId": "bda16c93-c75f-4b24-ab77-fde7488aa87d",
  "meta": { "instanceId": "bc5f82215be48fb0bc8c26e9e796ab07403e7202f46c7b0b9b39bd0750f645cd" },
  "settings": {
    "executionOrder": "v1",
    "availableInMCP": false,
    "timeSavedMode": "fixed",
    "timezone": "Asia/Jakarta",
    "callerPolicy": "workflowsFromSameOwner",
    "errorWorkflow": "ZKsINjA7ZC8c9yRHWp3ud"
  },
  "pinData": { "Webhook": "..." }
}
```
Top-level keys lengkap: `name, nodes, pinData, connections, active, settings, versionId, meta, id, tags`.

**Untuk import baru (workflow PCR) di n8n:**
- `id`/`versionId`/`meta.instanceId` di-generate otomatis oleh n8n saat import — **jangan copy nilai V4**, biarkan n8n assign baru (atau hapus field ini dari JSON export sebelum import supaya tidak konflik).
- `settings.errorWorkflow` berisi **ID internal workflow** (`ZKsINjA7ZC8c9yRHWp3ud` = ID Error Notifier di instance The Scholars) — ini **tidak portable**, harus di-set ulang manual dari UI n8n PCR setelah workflow Error Notifier PCR ter-import dan dapat ID barunya sendiri (selaras catatan §7 di atas).
- `settings.timezone: "Asia/Jakarta"` — pertahankan untuk PCR (WIB).
- `settings.executionOrder: "v1"` — pertahankan (standar n8n modern).
- `pinData.Webhook` di V4 berisi contoh payload pinned untuk testing — opsional untuk PCR, boleh dikosongkan `{}` saat build awal.
- File error-workflow & buffer-cleanup punya `settings` lebih minimal: `{ "executionOrder": "v1", "timezone": "Asia/Jakarta" }` saja (tidak ada `errorWorkflow`/`callerPolicy` — wajar karena keduanya bukan target Error Workflow untuk workflow lain).

Dump top-level lengkap (termasuk versi TEMPLATE untuk pembanding): `_extraction\V4\V4-top-level.txt`, `_extraction\TEMPLATE\TEMPLATE-top-level.txt`.

### Struktur node individual (semua node n8n, referensi umum)
Tiap entri di array `nodes` minimal punya: `parameters` (object, isi beda per type), `type` (string, mis. `n8n-nodes-base.code`), `typeVersion` (number), `position` ([x,y]), `id` (UUID atau string unik), `name` (string, harus unik dalam 1 workflow — inilah kunci yang dipakai ekspresi `$('Nama Node')`). Opsional: `credentials`, `disabled`, `notes`, `onError`, `retryOnFail`, `waitBetweenTries`, `maxTries`, `alwaysOutputData`, `executeOnce`, `continueOnFail`, `webhookId` (khusus webhook/wait node yang exposed sebagai webhook resume).

### Struktur `connections`
Object dengan key = **nama node sumber** (persis field `name`, case-sensitive), value = `{ "main": [ [ {node, type, index}, ... ], [ ... untuk output kedua ... ] ] }` — array terluar mewakili **output index** node sumber (output 0, output 1, dst — penting untuk IF/httpRequest dengan `continueErrorOutput` yang punya 2 output), array kedalam adalah daftar target (bisa >1 kalau 1 output nyambung ke banyak node, seperti `Process All` yang keluar ke 4 node sekaligus). Untuk node AI (`ai_languageModel`, `ai_memory`) polanya sama tapi key top-level bukan `"main"`.

---

## Ringkasan Temuan Tambahan (di luar 8 poin brief, relevan untuk Opus)

1. **Field Kirimi = `phone`**, bukan `receiver` — dikonfirmasi di 8+ node HTTP (§4). Blueprint sudah minta ini dicek eksplisit; jawabannya `phone`.
2. **Pola credential Kirimi TEMPLATE** (`httpCustomAuth` generic credential, hanya `phone`/`message` di body) adalah cara yang benar untuk PCR memenuhi prinsip pondasi #4 (secret → Credentials) — V4 production TIDAK memakai pola ini (masih plaintext `user_code`/`secret`/`device_id` di tiap node), jadi **jangan copy node HTTP Kirimi dari V4 apa adanya**, copy strukturnya dari TEMPLATE lalu isi credential ID PCR.
3. **TEMPLATE tidak punya node `If From Group`** — wajib disisipkan manual saat fork config layer ke atas logika V4 (§6).
4. Cabang **GForm (7 node)** adalah area abu-abu yang blueprint §9 tidak putuskan eksplisit — jangan asumsikan reuse/buang tanpa konfirmasi (§1).
5. `settings.errorWorkflow` di JSON export **bukan** nilai yang bisa langsung dipindah antar-instance n8n (ID internal) — harus di-set ulang manual dari UI setelah import (§8).

---

**File yang ditulis:**
- `D:\Documents\Claude Cowork\Persada Cisoka Residence\draft workflow\2026-07-15-referensi-ekstraksi-node-V4.md` (dokumen ini)
- `D:\Documents\Claude Cowork\Persada Cisoka Residence\draft workflow\_extraction\V4\...` (dump mentah V4: top-level, inventory, connections, 59 node-params JSON, 13 code-nodes JS)
- `D:\Documents\Claude Cowork\Persada Cisoka Residence\draft workflow\_extraction\TEMPLATE\...` (dump mentah TEMPLATE: top-level, inventory, connections, 59 node-params JSON, 15 code-nodes JS)
