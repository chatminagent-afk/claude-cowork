# Kontrak API — VIRA Dashboard

Versi 1.0 · 2026-07-28 · **Sumber kebenaran** untuk frontend, workflow n8n, dan mock server QA.
Kalau tiga pihak itu berbeda, file ini yang menang.

---

## 1. Transport

Satu endpoint, satu method.

```
POST  https://n8n.srv1270416.hstgr.cloud/webhook/vira-dash
Content-Type: text/plain;charset=UTF-8
Body: JSON string
```

**Kenapa `text/plain` dan bukan `application/json`:** `text/plain` termasuk *CORS simple request*, jadi browser tidak mengirim preflight `OPTIONS`. n8n Webhook node tidak menangani OPTIONS tanpa node tambahan; menghindarinya menghilangkan satu kelas kegagalan yang sulit didiagnosis. Body tetap JSON, di-`JSON.parse` di sisi server.

**Kenapa token di body dan bukan header `Authorization`:** header kustom akan memicu preflight, membatalkan keuntungan di atas.

Respons selalu `HTTP 200` dengan header:

```
Content-Type: application/json
Access-Control-Allow-Origin: <origin pemanggil, jika ada di allowlist>
Vary: Origin
```

Status error dibawa di dalam body (`ok:false` + `error`), bukan di HTTP status — supaya `fetch()` tidak perlu membedakan kegagalan jaringan dari penolakan aplikasi.

---

## 2. Bentuk request

```jsonc
{
  "action": "login | me | switch_tenant | stats | toggle_user",
  "token":  "<payload>.<sig>",   // wajib untuk semua action kecuali `login`
  ...field spesifik action
}
```

### `login`
```jsonc
{ "action":"login", "username":"sam", "password":"..." }
```

### `me`
Validasi token & kembalikan identitas. Dipakai saat halaman dibuka ulang.
```jsonc
{ "action":"me", "token":"..." }
```

### `switch_tenant` — hanya role `super`
```jsonc
{ "action":"switch_tenant", "token":"...", "tenant":"persada" }
```
Menerbitkan token BARU untuk tenant target. Token lama tetap berlaku sampai `exp`.

### `stats`
```jsonc
{ "action":"stats", "token":"...", "fresh":false }
```
`fresh:true` melewati cache server (dipakai tombol Refresh manual). Tetap dibatasi:
kalau cache baru dibuat <10 detik lalu, `fresh` diabaikan agar tidak jadi celah
menguras kuota Google Sheets.

### `toggle_user`
```jsonc
{ "action":"toggle_user", "token":"...", "key":"6281234567890", "mode":"ON" }
```
- `key` = nilai kolom `No WA` persis seperti yang dikirim server di `leads.rows[].key`.
  Server **tidak** menerima nomor sembarangan: kalau `key` tidak ketemu di STATS
  tenant tersebut, request ditolak `ROW_NOT_FOUND`.
- `mode` ∈ `"ON" | "OFF"` (huruf besar).

### `add_lead`
```jsonc
{ "action":"add_lead", "token":"...", "key":"081234567890",
  "nama":"Budi", "mode":"OFF" }
```
- `key` = nomor apa adanya dari isian pengguna. **Server yang menormalkan**,
  bukan client: `08…` dan `8…` menjadi `62…`, awalan `00` dibuang, non-digit
  dibuang. Nomor yang tidak masuk akal ditolak `BAD_NUMBER` — tidak pernah
  ditebak.
- `nama` opsional. Kosong berarti kolom `Nama` diisi nomornya sendiri.
  Maksimal 80 karakter.
- `mode` ∈ `"ON" | "OFF"`.

Server menolak sebelum menulis kalau: nomornya sudah ada (`DUPLICATE`, dicek
lewat `No WA` lalu `lid`, tidak pernah jatuh ke baris pertama), tab STATS tidak
terbaca (`SHEET_UNREADABLE`), atau header sheet tidak memuat persis keempat
kolom yang ditulis (`SHEET_SCHEMA`).

Kolom yang ditulis hanya empat: `No WA`, `Nama`, `bot_mode`, `Counter` (=0).
`Tanggal Chat Pertama` sengaja dibiarkan kosong — lead ini belum pernah chat.

> **Peringatan operasional.** Menambah lead dengan `mode:"ON"` membuat nomor itu
> masuk jangkauan workflow follow-up otomatis, yang bisa mengirim WhatsApp lebih
> dulu ke orang yang belum pernah menghubungi. Karena itu form di frontend
> default-nya `OFF` dan menampilkan peringatan saat digeser ke `ON`.

