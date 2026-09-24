---
Checklist finalisasi VIRA-PCR Main.json — dari state testing ke production
Dibuat: 2026-07-18 | Sumber: inspeksi langsung `draft workflow/VIRA-PCR Main.json` (live export n8n, 82 node)
---

# Checklist Go-Live VIRA-PCR

> **Temuan penting sebelum mulai:** file `VIRA-PCR Main.json` yang sedang ditesting masih membawa sisa kredensial **The Scholars** di beberapa node (bukan cuma butuh "ganti", tapi memang salah/bocor). Detail ada di §8 dan §9 — baca itu dulu sebelum eksekusi checklist 1-7, karena beberapa node TIDAK akan ikut berubah otomatis walau CONFIG sheet sudah diupdate.

---

## 1. Login Kirimi di nomor WA VIRA PCR
- [ ] Login/setup akun Kirimi baru pakai nomor WA yang akan jadi device VIRA PCR (bukan nomor The Scholars).
- [ ] Catat 3 nilai dari dashboard Kirimi: `user_code`, `secret`, `device_id`.
- [ ] Simpan 3 nilai ini — dipakai di §5 (CONFIG sheet) **dan** §8 (5 node yang hardcoded, tidak baca dari CONFIG).

## 2. Login Gmail & setup Google Cloud service (seperti The Scholars)
- [ ] Login Gmail baru khusus PCR.
- [ ] Buat Google Cloud Project baru (atau pakai existing project PCR) — aktifkan **Google Sheets API** dan **Google Drive API**.
- [ ] Buat OAuth 2.0 Client ID (atau Service Account, sesuaikan dengan yang dipakai The Scholars) untuk dipakai sebagai credential Google Sheets di n8n.

## 3. Upload database Google Sheet + dokumentasi ke folder Gmail PCR
- [ ] Copy/upload spreadsheet `Persada_Cisoka_Database` ke Drive akun Gmail PCR (sheet ID lama di workflow: `1dJWq7iq5PRGRguW6GRAgtclgvhSqppa-D6tSNrAo1PU` — cek dulu apakah ini sudah dibuat di akun PCR atau masih nebeng akun lama).
- [ ] Upload juga dokumentasi terkait (pitchdeck, checklist QA, form kebutuhan data) ke folder yang sama supaya terpusat.
- [ ] Catat **Sheet ID baru** (dari URL spreadsheet) — dipakai di §8.

## 4. Cek ulang informasi setiap sheet
Tab yang perlu direview isinya sebelum go-live: **CONFIG, PRODUK, FAQ, LINKS, STATS, MSG_BUFFER, SURVEY, EVENTS, UNKNOWN, CALL_REQUEST**.
- [ ] PRODUK: field `Status Stok` masih placeholder (belum ada data stok real per form 07-17) — cek `[persada-cisoka-status.md]`.
- [ ] PRODUK: `Dimensi Tanah` untuk tipe 36/81 masih gap.
- [ ] FAQ: cek jam operasional kantor pemasaran fisik (ada inkonsistensi: hotline 24 jam vs FAQ lain sebut 09.00–17.00).
- [ ] FAQ: verifikasi link Google Maps resmi (yang ada di FAQ r30 vs jawaban form "via WA").
- [ ] LINKS: masih ada URL Drive **dummy** dari Steven untuk video & foto (video id `1gJPQYKOG4UK4XonHe6GIDYMDctlRtxXC`, foto id `1z20ZYoZ4nXl1X-7K_qq6wMPz3IbWSmRT`) — WAJIB diganti ke file asli sebelum go-live, dan video perlu review isi + izin tim dulu.
- [ ] CONFIG: 3 key `kirimi_*` masih placeholder `(ISI: ...)`.

## 5. Replace nomor HP dengan yang sesuai
Semua nomor tim ada di tab **CONFIG** (bukan hardcode di workflow — kecuali 5 node di §8 poin C):
- [ ] `field_team_phone` → nomor Om Sulianto (untuk notif survey fix).
- [ ] `media_team_phone` → nomor Aar + Aqsa (notif permintaan media manual).
- [ ] `admin_phone` → nomor admin/Steven untuk notif error/unknown.
- [ ] Klarifikasi: nomor WA bot saat ini `6281299500371` = sama dengan nomor Aqsa (telemarketer) — perlu dipastikan ini benar atau salah input, karena kalau salah nomor bot bisa bentrok sama nomor kerja Aqsa.
- [ ] Cek nomor Aca (belum ada) dan format nomor Putri (belum sesuai) — dari gap data form 07-17.

