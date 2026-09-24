# Analisis Biaya Token VIRA-PCR — kenapa Sonnet 2× lebih mahal dari thescholars

Tanggal: 2026-07-20
Basis: `workflow/production/VIRA-PCR Main V1.2.json` (live) vs `the scholars/report/production/VIRA V4.json` (live, 1 bulan berjalan)
Tokenizer: `cl100k_base` sebagai proksi (±5% terhadap tokenizer Anthropic; cukup untuk perbandingan relatif)

---

## 1. Koreksi dari analisis sebelumnya

Di sesi sebelumnya saya menulis bahwa perbandingan dengan thescholars "kemungkinan besar keliru", berdasarkan angka **`systemMessage ~9rb kata`** di `2026-07-15-analisis-arsitektur-VIRA-eksisting.md` baris 64.

**Angka itu salah, dan kesimpulan saya ikut salah.** Setelah membaca file V4 langsung:

| | Kata | Token | Char |
|---|---|---|---|
| VIRA V4 (thescholars) `systemMessage` | **2.027** | **4.495** | 13.454 |
| VIRA-PCR V1.2 `systemMessage` | 3.244 | **7.464** | 22.552 |

Dokumen analisis lama melebih-lebihkan V4 sekitar 4,4×. Billing kamu valid, dan intuisimu benar sejak awal: **prompt PCR memang jauh lebih panjang.**

---

## 2. Di mana selisihnya

Arsitektur kedua workflow identik (Simple Memory window 10, maxTokens 512, `data_context` + `faq_context` disuntik ke systemMessage, tanpa tool). Selisih biaya lahir dari dua tempat saja:

| Komponen | VIRA V4 | VIRA-PCR V1.2 | Selisih |
|---|---|---|---|
| `systemMessage` statis | 4.495 tok | 7.464 tok | **+2.969** |
| `data_context` | 305–1.195 tok (**kondisional**) | 1.698 tok (**selalu**) | **+~1.100** |
| `faq_context` (top-4) | ~298 tok | ~251 tok | −47 |
| `ai_input_text` | ~250 tok | ~350 tok | +100 |
| Simple Memory (window 10) | ~1.300 tok | ~1.300 tok | 0 |
| **Total input / giliran** | **~6.900 tok** | **~11.060 tok** | **+4.160 (+60%)** |

Biaya per giliran (Sonnet $3/$15 per juta, output ~200 tok):

- V4: 6.900 × $3/M + $0,003 = **$0,024** → sesuai billing $0,02
- PCR: 11.060 × $3/M + $0,003 = **$0,036** → sesuai billing $0,03–0,04

Model biaya ini cocok sampai ke digit terakhir, termasuk kenapa eksekusi #1 kena $0,03 (memory masih kosong) sementara #2 dan #3 kena $0,04. Tidak ada kebocoran, tidak ada anomali. **Sonnet tidak mahal — prompt PCR yang 60% lebih berat.**

### 2a. Penyebab utama: `data_context` PCR tidak kondisional

Ini regresi paling mahal dan paling mudah diperbaiki.

`FAQ Retrieve` di **V4** menyaring per intent — harga hanya dikirim saat `askingPrice || wantsToRegister || askingProgramDetail`, syarat hanya saat `askingSyarat`, bio Sam hanya saat `askingAboutSam`. Hasilnya 305 token di turn dingin, 1.195 token di turn terberat.

`FAQ Retrieve` di **PCR** melakukan sebaliknya: loop generik yang mengirim **seluruh 19 kolom PRODUK tanpa syarat**, setiap giliran. Komentar di kode menyebut alasannya — supaya robust kalau sheet direstrukturisasi. Niatnya bagus, tapi harganya 1.306 token per giliran, termasuk saat user cuma bilang "halo".

Yang ikut terkirim setiap giliran padahal tidak pernah dipakai AI: kolom `Catatan` ("Sumber: pricelist resmi (foto)"), `Last Update`, dan `No`.

