# Plan Enhance VIRA Dashboard — Tambah Lead + Rekomendasi AI Topik

Tanggal: 2026-09-06
Basis kode: `VIRA Dashboard/2026-07-28-production/` (zip `app revamp.zip` == folder `app revamp/`, sudah diverifikasi identik)
Status: **menunggu approval Steven sebelum eksekusi**

---

## 0. Temuan yang menentukan bentuk pekerjaan

1. **Frontend sengaja buta.** `render.js:5-6` — tidak ada nama kolom, nama tenant, atau judul di JS.
   Semua label datang dari payload server. "Top Topic" bukan komponen khusus: itu `monthlySummary`
   (doughnut `topik_chart` + tabel `topik_table`) yang dibangun `vdBuildMonthly()`
   (`n8n/src/build-payload.js:362`) dari tab `MONTHLY_SUMMARY` kolom `top_json`.

2. **Satu-satunya write yang ada = `toggle_user`** (node `Update Bot Mode`, operation `update`,
   match `row_number`). Tidak ada append baris sama sekali di Dashboard API.
   Fitur tambah-lead = branch n8n baru dari nol.

3. **Tidak ada node AI di Dashboard API.** Klasifikasi topik dikerjakan WF-A (Topic Harvester)
   ke tab `TOPIC_LOG`, direkap WF-B (Monthly Rollup) ke `MONTHLY_SUMMARY.top_json`.
   File JSON WF-A/WF-B **tidak ada di folder lokal**, hanya hidup di n8n.

4. **Transport terkunci.** Satu webhook `POST /webhook/vira-dash`,
   `Content-Type: text/plain;charset=UTF-8`, token di **body** (bukan header), tanpa header custom —
   sengaja, supaya tetap CORS "simple request" dan tidak kena preflight OPTIONS yang tidak ditangani
   n8n (`config.js:36-40`). Semua penambahan wajib lewat `VDApi.call(action, body)`.

5. **Drift live vs lokal.** `live production/VIRA Dashboard API.json` = 2 tenant
   (thescholars, persada). Build lokal `n8n/VIRA-Dashboard-API.json` = 3 tenant (+ `personal`, 28 Agu).
   **Import build baru = sekalian menerbitkan tenant `personal` ke live.**

6. **Risiko WA keluar (sudah diputuskan, lihat K1).** Append baris ke `STATS` dengan `bot_mode = ON`
   bisa dijemput workflow Follow-up AI Powered dan di-WA duluan ke nomor yang belum pernah chat.
   Rem yang ada hanya `bot_mode=off` atau `survey_status=scheduled`; `followup_interval_hours`
   default 72 jam; `followup_max = 0` (tanpa batas).
   Sumber: `live production/2026-08-28-audit-workflow-produksi-n8n.md`.

---

## 1. Keputusan yang sudah diambil (2026-09-06)

| # | Topik | Keputusan |
|---|-------|-----------|
| K1 | Default `bot_mode` di form tambah lead | **OFF**, dan kalau digeser ke ON muncul teks peringatan bahwa VIRA bisa mengirim WA duluan ke nomor itu |
| K2 | Field form | **No WA + Nama + bot_mode**. Nama opsional; kalau kosong kolom Nama diisi nomornya sendiri |
| K3 | Notifikasi sukses | **Toast + baris baru di-highlight** beberapa detik di tabel |
| K4 | Lokasi komputasi rekomendasi AI | **Dashboard API + cache per-bulan** di workflow static data (kurang-lebih 1 panggilan LLM per tenant per bulan). WF-B tidak disentuh |

---

## PAKET A — Tambah Lead (nomor + bot_mode on/off)

### A1. Backend n8n

Semua perubahan di `n8n/build_workflow.py` dan `n8n/src/tenants.js`, lalu regenerate dengan
`python build_workflow.py`. Tidak ada node yang di-edit tangan di UI n8n.

