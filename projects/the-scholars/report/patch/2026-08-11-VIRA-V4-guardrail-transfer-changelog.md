# VIRA V4 — Safeguard: VIRA Tidak Boleh Bicara Transfer

**Tanggal:** 2026-08-11
**Basis:** `report/production/2026-08-08-VIRA-V4-retryable.json` (tidak diubah)
**Hasil:** `report/patch/2026-08-11-VIRA-V4-guardrail-transfer.json`
**Pemicu:** Titipan Sam (owner The Scholars)

> "Mungkin bisa kita safeguard untuk VIRA jangan pernah ngomong tentang transfer. Karena transfer selalu dihandle sama gw. Jadi ini bikin confusing buat si customer kalau VIRA ngomong tentang transfer."

---

## Keputusan yang disepakati

| Hal | Keputusan |
|-----|-----------|
| Sebut harga/nominal | **TETAP BOLEH** — aturan `# HARGA` lama dipertahankan |
| Sebut transfer / minta bukti bayar / rekening | **DILARANG TOTAL** |
| Balasan pengganti | `"Baik, nanti akan dibantu cek dengan Sam yaa."` lalu berhenti |
| Notifikasi ke WA Sam | **TIDAK ADA** — tag `[TALK_TO_SAM]` sengaja tidak dipicu untuk topik pembayaran |

**Alur bisnis yang benar (dari Sam):** user isi form → Sam cek kualifikasi **manual** → kalau lolos, **Sam sendiri** yang menghubungi soal pembayaran. VIRA berhenti di angka harga.

---

## Akar masalah

Kalimat di screenshot produksi (`"Baik ditunggu yaa, kalau sudah transfer kirim buktinya ke sini."`) diperkuat dari **dua arah** sekaligus, makanya keluar konsisten:

1. `AI Agent` → `systemMessage`, section `# BATCH` — template balasan literal.
2. `Preprocess - Context Detection` → `persuasionMode === 'PAYMENT'` — kalimat yang sama disuntik ulang sebagai "contoh nada" ke `[CONTEXT:]` input AI.

Menghapus salah satu saja tidak cukup.

---

## Perubahan (3 node, 8 titik)

Node lain **tidak disentuh**. Verifikasi: jumlah node tetap 53, blok `connections` identik byte-per-byte.

### 1. `AI Agent` → `options.systemMessage`

**a. Section `# BATCH`** — template transfer dihapus:

```diff
- Transfer/bayar -> "Baik ditunggu yaa, kalau sudah transfer kirim buktinya ke sini."
+ Transfer/bayar/konfirmasi pembayaran -> BUKAN wilayahmu. Seluruh proses pembayaran ditangani Sam
+ sendiri secara manual (setelah form masuk, Sam yang menilai kualifikasi lalu menghubungi langsung).
+ Balas PERSIS: "Baik, nanti akan dibantu cek dengan Sam yaa." lalu BERHENTI. Jangan minta bukti,
+ jangan jelaskan cara bayar, jangan sebut rekening, jangan tanya balik, dan JANGAN pasang tag
+ [TALK_TO_SAM] untuk topik ini.
```

**b. Section `# HARGA`** — janji "skema pembayaran" dicabut (VIRA tidak boleh menjanjikan info yang bukan wewenangnya):

```diff
- Jawab: "Untuk harga dan skema pembayarannya nanti saya infokan begitu pendaftaran Batch berikutnya dibuka yaa."
+ Jawab: "Untuk harganya nanti saya infokan begitu pendaftaran Batch berikutnya dibuka yaa."
```

**c. Section `# HARGA`** — aturan baru "berhenti di angka":

```
- BERHENTI DI ANGKA. Setelah menyebut harga, JANGAN lanjut ke langkah/cara bayar, jangan tawarkan
  proses pembayaran, jangan sebut transfer. Alurnya: user isi form -> Sam cek kualifikasi manual ->
  Sam sendiri yang menghubungi soal pembayaran.
```

**d. Section `# LARANGAN`** — 2 bullet baru:

```
- MENYEBUT TRANSFER dalam bentuk apa pun: "transfer", "tf", "kirim bukti", "bukti transfer",
  "rekening", "no rek", "nomor rekening". Menyebut harga/nominal TETAP BOLEH (ikut # HARGA) -
  yang dilarang adalah membahas cara/langkah membayarnya.
- Mengonfirmasi pembayaran ("pembayarannya sudah masuk", "sudah saya terima"), meminta/menerima
  bukti bayar, mengecek atau memverifikasi pembayaran, dan menjanjikan slot karena sudah bayar.
  Semua kasus ini -> "Baik, nanti akan dibantu cek dengan Sam yaa."
```

### 2. `Preprocess - Context Detection` (node Code)

**a. Urutan cek diubah + trigger `PAYMENT` dirombak.**

Dua bug ditemukan saat QA (detail di bagian *Temuan QA* di bawah):

1. `PAYMENT` dicek **paling akhir** dalam rantai `if/else if`, jadi kalah oleh `INTERESTED` dan `DEFER`. Pesan `"oke deh, mau transfer"` jatuh ke `INTERESTED`; `"udah transfer nih, nanti kabarin ya"` jatuh ke `DEFER`. Guardrail lapis 2 tidak pernah aktif untuk dua pola itu. → `PAYMENT` dinaikkan ke urutan **pertama**.
2. Kata `bayar` / `pembayaran` telanjang sebagai pemicu terlalu luas — pertanyaan harga yang sah (`"bisa bayar 2x?"`) ikut kena handover. → dibuang dari pemicu; pemicu dipersempit ke intent transfer/bukti/rekening saja.

```diff
  let persuasionMode = '';
- if (message.match(/mau daftar|tertarik|boleh deh|mau coba|mau ikut|oke deh/i)) {
-   persuasionMode = 'INTERESTED';
- } else if (message.match(/nanti|pikir dulu|setelah ujian|belum sekarang|ragu|mikir|lihat dulu/i)) {
-   persuasionMode = 'DEFER';
- } else if (message.match(/\b(tf|transfer|bayar|mau bayar|sudah bayar|kirim bukti)\b/i)) {
-   persuasionMode = 'PAYMENT';
- }
+ // PAYMENT dicek PALING DULU: intent transfer harus menang atas 'oke deh' (INTERESTED)
+ // dan 'nanti' (DEFER), spt pesan "oke deh mau transfer" / "udah tf, nanti kabarin yaa".
+ // Catatan: kata 'bayar'/'pembayaran' telanjang SENGAJA tidak dipakai sebagai pemicu -
+ // itu biasanya pertanyaan harga/cicilan yang MASIH BOLEH dijawab.
+ if (message.match(/\b(tf|trf|transfer|mau bayar|sudah bayar|udah bayar|sdh bayar|kirim bukti|
+     bukti transfer|bukti bayar|bukti pembayaran|rekening|no rek|norek|nomor rekening|
+     bayar ke ?mana|kirim ke ?mana|bayarnya ke ?mana)\b/i)) {
+   persuasionMode = 'PAYMENT';
+ } else if (message.match(/mau daftar|tertarik|boleh deh|mau coba|mau ikut|oke deh/i)) {
+   persuasionMode = 'INTERESTED';
+ } else if (message.match(/nanti|pikir dulu|setelah ujian|belum sekarang|ragu|mikir|lihat dulu/i)) {
+   persuasionMode = 'DEFER';
+ }
```

Pembagian tugasnya jadi tegas: **lapis 2 mengurus intent transfer** (user mau/sudah bayar, tanya rekening), **pertanyaan harga & cicilan tetap dijawab normal**, dan **lapis 3 menjaga kata-katanya** di semua kasus.

**b. `aiContext` untuk mode `PAYMENT` diganti total:**

```diff
- aiContext += `User konfirmasi pembayaran. Balas singkat & hangat, contoh nada:
-   "Baik ditunggu yaa, kalau sudah transfer kirim buktinya ke sini." `;
+ aiContext += `User menyinggung pembayaran/transfer. PEMBAYARAN DITANGANI SAM MANUAL, bukan kamu.
+   Balas PERSIS: "Baik, nanti akan dibantu cek dengan Sam yaa." lalu berhenti. DILARANG menyebut
+   transfer/tf/rekening/bukti bayar, dilarang minta bukti, dilarang konfirmasi pembayaran diterima,
+   dilarang pasang tag [TALK_TO_SAM]. `;
```

