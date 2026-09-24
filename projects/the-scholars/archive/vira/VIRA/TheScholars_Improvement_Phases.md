# THE SCHOLARS VIRA — IMPROVEMENT PHASES
## Roadmap Pengembangan Bertahap dengan Estimasi Biaya

**Prepared for:** Sam (The Scholars)  
**Prepared by:** Steven Leroy  
**Date:** May 2026  
**Version:** 1.0

---

## 📋 EXECUTIVE SUMMARY

Dokumen ini merupakan roadmap pengembangan VIRA AI Chatbot untuk The Scholars dalam 7 fase bertahap. Setiap fase dirancang untuk:
- ✅ Mengurangi beban kerja manual Sam
- ✅ Meningkatkan kecepatan response ke murid
- ✅ Meminimalkan human error
- ✅ Mengotomasi proses repetitif

**Total Estimasi Biaya Development:** Rp 42.000.000 - Rp 74.000.000  
**Total Estimasi Biaya Maintenance/Bulan:** Rp 7.500.000 - Rp 14.000.000

---

## 🎯 URUTAN FASE (OPTIMAL SEQUENCE)

Fase telah diurutkan berdasarkan:
1. **Dependencies** — fase yang diperlukan oleh fase berikutnya
2. **Complexity** — dari termudah ke tersulit
3. **Impact** — prioritas value untuk operasional
4. **Technical Difficulty** — tingkat kesulitan implementasi

```
FASE 1A (Prioritas Tertinggi) ← Fix pain point existing
    ↓
FASE 2 (Payment Automation)
    ↓
FASE 3 (Scheduling Automation)
    ↓
⚠️ FASE 4 (Attendance - NEEDS CLARIFICATION)
    ↓
FASE 5 (Recording Distribution)
    ↓
FASE 6 (Analytics Dashboard)
```

---

# FASE 1A — Google Form Auto-Detection
## 🎯 OTOMASI DETEKSI PENGISIAN GOOGLE FORM

### Deskripsi Singkat
Saat ini, Sam harus **manual** cek Google Form submission lalu update kolom `gform_filled = Y` di STATS sheet. Fase ini mengotomasi proses tersebut menggunakan Google Apps Script + n8n webhook, sehingga kolom `gform_filled` otomatis berubah menjadi `Y` real-time saat user submit form.

### Problem yang Diselesaikan
- ❌ Sam lupa update `gform_filled` → user tetap dapat reminder padahal sudah isi form
- ❌ Delay 1-2 hari antara form submission dan update manual
- ❌ Human error: salah nomor WA, typo, skip update

### Implementasi yang Diperlukan

#### A. Kolom Baru di Google Sheets
| Sheet | Kolom Baru | Diisi oleh | Keterangan |
|-------|------------|------------|------------|
| STATS | `gform_filled_ts` | Sistem otomatis | (Opsional) Timestamp saat form diisi — untuk analytics |

*(Kolom `gform_filled` sudah ada, hanya perubahan dari manual → otomatis)*

#### B. Google Apps Script
- **Location:** Di Google Sheet yang terima form responses
- **Trigger:** On form submit
- **Fungsi:** Normalize nomor WA → kirim webhook ke n8n

**File baru:**
```
Google Sheet Responses → Extensions → Apps Script
├── onFormSubmit.gs (trigger function)
└── Config.gs (webhook URL)
```

#### C. n8n Workflow Baru
**Workflow Name:** `GForm_Auto_Update`

**Nodes:**
1. **Webhook** — terima POST dari Apps Script
2. **Code: Extract & Validate** — extract noWA, validate format
3. **Google Sheets: Lookup Row** — cari user di STATS by No WA
4. **IF: Row Found?**
   - TRUE → Update STATS: `gform_filled = Y`, `gform_filled_ts = now`
   - FALSE → Log warning (user belum pernah chat)
5. **Respond to Webhook** — send 200 OK / 404 Not Found

**Total Nodes:** 6  
**Complexity:** ⭐⭐ (Low-Medium)

#### D. Testing Scenarios
- ✅ User isi form dengan nomor WA yang sudah ada di STATS
- ✅ User isi form dengan format nomor berbeda (08xxx, +628xxx)
- ❌ User isi form dengan nomor WA yang belum ada di STATS (expected 404)
- ✅ User submit form 2x → idempotent, tidak error

#### E. Documentation Updates
- Update `4_VIRA_MasterManual_v3.md` → section GForm Flow
- Tambah troubleshooting guide untuk Apps Script errors

### Dependencies
- ✅ Fase 1 (CHATBOT_MAIN + Follow-Up) sudah live
- ✅ Google Form sudah ada dan ada kolom "Nomor WhatsApp"
- ✅ n8n instance accessible

