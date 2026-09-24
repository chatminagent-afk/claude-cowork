# Analisa Menyeluruh — VIRA "V3.1 fixing greeting Y & unknown"

**Tanggal:** 2026-06-25
**File dianalisa:** `enhancement boros v2 vira 18 juni/VIRA V3.1 fixing greeting Y & unknown.json`
**Sifat dokumen:** analisa & rekomendasi (TIDAK ada perubahan workflow yang dilakukan)
**Validitas JSON:** valid · 56 node · `active: true`
**Status file (dikonfirmasi user 2026-06-25):** ini adalah file **LIVE & kanonik**. Konsekuensinya: temuan kritikal di bawah adalah kondisi PRODUKSI, bukan versi uji — terutama KRITIKAL-2 (whitelist).

---

## TL;DR (ringkasan eksekutif)

VIRA adalah workflow n8n yang solid sebagai **MVP untuk satu klien dengan volume rendah-menengah**. Logikanya pintar — debounce multi-bubble, HITL, anti-halusinasi berbasis data sheet, follow-up GForm — dan basis pengetahuannya sudah *data-driven* (tab PROGRAM/ABOUT/LINKS/FAQ), yang merupakan fondasi bagus untuk digandakan.

**Tapi dalam bentuk sekarang, arsitektur ini BELUM sustainable untuk skala besar dan BELUM bisa di-duplicate massal ke klien lain.** Tiga alasan utama: (1) **kredensial Kirimi tertanam plaintext** di dalam JSON, (2) **Google Sheets dipakai sebagai database transaksional** (sumber race condition + plafon kuota), dan (3) **segalanya hardcoded ke The Scholars** sehingga menggandakan = clone-and-edit di puluhan tempat, bukan multi-tenant.

Jawaban singkat untuk 3 pertanyaan Anda:

1. **Sustainable ke depan?** Untuk 1 klien volume kecil: ya. Untuk skala/multi-klien: belum — perlu migrasi DB & eksternalisasi config.
2. **Ada bug kritikal?** Ya — lihat 3 temuan **🔴 KRITIKAL** di bawah (secret bocor, whitelist mengunci produksi, webhook tanpa auth).
3. **Bisa diduplikasi massal untuk jualan?** Belum sebagai produk. *Pola*-nya bisa dipakai ulang, tapi butuh refactor jadi template multi-tenant dulu (estimasi & roadmap di bagian akhir).

---

## 1. Peta Arsitektur (cara kerja saat ini)

Alur pesan masuk:

```
WhatsApp (Kirimi) → Webhook (wa-inbound)
  → IF From Me (buang pesan dari diri sendiri)
  → IF (Whitelist)  ⚠️ hanya 5 nomor di-allow
  → Chat Counter (parse body, ekstrak LID/phone/nama/pesan)
  → Read User STATS → IF Bot Mode Active (cek HITL)
      ├─ bot OFF → Delete pending → STOP (Sam handle manual)
      └─ bot ON  → Update Buffer (tulis pending_msg + timestamp)
            → Rate Limiter LID (maks 5 pesan/menit/user)
            → Read STATS for HITL → HITL Check
            → Wait3 (60 detik DEBOUNCE)
            → Re-Read STATS Debounce
            → IF_Chat_Debounce (timestamp == run ini?)
                ├─ bukan run terakhir → STOP (pesan lama dibuang)
                └─ run terakhir → Cek_user_status (gabung semua bubble)
                    → Preprocess (deteksi status/grade/program/intent via regex)
                    → Read FAQ → Read PROGRAM → Read ABOUT → Read LINKS
                    → FAQ Retrieve (rakit konteks token-efisien)
                    → AI Agent (Claude + Simple Memory)
                        ├─ error → Reply Error
                        └─ ok → Process All (parse tag, bersihkan output)
                            → cabang: IF Send GForm / IF Unknown /
                              IF Status Update / Wait1→Reply / IF Talk To Sam
```

