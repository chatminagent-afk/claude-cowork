# Memory Proyek — VIRA Steven

Dokumen ingatan lintas-sesi untuk instance **VIRA Steven** (bot jualan milik Steven sendiri,
bukan milik klien). Disusun 2026-08-17 dari seluruh percakapan + file proyek sampai tanggal itu.

> Beda dengan `catatan-build-workflow.md` (apa yang diubah di workflow) dan
> `checklist-deploy` (langkah yang harus dijalankan): dokumen ini menyimpan **konteks,
> keputusan, dan alasan** — hal yang tidak terbaca dari kode atau checklist.

---

## 0. Identitas proyek — yang paling sering tertukar

| | VIRA Steven | VIRA The Scholars |
|---|---|---|
| Persona | **"Steven versi AI"** | "Sam versi AI" |
| Pemilik | Steven sendiri | Klien (Sam, TheScholars.id) |
| Tujuan | Menjual jasa VIRA; bot ini **adalah** demo produknya | Melayani calon siswa beasiswa Singapura |
| Nomor device | 6285155202354 (Kirimi `D-XKA2P`) | — |

`CLAUDE.md` proyek menulis *"VIRA speaks as 'Sam versi AI'"* — itu benar **hanya** untuk
The Scholars. Jangan dipakai di VIRA Steven.

**Angka & identitas kunci**
- Nomor bot / device: `6285155202354`
- Nomor admin (penerima notifikasi): `6285171701168`
- Spreadsheet: `1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk` ("VIRA Steven Database")
- Webhook: `wa-inbound-steven`
- Model: balasan `claude-sonnet-5` (CONFIG bilang `claude-sonnet-4.5`, JSON pakai
  `claude-haiku-4-5-20251001` di node AI Agent — **tiga sumber, tiga jawaban, perlu disamakan**)
- Harga yang boleh disebut bot: Basic Rp3.000.000/bln, Premium Rp5.000.000/bln, setup gratis.
  Add-on boleh disebut ada, **angkanya tidak boleh**.

---

## Sesi 1 — Build awal (sampai 2026-08-15)

Workflow lahir sebagai **turunan template Persada** (`2026-08-08-VIRA-PCR-Main-V2.1`, 91 node),
ditransformasi oleh skrip idempoten `workflow/_transform.py`. Empat workflow n8n:

| Workflow | Peran | Status |
|---|---|---|
| **Main** | Inti bot: webhook → gate → baca sheet → AI Agent → `Process All` → cabang aksi | Aktif |
| **Error Notifier** | Error workflow untuk Main | ID **belum diisi** ke Main |
| **Buffer Cleanup** | Cron harian 03:00 WIB, bersihkan MSG_BUFFER | — |
| **Follow-up** | Sengaja **NONAKTIF** sampai perilaku bot stabil | Nonaktif |

**Warisan Persada yang masih tersisa** (dead code, tidak berbahaya tapi membingungkan):
`Bootstrap Config` menghitung `sheet_id` Persada yang tidak dipakai node mana pun; `pinData`
webhook masih berisi payload contoh Persada Cisoka.

## Sesi 2 — Dokumen v1 (2026-08-15)

Lahir `catatan-build-workflow` v1, `checklist-deploy` v1, dan `system-prompt-VIRA-Steven.md`.
Keduanya yang pertama sudah **ditandai KEDALUWARSA** oleh versi 16 Agt — disimpan sebagai
riwayat saja. Alasan resmi: v1 kehilangan langkah header sheet baru, seluruh uji rantai
`[DECK_REQUEST]`, dan bagian F-nya keliru menganggap cap harian aktif.

## Sesi 3 — 25 langkah transformasi + uji live pertama (2026-08-16 pagi)

Perbaikan besar. Yang paling penting untuk diingat:

- `Whitelist Gate` → **`Blocklist Gate`**, kode ditulis ulang total. Keputusan sadar: *"bot ini
  publik, jadi default-nya semua orang boleh masuk"*. **Asumsi ini yang runtuh di Sesi 5.**
