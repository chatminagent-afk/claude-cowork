# Manual Deploy VIRA Dashboard

**Satu-satunya dokumen yang perlu kamu buka untuk deploy.** Berdiri sendiri —
tidak perlu lompat ke file lain.

Terakhir diperbarui: 2026-08-26

---

## 0. Di mana semuanya

```
D:\Documents\Claude Cowork\VIRA Dashboard\
├── 2026-08-26-runbook-deploy.md        <- file ini
└── 2026-07-28-production\              <- semua bahan deploy ada di sini
    ├── app\                            <- yang di-upload ke hosting (HANYA folder ini)
    ├── demo\VIRA-Dashboard-DEMO.html   <- demo offline, klik dua kali langsung jalan
    ├── n8n\
    │   ├── VIRA-Dashboard-API.json     <- workflow yang di-import ke n8n
    │   ├── build_workflow.py           <- perakit workflow
    │   └── src\*.js                    <- sumber kebenaran kode (edit di sini)
    ├── qa\                             <- test + server lokal (JANGAN di-upload)
    └── docs\
        ├── 2026-07-28-API-CONTRACT.md            <- spesifikasi API
        ├── 2026-07-28-UAT-report.md              <- laporan uji
        └── KREDENSIAL-JANGAN-DIBAGIKAN.txt       <- password owner
```

Semua perintah di manual ini dijalankan dari dalam `2026-07-28-production\`.

---

## 1. Apa yang di-deploy

Satu halaman statis + satu workflow n8n. Melayani dua klien (The Scholars &
Persada) dari satu kode; tiap owner hanya bisa melihat datanya sendiri.

```
Browser (Cloudflare Pages / Netlify)
      │  POST  {action, token, …}
      ▼
n8n  "VIRA Dashboard API"  ── webhook /vira-dash
      │  tenant diambil dari token, BUKAN dari request
      ▼
