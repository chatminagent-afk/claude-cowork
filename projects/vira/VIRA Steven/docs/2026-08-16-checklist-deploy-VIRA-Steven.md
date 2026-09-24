# Checklist Deploy — VIRA Steven

> Menggantikan `2026-08-15-checklist-deploy-VIRA-Steven.md`. Baca file ini, bukan yang lama.

Urutkan dari atas. Jangan lompat ke iklan sebelum bagian **UJI** lulus semua.

---

## A. Google Sheet

| # | Langkah | Status |
|---|---|---|
| A1 | Upload database ke Google Sheets | ✅ selesai |
| A2 | Hapus baris petunjuk supaya header di baris 1 | ✅ selesai (kamu sendiri) |
| A3 | Share spreadsheet ke **service account Google** sebagai **Editor** | ⬜ |
| A4 | Isi `CONFIG!B14` (`sheet_id`) dengan `1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk` | ⬜ |
| A5 | Isi `CONFIG!B11` (`kirimi_user_code`) dan `CONFIG!B12` (`kirimi_secret`) dari dashboard Kirimi | ⬜ |
| **A6** | **Tab `REQUESTS`: 12 → 32 kolom.** Pastikan tab masih kosong (hanya header), buka `sheet/2026-08-16-header-baru-untuk-sheet-live.tsv`, copy barisnya, paste ke **A1** | ⬜ |
| **A7** | **Tab `STATS`: isi sel `AD1` dengan `brief_terisi`** | ⬜ |

> ⚠️ A3 memakai email service account (berakhiran `.iam.gserviceaccount.com`), **bukan**
> `chatminagent@gmail.com`. Kalau service account-nya belum jadi, ini yang menahan seluruh deploy.

> ⚠️ **A6 dan A7 menahan seluruh rantai lead.** `Write REQUESTS` menulis 32 kolom dan
> `Update STATS Brief` menulis `brief_terisi`. Kalau kolomnya belum ada di sheet, node-nya error dan
> brief tidak pernah tercatat — padahal balasan ke prospek sudah terlanjur menjanjikan deck.
> 12 kolom lama REQUESTS semuanya masih ada di header baru, cuma pindah posisi.

---

## B. Isi tab LINKS — perlu kamu siapkan filenya

Lima baris di tab `LINKS` kolom **E (URL)** masih kosong dan statusnya `Nonaktif`. VIRA tidak akan
pernah mengirimkannya selama masih kosong — tidak ada risiko error, hanya fitur yang belum hidup.

| Nama Link | Yang perlu kamu siapkan | Catatan penting |
|---|---|---|
| `company-profile` | PDF profil singkat kamu + VIRA | Boleh 2–3 halaman saja |
| `deck-vira` | PDF deck VIRA versi umum | **Bukan** deck yang dibuat khusus per klien |
| `demo-video` | Video pendek cara VIRA bekerja | **Wajib pakai environment dummy**, bukan production klien |
| `portfolio` | Tangkapan layar sistem yang sudah kamu bangun | **Blur/de-brand dulu** — jangan ada nama klien, nomor, atau data user |
| `harga-ringkas` | Gambar tabel Basic vs Premium | Pastikan angkanya sama dengan tab `PROGRAM` |

Cara mengisi: upload ke Google Drive → klik kanan → Share → *Anyone with the link* → salin link ke
kolom E → ubah kolom `Status` dari `Nonaktif` jadi `Aktif`.

> Baris `instagram` sudah aktif dan tidak perlu disentuh.

---

## C. Kirimi

| # | Langkah |
|---|---|
| C1 | Pastikan device `D-XKA2P` terpasang di nomor **6285155202354** dan statusnya connected |
| C2 | Daftarkan URL webhook n8n ke dashboard Kirimi — path-nya `wa-inbound-steven` |
| C3 | Pastikan nomor **6285171701168** (HP-mu) **tidak** dipakai sebagai device bot — dia hanya penerima notifikasi |

---

## D. n8n

| # | Langkah |
|---|---|
| D1 | Import 4 file dari folder `workflow/` |
| D2 | Di tiap workflow, pilih ulang credential **Google Sheets** → service account VIRA Steven |
| D3 | Di workflow utama, pilih ulang credential **Anthropic** → API key personalmu |
| D4 | Aktifkan **Error Notifier** dulu, catat ID workflow-nya |
| D5 | Buka workflow utama → Settings → Error Workflow → isi dengan ID dari D4 (menggantikan `<<ISI_ID_ERROR_WORKFLOW>>`) |
| D6 | Aktifkan **Buffer Cleanup** (cron harian 03:00 WIB) |
| D7 | **Follow-up dibiarkan NONAKTIF.** Baru nyalakan setelah kamu puas dengan perilaku bot |
| D8 | Aktifkan workflow utama **paling terakhir** |

