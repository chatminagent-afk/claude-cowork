# TIM Interior v3 — Konten PPT untuk Canva
> Setup: Rp 5.000.000 | Bulanan: Rp 2.500.000/bln
> Total: 17 slide

---

## SLIDE 1 — COVER

**Headline:**
The Future of Team Coordination.
*v3*

**Tagline:**
"Satu sistem. Dua akses. Semua terkoordinasi."

**Sub:**
Presented by Steven Leroy

**Visual suggestion:** Background gelap/elegan, logo TIM Interior, tipografi besar serif + sans-serif contrast.

---

## SLIDE 2 — TABLE OF CONTENTS

1. The Problem
2. Our Solution
3. System Overview
4. Website 1 — Internal Dashboard
5. Website 2 — Worker View
6. Fitur Lengkap
7. Otomasi WhatsApp
8. Database & Backend
9. Benefit Harian
10. Benefit Manajerial
11. Investment
12. Next Steps

---

## SLIDE 3 — THE PROBLEM

**Heading:** Masalah yang Makin Rumit Seiring Proyek Bertambah

**Pain points (kiri):**
- 📩 Komplain nyebar — chat, lisan, foto di HP, sticky note
- 📋 Catatan pekerjaan tidak seragam antar tukang
- 🔄 Rekap manual — buang waktu, rawan miss
- ❓ Tidak ada yang tahu: *siapa ngerjain apa, sampai mana?*
- 💸 RAB & checklist dibuat ulang dari nol setiap proyek
- 🔥 Volume puluhan catatan/hari → kalau tidak 1 pintu → numpuk & berantakan

**Pull quote:**
> "Kalau chat lagi rame, komplain tenggelam. Kalau tidak ada sistem, tidak ada akuntabilitas."

---

## SLIDE 4 — OUR SOLUTION

**Heading:** TIM Interior v3 — Satu Ekosistem, Semua Terhubung

**3 pilar (bisa visual 3 kolom/kartu):**

**🖥️ 2 Website**
Internal Dashboard untuk admin/pengawas + Worker View khusus tukang — masing-masing punya tampilan dan akses sesuai perannya.

**⚡ Otomasi Penuh**
Dari input → database → notifikasi WA → status update, semua jalan tanpa intervensi manual.

**📊 1 Database Terpusat**
Google Sheets terstruktur. Bisa difilter, diedit, diexport kapan saja. Tidak ada data yang tercecer.

---

## SLIDE 5 — SYSTEM OVERVIEW / ARSITEKTUR

**Heading:** Bagaimana Sistemnya Bekerja?

**Diagram alur (kiri ke kanan / atas ke bawah):**

```
[Internal Dashboard]  ──┐
                         ├──► [n8n Automation Engine] ──► [Google Sheets DB]
[Worker View]        ──┘                                        │
                                                                 ▼
                                                        [Google Drive]
                                                                 │
                                                                 ▼
                                                     [WhatsApp Rekap Otomatis]
```

**Komponen:**
| Komponen | Fungsi |
|---|---|
| Internal Dashboard | Input komplain, pekerjaan, RAB, cek status |
| Worker View | Tukang lihat tugas & update status mereka sendiri |
| n8n Workflow | Otak otomasi — 72 node, 10 webhook endpoint |
| Google Sheets | Database utama (5 tab terstruktur) |
| Google Drive | Penyimpanan lampiran foto/dokumen otomatis |
| WhatsApp (Kirimi.id) | Rekap & notifikasi otomatis ke tim |

---

## SLIDE 6 — WEBSITE 1: INTERNAL DASHBOARD

**Heading:** Internal Dashboard
*Untuk Pengawas, Admin, dan PIC Proyek*

**Sub:** Akses penuh ke semua fungsi sistem. Dioptimalkan untuk mobile — bisa dipakai langsung dari lapangan.

**4 Menu Utama (tampilkan sebagai card/grid):**

