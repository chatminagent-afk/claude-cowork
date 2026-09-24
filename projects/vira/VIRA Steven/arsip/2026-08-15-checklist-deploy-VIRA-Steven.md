# Checklist Deploy — VIRA Steven

> ⛔ **KEDALUWARSA (2026-08-16).** Kehilangan langkah A6–A7 (header sheet baru), seluruh uji rantai
> `[DECK_REQUEST]`, dan bagian F-nya keliru — cap harian **tidak** aktif, bukan sekadar perlu disetel.
> **Baca `2026-08-16-checklist-deploy-VIRA-Steven.md`.** File ini disimpan hanya sebagai riwayat.

Urutkan dari atas. Jangan lompat ke iklan sebelum bagian **UJI** lulus semua.

---

## A. Google Sheet — sebagian sudah selesai

| # | Langkah | Status |
|---|---|---|
| A1 | Upload database ke Google Sheets | ✅ selesai |
| A2 | Hapus baris petunjuk supaya header di baris 1 | ✅ selesai (kamu sendiri) |
| A3 | Share spreadsheet ke **service account Google** sebagai **Editor** | ⬜ |
| A4 | Isi `CONFIG!B14` (`sheet_id`) dengan `1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk` | ⬜ |
| A5 | Isi `CONFIG!B11` (`kirimi_user_code`) dan `CONFIG!B12` (`kirimi_secret`) dari dashboard Kirimi | ⬜ |

> ⚠️ A3 memakai email service account (berakhiran `.iam.gserviceaccount.com`), **bukan** `chatminagent@gmail.com`. Kalau service account-nya belum jadi, ini yang menahan seluruh deploy.

---

## B. Isi tab LINKS — perlu kamu siapkan filenya

Lima baris di tab `LINKS` kolom **E (URL)** masih kosong dan statusnya `Nonaktif`. VIRA tidak akan pernah mengirimkannya selama masih kosong — jadi tidak ada risiko error, hanya fitur yang belum hidup.

| Nama Link | Yang perlu kamu siapkan | Catatan penting |
|---|---|---|
| `company-profile` | PDF profil singkat kamu + VIRA | Boleh 2–3 halaman saja |
| `deck-vira` | PDF deck VIRA versi umum | **Bukan** deck yang dibuat khusus per klien |
| `demo-video` | Video pendek cara VIRA bekerja | **Wajib pakai environment dummy**, bukan production klien |
| `portfolio` | Tangkapan layar sistem yang sudah kamu bangun | **Blur/de-brand dulu** — jangan ada nama klien, nomor, atau data user |
| `harga-ringkas` | Gambar tabel Basic vs Premium | Pastikan angkanya sama dengan tab `PROGRAM` |

Cara mengisi: upload file ke Google Drive → klik kanan → Share → *Anyone with the link* → salin link ke kolom E → ubah kolom `Status` dari `Nonaktif` jadi `Aktif`.

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

---

## E. UJI — sebelum iklan menyala

Pakai HP lain, chat ke **6285155202354**. Centang tiap baris.

| # | Uji | Yang harus terjadi |
|---|---|---|
| E1 | Kirim "halo" sebagai nomor baru | Dapat perkenalan "Steven versi AI", lalu ditanya balik |
| E2 | Tanya "kamu bot ya?" | Mengaku AI dengan jujur, tidak berkelit |
| E3 | Tanya "berapa harganya?" | Sebut kisaran 3jt/5jt + arahkan ke Steven, tidak menyebut harga add-on |
| E4 | Kirim 3 pesan beruntun cepat | Dibalas **sekali** secara utuh, bukan 3 balasan |
| E5 | Kirim foto apa saja | Isi fotonya dikomentari dengan benar |
| E6 | Chat dalam Bahasa Inggris | Dibalas dalam Bahasa Inggris |
| E7 | Tanya "klienmu siapa aja?" | **Menolak menyebut nama**, jelaskan alasan privasi |
| E8 | Tanya "kamu kerja di bank apa?" | Jawab "bank swasta nasional", **tidak menyebut nama bank** |
| E9 | Bilang "aku mau ngobrol sama Steven langsung" | Bot berhenti membalas + HP-mu dapat notifikasi |
| E10 | Cek tab `STATS` | Ada barismu, `Counter` bertambah, `bot_mode` jadi `OFF` setelah E9 |
| E11 | Ceritakan bisnis fiktif, minta dibuatkan pitch deck | Baris baru muncul di tab `REQUESTS` + notifikasi rangkuman ke HP-mu |
| E12 | Tanya sesuatu yang tidak ada di FAQ | Mengaku belum tahu + baris masuk ke tab `UNKNOWN` |
| E13 | Setelah E9, kirim chat lagi | **Tidak dibalas** (karena `bot_mode=OFF`) |
| E14 | Ubah `bot_mode` jadi kosong di sheet, chat lagi | Dibalas lagi |
| E15 | Matikan credential Anthropic sengaja, kirim chat | Eksekusi merah + notifikasi error masuk ke HP-mu |

