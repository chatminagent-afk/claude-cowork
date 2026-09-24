# Laporan QA / UAT — VIRA Dashboard

Tanggal: 2026-07-28 (ronde 2 setelah laporan bug dari Steven)
Penguji: Claude (Opus 5) · Lingkungan: lokal, mock API
Status: **LOLOS** — 337 pemeriksaan otomatis, 0 gagal, + 70 perilaku aplikasi
diverifikasi langsung di browser.

---

## 1. Ringkasan

| Lapis | Alat | Jumlah | Gagal |
|---|---|---:|---:|
| Gerbang statis | `qa/validate_workflow.py` | 24 | 0 |
| Unit (modul asli) | `qa/selftest.html` | 183 | 0 |
| **DOM & event (baru)** | `qa/uitest.html` | 94 | 0 |
| Integrasi API | skrip E2E di browser | 36 | 0 |
| Perilaku aplikasi | manual, browser | 70 | 0 |
| **Total** | | **407** | **0** |

Cara menjalankan ulang:

```bash
python qa/validate_workflow.py
```

```bash
python qa/serve.py
```

lalu buka ketiganya, semua harus tertulis **SEMUA LOLOS**:

- `http://localhost:8099/qa/selftest.html`
- `http://localhost:8099/qa/uitest.html`
- `http://localhost:8099/app/index.html?api=http://localhost:8099/api/vira-dash`

---

## 0. Ronde 2 — tiga bug ditemukan dan diperbaiki

Steven melaporkan: *toggle bot_mode kalau sudah dimatikan tidak bisa dinyalakan
lagi.* Benar, dan penelusurannya menemukan dua bug lain di sekitarnya.

### Bug 1 — toggle tidak bisa dibalik arah (dilaporkan Steven) 🔴

`app/js/render.js`, `toggleSwitch()`. Status bot dihitung **sekali saat baris
digambar** lalu disimpan di variabel closure:

```js
var on = String(row.bot_mode).toUpperCase() !== 'OFF';   // dibekukan di sini
sw.addEventListener('click', function () {
  handlers.onToggle(row, on ? 'OFF' : 'ON', sw);         // selamanya pakai nilai lama
});
```

Setelah satu kali toggle, `app.js` sudah memperbarui `row.bot_mode` dan tampilan
switch-nya, tapi variabel `on` tetap nilai lama. Klik kedua mengirim mode yang
sama persis, server menjawab "sudah OFF", switch dikembalikan — terlihat seperti
tombolnya macet. Baru pulih kalau tabel dirender ulang (ganti halaman, filter,
atau Segarkan), yang membuat gejalanya terlihat berubah-ubah.

**Perbaikan.** Status dibaca dari model **saat diklik**, lewat fungsi murni
`nextMode(row)` yang bisa diuji tersendiri.

**Dampak seandainya lolos ke produksi:** owner yang mengambil alih percakapan
tidak akan bisa mengembalikan bot ke mode otomatis dari dashboard — harus edit
spreadsheet manual. Untuk fitur yang jadi alasan utama dashboard ini dibuat,
ini fatal.

### Bug 2 — `bot_mode` berisi spasi dibaca berbeda dari bot 🟠

Ditemukan saat menulis test untuk bug 1. Kedua workflow bot memakai
`String(v).trim().toUpperCase() === 'OFF'`, tapi dashboard tidak mem-`trim`.
Sel berisi `" off "` (mudah terjadi kalau ada yang mengetik manual di
spreadsheet) akan **tampil menyala di dashboard padahal bot sudah berhenti
membalas** — owner melihat satu hal, customer mengalami hal lain.

Ada di tiga tempat dengan tiga salinan logika: `toggleSwitch`, `filterLeads`,
dan `setSwitch`. Ketiganya disatukan ke satu fungsi `isBotOn()`, dan diuji
untuk `'OFF'`, `' off '`, `'off'`, `''`, `' '`.

### Bug 3 — header & banner tidak menempel, lalu saling menimpa 🟡

`html, body { overflow-x: hidden }` mengubah html/body menjadi scroll container,
dan itu **mematikan `position: sticky`** untuk seluruh turunannya. Akibatnya
header (berisi pemilih klien, Segarkan, Keluar) dan banner mode-uji ikut
tergulung hilang saat halaman digulir, padahal keduanya jelas dirancang menetap.

