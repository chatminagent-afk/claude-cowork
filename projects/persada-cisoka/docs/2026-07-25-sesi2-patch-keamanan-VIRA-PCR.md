# SESI 2 — Patch Keamanan & Pembersihan Config (VIRA-PCR)

Tanggal: 2026-07-25
Status: **DRAFT — belum masuk produksi.** Semua file di `workflow/production/` tidak disentuh.
Kode siap paste: `2026-07-25-sesi2-kode-patch/`

Semua temuan di bawah sudah diverifikasi langsung terhadap file JSON + `PCR_Database.xlsx` tab CONFIG.

---

## T1 — `Bootstrap Config` hardcode Sheet ID yang salah

| | |
|---|---|
| File | `workflow/production/VIRA-PCR Main V1.3.json` |
| Node | `Bootstrap Config` (`n8n-nodes-base.code`, tv 2) |
| Patch | `2026-07-25-sesi2-kode-patch/bootstrap-config.js` |

**SEBELUM** (kutipan persis):
```js
// ============================================================
// BOOTSTRAP CONFIG
// Ganti SHEET_ID ke Sheet ID spreadsheet "Persada_Cisoka_Database".
// ============================================================
const SHEET_ID = '1dJWq7iq5PRGRguW6GRAgtclgvhSqppa-D6tSNrAo1PU';   // <-- EDIT INI
const wh = $input.first() ? $input.first().json : {};
return [{ json: { ...wh, sheet_id: SHEET_ID } }];
```

**SESUDAH**:
```js
// ============================================================
// BOOTSTRAP CONFIG  — PATCH Sesi 2 (T1)
// SHEET_ID = spreadsheet "Persada_Cisoka_Database" (PCR_Database.xlsx).
// WAJIB sama dengan documentId di 23 node Google Sheets workflow ini.
// Kalau spreadsheet dipindah/diganti, ubah di SATU tempat ini + di node Sheets.
// ============================================================
const SHEET_ID = '1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o';
const wh = $input.first() ? $input.first().json : {};
return [{ json: { ...wh, sheet_id: SHEET_ID } }];
```

**Alasan.** Terverifikasi: 23 node googleSheets di workflow ini semua menunjuk ke `1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o` (3 node pakai raw ID, 20 node pakai bentuk URL). ID `1dJWq...` hanya muncul 1× yaitu di node ini. `Parse Config` menyalurkan nilai salah itu ke `config.sheet_id`, dan `config.sheet_id` tidak dikonsumsi node mana pun (0 hit) — jadi belum meledak, tapi begitu ada yang memakainya, workflow akan membaca spreadsheet yang salah.

**Dampak fungsional patch: nol.** Nilai yang diperbaiki tidak dibaca siapa pun hari ini.

---

## T2 — `Rate Limiter LID` mengabaikan CONFIG

| | |
|---|---|
| File | `workflow/production/VIRA-PCR Main V1.3.json` |
| Node | `Rate Limiter LID` (`n8n-nodes-base.code`, tv 2) |
| Patch | `2026-07-25-sesi2-kode-patch/rate-limiter-lid.js` |

**SEBELUM** (bagian yang diubah, kutipan persis):
```js
// Rate Limiter: cegah spam (maks 5 pesan per menit per user)
const input = $input.first().json;
const userWa = $('Resolve User Row').first().json.resolved_key;
const now = Date.now();

// Global store menggunakan $workflow static data
const staticData = $getWorkflowStaticData('global');
const rateLimits = staticData.rateLimits || {};

const userKey = `rl_${userWa}`;
const windowMs = 60000; // 1 menit
const maxMessages = 5;
```
…dan dua baris log di bawah yang menyebut "1 menit" / tanpa batas.

