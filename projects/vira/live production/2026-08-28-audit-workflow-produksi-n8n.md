# Audit Workflow Produksi n8n — VIRA (TS + PCR + Dashboard)

**Tanggal:** 2026-08-28
**Cakupan:** 13 workflow JSON + 2 snapshot database di 3 folder produksi
**Metode:** ekstraksi struktural penuh (semua node, koneksi, parameter) + pembacaan isi setiap code node & prompt oleh 6 subagent paralel + verifikasi silang manual terhadap file sumber dan snapshot spreadsheet
**Status:** read-only. Tidak ada file workflow yang diubah.

---

## 1. Ringkasan eksekutif

| Dimensi | Skor | Alasan singkat |
|---|---|---|
| Arsitektur & desain | **8/10** | Debounce, HITL 2-lapis, identity resolution, error-notifier berlapis, dashboard multi-tenant — semuanya dirancang matang dan terdokumentasi. Jarang ketemu proyek n8n sedisiplin ini. |
| Efisiensi runtime | **4/10** | 3× full-tab read STATS per pesan masuk di **kedua** bot. PCR tanpa cache sama sekali. Plafon throughput PCR ±6–7 pesan/menit. |
| Keamanan | **3/10** | Secret Kirimi plaintext, HMAC dashboard plaintext, private key GCP di tab CONFIG dan di folder proyek, password hash SHA256 satu putaran. |
| Reusability / template | **5/10** | Config layer PCR bagus tapi setengah jadi; TS tidak punya sama sekali. 6 node identik byte-for-byte antar klien tanpa mekanisme sharing. |
| Reliability | **7/10** | Retry & error-workflow rapi di hampir semua tempat — kecuali justru di workflow yang paling merusak (STATS Cleanup v3). |
| Observability | **6/10** | Error notifier 2 lapis solid, tapi beberapa jalur gagal senyap (rate-limit drop, partial-batch harvester, partial purge). |

**Tiga hal yang harus dikerjakan sebelum yang lain:**

1. **Rotasi semua kredensial + pindahkan ke n8n Credentials.** Secret Kirimi, HMAC dashboard, dan private key service account semuanya ada dalam bentuk plaintext di lokasi yang bisa dibaca orang lain. (§3)
2. **Perbaiki `STATS Cleanup v3` sebelum diaktifkan.** Tanpa `timezone` dan tanpa `errorWorkflow` — kalau purge gagal separuh jalan, tidak ada satu pun notifikasi. (§6)
3. **Tambahkan cache tab statis di PCR + gabungkan 3 read STATS jadi 1.** Ini satu-satunya perubahan yang menaikkan kapasitas PCR dari ±6,6 → ±15 pesan/menit. (§4)

---

## 2. Inventaris & peta dependensi

| Workflow | ID | Aktif | TZ | errorWorkflow | Node | pinData |
|---|---|---|---|---|---|---|
| VIRA TS | `27Nw6efK…` | ✅ | Asia/Jakarta | `ZKsINjA7…` | 56 | — |
| VIRA TS Error Notifier | `ZKsINjA7…` | ✅ | Asia/Jakarta | `xGsl3M3t…` | 7 | — |
| Topic Harvester (WF-A) | `53SnbaFf…` | ✅ | Asia/Jakarta | `ZKsINjA7…` | 10 | — |
| Monthly Rollup (WF-B) | `49Idh3Um…` | ✅ | Asia/Jakarta | `ZKsINjA7…` | 4 | — |
| VIRA - MSG_BUFFER Cleanup | `LkpnapMd…` | ✅ | Asia/Jakarta | `ZKsINjA7…` | 4 | — |
| **STATS Cleanup v3** | `flkj_TqY…` | ❌ | **—** | **—** | 8 | — |
| VIRA PCR AI Powered | `oCQ315OH…` | ✅ | Asia/Jakarta | `rBsq-mGg…` | 84 | ⚠️ |
| VIRA-PCR Error Notifier | `rBsq-mGg…` | ✅ | Asia/Jakarta | `xGsl3M3t…` | 8 | — |
| Follow-up AI Powered | `qaux8b14…` | ✅ | Asia/Jakarta | `rBsq-mGg…` | 23 | ⚠️ |
| VIRA-PCR - MSG_BUFFER Cleanup | `TIt9Ns4H…` | ✅ | Asia/Jakarta | `rBsq-mGg…` | 4 | — |
| **VIRA-PCR - STATS Purge** | `Uqt1M4So…` | ❌ | Asia/Jakarta | `xGsl3M3t…` | 12 | — |
| VIRA Dashboard API | `OMJNTXpi…` | ✅ | Asia/Jakarta | `xGsl3M3t…` | 30 | ⚠️ |
| VIRA Dashboard - DASH_AUDIT Cleanup | `1PClsIt5…` | ✅ | Asia/Jakarta | `xGsl3M3t…` | 12 | — |
| GLOBAL - Email Fallback Notifier | `xGsl3M3t…` | ✅ | Asia/Jakarta | — (sengaja) | 10 | — |

**Rantai error:** workflow TS → TS Error Notifier (WA) → GLOBAL Email Fallback. Workflow PCR → PCR Error Notifier (WA) → GLOBAL Email Fallback. GLOBAL sendiri tidak punya errorWorkflow, jadi tidak ada infinite loop — desainnya benar.

**Dua anomali di peta ini:**

- `STATS Cleanup v3` adalah satu-satunya workflow tanpa `timezone` **dan** tanpa `errorWorkflow`.
- `VIRA-PCR - STATS Purge` melompati PCR Error Notifier dan langsung ke GLOBAL Email. README-nya (`2026-08-27-README-stats-purge.md`) menyebut `errorWorkflow = rBsq-mGgHfqfwbz3YmwxI`, tapi file live berisi `xGsl3M3t…`. Dokumentasi dan file sudah tidak sinkron. Efeknya: kalau purge gagal separuh jalan, notifikasi hanya lewat email, tanpa WA.

**Ukuran data (snapshot xlsx, 2026-08-28):**

| Tab | The Scholars | PCR |
|---|---|---|
| STATS | 1.517 baris × 24 kolom | 1.356 baris × 36 kolom |
| MSG_BUFFER | 3 baris | 1.069 baris |
| FAQ / PROGRAM-PRODUK / LINKS | ±1.000 baris (mayoritas padding kosong) | ±1.000 baris |

> Catatan: angka ±1.000 di banyak tab adalah grid default Google Sheets, bukan data riil. Panduan cleanup v3 mencatat STATS TS sebenarnya berisi **721 baris data** dari 1.515 baris grid. Untuk PCR, MSG_BUFFER 1.069 baris pantas dicek — TS hanya 3 baris dengan kode cleanup yang **identik**.

---

## 3. Temuan keamanan

Ini bagian yang paling mendesak. Semua sudah kuverifikasi langsung dari file, bukan dari ringkasan.

### 3.1 Secret Kirimi plaintext, dipakai bersama dua klien

Nilai `4efe3780…9ce0f2` (64 hex) + `user_code KM40LI0426` di-hardcode plaintext di:

| File | Jumlah kemunculan | Node |
|---|---|---|
| `VIRA TS.json` | 5 | Send WA + Verify, Notify Admin Unknown, Notify Talk to Sam, Send GForm Link, Send GForm Clarify |
| `VIRA TS Error Notifier.json` | 1 | Notify Admin Error |
| `STATS Cleanup v3.json` | 1 | Notify Steven |
| `VIRA-PCR Error Notifier.json` | 1 | Notify Admin Error |

Ditambah **tab CONFIG di PCR_Database baris 27** menyimpan nilai yang sama.