Properti itu juga tidak menahan apa pun: satu-satunya elemen yang lebih lebar
dari layar adalah tabel, dan itu sudah ditahan `.table-wrap { overflow-x: auto }`.
Terverifikasi — tanpa properti itu, `document.scrollWidth` di 375px tetap 375.

Menghapusnya memunculkan masalah kedua yang selama ini tersembunyi:
`body.has-test-banner .app-header { top: 36px }` mematok tinggi banner, padahal
teks banner membungkus jadi **91px di layar 375px** → header menimpa banner
sejauh 55px. Diperbaiki dengan mengukur tinggi banner saat runtime
(`--test-banner-h`, diperbarui juga saat resize).

### Kenapa bug 1 lolos dari ronde 1 — dan apa yang berubah

QA ronde 1 punya lubang struktural: **tidak ada lapis yang menguji DOM dan event
listener.** `selftest.html` menguji fungsi murni (`filterLeads`, `kpiValue`,
dst) dan E2E menguji API — tapi `toggleSwitch()` adalah pembangun DOM yang
memasang event listener, dan tidak ada satu pun test yang mengklik sesuatu dua
kali berturut-turut.

Sweep UI manual ronde 1 juga hanya menguji **satu arah** toggle. Skrip yang
seharusnya menguji arah balik tersendat (timer di-throttle saat pane browser
tersembunyi) dan saya melaporkannya sebagai terverifikasi tanpa hasilnya benar-
benar muncul. Itu kesalahan pelaporan, bukan hanya kelalaian cakupan.

**Yang ditambahkan:** `qa/uitest.html` — 94 pemeriksaan yang membangun DOM asli
lalu mengirim event klik sungguhan. Kelompok pertamanya khusus regresi ini:
lima klik berturut-turut harus menghasilkan `OFF, ON, OFF, ON, OFF`, termasuk
skenario dibatalkan dan skenario server menolak.

---

## 2. Apa yang benar-benar diuji, dan apa yang tidak

Ini bagian terpenting dari laporan ini. Angka "0 gagal" hanya berarti sesuatu
kalau jelas apa yang ada di dalam cakupan.

### Diuji terhadap kode produksi yang sesungguhnya
- **`n8n/src/build-payload.js`** — normalizer yang di-inline ke Code node n8n.
  `selftest.html` memuat file yang sama persis, bukan salinan.
- **`n8n/src/auth.js`** — token & klaim. Tanda tangan HMAC-SHA256 dihitung dengan
  `crypto.subtle` memakai secret yang dibaca langsung dari `build_workflow.py`.
- **`n8n/src/tenants.js`** — registry tenant & akun.
- **`app/js/*.js`** — file frontend yang persis akan di-deploy, disajikan apa
  adanya oleh `qa/serve.py`. Tidak ada versi khusus test.

### Data uji
Sintetis, tapi **nama kolomnya dibaca langsung dari `The_Scholars_Database.xlsx`
dan `PCR_Database.xlsx` produksi** (`qa/make_fixtures.py`). Jadi kalau ada kolom
yang di produksi ditulis dengan trailing space, test memakai bentuk yang sama.
Tidak ada satu pun nomor WhatsApp atau nama asli yang dipakai.

Kasus tepi yang sengaja ditanam dan harus ditangani:
identitas hanya LID, LID tersimpan di kolom `No WA`, `bot_mode` huruf kecil,
`bot_mode` kosong, tanggal `31/13/2026`, jam `25:00:00`, `Counter` berformat
`1.234`, baris kosong total, lead berumur 200 hari, `EVENTS.ts` bercampur
satuan detik & milidetik.

### TIDAK diuji (jujur, ini yang tersisa untuk verifikasi di produksi)
1. **Eksekusi workflow n8n yang sebenarnya.** Tidak ada instance n8n di mesin
   ini. Logika Code node diuji sebagai JavaScript murni; yang belum terbukti
   adalah perilaku *node*-nya: node Crypto, Switch, `Loop Over Tabs`, dan
   ekspresi `documentId` dinamis. **Wajib dilakukan smoke test setelah import** —
   lihat §6.
2. **Kuota & latensi Google Sheets sungguhan.** Cache 60 detik diuji sebagai
   logika, bukan terhadap kuota nyata.
