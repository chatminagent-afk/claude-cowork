# Panduan Deploy — VIRA Dashboard

Versi 1.0 · 2026-07-28

Dashboard statis + satu workflow n8n. Melayani dua klien dari satu kode; owner
hanya bisa melihat datanya sendiri.

```
Browser (Cloudflare Pages / Netlify)
      │  POST text/plain  {action, token, …}
      ▼
n8n  "VIRA Dashboard API"  ── webhook /vira-dash
      │  tenant diambil dari token, BUKAN dari request
      ▼
Google Sheets (service account khusus dashboard)
```

---

## Isi folder

| Path | Isi |
|---|---|
| `app/` | yang di-upload ke hosting statis. **Hanya folder ini.** |
| `demo/VIRA-Dashboard-DEMO.html` | demo satu-berkas, buka langsung tanpa setup |
| `n8n/VIRA-Dashboard-API.json` | workflow siap import |
| `n8n/src/*.js` | sumber kebenaran kode Code node |
| `n8n/build_workflow.py` | perakit workflow dari `src/` |
| `qa/` | test + mock server. **Jangan di-upload.** |
| `docs/` | dokumen ini + kontrak API + laporan UAT + kredensial |

---

## Sebelum mulai: lihat demonya

`demo/VIRA-Dashboard-DEMO.html` menjalankan aplikasi yang **sama persis** (CSS
dan JavaScript diambil apa adanya dari `app/`) dengan data contoh yang ditanam
di dalam berkas. Buka dengan klik dua kali, login `steven` / `demo`.

Gunanya: memastikan tampilan dan alurnya sudah sesuai **sebelum** repot mengurus
service account Google dan CORS. Kalau ada yang mau diubah, lebih murah diubah
sekarang.

Berkas itu tidak memuat kredensial dan tidak memuat data pelanggan asli, jadi
aman dikirim ke owner untuk minta masukan lebih dulu.

---

## Urutan pengerjaan

Kerjakan berurutan. Langkah 1 memakan waktu paling lama karena menunggu Google.

### 1. Service account Google khusus dashboard

Kenapa terpisah dari service account bot: kuota Google Sheets dihitung
**per pengguna** (60 read/menit). Service account sendiri = jatah sendiri, jadi
orang yang membuka dashboard tidak bisa membuat bot kehabisan kuota dan berhenti
membalas customer. Bot Persada sudah berjalan dekat plafonnya.

1. Google Cloud Console → project yang sama dengan service account bot → **IAM &
   Admin → Service Accounts → Create**. Nama: `vira-dashboard`.
2. Buat key JSON, simpan sementara.
3. Pastikan **Google Sheets API** aktif di project itu.
4. Bagikan **kedua** spreadsheet ke alamat email service account tersebut dengan
   akses **Editor** (butuh tulis untuk toggle `bot_mode`):
   - `The_Scholars_Database` — `1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE`
   - `PCR_Database` — `1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o`
5. n8n → **Credentials → New → Google Service Account API**. Beri nama persis:
   `Google Service Account - VIRA Dashboard`. Tempel email + private key.
6. Hapus file key JSON dari komputer. Jangan menyimpannya di spreadsheet —
   itu justru masalah yang sedang ada di CONFIG Persada (lihat dokumen
   konsultasi, temuan T1).

### 2. Tab audit (opsional tapi disarankan)

Di **kedua** spreadsheet, buat tab bernama `DASH_AUDIT` dengan header di baris 1:

```
ts | actor | role | no_wa | from | to
```

Setiap perubahan `bot_mode` dari dashboard dicatat di sini. Kalau nanti ada
pertanyaan "siapa yang mematikan bot untuk nomor ini", jawabannya ada.

Kalau tab ini tidak dibuat, toggle **tetap berfungsi** — node audit gagal diam
(`onError: continueRegularOutput`). Jadi aman dipasang belakangan.

### 3. Import workflow

1. n8n → **Import from File** → `n8n/VIRA-Dashboard-API.json`.
2. Buka **4 node Google Sheets** (`Read Tab`, `Read STATS for Toggle`,
   `Update Bot Mode`, `Append Audit`) → pilih credential dari langkah 1.
   Credential ID di file sengaja placeholder supaya salah pilih tidak mungkin
   terjadi diam-diam.
3. **Jangan aktifkan dulu.**

### 4. Upload frontend & kunci CORS

1. Upload isi folder `app/` ke Cloudflare Pages atau Netlify (drag-and-drop
   foldernya; tidak ada build step, tidak butuh Node).
2. Catat domain hasil deploy, misal `https://vira-dashboard.pages.dev`.
3. Buka `n8n/src/tenants.js` → `VIRA_SETTINGS.corsOrigins` → ganti
   `'https://vira-dashboard.pages.dev'` dengan domain kamu yang sebenarnya.