**SESUDAH** — lihat file patch, isi lengkap. Bagian inti:
```js
// Baca CONFIG; kalau node Parse Config tak terjangkau, pakai default lama.
const cfg = (() => {
  try { return $('Parse Config').first().json.config || {}; } catch (e) { return {}; }
})();

// Hanya terima angka finite > 0. 0 / negatif / NaN / '' -> default lama.
const posNum = (v, def) => {
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? n : def;
};

const maxMessages = posNum(cfg.rate_limit_max, 5);           // default lama: 5
const windowSec   = posNum(cfg.rate_limit_window_sec, 60);   // default lama: 60 detik
const windowMs    = windowSec * 1000;                        // default lama: 60000 ms
```
Log diperbarui supaya menyebut angka aktual:
```js
  console.log(`⛔ RATE LIMITED: ${userWa} sudah ${rateLimits[userKey].count} pesan dalam ${windowSec}s (maks ${maxMessages})`);
...
console.log(`✅ RATE OK: ${userWa} pesan ke-${rateLimits[userKey].count}/${maxMessages} dalam window ${windowSec}s`);
```

**Alasan.** `Parse Config` sudah mengekspos `config.rate_limit_max` dan `config.rate_limit_window_sec`, dan `Parse Config` terbukti upstream dari `Rate Limiter LID` (rantai: `Parse Config → Whitelist Gate → Chat Counter → Read User STATS → Resolve User Row → IF Bot Mode Active → Rate Limiter LID`). Hardcode membuat CONFIG jadi bohong: sheet bilang 10, sistem menerapkan 5.

**PERHATIAN — ini melonggarkan perilaku.** CONFIG saat ini `rate_limit_max = 10`, jadi setelah patch batas naik 5 → 10 pesan/menit per user. Kalau Steven memang mau tetap 5, ubah nilainya di tab CONFIG (bukan di kode) sebelum/sesudah deploy.

---

## T3 — `$vars.chatCounter` dead code

| | |
|---|---|
| File | `workflow/production/VIRA-PCR Main V1.3.json` |
| Node | `Chat Counter` (`n8n-nodes-base.code`, tv 2) |
| Patch | `2026-07-25-sesi2-kode-patch/chat-counter.js` |
| Keputusan | **DIHAPUS** (bukan diganti ke static data) |