**Komponen kunci:**

| Lapisan | Implementasi sekarang |
|---|---|
| Channel WA | Kirimi API (`api.kirimi.id/v1/send-message`) |
| Orkestrasi | n8n (56 node) |
| "Database" | 1 Google Sheet (`1tEJ…CwE`), tab: STATS, UNKNOWN, FAQ, PROGRAM, ABOUT_SAM, LINKS |
| LLM | **Claude Sonnet 4.6**, `maxTokens 512`, `temperature 0.7` |
| Memory | `Simple Memory` (buffer window 10), sessionKey = `user_wa` — **volatile** |
| Persona & aturan | System message (~11 KB) + Preprocess regex + Process All heuristik |

**Hal yang sudah BAGUS (kekuatan):**

- Knowledge base **data-driven** lewat tab sheet — fakta tidak hardcode di prompt. Ini fondasi penting untuk menggandakan.
- **Anti-halusinasi** eksplisit: "tidak punya tool, fakta hanya dari DATA/FAQ, kalau tidak ada → `[UNKNOWN]`".
- **HITL** (`bot_mode = OFF`) dicek dua kali (sebelum & sesudah debounce) — Sam bisa ambil alih kapan saja.
- **Debounce multi-bubble** + **rate limiter** per-user — desain matang untuk pola chat WA yang sering dipecah jadi banyak bubble.
- Identitas pakai **LID** sebagai kunci stabil (bukan nomor yang bisa berubah) — sudah benar pasca migrasi LID.

---

## 2. Bug & Risiko Kritikal

### 🔴 KRITIKAL-1 — Kredensial Kirimi tertanam plaintext di dalam JSON

Di **7 node HTTP** (Reply Chat Kirimi, Send GForm Link, Notify*, Reply Error, dll) nilai berikut ditulis langsung:

```
user_code: KM40LI0426
secret:    4efe3780e1c0b53c…9ce0f2   ← secret penuh, plaintext
device_id: D-4ZV1F
```

**Kenapa berbahaya:** siapa pun yang menerima file JSON ini (backup, kirim ke kontraktor, commit ke Git, atau **calon klien saat demo**) langsung memegang kredensial WA Anda — bisa mengirim pesan atas nama Anda. Ini jadi **show-stopper** untuk model "jual ke banyak klien": tiap salinan workflow ikut membawa secret yang sama.

**Rekomendasi:** pindahkan ke **n8n Credentials** (Header Auth / generic credential), referensikan via `{{$credentials}}`. JSON ekspor tidak akan memuat secret. **Rotasi secret Kirimi sekarang** karena sudah tersebar di beberapa file `.json` di folder ini.

### 🔴 KRITIKAL-2 — Whitelist mengunci bot ke 5 nomor

`IF (Whitelist)` (combinator OR) hanya meneruskan pesan dari:
`6285155202354, 6281510624599, 6596110395, 6589200455, 628176480658`.

**Karena user mengonfirmasi file ini LIVE, ini berstatus bug produksi aktif:** semua pesan dari nomor di luar 5 ini berhenti diam-diam tanpa balasan. Bila tujuan bot adalah melayani publik (calon murid), maka mayoritas chat tidak pernah dijawab.

**Tambahan kecurigaan teknis:** node mencocokkan `$json.body.from` dengan string **nomor telepon**. Padahal pasca-migrasi LID, Kirimi sering mengirim `from` dalam format `@lid` (lihat node Chat Counter yang menangani `@lid`). Jika `from` yang masuk berformat LID, **tidak ada satu pun** yang cocok dengan 5 nomor itu → bot berpotensi tidak membalas siapa pun. **Ini perlu diverifikasi segera** lewat log eksekusi n8n terakhir (lihat nilai `body.from` aktual) — apakah ada balasan keluar dalam beberapa hari terakhir?