---

## 3. Bentuk respons

### Sukses `login` / `me` / `switch_tenant`
```jsonc
{
  "ok": true,
  "action": "login",
  "token": "<payload>.<sig>",         // tidak dikirim pada `me`
  "session": {
    "username": "sam",
    "display":  "Sam — The Scholars",
    "role":     "owner",              // "owner" | "super"
    "tenant":   "thescholars",        // tenant aktif
    "tenants":  [ {"id":"thescholars","name":"The Scholars"} ],
    "exp":      1785000000            // epoch detik
  }
}
```
`session.tenants` hanya berisi tenant yang boleh diakses akun itu. Frontend
menampilkan pemilih tenant hanya kalau panjangnya > 1.

### Sukses `stats`
```jsonc
{
  "ok": true,
  "action": "stats",
  "tenant": { "id":"persada", "name":"Persada Cisoka Residence",
              "product":"VIRA-PCR — Telemarketer WhatsApp", "accent":"blue",
              "logo":"" },
  "generated_at": 1785000000000,      // epoch ms, waktu data ditarik dari Sheets
  "cached": true,                     // true = dilayani dari cache 60 detik
  "kpis":   [ KPI, ... ],
  "charts": [ Chart, ... ],
  "leads":  { "title":"Direktori Lead", "columns":[Column,...], "rows":[Lead,...] },
  "tables": [ Table, ... ],
  "insights": [ Insight, ... ]        // OPSIONAL — lihat di bawah
}
```

**`session` tidak ikut di respons `stats`** — frontend sudah memegangnya dari login.

#### `tenant.logo`
Path berkas logo **relatif terhadap `index.html` dashboard**, mis.
`"icons/thescholars.jpg"`. String kosong (atau field-nya tidak ada) berarti
header memakai emblem huruf awal nama tenant.

Field ini ada supaya frontend tidak perlu tahu klien mana yang punya logo;
sebelumnya pemetaannya hidup di `app/js/config.js`, sehingga menambah klien
ketiga menuntut perubahan kode frontend. Sekarang cukup satu entri `logo:` di
`n8n/src/tenants.js` plus berkas gambarnya di folder `icons/`.

Frontend **menolak** nilai yang bukan path relatif se-origin — URL absolut,
path berawalan `/`, `//`, `..`, atau apa pun yang memuat skema (`https:`,
`data:`, `javascript:`) diperlakukan sebagai "tidak ada logo". Jadi field ini
tidak bisa dipakai untuk menarik aset dari host luar.

#### KPI
```jsonc
{
  "id":"new_leads", "label":"Lead Baru",
  "tone":"blue|green|teal|purple|orange|red",
  "value": 12,
  "sub":   "47% dari total",          // opsional, teks kecil di bawah angka
  "hint":  "Lead dengan tanggal chat pertama di dalam rentang",  // tooltip
  "rangeAware": true,                 // opsional
  "values": { "7":3, "30":12, "90":31 }   // ada jika rangeAware
}
```
Kalau `rangeAware`, frontend menampilkan `values[rentangAktif]`, bukan `value`.
`value` adalah fallback (rentang 30 hari) untuk klien yang tidak paham rentang.

Kunci di `values` **selalu string** (`"7"`, `"30"`, `"90"`) — bukan angka.
Frontend mengonversi rentang aktif ke string sebelum melakukan lookup.

#### Chart
```jsonc
{
  "id":"daily", "type":"line|bar|doughnut", "title":"Tren Harian",
  "labels": ["2026-05-01", ...],
  "series": [ { "name":"Lead baru", "data":[0,1,...],
                "color":"blue" | ["green","orange"] | "palette" } ],
  "rangeAware": true,   // opsional: labels/data dipotong N terakhir oleh frontend
  "note": "...",        // opsional, keterangan kecil di bawah chart
  "empty": false        // opsional, true = tampilkan empty state
}
```
`color:"palette"` = frontend memakai palet kategorikal bawaannya.

**`rangeAware` pada chart berarti 1 titik = 1 hari.** Frontend memotong N titik
terakhir, dengan N = jumlah hari rentang aktif. Chart dengan granularitas lain
(mingguan, per jam) **tidak boleh** ditandai `rangeAware` — pemotongannya akan
salah. Saat ini hanya `daily` yang memakainya.

