# Update VIRA-PCR — Media Sending & Notifikasi Tim (2026-07-16)

**Tanggal:** 2026-07-16
**Basis:** `2026-07-15-VIRA-PCR-main.json` (71 node) → hasil update `2026-07-16-VIRA-PCR-main.json` (**74 node**).
**Pemicu:** requirement baru dari klien (Om Sulianto), 2026-07-16.
**Cara rakit:** lewat jalur build (`_extraction/build/assemble.py` + `codenodes.py`) — rerunnable. Jalankan `python assemble.py` untuk regenerasi. File 2026-07-15 TIDAK ditimpa.

---

## 0. Ringkasan cepat (TL;DR)

| # | Requirement klien | Status di workflow | Yang berubah |
|---|-------------------|--------------------|--------------|
| 1 | Notif manual ke telemarketer (Aar & Aqsa) saat user butuh gambar/video | **BARU dibangun** | 3 node baru + logika di `Process All` + key CONFIG `media_team_phone` |
| 2 | Notif survey ke Om Sulianto | **Sudah ada** (cabang `IF Schedule Survey → … → Notify Field Team`) | Cukup **isi CONFIG** `field_team_phone` = nomor Om Sulianto |
| 3 | Media sending native (gambar/video/PDF) via Kirimi | **Sudah ada** (cabang `IF Send Media → Wait Media → Send Media Kirimi`) | Tidak ada perubahan node; tinggal **isi katalog LINKS + host file** |

Jadi inti pekerjaan hari ini = **requirement 1** (notif manual Aar & Aqsa). Requirement 2 & 3 sudah terpasang sejak draft 2026-07-15, hanya butuh konfigurasi data (nomor + katalog).

---

## 1. Node yang DITAMBAH (3 node baru — cabang "Media Manual")

Cabang paralel baru dari `Process All`, sejajar dengan cabang media native:

| Node | Tipe | Fungsi |
|------|------|--------|
| **IF Media Manual** | `n8n-nodes-base.if` | Lolos bila `{{ $json.isMediaManual }}` true (user minta media TAPI file belum ada di katalog LINKS). |
| **Format Media Notif** | `n8n-nodes-base.code` | Susun pesan notif (nomor + nama user + ringkasan permintaan). Kembalikan **1 item per nomor tim** (pola loop identik `Format Handover Message`). |
| **Notify Media Team** | `n8n-nodes-base.httpRequest` (Kirimi) | Kirim notif WA ke tiap nomor tim (Aar & Aqsa). Auth `httpCustomAuth`, `continueOnFail`, `onError: continueRegularOutput` — mati-nya notif tidak menggagalkan balasan teks. Meniru persis pola `Notify Field Team`. |

**Koneksi baru:**
```
Process All ──▶ IF Media Manual ──(true)──▶ Format Media Notif ──▶ Notify Media Team
```

Isi pesan yang diterima Aar/Aqsa:
```
📸 [PCR] PERMINTAAN MEDIA - KIRIM MANUAL
User: 628xxxxxxxxxx
Nama: (nama user atau "(belum ada nama)")
Diminta: <key media, mis. brosur / foto / video>
Detail: key="foto" | pesan user: <kutipan pesan asli user, maks 300 char>

User menunggu file dikirim. Balas langsung ke user yaa.
Chat: wa.me/628xxxxxxxxxx
```

---

## 2. Node/kode yang DIUBAH

### 2.1 `Parse Config` (Code) — tambah key `media_team_phone`
Ditambah parsing `media_team_phone` (pola sama `field_team_phone`): menerima JSON array `["628988585871","6281299500371"]` atau string tunggal; dibersihkan jadi digit saja.

### 2.2 `Process All` (Code) — deteksi fallback media manual
Blok resolve media diperluas. Sebelumnya: kalau key `[SEND_MEDIA]` tidak ada di katalog LINKS → media di-skip diam-diam (user tidak dapat apa-apa selain teks). Sekarang:
- Key **ada** di LINKS (URL publik) → `isSendMedia=true` → **kirim native** (cabang lama, tidak berubah).
- Key **tidak ada** / katalog kosong → `isSendMedia=false`, **`isMediaManual=true`** + `mediaRequestSummary` (key + kutipan pesan user) → **cabang notif manual** ke tim.