---

## 3. Yang dipangkas dari system prompt

File hasil: **`2026-07-20-systemprompt-V1.3-trimmed.md`**

**7.464 → 5.209 token (−2.255, −30%)**

Prinsip: yang dipangkas hanya (a) instruksi yang sudah dijalankan sistem di luar prompt, (b) aturan yang ditulis 2–3 kali di section berbeda, (c) catatan developer yang tidak ditujukan ke AI. Tidak ada aturan faktual, format tag, atau anchor gaya yang dihapus.

### 3.1 Instruksi tanggal — DIHAPUS (~450 tok) 🔴 ini bahkan memperbaiki akurasi

V1.2 `# SURVEY` berisi:

> "TANGGAL WAJIB dihitung dari TANGGAL_SEKARANG di [SYSTEM_DATA], format YYYY-MM-DD. 'Besok' = TANGGAL_SEKARANG tambah 1 hari. 'Senin' / 'Senin depan' = hari Senin terdekat SETELAH hari ini. JANGAN menebak tahun…"

Padahal node `Preprocess - Context Detection` sudah menyuntikkan tabel jadi ke setiap pesan:

```
HARI_KE_TANGGAL (WAJIB pakai daftar ini, DILARANG menghitung/menebak tanggal sendiri):
  Selasa (besok) = 2026-07-21
  Rabu (lusa) = 2026-07-22
  ...
```

Jadi prompt menyuruh AI **menghitung**, sementara input menyuruh AI **jangan menghitung, pakai tabel**. Kontradiktif sekaligus mubazir. Diganti satu baris:

> "TANGGAL: ambil PERSIS dari tabel HARI_KE_TANGGAL di [SYSTEM_DATA]. DILARANG menghitung atau menebak tanggal sendiri. Format YYYY-MM-DD."

**Ini bukan sekadar penghematan** — menghapus perintah "hitung sendiri" menutup satu jalur halusinasi tanggal, dan itu justru bagian yang paling rawan kalau nanti pindah ke Haiku.

### 3.2 Aturan validasi slot — 4 bullet jadi 1 (~600 tok)

V1.2 menyatakan aturan yang sama dari empat sudut berbeda:

1. "SURVEY HARI INI BOLEH. Tidak ada aturan harus pesan jauh-jauh hari…"
2. "KAMU TIDAK MEMUTUSKAN SENDIRI apakah sebuah slot masih tersedia…"
3. "DILARANG menolak jam di hari ini dengan alasan 'sudah terlalu sore'…"
4. "Yang BOLEH kamu tolak duluan hanya kalau jelas-jelas di luar jangkauan…"

Pola akresi klasik — tiap bullet kemungkinan ditambahkan setelah satu kegagalan spesifik. Empat pernyataan yang saling tumpang tindih justru lebih lemah daripada satu aturan tegas, karena model harus merekonsiliasi keempatnya. Digabung jadi satu bullet yang memuat seluruh isi keempatnya, termasuk contoh batas ("jam sudah lewat" dan "di luar JAM_OPERASIONAL_SURVEY").

### 3.3 `# PROFIL USER` — dedupe (~500 tok)

Aturan minta nama+domisili sebelumnya ditulis di **empat** tempat: `# ALUR` poin 3, `# INTRO USER BARU` bullet 3, `# PROFIL USER` (paling panjang), dan `# SURVEY`. **Plus** disuntikkan runtime oleh `Cek_user_status` sebagai `CRITICAL INSTRUCTION: MINTA DATA: user ini belum melengkapi…`.

Yang runtime itu paling otoritatif karena tahu state aktualnya. Section prompt dipadatkan jadi rujukan + nada bicara, bukan pengulangan logika.

### 3.4 Daftar key media hardcoded — DIHAPUS (~120 tok) 🔴 ini juga menutup bug

V1.2 `# TAG` menulis:

> "Key kanonik yang ada: brosur, foto-36-72, foto-36-81, foto-30-60, video-36-72, video-36-81, video-30-60, maps, website."