Keputusan yang dibutuhkan: (a) lepas whitelist agar melayani publik, atau (b) ganti jadi toggle config bila memang ingin membatasi. Sebelum diputuskan, saya tidak mengubah workflow.

### 🔴 KRITIKAL-3 — Webhook tanpa autentikasi / verifikasi pengirim

`Webhook` di path `wa-inbound` (POST) tidak punya auth, signature, atau validasi HMAC. Siapa pun yang tahu URL-nya bisa mengirim payload palsu → memicu balasan WA, mengotori tab STATS/UNKNOWN, dan **membakar token Anthropic** (biaya). Untuk produk komersial ini harus ditutup (header secret, IP allowlist Kirimi, atau verifikasi tanda tangan bila Kirimi menyediakannya).

---

### 🟠 TINGGI

**H-1. Google Sheets sebagai database transaksional = race condition + plafon kuota.**
Ada **20 node Google Sheets**; satu pesan bisa memicu beberapa read+write. Masalah:
- **Lost update / double-write:** `appendOrUpdate` dengan match `lid` **tidak atomik**. Dua pesan paralel (user beda, atau bubble cepat) dapat sama-sama membaca `Counter` lalu sama-sama menulis `Counter+1` → satu update hilang. Sama untuk `pending_msg` (baca-gabung-tulis).
- **Kuota:** Sheets API ±60 read/menit/user & 300/menit/project. Beberapa klien atau lonjakan trafik → `429` → eksekusi gagal **tanpa fallback balasan** ke user.
- **Latensi & eventual consistency:** mekanisme debounce mengandalkan tulisan terlihat setelah 60 dtk. Saat API lambat, perbandingan timestamp bisa meleset (dua run lolos / tidak ada yang lolos).

Ini adalah **batasan sustainability terbesar**. Untuk skala, ganti ke Postgres/Supabase/Redis (transaksi atomik, kunci baris, throughput tinggi). Knowledge base (PROGRAM/FAQ/ABOUT/LINKS) **boleh tetap di Sheets** karena read-only & jarang berubah — yang wajib pindah adalah **state transaksional (STATS, pending_msg, counter, bot_mode)**.

**H-2. Race pada debounce.** Pola Update Buffer → Wait 60s → Re-Read → bandingkan `timestamp == process_start_ts` cerdas, tapi rapuh: bergantung pada konsistensi tulis Sheets dan keunikan `process_start_ts` (Date.now()). Pesan yang datang sangat berdekatan bisa bertabrakan. Di DB sungguhan, debounce sebaiknya pakai kolom timestamp + transaksi, atau queue (mis. Redis) dengan key per-user.

**H-3. `$vars.chatCounter` tidak persist & global.** Di node `Chat Counter`: `$vars.chatCounter = counter`. `$vars` (environment variables) bersifat read-only di n8n — penugasan ini kemungkinan **no-op / tidak persist**, dan counter ini global lintas semua user (bukan per-user). Untungnya hanya informatif (masuk ke teks AI), tapi menyesatkan dan sebaiknya dibuang atau diganti `$getWorkflowStaticData`.

**H-4. Tidak ada error workflow / retry global.** Banyak node Read Sheets tanpa cabang error. Kalau Sheets/Anthropic error di tengah, eksekusi mati senyap — user tidak dapat balasan dan tidak ada notifikasi admin (kecuali jalur error Kirimi & AI Agent yang sudah ada). Tambahkan: retry+backoff pada node HTTP/Sheets, dan satu **Error Trigger workflow** yang notifikasi admin saat eksekusi gagal.

---

### 🟡 SEDANG

**M-1. NLU berbasis regex & heuristik rapuh.** `Preprocess` (deteksi status/grade/program/intent) dan `Process All` (puluhan pola frasa fallback Bahasa Indonesia untuk "menambal" saat model lupa pasang tag) sangat spesifik ke domain & bahasa The Scholars. Untuk satu klien: bisa dijaga. Untuk tiap klien baru: harus ditulis ulang. Ini menambah biaya duplikasi (lihat bagian 3).

