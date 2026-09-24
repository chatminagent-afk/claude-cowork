# VIRA V4 — Kolom `Status` Jadi Penentu Tunggal Pendaftaran Buka/Tutup

**Tanggal:** 2026-08-12
**Basis:** `report/patch/2026-08-11-VIRA-V4-guardrail-transfer.json` (patch transfer)
**Hasil:** `report/patch/2026-08-12-VIRA-V4-r1-status-batch.json` — **kumulatif**, sudah memuat guardrail transfer + perbaikan batch. Ini file yang di-import; file 08-11 jadi versi antara.
**Pemicu:** Sam — VIRA menjawab "Batch 5 pendaftarannya belum dibuka" padahal di sheet PROGRAM `Nama Batch = Batch 5`, `Status = Active`.

---

## Akar masalah

Data-nya **tidak salah dan tidak putus**. Yang diverifikasi:

- Node `Read PROGRAM Data` ada, membaca tab `PROGRAM`, tersambung di rantai eksekusi
- Blok `STATUS & BATCH` di `FAQ Retrieve` **tidak punya gate apa pun** (komentar aslinya: `// selalu`) dan tidak memfilter status
- Nama kolom di kode (`val(r, 'Nama Batch')` = kolom I) cocok persis dengan header sheet

Jadi AI menerima baris ini apa adanya:

```
Junior: Status=Active, Batch 5, Mulai 15 Agustus 2026, Deadline daftar 8 Agustus 2026, Kuota 15 per kelas
```

**Masalah sebenarnya: VIRA tidak pernah diberi tahu hari ini tanggal berapa.**

`Chat Counter` menghitung `formattedDate` (Asia/Jakarta) tapi variabel itu tidak pernah masuk ke teks yang dikirim ke AI. Ketiga tempat yang membangun input AI — `Chat Counter` → `aiInputText`, `Cek_user_status` → `SYSTEM_DATA`, `Preprocess` → `enhancedInput` — semuanya tanpa tanggal.

Akibatnya model melihat dua tanggal 2026 tanpa titik acuan, **menebak** posisi waktu, membaca "Mulai 15 Agustus 2026" sebagai masa depan, lalu menyimpulkan sendiri "pendaftaran belum dibuka" — padahal `Status = Active` menyatakan sebaliknya.

Ini juga menjelaskan perilaku yang **tidak konsisten**: pada 8 Agustus VIRA menjawab "pendaftarannya sudah buka sekarang"; pada 12 Agustus, data sama, jawaban berlawanan. Ciri tebakan model, bukan bug data.

Dua faktor yang memperparah — keduanya teks statis yang basi:
- Contoh few-shot di `# GAYA SAM` meng-hardcode *"...begitu pendaftaran **Batch 5** dibuka"*
- Bullet di `# BATCH` meng-hardcode *"yang aktif sekarang **Batch 5** yaa"*
- Contoh di `# TAG` meng-hardcode nama link *"GForm Pendaftaran **Batch 5**"*

---

## Perubahan (3 node, 9 titik)

Node lain tidak disentuh — jumlah node tetap 53, `connections` identik.

### 1. `FAQ Retrieve` — verdict dihitung di kode (deterministik)

Ini inti perbaikannya. Sebelumnya AI dikirimi `Status=Active` mentah lalu **disuruh menyimpulkan sendiri**. Sekarang sistem yang memutuskan, AI tinggal membaca.

```diff
- return `${nm}: Status=${st || 'tidak tertulis'}...`;
+ let out = `${nm}: PENDAFTARAN ${isOpen ? 'DIBUKA' : 'DITUTUP'} (kolom Status=${st || 'tidak tertulis'})`;
+ if (hasBatch) out += `, ${batch}`;
+ if (mulai)    out += `, Program mulai ${mulai}`;
```

Pencocokan status dilakukan **per kata**, dengan daftar TUTUP diperiksa **duluan**:

```js
const CLOSED_RE = /(closed|close|tutup|ditutup|coming\s*soon|belum|tidak\s*aktif|non\s*-?\s*aktif|inactive|selesai|penuh|full)/i;
const OPEN_RE   = /(active|aktif|open|buka|dibuka|berjalan|ongoing)/i;
const isClosed  = CLOSED_RE.test(stRaw);
const isOpen    = !isClosed && OPEN_RE.test(stRaw);
```

Urutan ini penting: `"Belum dibuka"` dan `"Tidak aktif"` mengandung kata `dibuka`/`aktif`, jadi kalau daftar BUKA dicek duluan keduanya akan salah terbaca sebagai dibuka.