Daftar ini duplikat dari blok `LINK/MEDIA AKTIF` di `data_context`, yang sudah dibaca dari sheet LINKS lengkap dengan Tipe, Tipe Unit, dan Keyword. **Dan daftar hardcoded ini akan basi begitu kamu edit sheet LINKS** — AI akan menyebut key yang sudah tidak ada, atau tidak tahu key baru. Dihapus; prompt sekarang murni menunjuk ke DATA.

### 3.5 Catatan developer di dalam prompt produksi (~350 tok)

Yang ikut terkirim ke API setiap giliran, padahal ditujukan untuk kamu:

- `🔶konfirmasi lokasi` di baris identitas
- `🚧 KALAU klien memutuskan register netral -> ganti seluruh blok ini … seperti V4` (seluruh paragraf)
- `🔶Rp…` di contoh ritme — placeholder yang bisa ditiru AI sebagai output literal
- `🔶contoh "Senin-Jumat jam 9-16"` — jam yang berbeda dari CONFIG, berisiko dipakai AI
- `(catatan teknis: pastikan pesan non-teks tidak di-drop diam-diam — lihat risiko #7 dokumen analis; idealnya user tetap dapat balasan ini)`

Yang terakhir paling berbahaya: itu instruksi engineering yang ditulis seolah instruksi ke AI, di dalam `# LARANGAN`.

### 3.6 Merge `# KALAU RAGU ATAU DIBANTAH` + `# HAL YANG TIDAK BOLEH DIJAWAB SENDIRI` (~350 tok)

Section kedua membuka dengan "Pola eskalasinya sama dengan # KALAU RAGU ATAU DIBANTAH" lalu menjelaskan ulang pola itu di setiap dari empat itemnya. Digabung jadi `# ESKALASI`: prinsip sekali di atas, empat item jadi satu baris masing-masing.

### 3.7 `# ALUR` dan `# GALI KEBUTUHAN` — dipadatkan (~400 tok)

`# ALUR` adalah daftar isi yang menarasikan ulang setiap section di bawahnya. Dipertahankan sebagai urutan prioritas (fungsinya nyata) tapi tanpa mengulang isi section. `# GALI KEBUTUHAN` bullet "PENGECUALIAN 1-2 tipe" dipadatkan tanpa kehilangan aturan bahwa tipe SUBSIDI tidak boleh disembunyikan.

### Yang SENGAJA TIDAK dipangkas

| Bagian | Alasan |
|---|---|
| `# SUMBER FAKTA` | Utuh. Ini benteng anti-halusinasi. |
| String intro verbatim | Harus persis, dicek Process All. |
| Ritme Vira (3 contoh) | ~120 tok tapi ini yang menjaga output tidak kerasa bot. Ini justru bagian yang degradasinya paling sulit kamu ukur dari log. |
| Aturan emoji/format WhatsApp | Murah, efeknya langsung terlihat user. |
| Format & sintaks semua tag | Salah satu karakter = fitur mati. |
| Klaim "sudah booking/bayar" → `[TALK_TO_ADMIN]` | Nilai bisnis tinggi, mencegah menjual ke lead yang sudah dipegang tim. |
| Aturan klaim "sudah survey" | Baru ditambahkan, jelas hasil temuan lapangan. |

### Satu penambahan (bukan pemangkasan)

Di `# TAG`, ditambahkan:

> "Kalau kamu menjanjikan foto DAN video, pasang DUA tag terpisah. Jangan menjanjikan media yang tidak kamu pasang tagnya."

Dari transkrip tes 20 Juli: Vira menulis *"foto dan video tipe 36/72 nya saya kirimkan"* tapi hanya memasang satu tag, dan user cuma menerima foto. Bug kecil, tapi user merasa dijanjikan sesuatu yang tidak datang.

---

## 4. Patch `data_context` kondisional

File hasil: **`2026-07-20-patch-FAQ-Retrieve-data-context-kondisional.js`**