### 3. `Process All` (node Code) — **safety net baru**

Prompt bisa dilanggar model, dan data harga ditarik live dari Google Sheet (isinya bisa berubah kapan saja). Jadi dipasang filter keras persis sebelum teks dikirim ke WhatsApp, mengikuti pola safety net vokatif ("Om/Tante") yang sudah ada di node ini.

```js
const TRANSFER_SAFE_REPLY = 'Baik, nanti akan dibantu cek dengan Sam yaa.';
const transferRegex = /(\btransfer\b|\btf\b|\btrf\b|\brekening\b|\bnorek\b|\bno\.?\s*rek\b|
  \bnomor\s*rekening\b|bukti\s*(transfer|bayar|pembayaran)|kirim\s*bukti|konfirmasi\s*pembayaran|
  pembayaran\s*(nya\s*)?(sudah|udah|telah)\s*(masuk|diterima|kami\s*terima)|
  sudah\s*(saya|kami)\s*terima\s*pembayaran)/i;
```

Cara kerja: **per kalimat**, bukan per pesan. Hanya kalimat yang menyinggung transfer yang dibuang; kalimat harga di pesan yang sama tetap selamat. Baris kosong asli dipertahankan supaya format paragraf & link GForm tidak rusak. Kalau ada yang dicegat, `TRANSFER_SAFE_REPLY` ditempelkan di akhir. Kalau seluruh pesan habis, pesan diganti penuh dengan kalimat itu.

Ditambahkan juga flag `transferBlocked` ke output node untuk audit di n8n execution log (disertai `console.warn` sebelum/sesudah).

Catatan: filter ini berjalan **setelah** deteksi `isTalkToSam` (yang membaca `aiOutput` mentah), jadi tidak memicu notifikasi ke WA Sam — sesuai keputusan. Kalimat pengganti juga sengaja tidak memakai frasa `"sampaikan ke Sam"` yang ada di daftar fallback `talkToSamPatterns`.

---

## Temuan QA (dan perbaikannya)

QA dijalankan setelah patch pertama jadi. Empat hal yang ditemukan:

| # | Temuan | Status |
|---|--------|--------|
| 1 | `PAYMENT` dicek terakhir di if-chain → kalah oleh `INTERESTED`/`DEFER`. `"oke deh, mau transfer"` dan `"udah transfer nih, nanti kabarin ya"` lolos dari guardrail lapis 2. **Bug ini sudah ada di workflow asli**, bukan dari patch. | **Diperbaiki** — `PAYMENT` dinaikkan ke urutan pertama |
| 2 | Pemicu `PAYMENT` yang saya perluas memuat `bayar`/`pembayaran` telanjang → pertanyaan harga sah (`"bisa bayar 2x?"`) ikut kena handover, bentrok dengan keputusan "harga tetap boleh". | **Diperbaiki** — pemicu dipersempit ke intent transfer/bukti/rekening |
| 3 | Safety net awal membuang baris kosong → spasi paragraf & pemisah link GForm rusak saat filter aktif. | **Diperbaiki** — baris kosong asli dipertahankan |
| 4 | Node.js tidak terpasang di mesin ini → kode hasil patch tidak bisa dieksekusi sebagai JavaScript. | **Mitigasi**, lihat batasan di bawah |

### Audit statis yang dijalankan

