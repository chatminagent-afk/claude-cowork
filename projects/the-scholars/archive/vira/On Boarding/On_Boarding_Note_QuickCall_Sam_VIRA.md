# NOTE QUICKCALL SAM - VIRA THE SCHOLARS
**Post-Payment | Ringkasan Komprehensif**

---

## 📋 FITUR-FITUR VIRA YANG SAM PERLU TAU

### 1. **Deteksi & Personalisasi Otomatis**
   - **Deteksi User Status**: VIRA otomatis tanya apakah yang chat "orang tua" atau "murid" di awal percakapan
   - **Panggilan Disesuaikan**: 
     - Orang tua → dipanggil "Om/Tante", VIRA sebut diri "saya"
     - Murid → dipanggil "kamu", tone lebih encouraging dan casual
   - **Auto-detect dari Chat**: VIRA bisa deteksi status dari kata-kata seperti "anak saya", "saya sendiri", dll

### 2. **Follow-Up Otomatis Cerdas**
   - **Trigger**: 24 jam setelah user tidak balas
   - **Auto-Reset**: Begitu user balas lagi, sistem reset dan bisa follow-up lagi nanti
   - **Max 3x Follow-Up**: Setelah 3 kali follow-up, sistem berhenti (menghindari spam)
   - **2 Tipe Follow-Up**:
     - **GForm Reminder**: Jika user sudah dapat link GForm tapi belum isi (prioritas tinggi)
     - **General Follow-Up**: Jika user sempat chat tapi tidak lanjut
   - **Jadwal**: Otomatis jalan setiap hari jam **10 pagi**
   - **Smart Skip**: User yang sudah booking atau dalam mode manual akan di-skip

### 3. **Human-in-the-Loop (HITL) - Manual Mode**
   - **Fungsi**: Sam bisa "turn off" bot kapan saja untuk handle user tertentu secara manual
   - **Cara Aktifkan**: Buka STATS sheet → cari No WA user → isi kolom `bot_mode` dengan **OFF**
   - **Cara Matikan**: Hapus isi kolom `bot_mode` (kosongkan) atau isi **ON**
   - **Efek**: Selama OFF, VIRA 100% berhenti balas user tersebut (termasuk follow-up)
   - **Use Case**: Saat diskusi pembayaran Mock Interview yang perlu negosiasi personal

### 4. **Google Form Registration Flow**
   - **Trigger**: Saat user nyatakan mau daftar Mock Interview
   - **Auto-Send**: VIRA kirim link GForm otomatis
   - **Tracking**: Sistem catat kapan GForm dikirim (kolom `gform_sent_ts`)
   - **Reminder**: Jika >24 jam belum isi, otomatis kirim GForm Reminder
   - **Stop Reminder**: Setelah Sam isi `gform_filled = Y` (lihat bagian handling manual)

### 5. **Unknown FAQ → Notif ke Sam**
   - **Kapan**: User tanya hal yang tidak ada di database manapun
   - **Aksi**: 
     - VIRA tetap jawab dengan sopan ("Wah, pertanyaan bagus! Saya cek dulu ya...")
     - Sistem kirim notif WA ke Sam
     - Pertanyaan dicatat di sheet **UNKNOWN**
   - **Tujuan**: Sam bisa update FAQ atau jawab manual

### 6. **Error → Notif ke Steven**
   - **Kapan**: Ada error teknis (API gagal, connection issue, dll)
   - **Aksi**: Sistem kirim notif WA ke Steven (628...)
   - **Sam Tidak Perlu Handle**: Ini untuk teknis backend

### 7. **Rate Limiter Anti-Spam**
   - **Fungsi**: Max 5 pesan per menit per user
   - **Tujuan**: Mencegah spam dan menjaga performa sistem
   - **Efek**: Pesan ke-6 dalam <1 menit akan di-skip (user tidak sadar)

