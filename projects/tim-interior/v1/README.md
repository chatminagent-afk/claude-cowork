# Sistem Otomasi Komplain — Interior Consultant

Sistem pencatatan komplain dan catatan proyek dengan web form profesional, penyimpanan Google Sheets, upload foto ke Google Drive, dan rekapan harian otomatis ke WhatsApp.

---

## 📦 Daftar File

| File | Fungsi |
|---|---|
| `index.html` | Web form input komplain (dark elegant design) |
| `n8n_1_complaint_submit.json` | Workflow: terima form → upload Drive → simpan Sheet |
| `n8n_2_daily_recap.json` | Workflow: rekapan harian → kirim WA setiap 08.00 |
| `google_sheet_template.csv` | Template header kolom Google Sheet |

---

## ⚙️ Langkah Setup

### Step 1 — Google Sheet

1. Buat Spreadsheet baru di [sheets.google.com](https://sheets.google.com)
2. Rename tab pertama menjadi **`Database`**
3. Row 1 (header) — buat kolom persis seperti ini (urutan penting!):

   ```
   ID | Tanggal_Komplain | Nama_Project | Komplain | Pengaju | Prioritas | Kategori | Attachment_URLs | Status | Tanggal_Submit
   ```

4. Salin **Spreadsheet ID** dari URL:
   `docs.google.com/spreadsheets/d/`**`SPREADSHEET_ID`**`/edit`

> 💡 Atau import `google_sheet_template.csv` untuk langsung dapat contoh data.

---

### Step 2 — Google Drive Folder untuk Lampiran

1. Buka [drive.google.com](https://drive.google.com) → buat folder baru, misal **"Lampiran Komplain"**
2. Klik kanan folder → **Share** → atur akses sesuai kebutuhan
3. Klik kanan folder → **Get link** → salin **Folder ID** dari URL:
   `drive.google.com/drive/folders/`**`FOLDER_ID`**

---

### Step 3 — Setup Credentials di n8n

**Google Sheets OAuth2:**
1. n8n → Settings → Credentials → + Add → pilih **Google Sheets OAuth2 API**
2. Ikuti OAuth → simpan, catat ID credential

**Google Drive OAuth2:**
1. n8n → Settings → Credentials → + Add → pilih **Google Drive OAuth2 API**
2. Ikuti OAuth dengan akun yang sama → simpan, catat ID credential

---

### Step 4 — Import & Konfigurasi Workflow 1 (Form Submit)

1. n8n → **New Workflow → Import from File** → upload `n8n_1_complaint_submit.json`
2. Edit **node "Simpan ke Google Sheet"**:
   - `documentId.value` → isi Spreadsheet ID
   - Credential → pilih Google Sheets
3. Edit **node "Upload File ke Drive"**:
   - `folderId.value` → isi Folder ID dari Step 2
   - Credential → pilih Google Drive
4. Edit **node "Set Drive Permission (Public)"**:
   - Credential → pilih Google Drive (sama)
5. **Save** → toggle **Active = ON**
6. Salin **Webhook URL** dari node pertama
   Format: `https://[n8n-url]/webhook/salero-complaint`

---

### Step 5 — Setup Form HTML

1. Buka `index.html` dengan text editor
2. Cari baris (sekitar baris 5 di dalam `<script>`):
   ```javascript
   const WEBHOOK_URL = 'https://YOUR_N8N_URL/webhook/salero-complaint';
   ```
3. Ganti dengan URL webhook dari Step 4
4. Host `index.html`:
   - **Netlify Drop** (gratis, drag & drop): [app.netlify.com/drop](https://app.netlify.com/drop)
   - Upload ke hosting/server yang sudah ada
   - Testing lokal: buka langsung di browser (CORS harus diizinkan di n8n)

---

### Step 6 — Import & Konfigurasi Workflow 2 (Daily Recap)

1. Import `n8n_2_daily_recap.json`
2. Edit **node "Baca Semua Data Sheet"** & **"Update Status: resolved → reported"**:
   - `documentId.value` → isi Spreadsheet ID
   - Credential → pilih Google Sheets
3. Edit **node "Kirim Rekapan ke WhatsApp"**:
   - `user_code` → kode user kirimi.id
   - `secret` → secret key kirimi.id
   - `device_id` → device ID kirimi.id
   - `phone` → nomor WA tujuan format `62812XXXXXXXX`
     (untuk grup: gunakan group ID dari kirimi.id)
4. **Save** → **Active = ON**

---

## 🔄 Cara Kerja Sistem

```
User isi form web
       ↓
Webhook n8n terima JSON (termasuk base64 foto/video)
       ↓
Generate ID unik: CMP-YYYYMMDDHHMMSS
       ↓
Ada lampiran?
 ├─ YA  → Upload setiap file ke Google Drive
 │         → Set permission "public reader"
 │         → Kumpulkan link Drive
 └─ TIDAK → Skip upload
       ↓
Merge kedua jalur
       ↓
Simpan ke Google Sheet (status = "pending")
       ↓
Kirim response sukses ke form (tampilkan ID)

━━━━━━━━━━━ Setiap hari jam 08.00 WIB ━━━━━━━━━━━

Schedule Trigger
       ↓
Baca Sheet (filter: pending + resolved)
       ↓
Format pesan per proyek
       ↓
Ada data aktif?
 ├─ YA  → Kirim WA → Update resolved → reported
 └─ TIDAK → Skip
```

---

## 📊 Alur Status Komplain

```
[BARU MASUK]        → pending
[TIM SELESAIKAN]    → ubah manual di Sheet → resolved
[WA DIKIRIM]        → sistem ubah otomatis → reported (tidak dikirim lagi besok)
```

**Cara update status:** Buka Google Sheet → kolom `Status` → ganti `pending` → `resolved`.
Besok pagi sistem kirim WA dengan tanda ✅ lalu status otomatis berubah ke `reported`.

---

## 🗂️ Fitur Tambah Proyek di Form

Form menyimpan daftar proyek di **localStorage** browser. Cara menambah proyek:
1. Buka form → dropdown "Nama Proyek" → pilih **"＋ Tambah Proyek Baru..."**
2. Ketik nama proyek baru → klik **Simpan**
3. Proyek otomatis tersimpan dan muncul di dropdown, bahkan setelah browser ditutup
4. Setiap pengguna yang membuka form dari browser yang sama akan melihat list yang sama

> ⚠️ Karena disimpan di localStorage, list proyek bisa berbeda antar device/browser.
> Untuk list proyek terpusat, update langsung di kode `const DEFAULTS = [...]` di `index.html`.

---

## 📱 Contoh Output WA

```
📋 Daftar Komplain & Tambahan (17/04/26)

1️⃣ *KEMENPORA*
• Saluran air bermasalah (08/04/26) ✅
• Kebocoran dekat meja makan (08/04/26) 🔴
• CCTV 2 Unit area parungan (09/04/26)

2️⃣ *DPR*
• Lampu TL Parungan (06/04/26) ✅
• Penutup lubang kaca atas (08/04/26)
• Kursi VIP patah sandaran (06/04/26)

━━━━━━━━━━━━━━━
📊 *Summary:* Total 6 | ✅ Selesai: 2 | ⏳ Pending: 4

_Dikirim otomatis setiap hari pukul 08.00 WIB_
```

---

## 🔧 Kustomisasi

### Ganti Default Proyek di Form
Edit `index.html` baris: `const DEFAULTS = ['Kemenpora','DPR','UMKM','Brawijaya','KP2MI'];`

### Ganti Jam Kirim WA
Di Workflow 2, node "Jadwal", edit `cronExpression`:
- `0 1 * * *` = 08.00 WIB (UTC+7 → UTC 01:00)
- `0 2 * * *` = 09.00 WIB

### Kirim ke Beberapa Nomor WA
Duplikat node "Kirim Rekapan ke WhatsApp", ganti nomor di masing-masing.

---

## ⚠️ Troubleshooting

| Masalah | Solusi |
|---|---|
| Form tidak bisa submit | Cek `WEBHOOK_URL` di `index.html` & pastikan workflow aktif |
| File tidak terupload ke Drive | Cek Folder ID & credential Drive sudah benar |
| WA tidak terkirim | Cek kredensial kirimi.id & device terhubung |
| Waktu WA tidak sesuai | Pakai cron UTC: `0 1 * * *` untuk 08.00 WIB |
| Foto tidak muncul di Sheet | Cek kolom `Attachment_URLs` ada di header Sheet |
| Status tidak update ke reported | Cek `row_number` ada di Sheet (generate otomatis oleh Google Sheets node) |

---

*Sistem Otomasi Komplain — Interior Consultant © 2026*