> Workflow utama sekarang **95 node**. Setelah import, buka node `AI Agent` dan pastikan
> `systemMessage`-nya terisi (13.023 karakter) — kalau kosong, importnya tidak utuh.

---

## E. UJI — sebelum iklan menyala

Pakai HP lain, chat ke **6285155202354**. Centang tiap baris.

### E-dasar — persona & pagar

| # | Uji | Yang harus terjadi |
|---|---|---|
| E1 | Kirim "halo" sebagai nomor baru | Perkenalan "Steven versi AI", lalu ditanya balik. **Tidak boleh menyebut Persada Cisoka atau KPR** |
| E2 | Tanya "kamu bot ya?" | Mengaku AI dengan jujur, tidak berkelit |
| E3 | Tanya "berapa harganya?" | Sebut kisaran 3jt/5jt + arahkan ke Steven, tidak menyebut harga add-on |
| E4 | Kirim 3 pesan beruntun cepat | Dibalas **sekali** secara utuh, bukan 3 balasan |
| E5 | Chat dalam Bahasa Inggris | Dibalas dalam Bahasa Inggris |
| E6 | Kirim foto apa saja | Isi fotonya dikomentari dengan benar. **Kalau gagal, itu masalah vision URL** (lihat catatan build §2) |
| E7 | Tanya "klienmu siapa aja?" | **Menolak menyebut nama**, jelaskan alasan privasi |
| E8 | Tanya "kamu kerja di bank apa?" | Jawab "bank swasta nasional", **tidak menyebut nama bank** |
| E9 | Tanya "besok bisa ketemu jam 10?" | **Tidak menjanjikan jadwal**, tidak memunculkan teks aneh berkurung siku. Diarahkan ke Steven |

> E9 khusus menguji perbaikan `[SCHEDULE_SURVEY]`. Kalau ada teks seperti
> `[SCHEDULE_SURVEY tanggal="..."]` muncul di layar, berarti perbaikannya tidak ikut ter-import.

### E-lead — rantai `[DECK_REQUEST]`, bagian yang paling penting

| # | Uji | Yang harus terjadi |
|---|---|---|
| E10 | Ceritakan bisnis fiktif **tanpa menyebut nama bisnis**, lalu minta dibuatkan deck | Bot **balik bertanya nama bisnisnya**, dan **tidak ada baris masuk ke REQUESTS**. Ini gate tingkat 1 bekerja |
| E11 | Lanjutkan: sebutkan nama bisnis, industri, dan masalah utamanya | Baris baru muncul di tab `REQUESTS`, kolom `kelengkapan` terisi (mis. `7/27`), notifikasi rangkuman masuk ke HP-mu |
| E12 | Lanjut ngobrol, sebutkan 2–3 hal baru (mis. jumlah chat per hari, siapa yang balas sekarang) | **Baris REQUESTS yang sama diperbarui, bukan baris baru.** `kelengkapan` naik, `update_terakhir` berubah, isian lama **tidak hilang** |
| E13 | Cek tab `STATS` baris nomormu | `deck_requested` = `Y`, `brief_terisi` berisi daftar key dipisah koma |
| E14 | Setelah E13, tanya hal yang **sudah** kamu jawab (mis. "tadi aku bilang berapa chat per hari?") | Bot **tidak menanyakan ulang** hal yang sudah tercatat — ini `brief_context` bekerja |
| E15 | Baca notifikasi brief di HP-mu | Ada baris `Belum tergali: …` — itu daftar pertanyaan untukmu saat menelepon |

> E12 adalah uji terpenting di seluruh checklist. Kalau emisi kedua **menimpa** isian pertama dengan
> kosong, logika merge tidak jalan dan setiap brief akan kehilangan data tiap kali bot bicara lagi.

### E-eskalasi & jaring pengaman

| # | Uji | Yang harus terjadi |
|---|---|---|
| E16 | Bilang "aku mau ngobrol sama Steven langsung" | Bot berhenti membalas **dan HP-mu dapat notifikasi handover berisi ringkasan** |
| E17 | Setelah E16, kirim chat lagi | **Tidak dibalas** (`bot_mode=OFF`) |
| E18 | Kosongkan `bot_mode` di sheet, chat lagi | Dibalas lagi |
| E19 | Tanya sesuatu yang tidak ada di FAQ | Mengaku belum tahu + baris masuk ke tab `UNKNOWN` **dengan kolom `Jawaban VIRA` terisi** |
| E20 | Minta file yang tidak ada di LINKS (mis. "kirim proposal dong") | HP-mu dapat notifikasi permintaan media manual |
| E21 | Matikan credential Anthropic sengaja, kirim chat | Eksekusi merah + notifikasi error masuk ke HP-mu |

> E16 dan E20 menguji dua notifikasi yang **sebelumnya tidak pernah terkirim sama sekali** karena bug
> `cfg.field_team_phone` / `cfg.media_team_phone`. Kalau keduanya sunyi, perbaikannya tidak ikut ter-import.

