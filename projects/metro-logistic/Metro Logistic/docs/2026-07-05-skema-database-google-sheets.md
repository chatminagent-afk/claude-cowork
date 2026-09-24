# Skema Database Google Sheets — Metro Logistik Indonesia

**Dokumen:** Skema Database (Google Sheets sebagai backend data)
**Proyek:** Web Dashboard & Tracking PWA — Metro Logistik Indonesia (metrologistikindonesia.com)
**Dibuat oleh:** Software Architect & UI/UX Designer (Claude)
**Tanggal:** 2026-07-05
**Audiens:** Tim n8n Workflow, Programmer implementasi (Opus), Project Manager

---

## 1. Gambaran Umum

Google Sheets digunakan sebagai **database utama** (bukan RDBMS/NoSQL kustom) karena kesederhanaan operasional tim logistik & integrasi native dengan n8n. Ada **dua spreadsheet terpisah**:

1. **Spreadsheet Utama** — sheet `Tracking`, menyimpan seluruh resi yang **aktif/belum lewat masa retensi**.
2. **Spreadsheet Archive** — sheet `Archive`, menyimpan resi yang sudah selesai (Delivered) dan melewati ambang waktu tertentu, untuk menjaga Spreadsheet Utama tetap ringan & cepat diakses n8n/API.

---

## 2. Spreadsheet Utama — Sheet `Tracking`

### 2.1 Struktur Kolom (persis, urutan wajib dipatuhi)

| Kolom | Tipe Data | Wajib | Deskripsi |
|---|---|---|---|
| `No_Resi` | Text (string) | Ya, **unik** | Nomor resi pengiriman — primary key logis |
| `Pengirim` | Text (string) | Opsional | Nama & info pengirim (bisa kosong saat resi baru dibuat via update pertama) |
| `Penerima` | Text (string) | Opsional | Nama & info penerima (bisa kosong saat resi baru dibuat via update pertama) |
| `Status_Terakhir` | Text (enum, lihat §4) | Ya | Harus selalu sama dengan `status` pada elemen **terakhir** di `Riwayat_Posisi_JSON` |
| `Riwayat_Posisi_JSON` | Text (string berisi JSON array) | Ya | Riwayat perjalanan lengkap, append-only, terurut kronologis lama→baru |
| `Timestamp_Update` | Text (ISO 8601, Asia/Jakarta) | Ya | Waktu update terakhir — harus sama dengan `waktu` pada elemen terakhir `Riwayat_Posisi_JSON` |

### 2.2 Struktur `Riwayat_Posisi_JSON`

String JSON berisi **array**, setiap elemen merepresentasikan satu titik riwayat perjalanan:

```json
[
  {
    "waktu": "2026-07-01T09:00:00+07:00",
    "status": "Manifest",
    "lokasi": "Gudang Jakarta Pusat",
    "admin": "Andi Wijaya"
  },
  {
    "waktu": "2026-07-02T11:15:00+07:00",
    "status": "On Process",
    "lokasi": "Sortir di Gudang Jakarta Pusat",
    "admin": "Andi Wijaya"
  }
]
```

Field per elemen:

| Field | Tipe | Format | Keterangan |
|---|---|---|---|
| `waktu` | string | ISO 8601 dengan offset zona waktu Asia/Jakarta, contoh: `2026-07-05T14:30:00+07:00` | Selalu simpan offset `+07:00` eksplisit agar tidak ambigu meski server n8n berjalan di UTC |
| `status` | string enum | Salah satu dari 6 nilai enum resmi (§4) | Harus identik (case-sensitive) dengan opsi dropdown admin |
| `lokasi` | string | Bebas teks | Catatan posisi/lokasi barang saat titik ini dicatat |
| `admin` | string | Bebas teks | Nama petugas yang menginput update ini |

**Aturan append:**
- Elemen baru **selalu ditambahkan di akhir array** (`array.push(...)`), TIDAK PERNAH disisipkan di awal atau di tengah.
- n8n (WF2) bertanggung jawab: baca `Riwayat_Posisi_JSON` existing → parse JSON → `push` elemen baru → `stringify` kembali → tulis ke sel.
- **Frontend** (bukan backend) yang membalik urutan (`.reverse()`) saat menampilkan timeline "terbaru di atas" — backend tetap sederhana, hanya append.

