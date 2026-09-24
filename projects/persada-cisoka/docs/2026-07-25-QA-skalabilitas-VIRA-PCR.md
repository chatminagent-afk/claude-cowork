# QA Menyeluruh & Analisis Skalabilitas 100x — VIRA-PCR

**Tanggal:** 2026-07-25
**Scope:** `workflow/production/` — 4 workflow n8n + `PCR_Database.xlsx`
**Metode:** Sesi 1 = pembacaan paralel 4 subagent (Sonnet) + verifikasi silang manual atas klaim kritis.

---

## 0. Ringkasan Eksekutif

Sistem **fungsionalnya matang** (identity resolution No WA/lid, debounce single-flight, 3 lapis gate HITL, validasi slot survey deterministik, fail-loud pada media ambigu). Yang belum ada adalah **kapasitas**.

Plafon keras saat ini:

| Batas | Angka | Penyebab |
|---|---|---|
| **Throughput maksimum** | **~6–7 pesan/menit** | Kuota Google Sheets API: 60 read/menit/user. Sistem pakai **9 read + 4–5 write per pesan**. |
| Throughput riil (user multi-bubble) | **~3 pesan/menit** | Pesan yang kalah race debounce tetap membakar 7 call Sheets sebelum dibuang. |
| Outbound WhatsApp | **~500/hari** | 1 device Kirimi (`D-GHK1A`), gateway tidak resmi. Sudah dicatat di sticky note Follow-up. |
| Kapasitas follow-up | **780 kandidat** | `max_per_run 20 × 13 run/hari × interval 72 jam`. Di atas itu backlog tidak pernah habis. |

Naik 100x, **Google Sheets sebagai database yang pecah lebih dulu** — bukan Anthropic, bukan n8n. Setiap perbaikan lain sekunder terhadap ini.

Catatan penting: `whitelist_enabled = True` dengan hanya 3 nomor. Produksi masih **pilot tertutup**, jadi semua angka di bawah adalah proyeksi struktural, bukan hasil observasi beban nyata.

---

## 1. TEMUAN KEAMANAN — perlu tindakan segera, tidak bisa menunggu

### 1.1 🔴 Private key service account Google tersimpan plaintext di tab CONFIG

Tab `CONFIG` berisi 2 baris:

```
google service email        → persada@vira-persada.iam.gserviceaccount.com
google service private key  → -----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkq...  (1.732 karakter, PEM utuh)
kirimi_secret               → 4efe3780e1c0...  (64 karakter)
```

Tiga hal yang membuat ini serius:

1. **Node `Read CONFIG` membaca SELURUH tab tanpa filter.** Artinya private key masuk ke *execution data* n8n **setiap pesan masuk**, dan tersimpan di database eksekusi n8n. Siapa pun yang bisa membuka satu execution log bisa membaca private key.
2. **Private key itu adalah kredensial untuk mengakses spreadsheet itu sendiri.** Key disimpan di dalam objek yang dilindunginya — bocornya key = akses tulis penuh ke seluruh data pelanggan (STATS berisi nama, no WA, lokasi kerja, budget).
3. **Key juga ada di snapshot `PCR_Database.xlsx` di disk** — file yang ada di folder kerja ini.

Kredensial n8n (`Google Service Account - Persada`) sudah ada dan berfungsi. **Dua baris ini tidak dipakai oleh node manapun** — `Parse Config` tidak memasukkannya ke objek `config`. Ini murni residu.

**Tindakan:** hapus 2 baris dari tab CONFIG → rotate service account key di Google Cloud Console (key lama harus dianggap sudah bocor) → bersihkan execution history n8n → hapus/rotate `kirimi_secret` juga jika memungkinkan.

### 1.2 🟠 Kredensial Kirimi hardcoded di Error Notifier

`VIRA-PCR Error Notifier.json` → node `Notify Admin Error` menyimpan `user_code`, `secret`, `device_id` langsung di `bodyParameters` (bukan dari CONFIG). Rotate secret berarti harus edit workflow ini manual, dan secret ikut ter-commit di setiap ekspor JSON.

Bonus: nomor tujuan `6285155202354` (Steven) ≠ `admin_phone` di CONFIG (`6282321298930`). Ganti admin di CONFIG tidak mengubah tujuan notifikasi error.

---

## 2. BUG & INKONSISTENSI (tidak tergantung load)

