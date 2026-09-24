# Rencana Analytics Topik VIRA — The Scholars

**Tanggal:** 2026-08-26
**Status:** disetujui, siap eksekusi Fase 1
**Baseline workflow:** r6 (`report/patch/2026-08-14-VIRA-V4-r6-link-guard-wa-channel.json`)

---

## 1. Tujuan

Sam butuh dasar untuk keputusan bisnis: topik apa yang paling sering ditanyakan user dalam sebulan, supaya dia bisa memutuskan hal seperti "buka kelas IELTS" atau "cari tutor hari Rabu".

Bentuk akhirnya: **laporan bulanan** yang menampilkan ringkasan **bulan sebelumnya** — top 10 topik, dengan denominator jumlah **user unik** yang chat di bulan itu.

Contoh kalimat yang harus bisa dihasilkan:

> "September 2026 — 43 user unik chat. 18 di antaranya (42%) menanyakan IELTS."

---

## 2. Keputusan yang sudah dikunci

| # | Keputusan | Alasan |
|---|-----------|--------|
| 1 | Hanya panen dari user `bot_mode = ON` | User OFF pesannya memang tidak tersimpan di mana pun; menutupnya butuh patch workflow utama. Ditunda sampai Sam lihat nilainya. |
| 2 | Denominator = **user unik**, bukan jumlah pesan | 1 orang nanya 6x tidak boleh menggelembungkan persentase |
| 3 | Top 10 (boleh tipis) | Volume kecil diterima apa adanya |
| 4 | Satu orang bisa terhitung 2x kalau identitasnya `lid` | Diterima, belum ada solusi |
| 5 | **Tidak menyimpan isi chat permanen** | Hanya label topik + hitungan. Teks aslinya dibuang setelah diklasifikasi. |
| 6 | Cleanup STATS 3-bulan **tetap jalan** sesuai rencana | Tidak bentrok — cleanup hanya menyentuh tab `STATS` |
| 7 | Pakai dashboard multi-tenant yang sudah ada | Bukan bikin dashboard khusus The Scholars |
| 8 | Tab analytics di spreadsheet yang **sama** (`1tEJYay...`) | Schema tenant hanya punya satu `sheetId`; spreadsheet kedua butuh perombakan schema |
| 9 | Service account dashboard **terpisah** dari SA bot | Kuota Sheets 60 read/menit per akun; berbagi = risiko 429 yang dulu bikin pesan hilang |
| 10 | Top 10 disajikan sebagai **tabel + doughnut top-5** | `charts.js` belum punya horizontal bar, dan `shortLabel()` memotong label >8 karakter |

---

## 3. Batasan yang diterima (tulis apa adanya di dashboard)

Angka yang dilaporkan **bukan** cakupan penuh. Yang tidak terekam:

| Yang hilang | Sebabnya | Besarnya |
|---|---|---|
| User `bot_mode = OFF` | Cabang false `IF Bot Mode Active` tidak pernah sampai `Append MSG_BUFFER` | **384 dari 664 user (58%)** |
| Pesan non-teks (gambar, audio, dokumen, stiker) | `Chat Counter`: `if (messageType !== "text") return []` | tidak terukur |
| Pesan grup & pesan bot sendiri | `If From Group`, `IF From Me` | memang bukan chat user, benar dibuang |
| Pesan >5/menit/user | `Rate Limiter LID` — dibuang **tanpa jejak** | jarang |

Label wajib di dashboard:

> *Berdasarkan percakapan yang ditangani VIRA. Chat yang sudah diambil alih Sam tidak ikut terhitung.*

Ini bukan disclaimer basa-basi — 58% itu justru percakapan ber-intent tertinggi (yang sampai di-escalate ke Sam). Jangan sampai Sam mengira angkanya utuh.

---

## 4. Arsitektur

**Tiga workflow n8n baru. Nol perubahan pada workflow VIRA utama.**

```
MSG_BUFFER  (umur maks 24 jam)
    |
    |   WF-A   4x sehari — 01:00 / 07:00 / 13:00 / 19:00 WIB
    v
TOPIC_LOG   (1 baris per bulan+user+topik, tanpa teks chat)
    |
    |   WF-B   tanggal 1 tiap bulan, 00:30 WIB
    v
MONTHLY_SUMMARY   (1 baris per bulan, permanen, ~12 baris/tahun)
    |
    |   WF-C   dibaca dashboard
    v
Dashboard PWA  ->  Sam
```

### WF-A — `VIRA Topic Harvester`

**Cron:** `0 1,7,13,19 * * *` (Asia/Jakarta)