Dua field baru di output `Process All`: `isMediaManual`, `mediaRequestSummary`.

### 2.3 `Format Media Notif` (Code baru) — `codenodes.py: FORMAT_MEDIA_NOTIF`
Baca `media_team_phone` dari CONFIG, susun pesan, loop per nomor. Bila `media_team_phone` kosong → return `[]` (aman, tidak error).

### 2.4 System prompt AI Agent — instruksi tag `[SEND_MEDIA]` (lihat §7)

---

## 3. Keputusan desain penting

### 3.1 Media manual = FALLBACK OTOMATIS, bukan jalur terpisah
**Pilihan yang diambil: graceful degradation lewat resolusi katalog.**

Satu tag `[SEND_MEDIA: <key>]` dari AI menentukan jalur secara otomatis:
- **Sekarang (katalog LINKS masih kosong)** → semua permintaan media jatuh ke **notif manual Aar & Aqsa**. Ini memenuhi "jalur sementara sampai katalog terisi".
- **Nanti (klien sudah host file & isi LINKS)** → key yang cocok otomatis **dikirim native** oleh bot; sisanya (key yang belum ada) tetap fallback ke manual. Ini memenuhi "fallback bila media tidak ada di katalog".

Keuntungan: **tidak perlu ubah AI/prompt saat transisi** manual → native. Cukup isi baris di tab LINKS, perilaku berpindah sendiri. Native & manual **koeksis** tanpa konflik.

### 3.2 Katalog media = tab **LINKS** (bukan tab MEDIA baru)
Requirement menyebut "sheet baru MEDIA". **Keputusan: pakai tab `LINKS` yang sudah ada**, karena:
- Media sending native yang sudah terpasang (`Process All` → `Read LINKS Data`) meresolve URL dari LINKS. Membuat sheet MEDIA baru = harus tambah node Read + rewire, risiko regresi, tanpa manfaat fungsional.
- Desain `2026-07-15-desain-media-sending.md` secara eksplisit merekomendasikan LINKS (satu registry untuk semua URL).
- LINKS sudah mengandung semua kolom yang diminta klien untuk "MEDIA": `Nama Link` (=kode), `Deskripsi`, `Tipe`, `URL`, `Caption`.

Jadi **tab LINKS berperan sebagai katalog media**. Kalau klien tetap ingin nama "MEDIA", itu cukup rename tab + ganti 1 argumen `sheetName` di node `Read LINKS Data` (tidak dilakukan di update ini demi konsistensi).

### 3.3 Pemisahan nomor tujuan (penting — jangan tertukar)
| Kebutuhan | Key CONFIG | Nomor |
|-----------|-----------|-------|
| Notif **media manual** | `media_team_phone` | **Aar** `628988585871` + **Aqsa** `6281299500371` |
| Notif **survey** (delegasi) | `field_team_phone` | **Om Sulianto** `6287888542255` |
| Notif internal error/unknown/talk-to-admin | `admin_phone` | (nomor admin PCR — tentukan Steven/klien) |

---

## 4. Requirement 2 — Notif survey ke Om Sulianto (sudah ada)

Cabang `IF Schedule Survey` sudah lengkap sejak 2026-07-15:
```
Process All ─▶ IF Schedule Survey ─▶ Write SURVEY ─▶ Update STATS Survey
           ─▶ Collect Handover Context ─▶ Summarize Handover ─▶ Format Handover Message
           ─▶ Notify Field Team ─▶ Log EVENTS Delegated
```
- Tag `[SCHEDULE_SURVEY: tanggal jam unit]` hanya nyala setelah AI dapat **tanggal + jam valid** dari user (divalidasi deterministik `validateSurveySlot`). Jadi notif hanya keluar saat sudah ada waktu survey konkret — sesuai "user sudah kasih waktu rencana survey".
- Pesan yang diterima Om Sulianto sudah memuat **nomor WA, nama, waktu survey (SCHEDULED tgl jam), unit diminati, budget, sumber, ringkasan kebutuhan** (via `Summarize Handover`; ada fallback deterministik bila LLM mati).