## 6. Replace links dengan link file yang baru diupload di Gmail PCR
- [ ] Setelah upload ulang media (foto/video/brosur) ke Drive akun PCR (§3), update kolom URL di tab **LINKS** — pastikan formatnya `uc?export=download&id=...` (bukan link share biasa), karena node `Download Media` butuh binary GET langsung.
- [ ] Pastikan permission file di Drive PCR **"Anyone with the link"** (kalau private, `Download Media` akan gagal fetch).
- [ ] Update juga link Google Maps di FAQ kalau berubah (lihat §4).

## 7. Buat credentials baru di n8n
- [ ] **Google Sheets OAuth2** — credential baru pakai akun Gmail PCR (§2). Nama credential lama di semua node: `"Google Sheets account"` (id `8TSFDcV58PfhioCB`) — pastikan bikin credential baru, jangan reuse punya The Scholars.
- [ ] **Anthropic API (Claude)** — credential baru pakai API key Claude milik PCR/Steven. *Catatan: workflow saat ini TIDAK pakai Claude sama sekali — 2 node Chat Model masih pakai OpenAI `gpt-4.1-mini`. Ini bukan "ganti credential" tapi ganti tipe node juga, lihat §8 poin B.*
- [ ] *(Opsional tapi disarankan)* **Kirimi HTTP Custom Auth** — kalau mau rapikan 5 node hardcoded di §8 poin C jadi pakai credential n8n proper, bukan CONFIG-sheet-expression atau hardcode di body.

## 8. Node-by-node yang harus disesuaikan di n8n

### A. Google Sheets nodes — 23 node, ganti credential + Document ID
Semua 23 node ini pakai credential yang sama (`"Google Sheets account"`) dan **document ID yang sama** (hardcoded literal di tiap node, BUKAN via ekspresi — lihat catatan drift di §9). Ubah **credential** ke akun PCR (§7) dan **Document ID** ke sheet ID baru (§3) di **setiap node ini satu per satu** (n8n tidak auto-propagate walau nama sheet sama):

1. Read CONFIG
2. Read User STATS
3. Append MSG_BUFFER
4. Update Buffer
5. Read STATS for HITL
6. Re-Read STATS Debounce
7. Read MSG_BUFFER
8. Read FAQ
9. Read PRODUK Data
10. Read LINKS Data
11. Write SURVEY
12. Update STATS Survey
13. Log EVENTS Delegated
14. Log Call Request
15. Record to UNKNOWN
16. Read STATS
17. Update to STATS
18. Delete_Pending_Msg
19. Update Greeting
20. Update row in sheet
21. Delete_Pending_Msg_Bot_Off
22. Delete_Pending_Msg_Error
23. Delete_Pending_Msg_Bot_Off1

> Tips n8n: select semua 23 node ini (klik+drag atau ctrl-klik satu-satu di canvas), lalu ganti credential dari panel kanan bisa dilakukan sekaligus untuk field credential (tapi Document ID tetap harus per-node kalau field-nya beda per node — di case ini semua sama, jadi kalau n8n versi lo support "bulk edit expression" bisa dicoba, kalau tidak ya manual 23x).

### B. AI Model nodes — 2 node, ganti tipe node OpenAI → Anthropic
| Node | Sekarang | Ubah jadi |
|---|---|---|
| **OpenAI Chat Model** | `@n8n/n8n-nodes-langchain.lmChatOpenAi`, model `gpt-4.1-mini`, credential `OpenAi account` (dipakai oleh **AI Agent** utama) | Ganti ke node **Anthropic Chat Model** (`lmChatAnthropic`), pilih model Claude yang sesuai (samakan dengan VIRA The Scholars kalau mau konsisten), credential = Anthropic API PCR baru dari §7 |
| **OpenAI Chat Model1** | sama, dipakai oleh **FAQ Retrieve** | sama treatment-nya |

> Ini bukan sekadar ganti credential — node lama harus **dihapus & diganti node baru** (`lmChatAnthropic`), lalu re-connect wire-nya ke AI Agent / FAQ Retrieve masing-masing. Kalau connection putus, kedua fitur itu berhenti total.

### C. Kirimi HTTP nodes — 11 node, dikelompokkan per masalah

**C1. Sudah rapi, otomatis ikut CONFIG sheet (1 node)** — tinggal isi 3 key `kirimi_*` di CONFIG (§4), node ini tidak perlu diedit manual:
- `Send Media Kirimi` (baca `kirimi_user_code/secret/device_id` via ekspresi `Parse Config`)

**C2. ⚠️ Kirim ke Kirimi TAPI tanpa `user_code/secret/device_id` sama sekali di body (4 node)** — ini kemungkinan **bug**, bukan sekadar butuh ganti nomor. Body-nya cuma `phone` + `message`, tidak ada auth params, jadi kemungkinan call ini gagal ke API Kirimi (kecuali memang ada mekanisme auth lain yang saya belum lihat). **Wajib ditest ulang saat UAT**, dan kalau gagal — tambahkan 3 field `user_code/secret/device_id` dengan ekspresi yang sama seperti C1:
- `Notify Admin Unknown`
- `Notify Admin API Error`
- `Notify Admin Media Error`
- `Reply Error`

