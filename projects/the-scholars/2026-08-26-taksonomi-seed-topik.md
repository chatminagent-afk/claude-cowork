# Taksonomi Seed Topik — VIRA (The Scholars)

Sumber data: `archive\report-production-V4-obsolete\The_Scholars_Database.xlsx`
Tab `STATS` kolom `Pesan Pertama` (korpus utama) + tab `UNKNOWN` kolom `Pertanyaan` (pertanyaan yang tidak terjawab VIRA).
Metode: ekstraksi via Python/openpyxl, dibaca dan diklaster manual berdasarkan isi pesan asli (bukan asumsi), divalidasi dengan pencarian kata kunci menyeluruh untuk dua pertanyaan spesifik Steven (jadwal & IELTS).

---

## Ringkasan untuk Sam

- Dari 483 pesan pertama pengguna yang ada isinya, topik terbesar tetap seputar **ASEAN Scholarship** (55 orang) dan **kelayakan anak berdasarkan kelas/usia** (46 orang) — dua hal ini yang paling sering ditanyakan sejak awal kontak.
- **Dugaan soal jadwal hari tertentu ("ada kelas hari Rabu nggak") nyaris tidak muncul** — cuma 1 pertanyaan spesifik soal hari (dan itu nanya hari Sabtu, bukan Rabu). Pertanyaan soal jadwal/jam jauh lebih sering muncul di percakapan LANJUTAN (tab UNKNOWN) daripada di pesan pembuka.
- **Permintaan IELTS juga nyaris tidak ada** — cuma disebut lewat 5 pesan di seluruh data (gabungan kedua tab), dan cuma 1 yang benar-benar tanya "apakah ada mentoring IELTS/SAT". Ini bukan demand besar berdasarkan data historis.
- Yang justru paling banyak GAGAL dijawab VIRA (tab UNKNOWN) adalah **masalah teknis akses webinar/Zoom** (link invalid, minta passcode) — 28 dari 151 pertanyaan tak terjawab, jauh di atas topik lain. Ini murni masalah operasional, bukan konten, tapi paling sering bikin calon user macet.
- Ada pola besar yang perlu diperhatikan: sekitar 36 pesan pembuka cuma template klik-iklan ("Halo Sam! Saya mau tanya tentang program The Scholars Batch 4/5") tanpa isi tambahan — kemungkinan besar dari tombol WhatsApp di iklan IG/Meta, bukan pertanyaan asli. Dan 19 pesan lain cuma bilang "mau tanya" tanpa nyebut topiknya sama sekali.

---

## A. Pembersihan Korpus

**Catatan penting soal ukuran korpus:** brief awal menyebut "~664 baris" untuk `Pesan Pertama`. Angka 664 itu benar untuk kolom `No WA` (total user unik di tab STATS), tapi kolom `Pesan Pertama` sendiri hanya terisi di **483 baris** — 181 user tercatat di STATS tapi kolom "pesan pertama"-nya kosong (kemungkinan besar user yang masuk lewat jalur lain, atau field belum ke-capture). Jadi korpus riil yang dianalisis di sini adalah **483 pesan**, bukan 664.

| Kategori | Jumlah baris |
|---|---|
| Total baris `No WA` terisi (semua user tercatat) di STATS | 664 |
| Baris dengan `Pesan Pertama` terisi (korpus riil) | **483** |
| — Dikeluarkan (test/internal) | 2 |
| — Sapaan murni tanpa isi (halo/pagi/makasih/emoji saja, dll) | 99 |
| — **Substantif** (dipakai untuk taksonomi topik) | **382** |

**Baris yang dikeluarkan (2, aturan: nama pengirim adalah orang internal/QA)**
- Baris 127 — Nama "Samuel Oscar" (nama pemilik bisnis/"Sam" sendiri) — isi pesan cuma link undangan grup WhatsApp, bukan pertanyaan calon user.
- Baris 321 — Nama "Steven Leroy" — isi pesannya adalah duplikat persis dari pesan user asli di baris 315 ("selamat malam kaa izin bertanya terkait the scholars senior mentoring..."), indikasi kuat ini adalah tes manual terhadap bot, bukan calon user sungguhan.

**Sapaan murni (99 baris)** — pesan yang isinya cuma satu kata/frasa sapaan atau penutup tanpa konten apa pun setelah dibersihkan dari tanda baca/emoji: "Halo", "Hi", "Pagi", "Selamat siang", "Assalamualaikum", "Terimakasih", "🙏", "Ok", "Tc", dll. Daftar lengkap sudah diverifikasi manual satu per satu.

