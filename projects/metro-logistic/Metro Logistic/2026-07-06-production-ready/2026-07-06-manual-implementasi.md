# Manual Implementasi — Metro Logistik Tracking PWA (Production-Ready)

**Tanggal:** 2026-07-06
**Isi folder ini:** hasil QA ulang atas redesain `app/antigravity-redesign` + 3 workflow n8n, dengan semua perbaikan kontrak API sudah diterapkan. Folder lama tidak diubah sama sekali.

**[UPDATE] Dua aplikasi kini SEPENUHNYA TERPISAH** — di-deploy ke dua hosting/subdomain berbeda, tanpa link silang, tanpa file bersama. App publik tidak mengandung URL webhook update (keamanan), app admin tidak mengandung URL webhook get.

```
2026-07-06-production-ready/
├── app-publik/                           ← deploy ke domain publik (mis. tracking.domain.com)
│   ├── index.html                        (halaman pelacakan pelanggan)
│   ├── manifest.json                     (PWA "Metro Logistik")
│   ├── sw.js                             (service worker, cache prefix metropublik-)
│   ├── js/config.js                      ← edit: URL webhook GET saja
│   ├── js/tracking.js
│   └── icons/
├── app-admin/                            ← deploy ke domain terpisah (mis. ops-internal.domain.com)
│   ├── index.html                        (form admin lapangan — dulu admin.html)
│   ├── manifest.json                     (PWA "Metro Admin")
│   ├── sw.js                             (service worker, cache prefix metroadmin-)
│   ├── js/config.js                      ← edit: URL webhook UPDATE saja
│   ├── js/admin.js
│   └── icons/
├── n8n/                                  ← siap import ke n8n
│   ├── 2026-07-06-workflow-1-get-data.json
│   ├── 2026-07-06-workflow-2-update-data.json
│   └── 2026-07-06-workflow-3-housekeeping.json
└── 2026-07-06-manual-implementasi.md     (dokumen ini)
```

---

## Ringkasan Perbaikan (hasil QA 2026-07-06)

| # | Masalah | Perbaikan | File |
|---|---------|-----------|------|
| 1 | **KRITIS** — WF1 membalas `{ data: [...] }` padahal frontend membaca `data.results` → semua resi tampil "Tidak Ditemukan" di mode produksi | WF1 kini membalas `{ results: [...], data: [...], total }`; tracking.js juga menerima fallback `data` | WF1, tracking.js |
| 2 | Pesan error server tidak pernah tampil (n8n kirim `error`, frontend baca `message`) | WF2 kini kirim `message` + `error`; admin.js menerima keduanya | WF2, admin.js |
| 3 | `total_riwayat` tidak muncul di pop-up sukses (beda level nesting) | WF2 kirim di dua level; admin.js baca keduanya | WF2, admin.js |
| 4 | Retry saat timeout bisa menulis riwayat DOBEL ke Sheet | Idempotensi: `client_id` disimpan di entri riwayat; WF2 menolak duplikat & tetap balas sukses | WF2 |
| 5 | Sheet kosong → webhook timeout (node Code tidak jalan) | `alwaysOutputData: true` pada node baca Sheets di WF1 & WF2 | WF1, WF2 |
| 6 | WF3 jalan tiap 60 hari (spek: harian, ambang arsip 30 hari) | Schedule diubah ke harian jam 02:00 | WF3 |
| 7 | Antrean offline admin terhapus saat server error 5xx | Error 5xx kini dianggap sementara → data masuk antrean & dicoba ulang | admin.js |
| 8 | Tampilan rusak saat offline (Tailwind & font dari CDN tidak di-cache) | Service worker kini meng-cache `cdn.tailwindcss.com`, `fonts.googleapis.com`, `fonts.gstatic.com` | sw.js |
| 9 | `TEST_DUMMY: true` (mode demo) | Diubah ke `false` untuk produksi | config.js |
| 10 | "Terapkan Filter" tanpa pencarian tidak berfungsi di produksi | WF1 tanpa param `resi` kini membalas semua resi 30 hari terakhir (maks 100, terbaru dulu); frontend memanggilnya otomatis | WF1, tracking.js |
| 11 | Resi yang sudah diarsipkan WF3 tampil "Tidak Ditemukan" | WF1 kini fallback membaca spreadsheet Archive bila resi tak ada di Tracking (respons diberi flag `arsip: true`) | WF1 |
| 12 | App publik & admin satu paket: saling terhubung (link silang, SW publik ikut meng-cache halaman admin, URL webhook update terekspos di app publik) | Dipisah total jadi `app-publik/` dan `app-admin/`: config, service worker, manifest masing-masing; tanpa referensi silang | struktur folder |