**SEBELUM** (kutipan persis):
```js
// Counter sederhana
let counter = $vars.chatCounter || 0;
counter++;
$vars.chatCounter = counter;
```
```js
const aiInputText = `[SYSTEM_DATA]
CHAT_COUNTER: ${counter}
USER_NAME: ${userName}
```
```js
return [{
    json: {
        chat_counter: counter,
```

**SESUDAH**: 3 baris counter dihapus, baris `CHAT_COUNTER: ${counter}` dihapus dari template, field `chat_counter` dihapus dari output. Isi lengkap di file patch.

**Hasil pengecekan konsumsi `chat_counter` (grep seluruh 4 file workflow):**

| Lokasi | Hit | Keterangan |
|---|---|---|
| `Chat Counter` | 1 | definisi field itu sendiri |
| `Extract & Prepare Data` | 1 | **string literal** `source: "chat_counter_node"` — bukan pembacaan field |
| 3 workflow lain (Follow-up, Cleanup, Error Notifier) | 0 | — |

Node lain (`Process All`, `Extract & Prepare Data`, `Process Counter & Merge Data`) memang menulis `const chatCounter = $('Chat Counter').first().json;` — tapi itu nama variabel lokal untuk objek node-nya, dan tidak ada satu pun yang mengakses `.chat_counter`.

`CHAT_COUNTER: ${counter}` juga aman dihapus: `ai_input_text` dari `Chat Counter` **ditimpa total** oleh `Cek_user_status` (`ai_input_text: aiSystemData`, dibangun dari nol, tanpa baris CHAT_COUNTER), lalu ditimpa lagi oleh `Preprocess - Context Detection` (`ai_input_text: enhancedInput`), baru dikonsumsi `AI Agent` (`={{ $input.item.json.ai_input_text }}`). Tidak ada node antara `Chat Counter` dan `Cek_user_status` yang menyentuh `ai_input_text` (grep: hanya 4 node total yang menyebutnya).

**Alasan tidak diganti ke `$getWorkflowStaticData`:** tidak ada konsumen. Menghidupkan counter global lintas-user juga tidak bermakna secara bisnis (angka "pesan ke-N sejak workflow restart", bukan per user), dan counter per-user yang berguna sudah ada di kolom STATS. Menambah write ke static data hanya menambah beban tanpa manfaat.

---

## T4 — `Wait3` hardcode 60 detik

| | |
|---|---|
| File | `workflow/production/VIRA-PCR Main V1.3.json` |
| Node | `Wait3` (`n8n-nodes-base.wait`, tv **1.1**) |
| Keputusan | **DIPATCH** — dukungan ekspresi terverifikasi |

**SEBELUM** (parameter node, kutipan persis):
```json
{
  "parameters": {
    "amount": 60
  },
  "type": "n8n-nodes-base.wait",
  "typeVersion": 1.1,
  "name": "Wait3"
}
```

**SESUDAH** (`parameters` saja — sisa properti node jangan diubah):
```json
{
  "parameters": {
    "amount": "={{ Math.max(5, Number($('Parse Config').first().json.config.debounce_seconds) || 60) }}"
  }
}
```

**Verifikasi dukungan ekspresi (bukan asumsi).** Di workflow yang SAMA, node Wait dengan typeVersion yang SAMA (1.1) sudah memakai ekspresi di field `amount`:
- `Wait1`: `"amount": "={{ Math.floor(Math.random()*(10-5+1))+5}}"`
- `Wait2`: `"amount": "={{ Math.floor(Math.random()*(10-5+1))+5}}"`

Jadi ini bukan fitur yang perlu ditebak — sudah berjalan di produksi pada versi n8n yang dipakai Steven. Ekspresi `amount` juga dievaluasi **sebelum** wait dimulai, sehingga `$('Parse Config')` masih terjangkau (dan `Parse Config` terbukti upstream dari `Wait3`).

**Kenapa pakai `Math.max(5, ...)`.** `debounce_seconds` yang kosong atau 0 akan membuat debounce mati total → tiap pesan diproses sendiri-sendiri, memicu balasan ganda dan lonjakan kuota Sheets. Guard 5 detik mencegah salah-isi CONFIG merusak produksi. `|| 60` menangani `NaN`/kosong.

**Catatan nilai:** CONFIG saat ini `debounce_seconds = 60`, sama dengan hardcode → **dampak fungsional patch: nol** untuk sekarang. Nilainya baru terasa saat Steven mengubah CONFIG.

---

## T5 — `Error Notifier`: kredensial hardcode + nomor tujuan salah + tanpa retry

| | |
|---|---|
| File | `workflow/production/VIRA-PCR Error Notifier.json` |
| Node | `Notify Admin Error` (`n8n-nodes-base.httpRequest`, tv 4.3) |
| Kritis | Workflow ini adalah `errorWorkflow` untuk **ketiga** workflow lain (id `rBsq-mGgHfqfwbz3YmwxI`) |

**SEBELUM** (kutipan persis, nilai `secret` disensor):
```json
"bodyParameters": {
  "parameters": [
    { "name": "user_code", "value": "KM40LI0426" },
    { "name": "secret",    "value": "<REDACTED>" },
    { "name": "device_id", "value": "D-GHK1A" },
    { "name": "phone",     "value": "6285155202354" },
    { "name": "message",   "value": "={{ $json.notif_text }}" },
    { "name": "device_id", "value": "D-GHK1A" }
  ]
}
```
Node tidak punya `retryOnFail`, `maxTries`, `waitBetweenTries`, maupun `onError`.

**Fakta terverifikasi:**
- `device_id` memang muncul **2×** dengan nilai identik (`D-GHK1A`). Saat ini tidak merusak apa-apa, tapi kalau device Kirimi diganti dan hanya satu baris di-update, request akan mengirim dua nilai berbeda dan gagal secara membingungkan.
- `phone = 6285155202354` ≠ `admin_phone` di CONFIG (`6282321298930`). Nomor `6285155202354` ada di `whitelist_numbers` (nomor tes).
- 12 node Kirimi di `Main V1.3` dan 1 di `Follow-up` semua sudah pakai pola ekspresi `={{ $('Parse Config').first().json.config.kirimi_secret }}`. **Hanya node ini yang hardcode secret.**
- `Error Notifier` tidak punya node Sheets sama sekali (4 node: `Error Trigger → Compose Notif → Notify Admin Error`, + 1 sticky).

### Rekomendasi: pindahkan kredensial ke n8n **Custom Auth credential**, JANGAN tambah Read CONFIG

**Kenapa bukan tambah `Read CONFIG` + `Parse Config`.** Ini error handler untuk 3 workflow yang beban utamanya Google Sheets (Sesi 4 justru soal kuota Sheets). Menambahkan dependensi Sheets ke notifier berarti: saat Sheets yang error/kena kuota — kasus yang paling sering memicu notifier ini — notifier ikut gagal dan Steven **tidak dapat notifikasi sama sekali**. Menukar "secret di JSON" dengan "alert hilang saat paling dibutuhkan" bukan trade-off yang layak. Notifier harus punya nol dependensi eksternal selain Kirimi.

**Langkah:**

1. Di n8n → Credentials → New → **Custom Auth**, nama `Kirimi Body Auth`, isi:
```json
{
  "body": {
    "user_code": "KM40LI0426",
    "secret": "<REDACTED — paste secret Kirimi, pakai yang BARU kalau sudah dirotasi>",
    "device_id": "D-GHK1A"
  }
}
```
2. Ubah node `Notify Admin Error` jadi:
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://api.kirimi.id/v1/send-message",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpCustomAuth",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        { "name": "phone",   "value": "6282321298930" },
        { "name": "message", "value": "={{ $json.notif_text }}" }
      ]
    },
    "options": {}
  },
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.3,
  "position": [448, 0],
  "id": "142a9cd6-1a32-4def-9443-22284d5ec53a",
  "name": "Notify Admin Error",
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 5000,
  "credentials": {
    "httpCustomAuth": { "id": "<terisi otomatis saat dipilih di UI>", "name": "Kirimi Body Auth" }
  }
}
```
3. **Smoke test wajib** dengan Execute Node sebelum simpan-aktif: pastikan Custom Auth benar-benar meng-inject ketiga field ke body. Ini satu-satunya bagian T5 yang tidak bisa saya verifikasi dari file — komentar di `Parse Config` menyebut niat memakai `httpCustomAuth` untuk node teks, tapi kenyataannya **tidak ada** node Kirimi yang benar-benar memakainya (semua `credentials: {}`), jadi belum ada bukti empiris di repo ini.
4. `phone` sengaja tetap literal, bukan dari CONFIG — konsisten dengan prinsip nol-dependensi di atas. Nomor telepon bukan secret.

**Konfirmasi yang dibutuhkan dari Steven:** apakah `6285155202354` itu nomor Steven sendiri dan memang sengaja dijadikan penerima alert teknis? Kalau ya, jangan diganti (atau tambahkan node kedua supaya dua-duanya dapat). Kalau tidak, `6282321298930` yang benar.

### Minimal wajib — bisa deploy hari ini tanpa menunggu credential

Kalau langkah credential belum siap, patch ini saja sudah aman dan berdiri sendiri:
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://api.kirimi.id/v1/send-message",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        { "name": "user_code", "value": "KM40LI0426" },
        { "name": "secret",    "value": "<JANGAN DIKETIK ULANG — biarkan nilai yang sudah ada di node>" },
        { "name": "device_id", "value": "D-GHK1A" },
        { "name": "phone",     "value": "6282321298930" },
        { "name": "message",   "value": "={{ $json.notif_text }}" }
      ]
    },
    "options": {}
  },
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.3,
  "position": [448, 0],
  "id": "142a9cd6-1a32-4def-9443-22284d5ec53a",
  "name": "Notify Admin Error",
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 5000
}
```
Isi: `device_id` duplikat dihapus, `phone` diperbaiki ke `admin_phone`, retry 3× jarak 5 detik ditambahkan.

**`onError` sengaja TIDAK ditambahkan.** Ini node terakhir di error handler. Kalau setelah 3× retry Kirimi masih gagal, eksekusi memang harus ditandai FAILED supaya terlihat di execution list n8n — `continueRegularOutput` justru akan menyembunyikan kegagalan alert.

`Compose Notif` tidak perlu diubah sama sekali.

---

## Tindakan manual Steven

Urutan ini penting: **kunci baru dibuat & dipasang SEBELUM kunci lama dihapus**, supaya sistem tidak mati di tengah.

### A. Rotate service account key (lakukan pertama, sistem tetap hidup)
1. Google Cloud Console → **IAM & Admin → Service Accounts**.
2. Pilih `persada@vira-persada.iam.gserviceaccount.com`.
3. Tab **Keys** → **Add Key → Create new key → JSON** → download.
4. n8n → Credentials → `Google Service Account - Persada` (id `QC5aF1HyvTElhC0M`) → paste **email + private key BARU** → Save.
5. **Tes dulu**: jalankan `VIRA-PCR - MSG_BUFFER Cleanup` secara manual, atau Execute Node pada `Read CONFIG` di Main. Harus sukses.
6. Baru setelah tes hijau: kembali ke Cloud Console → Keys → **hapus key lama**.

> Jangan pernah hapus key lama sebelum langkah 5 hijau. Kalau dibalik, keempat workflow mati serentak.

### B. Bersihkan CONFIG di Google Sheets (setelah A selesai)
7. Buka spreadsheet `1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o` → tab **CONFIG**.
8. Hapus **2 baris**: `google service email` dan `google service private key`.
   - Terverifikasi tidak dipakai kode mana pun — `Parse Config` tidak membaca kedua key ini (tidak ada di daftar field objek `config`), dan node Sheets memakai credential n8n, bukan CONFIG.
   - Kredensial hanya boleh hidup di n8n Credentials, tidak di spreadsheet yang dibaca 23 node dan bisa dishare.
9. Setelah dihapus, jalankan sekali lagi tes di langkah 5 untuk memastikan tidak ada yang bergantung padanya.

### C. Bersihkan jejak di execution history n8n
10. n8n → **Executions** → hapus riwayat eksekusi lama workflow `Main`, `Follow-up`, `Cleanup`, `Error Notifier`.
    - Alasan: output node `Read CONFIG` tersimpan utuh di setiap eksekusi. Selama private key masih ada di CONFIG, **setiap** eksekusi menyimpan salinan private key di database n8n. Rotasi key (A) sudah membuat salinan itu tidak berguna, tapi hapus juga supaya tidak ada residu.
    - Lakukan **setelah** A dan B, bukan sebelum — kalau tidak, eksekusi baru langsung menulis salinan baru.
11. Pertimbangkan set `EXECUTIONS_DATA_MAX_AGE` / pruning di n8n supaya ini tidak menumpuk lagi (opsional, di luar scope Sesi 2).

### D. Rotate `kirimi_secret` (pertimbangkan, prioritas lebih rendah)
12. `kirimi_secret` (64 hex) tersimpan plaintext di tab CONFIG dan tertulis literal di `Error Notifier`. Kalau spreadsheet pernah dishare ke telemarketer / tim lapangan / vendor, anggap sudah bocor → rotate di dashboard Kirimi.
13. Kalau dirotasi: update tab CONFIG (`kirimi_secret`) **dan** credential `Kirimi Body Auth` (atau node `Notify Admin Error` kalau masih pakai versi minimal) dalam sesi yang sama. Kalau tidak, salah satu jalur kirim WA akan mati tanpa suara.
14. Rekomendasi jangka menengah (Sesi berikutnya, bukan sekarang): pindahkan `kirimi_user_code`/`kirimi_secret`/`kirimi_device_id` dari CONFIG ke credential `Kirimi Body Auth` untuk **semua** node teks, sisakan di CONFIG hanya untuk node multipart `send-message-file` yang memang butuh field form. Itu perubahan 12 node — jangan digabung ke Sesi 2.

---

## Risiko & urutan deploy

**Aman deploy sendirian (dampak fungsional nol, murni kebersihan):**

| Patch | Kenapa aman |
|---|---|
| T1 `Bootstrap Config` | `config.sheet_id` tidak dikonsumsi node mana pun (0 hit) |
| T3 `Chat Counter` | Field & baris yang dihapus terbukti tidak dikonsumsi; `ai_input_text` ditimpa 2× sebelum sampai AI Agent |
| T4 `Wait3` | CONFIG `debounce_seconds = 60`, persis sama dengan hardcode → perilaku identik |
| T5 minimal (`Notify Admin Error`) | Workflow terpisah, tidak menyentuh jalur balas user |

Ketiga T1/T3/T4 ada di file yang sama, jadi praktisnya jadi **satu deploy Main V1.3**. Boleh sekali jalan.

**Butuh perhatian / verifikasi pasca-deploy:**

| Patch | Risiko | Mitigasi |
|---|---|---|
| T2 `Rate Limiter LID` | **Mengubah perilaku**: batas 5 → 10 pesan/menit. Kalau nanti CONFIG salah diisi, batas ikut salah | Guard `posNum` menolak 0/negatif/NaN → jatuh ke 5. Setelah deploy, kirim 6 pesan cepat dari nomor tes dan cek log `RATE OK: ... ke-6/10` |
| T5 versi credential | Custom Auth belum terbukti meng-inject body di instance ini | Wajib Execute Node dulu (T5 langkah 3). Kalau gagal, tetap pakai T5 minimal — jangan dipaksa |

**Urutan yang disarankan:**

1. **Manual A** (rotate service account key) — paling mendesak, tidak bergantung patch mana pun.
2. **T5 minimal** — deploy sendiri, kirim WA tes ke `6282321298930`, pastikan sampai. Perbaiki jalur alert dulu sebelum menyentuh Main, supaya kalau langkah 3 bermasalah Steven benar-benar dapat notifikasi.
3. **T1 + T3 + T4** bareng dalam satu update Main V1.3. Tes: 1 chat penuh dari nomor whitelist, cek balasan normal + STATS ter-update.
4. **T2** terpisah setelah nomor 3 terbukti stabil — supaya kalau ada anomali rate limit, penyebabnya tidak tercampur dengan 3 perubahan lain.
5. **Manual B → C** (hapus baris CONFIG → bersihkan execution history).
6. **Manual D** (rotate `kirimi_secret`) belakangan, sendiri, dengan window tes.

**Jangan** gabungkan nomor 3 dan 4 dalam satu deploy: T2 satu-satunya yang mengubah perilaku, harus bisa di-rollback sendiri.

---

## Ditunda + alasan

| Item | Alasan |
|---|---|
| Migrasi kredensial Kirimi untuk **12 node** di `Main V1.3` + 1 di `Follow-up` ke credential `Kirimi Body Auth` | Semua sudah membaca dari CONFIG (bukan hardcode), jadi bukan temuan T1–T5. Perubahan 13 node berisiko tinggi untuk digabung ke Sesi 2. Masuk backlog (lihat Manual D no. 14) |
| Menghapus `const input = $input.first().json;` yang tidak terpakai di `Rate Limiter LID` | Dead variable, nol risiko, tapi bukan bagian temuan — dibiarkan supaya diff Sesi 2 tetap kecil dan mudah direview |
| Mengubah nilai `rate_limit_max` di tab CONFIG | Perubahan sheet = tindakan manual Steven, di luar scope file. Patch T2 hanya membuat kode **menghormati** nilai apa pun yang ada di situ |
| Retry/`onError` untuk 7 node Kirimi lain di Main yang belum punya (`Notify Admin Media Error`, `Notify Media Team`, `Notify Field Team`, `Notify Admin Unknown`, `Notify Admin API Error`, `Notify Talk to Admin`) | Isu reliabilitas, bukan keamanan/config. Bukan T1–T5 |
| Pruning `EXECUTIONS_DATA_MAX_AGE` | Setting instance n8n, bukan file workflow. Dicatat sebagai opsional di Manual C no. 11 |
| Apa pun terkait performa/kuota Google Sheets | Scope Sesi 4 |

---

## Ketidakcocokan yang ditemukan vs deskripsi awal

1. **T2 — jumlah node Sheets.** Deskripsi bilang "SEMUA 23 node googleSheets pakai documentId `1pzGu...`". Benar 23 node dan benar ID-nya, tapi formatnya tidak seragam: 3 node menyimpan raw ID, 20 node menyimpan bentuk URL lengkap (`=https://docs.google.com/spreadsheets/d/1pzGu.../edit?gid=...`). Tidak mengubah kesimpulan, tapi relevan kalau nanti ada script yang mencari-ganti Sheet ID.
2. **T4 — dukungan ekspresi terbukti, jadi TIDAK ditunda.** Deskripsi mengantisipasi kemungkinan sintaks tidak terverifikasi. Ternyata `Wait1` dan `Wait2` di workflow yang sama, typeVersion 1.1 yang sama, sudah memakai ekspresi di `amount` di produksi. Tidak perlu verifikasi manual di UI.
3. **T5 — `phone` juga saya patch di "minimal wajib".** Daftar "minimal yang HARUS diperbaiki" hanya menyebut hapus `device_id` duplikat + retry. Saya masukkan juga perbaikan `phone` karena mengirim alert ke nomor yang salah adalah kegagalan diam-diam yang lebih berbahaya daripada tidak ada retry, dan biayanya satu token. Tapi lihat "Konfirmasi yang dibutuhkan" di T5 — ada kemungkinan nomor itu memang disengaja.
4. **T5 — komentar di `Parse Config` tidak sesuai kenyataan.** Komentarnya berbunyi "Node teks (JSON body) tetap pakai credential httpCustomAuth", tapi **tidak satu pun** node httpRequest Kirimi di keempat workflow memakai credential (`credentials: {}`, `authentication` tidak diset). Semuanya mengirim `user_code`/`secret`/`device_id` sebagai body parameter. Komentar itu menggambarkan niat, bukan implementasi — perlu diperbaiki atau dihapus nanti supaya tidak menyesatkan reviewer berikutnya.
5. **T3 — cakupan penghapusan lebih luas dari deskripsi.** Deskripsi menyebut "hapus 3 baris + field `chat_counter`". Ada satu tempat lagi yang memakai `counter`: baris `CHAT_COUNTER: ${counter}` di dalam `aiInputText`. Kalau hanya 3 baris + field yang dihapus, kode langsung error (`counter is not defined`). Saya hapus juga baris itu, setelah memverifikasi `ai_input_text` dari node ini ditimpa total oleh `Cek_user_status`.
6. **Temuan tambahan (bukan T1–T5, tidak dipatch):** `whitelist_enabled = TRUE` di CONFIG dengan hanya 3 nomor di `whitelist_numbers`. Kalau VIRA-PCR sudah/akan go-live untuk publik, semua chat dari nomor lain diblokir di `Whitelist Gate`. Perlu dipastikan ini memang masih mode tes.
