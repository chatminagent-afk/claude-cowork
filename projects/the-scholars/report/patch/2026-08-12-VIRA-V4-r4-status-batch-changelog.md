# VIRA V4 r4 — Diagnostik di Output Node + Perbaikan Jawaban Meleset

**Tanggal:** 2026-08-12
**Basis:** `2026-08-12-VIRA-V4-r3-status-batch.json`
**Hasil:** `2026-08-12-VIRA-V4-r4-status-batch.json` — **kumulatif**, ini yang di-import.
**Pemicu:** log produksi r3 — data sudah pulih, tapi VIRA tidak menjawab pertanyaan yang diajukan.

---

## Kasus yang memicu

Pesan user (dua pertanyaan digabung debounce):
> `nanti tolong segera kabarin ya kalo batch 5 sudah dibuka`
> `kapan batch berikutnya dimulai?`

Jawaban VIRA:
> `Untuk Seniors, pendaftarannya sudah dibuka sekarang yaa. Kalau mau daftar, tinggal bilang aja.`

Tidak salah secara fakta — Seniors memang `DIBUKA`. Tapi **tidak menjawab satu pun pertanyaannya**: Batch 5 (statusnya `SUDAH DITUTUP`) tidak disinggung, dan tanggal mulai (`15 Agustus 2026`) yang ada di DATA tidak disebut.

Yang benar kira-kira: *"Untuk Batch 5 (Junior/Intermediate) pendaftarannya sudah ditutup yaa. Programnya mulai 15 Agustus 2026. Kalau untuk kelas 12, yang cocok Seniors dan pendaftarannya masih dibuka."*

**Dua penyebab, keduanya diperbaiki di r4.**

---

## Perubahan (3 node, 8 titik)

Jumlah node tetap 53, `connections` identik dengan workflow produksi asli.

### 1. `Preprocess` — `DEFER` tidak lagi kena kata `nanti` telanjang

```diff
- } else if (message.match(/nanti|pikir dulu|setelah ujian|belum sekarang|ragu|mikir|lihat dulu/i)) {
+ } else if (message.match(/nanti (dulu|aja|saja|lah)|nanti deh|pikir dulu|pikir-?2? dulu|
+     pikirkan dulu|dipikir dulu|setelah ujian|belum sekarang|belum kepikiran|masih ragu|\bragu\b|
+     mikir (dulu|lagi)|lagi mikir|dipikir-?pikir|lihat dulu|liat dulu|tunggu dulu|nunggu dulu/i)) {
    persuasionMode = 'DEFER';
  }
```

Pesan itu terbaca `DEFER` hanya karena memuat kata **`nanti`**, padahal user tidak menunda — ia minta dikabari. Akibatnya `aiContext` menyuntik *"User menunda. Validasi singkat dan santai, beri ruang tanpa menekan waktu"*, yang menyuruh model memangkas jawaban.

Pola yang dulu salah tertangkap: `"nanti tolong kabarin"`, `"nanti saya tanya lagi"`, `"nanti daftar"`.

### 2. `systemMessage` — pertanyaan langsung menang atas segmentasi

Karena `KELAS_ANAK = SMA 12`, context menyuntik *"Sebut HANYA program Seniors"*. Pengecualian *"kecuali user tanya"* sudah ada tapi terlalu lemah — model tetap mengunci ke Seniors walau user menyebut "batch 5" secara eksplisit.

```
- PERTANYAAN LANGSUNG MENANG ATAS SEGMENTASI: kalau user menyebut nama program atau nama batch
  secara EKSPLISIT (mis. "batch 5", "Junior", "Mock Interview", "Seniors"), WAJIB dijawab untuk
  program/batch ITU dari DATA - walaupun tidak cocok dengan kelas anaknya. Baru setelah itu boleh
  arahkan ke program yang sesuai kelasnya. DILARANG mengganti pertanyaan user dengan program lain
  tanpa menjawab yang ditanya.
- JAWAB SEMUA YANG DITANYA: satu pesan bisa berisi lebih dari satu pertanyaan (pesan user sering
  digabung sistem). Jawab semuanya, jangan ada yang dilewat. Tetap ringkas.
```

### 3. `systemMessage` — wajib menyebut tanggal mulai

```
- Ditanya KAPAN batch mulai / kapan programnya jalan -> sebut "Program mulai <tanggal>" dari DATA
  apa adanya. Jangan menjawab dengan status pendaftaran saja, dan jangan menjawab tidak tahu kalau
  tanggalnya ada di DATA.
```