**M-2. Drift dokumentasi & versi (file kanonik tidak terdokumentasi).** File LIVE ini memakai **Claude Sonnet 4.6, temp 0.7, 56 node**, padahal changelog `VIRA_V3.1` mendokumentasikan **Haiku 4.5, temp 0.4, 52 node** — dan ada pula seri `V3.2`–`V3.5` serta `VIRA V3 live 23 jun.json` yang **lebih baru** dari changelog V3.1. Artinya: **sistem yang sedang live tidak punya changelog yang cocok dengan isinya.** Risiko: saat handoff/duplikasi, orang bisa salah ambil versi, dan perubahan (mis. ganti ke Sonnet) tak tercatat alasannya. **Rekomendasi:** buat satu changelog untuk file live ini (mis. `VIRA_V3.1-live-changelog.md`) yang mencatat delta dari V3.1 resmi: model Haiku→Sonnet 4.6, temp 0.4→0.7, 52→56 node, plus fix greeting/unknown. Catatan biaya: Sonnet beberapa kali lipat Haiku per token — pastikan ini keputusan sadar, bukan warisan tak sengaja.

**M-3. `maxTokens 512`.** Cocok untuk gaya Sam yang pendek, tapi jawaban panjang (mis. syarat + dokumen) bisa terpotong. Pantau saat UAT.

**M-4. Memory volatile.** `Simple Memory` hilang saat n8n restart / jeda panjang. Identitas parent/student sudah durable di STATS (bagus), tapi konteks percakapan (kelas, program yang dibahas) tidak dipersist — sudah disadari di changelog V3.1. Untuk pengalaman lintas-hari yang mulus, persist `grade`/`recommended_program` ke STATS.

**M-5. Konsistensi kunci pencocokan.** Sebagian besar node cocokkan via `lid`, tapi `IF Bot Mode Active` membaca `$('Read User STATS').item.json.bot_mode` (baris pertama item, bukan hasil find by-lid). Jika Read User STATS mengembalikan banyak baris, ini bisa membaca baris yang salah. Pastikan node read sudah difilter ke user yang tepat, atau samakan pola find-by-lid seperti node `Cek_user_status`.

---

## 3. Sustainability & Kesiapan Multi-Tenant (jualan ke klien lain)

### Apakah pola ini bisa digandakan? Ya — tapi belum sebagai produk.

**Yang sudah mendukung duplikasi (aset reusable):**
- Knowledge base data-driven (tinggal ganti isi tab sheet per klien).
- Persona di system message (tinggal tulis ulang untuk brand klien).
- Protokol tag aksi (`[SEND_GFORM]`, `[TALK_TO_SAM]`, `[UNKNOWN]`, `[USER_STATUS]`) reusable.
- Pola HITL, debounce, rate-limit, follow-up GForm — semuanya pola umum yang bisa dipakai ulang.

**Yang menghalangi duplikasi massal (semua di-hardcode ke The Scholars):**

| Hardcoded | Lokasi | Dampak saat clone |
|---|---|---|
| Secret Kirimi | 7 node HTTP | secret sama menyebar; tidak aman |
| Doc ID Sheet | 20 node | edit manual tiap node |
| Nomor whitelist | IF (Whitelist) | edit/lepas manual |
| Persona "Sam" | system message | tulis ulang |
| Mapping program (Junior/Inter/Seniors) | Preprocess + FAQ Retrieve + prompt | tulis ulang logika |
| Regex Bahasa Indonesia | Preprocess + Process All | tulis ulang per klien |
| Link GForm | tab LINKS | ganti data (mudah) |