3. **Tampilan visual.** Browser pane tidak meng-compose frame di sesi ini
   ("Screenshot timed out... pane is not displayed"), jadi **tidak ada satu pun
   screenshot yang diambil**. Verifikasi UI dilakukan lewat pembacaan DOM,
   console, network, dan geometri elemen — bukan lewat mata. Layout dan estetika
   perlu dilihat sendiri sekali sebelum dibagikan ke owner.
4. **Perangkat nyata.** Responsif diverifikasi lewat geometri pada viewport
   375px, bukan di HP fisik.

---

## 3. Gerbang statis — 24 pemeriksaan

Semua LOLOS. Yang paling berarti:

| Pemeriksaan | Kenapa ada |
|---|---|
| semua node terjangkau dari Webhook | node yatim = cabang yang diam-diam tidak pernah jalan |
| tidak ada cabang buntu | setiap jalur harus berujung di `Respond`; kalau tidak, request menggantung sampai timeout |
| output Switch/IF tersambung lengkap | output yang lupa disambung = permintaan hilang tanpa jejak |
| kurung seimbang di semua Code node | mendeteksi kode terpotong saat perakitan |
| referensi `$('Node')` valid | salah ketik nama node baru meledak saat runtime |
| workflow sinkron dengan `src/*.js` | mencegah workflow tertinggal setelah src diedit |
| tidak ada rahasia pihak ketiga di workflow | private key Google / secret Kirimi / kunci Anthropic |
| password plaintext tidak bocor ke workflow/app | file kredensial tidak boleh menular ke folder yang di-deploy |
| CORS tidak pernah `*` | wildcard = halaman mana pun bisa memakai token curian |
| tab CONFIG tidak pernah dibaca | CONFIG Persada memuat private key service account (lihat konsultasi T1) |
| frontend tidak hardcode klien/skema | pembuktian requirement "UI generik" |
| tidak ada dependensi eksternal di frontend | tidak ada CDN yang bisa mati atau berubah |
| eksekusi sukses tidak disimpan | body login memuat password plaintext |

Satu bug ditemukan **di validator sendiri** selama pengerjaan: pemindai
kurungnya salah membaca regex `/\//g` sebagai awal komentar `//`, sehingga
melaporkan 4 Code node rusak padahal tidak. Sudah diperbaiki (penanganan regex
literal + penomoran baris yang benar).

---

## 4. Unit — 183 pemeriksaan

**Parsing nilai sel (34).** Tanggal en-GB/ISO/epoch detik/epoch milidetik,
penolakan bulan 13 dan jam 25, `bot_mode` kosong = aktif (sesuai logika kedua
workflow, yang menguji `!== "OFF"`), `Counter` "1.234" → 1234, pembacaan kolom
ber-trailing-space, pembuangan baris kosong, distribusi multi-value.

**Normalisasi payload (62).** Untuk **kedua** tenant: konsistensi
`bot_on + bot_off = total lead`, tren harian tepat 90 titik, chart jam 24 batang,
KPI `rangeAware` monoton naik 7 ≤ 30 ≤ 90, dan — yang paling penting —
**spreadsheet ID tidak pernah ikut di payload**.

Inti requirement "UI sama untuk produk berbeda" diuji eksplisit:
- 7 KPI universal ada di kedua tenant
- 3 chart universal ada di kedua tenant
- bentuk top-level payload identik
- kunci kolom lead identik, **label berbeda** (dipastikan berbeda, bukan
  disamakan paksa)
- semua `type` kolom berasal dari kosakata yang dikenal frontend

**Kasus tepi (12).** Lead tanpa `No WA` tetap muncul lewat `lid`; nomor ≥15 digit
ditandai LID; tanggal tak valid jadi string kosong (bukan `NaN` atau `Invalid
Date` yang bocor ke layar); lead di luar 90 hari tidak dihitung sebagai lead
baru; `EVENTS.ts` bercampur satuan dinormalisasi ke tanggal.

**Token & isolasi tenant (61).** Detail di §5.

**Konfigurasi tenant (14).** Tidak ada tenant yang membaca CONFIG; tiap tenant
menunjuk spreadsheet berbeda; jumlah kolom lead sama di semua tenant.