| # | Temuan | Lokasi | Dampak |
|---|---|---|---|
| 2.1 | `$vars.chatCounter = counter` — `$vars` di n8n **read-only**, assignment tidak persist | `Chat Counter` | `chat_counter` efektif selalu 1. Dead code yang menyesatkan. |
| 2.2 | `Bootstrap Config` hardcode `SHEET_ID = '1dJWq7iq...'`, sedangkan **semua** node Sheets pakai `1pzGuRZ...` | `Bootstrap Config` | `config.sheet_id` berisi ID salah. Tidak dipakai node Sheets, jadi belum meledak — tapi jebakan untuk perubahan berikutnya. |
| 2.3 | CONFIG punya `rate_limit_max=10`, `rate_limit_window_sec=60`, `debounce_seconds=60`, tapi `Rate Limiter LID` hardcode `maxMessages=5`/`windowMs=60000` dan `Wait3` hardcode `60` | 2 node | Mengubah CONFIG tidak berefek. Rate limit riil 5, bukan 10. |
| 2.4 | Pesan yang dihentikan gate HITL ke-2 (`HITL Check`) & ke-3 (`Cek_user_status`) sudah masuk MSG_BUFFER tapi **tidak ada `Mark Buffer Consumed`** | Jalur HITL | Pesan menggantung di buffer. Saat bot_mode kembali ON, pesan lama (≤30 menit) bisa ikut terkirim ke AI sebagai konteks. |
| 2.5 | Race condition lost-update pada `Counter`/`Intensitas Chat`: `Read STATS` → `+1` → `Update to STATS` tanpa lock | `Process Counter & Merge Data` | 2 pesan bersamaan → keduanya baca N, keduanya tulis N+1. Satu increment hilang. Makin sering seiring load. |
| 2.6 | Cleanup MSG_BUFFER **berhenti total** di baris pertama dengan `ts` tidak valid | `Pick expired block (>2h)` | Satu baris rusak = seluruh blok kadaluarsa di belakangnya **tidak pernah terhapus**. Buffer tumbuh permanen. |
| 2.7 | Tidak ada idempotency key di webhook | `Webhook` | Retry dari Kirimi = pesan diproses ulang sebagai pesan baru. Belum jadi masalah karena volume kecil. |
| 2.8 | `staticData.rateLimits` tidak pernah di-evict | `Rate Limiter LID` | Objek tumbuh 1 entry per user unik, selamanya, di memori n8n. |
| 2.9 | 6 node notifikasi tanpa `retryOnFail` **dan** tanpa `onError` | `Notify Admin Media Error`, `Notify Media Team`, `Notify Field Team`, `Notify Admin Unknown`, `Notify Admin API Error`, `Notify Talk to Admin` | Satu timeout jaringan = cabang mati diam-diam. `Notify Admin API Error` paling kritis: kalau gagal, `Mark Buffer Consumed (Kirimi Error)` tidak jalan **dan** admin tidak tahu. |
| 2.10 | Error Notifier tanpa throttle/dedup | `Error Trigger` | 1.000 eksekusi gagal = 1.000 pesan WA ke satu nomor via device yang sama yang dipakai reply user. |
| 2.11 | `followup_max = 0` di CONFIG = follow-up tak terbatas per user | CONFIG | Kombinasi dengan interval 72 jam: user yang tidak pernah balas di-follow-up selamanya. |

---

## 3. ANALISIS BEBAN — apa yang pecah pada 100x

### 3.1 Google Sheets: 13–14 API call per pesan

Jalur sukses satu pesan (terverifikasi dari `connections`, semua 23 node Sheets reachable dari Webhook):

**READ (9)** — 7 di antaranya **baca seluruh tab tanpa filter**:
`Read CONFIG`* → `Read User STATS`* → `Read STATS for HITL`* → `Re-Read STATS Debounce` → `Read MSG_BUFFER` → `Read FAQ`* → `Read PRODUK Data`* → `Read LINKS Data`* → `Read STATS`*
(* = full-sheet)

**WRITE (4–5):**
`Append MSG_BUFFER` → `Update Buffer` → `Update to STATS` → `Mark Buffer Consumed (Regular)` → (+`Update Greeting` jika user baru)

Kuota Google Sheets API = **60 read/menit/user**. Service account = 1 user.

```
60 read/menit ÷ 9 read/pesan  ≈  6,6 pesan/menit  ≈  400 pesan/jam
```

Write tidak binding (60 ÷ 4 = 15/menit). **Read adalah plafonnya.**

**Diperparah oleh burst multi-bubble.** Pesan yang kalah race `IF_Chat_Debounce` sudah membakar **5 read + 2 write** sebelum dibuang. User yang mengetik 3 bubble = 19 read untuk 1 giliran percakapan → plafon efektif turun ke **~3 giliran/menit**.

Ini juga berarti biaya read **tumbuh terhadap 2 dimensi sekaligus**: jumlah pesan × jumlah baris STATS. `Read User STATS`, `Read STATS for HITL`, dan `Read STATS` masing-masing menarik seluruh tab. 100x user = payload 100x per call, dan 4 call STATS per pesan.

### 3.2 Anthropic: system prompt 17.731 karakter, tanpa prompt caching