- 9 node Sheets masih menunjuk gid Persada → diganti ke mode nama tab (kalau tidak, bot mati total).
- `Process All` ditulis ulang (27.045 → 14.739 karakter).
- Rantai `[DECK_REQUEST]` (7 node baru) + tab `REQUESTS` 12 → 32 kolom + kolom `STATS.brief_terisi`.
- Bug notifikasi senyap: `Format Handover Message` & `Format Media Notif` memakai variabel
  `cfg` sementara langkah perbaikan mengganti pola `config` → `tujuan` kosong → node `return []`
  → **notifikasi berhenti tanpa jejak**. Pola bug ini kambuh lagi di Sesi 5 (lihat B-2).
- Optimasi kuota Sheets: 14 read → 8 read per pesan.

**Tiga gejala dari uji chat live pertama:** handover jalan di setiap pesan (diperbaiki), link
media tidak pernah terkirim (diklaim diperbaiki — **ternyata belum**, lihat Sesi 5), dan Sheets
nyaris kena kuota.

## Sesi 4 — Demo chat penuh + download ulang sheet (2026-08-16 siang–malam)

Steven menjalankan percakapan demo lengkap 10:44–15:32 dari nomor admin `6285171701168`
(skenario: "Akademi Arsi", bisnis edukasi software arsitek, 10 chat/hari, mulai September).
Sheet live di-download ulang 23:59.

**Yang berhasil di demo ini:** penggalian fakta bertahap, penulisan tab `REQUESTS`
(kelengkapan 14/27), `STATS.deck_requested=Y`, persona & pagar privasi konsisten.

**Yang gagal:** media tidak terkirim, notifikasi deck tidak sampai. Dianalisis di Sesi 5.

## Sesi 5 — Audit tiga arah (2026-08-17)

Tiga subagent Sonnet membaca paralel: workflow JSON (267 KB), `VIRA Database.xlsx`, dan
seluruh dokumen. Temuan → bagian B di bawah.

---

## A. Arsitektur — hal yang wajib dipahami sebelum menyentuh apa pun

**AI Agent TIDAK punya tool.** Grep `"ai_tool"` di seluruh JSON = **0 kemunculan**. Satu-satunya
koneksi non-`main` ke node `AI Agent` adalah `ai_memory` dan `ai_languageModel`. Artinya LLM
murni chat-completion, dan **semua aksi dipicu tag teks** yang ditulis LLM lalu di-regex oleh
Code node `Process All`:

`[SEND_MEDIA: nama-link]` · `[TALK_TO_ADMIN]` · `[UNKNOWN]` · `[DECK_REQUEST]…[/DECK_REQUEST]` · `[FACTS]`

Konsekuensinya besar: **LLM bisa mengklaim sudah melakukan sesuatu tanpa menulis tag, dan
tidak ada apa pun di sistem yang membantahnya.** Ini akar Bug B-1.

**Alur ringkas:**
```
Webhook → If From Group → IF From Me → Bootstrap/Read/Parse Config → Blocklist Gate
→ Chat Counter → Read STATS → Resolve User Row → IF Bot Mode Active → Rate Limiter LID
→ Append MSG_BUFFER → debounce → Read MSG_BUFFER → Cek_user_status → [Vision] 
→ Muat Katalog (FAQ/PROGRAM/LINKS/ABOUT_STEVEN) → Rakit Konteks → AI Agent → Process All
→ 5 cabang paralel: kirim teks · notif media manual · UNKNOWN · handover · DECK_REQUEST
```

**10 tab sheet:** CONFIG (49 baris), ABOUT_STEVEN (20), FAQ (48), PROGRAM (8), LINKS (6),
STATS, REQUESTS (32 kolom, sudah cocok 100% dengan TSV acuan), UNKNOWN (kosong), EVENTS, MSG_BUFFER.

---

## B. Bug terbuka — status per 2026-08-17

### B-1 · Media tidak pernah terkirim — 3 penyebab bertumpuk 🔴

