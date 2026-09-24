# Setup n8n — Metro Logistik Tracking (Fase A)

Panduan singkat untuk meng-import dan mengonfigurasi 3 workflow n8n backend
tracking. Semua komentar & dokumentasi dalam Bahasa Indonesia.

## Daftar Workflow

| File | Fungsi | Trigger |
|------|--------|---------|
| `2026-07-05-workflow-1-get-data.json` | Ambil data tracking per resi (bisa banyak) | Webhook **GET** `tracking-get` |
| `2026-07-05-workflow-2-update-data.json` | Update / tambah status resi (real-time) | Webhook **POST** `tracking-update` |
| `2026-07-05-workflow-3-housekeeping.json` | Arsip otomatis resi Delivered lama | Schedule (tiap 60 hari) |

---

## 1. Import Workflow ke n8n

1. Buka n8n → menu kiri atas **Workflows** → tombol **Import from File** (atau `...` → *Import from File*).
2. Pilih salah satu file `.json` di folder `n8n/`.
3. Ulangi untuk ketiga workflow.
4. Setelah import, tiap workflow masih **nonaktif**. Aktifkan setelah konfigurasi selesai (lihat langkah 4).

---

## 2. Setup Credential Google Sheets

Ketiga workflow memakai credential **Google Sheets OAuth2** yang sama.

1. Di n8n: **Credentials** → **New** → cari **Google Sheets OAuth2 API**.
2. Ikuti alur OAuth (butuh Google Cloud project dengan **Google Sheets API** aktif dan OAuth consent screen).
3. Beri nama, mis. `Google Sheets Metro Logistik`.
4. Pada tiap node Google Sheets di ketiga workflow, pilih credential ini.
   - Placeholder credential di file: `GANTI_DENGAN_CREDENTIAL_ID_GOOGLE_SHEETS`.
   - Cukup pilih ulang credential dari dropdown di editor n8n (ID akan terisi otomatis).

> Pastikan akun Google yang dipakai punya akses **edit** ke Spreadsheet Utama
> dan Spreadsheet Archive.

---

## 3. Ganti Placeholder Spreadsheet ID

Cari & ganti placeholder berikut pada node Google Sheets (bisa lewat UI n8n atau edit file sebelum import):

| Placeholder | Ganti dengan | Dipakai di |
|-------------|--------------|------------|
| `GANTI_DENGAN_SPREADSHEET_ID_UTAMA` | ID Spreadsheet Utama (sheet `Tracking`) | WF1, WF2, WF3 |
| `GANTI_DENGAN_SPREADSHEET_ID_ARCHIVE` | ID Spreadsheet Archive (sheet `Archive`) | WF3 |

**Cara ambil Spreadsheet ID:** dari URL Google Sheets
`https://docs.google.com/spreadsheets/d/<INI_ID_NYA>/edit` — bagian di antara `/d/` dan `/edit`.

### Struktur kolom yang harus ada

**Sheet `Tracking` (Spreadsheet Utama)** — baris 1 = header:

```
No_Resi | Pengirim | Penerima | Status_Terakhir | Riwayat_Posisi_JSON | Timestamp_Update
```

**Sheet `Archive` (Spreadsheet Archive)** — baris 1 = header (kolom sama + 1 tambahan):

```
No_Resi | Pengirim | Penerima | Status_Terakhir | Riwayat_Posisi_JSON | Timestamp_Update | Tanggal_Diarsipkan
```

Enum `Status_Terakhir` yang valid: `Manifest`, `On Process`, `Transit`,
`Out for Delivery`, `Delivered`, `Failed/Return`.

---

## 4. Ambil URL Webhook & Pasang ke `app/js/config.js`

1. Buka WF1 & WF2 → klik node Webhook → salin **Production URL**.
   - Format umum: `https://<domain-n8n-anda>/webhook/tracking-get`
   - dan: `https://<domain-n8n-anda>/webhook/tracking-update`