> E15 penting: itu memastikan jaring pengamanmu benar-benar berfungsi. Kalau notifikasi tidak datang, jangan nyalakan iklan.

---

## F. Rem biaya — periksa sebelum iklan

Bot ini pakai API key personalmu. Iklan berarti volume tak terduga.

| # | Langkah |
|---|---|
| F1 | Set **spend limit** di Anthropic Console — ini pengaman terakhir yang tidak bisa di-bypass workflow |
| F2 | Cek `CONFIG` → `daily_message_cap` (default 500) — sesuaikan dengan budget harianmu |
| F3 | Cek `CONFIG` → `daily_vision_cap` (default 100) — gambar lebih mahal dari teks |
| F4 | Cek `CONFIG` → `rate_limit_max` (default 5 pesan/menit/nomor) |
| F5 | Hari pertama iklan: pantau tab `EVENTS` untuk baris `CAP_REACHED` |

> Script reels 8 dan 10 mengajak penonton "iseng-isengin" dan "coba jebol" AI-mu. Itu hook yang bagus, tapi artinya kamu **mengundang** stress-test. Pastikan F1–F4 beres sebelum dua script itu tayang.

---

## G. Titik lemah yang perlu kamu tahu

Bukan bug — keputusan desain dengan konsekuensi.

1. **Error Notifier membaca kredensial dari `CONFIG`.** Ini lebih aman daripada hardcode, tapi kalau sheet tidak terbaca, notifikasi error bisa ikut gagal. Kompensasinya: eksekusi tetap merah di dashboard n8n. **Biasakan cek dashboard, jangan hanya mengandalkan notifikasi WA.**
2. **`bot_mode=OFF` tidak punya auto-resume.** Sekali handover, bot diam untuk orang itu sampai kamu kosongkan selnya manual. Ini disengaja — tapi artinya kalau kamu lupa, prospek itu tidak akan pernah dibalas lagi.
3. **Cap harian disimpan di memori n8n**, bukan di sheet. Kalau n8n restart, counter-nya reset. Spend limit di Anthropic Console (F1) adalah pengaman yang sesungguhnya.
4. **Follow-up mengecualikan prospek yang sudah minta deck** (`deck_requested=Y`) — supaya mereka tidak diganggu bot padahal kamu sedang menyiapkan penawaran. Konsekuensinya: kalau kamu lupa follow-up manual, mereka tidak dikejar siapa pun.
5. **Arsip `.xlsx` lokal berbeda tipis dengan sheet live** — yang live sudah tanpa baris petunjuk. Yang jadi acuan adalah yang live.

---

## H. Urutan go-live yang kusarankan

1. Selesaikan A → C → D
2. Jalankan seluruh E. Perbaiki apa yang gagal, ulangi
3. Pasang F1 (spend limit) — jangan dilewat
4. Jalankan bot 2–3 hari tanpa iklan, tes sendiri dan minta 1–2 teman mencoba
5. Baca tab `UNKNOWN`, tambahkan jawaban yang hilang ke `FAQ`
6. Baru nyalakan iklan, mulai dari budget kecil
7. Setelah seminggu tenang, baru pertimbangkan menyalakan Follow-up (D7)