Google Sheets (service account khusus dashboard)
```

Yang didapat Sam setelah ini hidup:
- Direktori lead + KPI + chart
- **Toggle bot ON/OFF per nomor** — dia bisa matikan VIRA sendiri tanpa lewat kamu
- Blok topik bulanan (baru muncul setelah `MONTHLY_SUMMARY` ada isinya, ~1 Oktober)

**Estimasi: ~90 menit.** Langkah 2 paling lama karena menunggu Google.

---

## 2. Sebelum mulai — lihat demonya (5 menit)

Buka `demo\VIRA-Dashboard-DEMO.html` dengan klik dua kali. Login `steven` / `demo`.

Ini menjalankan aplikasi yang **sama persis** dengan data contoh yang ditanam di
dalam berkas. Gunanya: pastikan tampilannya sudah sesuai **sebelum** repot
mengurus service account. Kalau ada yang mau diubah, jauh lebih murah sekarang.

Berkas itu tidak memuat kredensial dan tidak memuat data pelanggan asli — aman
dikirim ke Sam dulu untuk minta masukan.

---

## 3. Langkah 0 — Rotasi kunci penandatangan (5 menit)

**Kerjakan sebelum build pertama**, supaya tidak perlu rebuild dua kali.

`n8n/build_workflow.py` baris 29 memuat `HMAC_SECRET` dalam bentuk polos. Kunci
ini menandatangani semua token sesi — siapa pun yang memegangnya bisa memalsukan
token untuk akun dan tenant mana pun, tanpa perlu password. Nilainya ikut
tersalin ke `VIRA-Dashboard-API.json` setiap rebuild, jadi setiap kali workflow
di-export kunci itu ikut. Nilai yang sekarang sudah ada di folder proyek sejak
Juli — perlakukan sebagai sudah terekspos.

Buat nilai baru:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

- [x] Tempel hasilnya ke `n8n/build_workflow.py` baris 29, ganti nilai lama
      — **sudah dikerjakan 2026-08-26.** Kunci lama sudah tidak ada lagi di
      mana pun dalam folder proyek; `VIRA-Dashboard-API.json` sudah di-rebuild
      dengan kunci baru. Tidak perlu diulang.

---

## 4. Langkah 1 — Service account Google (~30 menit)

**Service account (SA)** = akun robot Google berbentuk email, misal
`vira-dashboard@nama-project.iam.gserviceaccount.com`. n8n memakainya untuk
membuka spreadsheet tanpa login sebagai kamu. Spreadsheet kamu *share* ke email
itu, persis seperti share ke orang.

**Kenapa harus terpisah dari SA bot:** kuota Google Sheets dihitung **60
read/menit per akun**. Kalau dashboard menumpang akun bot, keduanya berebut
jatah yang sama — itu persis penyebab pesan hilang yang dulu kamu kejar. SA
sendiri = jatah sendiri.

- [x] Google Cloud Console → IAM & Admin → Service Accounts → **Create**
      — dibuat di project `vira-506713`
- [x] Nama: `vira-425` (runbook awal menulis `vira-dashboard` — beda nama saja,
      tidak berpengaruh; yang penting terpisah dari SA bot)
- [x] Buat **key JSON**, download (nanti dihapus di akhir langkah ini)
- [x] APIs & Services → **Google Sheets API** aktif di `vira-506713`
- [x] Email SA: `vira-425@vira-506713.iam.gserviceaccount.com`
- [x] Share spreadsheet **The Scholars** ke email itu, akses **Editor**
      → `1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE`
- [x] Share spreadsheet **Persada** ke email itu, akses **Editor**
      → `1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o`

> Wajib **Editor**, bukan Viewer — toggle `bot_mode` perlu menulis.

- [x] n8n → Credentials → New → **Google Service Account API**
      → credential ID `5KD9A3Tef1H8UQKk`, di dalam n8n project `sXUEZy1FQDksvKLg`
- [ ] Nama credential **persis**: `Google Service Account - VIRA Dashboard`
- [x] Tempel *service account email* + *private key* dari file JSON
- [x] Klik **Test** — hijau ✅ 2026-08-26
- [ ] **Hapus file key JSON dari komputer.** Jangan simpan di spreadsheet.

---

## 5. Langkah 2 — Tab audit (5 menit, disarankan)

Di **kedua** spreadsheet, buat tab `DASH_AUDIT` dengan header persis di baris 1:

```
ts | actor | role | no_wa | from | to
```

- [ ] `DASH_AUDIT` di The_Scholars_Database
- [ ] `DASH_AUDIT` di PCR_Database

Setiap perubahan `bot_mode` dari dashboard tercatat di sini. Tanpa ini toggle
tetap jalan (node audit gagal diam), tapi kalau nanti ada pertanyaan *"siapa
yang mematikan bot untuk nomor ini"*, tidak ada jawabannya.

---

## 6. Langkah 3 — Build & import workflow (10 menit)

- [x] Buka credential yang dibuat di Langkah 1 di n8n — **ID-nya ada di URL browser**
- [x] Tempel ID itu ke `n8n/build_workflow.py` baris 35 — **sudah, 2026-08-26**
- [x] Rebuild — **sudah**; 4 node Sheets terverifikasi memakai ID di atas

```bash
python n8n/build_workflow.py
```

> Script punya penjaga: kalau masih placeholder dia akan protes. Kalau lolos
> tanpa keluhan, ID sudah masuk. Murni Python, tidak butuh Node/npm.

> ⚠️ n8n memakai **projects**. Credential-nya ada di project `sXUEZy1FQDksvKLg`.
> Import workflow ini ke **project yang sama** — kalau di-import ke project lain,
> node Sheets tidak akan menemukan credential-nya meski ID-nya benar.

- [ ] n8n → **Import from File** → `n8n/VIRA-Dashboard-API.json`
- [ ] Buka **7 node Google Sheets**, pastikan credential-nya terpilih:
      `Read Tab` · `Read STATS for Toggle` · `Update Bot Mode` · `Append Audit` ·
      `Read STATS for Add` · `Append Lead` · `Append Audit (Add)`
- [ ] Buka node **`Ask Anthropic`**, pastikan credential
      **Anthropic The Scholars** (`oO9D2lMQoz5UOhu8`) terpilih
- [ ] **JANGAN aktifkan dulu**

> ⚠️ **Import ini sekaligus menerbitkan tenant `personal`.** Ekspor produksi
> terakhir (28 Agu) hanya punya 2 tenant; build lokal punya 3. Kalau `personal`
> belum siap tayang, hapus entrinya dari `n8n/src/tenants.js` lalu rebuild
> sebelum import.

> ⚠️ **Nama model belum pernah diuji ke API.** `ANTHROPIC_MODEL` di
> `build_workflow.py` baris 45 berisi `claude-sonnet-5`. Kalau id itu tidak
> dikenali akun Anthropic-mu, node `Ask Anthropic` gagal **diam-diam** (sengaja
> `continueRegularOutput`) dan kartu rekomendasi tidak pernah muncul, tanpa
> pesan galat di dashboard. Cara memastikan: jalankan workflow manual sekali,
> lihat output node itu di n8n. Kalau 404 `model_not_found`, ganti konstanta
> tadi lalu rebuild + import ulang.

---

## 7. Langkah 4 — Upload frontend & kunci CORS (15 menit)

- [x] Upload **isi folder `app\` saja** — dideploy ke Cloudflare **Workers**
      (bukan Pages; sama saja untuk keperluan kita)

> Jangan upload `qa\`, `docs\`, atau `n8n\`. Folder `docs\` memuat file kredensial.

- [x] Domain: `https://vira-dashboard.chatminagent.workers.dev`
      — diverifikasi 2026-08-26, halaman login tampil, tidak ada error konsol