Alur:

1. Baca `MSG_BUFFER`, ambil hanya baris dengan `ts` > watermark milik WF-A sendiri
2. Klasifikasi topik secara **batch** (30–50 pesan per satu panggilan AI)
3. **Buang teks pesannya**
4. Upsert ke `TOPIC_LOG`
5. Simpan watermark baru

**Kenapa jam 01:00 dan bukan jam lain — ini presisi yang menentukan:**

Cleanup MSG_BUFFER jalan `0 3 * * *` dengan `RETENTION_MS = 2 jam`, jadi jam 03:00 dia menghapus baris dengan `ts < 01:00`. Run jam 01:00 menangkap **tepat sampai batas itu**. Celahnya nol.

Kalau harvester dijadwalkan jam 00:00, baris 00:00–01:00 akan terhapus sebelum sempat dipanen.

**Kenapa 4x sehari, bukan 1x:**

| | Harian 1x | 4x sehari |
|---|---|---|
| Normal | jalan | jalan |
| Run gagal 1x (n8n restart / 429 / API error) | **data 1 hari penuh hilang permanen** — run berikutnya 24 jam lagi, cleanup sudah menyapu | run berikutnya 6 jam lagi, baris masih hidup, **pulih sendiri** |
| Beban | 1 read/hari | 4 read/hari |

Selisih biaya nol koma sekian, selisih risiko = kehilangan sebulan data karena satu malam n8n restart.

**Klasifikasi pakai AI batch, bukan keyword.** Alasannya:

- Keyword gagal total di bahasa chat WA Indonesia (typo, singkatan, campur)
- Lebih penting: pertanyaan seperti *"ada kelas hari Rabu nggak?"* **tidak akan pernah muncul** kalau taksonominya dikunci di depan

Output AI per pesan: label dari taksonomi tetap **ATAU** `NEW:<label>`. Slot `NEW:` inilah mekanisme penemuan topik baru. Direview bulanan, yang sering muncul dipromosikan jadi kategori resmi.

Volume rendah → biaya token nyaris nol.

**Skema `TOPIC_LOG`** (1 baris per bulan+user+topik, bukan per pesan):

```
bulan | user_key | topic | jumlah_pesan | first_ts | last_ts
```

### WF-B — `VIRA Monthly Rollup`

**Cron:** `30 0 1 * *` (Asia/Jakarta) — tanggal 1 tiap bulan, 00:30 WIB

1. Baca `TOPIC_LOG` untuk bulan yang baru lewat
2. Hitung: total user unik, total pesan, top 10 topik (dihitung per **user unik**)
3. Tulis 1 baris ke `MONTHLY_SUMMARY`
4. Pangkas `TOPIC_LOG` bulan itu — tidak menumpuk data lama

**Skema `MONTHLY_SUMMARY`:**

```
bulan | total_user_unik | total_pesan | top_json | coverage_note
```

~12 baris per tahun. Ringan, permanen, aman dari cleanup mana pun.

### WF-C — Perluasan Dashboard API

Menyentuh workflow **`VIRA-Dashboard-API`**, bukan VIRA utama.

- Tambah `TOPIC_LOG` + `MONTHLY_SUMMARY` ke `tabs[]` tenant `thescholars` di `n8n/src/tenants.js`
- Tambah blok penghasil KPI + chart di `n8n/src/build-payload.js`
- **Jangan** beri flag `rangeAware` pada chart bulanan → selector 7/30/90 hari otomatis mengabaikannya dan merender array penuh apa adanya
- Rebuild: `python n8n/build_workflow.py` (murni Python, tidak butuh Node/npm)
- Frontend `app/` **tidak disentuh sama sekali**

---

## 5. Beban Sheets API

**WF-A + WF-B bukan masalahnya.**

| | Ops per hari |
|---|---|
| WF-A (4 run × 1 read + 1–2 write) | ~8–12 |
| WF-B | 2, sekali sebulan |
| **Workflow utama** (50 pesan/hari × 13 ops) | **~650** |

Analytics menambah **~1,5%**.

---

## 6. Optimasi workflow utama — JALUR TERPISAH

Bukan bagian dari analytics. Jangan digabung, jangan saling menyandera. Punya QA sendiri.

Happy path sekarang **13 operasi Sheets per pesan masuk**, semuanya ke satu spreadsheet. Ada riwayat 429 yang membuat pesan user hilang diam-diam.