Status di luar kedua daftar → **fail-safe `DITUTUP`** + `console.warn`. Lebih baik VIRA diam daripada mendorong pendaftaran yang tidak jelas statusnya.

**Deadline yang sudah lewat tidak dikirim ke AI.** Kalau `Status` dibuka tapi `Deadline Daftar` sudah terlewat, datanya kontradiktif — deadline dibuang dari konteks (supaya tidak dikutip sebagai fakta hidup) dan dicatat:

```
DATA KONTRADIKTIF: Junior Status=Active (dibuka) tapi Deadline Daftar 8 Agustus 2026 sudah lewat. Deadline tidak dikirim ke AI.
```

Tanggal Indonesia di-parse manual lewat tabel nama bulan (tidak bergantung locale runtime), dan "hari ini" dinormalkan ke tengah malam WIB supaya deadline **hari-H masih dihitung berlaku**.

### 2. `Cek_user_status` — suntik `TANGGAL_HARI_INI`

```diff
  const aiSystemData = `[SYSTEM_DATA]
+ TANGGAL_HARI_INI: ${TANGGAL_HARI_INI} (WIB)
  USER_WA: ${resolvedKey}
```

Nama bulan dirakit manual (`_BLN_ID`) supaya tidak bergantung ketersediaan locale `id-ID` di runtime n8n. Formatnya sengaja disamakan dengan sheet (`12 Agustus 2026`).

Ditaruh di dalam blok `[SYSTEM_DATA]` sebelum `[USER QUERY]`, jadi otomatis ikut terbawa saat `Preprocess` merakit ulang `enhancedInput`.

### 3. `AI Agent` → `systemMessage` (7 titik)

**`# BATCH`** — tiga bullet lama diganti enam bullet baru. Intinya:

```
- PENDAFTARAN DIBUKA / DITUTUP di blok STATUS & BATCH adalah SATU-SATUNYA penentu. Itu sudah
  dihitung sistem dari kolom Status di database. DILARANG menyimpulkan ulang buka/tutup dari
  tanggal mana pun.
- "Program mulai <tanggal>" yang masih di depan TIDAK berarti pendaftaran belum dibuka.
  Bedakan tegas: "program belum mulai" BUKAN "pendaftaran belum dibuka". Batch yang
  PENDAFTARAN DIBUKA tapi programnya baru mulai nanti -> tetap boleh daftar SEKARANG.
- TANGGAL_HARI_INI di SYSTEM_DATA = tanggal hari ini (WIB). Pakai untuk pertanyaan waktu
  ("masih sempat?", "udah mulai belum?"). Tapi untuk buka/tutup pendaftaran, PENDAFTARAN di
  STATUS & BATCH tetap yang menang - bukan hasil hitunganmu sendiri.
```

Pembedaan **"program belum mulai" ≠ "pendaftaran belum dibuka"** ini yang sebelumnya tidak ada sama sekali — dan persis di situ model tergelincir.

**Hardcode nomor batch dibuang di 3 tempat** (`# GAYA SAM`, `# BATCH`, `# TAG`), diganti rujukan ke DATA. Tidak ada lagi `Batch \d` tersisa di seluruh system message — diverifikasi otomatis.

**Istilah diseragamkan** — `# HARGA` dan `# TAG` sekarang memakai "PENDAFTARAN DIBUKA/DITUTUP", bukan "Batch DIBUKA/BELUM dibuka", supaya sinkron dengan label yang benar-benar dilihat AI.

---

## Efek ke `data_context` (data asli sheet, hari ini 12 Agustus 2026)

```diff
- Junior: Status=Active, Batch 5, Mulai 15 Agustus 2026, Deadline daftar 8 Agustus 2026, Kuota 15 per kelas
+ Junior: PENDAFTARAN DIBUKA (kolom Status=Active), Batch 5, Program mulai 15 Agustus 2026, Kuota 15 per kelas
```

Baris lengkap yang akan diterima AI:

| Program | Output |
|---|---|
| Junior | `PENDAFTARAN DIBUKA (kolom Status=Active), Batch 5, Program mulai 15 Agustus 2026, Kuota 15 per kelas` |
| Intermediate | `PENDAFTARAN DIBUKA (kolom Status=Active), Batch 5, Program mulai 15 Agustus 2026, Kuota 15 per kelas` |
| Seniors | `PENDAFTARAN DIBUKA (kolom Status=Active)` |
| Mock Interview | `PENDAFTARAN DIBUKA (kolom Status=Always Open)` |

---

## Temuan QA