#### Column
```jsonc
{ "key":"segment", "label":"Unit Diminati",
  "type":"text|int|date|wa|badge|toggle" }
```
`type` menentukan cara render, **bukan** isi. Label boleh berbeda antar tenant —
itulah cara satu UI melayani dua produk.

#### Lead (baris `leads.rows`)
```jsonc
{
  "key":"6281234567890",     // dipakai apa adanya untuk toggle_user
  "wa":"6281234567890",
  "lid":"123456789012345",
  "is_lid": false,           // true = identitas LID, nomor asli tidak diketahui
  "nama":"...", "segment":"...", "stage":"...",
  "counter": 14,
  "first_chat":"2026-06-02", "last_chat":"2026-07-21",   // "" kalau tak terbaca
  "bot_mode":"ON",
  "detail":[ {"label":"Sumber Traffic","value":"Instagram"}, ... ]
}
```
`detail` hanya memuat field yang **tidak kosong**, jadi lead yang baru masuk
bisa punya `detail: []`. Frontend wajib menangani ini dengan empty state, bukan
drawer kosong. `key` dijamin unik dalam satu tenant — server menolak toggle
dengan `ROW_NOT_FOUND` kalau tidak ada padanannya.

#### Table
```jsonc
{
  "id":"survey", "title":"Jadwal Survey",
  "empty":"Belum ada survey terjadwal.",
  "total": 43, "truncated": false,
  "columns":[ {"key":"tanggal","label":"Tanggal","type":"text"}, ... ],
  "rows":[ { "tanggal":"...", ... } ]     // key = Column.key
}
```
Kolom tabel tambahan terbatas pada `text | int | date | wa | badge`.
**`toggle` tidak berlaku di sini** — hanya tabel `leads` yang punya kontrol
bot_mode, karena hanya baris lead yang punya `key` untuk ditargetkan.

#### Insight (rekomendasi AI) — opsional
```jsonc
{
  "id":"ai_insight",
  "title":"Rekomendasi dari Topik — Agustus 2026",
  "hint":"Disusun otomatis oleh AI dari kartu topik bulan itu… Ini SARAN, bukan fakta.",
  "generated_at": 1785000000000,
  "model":"claude-sonnet-5",
  "items":[
    { "judul":"Buka kelas IELTS batch baru",
      "alasan":"IELTS jadi topik terbesar bulan ini.",
      "aksi":"Umumkan jadwal kelas IELTS ke lead yang menanyakannya.",
      "dampak":"tinggi",                      // tinggi | sedang | rendah
      "dasar":["IELTS: 34 user","22% dari total user"] }
  ]
}
```

**Kunci `insights` boleh tidak ada sama sekali**, dan frontend harus
memperlakukan itu sebagai keadaan normal: tidak ada kartu, tidak ada kotak
"belum ada data". Kunci ini hilang kalau ringkasan bulanan belum terisi, kalau
panggilan AI gagal, atau kalau balasannya tidak sesuai bentuk. Blok setengah
jadi tidak pernah dikirim — lebih baik hilang daripada terbaca sebagai saran
utuh padahal terpotong.

Maksimal 4 butir. Setiap butir wajib punya `judul` dan `aksi`; butir tanpa
salah satunya dibuang server. `dasar` selalu array (boleh kosong).

**Dari mana asalnya.** Dashboard **tidak pernah memanggil AI**. Blok ini dibaca
apa adanya dari kolom `ai_insight_json` di tab `MONTHLY_SUMMARY`, yang diisi
WF-B (Monthly Rollup) sekali sebulan. Bentuk isi selnya:

```jsonc
{"model":"claude-sonnet-4-6","generated_at":1756000000000,
 "items":[{"judul":"…","alasan":"…","aksi":"…","dampak":"tinggi","dasar":["…"]}]}
```

Array telanjang (`[{…}]`) juga diterima, supaya sel yang diisi tangan tetap
terbaca.

**Kenapa dibaca, bukan dihitung.** Versi pertama fitur ini memanggil Anthropic
di dalam jalur permintaan `stats`. Panggilan LLM melampaui batas tunggu
frontend (25 detik) dan **halaman gagal dimuat** — bukan sekadar kartunya
hilang. Dengan membaca kolom, tidak ada lagi jalan bagi kegagalan atau
kelambatan AI untuk menyentuh pemuatan dashboard. Sekaligus: "satu panggilan
per tenant per bulan" jadi sifat bawaan jadwal cron WF-B, bukan sesuatu yang
perlu dijaga dengan cache.

