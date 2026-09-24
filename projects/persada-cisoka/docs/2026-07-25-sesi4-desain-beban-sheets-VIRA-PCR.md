# Sesi 4 — Desain: Turunkan Beban Google Sheets

**Tanggal:** 2026-07-25
**Status:** desain, belum diimplementasi. Butuh go/no-go Steven.
**Basis:** peta ketergantungan `$('Nama Node')` seluruh 88 node (Sesi 4 tahap baca).

---

## 0. Kesimpulan yang harus dibaca lebih dulu

**Sesi 4 membeli ~1,8–2× kapasitas, bukan 100×.** Saya hitung ulang dan angka di laporan awal terlalu optimis.

Alasannya struktural: setiap pesan **wajib** baca STATS minimal 2×, dan itu tidak bisa dihapus tanpa mengganti backing store.

1. **Baca STATS #1** — sebelum buffer: resolve identitas user (No WA/lid) + cek `bot_mode`. Harus terjadi sebelum pesan masuk MSG_BUFFER.
2. **Baca STATS #2** — sesudah `Wait3`: baca ulang `debounce_ts` untuk menentukan siapa pemenang race. Nilainya baru valid setelah jeda 60 detik, jadi tidak bisa digabung dengan #1.

Dua read itu × jumlah pesan adalah lantai keras. Selama STATS hidup di Google Sheets dengan kuota 60 read/menit/user, plafonnya:

```
60 read/menit ÷ 2 read/pesan  =  30 pesan/menit  (batas teoretis absolut)
```

Dan itu mengabaikan semua write. Realistisnya setelah Sesi 4: **~12 giliran/menit** (naik dari ~6,6).

**Artinya: Sesi 4 bukan jawaban untuk 100×. Ia membeli headroom sambil migrasi STATS ke database sungguhan disiapkan.** Kalau target akhirnya di atas ~10.000 pesan/hari, Postgres/Supabase bukan opsi — wajib, dan Sesi 4 sebaiknya dipangkas ke bagian yang tidak akan dibuang saat migrasi (R2 + perbaikan bug), bukan dikerjakan penuh.

---

## 1. Beban sekarang — dihitung per giliran percakapan

Yang penting bukan "read per pesan" tapi **read per giliran**, karena user WhatsApp sering mengetik beberapa bubble beruntun dan hanya satu yang menang debounce.

Jalur **pecundang debounce** (dibuang di `IF_Chat_Debounce`) — 4 read + 2 write:
`Read CONFIG` → `Read User STATS` → `Read STATS for HITL` → *Wait3* → `Re-Read STATS Debounce` → ✗

Jalur **pemenang** — 9 read:
4 read di atas + `Read MSG_BUFFER` + `Read FAQ` + `Read PRODUK Data` + `Read LINKS Data` + `Read STATS`

| Bubble per giliran | Read sekarang | Plafon (60/menit) |
|---|---|---|
| 1 | 9 | 6,6 giliran/menit |
| 3 | 2×4 + 9 = **17** | 3,5 giliran/menit |

---

## 2. Perubahan yang diusulkan

### R1 — Gabung `Read User STATS` + `Read STATS for HITL` → 1 read
**Hemat 1 read per PESAN** (termasuk pecundang — pengali terbesar).

Keduanya baca seluruh tab STATS tanpa filter, keduanya sebelum `Wait3`, dipisah hanya oleh `Append MSG_BUFFER` + `Update Buffer` (hitungan milidetik).

Perubahan: hapus node `Read STATS for HITL`; di `HITL Check` ganti
`$('Read STATS for HITL').all()` → `$('Read User STATS').all()`.
Rewire: `Update Buffer` → `HITL Check` langsung.

**Yang hilang secara semantik:** gate HITL tidak lagi melihat toggle `bot_mode` yang terjadi di jendela milidetik antara dua read itu. Gate yang benar-benar berarti adalah pemeriksaan ketiga di `Cek_user_status`, yang jalan **setelah** `Wait3` 60 detik — di situlah admin realistis punya waktu menekan tombol. Risiko: bisa diabaikan.

### R2 — `Read FAQ` + `Read PRODUK Data` + `Read LINKS Data` → 1 HTTP Request `values:batchGet`
**Hemat 2 read per GILIRAN** (pemenang saja).