Artinya: satu akun Kirimi dipakai untuk dua klien (beda `device_id` saja — TS `D-4ZV1F`, PCR `D-LM6WE`). Siapa pun yang pegang salah satu file JSON ini bisa mengirim WhatsApp atas nama kedua klien.

Anomali tambahan: **PCR Error Notifier memakai `device_id: D-LM6WE` tapi secret yang di-hardcode**, bukan lewat CONFIG seperti workflow PCR lainnya. Komentar di `Parse Config PRG` sendiri mengklaim *"Kredensial Kirimi tidak pernah ditulis plaintext di node"* — klaim itu tidak berlaku untuk file ini.

### 3.2 Private key Google service account terekspos di tiga tempat

1. **Tab CONFIG PCR_Database baris 30** berisi `-----BEGIN PRIVATE KEY-----` utuh, kolom `keterangan`-nya cuma "JANGAN DIEDIT". Tab ini dibaca workflow setiap pesan masuk. Siapa pun yang punya akses *view* ke spreadsheet — termasuk Om Sulianto atau siapa pun yang pernah di-share — bisa menyalin key ini.
2. `VIRA/vira-506713-9304db011c49.json` — file key `vira-425@vira-506713.iam.gserviceaccount.com`, private key 1704 karakter.
3. `Persada Cisoka Residence/workflow/google service account/vira-persada-ab518094997a.json`

n8n sudah menyimpan kredensial ini di credential store (`QC5aF1Hy…` untuk Persada, `5KD9A3Te…` untuk Dashboard). Salinan plaintext di tab CONFIG dan di folder proyek **tidak dipakai workflow mana pun** — jadi bisa dihapus tanpa efek fungsional.

### 3.3 Dashboard: secret penanda-tangan token plaintext

Node `Sign Token` dan `Verify Token HMAC` di `VIRA Dashboard API.json` menyimpan secret HMAC `3b5c2942…f5db0f` langsung di parameter node — bukan di n8n credential, bukan env var.

Konsekuensinya konkret: siapa pun yang punya file JSON ini bisa membuat token sesi valid untuk user mana pun, termasuk `steven` (role `super`, akses kedua tenant). Ini melewati seluruh mekanisme auth yang sebenarnya sudah dibangun dengan baik (lihat §3.5).

Tambahan: `VIRA_USERS` — username + salt + hash untuk `steven`, `sam`, `sulianto` — ter-inline di **10 code node** karena `build_workflow.py` membundel `tenants.js` ke setiap node. Hash `44cb6fdb…` muncul 10× dalam satu file.

Hashing-nya `SHA256(salt + ':' + password)` satu putaran. Untuk password storage ini terlalu cepat — kalau file bocor, brute-force offline murah. Idealnya PBKDF2/scrypt/bcrypt, tapi node `crypto` n8n tidak menyediakannya; alternatif praktis: naikkan jadi ribuan iterasi SHA256 di code node, atau pindahkan verifikasi ke layer lain.

### 3.4 pinData berisi data live

- `VIRA PCR AI Powered.json` → pinData Webhook berisi lead asli: nomor `628568064176`, nama "Busana", isi pesan, IP `107.155.65.244`.
- `VIRA Dashboard API.json` → pinData berisi **token sesi valid utuh** (195 char payload + 64 char signature) dan `key: 6285155202354`.

Token itu masih bisa dipakai kalau belum kedaluwarsa (`tokenTtlSec = 2592000` = 30 hari). Hapus pinData sebelum file ini pernah di-share ke mana pun.

### 3.5 Yang justru sudah benar di Dashboard

Supaya adil — mekanisme auth dashboard-nya bagus, masalahnya murni penyimpanan secret:

- Perbandingan hash password **dan** signature token pakai `vaSafeEqual` (constant-time XOR) — tidak ada timing oracle.
- Username tak dikenal tetap di-hash dengan salt dummy `'no-such-user'` supaya tidak bisa dipakai enumerasi user.
- Tenant untuk read/toggle **selalu** diambil dari claim token yang sudah ditandatangani (`VIRA_TENANTS[c.t]`), tidak pernah dari body request. `switch_tenant` divalidasi ulang terhadap registry server-side, bukan terhadap daftar tenant di token lama — jadi pencabutan akses langsung berlaku.
- CORS allowlist (bukan wildcard). `sheetId` tidak pernah masuk ke response.
- Login lockout 5 gagal / 15 menit.

Tidak ada risiko kebocoran lintas-tenant di logika aplikasinya. Risikonya murni: kalau secret HMAC bocor, seluruh lapisan itu bisa dilewati sekaligus.

### 3.6 Data finansial di tab CONFIG TS

Tab CONFIG The Scholars berisi `NAMA_BANK: BCA`, `NOMOR_REKENING`, `ATAS_NAMA: Samuel Oscar`, `NOMINAL_BIAYA: 1.000.000`. Bukan secret teknis, tapi rekening penerimaan pembayaran klien — perlakukan aksesnya setara.

Menariknya, **tidak ada node di `VIRA TS.json` yang membaca tab CONFIG.** Nilai-nilai ini rupanya ditulis manual ke dalam system prompt. Kalau nomor rekening berubah, prompt harus diedit, bukan sheet — jebakan maintenance.

---

## 4. Efisiensi

### 4.1 Google Sheets I/O — masalah terbesar

Terverifikasi langsung: dari 19 node Sheets di TS dan 21 di PCR, **tidak satu pun read STATS memakai filter** kecuali `Re-Read STATS Debounce`. Semuanya full-tab read lalu difilter di JavaScript.

**Panggilan Sheets per satu pesan WhatsApp masuk:**

| | TS (cache hit) | TS (cache miss) | PCR (selalu) |
|---|---|---|---|
| Read | 5 | 9 | **9** |
| Write | 4–5 | 4–5 | 4–5 |
| **Total** | **9** | **13–14** | **13–14** |

Kuota Google Sheets: **60 read/menit per user per project**.

- PCR: 60 ÷ 9 = **±6,6 pesan/menit** sebelum kena rate limit. Komentar di kode Dashboard sendiri sudah mencatat *"Bot Persada sudah mendekati plafon 60 read/menit"* — jadi ini bukan teori.
- TS: 60 ÷ 5 = ±12 pesan/menit (cache hit), ±6,6 (cache miss).

Tiga read STATS itu berturut-turut membaca **tab yang sama** dalam satu eksekusi, terpisah beberapa detik:

| Node | Kenapa ada | Bisa dihapus? |
|---|---|---|
| `Read User STATS` | resolusi identitas user | Perlu — tapi seharusnya filtered, bukan full |
| `Read STATS for HITL` | cek `bot_mode` sebelum Wait3 | Bisa pakai hasil read #1 |
| `Read STATS` (rantai Extract & Prepare) | hitung ulang Counter/Intensitas | Bisa pakai `Re-Read STATS Debounce` yang sudah filtered |

Kalau ketiganya digabung jadi **satu filtered read** (pola `filtersUI` yang sudah terbukti jalan di `Re-Read STATS Debounce` dan `Read MSG_BUFFER`):

- PCR: 9 read → 4 read = **±15 pesan/menit** (+127%)
- TS: 5 read → 3 read = **±20 pesan/menit** (+67%)

Ditambah efek sekunder: full-tab read STATS 1.500 baris × 24–36 kolom memakan 1–3 detik per panggilan. Menghapus dua di antaranya memotong 2–6 detik dari latensi setiap balasan.

### 4.2 PCR tidak punya cache, TS punya