**Catatan tambahan (bukan pengurangan angka di atas, tapi transparansi):** dari 382 pesan "substantif", ada 37 baris yang secara teknis mengandung lebih dari satu kata tapi **tidak membawa topik bisnis** — ini dijelaskan di Bagian C (long tail) karena tetap dihitung sebagai substantif sesuai instruksi, tapi tidak cocok ke topik mana pun:
- 11 varian ucapan terima kasih/penutup ("Terimakasih banyak", "Thank u kakk!", "okay ko", dll — typo/variasi yang tidak tertangkap filter sapaan murni)
- 11 sapaan + konfirmasi kontak ("Halo the scholars", "Hi The Scholars team" — cuma mengonfirmasi nomor yang benar, tanpa pertanyaan)
- 5 komunikasi operasional dari siswa yang **sudah** terdaftar (izin absen, reminder kelas dari tutor — bukan calon user baru)
- 10 fragmen percakapan lanjutan yang ke-capture sebagai "Pesan Pertama" padahal jelas potongan tengah obrolan (mis. "Bentar. 2 mingguan lagi.", "Ooh iya sbb kak, bentar ya") — ini indikasi bahwa field `Pesan Pertama` kadang menangkap pesan pertama dari SESI baru (setelah gap), bukan pesan pertama secara harfiah dari user itu.

---

## B. Klaster Topik (15 topik)

Denominator taksonomi: **382 pesan substantif**. Diurutkan dari terbesar.

### 1. `minat_asean_scholarship` — Minat ASEAN Scholarship
Menyebut eksplisit "ASEAN Scholarship"/MOE-ASEAN — minat, info, atau persiapan program ini secara umum.
**n = 55**
- [74] "Apakah ada buka kelas persiapan asean sholarship"
- [94] "Program asean scholarship untuk kelas berapa saja ya kak? Dan persiapannya bagaimana?"
- [143] "Hi, boleh tau brp biaya utk latihan interview utk asean scholarship"

### 2. `syarat_usia_kelas` — Syarat Usia/Kelas Anak
Menanyakan apakah anak di kelas/usia tertentu memenuhi syarat ikut program, tanpa program spesifik lain jadi fokus utama.
**n = 46**
- [82] "Anak sy kelas 3smp / Tlg tnya ini coaching private untuk scholar atau gmn ya? Dia ada rencana ke sgp atau ausie untuk ambil uni"
- [100] "...untuk anaknya sekarang kan akan naik ke kelas 9 untuk juli ini, jadi baiknya di apply di kelas berapa, dan untuk dom apakah nanti akan dapat?"
- [148] "Sec 3"

### 3. `program_senior_admisi_uni` — Program Senior / Admisi Universitas
Pertanyaan soal jalur "Seniors" atau bimbingan apply ke NUS/NTU/SMU/kuliah di Singapura secara umum (bukan lewat jalur ASEAN Scholarship).
**n = 43**
- [131] "Halo Sam! Saya mau tanya tentang program persiapan kuliah di NTU untuk anak saya yang bulan ini masuk kelas 11"
- [150] "hai kaa mau tanya, aku sedang mencari bimbingan untuk kuliah di smu apakah dengan the scholars bisa?"
- [261] "Halo kak, aku mau nanya tentang program the scholars seniors"

### 4. `minat_program_batch_generik` — Minat Batch (Generik)
Pesan template/klik-iklan "Halo Sam! Saya mau tanya tentang program The Scholars Batch X" atau ekspresi minat umum ke sebuah batch tanpa rincian lain. Pola berulang identik (~20+ kali persis sama) — sangat mungkin ini pesan otomatis dari tombol WhatsApp di iklan Instagram/Meta, bukan pertanyaan yang diketik manual.
**n = 36**
- [68] "Halo Sam! Saya mau tanya tentang program The Scholars Batch 5 kapan dibuka?"
- [95] "Halo Sam! Saya mau tanya tentang program The Scholars Batch 4"
- [289] "Sy tertarik dengan the scholar bach 5"

### 5. `beasiswa_umum_luar_negeri` — Beasiswa Umum ke Luar Negeri
Menyebut "beasiswa"/"scholarship" secara umum tanpa nama program spesifik (ASEAN/UOB/CLI).
**n = 29**
- [73] "kira2 ada kesempatan u mencoba beasiswa apa"
- [93] "Mau tanya ttg scholarship , apakah ada preparation utk ke uni hongkong?"
- [119] "Siang mau tanya the scholars ini ngebantu anak buat dapt beasiswa keluar negri nga ya?"