**C3. 🚨 Kredensial Kirimi HARDCODED plaintext di body (5 node)** — nilainya **bukan** dari CONFIG sheet sama sekali, jadi **mengubah CONFIG tidak akan mengubah node ini**. Ini tampaknya kredensial device **The Scholars** yang kebawa waktu clone workflow. Harus diedit manual satu-satu, ganti ke `user_code`/`secret`/`device_id` PCR dari §1 (atau lebih baik: ganti jadi ekspresi `{{ $('Parse Config').first().json.config.kirimi_user_code }}` dkk supaya konsisten dan tidak plaintext lagi):
- `Reply Chat Kirimi` ⚠️ **paling kritis — ini node yang kirim balasan AI ke SETIAP chat user**
- `Notify Media Team`
- `Notify Field Team`
- `Notify Talk to Admin`
- `Notify User Error`

**C4. Bukan Kirimi (1 node)** — GET binary dari Google Drive, tidak butuh credential Kirimi:
- `Download Media` (URL dinamis dari kolom LINKS — otomatis ikut §6, tidak perlu diedit di node)

## 9. Catatan drift lain yang ditemukan (bukan diminta, tapi relevan)
- Node **`Bootstrap Config`** (code node paling awal) punya komentar *"satu-satunya titik edit manual per klien"* dengan constant `SHEET_ID`, tapi ternyata **tidak ada satupun dari 23 node Google Sheets yang membaca `sheet_id` ini** — semua pakai URL hardcoded sendiri-sendiri. Jadi asumsi desain awal ("edit 1 tempat, semua ikut") **tidak berlaku di file live ini**. Kalau mau benerin sekalian, bisa disambungkan lewat ekspresi `{{ $('Bootstrap Config').first().json.sheet_id }}` di 23 node itu — atau abaikan saja dan terima kalau ganti sheet ID = edit manual 23x tiap kali (sesuai §8A).
- Jalur `_extraction/build/assemble.py` (build script) sudah **drift** dari file live — jangan dipakai sebagai referensi, `VIRA-PCR Main.json` adalah satu-satunya sumber kebenaran (sudah tercatat juga di memory proyek).

## 10. Workflow pendamping (jangan lupa — beda file dari Main)

### A. MSG_BUFFER Cleanup (`VIRA-PCR - MSG_BUFFER Cleanup`, jadwal harian 03:00 WIB)
Housekeeping sudah jalan, tapi masih menunjuk credential/sheet testing. Sebelum go-live:
- [ ] Ganti **Google credential** ke akun PCR (§7) — samakan dengan Main (idealnya OAuth2 yang sama, biar 1 credential untuk semua).
- [ ] Ganti **Document ID** (sheet ID) ke sheet production PCR (§3) di semua node yang baca/hapus MSG_BUFFER.
- [ ] Pastikan workflow **active: true** di production.
- [ ] Tes 1x manual dulu (dry-run / MSG_BUFFER berisi baris kedaluwarsa + baris segar) → pastikan hanya baris kedaluwarsa yang terhapus, jangan buffer aktif.

### B. Error-notifier (masih template — lihat register #10)
- [ ] Konfirmasi workflow ber-ID `rBsq-mGgHfqfwbz3YmwxI` = error-notifier PCR.
- [ ] Ganti `phone` `{{ADMIN_PHONE}}` → nomor admin asli (literal `628...` atau expression valid).
- [ ] Buat/samakan credential Kirimi (konsisten pola body-parameter seperti Main).
- [ ] Aktifkan; tes paksa error di Main → notif WA admin masuk.

---

## Ringkasan urutan eksekusi yang disarankan
1. §1 + §2 + §3 (setup akun & sheet baru) dulu — biar ada nilai konkret buat isi ke n8n.
2. §7 (buat credential n8n) — Google Sheets PCR + Anthropic.
3. §8A (23 node Sheets) + §8B (2 node AI model) — ganti credential/tipe node.
4. §4, §5, §6 (isi data sheet: CONFIG, PRODUK, FAQ, LINKS) — sekarang CONFIG-driven nodes (C1) otomatis ikut.
5. §8C2 dan §8C3 — **wajib**, karena tidak ikut otomatis dari CONFIG. Prioritaskan `Reply Chat Kirimi` duluan karena itu jalur utama.
6. Full UAT ulang: kirim chat test, cek semua notif (admin/media/field team) benar-benar masuk ke nomor PCR yang benar — bukan nomor The Scholars.
