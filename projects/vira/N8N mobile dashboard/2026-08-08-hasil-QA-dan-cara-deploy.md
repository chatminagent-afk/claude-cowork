# Hasil QA & Cara Deploy — Retryable Error Handling VIRA

**Tanggal:** 2026-08-08
**Status:** selesai dikerjakan & lolos QA. **Belum di-deploy** — semua keluaran berupa file baru, produksi tidak ditimpa.

---

## 1. Berkas yang dihasilkan

| # | Berkas | Aksi |
|---|---|---|
| 1 | `the scholars/report/production/`**`2026-08-08-VIRA-V4-retryable.json`** | BARU — `VIRA V4.json` tidak disentuh |
| 2 | `Persada Cisoka Residence/workflow/production/`**`2026-08-08-VIRA-PCR-Main-V1.3-retryable.json`** | BARU — V1.3 asli tidak disentuh |
| 3 | `Persada Cisoka Residence/workflow/production/`**`2026-08-08-VIRA-PCR-Main-V2.1-Vision-retryable.json`** | BARU — V2.1 asli tidak disentuh |
| 4 | `mobile dashboard/production/upload/`**`index.html`** | **DIUBAH di tempat** (ini memang satu-satunya sumber HTML). Backup: `production/2026-08-08-index-BACKUP-sebelum-search.html` |
| 5 | `mobile dashboard/production/`**`upload-assets.zip`** + **`upload.zip`** | **DIREGENERASI** dari `upload/` |
| 6 | `mobile dashboard/production/`**`2026-08-08-QA-mock-dashboard.html`** | BARU — harness QA (dashboard + n8n palsu). Jangan ikut di-upload |
| 7 | `mobile dashboard/production/`**`2026-08-08-QA-syntax-check.html`** | BARU — cek sintaks Code node. Jangan ikut di-upload |

> ⚠️ `upload-assets.zip` ternyata **sudah basi sebelum pekerjaan ini** — isinya `sw.js` versi lama (1889 B) padahal yang aktif 2394 B. Kalau zip itu yang kamu upload selama ini, service worker lama ikut ter-deploy. Sekarang sudah sinkron.
>
> `upload/` tetap berisi **persis 5 file** sesuai aturan README. Kedua file QA sengaja ditaruh di `production/`, bukan di `upload/`.

---

## 2. Ringkasan perubahan workflow

| | VIRA V4 | PCR V1.3 | PCR V2.1-Vision |
|---|---|---|---|
| Node sebelum → sesudah | 59 → **53** | 88 → **81** | 98 → **91** |
| Node digabung | 2 → 1 | 2 → 1 | 2 → 1 |
| `On Error` dikembalikan ke Stop Workflow | 2 | 6 | 6 |
| Node dihapus | 5 | 6 | 6 |
| Sisa `continueErrorOutput` | 2 (GForm, **disabled**) | **nol** | **nol** |

### Node gabungan baru: `Send WA + Verify (Kirimi)`

Menggantikan `Reply Chat Kirimi` (HTTP Request) + `Check API Response` (Code) dengan satu Code node.

Perilaku lama dipertahankan **persis**:
- Retry HTTP 3× jeda 5 detik → meniru `retryOnFail: true, waitBetweenTries: 5000` milik `Reply Chat Kirimi`.
- Kasus "HTTP 200 tapi `status:false`" **tidak** auto-kirim-ulang → meniru `Check API Response` yang memang tidak punya `retryOnFail`. Ini disengaja: respons `status:false` berarti Kirimi sudah memproses permintaan, jadi kirim-ulang otomatis berisiko pesan dobel. Kirim ulang untuk kasus ini = keputusan manusia lewat tombol Retry.
- `retryOnFail` node **sengaja dimatikan** supaya dua perilaku di atas tidak tertukar.
- Timeout 60 detik. Untuk V4 sama seperti sebelumnya; **untuk PCR ini eksplisit baru** (dulu `options: {}` alias ikut default n8n).

Kredensial: V4 tetap literal, PCR tetap dari `$('Parse Config').first().json.config` — sama seperti node HTTP yang digantikan.

### Node yang dihapus