### 8. **Multi-Database FAQ**
   - **8 Sheet Terpisah**: PROGRAM, BATCH, HARGA, SYARAT, MOCK_INTERVIEW, FAQ, LINKS, ABOUT_SAM
   - **Smart Query**: VIRA tahu kapan harus query sheet mana
   - **Akurat**: Jawaban selalu dari database, bukan "asal jawab"

### 9. **Auto-Booking ke Sheets**
   - **Sheet**: MOCK_INTERVIEW_BOOKING
   - **Isi**: ID Booking, Tanggal, No WA, Nama, Sesi, Status (Pending), Timestamp
   - **Notif**: Sam dapat notif WA saat ada booking baru
   - **Manual Update**: Sam bisa update kolom Status (Confirmed/Cancelled) dan Catatan Sam

### 10. **Basic Analytics**
   - **Sheet STATS**: Tracking lengkap per user
     - Counter (jumlah pesan)
     - Tanggal chat pertama & terakhir
     - Jam chat terakhir
     - Follow-up count
     - User status (PARENT/STUDENT)
   - **Visual**: Lihat Intensitas Chat di sheet STATS (bar chart kuning di samping)

---

## 🔧 HANDLING DARI SAM UNTUK SEKARANG (MANUAL TASKS)

### 1. **Enrich FAQ & Database** ⭐ PRIORITAS TINGGI
   **Sheet yang Perlu Di-enrich**:
   - **FAQ**: Pertanyaan umum sehari-hari
   - **PROGRAM**: Detail program Junior/Intermediate/Senior
   - **BATCH**: Jadwal batch, deadline, kuota
   - **HARGA**: Biaya, cicilan, diskon (jika ada)
   - **SYARAT**: Syarat pendaftaran
   - **MOCK_INTERVIEW**: Detail layanan Mock Interview
   - **LINKS**: Link GForm, link apapun yang sering ditanya
   - **ABOUT_SAM**: Cerita personal Sam, biografi, motivasi (untuk build trust)

   **Cara**:
   - Buka setiap sheet → tambah baris baru
   - Isi dengan pertanyaan + jawaban yang relevan
   - Makin lengkap, makin pintar VIRA

   **Tips**:
   - Lihat sheet **UNKNOWN** untuk ide FAQ baru
   - Gunakan bahasa casual seperti Sam ngomong
   - Hindari jawaban terlalu panjang (max 2-3 kalimat per poin)

### 2. **Manual Update: gform_filled** ⭐ PENTING
   **Kapan**: Setiap kali Sam lihat ada submission baru di Google Form
   
   **Cara**:
   1. Buka sheet **STATS**
   2. Cari baris dengan No WA user yang baru submit GForm
   3. Di kolom **gform_filled** → isi **Y**

   **Kenapa Penting**: 
   - Menghentikan GForm Reminder untuk user tersebut
   - Sistem tahu user sudah daftar
   - Mencegah spam reminder

   **Note**: Fase 1 ini masih manual. Nanti fase 2 bisa otomatis detect dari GForm response.

### 3. **Manual Bot Mode: bot_mode = OFF**
   **Kapan**: Saat Sam perlu handle user secara manual (misal: diskusi pembayaran)
   
   **Cara Aktifkan Manual Mode**:
   1. Buka sheet **STATS**
   2. Cari baris dengan No WA user yang mau di-handle
   3. Di kolom **bot_mode** → isi **OFF**
   4. Sekarang Sam bebas chat manual, VIRA tidak akan balas

   **Cara Kembalikan ke Bot**:
   1. Buka sheet **STATS** lagi
   2. Hapus isi kolom **bot_mode** (kosongkan) atau isi **ON**
   3. VIRA aktif kembali

   **Use Case**:
   - Diskusi pembayaran Mock Interview
   - Negosiasi harga/cicilan
   - Handle komplain sensitif
   - Obrolan personal dengan calon murid/orang tua