**Aksi deploy:** set CONFIG `field_team_phone = ["6287888542255"]`. Selesai — tidak ada perubahan node.

---

## 5. Requirement 3 — Media sending native (sudah ada)

Cabang `IF Send Media` sudah lengkap sejak 2026-07-15:
```
Process All ─▶ IF Send Media ─(true)─▶ Wait Media (3s) ─▶ Send Media Kirimi
Send Media Kirimi ─(error out)─▶ Notify Admin Media Error
```
- `Send Media Kirimi` = HTTP Request ke Kirimi dengan `media_url` (URL file dari LINKS), `phone`, dan `message` (caption). Auth `httpCustomAuth`, `retryOnFail`, `continueOnFail`.
- `Wait Media 3s` menjamin balasan teks (`Reply Chat Kirimi`) sampai lebih dulu, baru file menyusul.
- Dukung gambar/video/PDF — semua lewat parameter `media_url` yang sama (lihat §6).

**Aksi deploy:** isi katalog LINKS + host file (lihat §8).

---

## 6. Hasil riset API Kirimi (dikonfirmasi 2026-07-16 dari kirimi.id/docs)

**Kirim media TIDAK butuh endpoint baru** — cukup tambah field opsional `media_url` di endpoint send-message yang sudah dipakai bot untuk balas chat.

| Aspek | Nilai |
|-------|-------|
| Endpoint | `POST https://api.kirimi.id/v1/send-message` |
| Field wajib | `user_code`, `device_id`, `receiver`, `message`, `secret` |
| Field opsional media | **`media_url`** — URL publik file (gambar/video/audio/dokumen) |
| Format didukung | Gambar: JPEG/PNG/GIF/WebP · Video: MP4/AVI/MOV · Audio: MP3/WAV/OGG · Dokumen: PDF/DOC/DOCX/XLS/XLSX/PPT/PPTX |
| Ukuran maks | **64 MB** |
| Rate limit | **60 request/menit** (default; hubungi support untuk lebih) |
| Paket | media tersedia di paket Lite/Basic/Pro |

> ⚠️ **Catatan nama field `phone` vs `receiver`.** Dokumentasi resmi Kirimi memakai **`receiver`**. Node produksi VIRA V4 (The Scholars) yang terbukti jalan memakai **`phone`**. Semua node Kirimi di workflow ini (termasuk `Send Media Kirimi`, `Notify Media Team`, `Notify Field Team`) memakai **`phone`** demi konsistensi dengan node yang sudah terbukti. **Saat deploy: verifikasi 1x dengan test call.** Bila gateway menolak `phone`, ganti nama parameter `phone` → `receiver` di node-node Kirimi (nilainya tetap sama).

> ⚠️ **`media_url` harus direct-download publik.** Docs tidak eksplisit menyebut ini, tapi gateway perlu mengunduh file dari URL tanpa login. Verifikasi tiap URL di browser incognito harus langsung mengunduh/menampilkan file, bukan halaman preview/login.

Sumber: https://kirimi.id/docs

---

## 7. Perubahan system prompt AI Agent

Diubah **deskripsi tag `[SEND_MEDIA]`** (di `2026-07-15-draft-system-prompt-telemarketer.md`, otomatis ikut terbawa ke `AI Agent.options.systemMessage` saat build).

**Sebelum:** contoh "saya kirim brosur lengkapnya yaa" (mengesankan file sudah terlampir saat itu juga).