TS punya `Cache Check` → `IF Cache Fresh` → `Cache Store` dengan TTL 120 detik untuk FAQ / PROGRAM / ABOUT_SAM / LINKS. PCR **membaca FAQ, PRODUK, dan LINKS penuh setiap pesan** tanpa cache apa pun.

Tiga node cache TS itu total 2.477 karakter kode. Menyalinnya ke PCR adalah pekerjaan setengah jam dan langsung memotong 3 read/pesan.

Catatan kecil di TS: `Read ABOUT Data` dibaca tanpa syarat, padahal `askingAboutSam` sering `false` dan hasilnya tidak dipakai.

### 4.3 Tiga write terpisah ke baris STATS yang sama

Setiap pesan menulis ke baris STATS yang sama sebanyak 3–4 kali dalam satu siklus:

- TS: `Update Buffer` → `Delete_Pending_Msg` → `Update to STATS` (+ `Update Greeting` untuk user baru)
- PCR: `Update Buffer` → `Mark Buffer Consumed (Regular)` → `Update to STATS` (+ `Update Greeting`)

`Update Buffer` harus tetap terpisah (penanda debounce ditulis *sebelum* Wait3). Tapi `Delete_Pending_Msg`/`Mark Buffer Consumed`, `Update to STATS`, dan `Update Greeting` semuanya terjadi setelah balasan terkirim ke baris yang sama — bisa digabung jadi **satu** `appendOrUpdate`. Hemat 2 write/pesan, dan menghilangkan window di mana baris STATS setengah ter-update kalau salah satu write gagal.

### 4.4 Latensi: debounce 60 detik

`Wait3` = 60 detik fixed di **kedua** bot (tanpa parameter `unit`, jadi default detik). `Wait1` = 5–10 detik jitter sebelum kirim.

Total latensi balasan per pesan: **60 + waktu AI (5–15 dtk) + 5–10 = ±70–85 detik.**

Debounce-nya jalan benar — pesan beruntun digabung dan eksekusi lama mematikan diri. Tapi konsekuensinya: user yang mengirim **satu** pesan tetap menunggu 60 detik penuh. Untuk bot telemarketer yang KPI-nya konversi survey, ini terasa lama.

Dua hal:
- CONFIG PCR sudah punya key `debounce_seconds: 60`, tapi **node `Wait3` meng-hardcode `60`** dan tidak pernah membacanya. Config drift.
- 12–20 detik biasanya sudah cukup untuk menangkap pesan beruntun WhatsApp. Turunkan ke 15 detik dan latensi jadi ±25–40 detik.

Efek samping teknis: n8n menyimpan eksekusi Wait <65 detik di memori (tidak di-offload ke DB). Dengan 60 detik, setiap percakapan aktif memegang slot eksekusi selama satu menit penuh.

### 4.5 Biaya AI — prompt caching belum dipakai

| | TS | PCR |
|---|---|---|
| Model | `claude-sonnet-4-6` | `claude-sonnet-4-5-20250929` |
| System prompt | 17.887 char (±4.500–5.100 token) | 17.731 char (±4.400–5.500 token) |
| max_tokens | 512 | 1024 |
| temperature | 0.7 | 0.4 |
| Memory window | 10 | 10 |

System prompt keduanya **100% statis** — tidak ada variabel per-user di dalamnya; konteks dinamis (`data_context`, `faq_context`) ditempel di ekor. Tapi **tidak ada `cache_control` di mana pun**, jadi ±4.500 token yang persis sama dikirim ulang penuh setiap pesan.

Estimasi per panggilan: 5.600–9.000 token input, output ≤512–1024. Dengan prompt caching (breakpoint tepat sebelum ekor dinamis), ±4.500 token itu masuk tarif cache — hemat besar pada volume harian.

Kendala: node `lmChatAnthropic` n8n mungkin belum mengekspos opsi cache_control. Perlu dicek versi node terpasang; kalau belum ada, alternatifnya panggil Messages API lewat HTTP Request node (pola yang sudah dipakai `Topic Harvester`).

**Version drift:** TS di Sonnet 4.6, PCR masih di Sonnet 4.5. Tidak salah, tapi tidak disengaja.

**Ketidakcocokan di Follow-up:** komentar `Parse Config FU` menyebut *"AI aktif = composer Haiku"*, tapi node yang terpasang `claude-sonnet-4-5-20250929`. Follow-up jalan tiap jam, sampai 20 lead/run. Kalau maksudnya memang Haiku, ini kelebihan biaya yang berjalan diam-diam sejak entah kapan.

### 4.6 Ukuran file & duplikasi bundle Dashboard

`VIRA Dashboard API.json` = 307 KB, dengan 278 KB berupa kode di 14 code node. Rasio baris identik antar-node 0.93–0.99; `Build Stats Response` dan `Find Row` berbagi 1.077 dari ±1.115 baris pertama.

**Ini bukan copy-paste manual** — file di-generate oleh `VIRA/VIRA Dashboard/2026-07-28-production/n8n/build_workflow.py` dari `src/tenants.js`, `src/auth.js`, `src/build-payload.js`. Single source of truth-nya ada dan benar. Jadi duplikasinya artefak bundling, bukan utang teknis.

Yang tetap perlu diperhatikan: n8n mem-parse ±20–45 KB JS per code node per request; satu request `stats` melewati ±6 code node = ±150 KB JS di-parse per request. Dan editor n8n berat membuka file 307 KB. `Find Row` mengangkut seluruh `build-payload.js` padahal hanya butuh `vdPick`/`vdDigits` — kalau `build_workflow.py` bisa memilih modul per node, ukuran file turun drastis tanpa mengubah arsitektur.

**Yang perlu dicatat:** TS dan PCR **tidak punya** build pipeline seperti ini. Justru mereka yang paling butuh.

---

## 5. Duplikasi & jawaban soal "digabung jadi 1 general workflow"

### 5.1 Bukti duplikasi (hash & rasio, bukan perkiraan)

**Node yang byte-identical antara TS dan PCR** (rasio 1.000):

| Node | Ukuran |
|---|---|
| `Chat Counter` | 2.079 char |
| `Extract & Prepare Data` | 773 char |
| `Rate Limiter LID` | 1.078 char |
| `Update STATS - Greeting Flag` | 726 char |

**Hampir identik:**

| Node | Rasio | Beda |
|---|---|---|
| `HITL Check` | 0.994 | 4 karakter |
| `Send WA + Verify (Kirimi)` | 0.967 | komentar |
| `Process Counter & Merge Data` | 0.831 | kolom slot |
| `Resolve User Row` | 0.605 | **hanya komentar + daftar kolom slot** — logikanya identik (diff manual terlampir di §5.2) |

**Workflow satelit yang praktis kembar:**

| Pasangan | Bukti |
|---|---|
| `MSG_BUFFER Cleanup` TS vs PCR | node `Pick expired block (>2h)` **md5 sama persis** (`f0555bc946`, 1.793 char). Beda cuma doc_id. |
| `Error Notifier` TS vs PCR | `Check Kirimi Response` md5 sama persis. `Compose Notif` beda 4 char, `Build Fallback Payload` beda 1 char (string `TENANT`). |

`Build Fallback Payload` bahkan menyimpan komentar `// >>> GANTI sesuai workflow: 'VIRA-PCR' atau 'VIRA-SCHOLARS' <<<` — jadi memang sudah disadari sebagai template yang di-copy per tenant.

**Node yang benar-benar milik klien** (rasio rendah = beda beneran): `AI Agent` (0.030), `Process All` (0.087), `Preprocess - Context Detection` (0.117), `FAQ Retrieve` (0.179), `Cek_user_status` (0.298).

