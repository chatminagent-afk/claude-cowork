# Planning: Enrich Sheet PRODUK — VIRA PCR

**Tanggal:** 2026-07-20
**Pemicu:** VIRA salah info ke user — menyatakan "setelah akad dapat cashback Rp20 juta".
**Fakta:** cashback Rp20jt adalah **potongan harga di depan**, bukan uang tunai setelah akad.
`Maksimal KPR = Harga Jual − Bonus Cashback − Uang Muka`.
**Status:** menunggu approval Steven. Belum ada perubahan yang diterapkan ke `PCR_Database.xlsx`.

---

## 1. Root cause

Sheet PRODUK menyimpan seluruh angka finansial sebagai **prosa di dalam 3 kolom** (`Harga Normal`, `Booking Fee / DP`, `Promo Berlaku`). Tidak ada satu pun angka yang berdiri sendiri sebagai field terstruktur, dan tidak ada relasi antar-angka yang tertulis eksplisit.

Kalimat yang dibaca AI saat ini (kolom `Promo Berlaku`):

> "Bonus Cashback Rp20.000.000 diberikan sebelum akad; jadi harga awal - bonus cashback - uang muka."

Klausa keduanya benar, tapi terpotong di tengah kalimat panjang berisi 5 klaim lain, dan kata **"diberikan"** membaca seperti pemberian tunai. AI mengambil framing "diberikan sebelum akad" → keluar sebagai "dapat cashback 20 juta". Tidak ada kolom yang bisa dipakai AI untuk cross-check bahwa 20jt itu sudah habis dipotong di plafon KPR.

Diperparah: `Harga Normal` = `Rp383.004.784` sementara `Maksimal KPR` tidak ada sama sekali di sheet, sehingga AI tidak punya angka pembanding untuk menyadari kontradiksinya.

---

## 2. Pola perhitungan hasil reverse-engineering (terverifikasi 100%)

Seluruh angka di kedua pricelist berhasil direproduksi sampai rupiah terakhir.

### 2.1 Komersil (36/72 & 36/81)

```
Harga Setelah Bonus = Harga Jual − Bonus Cashback (Rp20.000.000)
Uang Muka           = 5%  × Harga Setelah Bonus
Maksimal KPR        = 95% × Harga Setelah Bonus
                    = Harga Jual − Bonus Cashback − Uang Muka
Angsuran            = ANUITAS atas Maksimal KPR, bunga 8,25% p.a.
```

| Komponen | 36/72 | 36/81 |
|---|---:|---:|
| Harga Jual | 383.004.784 | 409.294.258 |
| − Bonus Cashback | 20.000.000 | 20.000.000 |
| = Harga Setelah Bonus | 363.004.784 | 389.294.258 |
| Uang Muka (5%) | **18.150.239** ✓ | **19.464.713** ✓ |
| Maksimal KPR (95%) | **344.854.545** ✓ | **369.829.545** ✓ |

Angsuran — anuitas 8,25% p.a. cocok pada **keempat tenor untuk kedua tipe** (selisih maks Rp1 karena pembulatan):

| Tenor | 36/72 | 36/81 |
|---|---:|---:|
| 15 thn | 3.345.573 | 3.587.865 |
| 20 thn | 2.938.387 | 3.151.190 |
| 25 thn | 2.719.006 | 2.915.921 |
| 30 thn | 2.590.777 | 2.778.405 |

### 2.2 Subsidi (30/60)

```
Maksimal KPR = Harga Jual − Uang Muka        (tidak ada bonus/cashback)
185.000.000 − 5.850.000 = 179.150.000 ✓
Angsuran     = ANUITAS atas Maksimal KPR, bunga 5,00% p.a. tetap sampai lunas
```

| Tenor | Angsuran |
|---|---:|
| 10 thn | 1.900.164 ✓ |
| 15 thn | 1.416.707 ✓ |
| 20 thn | 1.182.311 ✓ |

**Catatan penting:** label di pricelist berbunyi *"ANGSURAN FLAT 5%"*, tapi secara matematis ini **anuitas** dengan bunga tetap 5% (flat = *bunganya* tetap sampai lunas, bukan metode flat-rate). Jangan sampai VIRA menjelaskan cara hitung flat-rate — cukup sebut "bunga 5% tetap sampai lunas".