Semua file JS lolos `node --check`, semua JSON workflow valid, dan enum status (`Manifest`, `On Process`, `Transit`, `Out for Delivery`, `Delivered`, `Failed/Return`) sudah dicek identik di config.js, kedua HTML, dan WF2.

---

## Langkah 1 — Siapkan Google Sheets (± 10 menit)

Buat **dua spreadsheet terpisah** di akun Google yang sama:

**Spreadsheet 1 (Utama)** — beri nama misal `Metro Logistik - Tracking`:
1. Ganti nama sheet pertama menjadi persis: `Tracking`
2. Isi baris 1 (header) persis dan berurutan:
   `No_Resi` | `Pengirim` | `Penerima` | `Status_Terakhir` | `Riwayat_Posisi_JSON` | `Timestamp_Update`

**Spreadsheet 2 (Arsip)** — beri nama misal `Metro Logistik - Archive`:
1. Ganti nama sheet pertama menjadi persis: `Archive`
2. Header sama seperti di atas **plus satu kolom di akhir**: `Tanggal_Diarsipkan`

**Catat kedua Spreadsheet ID** — bagian acak di URL:
`https://docs.google.com/spreadsheets/d/`**`INI_SPREADSHEET_ID`**`/edit`

> Penting: nama sheet dan header **case-sensitive** dan harus persis, karena workflow n8n mencocokkan berdasarkan nama kolom.

---

## Langkah 2 — Setup n8n (± 20 menit)

### 2a. Credential Google Sheets
1. Di n8n: **Credentials → Add credential → Google Sheets OAuth2 API** → login akun Google pemilik kedua spreadsheet.
2. Beri nama, misal `Google Sheets Metro Logistik`.

### 2b. Import 3 workflow
Untuk tiap file di folder `n8n/`: **Workflows → Import from File**.

### 2c. Ganti placeholder (di ketiga workflow)
Buka tiap node Google Sheets, lalu:
1. **Credential** → pilih credential dari langkah 2a (placeholder `GANTI_DENGAN_CREDENTIAL_ID_GOOGLE_SHEETS` otomatis tergantikan saat Anda memilih dari dropdown).
2. **Document ID** → ganti `GANTI_DENGAN_SPREADSHEET_ID_UTAMA` dengan ID Spreadsheet Utama. Placeholder `GANTI_DENGAN_SPREADSHEET_ID_ARCHIVE` (ada di WF1 node "Baca Sheet Archive" dan WF3 node "Append ke Archive") → isi ID Spreadsheet Arsip.

Jumlah node yang perlu disentuh: WF1 = 2 node, WF2 = 3 node, WF3 = 3 node.

### 2d. Zona waktu (penting untuk WF3)
Pastikan timezone instance n8n = `Asia/Jakarta`: **Settings → Timezone**, atau environment variable `GENERIC_TIMEZONE=Asia/Jakarta` (dan `TZ=Asia/Jakarta` bila self-host Docker). WF3 dijadwalkan harian jam 02:00 mengikuti timezone ini.

### 2e. Aktifkan & catat URL
1. Aktifkan (toggle **Active**) ketiga workflow.
2. Buka node Webhook di WF1 & WF2, salin **Production URL**:
   - WF1: `https://<domain-n8n-anda>/webhook/tracking-get`
   - WF2: `https://<domain-n8n-anda>/webhook/tracking-update`

> Gunakan **Production URL** (`/webhook/...`), BUKAN Test URL (`/webhook-test/...`). Test URL hanya hidup saat Anda menekan "Listen for test event".