### 6. `tanya_tanpa_topik_spesifik` — Tanya Tanpa Topik Spesifik
Menyatakan niat bertanya/minta info tapi TIDAK menyebutkan topik apa pun. Topik sebenarnya kemungkinan besar ada di pesan berikutnya yang tidak tertangkap kolom `Pesan Pertama`.
**n = 19**
- [105] "Mau minta info ttg The Scholars...🙏"
- [207] "Apa ada?"
- [250] "Halo kk saya mau tanya"

### 7. `status_pendaftaran_dan_ketersediaan` — Status Pendaftaran & Ketersediaan
Menanyakan status pendaftaran yang sudah dilakukan (belum ada konfirmasi/balasan), cara daftar, atau apakah batch/kelas/slot masih dibuka.
**n = 17**
- [160] "Kemarin sudah daftar / bagaimana kelanjutannya?"
- [234] "cara daftar bagaimana ?"
- [298] "Malam ko Sam. Saya sedang mendaftar bimbingan utk batch 5 untuk anak saya, tapi saya tidak berhasil upload file yang diminta seperti rapor, sertifikat lomba. Mohon sarannya."

### 8. `akses_webinar_zoom` — Akses Webinar/Zoom
Masalah teknis akses webinar: link invalid, minta passcode, minta link Zoom/QR.
**n = 16**
- [460] "halo min mau daftar zoom yg free ga bisa scan QR nya ada linknya kah?"
- [465] "Halo kak.. Link untuk besok belum saya Terima di email.. Apakah bisa kirim lewat whatsapp kak?"
- [446] "Slamat malam / Kenapa qr bea siswa NTU DAN NTS di nonaktifkan / Trima kasih jawabanya"

### 9. `uob_cli_scholarship` — UOB / CLI Scholarship
Pertanyaan spesifik seputar beasiswa UOB atau CLI (jalur berbeda dari ASEAN Scholarship), termasuk mock interview terkait jalur ini.
**n = 12**
- [69] "pengen tanya apakah ada rencana untuk adain kelas karena anak saya dipanggil untuk UOB CLI scholarship"
- [78] "...I applied for UOB scholarship and yesterday I got the Invitation for selection test. I just want to ask is there any information or tips..."
- [185] "ko kelas persiapan utk UOB brp?"

### 10. `biaya_program` — Biaya Program
Menanyakan harga/biaya program secara langsung.
**n = 11**
- [104] "Berapa biaya perbulan dan brp kali pertemuan?"
- [206] "Biayanya berapa ya?"
- [245] "Selamat malam, saya tertarik dengan program-program yang diberikan. Apakah saya boleh melihat harga dan dan rincian programnya?"

### 11. `lokasi_cabang` — Lokasi/Cabang
Menanyakan alamat, kota, atau apakah kelas online/offline.
**n = 9**
- [90] "min ini ofline atau online ?"
- [140] "The scholars ini ada di kota mana saja ya?"
- [361] "Alamat di mn ni?"

### 12. `info_program_general` — Info Program (Umum)
Meminta penjelasan umum tentang program tanpa menyebut nama beasiswa spesifik.
**n = 7**
- [202] "Program bimbingan nya seperti apa, berapa lama dan harganya berapa?"
- [359] "Info program yg akan dimulai apa saja?"
- [428] "Itu programnya seperti apa ya?"

### 13. `konsultasi_langsung` — Ingin Konsultasi Langsung
Ingin bicara/telepon langsung dengan Sam, bukan lewat chat teks.
**n = 6**
- [80] "Mau ngomong sama sam"
- [555] "kalo bisa janjian telp drpd chat lebi gampang"
- [663] "Kalau saya mau konsultasi apakah bisa lewat call?"

### 14. `jadwal_kelas_waktu` — Jadwal/Waktu Kelas
Menanyakan hari, jam, atau frekuensi pertemuan kelas secara spesifik. **(Lihat jawaban detail di Bagian D.)**
**n = 5**
- [382] "Batch 5 for intermediate, jadwalnya ada yg hari sabtu apa masih available?"
- [290] "1 minggu 1x ya?"
- [564] "halo mau nanya ini 2.25 jt ini 1mgg 1x ya?"