- **Sintaks JS** — 13 node Code (asli & patch) di-parse pakai `esprima`, dibungkus sebagai badan fungsi supaya `return` top-level sah. **13/13 OK, 0 regresi** akibat patch.
- **Titik kirim tunggal** — ditelusuri mundur dari node pengirim: `Send WA + Verify (Kirimi)` ← `Wait1` ← `Process All` ← `AI Agent`. Node pengirim membaca `$('Process All').first().json.cleanOutput` — **persis variabel yang difilter safety net**. Tidak ada jalur teks ke customer yang melewati lapis 3. (`Notify Admin Unknown` dan `Notify Talk to Sam` mengirim ke WA Sam `6596110395`, bukan customer; node GForm sender dalam keadaan `disabled`.) `INTRO` user baru cuma instruksi ke dalam prompt, bukan kiriman terpisah.
- **Tabrakan nama variabel** — 6 identifier baru (`TRANSFER_SAFE_REPLY`, `transferRegex`, `transferBlocked`, `beforeNet`, `keptLines`, `DROP`) dicek terhadap kode asli `Process All`: **nol kemunculan sebelumnya**, tidak ada shadowing.
- **Flag regex** — `transferRegex` memakai flag `i` saja, **tanpa `/g`**. Penting: `RegExp.test()` dengan flag `/g` itu stateful (`lastIndex` berjalan) dan akan memberi hasil selang-seling.
- **Kalimat pengganti vs notifikasi** — dicek terhadap daftar `talkToSamPatterns` di `Process All`: tidak ada yang cocok, jadi tidak memicu notif ke WA Sam.

---

## Hasil uji

Regex diambil **langsung dari file hasil patch** (bukan disalin ulang) lalu diuji: **14 kasus routing lapis 2 + 13 kasus safety net lapis 3 + 5 assertion lapis 1 = 32 assertion, semua lolos, 0 kebocoran kata transfer.**

### Lapis 2 — routing `persuasionMode`

| Pesan user | Mode lama | Mode baru |
|---|---|---|
| `mau transfer nih` | PAYMENT | PAYMENT |
| `udah tf ka` | PAYMENT | PAYMENT |
| `oke deh, mau transfer` | ⚠️ INTERESTED | **PAYMENT** |
| `udah transfer nih, nanti kabarin ya` | ⚠️ DEFER | **PAYMENT** |
| `kirim ke rekening mana?` | ⚠️ (tidak kena) | **PAYMENT** |
| `bukti bayarnya kirim ke mana?` | ⚠️ (tidak kena) | **PAYMENT** |
| `bisa bayar 2x?` | ⚠️ PAYMENT | **(normal — harga dijawab)** |
| `Boleh tanya biaya nya brp ya` | (normal) | (normal) |
| `pembayarannya gimana ya?` | (normal) | (normal) |
| `mau daftar ka` | INTERESTED | INTERESTED |
| `nanti dulu deh, pikir dulu` | DEFER | DEFER |

### Lapis 3 — safety net `cleanOutput`

| Skenario | Input | Output |
|---|---|---|
| Kalimat asli dari screenshot | `Baik ditunggu yaa, kalau sudah transfer kirim buktinya ke sini.` | `Baik, nanti akan dibantu cek dengan Sam yaa.` |
| Harga + ajakan transfer | `Rp 9.000.000 yaa, dibagi 2x bayar: Rp 6.000.000 di awal. Kalau sudah transfer kirim buktinya ke sini yaa.` | `Rp 9.000.000 yaa, dibagi 2x bayar: Rp 6.000.000 di awal.`<br>`Baik, nanti akan dibantu cek dengan Sam yaa.` |
| Harga murni | `Rp 9.000.000 yaa, dibagi 2x bayar.` | **tidak diubah** |
| Cicilan | `Untuk pembayarannya bisa dicicil 2x yaa.` | **tidak diubah** |
| Minta bukti bayar | `Boleh dikirim bukti bayarnya ke sini yaa.` | `Baik, nanti akan dibantu cek dengan Sam yaa.` |
| Konfirmasi bayar masuk | `Oke, pembayarannya sudah masuk yaa. Terima kasih.` | `Terima kasih.`<br>`Baik, nanti akan dibantu cek dengan Sam yaa.` |
| Nomor rekening | `Silakan kirim ke nomor rekening BCA 123456 atas nama Sam.` | `Baik, nanti akan dibantu cek dengan Sam yaa.` |
| Singkatan `tf` | `Kalau sudah tf, info ke sini yaa.` | `Baik, nanti akan dibantu cek dengan Sam yaa.` |
| Multi-baris + link GForm | `Boleh daftar di sini yaa.`<br>`https://forms.gle/ABC`<br>`Kalau sudah transfer kirim buktinya.` | `Boleh daftar di sini yaa.`<br>`https://forms.gle/ABC`<br>`Baik, nanti akan dibantu cek dengan Sam yaa.` |
| Balasan normal | `Satu kelas sekitar 15 anak yaa. Untuk harganya nanti saya infokan begitu Batch 5 dibuka.` | **tidak diubah** |
| Kontrol false-positive `tf` | `Boleh daftar di sini yaa, tinggal isi formnya.` | **tidak diubah** |
| Intro user baru | `Haloo thank you sudah contact TheScholars.id yaa...` | **tidak diubah** |
| Kalimat pengganti itu sendiri | `Baik, nanti akan dibantu cek dengan Sam yaa.` | **tidak diubah** (tidak memfilter dirinya sendiri) |