`Anthropic Chat Model` = `claude-sonnet-4-6`, `maxTokens 1024`, `temp 0.4`. **Tidak ada `cache_control`.**

System prompt ~4.400 token dikirim **utuh dan ditagih penuh setiap pesan**. Ditambah `data_context` + `faq_context` + memory 10-turn ≈ 5.500 token input/pesan.

Proyeksi 3.000 pesan/hari (Sonnet 4.6 = $3/$15 per MTok; cache write 1,25×, read 0,1×; asumsi hit rate 90%):

| | Tanpa cache | Dengan cache |
|---|---|---|
| Input | ~$49/hari | ~$20/hari |
| Output (~300 tok × 3.000) | ~$13/hari | ~$13/hari |
| **Total** | **~$63/hari (≈ Rp 30 jt/bln)** | **~$34/hari (≈ Rp 16 jt/bln)** |

Penghematan **~46%** — bukan 72% seperti draf pertama laporan ini; angka itu mengabaikan biaya cache-write dan porsi prompt yang tetap variabel.

**Dua blocker, keduanya lebih penting dari angkanya:**

1. **Node `lmChatAnthropic` di n8n tidak punya opsi prompt caching sama sekali.** [PR #22318](https://github.com/n8n-io/n8n/pull/22318) closed tanpa merge; [issue #13231](https://github.com/n8n-io/n8n/issues/13231) closed as not planned. [PR #20484](https://github.com/n8n-io/n8n/pull/20484) yang merged hanya menyentuh `@n8n/ai-workflow-builder.ee` — fitur AI Builder internal n8n, nol efek ke AI Agent. Implementasinya harus lewat HTTP Request node langsung ke `/v1/messages` (feasible justru karena AI Agent VIRA **tidak punya tool** — tidak ada agent loop yang hilang; yang perlu diganti hanya Simple Memory).

2. **Struktur prompt sekarang membuat cache tidak akan pernah kena.** `data_context` dan `faq_context` di-interpolasi **di dalam** system prompt, di bagian akhir. Caching itu prefix match — konten volatil di dalam blok yang sama berarti tiap request menulis entry baru dan tidak ada yang pernah dibaca. Harus dipindah ke user message dulu. Ini benar dilakukan terlepas dari caching.

**Dan di volume pilot sekarang, caching justru lebih mahal.** TTL ephemeral 5 menit, break-even ≥2 request dalam window itu. Selama `whitelist_enabled=True` dengan 3 nomor, jeda antar pesan hampir pasti >5 menit → tiap request bayar write 1,25× tanpa pernah baca. Restrukturisasi prompt sekarang; migrasi ke HTTP Request tunggu traffic kontinu (>1 pesan/5 menit di jam aktif), atau pakai `ttl: "1h"` kalau bursty.

### 3.3 Kirimi: satu device untuk semuanya

Device `D-GHK1A` melayani: reply user, kirim media, notif admin, notif tim lapangan, notif tim media, follow-up, notif error. Semua paralel, semua satu device.

Gateway WhatsApp tidak resmi. Sticky note di workflow Follow-up sendiri sudah menandai **>500 pesan/hari = risiko ban**. 100x traffic melewati ini jauh. Kalau device kena ban, **seluruh sistem mati** — termasuk kemampuan mengabari admin bahwa sistem mati.

### 3.4 n8n: eksekusi menggantung

`Wait3` = 60 detik, `Wait1` = 5–10 detik acak. Setiap pesan menahan 1 eksekusi berstatus *waiting* selama **~65–70 detik**.

Pada 7 pesan/menit → ~8 eksekusi waiting bersamaan (masih aman). Pada 100x → ratusan sampai ribuan eksekusi waiting simultan, membebani tabel eksekusi dan scheduler resume n8n.

### 3.5 Simple Memory: in-memory, tidak tahan scale-out

`memoryBufferWindow` menyimpan riwayat percakapan **di memori proses n8n**, sessionKey = `resolved_key`. Selama n8n single-instance ini benar.

Begitu di-scale horizontal (yang wajib untuk 100x), giliran berikutnya user bisa mendarat di worker berbeda → **riwayat percakapan hilang di tengah percakapan**. Bukan crash, tapi korupsi state yang sulit dilacak. Restart n8n juga mengosongkan semua memory.

### 3.6 Follow-up: backlog matematis tidak pernah habis

- `followup_min/max_delay_sec` **tidak ada di CONFIG** → default kode 20–45 detik dipakai.
- `followup_max_per_run` **tidak ada di CONFIG** → default 20/run.
- `Loop Kandidat` batchSize = 1 (serial murni).
- Jendela aktif 08:00–20:00 = 13 run/hari.

```
Kapasitas = 20 × 13 = 260 kandidat/hari
Agar janji interval 72 jam terpenuhi: pool maks = 20 × 13 × 3 = 780 kandidat
```

| Pool kandidat | Waktu 1 putaran penuh |
|---|---|
| 10 | ~6 menit (selesai dalam 1 run) |
| 1.000 | ~4 hari |
| 10.000 | **~39 hari** (padahal dijanjikan 3 hari) |

Menaikkan `max_per_run` ke clamp maksimum 300 → 1 run = **172 menit**, melebihi interval trigger 1 jam → run saling tumpang tindih. Jalan buntu tanpa mengubah arsitektur.

### 3.7 FAQ Retrieve: TF-IDF dihitung ulang dari nol tiap request

Retrieval murni lexical (bukan embedding): tokenize → stopword ID → stemming sederhana → kamus sinonim manual → IDF → threshold `score ≥ 2,5`, ambil maks 4 item.

Kualitasnya wajar untuk 81 baris FAQ. Masalahnya: **index dibangun ulang setiap pesan** dari korpus penuh, dan isi `Jawaban` FAQ **tidak di-clip** (berbeda dari PRODUK yang di-clip 220 char/field) — FAQ panjang masuk penuh ke prompt.

---

## 4. RENCANA — 5 sesi

Sesi 1 sudah selesai (laporan ini). Urutan berikutnya sengaja menempatkan keamanan dan quick-win biaya di depan, refactor arsitektur di belakang.

### Sesi 2 — Keamanan & pembersihan (tanpa ubah arsitektur)
Risiko terbesar, usaha terkecil. Tidak menyentuh alur eksekusi.
- Hapus `google service private key` + `google service email` dari CONFIG; rotate key di GCP; bersihkan execution history
- Pindahkan kredensial Kirimi Error Notifier ke credential n8n / CONFIG
- Samakan nomor tujuan error ke `admin_phone`
- Perbaiki 2.1, 2.2, 2.3 (dead code + config yang diabaikan)
- **Deliverable:** patch JSON + checklist tindakan manual di GCP/n8n

### Sesi 3 — Prompt caching + hemat biaya
Satu perubahan, ~72% biaya token hilang. Independen dari yang lain.
- Aktifkan `cache_control` pada system prompt AI Agent
- Clip isi `Jawaban` FAQ agar prompt tidak melar tak terduga
- Ukur ulang token/pesan sebelum–sesudah
- **Deliverable:** node Anthropic + FAQ Retrieve ter-patch, tabel perbandingan biaya

### Sesi 4 — Turunkan beban Sheets dari 9 read → 2–3 read/pesan
Inti masalah skalabilitas. Ini sesi terberat.
- Cache CONFIG/PRODUK/LINKS/FAQ (data yang nyaris statis) — hilangkan 4 full-sheet read per pesan
- Konsolidasi 4 read STATS jadi 1 (`Read User STATS` dipakai ulang, bukan baca ulang 3x)
- Filter server-side / batchGet alih-alih tarik seluruh tab
- Short-circuit pesan yang kalah debounce **sebelum** membakar 7 call
- Perbaiki 2.4 (buffer menggantung), 2.5 (lost update), 2.6 (cleanup mandek)
- **Deliverable:** Main V1.4 + perhitungan ulang plafon throughput

### Sesi 5 — Ketahanan & jalur keluar arsitektural
Yang tidak bisa diselesaikan dengan optimasi.
- Idempotency key webhook (2.7)
- Eviction rate limiter (2.8)
- `retryOnFail` + `onError` pada 6 node notifikasi (2.9)
- Throttle/dedup Error Notifier (2.10)
- Rekomendasi: STATS → Postgres/Supabase, Simple Memory → external store, Kirimi → multi-device atau WhatsApp Cloud API resmi, Follow-up → queue worker
- **Deliverable:** patch ketahanan + dokumen keputusan migrasi (bukan implementasi migrasi)

---

## 5. Yang Belum Bisa Dipastikan

Hal-hal yang perlu data dari luar file — bukan asumsi yang boleh saya isi sendiri:

1. **Baseline traffic sekarang.** `whitelist_enabled=True` dengan 3 nomor, STATS berisi 2 user. "100x" perlu titik awal: berapa pesan/hari yang realistis diharapkan Om Sulianto? Angka ini menentukan apakah Sesi 4 cukup, atau Sesi 5 (migrasi DB) wajib.
2. **Kuota Google Sheets aktual** untuk project `vira-persada` — angka 60/menit adalah default; bisa jadi sudah dinaikkan.
3. **Tier Anthropic API** — menentukan plafon RPM/TPM.
4. **Batas Kirimi per device** — paket berbayar mana, apakah multi-device tersedia.
5. **Topologi n8n** — self-hosted atau cloud, single instance atau queue mode. Menentukan apakah Simple Memory (3.5) sudah jadi masalah sekarang atau baru nanti.