### Timeline
- **Setup + Development:** 2-4 jam
- **Testing:** 1-2 jam
- **Documentation:** 30 menit
- **Total:** 0.5 hari kerja

### Biaya Development
**Estimasi:** Rp 1.500.000 - Rp 2.500.000

**Breakdown:**
- Apps Script development: 1 jam × Rp 300.000 = Rp 300.000
- n8n workflow build: 1 jam × Rp 300.000 = Rp 300.000
- Testing + debugging: 2 jam × Rp 300.000 = Rp 600.000
- Documentation: 1 jam × Rp 300.000 = Rp 300.000
- Buffer (20%): Rp 300.000

### Biaya Maintenance Bulanan
**Estimasi:** Rp 250.000 - Rp 500.000/bulan

**Termasuk:**
- Monitoring webhook executions (5 menit/hari)
- Handle edge cases / errors (1-2 jam/bulan)
- Apps Script quota monitoring

### Success Metrics
- ✅ 100% form submissions terdeteksi dalam <30 detik
- ✅ 0% manual update oleh Sam untuk kolom `gform_filled`
- ✅ Follow-up GForm Reminder rate turun 80%+ (karena auto-stop saat form diisi)

---

# FASE 2 — Payment Info Sender
## 💰 OTOMASI PENGIRIMAN INFO REKENING & INSTRUKSI BAYAR

### Deskripsi Singkat
Setelah Sam menandai booking sudah confirmed (`send_payment = Y`), sistem otomatis kirim info rekening + instruksi pembayaran via WhatsApp. Sam tidak perlu ketik manual ke setiap user.

### Problem yang Diselesaikan
- ❌ Sam harus copy-paste info rekening manual ke setiap murid
- ❌ Typo nomor rekening / nominal
- ❌ Delay pengiriman (Sam sibuk, lupa)

### Implementasi yang Diperlukan

#### A. Kolom Baru di Google Sheets
| Sheet | Kolom Baru | Diisi oleh | Keterangan |
|-------|------------|------------|------------|
| MOCK_INTERVIEW_BOOKING | `send_payment` | **Sam manual** | Isi `Y` saat booking dikonfirmasi dan siap kirim info bayar |
| MOCK_INTERVIEW_BOOKING | `payment_sent` | Sistem otomatis | Terisi `Y` setelah info bayar terkirim |
| MOCK_INTERVIEW_BOOKING | `payment_sent_ts` | Sistem otomatis | Unix timestamp pengiriman |
| MOCK_INTERVIEW_BOOKING | `payment_confirmed` | **Sam manual** | Isi `Y` setelah bukti transfer diterima (untuk Fase 3) |

#### B. Sheet Baru (Opsional)
**Sheet Name:** `PAYMENT_INFO`

| Kolom | Nilai | Keterangan |
|-------|-------|------------|
| bank_name | BCA / Mandiri / dll | Nama bank |
| account_number | 1234567890 | Nomor rekening |
| account_name | Sam / The Scholars | Nama penerima |
| mock_interview_price | 150000 | Harga Mock Interview (Rp) |

*Alternatif: hardcode di n8n node (lebih simple untuk Fase 2)*

#### C. n8n Workflow Baru
**Workflow Name:** `FASE2_PaymentSender`

**Nodes:**
1. **Schedule Trigger** — setiap 15 menit (polling)
2. **Read MOCK_INTERVIEW_BOOKING** — baca seluruh sheet
3. **Code: Filter Payment Queue** — filter: `send_payment=Y` AND `payment_sent≠Y`
4. **IF: Queue Not Empty?**
   - TRUE → Loop Over Items
   - FALSE → Stop
5. **Loop Over Items** — proses per user
6. **Set Payment Message** — build pesan dengan template
7. **Send Payment Info (Kirimi)** — kirim WA
8. **Update MOCK_INTERVIEW_BOOKING** — set `payment_sent=Y`, `payment_sent_ts=now`
9. **Error Handler** — jika gagal kirim → notify Sam

**Total Nodes:** 9  
**Complexity:** ⭐⭐⭐ (Medium)

#### D. Template Pesan
```
Haii Kak [nama]! 🎉

Booking Mock Interview kamu sudah dikonfirmasi ya.
Berikut info pembayarannya:

🏦 Bank: BCA
📋 No. Rekening: 1234567890
👤 Atas Nama: The Scholars
💰 Nominal: Rp 150.000

Setelah transfer, tolong kirim bukti pembayarannya
ke nomor ini ya Kak. Kami akan konfirmasi dalam
1x24 jam. Semangat! 💪
```