Peta ketergantungan menunjukkan rantai `Read FAQ → Read PRODUK → Read LINKS → FAQ Retrieve` **murni untuk urutan eksekusi, bukan pass data** — tiap node Sheets menimpa input dengan hasilnya sendiri, dan `FAQ Retrieve` menarik ulang ketiganya lewat helper `grab(node) => $(node).all()`. Jadi ketiganya bisa dilebur tanpa mengganggu aliran.

Satu panggilan menggantikan tiga:
```
GET https://sheets.googleapis.com/v4/spreadsheets/1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o/values:batchGet
    ?ranges=FAQ!A:C&ranges=PRODUK!A:AB&ranges=LINKS!A:H
```

Auth: HTTP Request node → **Predefined Credential Type** → Google Service Account. Kredensial `Google Service Account - Persada` harus di-set **"Set up for use in HTTP Request node"** dan diberi scope `https://www.googleapis.com/auth/spreadsheets.readonly`.

⚠️ **Bentuk response beda.** `batchGet` mengembalikan `valueRanges[].values[][]` — array mentah, baris pertama = header. Node Sheets n8n mengembalikan objek-per-baris. Butuh 1 Code node (`Split Reference Data`) yang mengubah header row → objek, menghasilkan 3 array terpisah.

Konsumen yang harus diubah:
- `FAQ Retrieve` — `grab('Read FAQ')` / `grab('Read PRODUK Data')` / `grab('Read LINKS Data')` → baca dari node baru
- `Process All` — `$('Read LINKS Data').all()` dipanggil **2×** (`linkRows` dan `linkRows2`) → keduanya harus diubah

### R3 — Hapus `Read STATS` (yang telat), pakai ulang `Re-Read STATS Debounce`
**Hemat 1 read per GILIRAN** (pemenang saja).

`Read STATS` adalah satu-satunya dari 9 node read yang **tidak direferensikan `$('...')` oleh siapa pun** — dikonsumsi murni via `$input.all()` oleh `Process Counter & Merge Data`. Paling aman dihapus.

`Re-Read STATS Debounce` sudah difilter ke 1 baris (`No WA = resolved_key`) — persis baris yang dibutuhkan `Process Counter & Merge Data` untuk `Counter`, `Intensitas Chat`, `Pesan Pertama`, `Tanggal Chat Pertama`.

Perubahan: di `Process Counter & Merge Data` ganti `$input.all()` → `$('Re-Read STATS Debounce').all()`. Hapus node `Read STATS`, rewire `Extract & Prepare Data` → `Process Counter & Merge Data`.

**Aman secara timing?** Ya. Antara `Re-Read STATS Debounce` dan titik lama `Read STATS`, satu-satunya penulis ke baris itu adalah eksekusi ini sendiri (`Mark Buffer Consumed (Regular)`, yang hanya menyentuh `buffer_done_ts` — bukan `Counter`).

### R4 — Cache CONFIG di static data — **DITUNDA, jangan kerjakan sekarang**
Rasio kompleksitas/manfaat terburuk. Hemat 1 read/pesan, tapi butuh percabangan IF + jalur parse ganda, dan `$getWorkflowStaticData` di-persist saat eksekusi **berakhir** — eksekusi paralel bisa saling menimpa cache. Untuk read-cache dampaknya jinak (paling buruk: cache miss atau config basi-tapi-valid), tapi tetap menambah permukaan bug di jalur paling kritis.

Kerjakan R1–R3, ukur, baru putuskan.

---

## 3. Hasil yang bisa diharapkan

| Bubble/giliran | Sekarang | Setelah R1–R3 | Faktor |
|---|---|---|---|
| 1 | 9 read | **5** | 1,8× |
| 3 | 17 read | **11** | 1,55× |
| Plafon (1 bubble) | 6,6 giliran/mnt | **12 giliran/mnt** | 1,8× |

Kalau R4 ikut dikerjakan: 4 dan 8 read → ~2,1×. Lantai keras tetap 2 read/pesan.

---

## 4. Perbaikan correctness — kerjakan terlepas dari kinerja

Tiga bug ini tidak ada hubungannya dengan kuota, dan tetap valid setelah migrasi database nanti. Prioritaskan.