| Perubahan | Hemat | Risiko | Catatan |
|---|---|---|---|
| **Gabung 3 write STATS** jadi 1 node | −2 (−3 saat greeting) | Rendah | Kolom disjoint, sudah paralel, tidak ada read STATS di antaranya |
| **Buang `Query LINKS for GForm`** | −1 (jalur GForm) | Rendah | LINKS sudah dibaca sebelumnya, dan **tidak ada node yang pernah menulis ke LINKS** |
| **Paralelkan 4 read statis** | 0 ops, tapi −3 round-trip latency | Rendah | Sekarang berantai sekuensial: `FAQ → PROGRAM → ABOUT → LINKS` |
| **Cache 4 tab statis** (`getWorkflowStaticData` + TTL) | −4 di mayoritas pesan | Sedang | Pola sudah terbukti di workflow ini — `Rate Limiter LID` sudah memakainya. Risiko: Sam edit harga, bot masih quote data lama selama TTL. |

### Cara menggabung 3 write STATS

Sekarang `Send WA + Verify (Kirimi)` fan-out ke 3 cabang paralel, masing-masing punya node Sheets sendiri, semuanya menulis ke **baris yang sama** (match `No WA`), hanya beda kolom:

| Node | Kolom |
|---|---|
| `Update to STATS` | Nama, Pesan Pertama, Counter, Tanggal Chat Pertama, Tanggal Chat Terakhir, Jam Chat Terakhir, follow_up_count, lid, last_reply_ts, kelas_anak, kelas_anak_ts, program_interest, bot_mode |
| `Delete_Pending_Msg` | buffer_done_ts, lid |
| `Update Greeting` | greeting_sent, lid |

**Caranya: hapus 2 node, perluas column mapping node yang tersisa jadi gabungan ketiganya** (14 kolom unik, `lid` beririsan). Semua datanya sudah tersedia di titik itu — tidak ada yang perlu dihitung ulang.

**Tetap node Google Sheets biasa. Bukan HTTP Request, bukan JS custom.**

Jaminannya keras: n8n `appendOrUpdate` dengan `mappingMode: defineBelow` = **satu panggilan `values.update`**. 3 node = 3 panggilan. 1 node = 1 panggilan. Kolom yang tidak dipetakan tidak tersentuh.

Detail: `greeting_sent` sekarang dijaga `IF Update Greeting`. Setelah digabung, tulis saja selalu — menulis `Y` ke baris yang sudah `Y` itu idempoten.

### JANGAN disentuh

`Read User STATS`, `Read STATS for HITL`, `Re-Read STATS Debounce`, `Read STATS`, `Read MSG_BUFFER`.

Masing-masing menjaga concurrency window nyata. `Re-Read STATS Debounce` + `IF_Chat_Debounce` **adalah** mekanisme debounce-nya — itu persis yang mencegah kelas bug pesan hilang yang dulu dikejar.

---

## 7. Ketergantungan yang harus dijaga

> **Jadwal WF-A terikat pada cleanup MSG_BUFFER.**
>
> Cleanup: `0 3 * * *`, `RETENTION_MS = 2 jam`.
> WF-A run jam 01:00 adalah yang menanggung beban — dia menangkap tepat sampai batas yang akan dihapus.
>
> **Kalau cron cleanup diubah, atau `RETENTION_MS` dikecilkan, WF-A bocor diam-diam tanpa error.** Ubah keduanya bersamaan atau jangan sama sekali.

---

## 8. Dashboard — kondisi saat ini

### Yang sudah jadi

| | Status |
|---|---|
| PWA (installable iOS/Android) | ADA — `manifest.webmanifest`, `sw.js`, `display: standalone`, ikon 192/512 maskable |
| Mobile responsive | ADA — `MOBILE_BREAKPOINT: 640`, `CHART_HEIGHT_MOBILE`, SVG re-measure per lebar layar |
| Chart engine | ADA — SVG tulisan sendiri, tanpa library: line, bar, doughnut |
| Akun Sam | ADA — role `owner`, terkunci ke tenant `thescholars`, tanpa tenant switcher |
| **Toggle bot_mode ON/OFF** | **SUDAH JADI, lengkap end-to-end** |

Toggle bot_mode: action `toggle_user`, toggle switch ala iOS di `render.js:377`, dialog konfirmasi, node `Update Bot Mode`, plus audit trail. Identity logic sudah benar — **No WA primary → `lid` fallback → `ROW_NOT_FOUND`, tidak pernah fallback ke `rows[0]`**. Persis prinsip identity project. Tidak ada yang perlu dibangun.

### Isolasi tenant — ditegakkan di server, bukan sekadar UI