Kolom PRODUK dibagi tiga ember:

- **CORE** (selalu): Tipe Unit, Kategori, Harga Normal, Status Stok
- **MONEY** (saat `askingPrice || askingKPR || wantsSurvey || discussingUnit`): Harga Promo, Batas Tanggal Promo, Booking Fee/DP, Skema Cicilan, Bank/Skema KPR, Promo Berlaku
- **SPEK** (saat `discussingUnit || askingFasilitas || askingLegalitas`): Luas, Dimensi, Kamar Tidur/Mandi, Spesifikasi Lain
- **DROP** (tidak pernah): No, Catatan, Last Update

Blok LINKS: nama key + Tipe + Tipe Unit selalu dikirim (AI harus tahu katalognya); Keyword dan Deskripsi hanya saat `wantsMedia`.

**Robustness dijaga:** kolom yang tidak dikenal masuk ember SPEK, bukan dibuang. Jadi kalau sheet PRODUK nambah kolom baru, kolom itu tetap sampai ke AI saat user memang sedang membahas unit — tidak ada data yang hilang diam-diam.

| Skenario turn | Lama | Baru | Hemat |
|---|---|---|---|
| Dingin (sapaan/basa-basi) | 1.698 | 341 | −1.357 |
| Minta media saja | 1.698 | 585 | −1.113 |
| Tanya harga/KPR | 1.698 | 1.140 | −558 |
| Bahas unit (semua flag) | 1.698 | 1.662 | −36 |

Diuji terhadap transkrip 20 Juli (7 giliran nyata): rata-rata **714 tok**, hemat ~**984 tok/giliran**.

---

## 5. Hasil gabungan

| | Sebelum | Sesudah |
|---|---|---|
| `systemMessage` | 7.464 | 5.209 |
| `data_context` (rata-rata riil) | 1.698 | 714 |
| Sisanya (faq + input + memory) | 1.900 | 1.900 |
| **Total input / giliran** | **11.062** | **7.823** (−29%) |
| Biaya Sonnet / giliran | $0,036 | **$0,026** |
| Biaya Haiku / giliran | $0,012 | **$0,009** |
| Per lead (20 giliran, Sonnet) | Rp13.100 | **Rp9.500** |
| Per 100 lead/bulan (Sonnet) | Rp1.310.000 | **Rp950.000** |

Ini membawa PCR ke ~7.800 token/giliran, praktis setara V4 thescholars (~6.900) — selisih sisanya wajar karena domain properti memang butuh lebih banyak angka (harga, cicilan 4 tenor, DP, promo) dibanding domain edukasi.

---

## 6. Catatan deploy

1. **Trim ini berbasis V1.2 live, bukan `2026-07-19-systemprompt-V1.3-draft.md`.** Sudah dicek: V1.3 draft hanya berbeda 4 kalimat dari V1.2 — menghapus marker `🚧`/`🔶`, mengubah jam survey jadi "setiap hari jam 9-16", dan menyederhanakan `[TALK_TO_ADMIN]` (menghilangkan klausa "sudah booking"). Klausa "sudah booking" itu justru aturan yang lebih baru dan lebih baik, jadi **versi trimmed mempertahankannya**. Yang perlu kamu putuskan sendiri: jam operasional survey — trimmed merujuk ke `JAM_OPERASIONAL_SURVEY` dari CONFIG, jadi tidak ada angka hardcoded lagi.

2. **Patch `FAQ Retrieve` mengganti dua blok**, bukan seluruh node. Blok retrieval FAQ lexical (TF-IDF, stemming, sinonim) tidak disentuh sama sekali.

3. **Verifikasi setelah deploy** — cek di Google Sheet tab UNKNOWN apakah ada lonjakan `[UNKNOWN]` untuk pertanyaan yang seharusnya terjawab. Kalau ada, kemungkinan besar satu kolom PRODUK salah ember; tinggal pindahkan ke CORE.