4. Buka `app/js/config.js` → set URL API produksi ke
   `https://n8n.srv1270416.hstgr.cloud/webhook/vira-dash`.
5. Rebuild & import ulang:
   ```bash
   python n8n/build_workflow.py
   ```
6. Upload ulang `app/`.

CORS sengaja **tidak** memakai `*`. Kalau wildcard dipakai, halaman mana pun di
internet bisa memanggil API ini dengan token yang dicuri.

### 5. Aktifkan & smoke test

Aktifkan workflow, lalu kerjakan **checklist §8 di
`2026-07-28-UAT-report.md`** — empat hal di sana belum pernah diuji terhadap
n8n sungguhan (node Crypto, loop pembacaan tab, `documentId` dinamis, dan
ketepatan baris saat menulis `bot_mode`).

Yang paling penting dari checklist itu: **matikan bot untuk satu nomor uji, lalu
buka spreadsheet dan pastikan baris yang berubah memang baris itu.** Salah baris
berarti bot mati untuk customer yang salah.

### 6. Bagikan akses

Password ada di `docs/KREDENSIAL-JANGAN-DIBAGIKAN.txt`. Kirim link dan password
lewat **channel berbeda** (misal link via email, password via WhatsApp langsung).
Setelah semua owner menerima, pindahkan file itu ke password manager dan hapus
dari folder proyek.

---

## Cara kerja yang perlu diketahui saat memelihara

### Menambah klien ketiga
Tambahkan satu entri di `VIRA_TENANTS` (`n8n/src/tenants.js`): `sheetId`, daftar
`tabs`, pemetaan kolom, label kolom lead, KPI/chart/tabel tambahan. Lalu tambah
akun ownernya di `VIRA_USERS`, rebuild, import ulang, bagikan spreadsheet ke
service account dashboard.

**Frontend tidak perlu disentuh sama sekali.** Server mengirim deskriptor
(label, tipe kolom, judul chart) dan frontend merender apa pun yang diterima.
Ini sudah diuji: `qa/validate_workflow.py` menolak build kalau ada nama klien
atau nama kolom spesifik muncul di folder `app/`.

### Mengganti password
```bash
python qa/hash_password.py "password-baru"
```
Salin `salt` dan `hash` ke entri user, rebuild, import ulang. Token yang sudah
terbit tetap hidup sampai kedaluwarsa (maks 12 jam) — kalau perlu memutus akses
seketika, ganti juga `HMAC_SECRET` di `build_workflow.py`.

### Mencabut akses seseorang
Hapus entrinya dari `VIRA_USERS`, rebuild, import. Berlaku **langsung**: setiap
request memeriksa ulang akun ke registry, bukan sekadar percaya isi token.

### Jangan edit Code node lewat UI n8n
Isinya di-generate dari `n8n/src/*.js`. Edit di sana lalu jalankan
`python n8n/build_workflow.py`. `validate_workflow.py` akan menolak kalau
workflow tertinggal dari src.

### Menyetel beban Google Sheets
`VIRA_SETTINGS.statsCacheSec` (default 60 detik). Naikkan kalau kuota terasa
ketat; set `0` untuk mematikan cache. Frontend **tidak melakukan polling** —
data hanya ditarik saat login, ganti tenant, dan tombol Segarkan. Ganti rentang
7/30/90 hari diproses di browser, tanpa memanggil server.

---

## Kalau bermasalah

| Gejala | Kemungkinan penyebab |
|---|---|
| Login gagal terus padahal password benar | akun terkunci 15 menit setelah 5 kali salah — tunggu, atau restart workflow untuk mengosongkan static data |
| Semua request gagal di browser, error CORS | domain hosting belum ada di `corsOrigins`; rebuild + import ulang |
| Dashboard kosong tapi login berhasil | nama tab di `VIRA_TENANTS[...].tabs` tidak cocok (peka huruf besar-kecil), atau spreadsheet belum dibagikan ke service account |
| Sebagian tabel kosong, sebagian terisi | tab tertentu tidak ada / salah nama; node `Read Tab` sengaja tidak menjatuhkan seluruh request kalau satu tab gagal |
| Angka tidak berubah setelah toggle | cache 60 detik — tekan Segarkan; toggle sendiri sudah mengosongkan cache tenant itu |
| Banner oranye "Mode uji" muncul di produksi | `?api=` masih menempel di URL atau tersimpan di localStorage; klik "Kembali ke produksi" |
| Muncul `SHEET_ERROR` | service account belum punya akses Editor ke spreadsheet, atau Sheets API belum aktif |

Riwayat eksekusi sukses **sengaja tidak disimpan** (`saveDataSuccessExecution:
none`) karena body login memuat password plaintext. Untuk debug, aktifkan
sementara, lalu **kembalikan ke `none`** setelah selesai.