#### E. Testing Scenarios
- ✅ Sam isi `send_payment=Y` → dalam 15 menit user dapat WA
- ✅ User dapat WA → cek `payment_sent` otomatis jadi `Y`
- ✅ Sam isi `send_payment=Y` untuk 3 user sekaligus → semua terkirim
- ❌ Kirimi API error → Sam dapat notif error

### Dependencies
- ✅ Fase 1 sudah live
- ✅ Fase 1A sudah live (opsional tapi recommended)
- ✅ Sam punya rekening bank siap
- ✅ Harga Mock Interview sudah fix

### Timeline
- **Workflow development:** 3-4 jam
- **Template message refinement:** 1 jam
- **Testing:** 2-3 jam
- **Total:** 1 hari kerja

### Biaya Development
**Estimasi:** Rp 2.500.000 - Rp 4.000.000

**Breakdown:**
- n8n workflow build: 4 jam × Rp 300.000 = Rp 1.200.000
- Template message + personalization: 1 jam × Rp 300.000 = Rp 300.000
- Testing + edge cases: 3 jam × Rp 300.000 = Rp 900.000
- Documentation: 1 jam × Rp 300.000 = Rp 300.000
- Buffer (20%): Rp 500.000

### Biaya Maintenance Bulanan
**Estimasi:** Rp 500.000 - Rp 1.000.000/bulan

**Termasuk:**
- Monitoring scheduled runs
- Handle Kirimi API errors
- Update template jika ada perubahan info rekening
- Minor tweaks

### Success Metrics
- ✅ 100% booking yang di-mark `send_payment=Y` terkirim dalam <30 menit
- ✅ 0% manual copy-paste info rekening oleh Sam
- ✅ Waktu Sam untuk handle payment info turun 90%

---

# FASE 3 — Mock Interview Scheduler
## 📅 OTOMASI PENJADWALAN & KONFIRMASI MOCK INTERVIEW

### Deskripsi Singkat
Setelah Sam konfirmasi pembayaran (`payment_confirmed=Y`), sistem otomatis:
1. Assign slot jadwal dari sheet MOCK_INTERVIEW (cek availability)
2. Kirim konfirmasi jadwal + link Zoom
3. Kirim reminder H-1 sebelum sesi

### Problem yang Diselesaikan
- ❌ Sam harus manual cek jadwal mana yang available
- ❌ Sam harus manual assign murid ke slot
- ❌ Sam harus manual kirim konfirmasi + link Zoom
- ❌ Sam harus manual remind H-1 (sering lupa)

### Implementasi yang Diperlukan

#### A. Kolom Baru di Google Sheets
| Sheet | Kolom Baru | Diisi oleh | Keterangan |
|-------|------------|------------|------------|
| MOCK_INTERVIEW_BOOKING | `payment_confirmed` | **Sam manual** | Isi `Y` setelah bukti bayar valid |
| MOCK_INTERVIEW_BOOKING | `assigned_sesi` | Sistem otomatis | ID sesi yang di-assign |
| MOCK_INTERVIEW_BOOKING | `schedule_sent` | Sistem otomatis | `Y` setelah konfirmasi jadwal terkirim |
| MOCK_INTERVIEW_BOOKING | `reminder_sent` | Sistem otomatis | `Y` setelah reminder H-1 terkirim |
| MOCK_INTERVIEW | `zoom_link` | **Sam manual** | Link Zoom per sesi |
| MOCK_INTERVIEW | `slot_terisi` | Sistem otomatis | Counter jumlah murid yang sudah assign ke sesi ini |

#### B. n8n Workflow Baru
**Workflow Name:** `FASE3_Scheduler`

**Sub-Workflow A: Assign Schedule (Polling setiap 30 menit)**

**Nodes:**
1. **Schedule Trigger** — setiap 30 menit
2. **Read MOCK_INTERVIEW_BOOKING** — filter: `payment_confirmed=Y`, `schedule_sent≠Y`
3. **IF: Queue Not Empty?**
4. **Loop Over Items**
5. **Read MOCK_INTERVIEW** — cari sesi yang dipesan user (by Sesi name)
6. **Code: Check Availability** — cek `Sisa > 0` atau `slot_terisi < Kuota`
7. **IF: Slot Available?**
   - TRUE → Send Konfirmasi Jadwal + Update sheets
   - FALSE → Send "Slot Penuh" + Notify Sam
8. **Send Konfirmasi (Kirimi)**
9. **Update MOCK_INTERVIEW** — increment `slot_terisi`
10. **Update BOOKING** — set `schedule_sent=Y`, `assigned_sesi`