- [x] `n8n/src/tenants.js` → `corsOrigins` sudah berisi domain di atas
      (tanpa garis miring di akhir — browser mengirim `Origin` tanpa itu).
      Dua entry localhost dipertahankan.
- [x] Rebuild — **sudah dikerjakan 2026-08-26**

```bash
python n8n/build_workflow.py
```

- [ ] Import ulang `n8n/VIRA-Dashboard-API.json` ke n8n project `sXUEZy1FQDksvKLg`
- [ ] **Aktifkan workflow**

CORS sengaja tidak memakai `*`. Dengan wildcard, halaman mana pun di internet
bisa memanggil API ini memakai token curian.

> `app/js/config.js` sudah berisi alamat webhook produksi yang benar
> (`https://n8n.srv1270416.hstgr.cloud/webhook/vira-dash`) — **tidak perlu diubah.**

---

## 8. Langkah 5 — Smoke test ⚠️ BAGIAN PALING PENTING (20 menit)

Lima hal ini **belum pernah dijalankan di n8n sungguhan**. QA yang lolos selama
ini melawan mock server Python, bukan n8n asli.

### 5.1 Login & bentuk token
- [ ] Buka domainmu, login sebagai `steven`
- [ ] DevTools → Application → Local Storage → `vd.token`

**Harus:** `<base64url>.<64 karakter hex>`
**Kalau tanda tangannya kosong / panjangnya beda:** `encoding: hex` pada node
Crypto tidak terpasang benar.

### 5.1b Tambah lead — jalur tulis baru ⚠️
- [ ] Klik **+ Tambah** di direktori lead
- [ ] Isi nomor dummy milikmu sendiri, biarkan switch **OFF**, Tambahkan
- [ ] Cek tab `STATS`: baris baru muncul di **paling bawah**, kolom `No WA`
      berisi nomor ternormalkan (`62…`), `bot_mode` = `OFF`, `Counter` = 0
- [ ] Cek tab `DASH_AUDIT`: ada baris `from = (baru)`, `to = OFF`
- [ ] Coba tambahkan **nomor yang sama lagi** → harus ditolak dengan pesan
      yang menyebut nama pemiliknya, dan **tidak ada baris kedua** di STATS
- [ ] Toggle bot untuk nomor baru itu → harus mengenai baris yang benar
- [ ] Hapus baris dummy dari STATS setelah selesai

**Kalau baris mendarat di kolom yang salah / muncul kolom baru:** header sheet
tidak persis `No WA` / `Nama` / `bot_mode` / `Counter` (perhatikan spasi di
ujung nama kolom). Seharusnya ditolak `SHEET_SCHEMA` sebelum menulis — kalau
tetap tertulis, laporkan.

### 5.1c Rekomendasi AI — pastikan hanya 1 panggilan per bulan ⚠️
- [ ] Buka dashboard, catat apakah kartu **Rekomendasi dari Topik** muncul
- [ ] n8n → Executions, buka eksekusi tadi, lihat node `Ask Anthropic` → **jalan**
- [ ] Tekan **Segarkan** 3-4 kali
- [ ] Buka executions lagi: node `Ask Anthropic` **tidak boleh jalan lagi**
      (cabang `IF Need AI` harus ke output kedua)