Uang muka subsidi Rp5.850.000 = 3,16% dari harga — **bukan** persentase bulat, jadi diperlakukan sebagai **angka tetap dari pricelist**, bukan hasil rumus.

---

## 3. Konflik data yang harus dikonfirmasi ke Om Sulianto

Dua-duanya sudah ada di sheet sekarang dan saling bertabrakan tanpa penjelasan — ini sumber halusinasi berikutnya kalau tidak diselesaikan.

| # | Konflik | Isi sheet sekarang | Isi pricelist | Dampak |
|---|---|---|---|---|
| K1 | **DP komersil** | "TANPA DP — booking fee Rp2.500.000 all-in sampai terima kunci" | Uang Muka Rp18.150.239 | User tanya "jadi saya bayar berapa di awal?" → VIRA bisa jawab 2,5jt ATAU 18,1jt. Perlu kalimat resmi: apakah UM 5% ditanggung developer/masuk skema promo, atau tetap dibayar user? |
| K2 | **DP subsidi** | "DP Rp9.000.000 ALL-IN (booking 1,5jt + DP 7,5jt, termasuk BPHTB/AJB)" | Uang Muka Rp5.850.000 | Selisih Rp3.150.000 diduga BPHTB/AJB/surat-surat. Perlu ditulis eksplisit supaya VIRA bisa jelaskan rinciannya, bukan menyebut dua angka acak. |
| K3 | **Angsuran subsidi** | 1.900.000 / 1.400.000 / 1.100.000 (dibulatkan) | 1.900.164 / 1.416.707 / 1.182.311 | Angka sheet meleset s.d. Rp82.311/bln di tenor 20 thn. Harus dipakai angka pricelist. |
| K4 | **Umur pricelist subsidi** | — | tertera "Per Mei 2025" (14 bulan lalu) | Perlu konfirmasi harga & angsuran subsidi masih berlaku per Juli 2026. |
| K5 | **Bunga komersil** | "mengikuti suku bunga bank, flat mulai tahun ke-4" | 8,25% p.a. (implisit dari angka) | 8,25% adalah **asumsi pricelist**, bukan janji bank. VIRA wajib menyebutnya sebagai perkiraan. |

Sampai K1–K5 dijawab, kolom-kolom baru untuk poin tersebut diisi dengan penanda status, bukan dikosongkan atau ditebak.

---

## 4. Rancangan enrichment sheet PRODUK

### Prinsip

1. **Angka terstruktur, satu angka satu kolom.** AI tidak boleh perlu mem-parsing kalimat untuk dapat nominal.
2. **Rumus ditulis eksplisit sebagai data**, bukan diasumsikan bisa disimpulkan AI.
3. **Anti-miskonsepsi eksplisit.** Kesalahan yang sudah pernah terjadi ditulis sebagai larangan berlabel, bukan diharapkan tidak terulang.
4. **Prosa lama dirapikan**, bukan digandakan — kolom prosa yang angkanya sudah pindah ke kolom numerik dipangkas supaya token tidak membengkak.
5. **Konflik ditandai, bukan disembunyikan.**

### 4.1 Kolom BARU (T–AB, 9 kolom)

| Kol | Nama Kolom | Tujuan | Ember* |
|---|---|---|---|
| T | `Harga Jual (Rp)` | Angka murni harga jual | MONEY |
| U | `Bonus Cashback (Rp)` | 20000000 / 0 | MONEY |
| V | `Uang Muka Pricelist (Rp)` | 18150239 / 19464713 / 5850000 | MONEY |
| W | `Maksimal KPR (Rp)` | 344854545 / 369829545 / 179150000 | MONEY |
| X | `Bunga Acuan Simulasi` | "8,25% p.a. anuitas (asumsi pricelist, bukan komitmen bank)" | MONEY |
| Y | `Tabel Angsuran Resmi` | "15 thn Rp3.345.573 \| 20 thn Rp2.938.387 \| …" | MONEY |
| Z | `Rumus Harga` | Rantai perhitungan dalam satu kalimat | MONEY |
| AA | `Anti-Miskonsepsi` | Larangan eksplisit (termasuk kasus cashback) | MONEY |
| AB | `Sumber & Tanggal Pricelist` | "Pricelist resmi (foto), per Mei 2025" dst. | CORE |