Kesimpulan: menggandakan sekarang = **"clone seluruh workflow lalu sunting di ~40+ titik"** — rawan salah, lambat, tidak skalabel, dan tiap klien jadi cabang kode terpisah yang harus dipelihara satu per satu. Itu **bukan** model produk yang sehat untuk jualan massal.

### Yang dibutuhkan agar jadi template multi-tenant

1. **Eksternalisasi kredensial** → n8n Credentials (per klien). *(Wajib, juga menutup KRITIKAL-1.)*
2. **Pisahkan config dari logika** → satu "Client Config" (tab/DB) berisi: doc ID, persona, mapping program, link, channel keys — di-load berdasar `client_id` dari payload webhook. Logika workflow tetap satu, data klien berbeda.
3. **Ganti state transaksional ke DB sungguhan** (Postgres/Supabase) → hilangkan race & plafon kuota; baru aman untuk banyak user/klien bersamaan.
4. **Routing per klien** → satu webhook + `client_id`, atau sub-workflow per klien yang memanggil "core engine" bersama. Hindari menyalin seluruh 56 node tiap klien.
5. **Generalisasi NLU** → jadikan mapping kelas→program & keyword sebagai data config, bukan regex hardcode; atau geser lebih banyak ke LLM dengan few-shot per klien.
6. **Hapus whitelist** (atau jadikan toggle config untuk fase uji).
7. **Observability** → logging, error workflow, dashboard metrik per klien (jumlah chat, unknown, handoff, biaya token).

### Verdict sustainability

- **1 klien, volume rendah (≤ ratusan chat/hari):** arsitektur sekarang **cukup**, asal 3 temuan kritikal ditutup.
- **Banyak user bersamaan / banyak klien:** **belum sustainable** — Google Sheets sebagai DB transaksional adalah plafon keras. Migrasi DB + eksternalisasi config adalah prasyarat sebelum "jualan massal".

---

## 4. Rekomendasi Berurutan (prioritas)

**Segera (sebelum publish / sebelum demo ke siapa pun):**
1. Rotasi secret Kirimi + pindah ke n8n Credentials. *(KRITIKAL-1)*
2. Putuskan & dokumentasikan status whitelist — lepas untuk produksi atau tandai jelas sebagai mode uji. *(KRITIKAL-2)*
3. Tambah autentikasi webhook. *(KRITIKAL-3)*
4. Tetapkan **satu file kanonik** + changelog; selesaikan drift versi (Sonnet vs Haiku, 56 vs 52 node). *(M-2)*

**Jangka pendek (stabilitas 1 klien):**
5. Tambah retry+backoff pada node Sheets/HTTP + Error Trigger workflow notifikasi admin. *(H-4)*
6. Bereskan `$vars.chatCounter` & pola find-by-lid yang tidak konsisten. *(H-3, M-5)*
7. UAT skenario race: 2 user paralel + 1 user banyak bubble cepat → cek tidak ada lost update di STATS.

**Jangka menengah (siap jual massal):**
8. Migrasi state transaksional ke Postgres/Supabase (knowledge base boleh tetap Sheets). *(H-1, H-2)*
9. Bangun lapisan Client Config + routing `client_id`; ubah workflow jadi "core engine" + data per klien.
10. Generalisasi NLU & persona jadi config-driven.

---

## 5. Catatan

- Analisa ini **read-only**; tidak ada perubahan pada file workflow.
- Temuan secret plaintext sengaja **tidak** saya simpan ke memori sesuai kebijakan data sensitif — tapi mohon segera dirotasi karena sudah ada di beberapa `.json`.
- **Terkonfirmasi (2026-06-25):** file ini **LIVE & kanonik**. Maka prioritas #1–#2 di atas (rotasi secret + putuskan whitelist) bersifat mendesak karena memengaruhi produksi langsung.

**File dibuat:**
- `D:\Documents\Claude Cowork\the scholars\2026-06-25-analisa-arsitektur-vira\2026-06-25-analisa-arsitektur-vira-v3.1.md`
