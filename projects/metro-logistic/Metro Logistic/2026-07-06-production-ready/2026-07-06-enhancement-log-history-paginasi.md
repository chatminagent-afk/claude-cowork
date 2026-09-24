# Enhancement — Log_History, Snapshot Tracking, Re-inquiry Filter & Paginasi

**Tanggal:** 2026-07-06
**Ringkasan:** empat perubahan atas versi production-ready, plus 1 tambahan (paginasi). File lama TIDAK dihapus — workflow n8n baru dibuat sebagai versi `-v2`.

Yang diminta:

1. Setiap update admin kini ditulis sebagai **baris terpisah dengan kolom-kolom sendiri** (bukan JSON gabungan). Sheet **Tracking** kini hanya berisi **latest update per resi**.
2. Sheet baru **`Log_History`** — setiap update yang di-submit menambah satu baris, sehingga admin bisa menelusuri ke belakang.
3. App publik: setiap klik **"Terapkan Filter"** / **"Lacak"** kini **selalu inquiry ulang ke Google Sheet** (tidak lagi memakai data lama di memori).
4. Penyesuaian n8n, app, dan Google Sheet — dijelaskan di bawah.
5. **(Tambahan)** Paginasi hasil: model **"Halaman 1 dari 20"**, maksimum **50 resi per halaman**.

---

## ⚠️ BAGIAN 1 — YANG HARUS ANDA UBAH DI GOOGLE SHEETS (WAJIB)

Arsitektur data berubah. Lakukan ini **sebelum** mengaktifkan workflow v2.

### 1a. Sheet `Tracking` (di Spreadsheet Utama) — ganti header

Struktur **lama** (baris 1):

```
No_Resi | Pengirim | Penerima | Status_Terakhir | Riwayat_Posisi_JSON | Timestamp_Update
```

Struktur **BARU** (baris 1) — hapus kolom JSON + hapus Pengirim/Penerima, tambah 2 kolom terpisah:

```
No_Resi | Status_Terakhir | Lokasi_Terakhir | Nama_Admin | Timestamp_Update
```

Perubahan: **hapus** `Riwayat_Posisi_JSON`; **hapus** `Pengirim` & `Penerima` (form admin tidak pernah mengisinya — kolom mati); **tambah** `Lokasi_Terakhir` dan `Nama_Admin`. Sekarang Tracking = potret terbaru satu baris per resi (riwayat pindah ke `Log_History`).

### 1b. Sheet BARU `Log_History` (di Spreadsheet Utama) — buat tab baru

Buat tab baru, beri nama persis `Log_History`, isi baris 1 (header) persis:

```
Timestamp_Update | No_Resi | Status | Lokasi | Nama_Admin | Client_ID
```

Ini **ledger append-only**: setiap submit admin = satu baris baru di sini. Sumber timeline untuk app publik, dan tempat penelusuran ke belakang. `Client_ID` dipakai untuk anti-duplikat (idempotensi).

### 1c. Sheet `Archive` (di Spreadsheet Arsip) — ganti header

Struktur **BARU** (baris 1) — samakan dengan Tracking baru + kolom arsip:

```
No_Resi | Status_Terakhir | Lokasi_Terakhir | Nama_Admin | Timestamp_Update | Tanggal_Diarsipkan
```

Perubahan: **hapus** `Riwayat_Posisi_JSON`, `Pengirim`, `Penerima`; **tambah** `Lokasi_Terakhir` dan `Nama_Admin` (sebelum `Tanggal_Diarsipkan`).

> Nama sheet dan header **case-sensitive** dan harus persis — n8n mencocokkan berdasarkan nama kolom.

### 1d. Data lama yang sudah ada (migrasi) — perhatikan

Baris yang sudah ada di Tracking lama menyimpan riwayat di kolom `Riwayat_Posisi_JSON`. Setelah pindah skema, **timeline resi lama tidak akan tampil** karena `Log_History` masih kosong. Dua pilihan:

- **Mulai bersih (paling mudah):** biarkan; resi baru mulai mencatat riwayat lengkap sejak update pertama pasca-migrasi. Snapshot terakhir tetap benar bila Anda isi manual kolom `Lokasi_Terakhir`/`Nama_Admin` untuk resi aktif.
- **Backfill (opsional):** pecah setiap entri di `Riwayat_Posisi_JSON` lama menjadi baris-baris di `Log_History`. Saya bisa buatkan script sekali-jalan (Google Apps Script atau workflow n8n) untuk ini bila Anda mau — beri tahu saja.

---

## BAGIAN 2 — PERUBAHAN n8n

Tiga workflow baru (folder `n8n/`), aman diimpor berdampingan:

- `2026-07-06-workflow-1-get-data-v2.json`
- `2026-07-06-workflow-2-update-data-v2.json`
- `2026-07-06-workflow-3-housekeeping-v2.json`

Langkah:

1. **Nonaktifkan / hapus** ketiga workflow versi lama dulu. Path webhook sama (`tracking-get`, `tracking-update`) — bila dua workflow aktif dengan path sama, n8n bentrok.
2. **Import** ketiga file v2 (Workflows → Import from File).
3. Isi ulang **Credential** + **Document ID** di setiap node Google Sheets:
   - **WF1 v2** (3 node): `Baca Sheet Tracking` → ID Utama · `Baca Sheet Archive` → ID Arsip · `Baca Sheet Log_History` → ID Utama.
   - **WF2 v2** (5 node): `Baca Sheet Log_History`, `Baca Sheet Tracking`, `Append ke Log_History`, `Update Snapshot Tracking`, `Append Snapshot Tracking` → semua ID Utama.
   - **WF3 v2** (3 node): `Baca Snapshot Tracking` → ID Utama · `Append ke Archive` → ID Arsip · `Hapus Baris dari Tracking` → ID Utama.
4. **Aktifkan** ketiganya.

### Apa yang berubah di logika n8n

- **WF2 (update):** validasi → baca `Log_History` (cek duplikat `Client_ID`) → baca `Tracking` → satu node Code menyiapkan (a) baris baru untuk `Log_History` dan (b) snapshot untuk `Tracking`. Selalu **append** ke `Log_History`; **update** baris `Tracking` bila resi sudah ada, atau **append** bila resi baru. `total_riwayat` = jumlah baris `Log_History` untuk resi tersebut. Retry duplikat (Client_ID sama) → balas sukses tanpa menulis apa pun.
- **WF1 (get):** baca `Tracking` + `Archive` + `Log_History`. Timeline (`riwayat`) tiap resi **dirakit dari `Log_History`** (diurut menaik). Kontrak respons ke frontend **tidak berubah** (`{ results: [{ ..., riwayat: [...] }] }`), jadi app publik tidak perlu perubahan struktur. Mode tanpa param resi (daftar 30 hari) tetap ada.
- **WF3 (housekeeping):** arsip snapshot `Delivered` yang `Timestamp_Update`-nya > 30 hari (tak perlu parse JSON lagi). `Log_History` **tidak disentuh** — sengaja, agar penelusuran ke belakang tetap utuh meski resi sudah diarsipkan.

---

## BAGIAN 3 — PERUBAHAN APP

Hanya **app publik** yang berubah. **App admin tidak berubah** (kontrak update sama).