### 4. **Monitor & Tindak Lanjut Sheet UNKNOWN**
   **Apa itu**: Sheet yang nyimpen pertanyaan user yang tidak bisa dijawab VIRA
   
   **Cara Handle**:
   1. Buka sheet **UNKNOWN** secara berkala (misal: tiap hari)
   2. Lihat pertanyaan yang masuk
   3. Opsi:
      - **Enrich FAQ**: Tambahkan ke sheet FAQ/database yang relevan
      - **Jawab Manual**: Aktifkan bot_mode = OFF → jawab langsung via WA
      - **Update Prompt**: Kasih tau Steven jika perlu update AI prompt

   **Tujuan**: Continuous improvement VIRA

### 5. **Update Status Booking di MOCK_INTERVIEW_BOOKING**
   **Kolom yang Bisa Sam Edit**:
   - **Status**: Ubah dari "Pending" ke "Confirmed" atau "Cancelled"
   - **Catatan Sam**: Tulis note internal (misal: "Sudah transfer", "Minta reschedule")

   **Cara**:
   1. Buka sheet **MOCK_INTERVIEW_BOOKING**
   2. Cari booking yang mau di-update
   3. Edit kolom Status dan/atau Catatan Sam

### 6. **Handle Post-GForm Payment Discussion** ⭐ ALUR PENTING
   **Alur yang Disarankan**:
   ```
   User nyatakan mau daftar Mock Interview
      ↓
   VIRA kirim GForm otomatis
      ↓
   User isi GForm → Sam dapat notif (dari Google Forms notification)
      ↓
   Sam aktifkan HITL (bot_mode = OFF) untuk user tersebut
      ↓
   Sam diskusi pembayaran manual via WA
      ↓
   Setelah payment settled → Sam update:
      - gform_filled = Y
      - bot_mode = kosongkan (atau ON)
      - Status di MOCK_INTERVIEW_BOOKING = "Confirmed"
   ```

### 7. **Greeting Flag (OPSIONAL - Fase 2)**
   **Kolom**: `greeting_sent` di STATS
   **Status Sekarang**: Manual (belum auto-detect)
   **Untuk Fase 1**: Biarkan saja, tidak perlu diisi
   **Untuk Nanti**: Nanti fase 2 akan otomatis terisi Y saat greeting pertama terkirim

---

## 💰 BUDGET & KAPASITAS SISTEM

### Budget OpenAI yang Sudah Diset
- **Budget Bulanan**: **$20 USD/bulan** (sudah Steven set di OpenAI billing)
- **Fungsi**: Untuk "otak" VIRA (AI yang memproses dan balas chat)

### Estimasi Kapasitas Chat (Bahasa Awam)

**Dengan budget $20/bulan sekarang:**
- **Estimasi**: **3,000 - 5,000 chat bubbles per bulan**
- **Artinya**: ~100-170 chat bubbles per hari
- **Atau**: ~15-25 user aktif per hari (asumsi 1 user chat 5-7 kali)

**Penjelasan Sederhana**:
- Setiap kali user kirim pesan → VIRA "mikir" pakai OpenAI → kena biaya
- Makin panjang percakapan, makin banyak token (= biaya) yang terpakai
- $20/bulan ini cukup untuk bisnis skala kecil-menengah yang baru mulai

**Catatan**:
- Estimasi ini konservatif (aman)
- Actual usage bisa lebih banyak karena sistem sudah dioptimasi
- Steven bisa monitor usage real-time di OpenAI dashboard

### Skenario Scaling ke Depan

**Jika The Scholars Makin Ramai:**

**Contoh Skenario**:
- Sekarang: ~20 user aktif/hari
- Target 3-6 bulan: ~50-100 user aktif/hari
- Target 1 tahun: ~200+ user aktif/hari

**Yang Perlu Di-upgrade:**