### 2f. Uji cepat via terminal/HTTP client
```bash
# Uji WF2 (buat resi baru)
curl -X POST https://<domain-n8n-anda>/webhook/tracking-update \
  -H "Content-Type: application/json" \
  -d '{"no_resi":"TEST001","nama_admin":"QA Tester","status":"Manifest","lokasi":"Gudang Uji Coba"}'
# Harus balas: {"success":true,"no_resi":"TEST001","total_riwayat":1,...}

# Uji WF1 (baca resi tadi)
curl "https://<domain-n8n-anda>/webhook/tracking-get?resi=TEST001"
# Harus balas: {"results":[{"no_resi":"TEST001","found":true,...}],...}

# Uji WF1 tanpa parameter (mode 30 hari terakhir)
curl "https://<domain-n8n-anda>/webhook/tracking-get"
# Harus balas daftar resi yang diupdate <=30 hari, "cakupan":"terbaru-30-hari"
```
Cek juga baris `TEST001` muncul di Spreadsheet Utama. Hapus baris uji setelah selesai.

---

## Langkah 3 — Konfigurasi Frontend (± 3 menit)

Ada **dua** config yang diedit — masing-masing hanya tahu endpoint miliknya:

**`app-publik/js/config.js`:**
```js
const N8N_GET_URL = 'https://n8n.perusahaan-anda.com/webhook/tracking-get';
```

**`app-admin/js/config.js`:**
```js
const N8N_UPDATE_URL = 'https://n8n.perusahaan-anda.com/webhook/tracking-update';
```

`TEST_DUMMY` sudah `false` (produksi) di keduanya. Selama URL masih berisi `DOMAIN-N8N-ANDA`, aplikasi sengaja menampilkan pesan "endpoint belum dikonfigurasi" alih-alih retry percuma.

> Ingin demo tanpa server? Ubah sementara `TEST_DUMMY: true` di app publik — berjalan penuh dengan data simulasi (resi contoh: `JX12345678`, `JX87654321`, `JX55556666`, `JX11112222`). Catatan: karena kedua app kini terpisah origin, simulasi "update admin lalu lihat di publik" tidak lagi saling terhubung — uji alur nyata langsung ke n8n.

---

## Langkah 4 — Deploy Hosting (± 15 menit)

Deploy sebagai **dua situs terpisah** di dua origin (subdomain/domain) berbeda. Syarat mutlak keduanya: **HTTPS** (service worker & PWA tidak jalan di HTTP, kecuali `localhost`).

1. **App publik** — upload isi `app-publik/` ke hosting pertama, mis. `https://tracking.domain-anda.com/`. Ini yang dibagikan ke pelanggan.
2. **App admin** — upload isi `app-admin/` ke hosting kedua dengan nama yang tidak mudah ditebak, mis. `https://ops-internal.domain-anda.com/`. Hanya dibagikan ke petugas lapangan.

Pilihan mudah: **Netlify / Vercel / Cloudflare Pages** (buat 2 project, drag-and-drop tiap folder, HTTPS otomatis) atau **cPanel** (2 subdomain, masing-masing document root sendiri).

**Keamanan app admin** (karena tidak ada login bawaan):
- Kedua app kini tidak saling mereferensikan sama sekali — pengunjung publik tidak akan menemukan jejak URL admin di kode maupun cache.
- Sangat disarankan menambah lapisan akses di hosting: Basic Auth (cPanel Directory Privacy / Netlify password protection) atau Cloudflare Access.
- Opsional (hardening n8n): di node Webhook, isi opsi **Allowed Origins (CORS)** — WF1 = origin app publik, WF2 = origin app admin — sehingga browser dari origin lain ditolak.

---

## Langkah 5 — Uji End-to-End (checklist QA)

Lakukan berurutan di HP sungguhan (Chrome Android / Safari iOS):