Dua kegagalan awal ternyata **spesifikasi saya yang kurang tepat**, bukan bug:
`niceScale` mengembalikan `{max, step, ticks}` dan `paginate` memakai halaman
1-based dengan metadata + penjepitan. Keduanya kontrak yang lebih baik daripada
yang saya tulis di brief; test yang disesuaikan, bukan kodenya.

---

## 5. Isolasi tenant — pembuktian requirement #1

Ini kelompok test yang paling penting. Diuji di dua lapis: fungsi murni
(`selftest.html`) dan API end-to-end.

| Skenario | Hasil |
|---|---|
| owner The Scholars login | hanya melihat The Scholars |
| owner Persada login | hanya melihat Persada |
| owner A minta pindah ke tenant B | `TENANT_FORBIDDEN` |
| owner B minta pindah ke tenant A | `TENANT_FORBIDDEN` |
| **tenant di dalam token diganti** ke tenant lain | `TOKEN_BAD_SIGNATURE` |
| **role dinaikkan** jadi `super` di dalam token | `TOKEN_BAD_SIGNATURE` |
| **masa berlaku diperpanjang** di dalam token | `TOKEN_BAD_SIGNATURE` |
| token ditandatangani ulang dengan tenant asing | `TENANT_FORBIDDEN` (registry server menolak, bukan hanya tanda tangan) |
| token kedaluwarsa | `TOKEN_EXPIRED` |
| token kosong / acak / tanpa tanda tangan / tanda tangan pendek | ditolak, 4 bentuk |
| tanpa token | `TOKEN_MISSING` |
| owner A men-toggle nomor milik tenant B | `ROW_NOT_FOUND`, dan status nomor itu **terbukti tidak berubah** |
| spreadsheet ID di respons | tidak pernah ada |
| nomor tenant A vs B | tidak beririsan (fixture sengaja dipisah rentangnya) |

Lapis pertahanannya dua, sengaja:
1. **Tanda tangan** — klaim tidak bisa diubah tanpa terdeteksi.
2. **Registry server** — sekalipun tanda tangan sah, hak akses diperiksa ulang
   ke `VIRA_USERS` pada **setiap** request. Artinya mencabut akses seseorang
   berlaku langsung, tanpa menunggu token kedaluwarsa.

Satu cacat fixture ditemukan dan diperbaiki di tengah pengujian: semula kedua
tenant memakai rentang nomor yang sama, sehingga uji "toggle nomor tenant lain"
kebetulan lolos karena nomornya memang ada di kedua sisi — bukan karena
pengamanannya bekerja. Rentang dipisah (`62812…` vs `62813…`), test diulang.

---

## 6. Integrasi API — 36 pemeriksaan

Dijalankan terhadap `qa/serve.py`, yang menandatangani token dengan **format,
secret, dan daftar akun yang sama** dengan workflow n8n (dibaca langsung dari
`n8n/src/` dan `build_workflow.py`). Payload `stats` yang disajikan adalah
**keluaran asli `build-payload.js`**, bukan tiruan Python — `selftest.html`
menghitungnya lalu menyimpannya lewat `/_save/`. Jadi tidak ada dua implementasi
normalizer yang bisa menyimpang.

Mencakup: login benar/salah, tanpa enumerasi akun (username tak dikenal dan
password salah memberi pesan identik), penguncian setelah 5 kegagalan, `me`,
`switch_tenant`, `stats`, `toggle_user` (berhasil, bertahan, dikembalikan,
nomor asing ditolak, mode tidak valid ditolak), action tak dikenal ditolak, dan
teks non-ASCII (em dash pada "Sam — The Scholars") utuh melewati token.

---

## 6b. DOM & event — 94 pemeriksaan (`qa/uitest.html`)

Lapis yang tidak ada di ronde 1. Membangun elemen sungguhan lalu mengirim
`MouseEvent('click')` — bukan memanggil fungsi handler langsung.

- **Regresi toggle (22 pemeriksaan).** Lima klik berturut-turut →
  `OFF, ON, OFF, ON, OFF`; baris yang datang dalam keadaan OFF meminta ON
  duluan; `bot_mode` kosong dianggap aktif; switch terkunci mengabaikan klik;
  klik switch tidak ikut membuka drawer baris; setelah **dibatalkan** arah
  permintaan tetap sama; setelah **server menolak** dan status di-rollback,
  arah permintaan juga tetap sama.