### 15. `les_privat_lain` — Les Privat Non-ASEAN
Minta les/bimbingan di luar jalur ASEAN Scholarship: bahasa Inggris, geografi, O-Level, AEIS. **(Ini juga jawaban untuk pertanyaan IELTS — lihat Bagian D.)**
**n = 4**
- [111] "Mau tanya..Samuel ada kasi les inggris gitu gak ya?"
- [178] "Siang, saya dpt nomer ini dr Jenson. Mau tanya apa ada les untuk O level?"
- [329] "halo mau tanya disini ad les persiapan untuk AEIS ga ya?"

---

## C. Long Tail

Total yang tidak cocok ke 15 topik di atas: **67 dari 382 pesan substantif (17.5%)**, terdiri dari 4 sub-pola yang masing-masing punya 3+ anggota (jadi memenuhi syarat "kandidat topik" versi task, walau ketiganya lebih tepat disebut pola data/operasional daripada topik minat bisnis):

**1. Penutup/ucapan terima kasih (varian typo, tidak tertangkap filter sapaan murni) — 11 baris**
Contoh: [79] "Ok cool, thx u Sam", [373] "Terimakasih banyak", [605] "Thank u kakk!"
→ *Rekomendasi: masukkan ke kategori "no_topic/closing" di classifier, bukan salah satu dari 15 topik bisnis.*

**2. Sapaan + konfirmasi kontak (mengonfirmasi ini nomor The Scholars, tanpa pertanyaan) — 11 baris**
Contoh: [89] "Halo the scholars", [338] "Hello The Scholars", [525] "Hi The scholar"

**3. Fragmen percakapan lanjutan (bukan pembuka asli, potongan tengah obrolan) — 10 baris**
Contoh: [294] "Bentar. 2 mingguan lagi.", [356] "Ooh iya sbb kak, bentar ya", [322] "How did you get the list from Anderson?"
→ Ini indikasi data quality: field `Pesan Pertama` kadang menangkap pesan pertama dari SESI baru (setelah jeda lama), bukan pesan pertama harfiah dari user tersebut.

**4. Komunikasi operasional dari siswa yang SUDAH terdaftar — 5 baris**
Contoh: [117] "Another reminder that class is starting soon!! Please join the class" (ini pesan DARI tutor KE siswa, bukan pertanyaan masuk), [118] "Halo Sam, baru ingay kabarin Zoe gak bisa join hari ini karna ada competition", [307] "sorry u wont be coming yo class, im at my grandma's house right now"

**Sisanya (30 baris) benar-benar beragam/satuan** — tidak ada pola 3+ lain yang jelas. Contoh representatif:
- [130] "I just asked the contact admission whether i need to replace and translate my ijazah or not" (dokumen/ijazah)
- [383] "Kak mohon info untuk secondary tidak bisa untuk siswi berhijab ya?" (kebijakan hijab)
- [602] "Malam ko Sam, mau tny, di akhir bln sept sampai awal november kami sekeluarga rencana mau ke Jepang, itu anak sy kena 2x ga les, jadi gimana ya?" (kebijakan kelas pengganti)
- [367] pertanyaan detail kurikulum IGCSE/L1R4 spesifik

**Catatan metodologi:** banyak pesan di long tail sebenarnya bertopik sama dengan salah satu dari 15 klaster di atas, tapi memakai typo/singkatan yang tidak tertangkap aturan kata kunci (mis. "kyliah" utk "kuliah", "kls brp" utk "kelas berapa"). Ini bukti bahwa classifier produksi nanti **sebaiknya tidak murni berbasis kata kunci** — perlu toleransi typo/singkatan (embedding atau LLM-based), karena bahasa pesan asli sangat tidak baku.

---

## D. Jawaban Spesifik untuk Pertanyaan Bisnis Steven

### D.1 — Pertanyaan soal jadwal/hari spesifik ("ada kelas hari Rabu nggak")

**Di korpus utama (STATS, 483 pesan pembuka):** hanya **1 pesan** yang benar-benar menanyakan ketersediaan kelas di HARI TERTENTU:
- [382] **"Batch 5 for intermediate, jadwalnya ada yg hari sabtu apa masih available?"**

Dua pesan lain menyebut hari/waktu tapi bukan pertanyaan hari spesifik — lebih ke frekuensi atau konfirmasi slot yang sudah diberikan:
- [290] "1 minggu 1x ya?" (nanya frekuensi, bukan hari)
- [564] "halo mau nanya ini 2.25 jt ini 1mgg 1x ya?" (nanya frekuensi + harga)
- [466] "Intermediate / Minggu / 18.00 – 20.00 WIB" (kemungkinan ini user menuliskan ulang jadwal yang sudah dikasih tahu, bukan pertanyaan baru)