1. **Upgrade OpenAI Billing** 💵
   - **Kenapa**: Supaya token tidak habis di tengah bulan
   - **Estimasi Kebutuhan**:
     - 50 user/hari → ~$40-50/bulan
     - 100 user/hari → ~$80-100/bulan
     - 200 user/hari → ~$150-200/bulan
   - **Mudah**: Tinggal naikkan billing limit di OpenAI dashboard

2. **Upgrade Hardware/Server** 🖥️
   - **Kenapa**: n8n server (tempat VIRA jalan) perlu handle lebih banyak chat simultan
   - **Tanda-Tanda Perlu Upgrade**:
     - VIRA mulai lambat balas (delay >10 detik)
     - Ada error "timeout" atau "server busy"
     - Chat counter menunjukkan >100 chat/jam peak time
   - **Solusi**: 
     - Upgrade RAM server (dari 2GB → 4GB atau 8GB)
     - Upgrade CPU (lebih banyak core)
     - Pindah ke dedicated server jika perlu

**Rekomendasi Monitoring**:
- **Bulan 1-2**: Monitor daily chat volume di STATS sheet
- **Jika mendekati 150 chat/hari**: Siap-siap upgrade budget OpenAI ke $40-50/bulan
- **Jika ada error berulang**: Diskusi dengan Steven untuk upgrade server

**Good News**: 
- Scaling up itu tanda bagus = bisnis tumbuh! 🚀
- Upgrade bertahap, tidak perlu sekaligus
- Steven bisa adjust sesuai growth The Scholars

---

## 📊 QUICK REFERENCE: KOLOM PENTING DI GOOGLE SHEETS

### Sheet STATS
| Kolom | Isi Manual? | Keterangan |
|-------|-------------|------------|
| **bot_mode** | ✅ SAM | OFF = manual mode, kosong/ON = bot aktif |
| **gform_filled** | ✅ SAM | Y = user sudah isi GForm |
| **user_status** | ❌ AUTO | PARENT atau STUDENT (otomatis dari chat) |
| **greeting_sent** | ⚠️ OPSIONAL | Y = greeting sudah dikirim (fase 2) |
| Counter, Timestamp, dll | ❌ AUTO | Tracking otomatis oleh sistem |

### Sheet MOCK_INTERVIEW_BOOKING
| Kolom | Isi Manual? | Keterangan |
|-------|-------------|------------|
| **Status** | ✅ SAM | Pending → Confirmed/Cancelled |
| **Catatan Sam** | ✅ SAM | Note internal untuk Sam |
| ID Booking, Tanggal, dll | ❌ AUTO | Generated otomatis |

---

## ⚠️ CATATAN PENTING

1. **Jangan Edit Kolom Auto**: Kolom seperti Counter, Timestamp, No WA, dll jangan diedit manual (bisa bikin error)

2. **GForm Link**: Pastikan link GForm sudah dikasih ke Steven untuk diupdate di sistem

3. **Notifikasi WA**:
   - **Ke Sam**: Unknown FAQ, Booking baru
   - **Ke Steven**: Error teknis

4. **Follow-Up Jam 10 Pagi**: Sistem jalan otomatis, Sam tidak perlu trigger manual

5. **Testing**: Sebelum go-live, test semua skenario di Testing Checklist (ada di Master Manual)

6. **Database = Source of Truth**: VIRA hanya jawab dari database, jadi makin lengkap database, makin akurat jawaban

---

## 🎯 NEXT STEPS UNTUK SAM

**Hari 1-3 (Preparation)**:
1. ✅ Enrich minimal 10-15 FAQ per sheet (prioritas: FAQ, HARGA, BATCH)
2. ✅ Siapkan Google Form untuk Mock Interview
3. ✅ Test bot dengan nomor sendiri (kirim pesan, coba fitur)

**Go-Live**:
1. ✅ Monitor sheet UNKNOWN setiap hari
2. ✅ Update gform_filled setiap ada submission baru
3. ✅ Aktifkan bot_mode = OFF saat perlu handle manual

