# 🌕 LUNA — AI Assistant for myBCA
**Learning, Understanding, Navigating, Assisting**

> LUNA adalah AI assistant yang tertanam langsung di dalam aplikasi myBCA, dirancang untuk membantu nasabah mengakses seluruh fitur dan layanan BCA secara cerdas, personal, dan efisien — cukup dengan satu perintah.

---

## 📋 Daftar Isi
1. [Gambaran Umum](#gambaran-umum)
2. [Fitur Utama](#fitur-utama)
3. [Sistem Tier](#sistem-tier)
4. [Tabel Benefit](#tabel-benefit)
5. [UI & UX Guidelines](#ui--ux-guidelines)
6. [Alur Penggunaan](#alur-penggunaan)
7. [Catatan Teknis](#catatan-teknis)
8. [Roadmap Pengembangan](#roadmap-pengembangan)
   - [Phase 2 — Personalisasi & Engagement](#phase-2--personalisasi--engagement)
   - [Phase 3 — CASA Growth & Wealth](#phase-3--casa-growth--wealth)
   - [Phase 4 — Monetisasi Ekosistem](#phase-4--monetisasi-ekosistem)
   - [Phase 5 — Ekspansi Touchpoint](#phase-5--ekspansi-touchpoint)
   - [Phase 6 — Trust & Keamanan Lanjutan](#phase-6--trust--keamanan-lanjutan)
9. [Impact Matrix](#impact-matrix)

---

## Gambaran Umum

LUNA adalah embedded AI assistant di aplikasi myBCA yang berperan sebagai asisten perbankan pribadi. LUNA mampu memahami kebutuhan nasabah, memberikan rekomendasi layanan, mengotomasi transaksi, dan menjawab pertanyaan seputar layanan BCA — semua dalam satu antarmuka percakapan yang intuitif.

**Filosofi Desain:**
- *Proaktif* — LUNA menyarankan sebelum nasabah perlu bertanya
- *Aman* — Semua transaksi tetap memerlukan konfirmasi PIN dari nasabah
- *Personal* — Rekomendasi disesuaikan dengan profil dan kebiasaan nasabah
- *Inklusif* — Tersedia untuk semua nasabah dengan level akses berbeda berdasarkan tier

---

## Fitur Utama

### 1. 🤖 AI Embedded di myBCA
LUNA terintegrasi langsung di dalam aplikasi myBCA tanpa perlu berpindah ke aplikasi lain. Nasabah dapat mengakses LUNA kapan saja melalui floating button berbentuk bulan purnama (🌕) yang selalu tersedia di layar.

---

### 2. 💡 Rekomendasi & Navigasi Fitur myBCA
- LUNA mampu **menyarankan seluruh fitur dan layanan** yang tersedia di myBCA berdasarkan konteks percakapan dan kebiasaan penggunaan nasabah.
- LUNA dapat **mengotomasi navigasi** sehingga nasabah tidak perlu mencari menu secara manual — cukup sampaikan kebutuhan, LUNA yang membawa nasabah ke sana.
- Setelah LUNA menyiapkan transaksi/fitur, **nasabah hanya perlu memasukkan PIN** untuk mengeksekusi.

**Contoh perintah:**
```
"LUNA, saya mau upgrade kartu kredit saya"
"LUNA, aktifkan fitur tarik tunai tanpa kartu"
"LUNA, cek promo cashback bulan ini"
```

---

### 3. 🛍️ Rekomendasi Layanan & Lifestyle
LUNA dapat merekomendasikan dan memfasilitasi:
- **Pesan makanan** — Integrasi dengan merchant rekanan BCA
- **Bayar tagihan** — Listrik, air, internet, BPJS, dan lainnya
- **Pembelian produk & voucher** — Melalui ekosistem BCA
- **Rekomendasi investasi** — Reksa dana, deposito, atau produk BCA Sekuritas
- **Promo & penawaran** — Disesuaikan dengan profil spending nasabah

---

### 4. 📦 Bulk Transaction (Terjadwal & Non-Terjadwal)
Fitur unggulan untuk efisiensi transaksi bervolume tinggi:

- Nasabah dapat **menyiapkan banyak transaksi sekaligus** dalam satu sesi percakapan dengan LUNA.
- Transaksi dapat diatur sebagai:
  - **Non-terjadwal** → Eksekusi langsung setelah konfirmasi PIN
  - **Terjadwal** → Dieksekusi pada tanggal/waktu yang ditentukan nasabah
- LUNA menampilkan **ringkasan seluruh transaksi** sebelum konfirmasi.
- **Satu PIN** untuk mengeksekusi semua transaksi dalam batch tersebut.

**Contoh skenario:**
```
"LUNA, transfer 1jt ke Budi, 500rb ke Ani, dan bayar tagihan Telkom bulan ini.
Semuanya jadwalkan setiap tanggal 25."
```

---

### 5. 🎧 Integrasi Halo BCA
LUNA dapat menjawab pertanyaan layanan pelanggan setara agen Halo BCA:

| Kondisi Nasabah | Kemampuan LUNA |
|---|---|
| **Belum login** | Menjawab pertanyaan umum, informasi produk, lokasi cabang/ATM |
| **Sudah login** | Menjawab pertanyaan spesifik akun, status transaksi, mutasi rekening |
| **Perlu eskalasi** | Membuat **tiket pelaporan** otomatis (seperti fungsi agen Halo BCA) |

LUNA akan secara cerdas mendeteksi situasi dan menentukan kapan perlu membuat tiket pelaporan.

---

### 6. 🎙️ Voice Assistant
- Nasabah dapat berinteraksi dengan LUNA menggunakan **suara** (speech-to-text dan text-to-speech).
- Mendukung Bahasa Indonesia dan intonasi percakapan alami.
- Ideal digunakan saat berkendara atau beraktivitas — hands-free banking.
- LUNA merespons dengan suara yang dapat dikonfigurasi (volume, kecepatan).

---

### 7. 🌙 Dark Mode Eksklusif saat LUNA Aktif
- Saat LUNA diaktifkan, antarmuka myBCA **otomatis beralih ke Dark Mode**.
- Memberikan pengalaman visual yang berbeda dan premium saat berinteraksi dengan AI.
- Dapat dikustomisasi oleh nasabah di pengaturan LUNA.

---

### 8. 🌕 Floating Button — Ikon Bulan Purnama
- LUNA diakses melalui **floating button berbentuk bulan purnama** yang selalu tampil di atas layar myBCA.
- Desain yang ikonik dan mudah dikenali, konsisten dengan nama LUNA.
- Animasi halus saat disentuh (glowing/pulse effect).
- Posisi dapat disesuaikan (kiri/kanan layar).

---

## Sistem Tier

Akses dan kapabilitas LUNA ditentukan oleh **penempatan dana nasabah (CASA)** di BCA. Semakin besar penempatan dana, semakin tinggi tier dan semakin lengkap fitur yang tersedia.

### Struktur Tier

| Tier | Nama | Penempatan Dana (CASA) |
|------|------|------------------------|
| 🥇 | **LUNA Prioritas** | ≥ Rp 500 juta |
| 🥈 | **LUNA Premium** | Rp 50 juta – < Rp 500 juta |
| 🥉 | **LUNA Economy** | Rp 5 juta – < Rp 50 juta |
| ⚪ | **LUNA Basic** | < Rp 5 juta (akses gratis terbatas) |

> **Catatan:** Jika penempatan dana nasabah turun di bawah threshold tier aktif, LUNA akan **otomatis menurunkan tier** pada periode evaluasi berikutnya (bulanan).

---

## Tabel Benefit

### 📊 Benefit untuk Nasabah per Tier

| Fitur / Benefit | Basic ⚪ | Economy 🥉 | Premium 🥈 | Prioritas 🥇 |
|---|:---:|:---:|:---:|:---:|
| Akses LUNA (chat dasar) | ✅ Terbatas | ✅ | ✅ | ✅ |
| Rekomendasi fitur myBCA | ✅ Terbatas | ✅ | ✅ | ✅ |
| Bayar tagihan via LUNA | ❌ | ✅ | ✅ | ✅ |
| Pesan makanan & lifestyle | ❌ | ✅ | ✅ | ✅ |
| Bulk Transaction | ❌ | ✅ (maks 5) | ✅ (maks 20) | ✅ (unlimited) |
| Scheduled Transaction | ❌ | ✅ | ✅ | ✅ |
| Voice Assistant | ❌ | ❌ | ✅ | ✅ |
| Integrasi Halo BCA (tiket) | ❌ | ✅ | ✅ | ✅ |
| Dark Mode eksklusif | ✅ | ✅ | ✅ | ✅ |
| Jumlah token AI per bulan | 10.000 | 50.000 | 200.000 | Unlimited |
| Rekomendasi investasi personal | ❌ | ❌ | ✅ | ✅ |
| Analisis spending & insight | ❌ | ❌ | ✅ | ✅ |
| **Akses Lounge BCA** | ❌ | ❌ | ✅ (2x/bln) | ✅ (Unlimited) |
| **Free WiFi di Cabang BCA** | ❌ | ✅ | ✅ | ✅ |
| Prioritas antrian di cabang | ❌ | ❌ | ✅ | ✅ |
| Dedicated concierge AI | ❌ | ❌ | ❌ | ✅ |
| Early access fitur baru | ❌ | ❌ | ✅ | ✅ |

---

### 📈 Benefit untuk BCA

| Dimensi | Manfaat |
|---|---|
| **Engagement** | Meningkatkan frekuensi dan durasi penggunaan myBCA |
| **Retensi Nasabah** | Nasabah terdorong mempertahankan/meningkatkan saldo untuk naik tier |
| **AUM Growth** | Sistem tier berbasis CASA mendorong penempatan dana lebih besar |
| **Cross-selling** | LUNA merekomendasikan produk BCA yang relevan secara organik dan personal |
| **Efisiensi Operasional** | Mengurangi volume call ke Halo BCA untuk pertanyaan umum |
| **Data & Insight** | BCA mendapat insight perilaku nasabah dari pola interaksi dengan LUNA |
| **Loyalitas** | Benefit eksklusif (lounge, WiFi) menciptakan loyalitas dan differensiasi |
| **Revenue** | Token AI berbasis tier berpotensi menjadi revenue stream baru |
| **Brand Image** | Positioning BCA sebagai bank paling inovatif dan tech-forward di Indonesia |
| **Competitive Moat** | AI embedded yang terintegrasi mendalam sulit ditiru dalam jangka pendek |

---

## UI & UX Guidelines

### Floating Button
```
- Bentuk  : Lingkaran penuh (bulan purnama 🌕)
- Warna   : Gold/amber gradient saat aktif, abu-abu saat pasif
- Posisi  : Pojok kanan bawah (default), dapat dipindah
- Animasi : Gentle pulse saat ada notifikasi/saran proaktif
- Ukuran  : 56dp (mengikuti Material Design FAB standard)
```

### Dark Mode LUNA
```
- Background : #0D0D1A (deep navy-black)
- Accent     : #F5C842 (gold — warna BCA)
- Text       : #FFFFFF (primary), #A0A0B0 (secondary)
- Bubble AI  : #1A1A2E
- Bubble User: #F5C842 (gold)
```

### Onboarding LUNA
1. Nasabah pertama kali buka LUNA → tampil animasi bulan terbit
2. Penjelasan singkat 3 slide: *Apa itu LUNA / Cara pakai / Tier kamu*
3. Izin akses: mikrofon (voice), notifikasi (saran proaktif)
4. LUNA menyapa dengan nama nasabah dan tier aktif

---

## Alur Penggunaan

### Alur Transaksi via LUNA
```
Nasabah ketik/ucapkan perintah
        ↓
LUNA memahami intent (NLU)
        ↓
LUNA menyiapkan detail transaksi
        ↓
LUNA menampilkan ringkasan konfirmasi
        ↓
Nasabah masukkan PIN
        ↓
Transaksi dieksekusi ✅
```

### Alur Bulk Transaction
```
Nasabah menyebutkan semua transaksi dalam satu percakapan
        ↓
LUNA menyusun antrian transaksi
        ↓
LUNA menampilkan daftar + total nilai semua transaksi
        ↓
Nasabah masukkan PIN (1x untuk semua)
        ↓
Semua transaksi dieksekusi sekaligus / sesuai jadwal ✅
```

### Alur Pelaporan Halo BCA
```
Nasabah sampaikan masalah ke LUNA
        ↓
LUNA coba selesaikan mandiri (FAQ, info akun)
        ↓
Jika tidak bisa → LUNA tawarkan buat tiket pelaporan
        ↓
Nasabah konfirmasi → Tiket dibuat otomatis
        ↓
Nasabah terima nomor tiket & estimasi respons ✅
```

---

## Catatan Teknis

### Token & Model
- **Model AI**: Large Language Model dengan fine-tuning konteks perbankan BCA
- **Token limit**: Disesuaikan per tier (lihat tabel benefit)
- **Reset token**: Setiap awal bulan kalender
- **Bahasa**: Bahasa Indonesia (utama), Bahasa Inggris (opsional)

### Keamanan
- Semua transaksi **wajib konfirmasi PIN** — LUNA tidak pernah mengeksekusi transaksi tanpa persetujuan eksplisit nasabah
- Sesi LUNA mengikuti **session timeout** myBCA (15 menit tidak aktif)
- Riwayat percakapan LUNA **terenkripsi** dan tidak digunakan untuk keperluan di luar personalisasi nasabah
- Nasabah dapat **menghapus riwayat LUNA** kapan saja

### Evaluasi Tier
- Evaluasi dilakukan **setiap tanggal 1** berdasarkan rata-rata saldo CASA bulan sebelumnya
- Nasabah mendapat **notifikasi** jika tier akan berubah (H-7 sebelum evaluasi)
- Fitur yang sedang digunakan tidak langsung terganggu — ada **grace period 7 hari** setelah penurunan tier

---

---

## Roadmap Pengembangan

Fitur-fitur di bawah merupakan pengembangan lanjutan LUNA setelah peluncuran awal (v1.0). Setiap phase dirancang untuk memperdalam nilai bagi nasabah sekaligus mendorong pertumbuhan CASA dan profitabilitas BCA secara terukur.

```
v1.0 Launch → Phase 2 (Q3) → Phase 3 (Q1 tahun+1) → Phase 4 (Q3 tahun+1) → Phase 5 & 6 (tahun+2)
```

---

### Phase 2 — Personalisasi & Engagement
> **Target:** Meningkatkan retention dan daily active usage LUNA
> **Estimasi timeline:** 3–6 bulan pasca launch

#### 2.1 🧠 LUNA Financial Coach
LUNA berperan sebagai pelatih keuangan pribadi yang memantau dan menganalisis pola keuangan nasabah secara aktif.

**Fitur detail:**
- **Weekly Spending Digest** — Setiap Senin pagi, LUNA kirim ringkasan pengeluaran minggu lalu dengan breakdown kategori (F&B, transportasi, belanja, tagihan)
- **Anomaly Alert** — LUNA mendeteksi lonjakan spending yang tidak biasa dan proaktif memberitahu nasabah: *"Bulan ini pengeluaran F&B kamu 40% di atas rata-rata. Mau lihat detailnya?"*
- **Budget Planner** — Nasabah bisa set budget per kategori, LUNA memantau dan mengingatkan saat mendekati/melewati batas
- **Monthly Financial Report** — Laporan bulanan otomatis berisi income vs expense, net saving rate, dan rekomendasi perbaikan

**Tersedia untuk:** Economy, Premium, Prioritas
**Impact nasabah:** Kesadaran finansial meningkat, kepercayaan pada BCA sebagai mitra keuangan menguat
**Impact BCA:** Engagement harian naik, nasabah lebih sadar pentingnya menabung di BCA

---

#### 2.2 🎯 Life Event Detection
LUNA mendeteksi perubahan pola transaksi yang mengindikasikan momen penting dalam kehidupan nasabah, lalu menawarkan produk yang relevan *pada waktu yang tepat*.

**Sinyal yang dideteksi:**
| Pola Transaksi | Life Event Terdeteksi | Produk yang Ditawarkan |
|---|---|---|
| Pembelian cincin/toko perhiasan | Akan menikah | Tabungan bersama, KPR |
| Transaksi rumah sakit bersalin | Memiliki anak baru | Tabungan pendidikan, asuransi jiwa |
| Pembelian perlengkapan bayi berulang | Bayi baru lahir | BCA Insurance, deposito jangka panjang |
| Transfer besar ke developer properti | Membeli rumah/apartemen | KPR Top-up, asuransi properti |
| Pembelian perlengkapan kantor/domain | Memulai bisnis | myBCA Bisnis, fasilitas pinjaman UKM |
| Pengeluaran travel internasional naik | Mobilitas tinggi | Kartu kredit travel, BCA Dollar |

**Mekanisme:** LUNA tidak langsung menawarkan produk secara agresif. Pendekatan: *"Kelihatannya kamu sedang mempersiapkan sesuatu yang spesial — ada yang bisa LUNA bantu rencanakan?"*

**Tersedia untuk:** Premium, Prioritas
**Impact BCA:** Cross-sell yang tepat sasaran dan tepat waktu — konversi jauh lebih tinggi dari kampanye massal

---

#### 2.3 🏆 LUNA Savings Challenge
Gamifikasi menabung untuk mendorong nasabah mempertahankan dan menaikkan saldo CASA secara sukarela dan menyenangkan.

**Mekanisme:**
- LUNA tawarkan challenge menabung mingguan/bulanan dengan target yang dipersonalisasi berdasarkan kemampuan nasabah
- **Progress bar visual** yang muncul di floating button LUNA saat challenge aktif
- **Streak system** — Konsisten menabung selama X minggu berturut-turut dapat reward (poin BCA, cashback, atau upgrade tier temporary)
- **Social leaderboard** opsional — Nasabah bisa bandingkan pencapaian dengan teman yang juga pakai LUNA (dengan izin)
- **Challenge Templates:**
  - *52-Week Challenge* — Nabung kelipatan Rp 10.000 setiap minggu (minggu 1: Rp 10rb, minggu 52: Rp 520rb)
  - *Ramadan Challenge* — Nabung Rp 50.000/hari selama 30 hari Ramadan
  - *Liburan Challenge* — Set target dana liburan, LUNA bantu hitung dan monitor

**Tersedia untuk:** Semua tier
**Impact BCA:** Saldo CASA rata-rata nasabah naik, churn rate turun karena nasabah punya "tujuan" di BCA

---

### Phase 3 — CASA Growth & Wealth
> **Target:** Mendorong pertumbuhan AUM dan dana kelola BCA secara signifikan
> **Estimasi timeline:** 9–12 bulan pasca launch

#### 3.1 💸 Smart Sweep
Fitur otomasi pengelolaan dana idle yang memaksimalkan imbal hasil nasabah sekaligus menaikkan AUM BCA.

**Cara kerja:**
1. Nasabah set **threshold saldo minimum** yang ingin dipertahankan di rekening (misal: Rp 5 juta)
2. LUNA memantau saldo secara real-time
3. Saat saldo melebihi threshold, LUNA **otomatis menyarankan** (atau jika diizinkan, langsung memindahkan) kelebihan dana ke instrumen pilihan:
   - Deposito BCA (imbal hasil tertinggi)
   - Reksa dana pasar uang BCA
   - Tabungan Maxi BCA (bunga lebih tinggi)
4. Saat saldo turun di bawah threshold, LUNA **otomatis tarik kembali** dari instrumen tersebut

**Mode operasi:**
- **Advisory Mode** — LUNA sarankan, nasabah eksekusi dengan PIN
- **Auto Mode** *(Premium & Prioritas)* — LUNA eksekusi otomatis sesuai instruksi awal yang sudah dikonfirmasi nasabah

**Contoh notifikasi LUNA:**
> *"Saldo kamu sudah Rp 23 juta di atas threshold selama 7 hari. Mau LUNA pindahkan Rp 20 juta ke deposito 30 hari dengan bunga 4,5%/tahun? Kamu bisa dapat sekitar Rp 74.000 dalam sebulan."*

**Tersedia untuk:** Economy (Advisory), Premium & Prioritas (Auto Mode)
**Impact BCA:** Dana yang sebelumnya idle di tabungan biasa bermigrasi ke produk berbunga — meningkatkan fee income dan AUM

---

#### 3.2 📈 Auto-Invest
Instruksi investasi otomatis yang dijalankan LUNA secara berkala tanpa perlu aksi manual dari nasabah.

**Fitur detail:**
- Nasabah set instruksi **sekali saja**: produk, jumlah, frekuensi, dan sumber dana
- LUNA eksekusi secara otomatis sesuai jadwal yang ditetapkan
- Rekonfirmasi PIN hanya saat pertama kali setup instruksi (bukan setiap eksekusi)
- Nasabah bisa pause/stop kapan saja via perintah ke LUNA

**Contoh instruksi:**
```
"LUNA, investasikan Rp 500.000 ke reksa dana pasar uang BCA
setiap tanggal gajian (tanggal 25) mulai bulan depan."

"LUNA, beli emas digital BCA sebesar Rp 1 juta setiap minggu
setiap hari Senin pagi."
```

**Dashboard Auto-Invest:**
- Total yang sudah diinvestasikan (kumulatif)
- Pertumbuhan portofolio vs modal
- Jadwal investasi berikutnya
- Estimasi nilai portofolio di masa depan (proyeksi sederhana)

**Tersedia untuk:** Premium, Prioritas
**Impact BCA:** AUM reksa dana dan produk investasi naik konsisten, fee management meningkat

---

#### 3.3 📣 Tier Nudging — Smart Upgrade Prompt
Sistem notifikasi cerdas yang mendorong nasabah untuk naik tier secara organik dan tidak terasa memaksa.

**Mekanisme:**
- LUNA memantau saldo rata-rata nasabah secara pasif
- Saat nasabah berada dalam **15% jarak dari threshold tier berikutnya**, LUNA mulai memberikan nudge bertahap

**Jenis nudge:**
| Jarak ke Threshold | Tipe Nudge | Contoh Pesan LUNA |
|---|---|---|
| 15% dari threshold | Informasional | *"Tahukah kamu? Nasabah LUNA Premium bisa akses lounge BCA di 50+ kota."* |
| 10% dari threshold | Komparatif | *"Kamu hampir Premium! Selisihnya tinggal Rp 4,2 juta dari tier yang bisa akses voice assistant dan analisis investasi personal."* |
| 5% dari threshold | Action-oriented | *"Tambah Rp 1,8 juta ke rekening BCA kamu bulan ini dan LUNA akan upgrade kamu ke tier Premium — gratis bulan pertama!"* |

**Anti-spam rule:** Nudge maksimal 1x per minggu, dapat dimatikan oleh nasabah kapan saja.

**Tersedia untuk:** Semua tier (mendorong ke tier di atasnya)
**Impact BCA:** Pertumbuhan CASA organik yang berkelanjutan tanpa biaya akuisisi tambahan

---

### Phase 4 — Monetisasi Ekosistem
> **Target:** Membuka revenue stream baru berbasis data dan ekosistem merchant BCA
> **Estimasi timeline:** 15–18 bulan pasca launch

#### 4.1 🛒 LUNA Merchant Intelligence
Platform rekomendasi merchant yang dipersonalisasi — menguntungkan nasabah, merchant, dan BCA sekaligus.

**Cara kerja:**
- BCA memiliki data transaksi merchant yang sangat kaya dari jutaan nasabah
- LUNA menganalisis **histori spending individual** untuk merekomendasikan promo yang *benar-benar relevan*
- Merchant rekanan BCA dapat membeli **slot rekomendasi bertarget** di dalam LUNA

**Diferensiasi dari promo biasa:**
```
❌ Cara lama : "Promo diskon 20% di semua restoran rekanan BCA" → tidak relevan untuk semua
✅ LUNA way  : "Kamu biasa makan siang di area SCBD. Ada promo 30% di Sushi Tei Grand Hyatt 
               sampai Jumat ini — mau LUNA pesan sekarang?" → personal, timely, actionable
```

**Model bisnis untuk BCA:**
- Merchant bayar **Cost Per Recommendation (CPR)** — biaya per rekomendasi yang ditampilkan LUNA
- Merchant bayar **Cost Per Transaction (CPT)** — biaya per transaksi yang terjadi dari rekomendasi LUNA
- Data insight agregat (anonim) tentang perilaku spending segmen nasabah dijual ke merchant sebagai **market intelligence**

**Safeguard nasabah:**
- Maksimal 2 rekomendasi merchant per hari per nasabah
- Nasabah dapat opt-out dari rekomendasi merchant kapan saja
- LUNA selalu transparan: *"Ini adalah rekomendasi dari merchant rekanan BCA"*

**Impact BCA:** Revenue non-bunga baru yang signifikan, merchant makin loyal ke ekosistem BCA

---

#### 4.2 🔒 LUNA Fraud Shield
Sistem perlindungan transaksi berbasis AI yang mendeteksi dan mencegah fraud secara real-time.

**Cara kerja:**
- LUNA mempelajari **pola transaksi normal** setiap nasabah (waktu, lokasi, nominal, merchant)
- Saat ada transaksi yang menyimpang dari pola, LUNA **langsung intervensi** sebelum transaksi dieksekusi
- Verifikasi tambahan diterapkan secara adaptif berdasarkan skor risiko transaksi

**Contoh skenario:**
```
Nasabah biasa transfer maks Rp 5 juta, tiba-tiba ada perintah transfer Rp 50 juta ke rekening baru.

LUNA: "Hei, ini terlihat berbeda dari biasanya. Transfer Rp 50 juta ke [nama penerima] 
ini memang kamu yang minta? Kalau iya, ketik 'YA' dan masukkan PIN. 
Kalau tidak, LUNA akan blokir dan buat laporan keamanan sekarang."
```

**Fitur Fraud Shield:**
- **Real-time anomaly detection** pada setiap transaksi
- **Trusted device management** — LUNA tahu perangkat mana yang biasa dipakai nasabah
- **Location-based alert** — Transaksi dari lokasi tidak biasa langsung di-flag
- **Social engineering detection** — LUNA mendeteksi pola percakapan yang mengindikasikan nasabah sedang dimanipulasi (misal: transfer terburu-buru dengan alasan darurat)
- **Emergency freeze** — Nasabah bisa bilang *"LUNA, bekukan akun saya sekarang"* dan semua transaksi langsung diblokir sementara

**Model bisnis:** Fraud Shield dapat dijadikan fitur **premium add-on** berbayar (Rp 10.000–20.000/bulan) atau bundled eksklusif untuk tier Prioritas.

**Impact BCA:** Penurunan kerugian fraud, peningkatan kepercayaan nasabah, potensial revenue dari subscription

---

#### 4.3 📜 LUNA Digital Will (Warisan Digital)
Fitur eksklusif tier Prioritas untuk perencanaan aset dan instruksi darurat yang menciptakan loyalitas jangka panjang.

**Fitur detail:**
- **Instruksi darurat** — Nasabah bisa mendaftarkan ahli waris dan instruksi jika terjadi kondisi darurat (pembekuan rekening, kontak yang dihubungi, rekening yang diprioritaskan)
- **Trusted contact** — Satu orang terpercaya yang dapat dihubungi LUNA dalam situasi darurat atas permintaan nasabah
- **Asset summary** — LUNA menyusun ringkasan semua aset finansial di BCA (tabungan, deposito, reksa dana, kartu kredit) dalam satu dokumen terenkripsi yang bisa diakses oleh ahli waris terdaftar
- **Renewal reminder** — LUNA mengingatkan nasabah untuk memperbarui instruksi secara berkala

**Tersedia untuk:** Prioritas (eksklusif)
**Impact BCA:** Fitur ini menciptakan *switching cost* yang sangat tinggi — nasabah Prioritas hampir tidak akan berpindah bank jika instruksi warisan digitalnya sudah terintegrasi di BCA

---

### Phase 5 — Ekspansi Touchpoint
> **Target:** LUNA hadir di lebih banyak platform dan perangkat
> **Estimasi timeline:** 18–24 bulan pasca launch

#### 5.1 🖥️ LUNA Web (myBCA Desktop)
- LUNA hadir di versi web myBCA untuk nasabah yang lebih nyaman menggunakan laptop/komputer
- Interface yang dioptimalkan untuk layar besar: sidebar percakapan + panel utama myBCA aktif secara bersamaan
- Bulk transaction lebih mudah dilakukan via keyboard (upload CSV daftar penerima transfer)

#### 5.2 ⌚ LUNA Watch (Wearable Integration)
- Notifikasi cerdas dari LUNA muncul langsung di smartwatch
- Perintah suara singkat via smartwatch: *"Hey LUNA, saldo berapa?"* atau *"Bayar tagihan listrik"*
- Kompatibel dengan Apple Watch dan Galaxy Watch
- Ideal untuk nasabah dengan mobilitas tinggi

#### 5.3 🔔 LUNA Proactive Push — Smart Notifications
Sistem notifikasi proaktif yang kontekstual dan tepat waktu, bukan sekadar promosi.

**Contoh notifikasi LUNA yang cerdas:**
```
📅 "Tagihan listrik PLN-mu biasanya datang sekitar tanggal ini.
    Mau LUNA cek dan bayarkan sekarang?" [Cek Sekarang]

💱 "Kurs USD/IDR hari ini Rp 15.450 — terendah dalam 3 bulan.
    Mau beli valas sekarang?" [Beli via LUNA]

🎂 "Besok ulang tahun Budi (simpanan kontak kamu). Mau kirim
    hadiah saldo atau transfer sebagai kado?" [Kirim Sekarang]

⚡ "Saldo rekeningmu tinggal Rp 850.000. Mau LUNA pindahkan
    sebagian dari deposito yang jatuh tempo minggu ini?" [Pindahkan]
```

**Ketentuan:** Maksimal 3 notifikasi proaktif per hari, dapat dikustomisasi jenis dan waktunya oleh nasabah.

---

### Phase 6 — Trust & Keamanan Lanjutan
> **Target:** Memperkuat posisi LUNA sebagai asisten perbankan paling terpercaya di Indonesia
> **Estimasi timeline:** 24+ bulan pasca launch

#### 6.1 🧬 Biometric Behavioral Authentication
- LUNA mempelajari **pola perilaku unik** nasabah: kecepatan mengetik, pola scrolling, ritme interaksi
- Jika pola berbeda signifikan dari biasanya, LUNA menerapkan verifikasi tambahan secara diam-diam
- Keamanan berlapis tanpa mengganggu pengalaman nasabah yang normal

#### 6.2 🌍 LUNA Multilingual
- Ekspansi dukungan bahasa: Bahasa Inggris, Mandarin, Jawa, Sunda (untuk jangkauan nasabah lebih luas)
- Berguna untuk nasabah asing (WNA) dan segmen senior yang lebih nyaman dengan bahasa daerah

#### 6.3 🤝 LUNA Family Link
- Satu akun LUNA dapat dihubungkan dengan anggota keluarga (spouse, orang tua, anak)
- Orang tua bisa pantau pengeluaran anak via LUNA (dengan persetujuan anak)
- Transfer antar anggota Family Link lebih cepat dan dengan limit khusus
- Shared budget planner untuk keluarga

---

## Impact Matrix

Matriks di bawah merangkum proyeksi dampak setiap phase terhadap metrik bisnis utama BCA.

| Phase | Inisiatif Utama | Impact CASA | Impact Revenue Non-Bunga | Impact Engagement | Kompleksitas | Prioritas |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Phase 2** | Financial Coach | 🔥🔥 | 🔥 | 🔥🔥🔥 | Medium | ⭐⭐⭐⭐⭐ |
| **Phase 2** | Life Event Detection | 🔥🔥 | 🔥🔥🔥 | 🔥🔥 | Tinggi | ⭐⭐⭐⭐⭐ |
| **Phase 2** | Savings Challenge | 🔥🔥🔥 | 🔥 | 🔥🔥🔥 | Rendah | ⭐⭐⭐⭐⭐ |
| **Phase 3** | Smart Sweep | 🔥🔥🔥 | 🔥🔥 | 🔥🔥 | Medium | ⭐⭐⭐⭐⭐ |
| **Phase 3** | Auto-Invest | 🔥🔥 | 🔥🔥🔥 | 🔥🔥 | Medium | ⭐⭐⭐⭐ |
| **Phase 3** | Tier Nudging | 🔥🔥🔥 | 🔥 | 🔥 | Rendah | ⭐⭐⭐⭐⭐ |
| **Phase 4** | Merchant Intelligence | 🔥 | 🔥🔥🔥 | 🔥🔥 | Tinggi | ⭐⭐⭐⭐ |
| **Phase 4** | Fraud Shield | 🔥 | 🔥🔥 | 🔥🔥 | Tinggi | ⭐⭐⭐⭐ |
| **Phase 4** | Digital Will | 🔥🔥 | 🔥 | 🔥 | Medium | ⭐⭐⭐ |
| **Phase 5** | Smart Notifications | 🔥🔥 | 🔥🔥 | 🔥🔥🔥 | Medium | ⭐⭐⭐⭐ |
| **Phase 5** | LUNA Web | 🔥 | 🔥 | 🔥🔥 | Rendah | ⭐⭐⭐ |
| **Phase 5** | LUNA Watch | 🔥 | 🔥 | 🔥🔥 | Tinggi | ⭐⭐⭐ |
| **Phase 6** | Family Link | 🔥🔥 | 🔥🔥 | 🔥🔥🔥 | Tinggi | ⭐⭐⭐ |
| **Phase 6** | Multilingual | 🔥 | 🔥 | 🔥🔥 | Medium | ⭐⭐ |

### Quick Wins yang Direkomendasikan untuk Dikerjakan Lebih Awal

Tiga inisiatif dengan effort rendah namun dampak CASA langsung tinggi yang sebaiknya diprioritaskan bersamaan dengan atau segera setelah launch v1.0:

1. **Tier Nudging** — Effort paling rendah, dampak CASA terasa dalam 1–2 bulan pertama
2. **Savings Challenge** — Engagement tinggi, viral potential, mendorong saldo CASA naik organik
3. **Smart Sweep** — Monetisasi dana idle yang selama ini tidak teroptimalkan, meningkatkan AUM dengan effort nasabah minimal

---

*Dokumen ini merupakan spesifikasi produk LUNA v1.1 (termasuk roadmap pengembangan) — bersifat internal dan dapat berubah sesuai perkembangan pengembangan.*

*Terakhir diperbarui: Juni 2026*