### 4. `FAQ Retrieve` — diagnostik pindah ke OUTPUT node

Di r3, hasil diagnosis hanya masuk `console.log/warn/error`, yang di n8n muncul di panel **Logs** — bukan di output JSON node. Karena alur kerja pemeriksaan selama ini lewat output node, diagnostiknya jadi tidak pernah terbaca.

Sekarang setiap pembacaan sheet dicatat ke field **`sheet_debug`** di output:

| Nilai `sheet_debug` | Artinya |
|---|---|
| `4 baris — normal` | baca sheet normal |
| `4 baris — FALLBACK run pertama (run saat ini error: ...)` | **dugaan run-index terbukti**, fallback menyelamatkan |
| `4 baris — FALLBACK run pertama (run saat ini 0 baris)` | idem, versi tanpa error |
| `GAGAL — <pesan error>` | pembacaan sheet benar-benar error |
| `0 baris — KOSONG` | node jalan tapi tidak mengembalikan baris |

Contoh output yang diharapkan:

```json
"sheet_issues": [],
"sheet_debug": {
  "Read PROGRAM Data": "4 baris — normal",
  "Read LINKS Data": "6 baris — normal",
  "Read FAQ": "113 baris — normal"
}
```

`console.*` tetap dipertahankan untuk yang punya akses panel Logs. `catch` besar di ujung node juga mengisi `sheet_debug`.

---

## Hasil QA — 80 assertion, 0 gagal

Semua regex dan logika diambil **langsung dari file hasil patch**, bukan disalin ulang.

| Kelompok | Isi | Hasil |
|---|---|---|
| **A. Struktur** | 53 node, `connections` identik dengan r3 **dan** dengan workflow produksi asli, hanya 3 node berubah | 4/4 |
| **B. Sintaks** | 13 node Code di-parse `esprima`, dibandingkan dengan produksi | 1/1, 0 regresi |
| **C. Routing** | 18 pesan — termasuk pesan asli yang tadi salah, 6 penundaan sungguhan, PAYMENT menang atas INTERESTED & DEFER, pertanyaan harga tetap normal | 19/19 |
| **D. Verdict** | 14 kombinasi Status × tanggal + 4 baris data asli sheet | 18/18 |
| **E. Transfer** | 13 kalimat, termasuk kalimat asli screenshot dan `"Batch 5 sudah ditutup"` (tidak boleh kena) + cek flag `/g` | 14/14 |
| **F. systemMessage** | 12 aturan wajib ada + nol hardcode batch + template transfer lama hilang | 14/14 |
| **G. Diagnostik** | `sheet_debug` di output, 4 jalur pencatatan, fallback run-0, penanda database tidak terbaca | 10/10 |

Total node yang berubah sejak workflow produksi `2026-08-08-VIRA-V4-retryable`:
`AI Agent` · `Cek_user_status` · `FAQ Retrieve` · `Preprocess - Context Detection` · `Process All`

**Batasan (tidak berubah):** tidak ada Node.js di mesin ini — kode belum pernah dieksekusi sebagai JavaScript. Validasi sebatas parser `esprima` + port logika 1:1 ke Python. Perbedaan JS↔Python yang relevan sudah diperiksa dan nihil untuk kasus ini.

---

## File pendamping

| File | Isi |
|---|---|
| `2026-08-12-VIRA-V4-r4-snippet-faq-retrieve.js` | kode `FAQ Retrieve` lengkap (256 baris), siap paste |
| `2026-08-12-VIRA-V4-r4-snippet-preprocess.js` | kode `Preprocess` lengkap (254 baris) |

---

## Cara uji setelah import

1. Ulangi pesan yang tadi meleset: `"nanti tolong segera kabarin ya kalo batch 5 sudah dibuka"` + `"kapan batch berikutnya dimulai?"`
   - **Harapan:** VIRA menyebut Batch 5 **sudah ditutup**, menyebut **15 Agustus 2026**, lalu baru mengarahkan ke Seniors
   - Cek `persuasionMode` di output — harus **kosong**, bukan `DEFER`
2. Cek field **`sheet_debug`** di output `FAQ Retrieve` — ini yang akhirnya menjawab penyebab data kosong kemarin
3. `"mau transfer nih"` → `Baik, nanti akan dibantu cek dengan Sam yaa.`
4. `"nanti dulu deh, pikir dulu"` → `persuasionMode` harus tetap `DEFER` (tidak ikut rusak)

**Rollback:** import ulang `report/production/2026-08-08-VIRA-V4-retryable.json`.