### 2.3 Contoh Lengkap 1 Baris Data (Manifest → Delivered, 5 riwayat)

Contoh nilai kolom untuk satu resi lengkap perjalanannya:

| Kolom | Nilai |
|---|---|
| `No_Resi` | `JX12345678` |
| `Pengirim` | `Toko Sinar Jaya, Jakarta` |
| `Penerima` | `Budi Santoso, Surabaya` |
| `Status_Terakhir` | `Delivered` |
| `Timestamp_Update` | `2026-07-05T14:30:00+07:00` |

Isi lengkap `Riwayat_Posisi_JSON` (string JSON, ditulis dalam satu sel Google Sheets):

```json
[
  {
    "waktu": "2026-07-01T09:00:00+07:00",
    "status": "Manifest",
    "lokasi": "Gudang Jakarta Pusat",
    "admin": "Andi Wijaya"
  },
  {
    "waktu": "2026-07-02T11:15:00+07:00",
    "status": "On Process",
    "lokasi": "Sortir & pengemasan di Gudang Jakarta Pusat",
    "admin": "Andi Wijaya"
  },
  {
    "waktu": "2026-07-03T20:00:00+07:00",
    "status": "Transit",
    "lokasi": "Hub Transit Semarang",
    "admin": "Siti Rahma"
  },
  {
    "waktu": "2026-07-05T09:00:00+07:00",
    "status": "Out for Delivery",
    "lokasi": "Gudang Transit Surabaya, dalam perjalanan ke alamat penerima",
    "admin": "Rudi Hartono"
  },
  {
    "waktu": "2026-07-05T14:30:00+07:00",
    "status": "Delivered",
    "lokasi": "Diterima langsung oleh penerima di alamat, Surabaya",
    "admin": "Rudi Hartono"
  }
]
```

Ketika frontend menampilkan (setelah `.reverse()`), urutan tampil menjadi Delivered → Out for Delivery → Transit → On Process → Manifest (terbaru di atas), sesuai pola timeline Shopee/JNE.

### 2.4 Representasi Baris di Google Sheets (ilustrasi tabel)

```
| No_Resi     | Pengirim          | Penerima        | Status_Terakhir | Riwayat_Posisi_JSON                  | Timestamp_Update            |
|-------------|-------------------|-----------------|------------------|----------------------------------------|------------------------------|
| JX12345678  | Toko Sinar Jaya,  | Budi Santoso,   | Delivered        | [{"waktu":"2026-07-01T09:00:00+07:00", | 2026-07-05T14:30:00+07:00    |
|             | Jakarta           | Surabaya        |                  | "status":"Manifest", ... }, ... ]      |                              |
```

(Sel `Riwayat_Posisi_JSON` berisi satu string JSON panjang tanpa line break di dalam sel — Google Sheets menyimpannya sebagai text biasa.)

---

## 3. Aturan Konsistensi Data

Aturan ini **wajib** diterapkan oleh workflow n8n (WF2) setiap kali menulis ke sheet `Tracking`, agar data selalu konsisten dan dapat dipercaya frontend:

1. **`No_Resi` unik** — sebelum insert baris baru, WF2 wajib melakukan pencarian (lookup) apakah `No_Resi` sudah ada. Tidak boleh ada dua baris dengan `No_Resi` sama.
2. **`Timestamp_Update` = waktu update terakhir** — setiap kali ada update baru (baik resi baru maupun existing), kolom ini di-overwrite dengan `waktu` dari elemen riwayat yang baru saja ditambahkan (bukan waktu proses n8n, tapi waktu logis kejadian — dalam praktik keduanya sama karena dicatat real-time).
3. **`Status_Terakhir` harus sinkron dengan elemen terakhir array** — setelah `push` elemen baru ke `Riwayat_Posisi_JSON`, WF2 wajib meng-update `Status_Terakhir` dengan nilai `status` dari elemen yang baru saja di-push. Kedua kolom ini tidak boleh pernah berbeda (redundansi kolom `Status_Terakhir` sengaja dipertahankan untuk mempercepat filter/pencarian tanpa perlu parse JSON setiap saat).
4. **Penanganan resi baru:**
   - Baris baru **dibuat otomatis saat update pertama** oleh admin lapangan (bukan proses terpisah "buat resi dulu").
   - Status update pertama **wajib** `Manifest` secara konvensi operasional (meskipun secara teknis dropdown admin mengizinkan status apa pun — proses bisnis mengasumsikan entri pertama sebuah resi adalah pendaftaran/manifest). Jika tim operasional butuh validasi ketat "update pertama harus Manifest", ini dapat ditambahkan sebagai validasi di WF2 (opsional, catat sebagai keputusan bisnis yang perlu dikonfirmasi PM).
   - Kolom `Pengirim` dan `Penerima` **boleh dikosongkan (opsional)** saat pembuatan baris baru, karena form admin lapangan (lihat dokumen wireframe) tidak memiliki field untuk itu — field ini diisi lewat proses lain (mis. input manual oleh CS/back office, atau integrasi order management di fase mendatang). Nilai default: string kosong `""`, bukan `null`, agar konsisten sebagai tipe text di Sheets.
   - `Riwayat_Posisi_JSON` untuk resi baru diinisialisasi sebagai array berisi **satu elemen** (entri update pertama).
5. **Validasi sebelum tulis (server-side, WF2):** meskipun frontend sudah validasi client-side, n8n **wajib** validasi ulang: `no_resi` tidak kosong, `nama_admin` tidak kosong/bukan hanya spasi, `status` termasuk dalam daftar enum resmi (§4), `lokasi` tidak kosong. Tidak boleh langsung dianggap valid dari kiriman frontend.
6. **Tidak ada penghapusan riwayat** — array `Riwayat_Posisi_JSON` bersifat append-only selamanya (kecuali proses arsip, yang memindahkan seluruh baris apa adanya ke spreadsheet Archive, bukan menghapus sebagian riwayat).

---

## 4. Daftar Enum Status (Resmi)

Nilai berikut **harus identik persis** (termasuk kapitalisasi & spasi) antara: dropdown Status di halaman admin, field `status` di `Riwayat_Posisi_JSON`, kolom `Status_Terakhir`, dan mapping warna/ikon di dokumen UI/UX.

| # | Nilai Enum (persis) | Urutan Alur Normal |
|---|---|---|
| 1 | `Manifest` | Tahap awal — resi terdaftar |
| 2 | `On Process` | Diproses di gudang asal |
| 3 | `Transit` | Dalam perjalanan antar hub/kota |
| 4 | `Out for Delivery` | Sedang diantar ke alamat penerima |
| 5 | `Delivered` | Diterima penerima (status akhir sukses) |
| 6 | `Failed/Return` | Gagal antar / dikembalikan (status akhir tidak sukses) |

Catatan: `Delivered` dan `Failed/Return` dianggap **status akhir (terminal)** — memicu kelayakan arsip untuk `Delivered` (lihat §5). `Failed/Return` tidak otomatis diarsipkan pada fase ini (kriteria arsip hanya berdasarkan `Delivered`, sesuai keputusan PM); dapat diperluas di iterasi berikutnya jika dibutuhkan.

---

## 5. Spreadsheet Archive — Sheet `Archive`

### 5.1 Tujuan

Menjaga Spreadsheet Utama (`Tracking`) tetap berukuran kecil dan cepat diakses oleh n8n & Google Sheets API, dengan memindahkan resi yang sudah lama selesai ke penyimpanan terpisah.

### 5.2 Struktur Kolom

Kolom sama persis dengan sheet `Tracking`, **ditambah satu kolom baru**:

| Kolom | Tipe Data | Deskripsi |
|---|---|---|
| `No_Resi` | Text | Sama seperti sheet Tracking |
| `Pengirim` | Text | Sama seperti sheet Tracking |
| `Penerima` | Text | Sama seperti sheet Tracking |
| `Status_Terakhir` | Text | Sama seperti sheet Tracking (akan selalu `Delivered` berdasar kriteria arsip di bawah) |
| `Riwayat_Posisi_JSON` | Text (JSON) | Sama persis, dipindahkan apa adanya (tidak diringkas/dipotong) |
| `Timestamp_Update` | Text (ISO 8601) | Sama seperti sheet Tracking |
| `Tanggal_Diarsipkan` | Text (ISO 8601, Asia/Jakarta) | **Kolom tambahan** — waktu saat proses arsip memindahkan baris ini |