**Kalau `Ask Anthropic` jalan setiap refresh:** static data tidak tersimpan.
Itu berarti biaya token per buka dashboard — hentikan dan laporkan sebelum
dibagikan ke klien.

### 5.2 Pembacaan multi-tab
- [ ] Dashboard harus terisi: direktori lead + tabel-tabelnya

**Kalau ada tabel kosong padahal sheetnya berisi:** nama tab di
`VIRA_TENANTS[...].tabs` tidak cocok — **peka huruf besar-kecil**.

### 5.3 `documentId` dinamis
- [ ] Perhatikan node Sheets menerima ekspresi `{{ $json.doc_id }}`

**Kalau n8n menolak:** ganti mode Resource Locator ke **"By ID"**, pastikan
nilainya diawali `=`.

### 5.4 Toggle menulis ke baris yang benar 🔴 PALING KRITIS
- [ ] Siapkan **satu nomor uji** — nomormu sendiri, jangan customer
- [ ] Catat posisi barisnya di tab STATS **sebelum** toggle
- [ ] Matikan bot untuk nomor itu lewat dashboard
- [ ] **Buka spreadsheet, pastikan yang berubah adalah baris itu — bukan baris lain**

**Salah baris berarti bot mati untuk customer yang salah, dan tidak ada yang
tahu sampai customer itu komplain.** Kalau meleset: hentikan, jangan lanjut,
jangan kasih akses ke Sam.

### 5.5 Integrasi — bot beneran diam
- [ ] Dari nomor uji yang barusan di-OFF, kirim pesan WhatsApp ke VIRA
- [ ] **Bot harus benar-benar diam**
- [ ] Nyalakan lagi lewat dashboard, kirim lagi → bot harus membalas
- [ ] Cek `DASH_AUDIT` — kedua perubahan tercatat

> Kerjakan tes ini **selagi bot masih versi r6 yang sudah terbukti.** Kalau
> kamu ganti botnya (patch r8) bersamaan dan tes ini gagal, kamu tidak bisa tahu
> penyebabnya dashboard atau r8.

---

## 9. Langkah 6 — Bagikan akses (10 menit)

- [ ] Password ada di `docs\KREDENSIAL-JANGAN-DIBAGIKAN.txt`
- [ ] Kirim link dan password lewat **channel berbeda**
      (link via email, password via WA langsung)
- [ ] Setelah semua owner terima → pindahkan file itu ke password manager,
      **hapus dari folder proyek**
- [ ] Minta Sam install: buka domain di **Safari** (iOS) atau Chrome (Android)
      → *Add to Home Screen*

> iOS hanya bisa install lewat **Safari**. Chrome di iOS tidak memunculkan opsi
> install. Ini batasan Apple, bukan bug.

Akun yang tersedia: `steven` (dua klien, bisa ganti tenant), `sam` (The Scholars
saja), `sulianto` (Persada saja).

---

## 10. Kalau bermasalah

| Gejala | Penyebab |
|---|---|
| Login gagal terus padahal password benar | Akun terkunci 15 menit setelah 5 kali salah. Tunggu, atau restart workflow untuk mengosongkan static data. |
| Semua request gagal, error CORS di console | Domain hosting belum masuk `corsOrigins`. Rebuild + import ulang. |
| Login berhasil tapi dashboard kosong | Nama tab tidak cocok (peka huruf besar-kecil), **atau** spreadsheet belum di-share ke SA |
| Sebagian tabel kosong, sebagian terisi | Tab tertentu salah nama. `Read Tab` sengaja tidak menjatuhkan seluruh request kalau satu tab gagal. |
| `SHEET_ERROR` | SA belum punya akses **Editor**, atau Sheets API belum aktif |
| Angka tidak berubah setelah toggle | Cache 60 detik — tekan Segarkan |
| Banner oranye "Mode uji" di produksi | `?api=` masih menempel di URL atau tersimpan di localStorage. Klik "Kembali ke produksi". |
| Blok topik bulanan tidak muncul | Normal sampai `MONTHLY_SUMMARY` ada isinya (~1 Oktober) |

**Debug:** riwayat eksekusi sukses sengaja tidak disimpan
(`saveDataSuccessExecution: none`) karena body login memuat password plaintext.
Kalau perlu debug, aktifkan sementara lalu **kembalikan ke `none`**.

**Pratinjau lokal tanpa deploy:**

```bash
python qa/serve.py
```