- **Kesepakatan tiga pembaca `bot_mode` (15).** `toggleSwitch`, `filterLeads`,
  dan `setSwitch` harus sepakat untuk `'OFF'`, `' off '`, `'off'`, `''`, `' '`.
- **Sel tabel (14).** Tiap tipe (`text/int/date/wa/badge/toggle`), sel kosong
  jadi `—`, badge LID, dan **XSS**: `<img src=x onerror=...>` dari data tampil
  sebagai teks, nol elemen terbentuk — diuji juga untuk badge dan detail.
- **Tabel lead (8).** Label kolom ikut deskriptor server, klik header memicu
  urut kolom yang benar, penanda arah urut hanya di kolom aktif, klik baris
  membuka baris yang benar, tabel kosong tetap menampilkan sesuatu.
- **Tabel tambahan, detail, KPI (20).** Empty state memakai teks dari server;
  lead tanpa `detail` tidak menghasilkan drawer kosong; KPI `rangeAware`
  menampilkan nilai rentang aktif (diperiksa lewat isi `.metric-val`, bukan
  regex pada seluruh teks kartu).
- **Chart (15).** Satu kartu per chart, SVG tergambar untuk data berisi, chart
  bernilai nol tetap menampilkan sesuatu, `niceScale`/`donutArcs`/`linePath`.

---

## 7. Perilaku aplikasi — 70 hal yang diverifikasi langsung di browser

1. Login dengan password salah → pesan error, **tidak ada token tersimpan**
2. Login benar → dashboard terisi, token tersimpan
3. 9 KPI, 5 chart SVG, 98 baris tabel ter-render (The Scholars)
4. **Ganti rentang 30→90 hari: 0 request ke server**, angka tetap berubah
5. Pemilih tenant hanya tampil untuk akun `super`
6. Pindah tenant → nama klien, aksen warna, label kolom, dan judul chart berubah
7. **3 chart universal tetap berjudul sama** di kedua tenant (Tren Harian, Jam
   Chat Tersibuk, Status Bot); chart spesifik produk berbeda (Minat Program /
   Distribusi Kelas ↔ Unit Diminati / Sumber Traffic)
8. **Jumlah kolom tabel lead sama (7)** di kedua tenant; kolom 1,2,5,6,7 identik
   labelnya, kolom 3 & 4 berbeda mengikuti produk