2. **Aktifkan** kedua workflow (toggle *Active* kanan atas) — URL production baru aktif setelah workflow di-*activate*.
3. Buka `app/js/config.js` dan isi konstanta:

```js
const CONFIG = {
  // URL WF1 (GET) — pencarian resi
  API_GET_URL:    "https://DOMAIN-N8N-ANDA/webhook/tracking-get",
  // URL WF2 (POST) — update status
  API_UPDATE_URL: "https://DOMAIN-N8N-ANDA/webhook/tracking-update"
};
```

> WF3 (housekeeping) tidak punya webhook — dijalankan otomatis oleh Schedule Trigger.

---

## 5. Cara Test Manual Tiap Workflow

Gunakan URL **Test** (tombol *Listen for test event* di editor, path `/webhook-test/...`)
atau URL **Production** setelah aktif.

### WF1 — Get Data (GET)

Satu resi:

```bash
curl "https://DOMAIN-N8N-ANDA/webhook/tracking-get?resi=MLI001"
```

Banyak resi (dipisah koma):

```bash
curl "https://DOMAIN-N8N-ANDA/webhook/tracking-get?resi=MLI001,mli002,%20MLI003"
```

Respons yang diharapkan (per resi): objek dengan `no_resi`, `pengirim`,
`penerima`, `status_terakhir`, `timestamp_update`, `riwayat[]`.
Resi tak ada → `{ "no_resi": "...", "found": false }`.
JSON riwayat korup → `riwayat: []` + `riwayat_error: true`.

### WF2 — Update Data (POST)

Update valid:

```bash
curl -X POST "https://DOMAIN-N8N-ANDA/webhook/tracking-update" \
  -H "Content-Type: application/json" \
  -d '{"no_resi":"MLI001","nama_admin":"Budi","status":"Transit","lokasi":"Gudang Bandung"}'
```

Respons sukses: `{ "success": true, "no_resi": "MLI001", "total_riwayat": 3 }`.

Update invalid (status di luar enum / field kosong):

```bash
curl -X POST "https://DOMAIN-N8N-ANDA/webhook/tracking-update" \
  -H "Content-Type: application/json" \
  -d '{"no_resi":"MLI001","nama_admin":"Budi","status":"Ngawur","lokasi":"   "}'
```

Respons error (HTTP 400): `{ "success": false, "error": "..." }`.

Uji resi baru: kirim `no_resi` yang belum ada → baris baru otomatis ditambahkan
dengan 1 entri riwayat.

### WF3 — Housekeeping (Schedule)

1. Buka workflow → klik **Execute Workflow** untuk menjalankan manual (tanpa menunggu 60 hari).
2. Pastikan ada baris uji di sheet Utama dengan:
   - `Status_Terakhir = Delivered`, dan
   - entri Delivered terakhir di riwayat (atau `Timestamp_Update`) **lebih tua dari 30 hari**.
3. Hasil yang diharapkan:
   - Baris tersebut ter-**append** ke sheet `Archive` (dengan `Tanggal_Diarsipkan` terisi).
   - Baris tersebut **terhapus** dari sheet `Tracking`.
   - Baris Delivered yang baru (< 30 hari), status non-Delivered, atau JSON korup **tidak** tersentuh.
4. Bila tidak ada baris memenuhi syarat, workflow selesai tanpa aksi.

> **Urutan aman WF3:** append ke Archive dijalankan lebih dulu; penghapusan
> dari sheet Utama diproses dari `row_number` **terbesar ke terkecil** agar
> index baris tidak bergeser saat menghapus.

---

## Catatan CORS

WF1 & WF2 mengembalikan header `Access-Control-Allow-Origin: *` melalui node
*Respond to Webhook*, sehingga bisa dipanggil langsung dari PWA di origin mana pun.
Untuk produksi, disarankan mengganti `*` dengan domain PWA yang spesifik.