### 📋 Catat Pekerjaan
Input item kerja harian dalam format RAB. Pilih tukang, pilih proyek, tambah item pekerjaan lengkap dengan volume, satuan, dan harga satuan → sistem otomatis hitung total.

### ⚠️ Catat Komplain
Laporkan temuan atau masalah lapangan. Input proyek, pengaju, deskripsi komplain, lokasi, dan prioritas (Tinggi / Sedang / Rendah). Opsional: lampiran foto langsung ke Drive.

### 🔍 Cek Pekerjaan & Komplain
Cari per nama tukang → lihat semua pekerjaan dan komplain mereka. Update status langsung dari sini (Pending / Proses / Selesai).

### 📊 Generate RAB / Checklist
Pilih proyek → sistem tarik data pekerjaan yang sudah diinput → generate dokumen RAB siap cetak + checklist lapangan otomatis.

**Footer note:** *Dapat diinstal sebagai PWA (shortcut di homescreen HP)*

---

## SLIDE 7 — WEBSITE 2: WORKER VIEW

**Heading:** Worker View
*Untuk Tukang & Tenaga Lapangan*

**Sub:** Tampilan sederhana, hanya yang relevan. Tukang pilih nama mereka → langsung lihat tugas hari ini.

**Flow penggunaan:**

1. 👤 **Pilih Nama** — tukang ketuk nama mereka dari daftar
2. 📋 **Lihat Tugas** — tampil semua item pekerjaan yang ditugaskan, dikelompokkan per proyek/catatan
3. ✅ **Update Status** — ketuk per item: Pending → In Progress → Done
4. 💾 **Simpan** — status langsung tersimpan ke database, tim internal langsung bisa lihat

**Tambahan:**
- Kartu komplain yang pengaju = nama tukang tersebut juga tampil, bisa update status (Open → Proses → Selesai)
- Progress summary: berapa item aktif, berapa sudah done

**Footer note:** *Dapat diinstal sebagai PWA — tukang tidak perlu install app apapun*

---

## SLIDE 8 — FITUR: PENCATATAN PEKERJAAN & RAB

**Heading:** Pencatatan Pekerjaan Format RAB

**Kiri — Input:**
- Pilih nama tukang (dari dropdown database)
- Pilih proyek
- Tanggal & catatan area pekerjaan
- Tambah item: nama pekerjaan, volume, satuan, harga satuan
- Sistem hitung total otomatis per item dan keseluruhan
- Bisa tambah banyak item sekaligus dalam 1 batch

**Kanan — Output yang dihasilkan:**
- **Batch ID otomatis** (contoh: `PKJ-2026-001`)
- Data tersimpan ke Google Sheets tab Pekerjaan
- Tersedia untuk di-generate menjadi **dokumen RAB** (format tabel siap cetak)
- Tersedia untuk di-generate menjadi **Checklist lapangan** (item kerja + kotak centang)

**Visual suggestion:** mockup tabel RAB dengan kolom No | Pekerjaan | Vol | Sat | Harga/Sat | Total

---

## SLIDE 9 — FITUR: PENCATATAN KOMPLAIN

**Heading:** Pencatatan Komplain — 1 Pintu, Semua Tercatat

**Input fields:**
| Field | Keterangan |
|---|---|
| Proyek | Pilih dari dropdown |
| Pengaju | Nama pelapor |
| Deskripsi Komplain | Isi temuan / masalah |
| Lokasi | Area spesifik di lapangan |
| Prioritas | Tinggi / Sedang / Rendah |
| Lampiran | Foto opsional → auto upload ke Drive |

**Setelah submit:**
- ID komplain otomatis (contoh: `KMP-2026-047`)
- Status awal: **Pending** (jelas mana yang baru masuk)
- Data masuk real-time ke Google Sheets
- Muncul di rekap WA pagi berikutnya
- Link lampiran tersimpan di kolom database (tidak tercecer di chat)

---

## SLIDE 10 — FITUR: CEK & UPDATE STATUS

**Heading:** Real-Time Status Tracking