**Sub-Workflow B: H-1 Reminder (Schedule setiap hari jam 09:00)**

**Nodes:**
1. **Schedule Trigger** — daily 09:00
2. **Read MOCK_INTERVIEW_BOOKING** — filter: `schedule_sent=Y`, `reminder_sent≠Y`, `tanggal_sesi=besok`
3. **IF: Queue Not Empty?**
4. **Loop Over Items**
5. **Read MOCK_INTERVIEW** — ambil detail sesi + zoom_link
6. **Send Reminder H-1 (Kirimi)**
7. **Update BOOKING** — set `reminder_sent=Y`

**Total Nodes:** 17  
**Complexity:** ⭐⭐⭐⭐ (Medium-High)

#### C. Template Pesan

**Konfirmasi Jadwal:**
```
Haii Kak [nama]! ✅

Pembayaran sudah kami terima. Mock Interview
kamu sudah terkonfirmasi ya!

📅 Tanggal: [tanggal sesi]
⏰ Waktu: [waktu] WIB
🎥 Format: Online via Zoom
🔗 Link: [zoom_link]

Reminder akan kami kirim H-1 sebelum sesi.
Semangat persiapannya Kak! 💪
```

**Reminder H-1:**
```
Haii Kak [nama]! 👋

Reminder: Mock Interview kamu besok ya!

📅 [tanggal] pukul [waktu] WIB
🔗 Link Zoom: [zoom_link]

Pastikan koneksi internet stabil dan siap
15 menit sebelum sesi mulai. Semangat! 🌟
```

**Slot Penuh:**
```
Haii Kak [nama], 

Maaf ya, slot sesi [nama_sesi] yang kamu pilih
sudah penuh. Kami akan hubungi kamu untuk
reschedule ke sesi lain yang available.

Terima kasih pengertiannya! 🙏
```

#### D. Logic Availability Check
```javascript
// Di node Code: Check Availability
const sesi = $('Read MOCK_INTERVIEW').item.json;
const kuota = parseInt(sesi.Kuota);
const terisi = parseInt(sesi.slot_terisi || 0);
const sisa = kuota - terisi;

return {
  json: {
    available: sisa > 0,
    sisa: sisa,
    sesi_id: sesi['ID Sesi'],
    zoom_link: sesi.zoom_link
  }
};
```

#### E. Testing Scenarios
- ✅ Sam isi `payment_confirmed=Y` → user dapat konfirmasi dalam 30 menit
- ✅ Sesi sudah penuh (Sisa=0) → user dapat pesan "Slot Penuh"
- ✅ 3 user book sesi yang sama → hanya 3 pertama yang dapat (jika Kuota=3)
- ✅ H-1 sebelum sesi → user dapat reminder jam 09:00
- ❌ Zoom link kosong → Sam dapat notif error

### Dependencies
- ✅ Fase 2 sudah live
- ✅ Sam sudah setup Zoom meeting per sesi
- ✅ Sheet MOCK_INTERVIEW sudah ada kolom Kuota, Tanggal, Waktu

### Timeline
- **Workflow development:** 5-6 jam
- **Availability logic + edge cases:** 3-4 jam
- **Testing:** 3-4 jam
- **Total:** 2 hari kerja

### Biaya Development
**Estimasi:** Rp 5.000.000 - Rp 8.000.000

**Breakdown:**
- n8n workflow (2 sub-workflows): 6 jam × Rp 350.000 = Rp 2.100.000
- Availability logic + edge cases: 4 jam × Rp 350.000 = Rp 1.400.000
- Template messages (3 variants): 2 jam × Rp 350.000 = Rp 700.000
- Testing comprehensive: 4 jam × Rp 350.000 = Rp 1.400.000
- Documentation: 1.5 jam × Rp 350.000 = Rp 525.000
- Buffer (20%): Rp 1.000.000

### Biaya Maintenance Bulanan
**Estimasi:** Rp 1.000.000 - Rp 2.000.000/bulan

**Termasuk:**
- Monitor scheduled runs (2x daily)
- Handle slot availability conflicts
- Update Zoom links jika berubah
- Adjust reminder timing jika diperlukan
- Minor logic tweaks

### Success Metrics
- ✅ 100% booking yang confirmed dapat konfirmasi jadwal otomatis
- ✅ 0% double-booking ke sesi yang sama
- ✅ 95%+ reminder H-1 terkirim tepat waktu
- ✅ Waktu Sam untuk scheduling turun 95%

---

# ⚠️ FASE 4 — Attendance & Class Integration
## 📝 INTEGRASI ABSENSI KEHADIRAN MURID DI BATCH REGULER