1. **Halusinasi tanpa tag.** Di chat 10:47 VIRA menjawab *"Aku sudah kirim video demonya tadi
   kak"* tanpa menulis `[SEND_MEDIA]` sama sekali. Guard FAIL LOUD di `Process All` hanya
   menyala kalau tag **sudah muncul** tapi key-nya tidak ketemu di LINKS (`isMediaManual`).
   Tidak ada guard untuk kasus "menjanjikan tapi tag tidak ada". Kalimat bohong lolos utuh.
2. **5 dari 6 URL di tab LINKS identik byte-per-byte** — `company-profile`, `deck-vira`,
   `demo-video`, `portfolio`, dan `harga-ringkas` semuanya menunjuk Drive ID yang sama
   (`1gJPQYKOG4UK4XonHe6GIDYMDctlRtxXC`). Jadi seandainya pun tag keluar, file yang terkirim salah.
3. **Teks dikirim sebelum media, dan kegagalan hanya dilapor ke admin.** `IF Send Media` baru
   berjalan **setelah** `Send WA + Verify (Kirimi)` sukses. Kalau `Download Media` gagal — dan
   untuk video, `uc?export=download` Drive memang membalas halaman konfirmasi virus-scan HTML —
   cabang `false` pergi ke `Notify Admin Media`. **User tidak pernah dikoreksi.**

### B-2 · Notifikasi deck tidak sampai ke admin 🔴

Koreksi penting terhadap dugaan awal: **rantai deck-nya JALAN.** Bukti dari sheet live —
`REQUESTS` terisi (ts 16/8/2026 11.19.08, "Akademi Arsi", kelengkapan 14/27) dan
`STATS.deck_requested=Y`. Jadi `IF Deck Request` lolos, `Merge Brief`, `Write REQUESTS`,
`Wait Deck`, `Update STATS Brief` semua sukses. **Hanya node terakhir `Notify Admin Deck`
yang gagal.**

Faktor yang membuatnya gagal dalam diam sudah pasti:
- `onError: "continueRegularOutput"` **tanpa** `retryOnFail`/`maxTries` → gagal sekali =
  senyap, workflow tetap dianggap sukses.
- `errorWorkflow` di level workflow masih placeholder `<<ISI_ID_ERROR_WORKFLOW>>` → tidak ada
  alert ke mana pun.

**Node itu sendiri sehat secara statis** — sudah dibedah baris 4669–4709. Kelima field
(`user_code`, `secret`, `device_id`, `phone`, `message`) memakai referensi eksplisit
`$('Parse Config').first().json.config.*` dan `$('Merge Brief').first().json.notif_text`,
**tidak ada satu pun bare `$json.xxx`**. Jadi dua hipotesis awal terbantahkan oleh kode:
tidak ada bug `cfg` vs `config` di sini, dan `$json` yang ketiban echo baris Sheets tidak
relevan karena node ini tidak pernah membaca `$json`. Nama kolom `"No WA"` di
`Update STATS Brief` juga sudah benar.

**ROOT CAUSE (terkonfirmasi 2026-08-17 dari data eksekusi live): `Wait Deck` memutus akses ke
data node sebelumnya.** Buktinya ada di dalam satu node yang sama, `Update STATS Brief`:

| Field | Expression | Hasil di sheet |
|---|---|---|
| `deck_requested` | `"Y"` — **literal** | ✅ tertulis |
| `brief_terisi` | `{{ $('Merge Brief').first().json.brief_terisi }}` | ❌ **kosong** |

Satu node, dua field — yang berhasil persis yang tidak memakai referensi node. `Notify Admin
Deck` yang jalan sesudahnya memakai **referensi node di kelima field-nya**
(`$('Parse Config')…admin_phone`, `$('Merge Brief')…notif_text`), jadi Kirimi ditembak dengan
`phone` dan `message` kosong → ditolak → `onError: continueRegularOutput` tanpa retry →
hilang tanpa jejak.

Pola ini konsisten di keempat jalur notifikasi — **ada `Wait` di jalur = notifikasi gagal**:

| Jalur | `Wait` sebelum notify? | Hasil |
|---|---|---|
| Handover | tidak ada | ✅ sampai (dikonfirmasi Steven) |
| Media manual | tidak ada, pakai `$json` dari Code node | ✅ seharusnya jalan |
| Deck | `Wait Deck` 20 dtk | ❌ gagal senyap |
| Unknown | `Wait2` | ❌ (lagipula `Record to UNKNOWN` gagal — tab UNKNOWN kosong) |