**Regresi yang tertangkap sebelum sempat dikirim:** regex status versi pertama saya di-anchor `^(active|aktif|dibuka|open|buka)$`. Nilai `Status = "Always Open"` milik **Mock Interview** tidak cocok → programnya dinyatakan `PENDAFTARAN DITUTUP`. Karena verdict sekarang otoritatif, ini lebih merusak daripada perilaku lama. Diperbaiki jadi pencocokan per kata + daftar TUTUP didahulukan.

**Audit yang dijalankan:**
- Sintaks JS 13 node Code (basis & patch) via `esprima`, dibungkus sebagai badan fungsi → **13/13 OK, 0 regresi**
- Logika verdict di-port 1:1 ke Python lalu dijalankan atas **data asli sheet PROGRAM**, dengan 3 skenario tanggal (sebelum deadline / tepat hari-H / setelah lewat) dan 11 variasi nilai `Status`
- Guardrail transfer dari patch sebelumnya dicek masih utuh

**22 assertion, semua lolos:**

| Kelompok | Isi |
|---|---|
| Bug asli | `Status=Active` → `PENDAFTARAN DIBUKA` |
| Deadline | lewat → dibuang + warning; hari-H → tetap dikirim; masa depan → tetap dikirim |
| Status | `Always Open`/`Aktif`/`Open`/`DIBUKA` → DIBUKA; `Coming soon`/`Closed`/`Belum dibuka`/`Tidak aktif`/`Penuh`/kosong/tak dikenal → DITUTUP |
| Hardcode | nol `Batch \d` tersisa di systemMessage |
| Tanggal | `TANGGAL_HARI_INI` ada di `Cek_user_status`, di dalam blok `SYSTEM_DATA`, dan diajarkan di systemMessage |
| Tidak regresi | safety net transfer utuh, template transfer tetap hilang |

**Batasan — sama seperti patch sebelumnya:** tidak ada Node.js di mesin ini, jadi kode belum pernah dieksekusi sebagai JavaScript; validasi sebatas parser + port logika. Belum diuji di n8n sungguhan.

---

## ⚠️ Perlu keputusan Sam

**`Deadline Daftar` Batch 5 = 8 Agustus 2026, sudah lewat, tapi `Status` masih `Active`.**

Selama dua kolom ini bertentangan, patch akan memihak `Status` — VIRA akan bilang pendaftaran **dibuka** dan tidak menyebut deadline sama sekali. Kalau itu tidak sesuai maksud Sam, salah satu harus diperbaiki di sheet:

- Pendaftaran memang masih dibuka → **geser `Deadline Daftar`** ke tanggal yang benar
- Pendaftaran sudah ditutup → **ubah `Status`** jadi `Closed`

Cek `console.warn` di execution log untuk memantau: selama pesan `DATA KONTRADIKTIF` masih muncul, sheet-nya belum beres.

---

## Cara deploy

1. n8n → **Import from File** → `2026-08-12-VIRA-V4-r1-status-batch.json` (sudah termasuk guardrail transfer, tidak perlu import file 08-11)
2. Cek binding kredensial (Anthropic Personal, Google Sheets, Kirimi) — import n8n kadang melepasnya
3. Uji sebelum activate:
   - `"Batch 5 udah buka?"` → harus **sudah dibuka** + kirim link
   - `"programnya udah mulai belum?"` → belum, mulai 15 Agustus 2026
   - `"berapa biayanya?"` → harga keluar normal
   - `"mau transfer nih"` → `Baik, nanti akan dibantu cek dengan Sam yaa.` (tanpa notif ke Sam)
4. Pantau execution log: `DATA KONTRADIKTIF` dan `STATUS TIDAK DIKENALI` menandakan masalah di sheet, bukan di workflow

**Rollback:** import ulang `report/production/2026-08-08-VIRA-V4-retryable.json` (tidak disentuh sama sekali).

---

## Belum dikerjakan

**Janji notifikasi yang tidak bisa ditepati.** VIRA menjawab *"nanti saya kabari begitu Batch 5 dibuka"* dan *"Noted, nanti saya kabari ke nomor ini"*. Workflow ini hanya punya satu entry point — `n8n-nodes-base.webhook`. Tidak ada schedule/cron trigger dan tidak ada node kirim WA di luar alur balas-pesan, jadi **janji itu tidak akan pernah ditepati**. Customer di screenshot 12 Agustus sudah eksplisit minta nomornya dicatat. Opsi: VIRA berhenti menjanjikan (murah, cukup aturan di systemMessage), atau dibuatkan mekanisme waitlist beneran (lebih besar). Menunggu keputusan.