1. [ ] Buka **app admin** (origin-nya sendiri) → isi form (status `Manifest`) → submit → pop-up "Berhasil Diperbarui" muncul, baris baru ada di Spreadsheet.
2. [ ] Submit update kedua untuk resi yang sama (status `Transit`) → kolom `Riwayat_Posisi_JSON` kini berisi 2 entri; `Status_Terakhir` & `Timestamp_Update` ikut berubah.
3. [ ] Buka halaman publik → lacak resi tadi → kartu muncul, "Lihat Detail" menampilkan timeline terbaru-di-atas.
4. [ ] Lacak beberapa resi sekaligus (pisah koma) termasuk satu resi ngawur → yang ngawur tampil "Tidak Ditemukan", lainnya normal.
5. [ ] Uji filter tanggal & status → kartu dan step tersaring konsisten.
5b. [ ] Muat ulang halaman publik (tanpa melacak apa pun) → langsung klik **Terapkan Filter** → app memuat semua resi 30 hari terakhir dari server.
5c. [ ] (Setelah WF3 pernah jalan) Lacak resi yang sudah diarsipkan → tetap ditemukan (diambil dari spreadsheet Archive).
6. [ ] **Uji offline (publik):** lacak resi → aktifkan mode pesawat → refresh & lacak resi yang sama → data tampil dari cache + banner offline; tampilan (styling) tetap utuh.
7. [ ] **Uji offline (admin):** mode pesawat → submit update → pesan "disimpan di perangkat"; matikan mode pesawat → toast sinkronisasi muncul → data masuk Spreadsheet **satu kali saja** (tidak dobel).
8. [ ] Instal PWA di kedua app ("Add to Home Screen") → dua ikon terpisah muncul ("Metro Logistik" & "Metro Admin"), masing-masing terbuka standalone.
8b. [ ] Verifikasi isolasi: buka DevTools di app publik → Application → Cache Storage → hanya cache `metropublik-*`; tidak ada file admin. Cari string "webhook/tracking-update" di source app publik → tidak boleh ada.
9. [ ] Kirim status tidak valid via curl (mis. `"status":"Dikirim"`) → respons 400 dengan pesan jelas, tidak ada baris masuk Sheet.
10. [ ] (Opsional, WF3) Ubah sementara `Timestamp_Update` sebuah resi `Delivered` menjadi > 30 hari lalu → jalankan WF3 manual (**Execute workflow**) → baris pindah ke Archive & terhapus dari Tracking.

---

## Troubleshooting

**Semua resi "Tidak Ditemukan" padahal ada di Sheet** → Anda memakai workflow versi lama (respons `data` tanpa `results`). Pastikan yang aktif adalah workflow dari folder ini. Frontend versi ini sebenarnya sudah menerima kedua format — cek juga nama kolom header Sheet persis `No_Resi` dst.

**Error CORS di console browser** → pastikan yang dipanggil Production URL n8n, dan workflow **Active**. Node webhook & respond di workflow ini sudah menyertakan header `Access-Control-Allow-Origin: *`.

**Webhook balas 404** → workflow belum Active, atau Anda memakai `/webhook-test/` alih-alih `/webhook/`.

**Update admin tidak muncul di pelacakan** → tunggu beberapa detik lalu lacak ulang (halaman publik selalu fetch data segar; bila hasil lama tampil, itu cache offline — pull-to-refresh saat online).

**Jam di timeline aneh** → pastikan timezone n8n `Asia/Jakarta` (langkah 2d). Semua timestamp ditulis eksplisit `+07:00`.

**Setelah update file di hosting, HP masih menampilkan versi lama** → service worker menyimpan shell. Naikkan `CACHE_VERSION` di `sw.js` app yang bersangkutan setiap kali deploy ulang (mis. `v2.0.1-publik` / `v2.0.1-admin`), lalu muat ulang dua kali.

---

## Catatan Arsitektur Singkat

- **Alur data:** PWA → webhook n8n → Google Sheets (Utama) → arsip otomatis harian ke Spreadsheet Archive (WF3, `Delivered` > 30 hari).
- **Kontrak WF1:** `GET /webhook/tracking-get?resi=A,B` → `{ results: [{ no_resi, found, pengirim, penerima, status_terakhir, timestamp_update, riwayat: [...] }], total }`. Resi yang tak ada di `Tracking` dicari di `Archive` (hasil diberi `arsip: true`). Tanpa param `resi` → semua resi 30 hari terakhir (maks 100), plus `cakupan: "terbaru-30-hari"`.
- **Kontrak WF2:** `POST /webhook/tracking-update` body `{ no_resi, nama_admin, status, lokasi, client_id? }` → sukses `{ success: true, no_resi, total_riwayat, message }` / gagal 400 `{ success: false, error, message }`.
- **Idempotensi:** `client_id` (UUID dari perangkat admin) tersimpan di tiap entri riwayat; request ulang dengan `client_id` sama tidak menggandakan data.
- Dokumen referensi lengkap tetap di folder `docs/` proyek (skema sheet, arsitektur, wireframe).