### ⚠️ NEEDS CLARIFICATION — FASE INI BERBEDA DARI ROADMAP AWAL

**Ada perbedaan scope antara rencana awal vs yang disebutkan:**

**Roadmap Awal (di 5_VIRA_FaseRoadmap.md):**
- Fokus: Absensi untuk **Mock Interview** saja
- Trigger: Sam isi manual / Google Form per sesi Mock Interview
- Sheet: ATTENDANCE (track kehadiran Mock Interview)

**Rencana Baru yang Disebutkan:**
- Fokus: Absensi untuk **batch reguler yang berjalan** (misal: setiap Sabtu selama batch)
- Trigger: Form otomatis setiap pertemuan di batch yang aktif
- Integrasi: Dengan jadwal batch yang sedang berlangsung

### 🔍 Pertanyaan untuk Klarifikasi

Sebelum lanjut development Fase 4, tolong konfirmasi:

1. **Apakah Fase 4 ini untuk:**
   - [ ] A. Mock Interview saja (sesuai roadmap awal)
   - [ ] B. Batch reguler (kelas mingguan/rutin)
   - [ ] C. Keduanya (Mock Interview + Batch Reguler)

2. **Jika untuk Batch Reguler:**
   - Berapa batch yang biasanya berjalan bersamaan? (misal: 2-3 batch paralel?)
   - Jadwal batch fix atau fleksibel? (misal: selalu Sabtu jam 10, atau bisa berubah?)
   - Siapa yang isi form absensi? Murid atau Sam?
   - Kapan form dibuka? (H-0 pagi, atau saat kelas berlangsung?)

3. **Untuk opsi "geser hari":**
   - Apakah murid bisa pilih hari pengganti sendiri?
   - Atau Sam yang tentukan jadwal pengganti?

4. **Rekaman video yang diminta murid:**
   - Format: link YouTube? Google Drive?
   - Sam upload manual atau ada sistem lain?

### 💡 Rekomendasi Sementara

**Jika fokusnya Mock Interview (opsi A):**
→ Lanjut dengan scope roadmap awal (relatif simple)

**Jika fokusnya Batch Reguler (opsi B):**
→ Ini akan jadi fase yang **lebih kompleks** dari estimasi awal karena:
- Perlu tracking batch yang sedang aktif
- Perlu generate form per pertemuan otomatis
- Perlu handle "geser hari" (reschedule logic)
- Integration dengan sistem batch yang mungkin belum ada

**Estimasi Sementara (jika opsi B):**
- Development: 10-15 hari (lebih kompleks dari fase lain)
- Biaya: Rp 15.000.000 - Rp 25.000.000
- Maintenance: Rp 2.000.000 - Rp 3.500.000/bulan

### ⏸️ STATUS: ON HOLD — Menunggu Klarifikasi

**Setelah dapat klarifikasi, saya akan:**
1. Update fase 4 dengan detail lengkap
2. Re-adjust urutan fase jika diperlukan
3. Provide accurate cost estimate

---

# FASE 5 — Recording Distribution System
## 🎬 PENGIRIMAN LINK REKAMAN KELAS OTOMATIS

### Deskripsi Singkat
Murid yang tidak hadir (atau pilih opsi "berhalangan - kirim rekaman") otomatis menerima link rekaman kelas via WhatsApp setelah Sam upload dan publish rekaman.

### Problem yang Diselesaikan
- ❌ Sam harus manual catat siapa yang tidak hadir
- ❌ Sam harus manual kirim link rekaman satu-satu
- ❌ Lupa kirim rekaman untuk murid tertentu

### Dependencies
- ⚠️ **BLOCKED by Fase 4 clarification**
- Butuh data kehadiran dari Fase 4 (sheet ATTENDANCE)

### Implementasi yang Diperlukan

#### A. Kolom Baru di Google Sheets
| Sheet | Kolom Baru | Diisi oleh | Keterangan |
|-------|------------|------------|------------|
| MOCK_INTERVIEW (or BATCH_CLASSES) | `recording_link` | **Sam manual** | Link YouTube/Drive rekaman |
| MOCK_INTERVIEW (or BATCH_CLASSES) | `recording_published` | **Sam manual** | `Y` = siap dikirim ke murid |
| ATTENDANCE | `rekaman_terkirim` | Sistem otomatis | `Y` setelah link terkirim |
| ATTENDANCE | `rekaman_sent_ts` | Sistem otomatis | Timestamp pengiriman |

#### B. n8n Workflow Baru
**Workflow Name:** `FASE5_RecordingSender`