Lalu buka `http://localhost:8099/qa/selftest.html` (unit test) atau
`http://localhost:8099/qa/preview-monthly.html` (pratinjau blok topik bulanan).

---

## 11. Rollback

Dashboard **read-only** untuk semua data kecuali kolom `bot_mode`. Risiko
terburuk terbatas pada satu kolom itu.

1. **Nonaktifkan workflow** di n8n → seluruh dashboard mati, bot tidak
   terpengaruh sama sekali (workflow terpisah, credential terpisah)
2. Kalau `bot_mode` sempat salah tulis → perbaiki manual di spreadsheet,
   cek `DASH_AUDIT` untuk tahu baris mana yang tersentuh
3. Frontend statis — hapus deployment di Cloudflare/Netlify kapan saja

**Bot tidak pernah dalam risiko dari langkah mana pun di manual ini.**

---

## 12. Pemeliharaan

### Menambah klien ketiga
Tambah satu entri di `VIRA_TENANTS` (`n8n/src/tenants.js`): `sheetId`, daftar
`tabs`, pemetaan kolom, KPI/chart/tabel tambahan. Lalu tambah akun ownernya di
`VIRA_USERS`, rebuild, import ulang, share spreadsheet ke SA dashboard.

**Frontend tidak perlu disentuh sama sekali** — dijaga oleh
`qa/validate_workflow.py` yang menolak build kalau ada nama klien bocor ke `app\`.

### Mengganti password — bisa dikerjakan sendiri, tanpa bantuan
Klik dua kali `qa\ganti-password.bat`. Dia menanyakan akun mana (daftarnya
dibaca dari `tenants.js`), lalu mengeluarkan `salt` + `hash`.

1. Buka `n8n/src/tenants.js`, cari entri akun itu
2. Ganti dua baris `salt:` dan `hash:`-nya dengan keluaran tadi
3. `python n8n/build_workflow.py`
4. Import ulang workflow ke n8n

Password memang tertanam di dalam workflow — sistem ini sengaja tidak punya
database, jadi semua state hidup di workflow. Konsekuensinya setiap ganti
password perlu rebuild + import. Empat langkah di atas itu keseluruhannya.

Token lama tetap hidup sampai kedaluwarsa (lihat `tokenTtlSec`, sekarang 30
hari). Kalau perlu memutus akses seketika: hapus entri usernya lalu
rebuild+import (hanya orang itu), atau ganti `HMAC_SECRET` (semua orang).

### Mencabut akses seseorang
Hapus entrinya dari `VIRA_USERS`, rebuild, import. Berlaku **langsung** — setiap
request memeriksa ulang akun ke registry, bukan sekadar percaya isi token.

### Jangan edit Code node lewat UI n8n
Isinya di-generate dari `n8n/src/*.js`. Edit di sana lalu jalankan
`python n8n/build_workflow.py`. `validate_workflow.py` akan menolak kalau
workflow tertinggal dari src.

### Umur sesi login
`VIRA_SETTINGS.tokenTtlSec` = **30 hari** (2026-08-26; sebelumnya 12 jam).
Owner cukup masuk sekali lalu memakai ikon PWA tanpa login ulang selama sebulan.

Konsekuensinya: kalau HP owner hilang, sesinya hidup sampai 30 hari. Dua cara
memutus — hapus entri usernya di `VIRA_USERS` lalu rebuild+import (berlaku
seketika, hanya orang itu), atau ganti `HMAC_SECRET` (seketika, tapi menendang
semua orang). Kembalikan ke `12 * 60 * 60` kalau dirasa terlalu longgar.

### Menyetel beban Google Sheets
`VIRA_SETTINGS.statsCacheSec` (default 60 detik). Naikkan kalau kuota terasa
ketat; set `0` untuk mematikan cache. Frontend **tidak polling** — data hanya
ditarik saat login, ganti tenant, dan tombol Segarkan.

---

## 13. Belum tercakup (di luar deploy ini)

- Rotasi service account Persada — private key tersimpan polos di tab CONFIG
  Persada. Terpisah dari deploy ini, tapi masih terbuka.
- Kredensial Kirimi hardcoded di node workflow bot, bukan di credential store —
  ikut bocor di setiap export workflow bot.
- Webhook inbound bot (`/wa-inbound`, `/wa-inbound-pcr`) tanpa autentikasi.
