# Analisa Bug Baru & Sustainability — VIRA V4 (export live 6 Juli 2026)

File: `report/patch/V4 Fable/VIRA V4.json` — **JSON valid, 60 node, active: true** (export truncated 3 Juli sudah teratasi).
Exclude sesuai permintaan: IF (Whitelist) — sekarang statusnya **disabled** — dan credentials Kirimi/webhook auth.
Status known-issues lama: 13/16 `.item` sudah difix; sisa 3 (`Reply Chat Kirimi`, `Record to UNKNOWN`, `IF Bot Mode Active`) ternyata **risiko rendah** — ketiganya me-refer node induk langsung/lewat IF & Wait yang meneruskan pairedItem, jadi resolvable. Tidak urgent.

---

## A. BUG BARU (belum terdeteksi sebelumnya)

### B1 — KRITIKAL: `Update GForm Sent TS1` jalan di SETIAP pesan (pass-through jalur mati)
Jalur GForm lama sudah di-disable (`IF Send GForm` → `Query LINKS` → `Pick GForm Link` → `IF GForm Resolved` → `Send GForm Link`), TAPI node terakhir rantai itu, **`Update GForm Sent TS1`, masih ENABLED**. Di n8n, node disabled *meneruskan data dari input ke output pertama* (konfirmasi founder n8n Jan: "If a node is disabled the data from the first input will be simply passed through to the first output" — [community.n8n.io/t/9640](https://community.n8n.io/t/disabled-nodes-executing/9640)). Ini persis mekanisme yang sama yang membuat IF (Whitelist) disabled meloloskan traffic publik.

Akibat: `Process All` → 5 node disabled (pass-through) → `Update GForm Sent TS1` menulis `gform_sent_ts = now` ke STATS **setiap turn, untuk semua user, terlepas GForm dikirim atau tidak**.

Dampak: (1) kolom `gform_sent_ts` korup total — workflow follow-up ("follow-up otomatis kalau belum isi form", fungsi inti VIRA) akan menganggap SEMUA user sudah dikirimi form, dan timer follow-up ter-reset tiap user chat; (2) +1 write Sheets per pesan (kuota). Fix: hapus koneksi `Send GForm Link → Update GForm Sent TS1` (atau disable node-nya). Karena link GForm sekarang di-inject inline di `Process All`, penulisan `gform_sent_ts` yang benar harus dipindah: hanya saat `isSendGForm === true`.

### B2 — TINGGI: Validasi `Check API Response` nyaris selalu lolos
```js
const isSuccess = responseData.status === true || responseData.success === true ||
                  (responseData.data && responseData.data.id) ||
                  (responseData.message && responseData.message !== 'error');
```
Klausa terakhir: respons gagal Kirimi yang HTTP 200 dengan body mis. `{status:false, message:"Insufficient balance"}` atau `"Device disconnected"` → `message !== 'error'` → dianggap **sukses**. Konsekuensi berantai: user TIDAK menerima balasan, admin TIDAK dinotif, dan yang paling merusak — `Update STATS - Greeting Flag` tetap set `greeting_sent=Y`, jadi **user baru yang gagal menerima intro tidak akan pernah dapat intro**, plus watermark buffer maju (pesan dianggap terjawab). Fix: hapus klausa `message`, sisakan `status === true || data.id`; verifikasi dulu 1 sample respons sukses Kirimi real sebelum deploy.

### B3 — SEDANG-TINGGI: Paragraf balasan dihancurkan (`\s{2,}` → spasi)
Di `Process All`, cleanup markdown & vokatif memakai `.replace(/\s{2,}/g, ' ')` (2×). `\n\n` (pemisah paragraf) = 2 whitespace → diganti satu spasi. Semua balasan AI multi-paragraf jadi **satu blok teks panjang** di WhatsApp — merusak keterbacaan, terasa bukan "Sam". (Link injection selamat karena `\n\n👉` ditambahkan setelah cleanup.) Fix: ganti kedua occurrence menjadi `[ \t]{2,}` dan normalisasi newline terpisah (`\n{3,}` → `\n\n`).

### B4 — SEDANG: SEND_GFORM fallback bisa klaim kirim link tanpa link
Kalau `isSendGForm` ter-trigger (tag atau fallback frasa "link pendaftaran...") tapi lookup di LINKS tidak menemukan row aktif yang cocok → hanya `console.warn`. User menerima kalimat "link sudah saya kirim" **tanpa URL**, tanpa notifikasi admin. Fix: bila match gagal → append teks pengganti ("sebentar yaa, linknya menyusul") + kirim notif admin (pakai pola `Notify Admin Unknown`).

### B5 — SEDANG: Tidak ada dedup webhook + race duplikat row user baru
(a) Tidak ada dedup `message id` dari payload Kirimi — bila Kirimi retry delivery, pesan yang sama masuk 2 eksekusi → 2 row MSG_BUFFER → teks user dobel di merge (AI membaca pertanyaan dua kali) atau 2 balasan. (b) User baru yang mengirim 2 pesan beruntun cepat: dua eksekusi `Update Buffer` (appendOrUpdate) bisa sama-sama tidak menemukan row → **duplicate row STATS** untuk No WA yang sama; semua update selanjutnya ambigu. Fix: (a) simpan id pesan terakhir per user di `workflowStaticData` dan skip duplikat di `Chat Counter`; (b) sulit dihilangkan total di Sheets — mitigasi: pembersihan duplikat di cleanup workflow + jangka menengah pindah ke store yang atomik (lihat S5).

### B6 — SEDANG (UX): Jawaban kelas berupa angka polos dianggap "unclear"
`Preprocess`: balasan ≤4 karakter tanpa match kelas → `unclearReply` → AI diinstruksikan "JANGAN ulang pertanyaan, tawarkan [TALK_TO_SAM]". Padahal jawaban paling umum atas "kelas berapa?" adalah **"9"**, **"12"**, "8 smp". Pola regex kelas tidak menangkap angka polos. Fix: di Preprocess, bila pesan hanya angka 6–12 (±suffix sd/smp/sma), map langsung ke kelas → grades, dan exclude dari `unclearReply`.

### B7–B10 — RENDAH (hygiene & ketahanan)
- **B7**: `$vars.chatCounter` di `Chat Counter` — `$vars` read-only, counter selalu 1; `ai_input_text` yang dibangun di node ini juga tak terpakai (di-overwrite `Cek_user_status`). Dead code, hapus saja.
- **B8**: Rate Limiter — `staticData.rateLimits` tidak pernah di-prune (tumbuh 1 entry/user selamanya) dan drop pesan diam-diam tanpa jejak di sheet.
- **B9**: Node yatim **`Notify Admin API Error1`** (tanpa koneksi apa pun) + **pinData Webhook** masih tertinggal di workflow aktif. Bersihkan.
- **B10**: `Wait3` 60 dtk berjalan **in-memory** (n8n hanya offload ke DB untuk wait >65 dtk) → restart/redeploy n8n saat ada eksekusi menunggu = eksekusi hilang. Mitigasi sudah ada (pesan tetap di MSG_BUFFER, ikut ter-merge bila user chat lagi ≤30 mnt), tapi kalau user tidak chat lagi, pesan tak terjawab. Opsi: naikkan Wait3 ke 66 dtk agar persist ke DB.

---

## B. PLAN FIXING — TOP 5 PRIORITAS

> Konfirmasi dulu sebelum saya eksekusi (sesuai aturan project). Semua fix di bawah bisa saya siapkan sebagai patch JSON + langkah manual UI.

| # | Fix | Aksi | Effort | Risiko regresi |
|---|-----|------|--------|----------------|
| 1 | **B1** gform_sent_ts korup | Hapus koneksi `Send GForm Link → Update GForm Sent TS1`. Pindahkan penulisan ts: tambah IF `isSendGForm==true` setelah `Check API Response` → node update `gform_sent_ts` (reuse node yang sama). | 15 mnt | Rendah — jalur terisolasi |
| 2 | **B2** validasi API | Ketatkan `Check_API_Response.js`: `status===true \|\| success===true \|\| data?.id` saja. Sebelumnya: kirim 1 pesan test, catat body respons sukses Kirimi persis. | 20 mnt + 1 test | Rendah; kalau terlalu ketat, false-alarm ke admin (fail-safe, bukan fail-silent) |
| 3 | **B3** paragraf hancur | Di `Process All`: 2× `\s{2,}` → `[ \t]{2,}`; tambah `\n{3,}`→`\n\n`. Test dengan balasan multi-paragraf. | 10 mnt | Rendah |
| 4 | **B6** angka polos kelas | Tambah deteksi angka-polos di `Preprocess` + guard `unclearReply`. | 20 mnt | Rendah — regex tambahan terisolasi |
| 5 | **B4** link ghaib | Guard di `Process All`: no-match → ubah kalimat + notif admin. | 20 mnt | Rendah |

Sekalian saat di UI (≤5 mnt, opsional): hapus node yatim `Notify Admin API Error1`, unpin data Webhook, hapus blok `$vars.chatCounter`. B5 (dedup) saya sarankan masuk batch berikutnya karena butuh test race yang lebih hati-hati.

Urutan deploy yang aman: fix di copy workflow → test 3 skenario (user baru intro, user lama tanya harga, minta daftar/GForm) → baru apply ke live. Backup export sebelum edit.

---

## C. SUSTAINABILITY — SUPAYA VIRA TAHAN LAMA & MINIM MAINTENANCE

### S1 — Kuota Google Sheets = bottleneck #1 (bukan FAQ penuh)
Per pesan saat ini: **±9 read** (Read User STATS full, Read STATS for HITL full, Re-Read Debounce, Read MSG_BUFFER, FAQ, PROGRAM, ABOUT, LINKS, Read STATS full di jalur counter) + **4–6 write**. Limit Sheets API: **60 read/menit & 60 write/menit per service account** ([developers.google.com/sheets quota](https://developers.google.com/workspace/sheets/api/limits)). Artinya sistem mulai kena 429 di kisaran **~6 pesan/menit total semua user** — angka yang mudah tercapai saat musim pendaftaran. Ini penyebab paling mungkin "eksekusi gagal diam-diam" ke depan.

Penyesuaian (urutan dampak):
1. **Hapus `Read STATS for HITL`** — redundan: bot_mode sudah dicek di `IF Bot Mode Active` (pre) dan dicek ulang post-debounce di `Cek_user_status` via `Re-Read STATS Debounce`. −1 read.
2. **Hapus `Read STATS` di jalur counter** — `Resolve User Row` sudah membawa `counter_db` dan seluruh row; `Process Counter & Merge Data` tinggal pakai itu. −1 read (full-sheet pula).
3. **Cache 4 read statis (FAQ/PROGRAM/ABOUT/LINKS)** di `workflowStaticData` dengan TTL 5–10 menit — konten ini jarang berubah. −4 read untuk mayoritas pesan. Total: dari ~9 jadi **~3 read/pesan** → headroom ~20 pesan/menit.

### S2 — FAQ semakin penuh
Desainnya sudah benar: retrieval lexical hanya menyertakan top-4 Q/A ke prompt, jadi **token cost TIDAK naik** seiring FAQ bertambah. Yang naik hanya ukuran read & CPU scoring — dengan cache S1(3), aman sampai **ribuan baris**. Yang perlu dijaga manusia: (a) kolom `Kategori` konsisten (boost scoring bergantung ini); (b) pertanyaan ditulis dengan kata kunci yang natural (retrieval berbasis kata); (c) buat loop mingguan **UNKNOWN → FAQ**: tab UNKNOWN sudah menampung pertanyaan gagal — jadwalkan review, jawab, pindahkan ke FAQ. Ini satu-satunya "maintenance" konten yang sesungguhnya, dan justru membuat bot makin pintar tanpa sentuh workflow.

### S3 — STATS & MSG_BUFFER membesar
- STATS dibaca full-sheet tiap pesan (perlu untuk fallback lid). Sampai ~2–3rb row masih oke; setelah itu latensi & memori n8n naik. Mitigasi murah: **arsipkan user tidak aktif >6 bulan** ke tab `STATS_ARCHIVE` (workflow terjadwal bulanan).
- MSG_BUFFER **append-only tanpa penghapusan di workflow utama** — tumbuh tanpa batas. File cleanup sudah ada (`2026-07-03-VIRA_MSG_BUFFER-cleanup.json`) — **pastikan sudah di-deploy & aktif**; kalau belum, ini prioritas deploy minggu ini. Sekalian tambahkan pembersihan duplicate-row STATS (B5b).
- Jangka menengah (saat >5rb user / mulai sering 429): pindahkan STATS+MSG_BUFFER ke **n8n Data Tables atau Postgres** (Sheets tetap jadi "dashboard" read-only untuk Sam via sync satu arah). Sheets bukan database — batas praktisnya akan terasa jauh sebelum batas 10 juta cell.

### S4 — Biaya AI (lanjutan audit 3 Juli)
Window memory sudah 10 ✓. Sisa dua langkah hemat yang belum jalan: (a) **SYSTEM_DATA jadi flags saja** — kalimat intro verbatim (~700 char) masih terduplikasi ke memory tiap turn user baru; (b) **prompt caching** — system message 13,5rb char statis, tapi `data_context`/`faq_context` di-inject di ujungnya sehingga cache putus; pindahkan kedua variabel itu ke user message agar blok statis cacheable (cache read Sonnet $0.30/M). Estimasi gabungan: $0.03 → ~$0.012–0.015/conv.

### S5 — Ketahanan operasional
- **Versi & backup**: simpan export JSON ke git (atau minimal folder tanggal) tiap perubahan — insiden export truncated 3 Juli tidak boleh jadi satu-satunya backup.
- **Health check terjadwal** (workflow n8n harian): test read STATS + cek saldo/status device Kirimi → notif admin kalau anomali. Kegagalan Kirimi paling sering bukan bug workflow (kasus pesan Adrian yang tidak pernah sampai n8n).
- **Model**: `claude-sonnet-4-6` akan deprecated suatu saat — catat sebagai item review kuartalan, jangan tunggu error.
- **Webhook auth + secret ke credentials** (known, exclude dari analisa ini — tapi tetap harus masuk roadmap; secret yang bocor di export = orang lain bisa kirim WA atas nama The Scholars).

### Ringkasan prioritas sustainability
Bulan ini: S1 (kuota, 3 langkah), deploy cleanup MSG_BUFFER, loop UNKNOWN→FAQ. Kuartal ini: S4 (caching), health check, git backup, webhook auth. Nanti (>5rb user): migrasi Data Tables/Postgres.

---
*Analisa: Claude, 6 Juli 2026. Sumber perilaku n8n disabled-node: [community.n8n.io/t/9640](https://community.n8n.io/t/disabled-nodes-executing/9640); kuota Sheets API: [developers.google.com/workspace/sheets/api/limits](https://developers.google.com/workspace/sheets/api/limits).*