**V4:** `Notify Admin API Error`, `Delete_Pending_Msg_Error`, `Reply Error`, `Delete_Pending_Msg_Bot_Off1`, `Notify User Error`
**PCR (V1.3 & V2.1):** `Notify Admin API Error`, `Mark Buffer Consumed (Kirimi Error)`, `Reply Error`, `Mark Buffer Consumed (AI Agent)`, `Notify User Error`, `Notify Admin Media Error`

### Node yang SENGAJA tidak disentuh

`Notify Admin Unknown`, `Notify Talk to Sam` / `Notify Talk to Admin`, `Notify Media Team`, `Notify Field Team` — namanya mengandung "Notify" tapi semuanya notifikasi **bisnis di jalur sukses**, bukan error handler.
`FAQ Retrieve`, `Summarize Handover`, `Analisa Gambar (Claude Haiku)` — `continueRegularOutput` = degradasi anggun, bukan pesan user yang hilang.
`Mark Buffer Consumed (Regular)` / `(Bot_Off)`, `Delete_Pending_Msg` / `_Bot_Off` — watermark jalur normal, wajib ada.

---

## 3. Hasil QA

### 3.1 Struktural workflow (Python, deterministik) — **66/66**

22 cek × 3 workflow. Yang diperiksa: nama & id node unik · semua sumber/target koneksi ada · node terhapus bersih total termasuk di ekspresi · semua `$('node')` menunjuk node yang ada · tidak ada referensi menggantung baru · target stop-on-error bersih dari `onError`/`continueOnFail` · node stop-on-error tinggal 1 cabang output · node gabungan lengkap & tanpa `onError`/`retryOnFail` · kredensial terisi · hulu & hilir node gabungan sama persis dengan sebelum patch · tidak ada node yatim baru · jumlah node sesuai · node wajib-utuh masih ada · `settings.errorWorkflow` tidak berubah · sisa `continueErrorOutput` sesuai daftar sadar.

**Dua bug tertangkap dan diperbaiki di proses ini:**
1. Koneksi masuk `Wait1 → Reply Chat Kirimi` tidak ikut dialihkan ke node gabungan → node gabungan jadi yatim. Ketahuan oleh cek "semua target koneksi ada".
2. Validator sempat salah menuduh `$('Read LINGKUNGAN Data')` sebagai referensi mati. Ternyata itu ada di **komentar CHANGELOG** `FAQ Retrieve` di V1.3 *dan* V2.1 — bawaan produksi, bukan akibat patch. Validator diperbaiki jadi sadar-komentar (bukan diberi pengecualian) supaya ceknya tetap ketat.

### 3.2 Sintaks JavaScript (browser, `AsyncFunction`) — **semua lolos**

- 3/3 node gabungan lolos parse + memuat seluruh bagian wajib.
- **53 Code node lain** di ketiga workflow ikut diperiksa: 0 gagal → patch tidak merusak kode lain.

### 3.3 Fungsional dashboard (browser, n8n di-mock) — **18/18 pada build final**

Diuji di UI sungguhan, kode produksinya sendiri, hanya `fetch` yang diganti n8n palsu (25 execution, 2 workflow, pagination, 404).

| | Kasus | Hasil |
|---|---|---|
| F01 | Daftar awal 20 kartu | PASS |
| F02 | Cari ID yang sudah dimuat → 1 hasil, **nol request tambahan** | PASS |
| F03 | Teks bantuan memakai hitungan daftar | PASS |
| F04 | Cari ID yang **belum** dimuat → ketemu via `GET /api/v1/executions/{id}` | PASS |
| F05 | Teks bantuan akurat untuk hasil langsung | PASS |
| F06 | Badge `HASIL CARI` + border ungu | PASS |
| F07 | ID tidak ada → pesan lokal, **bukan** banner "Endpoint tidak ditemukan" | PASS |
| F08 | Cari berdasarkan nama workflow | PASS |
| F09 | Cari berdasarkan status | PASS |
| F10 | Tidak ada hasil → empty state pencarian | PASS |
| F11 | Tombol bersihkan → daftar penuh lagi | PASS |
| F12 | Ganti filter status membersihkan pencarian | PASS |
| F13 | Filter Failed murni ERROR | PASS |
| F14 | Hasil pencarian lama tidak nyangkut saat filter diganti | PASS |
| F15 | Load more → 25 kartu | PASS |
| F16 | Deep link `#/e/<id>` membuka drawer | PASS |
| F17 | Badge RETRY / Retry of tampil | PASS |
| F18 | **Nol error runtime** sepanjang pengujian | PASS |