### 5.2 `Resolve User Row` — kabar bagus

Node paling kritis (prinsip "No WA primary, lid backup, never rows[0]") sudah **konsisten sempurna** antara TS dan PCR. Logikanya baris-per-baris sama:

```js
if (phone) row = rows.find(r => digits(r['No WA']) === phone) || null;
if (!row && lid) {
  row = rows.find(r => digits(r['lid']) === lid) || rows.find(r => digits(r['No WA']) === lid) || null;
}
const resolvedKey = row ? String(row['No WA']).trim() : (phone || lid);
```

Yang berbeda hanya daftar kolom yang di-hidrasi di akhir: TS mengembalikan `kelas_anak`/`program_interest`, PCR mengembalikan `unit_interest`/`budget_range`/`lokasi_kerja`/`pending_survey_*`.

Artinya node ini = **logika generik + daftar field per klien**. Persis bentuk yang cocok untuk config-driven `SLOT_FIELDS`.

### 5.3 Rekomendasi: jangan gabung jadi satu workflow raksasa

Menggabungkan `VIRA TS` (56 node) dan `VIRA PCR` (84 node) jadi satu workflow bercabang tenant akan menghasilkan ±120 node dengan percabangan `if tenant == …` di mana-mana. Setiap perubahan untuk satu klien berisiko ke klien lain, dan blast radius insiden jadi dua kali lipat. Itu mundur, bukan maju.

**Yang benar: ekstrak yang generik, biarkan yang spesifik terpisah.** Empat lapis, urut dari yang paling murah:

**Lapis 1 — Sub-workflow `GLOBAL - Kirimi Send` (paling mudah, dampak paling luas)**

Body POST Kirimi yang identik (`user_code`/`secret`/`device_id`/`phone`/`message`) muncul **minimal 13×** di seluruh stack: 5× di VIRA TS, 7× di PCR (5 node + media), 3× di Follow-up, 1× di masing-masing Error Notifier, 1× di tiap workflow cleanup.

Satu sub-workflow yang menerima `{tenant, phone, message}`, membaca kredensial dari CONFIG, dan mengembalikan status terverifikasi akan:
- menghapus 13 salinan
- **sekaligus menyelesaikan §3.1** — tidak ada lagi secret plaintext di node
- menyeragamkan verifikasi respons (saat ini hanya `Send WA + Verify` yang memeriksa body Kirimi; `Notify Admin Unknown` dan `Notify Talk to Sam` menganggap HTTP 200 = sukses padahal Kirimi bisa balas 200 dengan isi gagal — masalah yang **sudah** ditemukan dan diperbaiki di Error Notifier, tapi belum di-backport)

Polanya sudah terbukti: `Call Global Email Fallback` memakai `executeWorkflow` persis seperti ini.

**Lapis 2 — Gabungkan workflow maintenance jadi 1 per jenis, iterasi tenant**

Contoh yang **sudah ada dan bekerja**: `VIRA Dashboard - DASH_AUDIT Cleanup` memakai `Fan Out Tenants` → `Loop Over Tenants` → read/delete per tenant → `Ringkasan`. Sticky note-nya sendiri menulis: *"Tambah klien ke-3 = tambah 1 baris di node Fan Out Tenants. Node lain tidak perlu disentuh."*

Terapkan pola yang sama ke:
- `MSG_BUFFER Cleanup` TS + PCR → **1 workflow** (kodenya sudah byte-identical, hanya perlu doc_id dari array tenant)
- `STATS Cleanup v3` + `STATS Purge` → **1 workflow** dengan aturan retensi per tenant di CONFIG (aturannya memang beda — TS melindungi baris OFF, PCR tidak — tapi itu parameter, bukan kode)

Dari 4 workflow jadi 2, dan klien ke-3 nanti = tambah 1 baris.

**Lapis 3 — Satu Error Notifier**

TS dan PCR Error Notifier beda 5 karakter total. Yang membedakan hanya string `TENANT`. n8n memberi nama workflow asal di payload `errorTrigger`, dan `GLOBAL - Email Fallback Notifier` **sudah** mendeteksi tenant dari nama itu:

```js
if (hay.includes('pcr') || hay.includes('persada')) tenant = 'VIRA-PCR';
else if (hay.includes('scholar') || hay.includes('v4')) tenant = 'VIRA-SCHOLARS';
```

Logika yang sama bisa dipindah ke satu notifier WA bersama. 2 workflow → 1.

Sekalian perbaiki: notifier global saat ini mengirim **semua** alert tenant ke satu inbox `stevenleroy0@gmail.com` — hardcoded di keempat jalur kirim. Kalau nanti Om Sulianto perlu dapat alert sendiri, ini butuh ubah kode, bukan ubah data.

**Lapis 4 — Build pipeline untuk bot utama (paling berat, paling bernilai jangka panjang)**

Ini sebenarnya sudah ada polanya: `build_workflow.py` + `src/*.js` yang membangun Dashboard API. Terapkan konsep yang sama ke bot:

- `src/engine.js` — `Chat Counter`, `Resolve User Row`, `Rate Limiter LID`, `HITL Check`, `Send WA + Verify`, rantai debounce, `Update STATS - Greeting Flag`, `Extract & Prepare Data`, `Process Counter & Merge Data`, `Cache Check`/`Cache Store`
- `src/tenants/thescholars.js` dan `src/tenants/persada.js` — system prompt, `Preprocess`, `FAQ Retrieve`, `Process All`, `SLOT_FIELDS`, doc_id, nama tab

Hasilnya tetap 2 workflow terpisah di n8n (blast radius tetap terisolasi), tapi lapisan enginenya satu sumber. Perbaikan bug identitas atau debounce cukup sekali, lalu rebuild keduanya.

**Berapa yang sebenarnya bisa dibagi?** Dari ±97 KB kode di TS, ±16 KB adalah node yang identik/nyaris identik dengan PCR. Kelihatannya kecil (16%), tapi itu **seluruh lapisan plumbing** — webhook → identitas → rate limit → buffer → debounce → HITL → kirim → verifikasi. Yang tidak bisa dibagi (AI prompt, `Process All`, `Preprocess`, `FAQ Retrieve`) memang seharusnya tidak dibagi: itu logika bisnis klien.

### 5.4 Duplikasi dalam satu workflow

**PCR — blok media ganda.** `IF Send Media` → `Wait Media` → `Download Media` → `Send Media Kirimi`, lalu `IF Send Media 2` → `Wait Media 2` → `Download Media 2` → `Send Media Kirimi 2`. Delapan node untuk mengirim maksimal dua media. Kalau nanti butuh media ketiga, jadi 12 node. Bentuk yang benar: satu `splitInBatches` atas array media.

**PCR — resolusi identitas ditulis ulang 4×.** Algoritma `digits(phone) → lid → No WA==lid` diimplementasi terpisah di `Resolve User Row`, `HITL Check`, `Cek_user_status`, dan `Process Counter & Merge Data`. **TS: 3×** (tiga node pertama). Kalau aturan matching berubah, harus diedit di 3–4 tempat manual — persis kelas bug yang dulu menyebabkan insiden Vivipoh/DSS.

**PCR — perhitungan "sekarang WIB" ditulis ulang 3×** (`Cek_user_status`, `Preprocess`, `Process All`).

**TS — `bulanWIB()` diduplikasi** antara Topic Harvester dan Monthly Rollup.

**PCR — `stripMd()` diduplikasi** antara `Format Handover Message` dan `Merge Konteks`.