**Nodes:**
1. **Schedule Trigger** — setiap hari jam 20:00 (setelah kelas biasanya selesai)
2. **Read MOCK_INTERVIEW / BATCH_CLASSES** — filter: `recording_published=Y`
3. **Loop Over Sessions**
4. **Read ATTENDANCE** — filter: sesi ini + `hadir=N` + `rekaman_terkirim≠Y`
5. **IF: Queue Not Empty?**
6. **Loop Over Students**
7. **Send Recording Link (Kirimi)**
8. **Update ATTENDANCE** — set `rekaman_terkirim=Y`, timestamp

**Total Nodes:** 8  
**Complexity:** ⭐⭐⭐ (Medium)

#### C. Template Pesan
```
Haii Kak [nama]! 👋

Sayang kamu tidak bisa hadir di kelas kemarin.
Tapi tenang — ini link rekamannya:

🎬 [recording_link]

Bisa ditonton kapan saja ya Kak. Kalau ada pertanyaan
setelah nonton, langsung aja tanya ke sini!

Semangat belajarnya! 💪✨
```

#### D. Testing Scenarios
- ✅ Sam upload rekaman + isi `recording_published=Y` → murid yang tidak hadir dapat link
- ✅ Murid yang hadir tidak dapat link rekaman
- ✅ Sam publish 2 rekaman sekaligus → semua murid terkait dapat link masing-masing
- ❌ Recording link invalid → Sam dapat notif error

### Timeline (setelah Fase 4 selesai)
- **Workflow development:** 3-4 jam
- **Testing:** 2-3 jam
- **Total:** 1 hari kerja

### Biaya Development
**Estimasi:** Rp 3.000.000 - Rp 5.000.000

**Breakdown:**
- n8n workflow build: 4 jam × Rp 350.000 = Rp 1.400.000
- Integration with ATTENDANCE: 2 jam × Rp 350.000 = Rp 700.000
- Testing: 3 jam × Rp 350.000 = Rp 1.050.000
- Documentation: 1 jam × Rp 350.000 = Rp 350.000
- Buffer (20%): Rp 700.000

### Biaya Maintenance Bulanan
**Estimasi:** Rp 750.000 - Rp 1.500.000/bulan

**Termasuk:**
- Monitor scheduled runs
- Handle invalid recording links
- Update template jika ada perubahan format rekaman

### Success Metrics
- ✅ 100% murid yang tidak hadir dapat link rekaman dalam 24 jam
- ✅ 0% manual sending oleh Sam
- ✅ Waktu Sam untuk distribusi rekaman turun 100%

---

# FASE 6 — Analytics Dashboard
## 📊 LAPORAN PERFORMA & ANALISIS DATA CHAT

### Deskripsi Singkat
Laporan otomatis mingguan ke Sam via WhatsApp berisi metrik:
- Engagement chat (total user, pesan, rata-rata interaksi)
- Conversion rate (GForm dikirim → diisi → booking → confirmed)
- Kehadiran kelas (jika Fase 4 sudah jalan)
- Top pertanyaan yang tidak terjawab (dari sheet UNKNOWN)

### Problem yang Diselesaikan
- ❌ Sam tidak tahu performa VIRA tanpa manual count
- ❌ Tidak ada visibility untuk bottleneck di funnel
- ❌ Sulit track effectiveness follow-up

### Implementasi yang Diperlukan

#### A. Kolom Baru di Google Sheets
*Tidak ada kolom baru — read-only dari semua sheet existing*

#### B. Sheet Baru (Opsional)
**Sheet Name:** `WEEKLY_REPORTS` (untuk archive laporan)

| Kolom | Keterangan |
|-------|------------|
| week_start | Tanggal awal minggu |
| week_end | Tanggal akhir minggu |
| total_users | Total user baru minggu ini |
| total_messages | Total pesan masuk |
| gform_sent | GForm dikirim |
| gform_filled | GForm diisi (%) |
| bookings | Total booking |
| confirmed | Booking confirmed (%) |
| top_unknown | 3 pertanyaan paling sering di UNKNOWN |

#### C. n8n Workflow Baru
**Workflow Name:** `FASE6_Analytics`

**Nodes:**
1. **Schedule Trigger** — setiap Senin jam 08:00
2. **Set Week Range** — calculate start/end date minggu lalu
3. **Read STATS** — aggregate: new users, messages
4. **Read MOCK_INTERVIEW_BOOKING** — count: sent, filled, confirmed
5. **Read ATTENDANCE** (if Fase 4 done) — calculate: hadir, tidak hadir
6. **Read UNKNOWN** — aggregate: top 3 questions
7. **Code: Calculate All Metrics** — compile data jadi report
8. **Set Report Message** — format pesan WhatsApp
9. **Send Report to Sam (Kirimi)**
10. **(Optional) Save to WEEKLY_REPORTS sheet**