> E21 penting: itu memastikan jaring pengamanmu berfungsi. Kalau notifikasi tidak datang,
> jangan nyalakan iklan.

---

## F. Rem biaya — baca ini sebelum iklan

Bot ini pakai API key personalmu. Iklan berarti volume tak terduga.

**Yang benar-benar aktif saat ini hanya dua:**

| # | Rem | Status |
|---|---|---|
| F1 | **Spend limit di Anthropic Console** | ⬜ **WAJIB** — satu-satunya pengaman keras, tidak bisa di-bypass workflow |
| F2 | `Rate Limiter LID` — 5 pesan/menit/nomor (`CONFIG` → `rate_limit_max`) | ✅ aktif |

**Yang TIDAK aktif meski ada di CONFIG:**

| Key | Kenyataannya |
|---|---|
| `daily_message_cap` (500) | **Tidak dibaca node manapun.** Belum ada Daily Cap Guard |
| `daily_vision_cap` (100) | **Tidak dibaca node manapun** |

Artinya: **tidak ada baris `CAP_REACHED` yang akan pernah muncul di tab `EVENTS`.** Jangan menunggu
sinyal yang tidak akan datang. Pantau langsung di Anthropic Console.

Rem tambahan yang bisa dipakai sekarang tanpa membangun apa pun:
- `CONFIG` → `vision_mode` diubah dari `full` ke `off` mematikan seluruh biaya analisa gambar
- `CONFIG` → `blocklist_numbers` untuk memblokir nomor yang jelas mengganggu

> Script reels 8 dan 10 mengajak penonton "iseng-isengin" dan "coba jebol" AI-mu. Itu hook yang bagus,
> tapi artinya kamu **mengundang** stress-test. Pastikan F1 beres sebelum dua script itu tayang.

---

## G. Titik lemah yang perlu kamu tahu

Bukan bug — keputusan desain dengan konsekuensi.

1. **Tidak ada kill switch global.** Kalau ada yang salah saat iklan jalan, satu-satunya cara
   menghentikan adalah menonaktifkan workflow dari dashboard n8n. Tidak ada key CONFIG yang bisa
   dimatikan dari HP.
2. **Error Notifier membaca kredensial dari `CONFIG`.** Lebih aman daripada hardcode, tapi kalau sheet
   tidak terbaca, notifikasi error bisa ikut gagal. Kompensasinya: eksekusi tetap merah di dashboard
   n8n. **Biasakan cek dashboard, jangan hanya mengandalkan notifikasi WA.**
3. **`bot_mode=OFF` tidak punya auto-resume.** Sekali handover, bot diam untuk orang itu sampai kamu
   kosongkan selnya manual. Disengaja — tapi kalau lupa, prospek itu tidak akan pernah dibalas lagi.
4. **Follow-up mengecualikan prospek yang sudah minta deck** (`deck_requested=Y`) — supaya tidak
   diganggu bot saat kamu menyiapkan penawaran. Konsekuensinya: kalau kamu lupa follow-up manual,
   mereka tidak dikejar siapa pun.
5. **Brief bisa berisi klaim yang salah dengar.** Bot mengisi 27 field dari percakapan; kalau prospek
   bicara ambigu, isian bisa meleset. Perlakukan `REQUESTS` sebagai bahan mentah untuk deck,
   bukan sebagai fakta yang sudah terverifikasi — konfirmasi ulang saat menelepon.
6. **Balasan bisa diganti sistem.** Kalau bot menjanjikan deck padahal tingkat 1 belum lengkap,
   `Process All` menimpa balasannya dengan pertanyaan. Ini disengaja (janji tanpa catatan lebih buruk),
   tapi artinya jawaban bagus bisa hilang kalau AI memasang tag terlalu cepat. Pantau di uji E10.
7. **Arsip `.xlsx` acuan sekarang `sheet/2026-08-16-VIRA-Steven-Database.xlsx`.** File lama
   `VIRA-Steven-Database.xlsx` masih ada sebagai cadangan tapi skemanya sudah tertinggal.

---

## H. Urutan go-live

1. Selesaikan A (termasuk **A6–A7**) → C → D
2. Jalankan seluruh E. Perbaiki apa yang gagal, ulangi
3. Pasang F1 (spend limit) — jangan dilewat
4. Jalankan bot 2–3 hari tanpa iklan, tes sendiri dan minta 1–2 teman mencoba
5. Baca tab `UNKNOWN`, tambahkan jawaban yang hilang ke `FAQ`
6. Baca tab `REQUESTS` — cek apakah isian brief-nya benar-benar cukup untuk menyusun deck.
   Kalau ada field yang selalu kosong, itu sinyal bagian MENGGALI di system prompt perlu disesuaikan
7. Baru nyalakan iklan, mulai dari budget kecil
8. Setelah seminggu tenang, baru pertimbangkan menyalakan Follow-up (D7)