**Di tab UNKNOWN (151 pertanyaan yang gagal dijawab VIRA)**, pola ini justru lebih sering muncul — total **9 pesan** terkait jadwal/jam, termasuk yang paling mirip pola "ada kelas hari Rabu nggak":
- [132] **"Les nya setiap hari sabtu ya kak? Jam berapa kah?"** — ini yang paling persis mirip contoh Steven, tapi tanya hari SABTU, bukan Rabu.
- [88] "Boleh tau jadwal nya belajarnya hr apa aj ?"
- [50] "Les nya tiap hari apa / 15 anak apa sempat itu bimbingan interview"
- [137] "Sbntr sy cek ig utk jdwalnya / Sisa Minggu 6-8pm ya kak?"
- [141], [147] "Minggu jam 6-8" (dua kali, tampaknya jawaban/konfirmasi yang berulang)

**Kesimpulan:** pola pertanyaan Steven ITU BENAR ADA dalam data, tapi:
1. Jarang muncul di pesan PEMBUKA (cuma 1 dari 483) — jauh lebih sering muncul sebagai pertanyaan LANJUTAN setelah user sudah dapat info awal (makanya nyangkut di tab UNKNOWN, bukan STATS).
2. **Tidak ada satu pun** yang menyebut hari Rabu spesifik. Hari yang benar-benar disebut orang: **Sabtu** (2x) dan **Minggu** (3x, termasuk yang kemungkinan konfirmasi berulang). Kalau mau siapkan jawaban template hari spesifik, prioritaskan Sabtu & Minggu dulu, bukan Rabu.

### D.2 — Pertanyaan IELTS / persiapan tes bahasa Inggris

**Sangat minim.** Di seluruh data (STATS + UNKNOWN, 483 + 151 = 634 pesan), kata "ielts" muncul di **hanya 5 pesan**, dan TOEFL/tes bahasa Inggris lain (di luar IELTS) **tidak muncul sama sekali**.

Dari STATS (2 pesan, keduanya cuma menyebut IELTS sekilas, bukan minta kelas IELTS):
- [190] "...untuk masuk top uni di singapore seperti NUS, NTU, dan SMU bisa prepare apa aja yaa dr skrg? selain ielts dan sat karena emg lagi ambil kursus keduanyaa" — user bilang dia SUDAH ambil kursus IELTS/SAT di tempat lain, bukan minta ke The Scholars.
- [324] "...Bahasa inggris lumayan lah...wpun blm test ielts secara resmi..." — sekadar menyebut status, bukan permintaan.

Dari UNKNOWN (3 pesan, satu di antaranya benar-benar bertanya):
- [84] **"...apakah mentoring khusus ngincer asean scholarship saja? atau bs mentoring untuk test lainnya spt ielts/sat / klo boleh mau tau pricelist untuk mock interview jg dong kak"** — ini SATU-SATUNYA pertanyaan langsung "apakah kalian sediakan mentoring IELTS/SAT?" di seluruh data, dan ini gagal dijawab VIRA (masuk tab UNKNOWN).
- [46] "...Krn anaknya msh persiapan ielts dan SAT..." — konteks sampingan.
- [56] "Kalau test yang wajib diambil seperti SAT, IELTS gitu ada apa aja kah? Atau kaya ada rekomen lebih baik ambil SAT atau A level?" — nanya rekomendasi, bukan minta kelas IELTS langsung.

**Kesimpulan:** dugaan Steven soal "user sering minta coaching IELTS" **tidak terbukti dari data historis** — ini bukan demand berulang, cuma muncul sesekali dan biasanya sebagai info tambahan, bukan permintaan utama. Tidak perlu dibuatkan topik `ielts_prep` tersendiri di taksonomi; kalau muncul lagi, cukup masuk ke topik `les_privat_lain` yang sudah ada. Yang lebih relevan justru: apakah The Scholars mau menjawab pertanyaan "apakah ASEAN Scholarship prep termasuk IELTS/SAT atau nggak" — karena itu pertanyaan yang sekarang gagal dijawab bot (baris UNKNOWN [84]).

### D.3 — Top 5 topik di tab UNKNOWN (demand yang gagal dilayani VIRA)

Dari 151 baris di tab UNKNOWN, 3 dikeluarkan sebagai pesan uji/QA jelas (pertanyaan di luar topik seperti "kalo kelinci makan apa" dan "kambing makan apa?" yang muncul di tengah satu thread yang juga berisi "tapi kamu paham gak maksudku?" — pola menguji pemahaman bot, bukan pertanyaan calon user). Denominator top 5 = 151 (persentase dihitung dari total baris tab, exclude tetap ditampilkan terpisah).