**Total Nodes:** 10  
**Complexity:** ⭐⭐⭐⭐ (Medium-High)

#### D. Template Laporan
```
📊 WEEKLY REPORT THE SCHOLARS
Minggu: [tanggal] - [tanggal]

💬 CHAT
• Total user baru: X
• Total pesan masuk: X
• Rata-rata pesan/user: X

📋 MOCK INTERVIEW
• GForm dikirim: X
• GForm diisi: X (X%)
• Booking confirmed: X
• Menunggu konfirmasi: X

📚 KEHADIRAN (jika Fase 4 aktif)
• Sesi berlangsung: X
• Total hadir: X (X%)
• Total tidak hadir: X
• Rekaman terkirim: X

❓ TOP UNKNOWN
1. [pertanyaan]
2. [pertanyaan]
3. [pertanyaan]

🎯 INSIGHTS
[Auto-generated insights based on metrics]
```

#### E. Metrics & Calculations

**Conversion Funnel:**
```
Chat → GForm Sent → GForm Filled → Booking → Confirmed → Attended
(100%) → (X%) → (X%) → (X%) → (X%) → (X%)
```

**Auto-Insights Logic:**
```javascript
// Contoh insights otomatis
if (gform_filled_rate < 50%) {
  insights.push("⚠️ GForm fill rate rendah (<50%) — cek apakah form terlalu panjang?");
}
if (booking_confirmed_rate < 70%) {
  insights.push("⚠️ Banyak booking belum confirmed — follow up payment?");
}
if (attendance_rate < 80%) {
  insights.push("💡 Attendance rate di bawah 80% — reminder H-1 sudah efektif?");
}
```

#### F. Testing Scenarios
- ✅ Senin jam 08:00 → Sam dapat laporan otomatis
- ✅ Data di laporan match dengan manual count di sheets
- ✅ Top UNKNOWN questions akurat (tidak duplikat)
- ✅ Insights relevant dengan kondisi data

### Dependencies
- ✅ Fase 1 sudah live minimal 2 minggu (ada data untuk dianalisis)
- ✅ Fase 1A-3 sudah live (untuk full funnel metrics)
- ⚠️ Fase 4-5 opsional (untuk attendance metrics)

### Timeline
- **Workflow development:** 5-6 jam
- **Metrics calculation logic:** 3-4 jam
- **Auto-insights algorithm:** 2-3 jam
- **Testing:** 2-3 jam
- **Total:** 2 hari kerja

### Biaya Development
**Estimasi:** Rp 6.000.000 - Rp 10.000.000

**Breakdown:**
- n8n workflow + aggregations: 6 jam × Rp 400.000 = Rp 2.400.000
- Metrics calculations: 4 jam × Rp 400.000 = Rp 1.600.000
- Auto-insights logic: 3 jam × Rp 400.000 = Rp 1.200.000
- Template + formatting: 2 jam × Rp 400.000 = Rp 800.000
- Testing comprehensive: 3 jam × Rp 400.000 = Rp 1.200.000
- Documentation: 1.5 jam × Rp 400.000 = Rp 600.000
- Buffer (20%): Rp 1.500.000

### Biaya Maintenance Bulanan
**Estimasi:** Rp 500.000 - Rp 1.000.000/bulan

**Termasuk:**
- Monitor weekly report accuracy
- Adjust metrics jika ada perubahan bisnis
- Update insights algorithm
- Add new metrics jika diperlukan

### Success Metrics
- ✅ Sam dapat laporan setiap Senin pagi tanpa request
- ✅ Data accuracy 100% (match dengan sheet data)
- ✅ Insights actionable dan relevan
- ✅ Sam bisa track progress week-over-week

---

# 📊 SUMMARY: INVESTMENT & ROI

## Total Investment Estimate

| Fase | Development Cost | Maintenance/Month | Timeline |
|------|------------------|-------------------|----------|
| **1A** — GForm Auto | Rp 1.500.000 - 2.500.000 | Rp 250.000 - 500.000 | 0.5 hari |
| **2** — Payment Sender | Rp 2.500.000 - 4.000.000 | Rp 500.000 - 1.000.000 | 1 hari |
| **3** — Scheduler | Rp 5.000.000 - 8.000.000 | Rp 1.000.000 - 2.000.000 | 2 hari |
| **4** — Attendance | ⚠️ TBD (pending clarification) | ⚠️ TBD | ⚠️ TBD |
| **5** — Recording | Rp 3.000.000 - 5.000.000 | Rp 750.000 - 1.500.000 | 1 hari |
| **6** — Analytics | Rp 6.000.000 - 10.000.000 | Rp 500.000 - 1.000.000 | 2 hari |
| **TOTAL** | **Rp 18.000.000 - 29.500.000** | **Rp 3.000.000 - 6.000.000** | **6.5 hari** |