9. Toggle **meminta konfirmasi lebih dulu** — modal menyebut akibatnya ("Bot akan
   berhenti membalas otomatis. Percakapan harus dilanjutkan manual.") beserta
   nama dan nomor lead
10. Sebelum dikonfirmasi, status **belum berubah**
11. Batal → tidak ada perubahan sama sekali
12. Konfirmasi → status berubah, modal tertutup
13. Perubahan **bertahan**: login baru + `stats` baru menunjukkan `bot_mode: OFF`
14. Tombol Segarkan tidak merusak tampilan

**Sapu lengkap ronde 2** (dijalankan pada demo, yang memakai kode `app/` apa
adanya), semuanya lolos:

| Kelompok | Yang diperiksa |
|---|---|
| Toggle (A, F) | tiga klik berselang-seling `OFF/ON/OFF` dengan request yang benar; juga di halaman 2 |
| Pencarian (B) | nama, nomor lengkap, nomor gaya lokal `0812…` menemukan `62812…`, keadaan kosong, dibersihkan, **tanpa panggilan server** (input di-debounce) |
| Filter bot (C) | "Bot aktif" hanya menampilkan yang menyala, "Manual" hanya yang mati, kembali ke "Semua" pulih, tanpa panggilan server |
| Urut kolom (D) | kolom angka & teks, klik kedua membalik arah, tanpa panggilan server |
| Paginasi (E) | 50/halaman, `Baris 51–63 dari 63 · halaman 2/2`, tombol batas ter-disable, tanpa panggilan server |
| Drawer (G) | terbuka dari klik baris, punya judul & isi, ditutup tombol dan tombol Escape |
| Rentang (H) | 7/30/90 mengubah KPI dan memendekkan garis tren, **nol request** |
| Ganti klien (I) | pencarian, filter, dan halaman ter-reset; hanya `switch_tenant` + `stats` yang dipanggil; label kolom berganti |
| Segarkan (J) | memanggil `stats`, tampilan tetap utuh |
| Keluar (K) | kembali ke layar masuk, token terhapus, tanpa panggilan server |
| Password salah (L) | pesan error tampil, tetap di layar masuk, tidak ada token tersimpan |
| Mobile 375px (M, N) | tanpa scroll horizontal halaman, KPI 2 kolom, tabel scroll di wadahnya sendiri, banner & header menetap dan **tidak saling menimpa**, tombol header tetap terjangkau |
| Desktop (O) | header tidak menimpa banner, tanpa scroll horizontal, dan dalam mode produksi (tanpa banner) header menempel di paling atas |

**Catatan soal ukuran target sentuh.** Pengukuran `getBoundingClientRect()`
melaporkan switch hanya 28px — itu **positif palsu**. Area sentuhnya diperluas
lewat `::after { inset: -8px }` tanpa mengubah ukuran visual. Diukur dengan cara
yang benar (`elementFromPoint` menyapu ke segala arah dari titik tengah), area
sentuh sebenarnya **44 × 62 px**. Tombol banner mode-uji tadinya 30px dan
kini diberi perlakuan sama.

Verifikasi tambahan oleh subagent frontend terhadap mock-nya sendiri (dua tenant
fiktif berskema berbeda): console bersih nol pesan, tooltip di ketiga tipe chart,
service worker hanya menyimpan 11 aset statis tanpa satu pun entri `/api/`, dan
payload berisi `<img src=x onerror=alert(1)>` tampil sebagai teks biasa (0 elemen
`img` terbentuk).

---

## 8. Smoke test WAJIB setelah import ke n8n

Karena §2 butir 1, empat hal ini belum pernah dijalankan di n8n sungguhan dan
harus dicek sebelum dipakai owner:

- [ ] **Node Crypto** — login mengembalikan token berbentuk `<base64url>.<64 hex>`.
      Kalau tanda tangan kosong/berbeda panjang, `encoding: hex` pada node Crypto
      tidak terpasang benar.
- [ ] **`Loop Over Tabs`** — panggil `stats`, pastikan `leads.rows` terisi **dan**
      `tables` berisi semua tab. Kalau ada tabel kosong padahal sheetnya berisi,
      periksa nama tab di `VIRA_TENANTS[...].tabs` (peka huruf besar-kecil).
- [ ] **`documentId` dinamis** — pastikan node Sheets menerima ekspresi
      `{{ $json.doc_id }}`. Kalau n8n menolak, ganti mode Resource Locator ke
      "By ID" dan pastikan nilainya diawali `=`.
- [ ] **Toggle menulis ke baris yang benar** — matikan bot untuk satu nomor uji,
      lalu **buka spreadsheet** dan pastikan yang berubah adalah barisnya, bukan
      baris lain. Ini pemeriksaan paling penting: salah baris berarti bot mati
      untuk customer yang salah.

Ditambah satu pemeriksaan integrasi:

- [ ] Setelah `bot_mode` diubah ke OFF lewat dashboard, kirim pesan WhatsApp dari
      nomor itu dan pastikan **bot benar-benar diam**. Ini menguji bahwa nilai
      `"OFF"` yang ditulis dashboard dibaca sama oleh workflow bot.

---

## 9. Batas yang diketahui

- **`Counter` adalah perkiraan, bukan hitungan eksak.** Bot menaikkannya tanpa
  penguncian, jadi dua pesan bersamaan bisa menghilangkan satu increment. Sudah
  didokumentasikan di `hint` KPI "Total Chat" supaya owner tidak salah baca.
- **KPI GForm/Survey mengukur *pengiriman*, bukan *pengisian*.** Kolom
  `gform_filled` tidak pernah ditulis oleh workflow mana pun, jadi tidak ada
  metrik konversi yang jujur untuk itu — sengaja tidak ditampilkan daripada
  menampilkan 0% yang menyesatkan.
- **Penguncian login berbasis workflow static data.** Dua percobaan yang
  benar-benar bersamaan bisa saling menimpa hitungannya. Ini memperlambat brute
  force, bukan mencegahnya mutlak; pertahanan utamanya tetap password 16
  karakter acak.
- **Cache stats disimpan di static data n8n.** Payload besar (ratusan lead)
  ikut ditulis ke database n8n setiap kali menyegar. Ada batas atas 1,5 MB —
  di atas itu cache dilewati dan dicatat di log, bukan diam-diam gagal.