| Peringkat | Topik | Jumlah | % dari 151 |
|---|---|---|---|
| 1 | **Akses webinar/Zoom** (link invalid, minta passcode, minta link ulang) | 28 | 18.5% |
| 2 | **Syarat & dokumen/nilai** (rapor, ijazah, nilai minimum, sertifikat) | 19 | 12.6% |
| 3 | **Biaya program** (rincian biaya, apa yang termasuk, cara bayar) | 12 | 7.9% |
| 4 | **Proses seleksi & kriteria** (persentase diterima, requirement, tes) | 10 | 6.6% |
| 5 | **Jadwal/waktu kelas** (hari, jam, frekuensi pertemuan) | 9 | 6.0% |

Contoh verbatim tiap peringkat:
1. [4] "kayanya salah link deh"; [85] "Untuk webinar tgl 1 Aug akan membahas tentang apa ya?"
2. [29] "untuk documents yg udah harus prepared saat waktu itu apa aja ya? biar gaada yg kurang gitu"; [38] "tidak ada batas nilai yg pasti utk langsung gugur / tapi apakah ada nilai 70 prnah lulus?"
3. [48] "mau tanyaa ini biaya 4 juta itu hanya Konsul aja atau sampai ngurusin berkas ke nus nya?"
4. [52] "Utk proses seleksi yg dibutuhkan datanya apa aja ya Sam?"
5. [132] "Les nya setiap hari sabtu ya kak? Jam berapa kah?"

**Implikasi bisnis:** masalah #1 (akses webinar/Zoom) itu murni operasional/teknis, bukan soal konten — kemungkinan bisa diselesaikan dengan perbaikan sistem link/reminder, bukan menambah pengetahuan VIRA. Tapi #2–#5 adalah gap konten nyata: VIRA belum punya jawaban siap untuk syarat dokumen detail, rincian biaya, proses seleksi, dan jadwal — ini kandidat kuat untuk ditambahkan ke FAQ/basis pengetahuan VIRA.

---

## E. Tabel Peringkat Lengkap

Denominator: **382 pesan substantif** (1 baris = 1 user, dari total 483 pesan pembuka non-kosong setelah 2 baris test/internal dikeluarkan dan 99 sapaan murni dipisahkan).

| Topik | Jumlah user | % dari substantif |
|---|---|---|
| `minat_asean_scholarship` | 55 | 14.4% |
| `syarat_usia_kelas` | 46 | 12.0% |
| `program_senior_admisi_uni` | 43 | 11.3% |
| `minat_program_batch_generik` | 36 | 9.4% |
| `beasiswa_umum_luar_negeri` | 29 | 7.6% |
| `tanya_tanpa_topik_spesifik` | 19 | 5.0% |
| `status_pendaftaran_dan_ketersediaan` | 17 | 4.5% |
| `akses_webinar_zoom` | 16 | 4.2% |
| `uob_cli_scholarship` | 12 | 3.1% |
| `biaya_program` | 11 | 2.9% |
| `lokasi_cabang` | 9 | 2.4% |
| `info_program_general` | 7 | 1.8% |
| `konsultasi_langsung` | 6 | 1.6% |
| `jadwal_kelas_waktu` | 5 | 1.3% |
| `les_privat_lain` | 4 | 1.0% |
| *(long tail — Bagian C)* | 67 | 17.5% |
| **Total** | **382** | **100%** |

---

## Catatan Metodologi Singkat

- Klasifikasi topik dilakukan dengan membaca seluruh 483 pesan secara manual, lalu memvalidasi dengan pencarian kata kunci sistematis (termasuk cek typo umum) untuk memastikan tidak ada pesan relevan yang terlewat, khususnya untuk pertanyaan jadwal dan IELTS di Bagian D.
- Semua kutipan verbatim, termasuk typo dan campuran bahasa, tidak diedit.
- Tidak ada nomor HP, nama lengkap, atau info identitas lain yang dicantumkan — baris dirujuk dengan nomor indeks saja.
- Taksonomi ini adalah SEED — dirancang untuk dipakai AI classifier melabeli pesan baru. Karena banyak variasi typo/singkatan di data asli, disarankan classifier berbasis pemahaman bahasa (LLM/embedding), bukan pure keyword-matching, supaya bisa menangkap variasi seperti yang ditemukan di Bagian C.