**Satu bug asli tertangkap QA dan diperbaiki:** hasil "GET by id" tetap ditempel di daftar walau chip filter status diganti — akibatnya filter **Failed** bisa menampilkan execution ber-status **success**. Perbaikannya: `setFilter()` sekarang membersihkan pencarian, karena filter status disaring di sisi n8n sedangkan GET-by-id tidak lewat filter itu.

Satu ketidakakuratan teks juga dibetulkan: dulu tertulis "1 cocok dari 20 yang dimuat" padahal hasilnya justru datang langsung dari n8n. Sekarang: "Ditemukan #23443 langsung dari n8n."

### 3.4 Integritas deploy

| Cek | V4 | PCR V1.3 | PCR V2.1 |
|---|---|---|---|
| `webhookId` & path identik dengan asli | YA | YA | YA |
| Tipe kredensial utuh (`anthropicApi`, `googleApi`) | YA | YA | YA |
| `settings.errorWorkflow` tidak berubah | YA | YA | YA |

---

## 4. Jawaban: apakah `n8n-proxy` perlu diubah?

**Tidak. Nol perubahan.**

Pencarian hanya memakai `GET /api/v1/executions/{id}` dan `GET /api/v1/executions?...`. Keduanya:
- lolos allowlist `ALLOWED_PREFIX = '/api/v1/'` di `worker-proxy.js` baris 18 & 42,
- memakai method `GET` yang sudah ada di `Access-Control-Allow-Methods` (baris 99),
- tidak butuh header baru (`X-N8N-API-KEY` sudah diizinkan).

Variables/secrets Cloudflare juga tidak perlu disentuh. Yang di-deploy ulang cuma worker **`n8n`** (static assets), bukan worker `n8n-proxy`.

---

## 5. Cara deploy

### 5.1 Dashboard

1. Cloudflare → Workers & Pages → worker **`n8n`** → **New deployment**
2. Upload isi folder `production/upload/` (5 file) **atau** `production/upload-assets.zip`
3. Di HP: hard refresh. `sw.js` tidak berubah, jadi hard refresh cukup.
4. Uji: ketik `23443` (atau nomor apa pun) di kotak cari baru di tab Executions.

### 5.2 Workflow — ⚠️ JANGAN "import as new workflow"

Ketiga JSON masih membawa `id` dan `webhookId` aslinya. Kalau di-import sebagai workflow baru, kamu akan punya duplikat dan **URL webhook bisa berubah → Kirimi berhenti masuk.**

Cara yang benar, untuk tiap workflow:
1. Buka workflow yang **sudah ada** di n8n (mis. `VIRA V4`).
2. Menu **⋯** kanan atas → **Import from File…** → pilih JSON `-retryable.json`.
   Ini mengganti isi kanvas workflow yang sedang terbuka, ID dan webhook-nya tetap.
3. Periksa cepat: node **`Send WA + Verify (Kirimi)`** ada, node `Notify Admin API Error` sudah hilang, `Wait1` menyambung ke node gabungan.
4. **Ctrl+S**.

Urutan yang disarankan: **V4 dulu** (paling sedikit perubahan) → pantau → **PCR V1.3** → pantau → **V2.1** belakangan.

> **V2.1 catatan penting:** `webhookId` dan path-nya **sama persis** dengan V1.3 (`wa-inbound-pcr`). Dua workflow dengan path webhook sama tidak boleh aktif bersamaan — nonaktifkan V1.3 dulu sebelum mengaktifkan V2.1.

### 5.3 Sebelum deploy — habiskan backlog execution lama

Setelah node dihapus, me-retry execution **lama** dengan centang "pakai versi workflow terbaru" akan gagal dengan `WorkflowOperationError` (n8n menolak kalau ada node yang hilang/di-rename). Ini **perilaku benar**, bukan bug.