Sebagian besar ini tidak terhindarkan tanpa build pipeline (code node n8n tidak bisa impor modul). Tapi pola "hitung sekali, teruskan lewat `$json`" **sudah dipakai** di workflow yang sama untuk `resolved_key` — jadi ini inkonsistensi, bukan keterbatasan platform.

---

## 6. Review pra-aktivasi: dua workflow yang mau kamu jalankan tanggal 1

Kamu bilang keduanya sengaja belum aktif dan mau di-run manual tanggal 1. Ini review khususnya.

### ⚠️ 6.0 Cron-nya tidak akan menyala 1 September

Ini yang paling penting dan mungkin belum kamu sadari:

| Workflow | Cron | Bulan yang aktif |
|---|---|---|
| STATS Cleanup v3 | `1 0 1 */3 *` | Jan, Apr, Jul, **Okt** |
| VIRA-PCR STATS Purge | `30 2 1 */3 *` | Jan, Apr, Jul, **Okt** |
| DASH_AUDIT Cleanup | `0 2 1 1,4,7,10 *` | Jan, Apr, Jul, Okt |

`*/3` di field bulan berarti 1,4,7,10 — **bukan** "tiap 3 bulan dari sekarang". **September tidak termasuk.** Jadi:

- Run manual kamu tanggal 1 September: jalan (Execute Workflow manual mengabaikan cron). ✅
- Run otomatis berikutnya: **1 Oktober 2026**, bukan 1 Desember.

Kalau yang kamu mau memang kuartal kalender (Jan/Apr/Jul/Okt), tidak ada yang perlu diubah — cuma perlu tahu bahwa jeda dari run manual September ke otomatis Oktober cuma 1 bulan.

### 6.1 `STATS Cleanup v3` (The Scholars) — 3 hal harus dibereskan dulu

**Kualitas logikanya bagus.** Panduan `2026-08-27-VIRA-STATS-cleanup-v3-panduan.md` menunjukkan QA 72 PASS/0 FAIL, sudah dijalankan manual terhadap sheet live 2026-08-27, dan 10 metrik cocok persis dengan port Python. Aturan retensinya konservatif dan benar: baris `bot_mode=OFF` non-VIRA dilindungi selamanya, baris tanpa jejak waktu **tidak** dihapus, umur diambil dari nilai terbesar 5 kolom timestamp (dengan normalisasi per-nilai `n > 1e12 ? n/1000 : n` karena unit kolomnya campur detik/milidetik). Tiga guard `throw` yang membatalkan seluruh penghapusan kalau skema tidak cocok. Penghapusan blok kontigu dari bawah ke atas. Semua benar.

Yang perlu diperbaiki:

**A. `settings` tidak lengkap — ini blocker.**

```json
{"executionOrder": "v1", "availableInMCP": false}
```

Tidak ada `timezone`, tidak ada `errorWorkflow`. Semua 12 workflow lain punya keduanya.

- Tanpa `timezone`, cron `1 0 1 */3 *` jalan di timezone default instance n8n. Kalau instance-nya UTC, "00:01 WIB" sebenarnya jadi **07:01 WIB**.
- Tanpa `errorWorkflow`, kalau `Delete STATS rows` gagal di blok ke-3 dari 5, blok 1–2 sudah terhapus permanen, eksekusi berhenti sebelum `Collapse to one` → `Notify Steven`, dan **tidak ada satu pun notifikasi**. Sheet tinggal setengah bersih, kamu tidak tahu.

Fix: tambahkan `"timezone": "Asia/Jakarta"` dan `"errorWorkflow": "ZKsINjA7ZC8c9yRHWp3ud"` (TS Error Notifier).

**B. Tidak ada dry-run.** PCR Purge punya `stats_purge_dry_run`. Yang ini tidak punya sama sekali. `RETENTION_DAYS = 90` di-hardcode di baris awal `Plan cleanup`, dan panduannya sendiri mengakui ini (§7: *"Tidak dibaca dari CONFIG seperti Persada"*).

Untuk run manual pertama, workaround aman: ubah sementara `RETENTION_DAYS` jadi angka sangat besar (misal `99999`) → `deleteCount` jadi 0 → cabang false → notifikasi tetap terkirim dengan laporan lengkap. Baca laporannya, baru kembalikan ke 90.

**C. Laporan dikirim setelah hapus, bukan sebelum.** `Notify Steven` ada di ujung, jadi fungsinya kuitansi, bukan gerbang persetujuan. Digabung dengan poin B, run pertama sebaiknya kamu perlakukan sebagai dry-run manual.

**Proyeksi dari panduan** (data 2026-08-27, 721 baris): run 1 Oktober akan menghapus **±76 baris**; run 1 Januari 2027 ±329 baris. Per 2026-08-27, `deleteCount = 0` karena belum ada baris berumur >90 hari.

### 6.2 `VIRA-PCR - STATS Purge` — 4 hal, satu di antaranya bikin run pertama menghapus beneran

**Rekayasanya lebih matang dari versi TS**: ada config layer, ada dry-run, ada guard skema (`No WA` + `last_reply_ts` wajib ada, kalau tidak → `throw`, penghapusan dibatalkan), retry 3×/5 detik di node delete, peringatan kuota kalau >40 blok, penghapusan blok kontigu dari bawah ke atas. README-nya (`2026-08-27-README-stats-purge.md`) sangat jujur soal apa yang tidak dilindungi.

**A. ⚠️ Dry-run tidak akan menyala di run pertama.**

README langkah 3 menyuruh: *"Run pertama = DRY RUN. Isi CONFIG `stats_purge_dry_run` = Y."*

Aku cek isi tab CONFIG PCR (33 baris): **key `stats_purge_dry_run` dan `stats_purge_retention_days` belum ada.** Tanpa key itu, `Parse Config PRG` jatuh ke default — dan default `dry_run` adalah **N** (empty = false).

**Jadi kalau kamu Execute Workflow tanggal 1 tanpa menambah key itu dulu, penghapusan langsung nyata dan permanen.**

Fix, urutan wajib:
1. Tambah baris di tab CONFIG: `stats_purge_dry_run` | `Y`
2. (opsional) `stats_purge_retention_days` | `90`
3. Duplicate tab STATS sebagai backup — README menyebut ini *"satu-satunya jaring pengaman"*
4. Baru Execute Workflow, baca laporan WA-nya
5. Kalau angkanya masuk akal → ubah ke `N` → run lagi

**B. `maintenance_phone` di CONFIG adalah dead code.**

`Parse Config PRG` menghitung `reportPhone = digits(cfg.maintenance_phone) || digits(cfg.admin_phone)`. Tapi node `Notify Maintenance` **meng-hardcode** `"phone": "=6285155202354"`.

Terverifikasi: string `report_phone` muncul **1×** di seluruh file — hanya di definisinya sendiri, tidak pernah dibaca. Mengubah `maintenance_phone` di CONFIG tidak akan berpengaruh apa pun. Laporan selalu ke nomormu sampai node-nya diedit langsung.

**C. errorWorkflow tidak sesuai README.**

README menyebut `rBsq-mGgHfqfwbz3YmwxI` (PCR Error Notifier, jalur WA). File live berisi `xGsl3M3tONsHPDgT9lOWF` (GLOBAL Email Fallback).

Efeknya: kalau purge gagal di tengah, kamu hanya dapat email — bukan WA — dan email itu berisi payload error generik n8n yang **tidak menyebutkan blok mana yang sudah terhapus dan mana yang belum**. Untuk workflow paling destruktif di seluruh stack, ini justru jalur alert paling tipis. Ubah ke `rBsq-mGgHfqfwbz3YmwxI`.

**D. Baris tanpa `last_reply_ts` ikut terhapus — pastikan ini masih yang kamu mau.**