### 5.3 Kriteria Arsip

Sebuah baris di sheet `Tracking` dipindahkan ke `Archive` **jika dan hanya jika kedua syarat berikut terpenuhi**:

1. `Status_Terakhir` = `Delivered` (pengiriman sudah selesai/sukses).
2. Selisih antara waktu sekarang dan `Timestamp_Update` (yang mencerminkan waktu status Delivered dicatat) **lebih dari 30 hari**.

Pseudo-kondisi:
```
JIKA Status_Terakhir == "Delivered"
  DAN (waktu_sekarang - Timestamp_Update) > 30 hari
MAKA pindahkan baris ke sheet Archive, hapus dari sheet Tracking
```

### 5.4 Mekanisme Proses Arsip (rekomendasi implementasi n8n)

- Dijalankan sebagai **workflow n8n terjadwal (Cron/Schedule Trigger)**, disarankan berjalan **harian** (mis. setiap jam 02:00 WIB, di luar jam sibuk).
- Langkah proses:
  1. Baca seluruh baris di sheet `Tracking`.
  2. Filter baris yang memenuhi kriteria arsip (§5.3).
  3. Untuk setiap baris yang memenuhi kriteria: tulis (append) baris tersebut ke sheet `Archive` dengan seluruh kolom sama + `Tanggal_Diarsipkan` = timestamp proses berjalan (ISO 8601, Asia/Jakarta).
  4. Hapus baris yang sudah diarsipkan dari sheet `Tracking`.
- Proses ini **tidak mengubah isi `Riwayat_Posisi_JSON`** — riwayat lengkap tetap utuh dipindahkan, tidak diringkas.
- Resi yang sudah diarsipkan **tetap dapat dilacak** jika suatu saat dibutuhkan (mis. keluhan pelanggan lama) — cakupan ini adalah peningkatan lanjutan: WF1 (GET tracking) pada fase awal hanya membaca sheet `Tracking`; jika PM memutuskan publik perlu bisa melacak resi lama yang sudah diarsip, WF1 perlu ditambah langkah fallback membaca sheet `Archive` saat resi tidak ditemukan di `Tracking`. Keputusan ini dicatat sebagai **catatan terbuka untuk PM**, belum termasuk dalam cakupan wajib fase ini.

---

## 6. Ringkasan Keputusan Skema Data

1. Riwayat perjalanan disimpan sebagai **satu kolom JSON string** (bukan sheet/baris terpisah per event) — memudahkan pembacaan satu resi dalam satu kali baca sel, cocok dengan pola akses n8n (baca-parse-modifikasi-tulis) dan menghindari kompleksitas join antar-sheet.
2. Kolom `Status_Terakhir` sengaja didenormalisasi (duplikat dari elemen terakhir array) untuk mempercepat filter status di frontend/n8n tanpa perlu parse JSON di setiap query filter.
3. Zona waktu **selalu eksplisit** (`+07:00`, Asia/Jakarta) di setiap timestamp untuk menghindari ambiguitas, terutama karena n8n sering berjalan di server dengan timezone UTC.
4. Resi baru dibuat **implisit** saat update pertama oleh admin — tidak ada proses "registrasi resi" terpisah, menyederhanakan alur kerja lapangan (satu form, satu aksi).
5. Pemisahan Spreadsheet Utama vs Archive menjaga performa akses data aktif tetap cepat, dengan kriteria arsip yang jelas dan otomatis (Delivered + lebih dari 30 hari).
6. Enum status dijaga identik lintas seluruh lapisan (dropdown admin, JSON riwayat, kolom status, mapping warna UI) untuk mencegah bug akibat mismatch string.

---

**Daftar File Referensi Terkait:**
- `docs/2026-07-05-arsitektur-frontend-pwa.md` — kontrak API WF1/WF2 yang mengonsumsi skema ini
- `docs/2026-07-05-wireframe-uiux.md` — mapping visual status & dropdown admin