### Sukses `add_lead`
```jsonc
{ "ok":true, "action":"add_lead", "key":"6281234567890", "bot_mode":"OFF",
  "row": Lead,
  "message":"Nomor 6281234567890 ditambahkan dengan bot OFF. VIRA belum akan membalas nomor ini." }
```
`row` berbentuk **persis** seperti elemen `leads.rows` (dibangun lewat jalur
yang sama), supaya frontend bisa menyisipkannya ke tabel tanpa memanggil
`stats` ulang — kuota Google Sheets dipakai bersama bot produksi. Cache stats
tenant itu ikut dikosongkan.

### Sukses `toggle_user`
```jsonc
{ "ok":true, "action":"toggle_user", "key":"628...", "bot_mode":"OFF",
  "message":"Bot dimatikan untuk 628…. Percakapan sekarang dipegang manual." }
```
Server juga mengosongkan cache stats tenant itu, sehingga refresh berikutnya
menampilkan status baru.

---

## 4. Bentuk error

```jsonc
{ "ok":false, "action":"stats", "error":"TOKEN_EXPIRED",
  "message":"Sesi sudah berakhir. Silakan login ulang." }
```

| `error` | Arti | Aksi frontend |
|---|---|---|
| `BAD_REQUEST` | body bukan JSON / action tidak dikenal | tampilkan pesan |
| `BAD_CREDENTIALS` | username/password salah | tampilkan di form login |
| `LOCKED_OUT` | terlalu banyak percobaan gagal | tampilkan sisa waktu |
| `TOKEN_MISSING` / `TOKEN_MALFORMED` | token tidak ada / bentuk salah | logout |
| `TOKEN_BAD_SIGNATURE` | tanda tangan tidak cocok — **percobaan pemalsuan** | logout |
| `TOKEN_EXPIRED` | lewat `exp` | logout, minta login ulang |
| `TENANT_FORBIDDEN` | token menunjuk tenant yang bukan haknya | logout |
| `TENANT_UNKNOWN` | tenant tidak ada di registry | logout |
| `ROLE_CHANGED` | peran akun berubah sejak token terbit | logout |
| `ROW_NOT_FOUND` | `key` tidak ada di STATS tenant ini | tampilkan, refresh data |
| `SHEET_ERROR` | Google Sheets gagal dibaca/ditulis | tampilkan, tawarkan retry |
| `BAD_NUMBER` | `add_lead`: nomor tidak terbaca sebagai nomor WA | tampilkan, biarkan form terbuka |
| `DUPLICATE` | `add_lead`: nomor sudah ada (pesan menyebut pemiliknya) | tampilkan, biarkan form terbuka |
| `SHEET_UNREADABLE` | `add_lead`: tab STATS tidak terbaca — **tidak ada yang ditulis** | tampilkan, tawarkan retry |
| `SHEET_SCHEMA` | `add_lead`: header sheet tidak sesuai — **tidak ada yang ditulis** | tampilkan; perlu perbaikan sheet |
| `WRITE_FAILED` | `add_lead`: append gagal — **nomor BELUM tersimpan** | tampilkan, tawarkan retry |

`message` selalu Bahasa Indonesia dan aman ditampilkan ke owner. `error` adalah
kode stabil untuk logika frontend — jangan mencocokkan `message`.

---

## 5. Aturan keamanan yang mengikat implementasi

1. **Spreadsheet ID tidak pernah keluar dari n8n.** Tidak ada field respons yang
   memuatnya. Client hanya tahu `tenant.id`.
2. **Tenant diambil dari token, bukan dari body request.** Tidak ada action yang
   menerima parameter `tenant` selain `switch_tenant`, dan itu pun divalidasi
   terhadap `user.tenants` di registry server — bukan terhadap isi token.
3. **Tanda tangan diverifikasi setiap request.** Tidak ada jalur "percaya klaim
   karena sudah pernah login".
4. **Tab `CONFIG` tidak pernah dibaca.** Di Persada tab itu memuat private key
   service account Google dalam bentuk plaintext.
5. **CORS tidak pernah `*`.** Hanya origin di `VIRA_SETTINGS.corsOrigins`.
6. Nilai `bot_mode` yang ditulis hanya `"ON"` atau `"OFF"` — dua workflow
   produksi sama-sama menguji `!== "OFF"`, jadi ini kompatibel keduanya.