**Alur dari Worker View:**
- Tukang buka Worker View → pilih nama → semua tugas tampil
- Per item: ketuk status → pilih Pending / In Progress / Done
- "Simpan Update" → sistem kirim ke n8n → update sheet PekerjaanStatus

**Alur dari Internal Dashboard:**
- Admin/pengawas cari per nama tukang
- Lihat progress semua item sekaligus
- Update status komplain: Open → Proses → Selesai

**Visibilitas untuk manajemen:**
- Siapa ngerjain apa → jelas
- Item mana yang stuck → langsung ketahuan
- Tidak ada lagi tanya-tanya di chat "udah selesai belum?"

---

## SLIDE 11 — FITUR: OTOMASI WHATSAPP

**Heading:** Rekap Harian Otomatis via WhatsApp

**Kapan terkirim:** Setiap hari pukul 08.00 WIB (bisa disesuaikan)

**Isi rekap WA:**
- 📌 Daftar komplain dikelompokkan per proyek
- 📊 Summary: total komplain, pending, reported
- 🆕 Komplain baru dengan penanda khusus
- 🔴 Komplain prioritas tinggi dengan penanda khusus
- Progress pekerjaan tukang (opsional per kebutuhan)

**Setelah rekap terkirim, sistem otomatis:**
- Update status: Pending → Reported
- Naik Notify_Count (info berapa kali sudah diingatkan)

**Manfaat:**
> Semua PIC mulai hari dengan situasi terkini yang sama — tanpa perlu scroll chat panjang.

**Visual suggestion:** mockup bubble WA dengan format rekap

---

## SLIDE 12 — DATABASE & BACKEND

**Heading:** Infrastruktur yang Solid & Transparan

**Google Sheets — 5 Tab Terstruktur:**
| Tab | Isi |
|---|---|
| **Pekerja** | Nama, No HP, Keterangan |
| **Pekerjaan** | Batch ID, Tanggal, Proyek, Pekerja, Item, Vol, Sat, Harga, Total |
| **PekerjaanStatus** | Batch ID, No Item, Status, Updated At |
| **Komplain** | ID, Tanggal, Proyek, Pengaju, Deskripsi, Lokasi, Prioritas, Status |
| **Project** | Nama Project, Keterangan |

**Bisa difilter langsung di Sheet:**
- Per proyek, per status, per prioritas, per tanggal, per tukang

**n8n Workflow Engine:**
- 72 node otomasi
- 10 webhook endpoint aktif
- Error handling di setiap jalur
- Self-hosted → data tidak keluar ke third party

**Google Drive:**
- Lampiran foto tersimpan otomatis per folder
- Link tercatat di database

---

## SLIDE 13 — BENEFIT HARIAN

**Heading:** Apa yang Berubah Sehari-hari?

**Untuk Tukang / Tenaga Lapangan:**
- ✅ Tahu persis apa yang harus dikerjakan hari ini
- ✅ Bisa update progress sendiri — tidak tunggu ditanya
- ✅ Komplain yang mereka laporkan punya bukti + ID resmi

**Untuk Pengawas / Admin:**
- ✅ Tidak perlu tanya satu-satu "udah sampai mana?"
- ✅ Komplain tidak tenggelam di chat — semua punya ID & status
- ✅ Lampiran foto aman di Drive, tidak hilang di HP orang
- ✅ RAB & checklist bisa generate dalam hitungan detik
- ✅ Prioritas terlihat jelas — bukan perasaan

**Pull quote:**
> "Tidak ada lagi 'siapa yang harus follow up?' — ownership terlihat dari database."

---

## SLIDE 14 — BENEFIT MANAJERIAL

**Heading:** Kontrol Penuh untuk Owner & Leader

**Visibility:**
- Cukup buka sheet atau baca summary WA: lihat kondisi semua proyek tanpa harus telepon satu-satu
- Total komplain, pending, sudah ditangani — semua dalam 1 view