`Wait Deck` juga satu-satunya node Wait di seluruh file **tanpa `webhookId`**. Hipotesis yang
sempat dikejar dan **gugur**: bukan `contentType` (Handover bentuknya identik dan berhasil),
bukan `cfg` vs `config`, bukan gate Tingkat-1, bukan nama kolom.

**Satu bug, empat gejala.** Rantai akibatnya lebih luas dari sekadar notifikasi hilang:

```
Wait Deck memutus $('Merge Brief')
   └─ brief_terisi di STATS kosong
        ├─ Resolve User Row → brief_context = "(belum ada brief untuk orang ini)"
        │     ├─ bot menanyakan ulang hal yang sudah dijawab
        │     └─ ringkasan handover bilang "Belum ada brief terstruktur"
        └─ Notify Admin Deck kirim phone & message kosong → gagal senyap
```

Gejala ketiga terkonfirmasi dari notif handover 2026-08-17 00:59: isinya menyatakan *"Status
Brief: Belum ada brief terstruktur"* padahal tab REQUESTS sudah terisi sejak 16 Agt 11:19
(Akademi Arsi, 14/27). Artinya **mekanisme "sadar diri" — fitur yang paling serius dirancang
di brief deck — tidak pernah hidup sejak awal.**

**Perbaikan:** buang `Wait Deck`, atau bawa `notif_text` + `admin_phone` ikut mengalir di item
JSON alih-alih diambil lewat `$('Node')`. `Wait Deck` semula ada untuk menghindari balapan
tulis dengan `Update to STATS` — balapan itu perlu diselesaikan lewat urutan koneksi, bukan
jeda waktu (jeda 20 detik itu tebakan, bukan jaminan).

**Dua temuan sampingan dari notif handover yang sama:**
- `lead_source` tertulis `Organik` padahal prospek bilang *"dari iklan ig sih"* —
  `Detect Lead Source` gagal menangkap. Kolom ini justru yang paling penting benar untuk bot
  yang tujuannya menyaring lead iklan IG.
- FAQ baris 15 menjanjikan VIRA bisa membaca **dokumen**; kenyataannya vision hanya menangani
  gambar (lampiran dokumen dijawab *"aku belum bisa membukanya dari sini"*). Turunkan janji di
  FAQ, atau naikkan kemampuannya.

### B-2b · Gate deck menimpa balasan bagus **dan** membuang data 🔴

Dari data eksekusi 16 Agt 11:09:08 — `deckMissing: ["nama_bisnis"]` → `deckRejected: true`:

- **Balasan ditimpa.** AI sudah menulis jawaban lengkap (manfaat VIRA untuk kasus edukasi,
  harga Basic/Premium, biaya token, closing "Kamu tertarik untuk Steven buatkan penawaran
  khusus?"). Seluruhnya dibuang, diganti `cleanOutput` = *"Boleh tahu nama bisnisnya dulu kak?
  Biar aku catat dengan benar."* Cocok persis dengan transkrip 11:10 — prospek bertanya soal
  manfaat, dijawab pertanyaan administratif.
- **Data hangus.** 9 field sudah tergali di giliran itu (`industri`, `deskripsi_bisnis`,
  `target_pelanggan`, `channel`, `sumber_leads`, `masalah_utama`, `aksi_utama`,
  `pertanyaan_tersering`, `catatan`) — tapi karena gate menolak, `Write REQUESTS` tidak jalan
  dan semuanya hilang. Tertulis di sheet cuma karena AI kebetulan mengulanginya di 11:19.

**Desainnya terbalik:** gate Tingkat-1 seharusnya menahan **notifikasi ke Steven**, bukan
menahan **penyimpanan data**. Capture dan notify harus dipisah.

### B-2c · Model balasan bukan Sonnet — `reply_model` dead config 🔴

CONFIG bilang `reply_model = claude-sonnet-4.5`, catatan build bilang `claude-sonnet-5`, tapi
node `AI Agent` hardcode **`claude-haiku-4-5-20251001`** dengan `max_tokens: 1024`. Key
`reply_model` tidak pernah dibaca node mana pun — dead config ketiga, setelah
`blocklist_numbers` dan `whitelist_*`.

Kemungkinan besar ini penyebab halusinasi *"Aku sudah kirim video demonya"*: `links_context`
membuktikan AI **memang melihat** `demo-video` di katalog, jadi bukan soal data — Haiku sekadar
tidak patuh. Risiko tambahan: blok `[DECK_REQUEST]` saja 27 baris, kalau output kepotong di
1024 token maka tag penutup `[/DECK_REQUEST]` hilang → regex gagal → deck lenyap diam-diam.

### B-2d · Sisa Persada masih hidup di `Preprocess - Context Detection`

Dari data eksekusi: `askingLokasi: true` padahal tidak ada yang bertanya lokasi (false
positive), plus `askingKPR`, `askingLegalitas`, `askingFasilitas`, `discussingUnit`, `units`,
`unitInterestDB`, `budgetRangeDB` yang semuanya domain properti. Setiap prompt juga masih
menyuntik `JAM_OPERASIONAL_SURVEY: 08:00-17:00` dan tabel `HARI_KE_TANGGAL` untuk penjadwalan
survei — tidak relevan untuk bot jualan software, dan memakan token tiap giliran.

### B-3 · Gating nomor: default-ALLOW, dan blocklist-nya mati total 🔴🔴 (paling mendesak)

**Terverifikasi langsung, dua arah:**
- `blocklist_numbers`, `bot_wa_number`, `ignore_self_number` hanya muncul di **baris 84**
  (`Blocklist Gate`, tempat mereka **dibaca**) — tidak pernah di baris 71 (`Parse Config`,
  tempat objek config **dibangun**). Jadi `cfg.blocklist_numbers` = `undefined` →
  `JSON.parse(undefined \|\| '[]')` = `[]`. **Apa pun yang Steven tulis di CONFIG untuk key itu
  tidak pernah terbaca.** Guard anti-balas-diri-sendiri juga mati (`botNumber = ''`).
- Kebalikannya, `whitelist_enabled` & `whitelist_numbers` hanya muncul di **baris 71**
  (di-parse) dan **tidak pernah dibaca satu node pun**. Config mati.

Akibat: **saat ini siapa pun yang chat 6285155202354 akan dibalas AI.** Satu-satunya gerbang
yang benar-benar hidup adalah `bot_mode` per-nomor di STATS — dan itu hanya berlaku setelah
nomor tersebut punya baris, yang baru terjadi **setelah bot terlanjur membalas**.

### B-4 · Warisan sisa yang belum dikonfirmasi

Disebut di catatan Sesi 3 dengan bahasa "masih/belum", tapi tidak masuk daftar resmi "belum
selesai" — status ambigu, **jangan diasumsikan aman**:
- Vision prompt masih berbunyi "chatbot perumahan Persada Cisoka" dengan kategori KPR/siteplan.
- `Record to UNKNOWN` menulis kolom `message` yang tidak ada di tabnya → append gagal
  (konsisten dengan tab UNKNOWN yang kosong total).
- Sanitizer tag pada deskripsi gambar belum mengenal `DECK_REQUEST` → **celah injeksi lewat gambar**.

### B-5 · Belum ada, diakui sebagai celah

- **Kill switch global** — CONFIG tidak punya `VIRA_STATUS`, tidak ada node yang memeriksanya.
  Satu-satunya cara berhenti: nonaktifkan workflow di n8n. Untuk bot yang di-ads di nomor
  kerja, ini celah nyata.
- **Daily cap guard** — `daily_message_cap`/`daily_vision_cap` ada di CONFIG tapi **tidak dibaca
  node mana pun**. Rem biaya yang benar-benar aktif hanya `Rate Limiter LID` (5 pesan/menit/nomor)
  dan spend limit Anthropic Console (**belum disetel**).
- **PWA dashboard** belum diadaptasi.

### B-6 · Higiene data di sheet

- Nomor WA disimpan **teks** di CONFIG tapi **angka** di STATS/REQUESTS/EVENTS/MSG_BUFFER
  (terbaca `6285171701168.0`) → risiko gagal match kalau dibandingkan `===` tanpa cast.
- Satuan timestamp campur **dalam satu tab**: `volume_chat_ts`/`last_reply_ts` epoch detik,
  `debounce_ts`/`buffer_done_ts` epoch milidetik. Selisih 1000×.
- Normalisasi nomor `String(v).replace(/\D/g,'')` membuang `+`, spasi, dan suffix
  `@s.whatsapp.net`/`@lid` — tapi **tidak mengkonversi prefix `0` ↔ `62`**.
- MSG_BUFFER menyimpan pesan rentang 5j53m padahal `msg_buffer_retention_hours=2` → cleanup
  belum jalan atau belum sempat.
- Duplikat pesan beruntun di MSG_BUFFER (jarak 34,9 dtk dan 50,7 dtk) dan 2 event `DELEGATED`
  berjarak 95 detik → relevan dengan investigasi debounce.

---

## C. Keputusan desain yang sudah mengikat

- **Identitas user:** No WA primer, `lid` cadangan, **tidak pernah** fallback ke `rows[0]`.
- **Bot on/off per nomor:** kolom `bot_mode` di STATS. Di-`OFF` otomatis oleh `[TALK_TO_ADMIN]`,
  **tanpa auto-resume** — harus dikosongkan manual.
- **Penggalian brief 3 tingkat** supaya tidak terasa menginterogasi: Tingkat 1 wajib
  (`nama_bisnis`, `industri`, `masalah_utama` — menggerbangi tag), Tingkat 2 digali aktif satu
  per balasan, Tingkat 3 hanya dicatat kalau disebut sendiri. Kolom kosong bukan kegagalan —
  itu daftar pertanyaan untuk Steven saat menelepon.
- **`brief_terisi`** ditulis ke STATS, dibaca lagi di giliran berikutnya sebagai `brief_context`
  supaya bot tidak menanyakan ulang hal yang sudah dijawab.
- **Pagar privasi bot:** tidak menyebut nama klien Steven yang sudah ada ("salah satu klienku
  platform edukasi"), tidak menyebut nama bank tempat Steven bekerja ("bank swasta nasional"),
  tidak membahas detail teknis build, selalu jujur kalau ditanya apakah dia AI.
- **Gaya balasan:** panggil "kak", maksimal 4 kalimat, tanpa markdown/bullet, maksimal 1 emoji,
  hindari tanda seru, variasikan pembuka.
- **Follow-up sengaja mati** sampai perilaku bot stabil; prospek `deck_requested=Y` dikecualikan.

---

## D. Batasan yang datang dari luar workflow

- **Kuota Google Sheets 60 read/menit per akun** — dipakai bareng VIRA Steven, The Scholars,
  dan Persada. Detail di memory `kuota-google-sheets-lintas-klien`.
- **Nomor bot = nomor pribadi campuran Steven** — rekan kantor BCA, urusan kerja lain, dan
  saudara semua chat ke nomor itu. Ini batasan terbesar proyek dan mengubah seluruh desain
  gating. Detail + arah solusi di memory `vira-steven-jalan-di-nomor-pribadi-campuran`.
- **Kirimi adalah gateway tidak resmi.** Konsekuensi yang jarang dihitung: kalau nomor kena
  banned WhatsApp, yang hilang bukan cuma bot — hilang juga nomor bisnis dan seluruh kontak
  kerja Steven di nomor yang sama.

---

## E. Cara kerja yang disepakati

- Baca file besar (workflow JSON, xlsx, docs) **selalu lewat subagent Sonnet paralel**, minta
  kutipan mentah bukan ringkasan.
- Dokumen analisis ditulis **bahasa Indonesia**.
- Nama file baru: `YYYY-MM-DD-nama-deskriptif`.
- Konfirmasi dulu sebelum menghapus/menimpa/mengganti nama file.
- Kerja bertahap: rencana dulu → tunggu persetujuan → ringkas tiap langkah besar.