| Langkah | Isi |
|---|---|
| A1.1 | Tambah `'add_lead'` ke array `AUTHED` (`build_workflow.py:147`) |
| A1.2 | Tambah output branch `add_lead` di switch `Route Authed` (`build_workflow.py:660`) |
| A1.3 | Node **`Prepare Add Lead`** (code). Validasi `mode` harus `ON`/`OFF`; normalisasi nomor (`08xx` jadi `628xx`, lewat `vdDigits`); tolak kosong / terlalu pendek; resolve `sheetId`/`statsTab` **dari klaim token** — client tidak pernah menyebut spreadsheet (pola sama dengan `Prepare Toggle`) |
| A1.4 | Node **`Read STATS for Add`** (Sheets read) lalu node **`Find Duplicate`** (code). Prinsip identitas sama dengan `Find Row`: **No WA primer, lid cadangan, tidak pernah jatuh ke `rows[0]`**. Nomor sudah ada berarti tolak `DUPLICATE` + sebut nama pemiliknya. Alasan: duplikat `No WA` membuat `Update Bot Mode` dan Follow-up (`matchingColumns: ["No WA"]`) jadi ambigu — risiko yang sudah di-flag audit |
| A1.5 | Node **`Append Lead`** (Sheets `operation: append`, `mappingMode: autoMapInputData`). Mapping harus dinamis karena nama kolom beda per tenant (`Nama` vs `nama_lengkap`), jadi `Find Duplicate` mengeluarkan objek yang **key-nya sudah nama kolom asli** hasil `profile.map`. Node hilir mengambil `_cors`/`_claims` lewat `$('Find Duplicate').first().json` — pola yang sudah dipakai `Append Audit` |
| A1.6 | Node **`Append Audit (Add)`** ke tab `DASH_AUDIT`, `from: '(baru)'`, `to: mode`. Header tab (`ts,actor,role,no_wa,from,to`) **tidak berubah** |
| A1.7 | Node **`Build Add Lead Response`** (code). Batalkan `statsCache[tenant]`; balikkan `{ok:true, action:'add_lead', key, bot_mode, row:{...}, message}`. `row` berisi baris siap-render supaya frontend tidak perlu refetch |
| A1.8 | `Append Lead` pakai `onError: continueErrorOutput`, cabang error diarahkan ke node respons gagal. **Bukan** `continueRegularOutput` — kalau append gagal tapi kita bilang "berhasil", itu lebih buruk daripada error mentah. Sekaligus menutup bug yang di-flag audit di `Update Bot Mode` (tanpa `onError`, eksekusi berhenti sebelum `Respond` dan request client menggantung sampai timeout) |
| A1.9 | Default kolom saat append: `bot_mode` dari form (default OFF per K1), `Counter` = 0, `Tanggal Chat Pertama` dikosongkan (lead ini belum pernah chat — jangan mengarang riwayat). Kolom lain dibiarkan kosong |

### A2. Frontend (`app revamp/`)

- **`index.html`** — tombol `+ Tambah` di `.table-toolbar` (baris 163-185). Ditaruh di situ karena
  toolbar berada di luar dua jalur render (`R.leadTable` desktop / `R.leadCards` di bawah 720px),
  jadi tampil identik di kedua mode. Plus markup drawer form baru, mencontoh `#viewPanel`
  (baris 241-253).
- **`app.js`** — `openAddLead()` / `submitAddLead()`, mencontoh persis pola `doToggle()`
  (`app.js:867-898`): disable kontrol, `api.call('add_lead', {...})`, `guard(res)`, sukses/gagal.
- **Validasi client**: digit-only, normalisasi `08` jadi `62`, panjang minimum, tombol submit
  disabled sampai valid. Validasi server tetap jalan; client-side hanya untuk kenyamanan.
- **Switch bot_mode di form**: `<button class="ios-switch" role="switch">` polos yang di-toggle
  sendiri (seperti `buildViewPanel()` di `app.js:933-946`) — **bukan** `R.toggleSwitch()`, karena
  itu terikat ke `row`/`handlers.onToggle` untuk baris yang sudah ada.
- **Peringatan K1**: teks peringatan muncul/hilang saat switch digeser ke ON.
- **Sukses** → `toast(res.message, 'ok')` + `state.stats.leads.rows.unshift(res.row)` +
  `paintLeads()` + highlight baris baru (K3). **Tidak** memanggil `loadStats()` — kuota Google
  Sheets dipakai bareng bot produksi (`app.js:8-11`).
- **CSS** (`css/app.css`) — pakai token yang ada (`.input`, `.field`, `.btn`, `.btn-block`,
  `.drawer`, `--radius-*`, `--accent`). Tambah keyframe highlight baris. Warna **wajib**
  didefinisikan di kedua blok tema (`css/app.css:6-7`).
- **`sw.js`** — naikkan `CACHE_VERSION` dari `v1.3.0` ke `v1.4.0`. Tanpa ini user PWA tetap dapat
  versi lama.

---

## PAKET B — Rekomendasi AI di Top Topic

### B1. Data masukan AI (tanpa baca sheet tambahan)