`KEEP_WHEN_EMPTY = false`. Terverifikasi di file. README mendokumentasikannya sebagai keputusan sadar 2026-08-27, jadi ini bukan bug — tapi konsekuensinya: **lead hasil impor telemarketer yang belum pernah dibalas VIRA akan hilang di run pertama.**

Ini beda tajam dari versi TS, yang justru melindungi baris tanpa jejak (di TS, 103 baris tanpa timestamp semuanya `bot_mode=OFF` — kontak Sam). Kalau di PCR ada blok lead impor serupa, dry-run di poin A akan menunjukkannya di baris `last_reply_ts kosong : N`. **Baca angka itu sebelum lanjut.**

**E. Pastikan `VIRA-PCR - STATS Archive 3bulan` tetap non-aktif.**

Sudah kuverifikasi: file di `2026-08-25-stats-archive/` berstatus `active: false`. ✅ Cron-nya di tanggal yang sama (02:00 vs 02:30). Kalau keduanya hidup, dua workflow menghapus baris STATS di pagi yang sama.

### 6.3 Bonus: `DASH_AUDIT Cleanup` yang **sudah aktif** perlu kamu lihat

Workflow ini aktif sekarang, dan `RETENTION_DAYS = 0`. Komentarnya sendiri menjelaskan: *"hapus SEMUA baris data, sisakan header saja."*

Jadi ini bukan retensi bergulir — ini **wipe total riwayat audit dashboard kedua tenant setiap kuartal.** Cabang `RETENTION_DAYS = 90` ada di kode tapi tidak aktif.

Kalau memang disengaja, tidak apa-apa. Kalau kamu mengira ini memangkas audit >90 hari, ubah konstanta itu ke `90`.

Dua catatan lain:
- Node `Test manual` masuk ke `Fan Out Tenants` yang sama dengan doc_id produksi. **Menjalankan "test" = wipe produksi nyata.** Tidak ada sheet staging.
- Tidak ada arsip/backup/dry-run sebelum delete.

Ditambah dari Dashboard API: `DASH_AUDIT` hanya mencatat aksi `toggle_user`. Aksi `login` (termasuk lockout) dan `switch_tenant` **tidak diaudit sama sekali**. Jadi tiap kuartal, satu-satunya jejak yang ada pun dihapus total.

---

## 7. Bug & risiko lain, per workflow

### VIRA TS

| # | Temuan | Dampak | Prioritas |
|---|---|---|---|
| 1 | **Cabang GForm zombie.** `IF Send GForm` (aktif) → 4 node `disabled` → `Update GForm Sent TS1` (**aktif**, googleSheets update). Node disabled di n8n meneruskan input apa adanya, jadi tiap AI mengeluarkan `[SEND_GFORM]`, `gform_sent_ts` tetap ditulis ke STATS padahal tidak ada link yang dikirim lewat jalur itu (link asli datang dari logika inline di `Process All`). | Timestamp palsu di STATS + 1 write kuota terbuang | **Tinggi** — hapus 5 node cabang ini |
| 2 | **Pesan kena rate-limit hilang tanpa jejak.** `Rate Limiter LID` `return []` untuk pesan ke-6+ dalam 60 detik: tidak masuk MSG_BUFFER, tidak digabung ke balasan mana pun, tidak ada notifikasi admin. | Kehilangan pesan senyap | **Tinggi** |
| 3 | **`$vars.chatCounter` no-op.** `Chat Counter` melakukan `$vars.chatCounter = counter` — `$vars` di n8n read-only, jadi assignment ini tidak persist. Field `chat_counter` juga tidak dibaca node mana pun. | Kode mati | Rendah |
| 4 | **`ai_input_text` dari `Chat Counter` tidak pernah dipakai** — ditimpa `Cek_user_status` lalu `Preprocess`. | Kode mati | Rendah |
| 5 | **Verifikasi respons Kirimi tidak konsisten.** Hanya `Send WA + Verify` yang memeriksa body. `Notify Admin Unknown` dan `Notify Talk to Sam` menganggap HTTP 200 = sukses. Padahal Error Notifier **sudah** memperbaiki kelas bug ini (`Check Kirimi Response`) — tapi belum di-backport. | Notifikasi admin bisa gagal senyap | **Tinggi** (selesai otomatis kalau §5.3 Lapis 1 dikerjakan) |
| 6 | Penamaan menyesatkan: `Delete_Pending_Msg` tidak menghapus apa pun — dia `update` kolom `buffer_done_ts`. | Kebingungan maintenance | Rendah |
| 7 | `follow_up_count` ditulis sebagai string kosong tiap pesan (`"={{ \"\" }}"`) — kolom sisa fitur lama. | Write sia-sia | Rendah |
| 8 | `IF (Whitelist)` disabled dengan 5 nomor hardcoded — gerbang UAT yang sudah dilewati. | Berat mati | Rendah |
| 9 | Instruksi prompt "Balas non-teks → ..." tidak akan pernah jalan; `Chat Counter` sudah memfilter non-teks (`return []`) sebelum AI. | Token prompt terbuang | Rendah |

### VIRA PCR

| # | Temuan | Dampak | Prioritas |
|---|---|---|---|
| 1 | **Tidak ada cache** untuk FAQ/PRODUK/LINKS — 3 full read/pesan. TS sudah punya. | Kapasitas | **Tinggi** |
| 2 | **`Bootstrap Config` dead code.** `SHEET_ID = '1dJWq7iq5PRG…'` diproduksi, masuk `config.sheet_id`, dan **tidak dibaca satu pun dari 21 node Sheets** — semuanya hardcode `1pzGuRZb…` lewat resource-locator (32 kemunculan literal). Ironisnya node ini dibuat justru supaya clone-per-klien cukup ubah satu tempat. | Config layer palsu untuk nilai terpenting | **Tinggi** |
| 3 | **`rate_limit_max` / `rate_limit_window_sec` / `debounce_seconds` di CONFIG tidak pernah dibaca.** `Rate Limiter LID` hardcode `5`/`60000`; `Wait3` hardcode `60`. | Config drift — ubah CONFIG tidak berefek | Sedang |
| 4 | **`Notify Admin Unknown` dan `Notify Talk to Admin` tanpa retry & tanpa `onError`.** Satu kegagalan transient Kirimi menggagalkan **seluruh eksekusi** — padahal balasan ke user mungkin sudah terkirim di cabang paralel. Inkonsisten dengan `Notify Media Team`/`Notify Field Team` yang pakai `continueRegularOutput`. | Eksekusi merah palsu | Sedang |
| 5 | **Blok media diduplikasi** (8 node untuk 2 media). | Maintenance | Sedang |
| 6 | **Notifikasi tim bisa tiba sebelum balasan user.** `Process All` bercabang 6; notifikasi internal langsung, balasan user lewat `Wait1` 5–10 detik. | Kejanggalan UX untuk tim | Rendah |
| 7 | **10 sticky note isinya cuma `DONE`** — penanda checklist migrasi, bukan dokumentasi. | Berat mati | Rendah |
| 8 | Race `appendOrUpdate` untuk user benar-benar baru: dua pesan dalam ratusan milidetik bisa menghasilkan **dua baris STATS duplikat**. Tidak ada guard. | Korupsi data (jarang) | Sedang |
| 9 | pinData berisi lead asli (nomor, nama, isi pesan, IP). | Privasi | **Tinggi** |

### Debounce — risiko yang berlaku di kedua bot

Mekanismenya benar secara desain, tapi ada satu jendela yang layak dicatat karena berhubungan dengan investigasi pesan hilang Adrian:

`Update Buffer` memakai `appendOrUpdate` tanpa compare-and-swap. Dua pesan yang datang berdekatan sama-sama menulis kolom `timestamp`. Yang menang adalah tulisan yang **secara fisik mendarat terakhir di server Google** — belum tentu yang `process_start_ts`-nya lebih besar, kalau latensi jaringan membalik urutan.

Kalau eksekusi yang "salah" (lebih tua) yang menang perbandingan string, maka `myTs`-nya lebih kecil dari `ts` pesan terbaru, dan filter `r.ts <= myTs` di `Cek_user_status` **mengeluarkan isi pesan terbaru dari penggabungan**. Pesan itu tidak terjawab.

Tambahan: perbandingan `IF_Chat_Debounce` adalah **string equals** antara nilai yang pulang-pergi lewat Google Sheets dan integer `Date.now()` mentah. Kalau Sheets pernah mengembalikan format berbeda (misal notasi lokal), perbandingan selalu gagal dan debounce mati diam-diam — setiap pesan dibalas sendiri-sendiri.

Perbaikan yang mungkin, terurut dari yang paling murah:
1. Ubah operator jadi numeric equals (menghilangkan risiko format).
2. `bot_mode` tidak dicek ulang tepat sebelum `Send WA` — kalau Sam/admin mematikan bot selama panggilan LLM (1–5 detik), balasan tetap terkirim. Cek ketiga di `Cek_user_status` sudah menutup sebagian, tapi tidak seluruhnya.
3. Untuk anti-race sesungguhnya perlu tie-break tambahan (misal execution ID) selain timestamp.

### Topic Harvester (WF-A)

- **Kehilangan data senyap pada kegagalan sebagian.** Kalau sebagian batch gagal di-parse (`parseLabels` → `null`), pesan-pesan itu di-skip (`failedBatches++; continue`), **tapi `Update Watermark` tetap maju ke `new_watermark` global** yang mencakup timestamp batch yang gagal. Pesan itu tidak akan pernah di-retry. Guard `throw` yang ada hanya menangkap kasus **semua** batch gagal.
- **Kopling ke MSG_BUFFER Cleanup.** Harvester jalan 01/07/13/19, cleanup menghapus baris >2 jam tiap 03:00. Kalau run 01:00 gagal, baris sebelum 01:00 bisa terhapus pukul 03:00 sebelum run 07:00 sempat memanennya. Hilang permanen dari analytics.
- `TOPIC_LOG` tumbuh selamanya, tidak ada yang memangkasnya, dan dibaca penuh 4×/hari oleh Harvester + 1×/bulan oleh Rollup.
- API key Anthropic dipanggil lewat HTTP Request langsung (`api.anthropic.com`) — perlu dipastikan pakai credential n8n, bukan header literal.

### Follow-up AI Powered