**Sesudah:** VIRA diinstruksikan:
- Pakai `[SEND_MEDIA: <key>]` untuk brosur/gambar/denah/**foto/video** unit.
- Sistem yang mengirim file (native kalau ada di katalog, manual oleh tim kalau belum) — AI cukup pasang tag, **jangan mengarang URL**.
- **Konfirmasi ke user bahwa file akan DIKIRIM tim sebentar lagi**, jangan bilang "ini filenya" seolah sudah terlampir. Kalimat ini jujur untuk kedua jalur (native maupun manual).
- Contoh baru: `"[SEND_MEDIA: foto] Boleh Kak, foto unitnya akan tim kami kirimkan sebentar lagi yaa."`

Tidak ada perubahan pada tag lain (`[SCHEDULE_SURVEY]`, `[REQUEST_CALL]`, `[TALK_TO_ADMIN]`, `[UNKNOWN]`, `[FACTS]`).

---

## 8. Yang harus dikonfigurasi Steven saat deploy

### 8.1 Tab CONFIG (tambah/isi key)
| key | value | keterangan |
|-----|-------|-----------|
| `media_team_phone` | `["628988585871","6281299500371"]` | **BARU** — Aar & Aqsa (notif media manual). JSON array. |
| `field_team_phone` | `["6287888542255"]` | Om Sulianto (notif survey). |
| `admin_phone` | `628xxxxxxxxxx` | nomor admin PCR (error/unknown/talk-to-admin). |
| `admin_phone_display` | `08xx-xxxx-xxxx` | nomor yang ditampilkan ke user saat `[REQUEST_CALL]`. |

> Nomor: Aar `+62 898-8585-871` → `628988585871` · Aqsa `+62 812-9950-0371` → `6281299500371` · Om Sulianto `+62 878-8854-2255` → `6287888542255`. **Verifikasi digit ini** (khususnya Aar yang formatnya tidak biasa) sebelum go-live.

### 8.2 Credential Kirimi (device pengirim = sama dengan bot balas chat)
Semua node Kirimi (termasuk 3 node notif + `Send Media Kirimi`) memakai credential placeholder `Kirimi Custom Auth (REPLACE per client)` (id `REPLACE_WITH_KIRIMI_CUSTOM_AUTH_CRED_ID`). Buat 1 credential **Custom Auth** berisi `user_code`, `secret`, `device_id` Kirimi PCR, assign ke semua node Kirimi. Notif dikirim dari **device yang sama** dengan yang dipakai bot membalas chat.

### 8.3 Katalog media = tab **LINKS** (untuk media native)
Kolom: `Nama Link` (kode, mis. `brosur`/`siteplan`/`tipe36`/`foto`/`video`) | `Tipe` (`image`/`video`/`document`) | `Status` (harus `Aktif`) | `URL` (direct-download publik) | `Caption` (opsional; fallback ke `Deskripsi`).
- Selama LINKS masih kosong → semua permintaan media otomatis lewat notif manual Aar & Aqsa (tidak error).
- Begitu diisi + di-host → key yang cocok dikirim otomatis oleh bot.

### 8.4 Hosting file media (agar bisa dikirim native)
Kirimi butuh URL **direct-download publik** (maks 64 MB). Opsi (dari `2026-07-15-desain-media-sending.md`):
- **MVP cepat:** Google Drive → set "Anyone with the link" → URL `https://drive.google.com/uc?export=download&id=FILE_ID` (ambil `FILE_ID` dari share link `/d/FILE_ID/view`).
- **Produksi:** object storage (S3/R2/Supabase) atau hosting web klien (`persadacisoka.com/brosur.pdf`) → URL permanen, tidak kena kuota Drive.
- **Verifikasi:** buka URL di incognito, harus langsung unduh/tampil file. Simpan URL final di sel `LINKS.URL`.

### 8.5 Verifikasi field `phone` vs `receiver`
Test call 1x (lihat §6). Bila perlu, ganti nama parameter `phone`→`receiver` di semua node Kirimi.

---

## 9. Validasi

- `python -m json.tool 2026-07-16-VIRA-PCR-main.json` → **VALID**.
- Struktur: 74 node, semua referensi koneksi & `$('node')` valid, tidak ada secret plaintext bocor (`user_code`/`secret`/`device_id`/nomor lama Scholars = 0 hit).
- 3 node baru hadir & terhubung: `Process All → IF Media Manual → Format Media Notif → Notify Media Team`.
- `Notify Media Team` meniru persis pola `Notify Field Team` (auth httpCustomAuth, loop `phone`/`message` per item, continueOnFail).

**File buffer-cleanup & error-notifier TIDAK berubah** untuk update ini — tetap pakai `2026-07-15-*`.