- `top_json`: `topic`, `users`, `pct`, `messages` + label rapi dari `profile.topicLabels`
- `coverage_note` + `bulan`
- Chart `hourly` (Jam Chat Tersibuk) dan `daily` (Tren Harian) yang sudah dihitung
- `distributions`: Minat Program, Distribusi Kelas
- KPI: `unanswered`, `bot_off`, `total_leads`
- **BARU — agregasi hari-dalam-seminggu**, diturunkan dari `Tanggal Chat Terakhir` di STATS
  (sumber yang sama dengan chart `daily`, jadi nol biaya baca tambahan).
  **Ini prasyarat untuk rekomendasi bertipe "buka kelas hari Rabu"** — datanya sekarang belum ada.

### B2. Node AI

- HTTP Request ke `api.anthropic.com` (pola yang sudah dipakai WF-A), model `claude-sonnet-5`.
- **Pakai credential n8n `httpHeaderAuth`, bukan header literal.** Audit sudah menandai WF-A soal
  API key literal — jangan mengulanginya di workflow baru.
- **Cache per-bulan** di `$getWorkflowStaticData('global').aiInsight[tenant]`, key = `bulan` +
  hash dari `top_json`. `MONTHLY_SUMMARY` hanya berubah sebulan sekali, jadi kurang-lebih
  1 panggilan LLM per tenant per bulan, bukan per refresh. Latency dan biaya praktis nol.
  Static data hilang saat re-import n8n — konsekuensinya cuma satu panggilan ekstra.
- `onError: continueRegularOutput` — blok ini non-kritis. Anthropic mati berarti `insights` hilang
  dari payload, kartunya sembunyi, sisa dashboard normal.
- **Prompt guardrail**: bahasa Indonesia; konteks konsultan pendidikan; dilarang mengarang angka;
  setiap rekomendasi wajib menyebut angka pendukung dari data yang diberikan; keluaran JSON ketat;
  jumlah rekomendasi 2-4.

### B3. Bentuk payload (blok generik baru, tetap tenant-agnostic)

```
insights: [{
  id, title, hint, generated_at, model,
  items: [{ judul, alasan, aksi, dampak: 'tinggi|sedang|rendah', dasar: [ ... ] }]
}]
```

### B4. Frontend

- Container `#insightsWrap` baru, tepat di bawah `#chartGrid` (jadi persis di bawah doughnut topik).
- Renderer generik `R.insightCard()` di `render.js` — **tanpa teks hardcoded**, semua dari payload,
  konsisten dengan aturan file itu.
- Ikut sistem fold/hide per-tenant (`vd.sections::<tenantId>`) seperti section lain.
- **Wajib ada label "dibuat AI" + bulan sumbernya**, supaya Sam tahu ini saran, bukan fakta.

---

## PAKET C — QA & Deploy

- `python qa/validate_workflow.py` — gate build, gagal kalau nama klien bocor ke `app/`
- `qa/selftest.html` + `qa/uitest.html` — tambah case `add_lead`: sukses / duplikat / nomor invalid /
  append gagal, lewat `window.__VD_MOCK__` (`api.js:104-115`)
- `python demo/build_demo.py` — rebuild `demo/VIRA-Dashboard-DEMO.html`
- Re-zip `app revamp.zip`
- Update `docs/2026-07-28-API-CONTRACT.md` (action `add_lead` + blok `insights`)
- Update `2026-08-26-runbook-deploy.md` (langkah deploy + smoke test baru)

### Deploy (manual, oleh Steven)

1. Import `n8n/VIRA-Dashboard-API.json` ke n8n project `sXUEZy1FQDksvKLg`, lalu aktifkan
   — **catatan: sekalian menerbitkan tenant `personal`** (temuan #5)
2. Buat credential n8n untuk Anthropic API key (httpHeaderAuth)
3. Upload isi `app revamp/` ke Cloudflare Worker `vira-dashboard.chatminagent.workers.dev`
4. Smoke test: tambah nomor dummy, cek baris muncul di STATS, toggle nomor itu, lalu hapus manual

---

## Di luar cakupan (tidak disentuh)

- WF-A Topic Harvester, WF-B Monthly Rollup, workflow bot utama, Follow-up AI Powered —
  semuanya di luar folder ini dan tidak ada file lokalnya
- Rotasi HMAC secret / private key Persada (dicatat audit sebagai open risk, bukan bagian
  pekerjaan ini)
- Pembersihan `pinData` berisi token sesi + nomor asli di `VIRA Dashboard API.json`
  (dicatat audit; layak dikerjakan terpisah sebelum file itu dibagikan lagi)