### 2.4 — Pesan menggantung di MSG_BUFFER saat HITL aktif
Pesan yang dihentikan gate HITL ke-2 (`HITL Check`) atau ke-3 (`Cek_user_status`) sudah masuk MSG_BUFFER, tapi tidak ada `Mark Buffer Consumed` yang jalan. Saat `bot_mode` kembali ON, pesan lama (≤30 menit, batas `MAX_AGE_MS` di `Cek_user_status`) ikut terkirim ke AI sebagai konteks — user bisa dapat jawaban atas pertanyaan yang sudah dijawab admin manual.

Perbaikan: sambungkan `HITL Check` dan cabang stop `Cek_user_status` ke node `Mark Buffer Consumed` (update `buffer_done_ts`).

### 2.5 — Lost update pada `Counter` / `Intensitas Chat`
`Read STATS` → `+1` → `Update to STATS` tanpa lock. Dua pesan bersamaan → keduanya baca N, keduanya tulis N+1. Satu increment hilang.

Google Sheets tidak punya transaksi, jadi tidak ada perbaikan yang benar-benar bersih. Opsi paling jujur: **terima ketidakakuratannya** dan dokumentasikan bahwa `Counter` adalah perkiraan, bukan hitungan eksak. Perbaikan sungguhan datang bersama migrasi database (`UPDATE ... SET counter = counter + 1` yang atomik). Jangan bangun locking di atas Sheets — kompleksitasnya tidak sepadan untuk kolom statistik.

### 2.6 — Cleanup MSG_BUFFER berhenti permanen di baris `ts` rusak
`Pick expired block (>2h)` menghapus blok kontigu dari baris 2 dan **`break` di baris pertama dengan `ts` tidak valid**. Satu baris rusak = seluruh blok kadaluarsa di belakangnya tidak pernah terhapus, selamanya. Buffer tumbuh tanpa batas, dan setiap `Read MSG_BUFFER` ikut membesar.

Perbaikan: jangan `break` pada `ts` invalid — perlakukan baris dengan `ts` tidak valid sebagai **kadaluarsa** (baris tanpa timestamp valid tidak mungkin masih relevan), atau lewati dan lanjutkan scan, lalu hapus dalam beberapa range terpisah. Tambah juga logging jumlah baris yang dilewati supaya kerusakan data terlihat, bukan diam-diam.

---

## 5. Urutan implementasi & risiko

| # | Perubahan | Risiko | Bisa deploy sendirian? |
|---|---|---|---|
| 1 | 2.6 cleanup fix | Rendah — workflow terpisah, jalan 03:00 | Ya |
| 2 | 2.4 buffer menggantung | Rendah — hanya menambah edge | Ya |
| 3 | R3 hapus `Read STATS` | Rendah — 0 referensi by-name | Ya |
| 4 | R1 gabung 2 read STATS | Sedang — ubah `HITL Check` + rewire | Ya |
| 5 | R2 batchGet | **Tinggi** — auth baru, bentuk data baru, 3 konsumen berubah | **Tidak** — butuh smoke test terpisah |

R2 adalah satu-satunya yang butuh verifikasi di luar file: **Predefined Credential Type untuk Google Service Account di HTTP Request node belum pernah terbukti jalan di instance n8n ini.** Sesi 2 menemukan nol dari 16 node httpRequest punya credential — semuanya kirim kredensial via body parameter. Uji di workflow kosong lebih dulu sebelum menyentuh Main.

---

## 6. Yang masih belum terjawab

**Baseline traffic.** Pertanyaan ini sudah dua kali diajukan dan belum terjawab, dan ia menentukan apakah Sesi 4 cukup atau sekadar menunda:

- Target ~3.000 pesan/hari (~2/menit rata-rata, puncak ~10–15/menit) → Sesi 4 **cukup**, migrasi database bisa ditunda.
- Target ~30.000 pesan/hari → Sesi 4 **tidak cukup**, dan mengerjakan R1/R3/R4 adalah usaha yang akan dibuang saat migrasi. Kerjakan hanya R2 + perbaikan correctness, lalu langsung ke Postgres.

Produksi masih `whitelist_enabled=True` dengan 3 nomor, jadi tidak ada data observasi untuk menebak ini.