- **Tidak ada penanganan stop-word / opt-out.** Satu-satunya jalan keluar adalah `bot_mode=off` atau `survey_status=scheduled`, yang di-set workflow lain. Kalau lead mengetik "stop"/"jangan hubungi lagi" tapi bot utama tidak membalik salah satu flag itu, Follow-up **akan tetap mengirim lagi** setelah `followup_interval_hours` (default 72 jam) lewat. Untuk outbound telemarketing, ini risiko keluhan yang nyata.
- **Model mismatch** — komentar bilang Haiku, node terpasang Sonnet 4.5 (§4.5).
- `Rollback STATS FU` pakai `onError: continueRegularOutput` + retry 3×. Kalau rollback-nya sendiri gagal setelah retry, baris tetap ter-*claim* (`last_follow_up_ts` naik) padahal pesan tidak pernah terkirim — jejaknya cuma `console.warn`. Lead itu diam-diam melewatkan satu siklus follow-up.
- `followup_max = 0` di CONFIG = tanpa batas. Terdokumentasi sebagai keputusan tim 2026-07-17, jadi bukan bug — tapi digabung dengan tidak adanya stop-word, seorang lead bisa dikejar tanpa akhir.
- Update dicocokkan dengan `matchingColumns: ["No WA"]`. Kalau STATS punya `No WA` duplikat (lihat risiko race di PCR #8), update jadi ambigu.

### Dashboard API

- **`Update Bot Mode` tanpa `onError`/`alwaysOutputData`.** Ini satu-satunya write yang benar-benar mengubah data. Kalau gagal (kuota, jaringan), eksekusi berhenti **sebelum** mencapai `Respond`. Karena `responseMode: responseNode`, klien tidak menerima JSON apa pun — request menggantung sampai timeout webhook, bukan error yang rapi. Node saudaranya di jalur `stats` (`Read Tab`) sudah pakai `continueRegularOutput`; yang ini terlewat.
- **Endpoint `stats` = N full-tab read berurutan** (5 tab untuk thescholars, 4 untuk persada) lewat `splitInBatches` batch=1, jadi strictly serial. Cache 60 detik meredam, tapi ada plafon: payload >1,5 MB **tidak di-cache** (di-skip diam-diam), jadi begitu data satu tenant melewati ambang itu, setiap panggilan stats kembali melakukan N full read tanpa peringatan.
- **`toggle_user` = N+1 read.** Full-tab read STATS hanya untuk menemukan satu baris.
- Audit: hanya `toggle_user`. `login` dan `switch_tenant` tidak tercatat sama sekali.

### GLOBAL - Email Fallback Notifier

- **`GANTI_RESEND_API_KEY` dan `GANTI_BREVO_API_KEY`** masih placeholder literal. Node-nya disabled, jadi tidak berbahaya — tapi ketiga jalur cadangan (Resend/SMTP/Brevo) sebenarnya **tidak tersambung sama sekali** di `connections`, jadi bukan cuma disabled, tapi yatim. Yang jalan cuma Gmail.
- **Titik kegagalan tunggal.** Kalau node Gmail kehabisan retry, eksekusi berakhir gagal — dan workflow ini sengaja tidak punya `errorWorkflow` (benar, untuk mencegah loop). Artinya: **seluruh rantai alert berhenti tanpa sinyal apa pun.** Sticky note-nya sendiri memperingatkan token Google mati tiap 7 hari kalau OAuth consent screen masih status "Testing".
- **Tidak ada dedupe/throttle.** Satu node yang flapping selama sejam menghasilkan satu email per error, tanpa batas.
- `N8N_BASE = 'https://n8n.srv1270416.hstgr.cloud'` ditandai `// >>> WAJIB DIGANTI` di sticky note — tapi nilai itu **cocok** dengan host yang muncul di pinData PCR dan Dashboard, jadi kemungkinan besar sudah benar dan komentarnya yang basi. Perlu konfirmasi.

---

## 8. Rekomendasi berprioritas

### Sekarang — sebelum tanggal 1

| # | Aksi | File |
|---|---|---|
| 1 | Tambah `stats_purge_dry_run = Y` ke tab CONFIG PCR **sebelum** menjalankan purge | PCR_Database → CONFIG |
| 2 | Duplicate tab STATS (TS **dan** PCR) sebagai backup | kedua spreadsheet |
| 3 | Tambah `"timezone": "Asia/Jakarta"` + `"errorWorkflow": "ZKsINjA7ZC8c9yRHWp3ud"` ke settings STATS Cleanup v3 | `STATS Cleanup v3.json` |
| 4 | Ubah errorWorkflow STATS Purge → `rBsq-mGgHfqfwbz3YmwxI` (WA, bukan email saja) | `VIRA-PCR - STATS Purge.json` |
| 5 | Untuk run manual TS: naikkan sementara `RETENTION_DAYS` jadi `99999` supaya jadi laporan-saja, baca hasilnya, baru kembalikan ke 90 | `Plan cleanup` |
| 6 | Pastikan `STATS Archive 3bulan` tetap non-aktif (sudah terverifikasi ✅) | — |

### Minggu ini — keamanan

| # | Aksi |
|---|---|
| 7 | **Rotasi secret Kirimi.** Nilainya sudah ada plaintext di 4 file JSON + 1 tab spreadsheet. |
| 8 | **Rotasi secret HMAC dashboard** `3b5c2942…` dan pindahkan ke env var / n8n credential. Semua sesi aktif akan invalid — kabari Sam & Om Sulianto dulu. |
| 9 | **Hapus baris `google service private key` dan `google service email` dari tab CONFIG PCR.** Tidak dipakai workflow mana pun — n8n sudah punya credential `QC5aF1Hy…`. |
| 10 | Pindahkan kedua file `.json` service account keluar dari folder proyek. |
| 11 | Hapus `pinData` dari VIRA PCR, Dashboard API, dan Follow-up (satu berisi token sesi valid). |
| 12 | Pertimbangkan akun Kirimi terpisah per klien — sekarang satu secret memegang dua klien. |

### 2–4 minggu — efisiensi (dampak terukur)

| # | Aksi | Dampak |
|---|---|---|
| 13 | Salin 3 node cache TS (`Cache Check`/`IF Cache Fresh`/`Cache Store`) ke PCR | PCR 9 → 6 read/pesan |
| 14 | Gabungkan 3 full read STATS jadi 1 filtered read di kedua bot | TS 5→3, PCR 6→4 read/pesan. Kapasitas PCR ±6,6 → **±15 pesan/menit** |
| 15 | Gabungkan write pasca-balasan (`Delete_Pending_Msg`/`Mark Buffer Consumed` + `Update to STATS` + `Update Greeting`) jadi satu `appendOrUpdate` | −2 write/pesan |
| 16 | Turunkan `Wait3` 60 → 15 detik, dan baca dari `debounce_seconds` di CONFIG | latensi ±75 → ±30 detik |
| 17 | Aktifkan prompt caching Anthropic (cek dukungan node; kalau belum, pakai HTTP Request) | ±4.500 token/pesan masuk tarif cache |
| 18 | Samakan model: TS Sonnet 4.6, PCR masih 4.5. Konfirmasi Follow-up: Haiku atau Sonnet? | konsistensi + biaya |
| 19 | Hapus cabang GForm zombie di TS (5 node + `Update GForm Sent TS1`) | menghentikan write timestamp palsu |
| 20 | Tambah `onError: continueRegularOutput` + `alwaysOutputData` ke `Update Bot Mode` di Dashboard | menghentikan request menggantung |

### 1–2 bulan — struktur

| # | Aksi | Hasil |
|---|---|---|
| 21 | Sub-workflow `GLOBAL - Kirimi Send` | −13 salinan, sekaligus menyelesaikan secret plaintext + verifikasi respons tidak konsisten |
| 22 | Gabungkan 2 MSG_BUFFER Cleanup jadi 1 (pola `Fan Out Tenants` dari DASH_AUDIT Cleanup) | 2 → 1 workflow, kodenya sudah identik |
| 23 | Gabungkan 2 Error Notifier jadi 1 (deteksi tenant dari nama workflow, pola sudah ada di GLOBAL notifier) | 2 → 1 |
| 24 | Gabungkan 2 STATS cleanup/purge jadi 1, aturan retensi per tenant di CONFIG | 2 → 1 |
| 25 | Extend `build_workflow.py` untuk bot utama: `src/engine.js` + `src/tenants/*.js` | perbaikan identitas/debounce cukup sekali |
| 26 | Tambah audit `login` + `switch_tenant` ke DASH_AUDIT; ubah `RETENTION_DAYS` 0 → 90 kalau wipe total bukan yang dimaksud | jejak audit benar-benar ada |
| 27 | Tambah penanganan stop-word di Follow-up | risiko keluhan outbound |
| 28 | Sheet staging untuk `Test manual` DASH_AUDIT Cleanup | "test" berhenti berarti wipe produksi |

---

## 9. Yang layak diapresiasi

Supaya laporan ini tidak terbaca sebagai daftar keluhan — beberapa hal di stack ini di atas rata-rata:

- **Prinsip identitas konsisten sempurna** antara dua klien. "No WA primary, lid backup, never rows[0]" bukan cuma tertulis di CLAUDE.md, tapi benar-benar diterapkan identik di keduanya.
- **HITL 3 lapis** (sebelum Wait, sesudah Wait, di `Cek_user_status`) supaya Sam/admin bisa mengambil alih kapan saja selama bot menunggu.
- **Error notifier yang tahu bahwa Kirimi bisa balas HTTP 200 dengan isi gagal**, lalu sengaja `throw` supaya fallback email tetap jalan. Itu tingkat kepedulian yang jarang.
- **Guard skema di semua workflow purge** yang membatalkan seluruh penghapusan kalau kolom wajib hilang. Ini yang membedakan "script hapus" dari "workflow produksi".
- **Penghapusan blok kontigu dari bawah ke atas** — benar, dan sudah diverifikasi terhadap source n8n (`startIndex` memang 1-based dan node melakukan `startIndex--` internal). Simulasi 300/300 kasus acak di QA PCR.
- **Price-hallucination guard di PCR** yang menolak angka Rupiah yang tidak ada di PRODUK/FAQ/pesan user — lahir dari insiden nyata (AI menyebut Rp 1,15 M untuk unit Rp 409 jt). Guard di kode, bukan cuma di prompt.
- **Canary `_diag`** di FAQ Retrieve, dideklarasikan **di luar** blok `try` setelah insiden 2026-08-21 di mana rename node membuat `data_context` kosong senyap.
- **Auth dashboard**: constant-time compare di dua tempat, dummy-hash anti-enumerasi, tenant selalu dari signed claim, validasi ulang terhadap registry server-side. Yang salah cuma penyimpanan secret-nya.
- **Dokumentasi pra-aktivasi** kedua workflow purge, lengkap dengan bagian "Yang TIDAK dilindungi". Itu yang membuat review ini bisa membandingkan niat vs implementasi dan menemukan tiga ketidaksesuaian.

---

## Lampiran — cara temuan diverifikasi

| Klaim | Cara verifikasi |
|---|---|
| Duplikasi node antar-klien | `difflib.SequenceMatcher` pada `jsCode` tiap node bernama sama; md5 untuk klaim byte-identical |
| Sheets I/O per pesan | Enumerasi seluruh node googleSheets + graf `connections`, dicek ada/tidaknya `filtersUI` |
| Ukuran data | Parsing langsung XML `xl/worksheets/*.xml` dari kedua `.xlsx` |
| Secret plaintext | `grep -c` nilai secret literal di 13 file |
| Isi tab CONFIG | Parsing `sharedStrings.xml` + baris sheet CONFIG dari kedua `.xlsx` |
| Cron & settings | Ekstraksi `settings` + `rule` tiap `scheduleTrigger` |
| Node zombie GForm | Pemeriksaan flag `disabled` per node + graf koneksi |
| `report_phone` dead code | `grep -c "report_phone"` = 1 (hanya definisi) |
| `startIndex` 1-based | Dicek terhadap source n8n `delete.operation.ts` (`startIndex--` internal) |
| Isi code node & prompt | 6 subagent Sonnet membaca seluruh body node yang di-dump |

Skrip bantu dan hasil dump ada di scratchpad sesi ini (`skel.py`, `dump.py`, `dup.py`, `xdup.py`, `scan.py`).