- Retry dulu semua execution merah yang masih mau kamu selamatkan, **sebelum** deploy.
- Sesudah deploy, untuk execution lama pakai centang tersebut dalam keadaan **OFF**.

---

## 6. Uji asap di produksi (wajib, urut)

| # | Skenario | Cara | Harapan |
|---|---|---|---|
| S1 | Happy path | Chat normal ke bot | Hijau · user terbalas · `Counter`/`greeting_sent`/`buffer_done_ts` terisi |
| S2 | Kirimi mati | Ubah `KIRIMI_URL` di node gabungan jadi `.../send-message-ngasal` | Execution **merah** · notif WA + email masuk · setelah URL dibalikkan, **Retry dari HP** mengirim ulang WA dan alur lanjut sampai `Update to STATS` |
| S3 | Kirimi 200 tapi gagal | Ubah nomor tujuan jadi `628000000000` | Execution **merah** · notif masuk · Retry kini **benar-benar mengirim ulang** (ini yang dulu mustahil) |
| S4 | Sheets tidak terjangkau | Rename tab `STATS` sebentar | Merah di node GS · Retry lanjut · **tidak ada** duplikat baris MSG_BUFFER |
| S5 | Watermark | Picu S2, jangan retry, suruh user kirim pesan lagi <30 menit | Pesan lama + baru **digabung** dan dijawab sekaligus |
| S6 | Media (PCR) | Rusak `mediaUrl` di sheet | Merah di `Download Media` · **teks tetap terkirim sekali** dan tidak dikirim ulang saat retry |
| S7 | Non-regresi notifikasi bisnis | Tanya di luar FAQ; minta bicara dengan Sam/admin | `Notify Admin Unknown` & `Notify Talk to Sam/Admin` tetap jalan, execution tetap hijau |
| S8 | Alur ops utuh | Picu S2, lalu kerjakan **hanya dari HP** | Notif WA → buka dashboard → ketik nomor execution → Retry → hijau, **tanpa membuka UI n8n** |

---

## 7. Yang belum dikerjakan / masih terbuka

1. **Deep link di notifikasi belum dipasang.** Dashboard sudah mendukung `#/e/<id>`, tapi pesan WA/email masih memuat URL UI n8n saja. Supaya jadi satu ketukan, `Compose Notif` di **VIRA Error Notifier** + **VIRA-PCR Error Notifier**, dan `Normalize & Compose Email` di **GLOBAL Email Fallback Notifier**, perlu tambahan satu baris:
   `https://n8n.chatminagent.workers.dev/#/e/{execution.id}`
   Menyentuh 3 workflow lagi — belum kukerjakan karena di luar 4 item yang kamu sebut. Tinggal bilang kalau mau.
2. **Tombol "Deep scan 20 terakhir"** (item 4.4 di plan) dilewati — kamu belum memutuskan. Gunanya menangkap sisa `continueRegularOutput` yang sengaja dipertahankan.
3. **Blind spot yang disengaja:** `FAQ Retrieve`, `Summarize Handover`, `Notify Media Team`, `Notify Field Team`, dan `Analisa Gambar (Claude Haiku)` masih `continueRegularOutput` — kegagalannya tetap tidak terlihat. Sengaja, karena bukan "pesan user hilang".
4. **Temuan lama yang masih berdiri** (di luar cakupan, tidak kusentuh):
   - Kredensial Kirimi (`user_code`, `secret`, `device_id`) plaintext di parameter node, sekarang juga di dalam Code node gabungan V4 — sama seperti sebelumnya, tidak lebih buruk.
   - `Notify Admin Error` di VIRA-PCR Error Notifier punya key `device_id` **dobel** di `bodyParameters`.
   - Referensi mati `$('Read LINGKUNGAN Data')` di komentar `FAQ Retrieve` — tidak berbahaya, cuma catatan usang.
5. **Rollback:** import ulang JSON asli (`VIRA V4.json`, `VIRA-PCR Main V1.3.json`, `2026-08-07-VIRA-PCR-Main-V2.1-Vision.json`) dengan cara yang sama di §5.2. Dashboard: deploy ulang `production/2026-08-08-index-BACKUP-sebelum-search.html`.