```js
// n8n/src/auth.js — vaCheckClaims
if (user.tenants.indexOf(claims.t) === -1) return { ok: false, reason: 'TENANT_FORBIDDEN' };
```

Tenant diambil dari token bersignature, spreadsheet ID tidak pernah keluar dari n8n, `switch_tenant` divalidasi ulang ke registry live setiap request. Sam **tidak bisa** melihat Persada, bahkan dengan memalsukan field dari browser.

### Onboarding klien baru (alasan utama tidak bikin dashboard terpisah)

| Yang berubah | Apa |
|---|---|
| `n8n/src/tenants.js` | 1 entry + 1 akun owner |
| Rebuild | `python n8n/build_workflow.py` |
| n8n UI | Re-import + konfirmasi credential |
| Google | Share spreadsheet baru ke service account |
| **`app/` (frontend)** | **NOL perubahan** — dipaksa build gate `qa/validate_workflow.py` §6 yang menggagalkan build kalau string spesifik-klien bocor ke `app/` |

### Yang belum — prasyarat sebelum Sam bisa buka apa pun

Dashboard **belum pernah dideploy dan belum pernah menyentuh n8n asli**. 407 QA check itu lawan mock server Python, bukan n8n beneran.

| # | Blocker | Siapa |
|---|---|---|
| 1 | Service account `vira-dashboard` belum dibuat, JSON key belum ada | Steven (Google Cloud Console) |
| 2 | Spreadsheet belum di-share ke SA itu | Steven |
| 3 | `GOOGLE_CRED_ID` masih literal `REPLACE_WITH_DASHBOARD_SA_CREDENTIAL_ID` | Steven (n8n UI) |
| 4 | `app/` belum di-upload (Cloudflare Pages / Netlify) | Steven |
| 5 | `corsOrigins` masih placeholder `vira-dashboard.pages.dev` | Claude, setelah domain final |
| 6 | 5 item UAT belum pernah jalan di n8n asli | Steven + Claude |
| 7 | Password belum didistribusi | Steven |

**Workflow yang di-deploy: `n8n/VIRA-Dashboard-API.json`** (248 KB, di-generate oleh `python n8n/build_workflow.py`). Satu workflow ini melayani webhook `POST /webhook/vira-dash` — login, stats, `toggle_user`, `switch_tenant`.

5 item UAT yang belum pernah diuji ke n8n asli:

1. Node Crypto — format token `<base64url>.<64 hex>`
2. `Loop Over Tabs` — loop baca multi-tab
3. Dynamic `documentId` (`{{ $json.doc_id }}`) di Resource Locator
4. **Toggle menulis ke baris yang benar** — paling kritis. Salah baris = bot mati untuk customer yang salah.
5. Integrasi: setelah `bot_mode=OFF` dari dashboard, bot beneran diam

---

## 9. Urutan & timeline

Kuncinya: **hanya WF-A yang punya jam berdetak.** Setiap hari tertunda = satu hari data hilang permanen. Tapi WF-A tidak butuh dashboard untuk mulai mengumpulkan.

| Fase | Kapan | Blocker |
|---|---|---|
| **1. Taksonomi seed + WF-A Harvester** | **Sekarang** | Tidak ada |
| **2. Deploy + smoke test dashboard** | Paralel | Blocker #1–4 (tangan Steven) |
| **3. WF-B Monthly Rollup** | Sebelum 1 Okt | Butuh WF-A jalan |
| **4. View analytics di dashboard** | Sebelum 1 Okt | Butuh Fase 2 + 3 |
| *(opsional)* Optimasi ops workflow utama | Kapan saja | Jalur terpisah |

**Laporan penuh pertama: data September, tampil 1 Oktober.** Agustus sudah lewat setengah dan datanya sudah tersapu — tidak bisa diselamatkan.

Fase 2 layak didahulukan meski analytics belum ada: begitu dashboard live, Sam langsung dapat **toggle bot_mode** — nilai instan tanpa menunggu Oktober.

---

## 10. Taksonomi seed — langkah pertama

Menebak-nebak daftar topik adalah cara tercepat menghasilkan analytics yang salah. Datanya sudah ada di tangan:

- **664 baris `Pesan Pertama`** di STATS — pesan pembuka tiap user, tidak pernah ditimpa
- **151 baris `UNKNOWN`** — pertanyaan mentah + jawaban VIRA, khusus yang VIRA tidak tahu

Sekali kerja, dua hasil:

1. Daftar topik untuk WF-A
2. Laporan baseline yang bisa ditunjukkan ke Sam **sekarang**, tanpa menunggu Oktober

Nol risiko, tidak menyentuh apa pun.