\* Ember = bucket serialisasi di node `FAQ Retrieve` (lihat §5).

### 4.2 Kolom LAMA yang diubah

| Kol | Nama | Perubahan |
|---|---|---|
| F | `Harga Normal` | Buang nominal (sudah di kolom T) → sisakan pointer media saja |
| H | `Booking Fee / DP` | Buang nominal uang muka & maks KPR (sudah di V/W) → sisakan penjelasan skema + penanda konflik K1/K2 |
| I | `Skema Cicilan` | Buang daftar angsuran (sudah di Y) → sisakan penjelasan sifat bunga |
| Q | `Promo Berlaku` | **Perbaikan utama** — kalimat cashback ditulis ulang agar tidak bisa dibaca sebagai uang tunai |
| S | `Last Update` | 2026-07-20 |

Kolom lain (A–E, G, J–P, R) tidak berubah.

---

## 5. Perubahan sisi n8n yang WAJIB menyertai (jangan dilewat)

Node **`FAQ Retrieve`** di `VIRA-PCR Main V1.2.json` mem-bucket kolom PRODUK menjadi CORE / MONEY / SPEK. Kolom yang **tidak dikenal namanya masuk ember SPEK**, dan SPEK hanya dikirim saat `discussingUnit || askingFasilitas || askingLegalitas`.

**Artinya: kalau sheet di-enrich tanpa patch ini, 8 kolom finansial baru TIDAK terkirim saat user cuma tanya harga (`askingPrice`) — bug-nya tidak sembuh.**

Patch pada `const MONEY = new Set([...])`:

```js
const CORE  = new Set(['kategori', 'harga normal', 'status stok',
                       'sumber & tanggal pricelist']);
const MONEY = new Set(['harga promo', 'batas tanggal promo', 'booking fee/dp',
                       'skema cicilan', 'bank/skema kpr', 'promo berlaku',
                       'harga jual (rp)', 'bonus cashback (rp)',
                       'uang muka pricelist (rp)', 'maksimal kpr (rp)',
                       'bunga acuan simulasi', 'tabel angsuran resmi',
                       'rumus harga', 'anti-miskonsepsi']);
```

Ditambah menaikkan batas `clip()` khusus kolom `Rumus Harga` & `Anti-Miskonsepsi` dari 220 → 300 karakter, karena kedua kolom itu akan terpotong di tengah kalimat pada 220.

**Dampak token:** ember MONEY naik ± 480 token per giliran yang menyentuh harga. Dikompensasi pemangkasan kolom F/H/I/Q (± −300 token). Net ± +180 token, hanya pada giliran ber-intent harga.

---

## 6. Perubahan system prompt (opsional, direkomendasikan)

Tambahkan satu baris di blok anti-halusinasi (sekitar baris 18–20 `2026-07-17-enhanced-system-prompt-vira-pcr.md`):

> - Untuk pertanyaan harga/DP/cicilan: pakai kolom angka (`Harga Jual`, `Bonus Cashback`, `Uang Muka Pricelist`, `Maksimal KPR`, `Tabel Angsuran Resmi`) dan ikuti kolom `Rumus Harga` apa adanya. DILARANG menghitung sendiri di luar rumus itu, dan DILARANG menyebut bonus/cashback sebagai uang yang diterima user.

---

## 7. Urutan eksekusi

| Paket | Isi | Prasyarat |
|---|---|---|
| P1 | Enrich `PCR_Database.xlsx` sheet PRODUK (§4) | approval Steven |
| P2 | Copy-paste hasil P1 ke live Google Sheet | P1 selesai |
| P3 | Patch node `FAQ Retrieve` (§5) | P2 selesai — kalau dibalik, kolom baru terkirim sebelum ada isinya |
| P4 | Tambah baris system prompt (§6) | P3 |
| P5 | Regresi: "cashback 20jt dapat kapan?", "cicilan 36/72 20 tahun?", "DP berapa?", "total bayar di awal?" | P4 |
| P6 | Update sheet setelah K1–K5 dijawab Om Sulianto | jawaban klien |

K1–K5 dan P3–P6 dicatat ke `Pending Waiting Changes.md`.