---

## Batasan QA — yang BELUM diuji

Supaya jelas sampai mana jaminannya:

1. **Kode belum pernah dieksekusi sebagai JavaScript.** Node.js/Deno/Bun tidak terpasang di mesin ini. Sintaks sudah divalidasi parser (`esprima`) dan logika regex diuji lewat port 1:1 ke Python, tapi itu bukan pengganti run beneran di n8n. Perbedaan JS↔Python yang relevan sudah diperiksa satu per satu dan **nihil** untuk kasus ini: tidak ada capture group di regex `split` (jadi `String.split` tidak menyisipkan grup ke hasil), tidak ada flag `/g` (jadi `test()` tidak stateful), dan lookbehind `(?<=[.!?])` didukung Node 9+ (n8n butuh Node 18+).
2. **Belum diuji di n8n sungguhan** — import, binding kredensial, dan eksekusi end-to-end lewat WhatsApp belum dijalankan. Ini wajib dilakukan Steven sebelum activate.
3. **Perilaku AI belum diuji.** Lapis 1 & 2 itu instruksi ke model, dan model bisa saja tidak patuh. Yang dijamin deterministik cuma lapis 3. Artinya: kata transfer **tidak akan pernah sampai ke customer**, tapi *bentuk* balasan saat guardrail aktif belum tentu seindah yang dirancang — bisa saja kalimat harga terpotong lalu menyambung agak kaku ke kalimat pengganti.
4. **Isi Google Sheet belum dicek** — lihat bagian berikutnya.

---

## ⚠️ BELUM SELESAI — perlu dicek manual di luar workflow

Nomor rekening dan nominal Rp **tidak ada** di file workflow. Harga ditarik **live saat runtime** oleh node `FAQ Retrieve` dari Google Sheet tab `PROGRAM`, kolom **`Harga`**, **`Pembayaran`**, dan **`Catatan`**, lalu disuntik ke system message sebagai `data_context`.

Kalimat `"dibagi 2x bayar: Rp 6.000.000 di awal saat konfirmasi"` di screenshot kemungkinan besar berasal dari kolom `Pembayaran` itu.

**Tindakan:** buka sheet `PROGRAM` dan cek isi kolom `Pembayaran` + `Catatan`. Kalau di dalamnya ada kata "transfer", instruksi kirim bukti, atau nomor rekening:
- Safety net di `Process All` **akan tetap mencegatnya** sebelum sampai ke customer (lapis 3 memang dipasang untuk ini), **tapi**
- akibatnya kalimat itu ikut terpotong dari balasan, jadi lebih rapi kalau teks di sheet-nya juga dibersihkan di sumbernya.

---

## Cara deploy

1. n8n → **Import from File** → `2026-08-11-VIRA-V4-guardrail-transfer.json`.
2. Cek kredensial masih ter-mapping (Anthropic Personal, Google Sheets, Kirimi) — import n8n kadang melepas binding kredensial.
3. Uji 4 skenario di chat sungguhan sebelum di-activate:
   - `"berapa biayanya?"` → harga tetap keluar normal
   - `"mau transfer nih"` → `Baik, nanti akan dibantu cek dengan Sam yaa.`
   - `"udah tf ka"` → sama
   - `"kirim ke rekening mana?"` → sama
4. Pastikan WA Sam **tidak** menerima notifikasi dari keempat tes di atas.
5. Pantau execution log untuk `transferBlocked: true` — kalau sering muncul, artinya AI masih sering improvisasi soal transfer dan prompt-nya perlu dipertegas lagi.

**Rollback:** import ulang `report/production/2026-08-08-VIRA-V4-retryable.json` (file itu tidak disentuh sama sekali).