**Ongoing**:
1. ✅ Continuous enrichment FAQ berdasarkan pertanyaan user
2. ✅ Review analytics (counter, intensitas chat) untuk insight
3. ✅ Monitor volume chat harian - info ke Steven jika mulai ramai (>150 chat/hari)
4. ✅ Feedback ke Steven jika ada bug atau improvement ideas

---

## 💰 BUDGET OPENAI: $20 USD/BULAN - ESTIMASI KAPASITAS

**Budget**: $20 USD/bulan untuk OpenAI API

### Estimasi Kapasitas Chat:

**Skenario Konservatif** (lebih aman):
- **~1,300-1,500 percakapan/bulan**
- **~40-50 percakapan/hari**
- Asumsi: 1 user = 2-3 kali percakapan (chat awal + follow-up)
- **Artinya bisa handle ~20-25 user baru per hari**

**Skenario Optimis** (usage ringan):
- **~2,000-2,500 percakapan/bulan**
- **~65-80 percakapan/hari**
- Asumsi: User cuma tanya singkat 1-2 pertanyaan
- **Artinya bisa handle ~30-40 user per hari**

### Bahasa Awam:

**Analogi Simple**:
- 1 percakapan = 1 user chat dengan VIRA (bisa 3-5 pesan bolak-balik)
- Budget $20 = cukup untuk **40-50 user chat per hari** (konservatif)
- Kalau The Scholars dapat **10-15 inquiry per hari** → **masih sangat aman**
- Kalau tiba-tiba viral dan dapat **100+ chat/hari** → budget bisa habis lebih cepat

### Yang Bikin Budget Cepat Habis:
1. ❌ User chat panjang-panjang (10+ pesan bolak-balik)
2. ❌ Banyak query database (tools) per chat
3. ❌ Follow-up berjalan ke banyak user sekaligus
4. ❌ Spam dari bot testing (makanya ada rate limiter)

### Yang Bikin Budget Hemat:
1. ✅ User tanya singkat dan langsung to the point
2. ✅ FAQ database lengkap (VIRA langsung jawab tanpa banyak query)
3. ✅ Follow-up di-manage dengan baik (max 3x)
4. ✅ HITL aktif untuk diskusi panjang (Sam handle manual)

### Monitoring & Tips:

**Cara Monitor Usage**:
- Cek dashboard OpenAI: https://platform.openai.com/usage
- Lihat daily usage → kalau mendekati $0.70-1/hari = perlu waspada
- Set alert di OpenAI dashboard kalau usage >$15

**Tips Hemat**:
1. **Enrich FAQ maksimal** → makin lengkap FAQ, makin cepat jawab, makin hemat token
2. **Aktifkan HITL untuk chat panjang** → diskusi payment/komplain handle manual
3. **Batasi follow-up** → max 3x sudah cukup (sudah di-set di sistem)
4. **Pastikan rate limiter aktif** → mencegah spam

**Kalau Budget Hampir Habis**:
1. Upgrade budget jadi $30-40/bulan (untuk scale)
2. Atau: Batasi follow-up jadi max 2x
3. Atau: Non-aktifkan follow-up sementara untuk user lama (fokus user baru)

### Real Example The Scholars:

**Asumsi realistis**:
- Instagram followers: ~5,000
- Conversion rate inquiry: 0.5% = **25 inquiry/bulan**
- Setiap inquiry: 2-3 chat session
- Total chat: 25 x 2.5 = **62.5 chat/bulan**
- Cost estimate: 62.5 x $0.015 = **~$0.94/bulan** ✅

**Kesimpulan**: 
Dengan traffic normal The Scholars, budget $20/bulan **lebih dari cukup** bahkan untuk handle 10x lipat traffic (250 inquiry/bulan). Budget ini aman untuk **6-12 bulan kedepan** dengan growth normal.

---

**VIRA sudah siap kerja 24/7 untuk The Scholars! 🚀**

*Note ini bisa disimpan sebagai reference guide untuk Sam.*