- `app-publik/index.html` — tambah elemen navigasi paginasi (`<nav id="paginasi">`).
- `app-publik/js/tracking.js`:
  - **[#3]** Tombol **"Terapkan Filter"** kini **selalu fetch ulang** dari n8n: bila ada resi di kotak input → lacak ulang resi tersebut; bila kosong → muat ulang daftar 30 hari terakhir. Tombol **"Lacak"** memang sudah selalu fetch segar.
  - **[#5]** Paginasi: hasil dipotong maks **50 resi/halaman**, dengan bar **"Halaman X dari Y"** + tombol Sebelumnya/Berikutnya + info "Menampilkan A–B dari N resi". Muncul otomatis hanya bila hasil > 50.
- `app-publik/sw.js` — `CACHE_VERSION` dinaikkan ke `v2.1.0-publik` (agar HP menarik versi baru; muat ulang 2× setelah deploy).
- `app-publik/js/config.js` — field `pengirim`/`penerima` dibuang dari data dummy (form admin tak pernah mengisinya). Data dummy dinaikkan menjadi **60 resi** dengan status akhir dirotasi merata (10 Manifest, 10 On Process, 10 Transit, 10 Out for Delivery, 10 Delivered, 10 Failed/Return) — untuk menguji paginasi & perbedaan status. URL webhook get **tidak berubah**. `TEST_DUMMY` tetap `false` (produksi).

### Uji tampilan tanpa server (mode dummy)

Ubah sementara `TEST_DUMMY: true` di `config.js`, lalu buka app publik dan klik **"Terapkan Filter"** tanpa mengetik resi. Semua 60 resi dummy dimuat → bar **"Halaman 1 dari 2"** muncul (50 di halaman 1, 10 di halaman 2), dan tiap kartu menampilkan badge status berbeda (Manifest/On Process/Transit/Out for Delivery/Delivered/Failed/Return). Setiap timeline realistis meniru JNE/Shopee: status akhir selalu melewati semua tahap sebelumnya (mis. *Delivered* = Manifest → On Process → Transit multi-hop lewat hub nyata seperti "Jakarta - Cakung DC" → Out for Delivery → Delivered), lengkap dengan keterangan gaya kurir. Resi dummy mudah ditebak: `JX10000000`, `JX10000137`, `JX10000274`, … (kelipatan 137). Kembalikan ke `false` sebelum deploy produksi.

---

## BAGIAN 4 — CATATAN WEBHOOK ANDA

Anda mengirim:

- Admin (update): `https://n8n.srv1270416.hstgr.cloud/webhook/tracking-update` — ✅ benar (Production URL). Sudah cocok dengan `app-admin/js/config.js`.
- Publik (get): `https://n8n.srv1270416.hstgr.cloud/webhook-test/tracking-get` — ⚠️ ini **Test URL** (`/webhook-test/`). Test URL hanya hidup saat Anda menekan **"Listen for test event"** di editor n8n, dan hanya untuk 1 kali panggil. Untuk produksi gunakan **Production URL**: `https://n8n.srv1270416.hstgr.cloud/webhook/tracking-get` — dan itulah yang sudah terpasang di `app-publik/js/config.js`. Jadi tidak perlu diubah; cukup pastikan WF1 v2 dalam keadaan **Active**.

---

## Uji cepat setelah migrasi

```bash
# 1) Submit update (buat baris di Log_History + snapshot Tracking)
curl -X POST https://n8n.srv1270416.hstgr.cloud/webhook/tracking-update \
  -H "Content-Type: application/json" \
  -d '{"no_resi":"TEST001","nama_admin":"QA","status":"Manifest","lokasi":"Gudang Uji"}'
# → {"success":true,"no_resi":"TEST001","total_riwayat":1,...}

# 2) Submit update kedua resi sama (status Transit)
curl -X POST https://n8n.srv1270416.hstgr.cloud/webhook/tracking-update \
  -H "Content-Type: application/json" \
  -d '{"no_resi":"TEST001","nama_admin":"QA","status":"Transit","lokasi":"Hub Semarang"}'
# → total_riwayat:2. Cek: Log_History bertambah 2 baris; Tracking hanya 1 baris (snapshot = Transit).

# 3) Get resi (timeline dari Log_History)
curl "https://n8n.srv1270416.hstgr.cloud/webhook/tracking-get?resi=TEST001"
# → riwayat berisi 2 entri (Manifest lalu Transit)
```

Checklist app publik: buka halaman → klik "Terapkan Filter" tanpa mengetik apa pun → harus memuat ulang daftar dari server (bukan diam). Bila resi > 50 → bar "Halaman 1 dari N" muncul; Sebelumnya/Berikutnya berpindah halaman.