*Estimasi di atas **BELUM termasuk Fase 4** karena menunggu klarifikasi scope.*

**Jika Fase 4 (Batch Reguler - Complex):**
- Development: +Rp 15.000.000 - 25.000.000
- Maintenance: +Rp 2.000.000 - 3.500.000/bulan
- Timeline: +10-15 hari

**GRAND TOTAL (jika semua fase):**
- **Development:** Rp 33.000.000 - 54.500.000
- **Maintenance:** Rp 5.000.000 - 9.500.000/bulan

## ROI Calculation (Conservative Estimate)

### Sam's Time Saved per Month

| Task | Before (jam/bulan) | After | Saved |
|------|-------------------|-------|-------|
| Update gform_filled manual | 2 jam | 0 jam | 2 jam |
| Send payment info manual | 4 jam | 0 jam | 4 jam |
| Schedule + send confirmations | 6 jam | 0 jam | 6 jam |
| Send recording links | 3 jam | 0 jam | 3 jam |
| Manual follow-up reminders | 4 jam | 0 jam | 4 jam |
| Generate reports manual | 2 jam | 0 jam | 2 jam |
| **TOTAL** | **21 jam/bulan** | **0 jam** | **21 jam** |

**Asumsi:** Sam's hourly rate = Rp 150.000/jam  
**Monthly savings:** 21 jam × Rp 150.000 = **Rp 3.150.000/bulan**

**Annual savings:** Rp 3.150.000 × 12 = **Rp 37.800.000/tahun**

### Break-Even Point

**Scenario 1 (Without Fase 4):**
- One-time dev cost: Rp 18.000.000 - 29.500.000
- Monthly cost: Rp 3.000.000 - 6.000.000
- Monthly savings: Rp 3.150.000
- **Net monthly:** Rp 150.000 - Rp 3.000.000 (deficit)
- **Break-even:** 6-10 bulan

**Scenario 2 (With Fase 4 - Complex):**
- One-time dev cost: Rp 33.000.000 - 54.500.000
- Monthly cost: Rp 5.000.000 - 9.500.000
- Monthly savings: Rp 3.150.000
- **Net monthly:** -Rp 1.850.000 to -Rp 6.350.000 (deficit)
- **Note:** Maintenance > savings — perlu evaluate business case

### Intangible Benefits (Not in ROI calc)
- ✅ Zero human error in data entry
- ✅ Faster response time → better student experience
- ✅ Scalability — handle 10x students without 10x Sam's time
- ✅ Data-driven decisions from analytics
- ✅ Professional brand image (fast, reliable, automated)

---

# 🚦 RECOMMENDATIONS

## Priority 1 (Immediate - High ROI)
✅ **Fase 1A** — GForm Auto-Detection  
**Why:** Fixes current pain point, low cost, quick win

✅ **Fase 2** — Payment Sender  
**Why:** High manual effort saved, simple implementation

## Priority 2 (Medium-term - Medium ROI)
✅ **Fase 3** — Scheduler  
**Why:** Complex but high value, saves significant time

✅ **Fase 6** — Analytics  
**Why:** Low dependency, can be done anytime, provides strategic insights

## Priority 3 (Long-term - Needs Evaluation)
⚠️ **Fase 4** — Attendance System  
**Why:** Needs scope clarification first. If complex (batch reguler), evaluate business case vs cost

⚠️ **Fase 5** — Recording Distribution  
**Why:** Depends on Fase 4, evaluate after Fase 4 scope is clear

---

# ❓ NEXT STEPS

**For Sam:**
1. **Review & approve** Fase 1A - 3 + 6 development plan
2. **Clarify Fase 4 scope:**
   - Mock Interview only? Or Batch Reguler?
   - How do you envision the attendance flow?
3. **Provide payment info** (bank account details for Fase 2)
4. **Setup Zoom links** for Mock Interview sessions (for Fase 3)

**For Development:**
1. Start with **Fase 1A** (quick win, 0.5 hari)
2. Proceed to **Fase 2** (1 hari)
3. **Fase 3** after Fase 2 tested & stable (2 hari)
4. **Fase 6** can run parallel or after Fase 3
5. **Fase 4-5** after clarification

---

**Questions? Clarifications?** Let me know mana fase yang mau di-adjust atau di-takeout! 🚀

---

*Document Version: 1.0*  
*Last Updated: May 2026*  
*Prepared by: Steven Leroy for The Scholars*