**Evaluasi Performa:**
- Notify_Count per komplain → tahu mana yang sering diingatkan & mana bottleneck
- Histori status + timestamp → bisa audit alur penanganan

**Analisis Pola:**
- Kategori + proyek → ketahuan "Proyek A sering ada masalah di area X" → jadi bahan perbaikan proses atau evaluasi vendor

**Handover Lebih Mudah:**
- Semua catatan ada di database — bukan di chat pribadi tukang atau HP pengawas lama
- PIC baru tinggal buka sheet, langsung dapat konteks penuh

**Risiko Berkurang:**
- Komplain numpuk lebih cepat kebaca
- Tidak ada lagi "lupa follow up yang bikin klien komplain berulang"

---

## SLIDE 15 — INVESTMENT

**Heading:** Investasi yang Sepadan

**Layout: 1 paket besar (bukan 2 kolom)**

---

### 🚀 TIM Interior v3 — Full Package

**Setup (1x bayar):**
# Rp 5.000.000

**Termasuk:**
- ✅ Setup 2 Website (Internal Dashboard + Worker View)
- ✅ Konfigurasi n8n Workflow (72 node, 10 endpoint)
- ✅ Setup Google Sheets Database (5 tab terstruktur)
- ✅ Koneksi Google Drive (lampiran otomatis)
- ✅ Integrasi WhatsApp otomatis (via Kirimi.id)
- ✅ Testing & QA end-to-end
- ✅ Onboarding & panduan penggunaan tim

---

**Biaya Bulanan:**
# Rp 2.500.000 / bulan

**Termasuk:**
- ✅ Biaya tools (n8n hosting + Kirimi.id WA gateway)
- ✅ Maintenance & monitoring sistem
- ✅ Minor adjustment (maks 1 jam/bulan) — contoh: tambah/kurangi kategori, ubah format rekap WA, update daftar proyek, dll
- ✅ Support troubleshooting

**Catatan:**
> Pengembangan modul baru (fitur di luar scope v3) dihitung terpisah.
> Minimum komitmen: 3 bulan.

---

## SLIDE 16 — TIMELINE & NEXT STEPS

**Heading:** Dari Sekarang ke Go-Live dalam 4 Hari

**Timeline visual (horizontal):**

| Hari | Kegiatan |
|---|---|
| **Day 1** | Finalisasi akses (Google Sheet, Drive, WA number) + konfirmasi field & proyek |
| **Day 2** | Setup sistem, konfigurasi workflow, koneksi database |
| **Day 3** | Testing internal — semua endpoint, semua screen |
| **Day 4** | Go-Live + pilot 14 hari dengan data real |
| **Week 2** | Evaluasi pilot → tweak kecil jika perlu |

**Rekomendasi:**
1. Pilot 14 hari — pakai data real, lihat flow
2. Setelah pilot → langsung lanjut (min. 3 bulan)
3. Evaluasi bersama di bulan ke-2: ada fitur tambahan yang dibutuhkan?

---

## SLIDE 17 — PENUTUP / Q&A

**Headline:**
Siap Koordinasi Lebih Rapi?

**Sub:**
Mulai dengan satu langkah kecil — sistem yang bekerja untuk timmu, bukan sebaliknya.

**CTA:**
> Let's talk. →

**Contact:**
Steven Leroy
[kontak / WA]

---

## CATATAN VISUAL UNTUK CANVA

- **Palet warna:** Gelap elegan (navy/charcoal) + aksen emas/krem (sesuai brand TIM Interior)
- **Font pairing:** Playfair Display (heading) + Inter/Poppins (body)
- **Ikon:** Gunakan emoji atau icon set konsisten (Phosphor / Heroicons)
- **Slide rasio:** 16:9 standar presentasi
- **Foto/mockup:** Gunakan screenshot nyata dari webform & worker-view sebagai visual pendukung di slide fitur
- **Diagram arsitektur (slide 5):** Buat dengan shape + panah di Canva — 4 kotak horizontal: Dashboard → n8n → Sheets → WA
