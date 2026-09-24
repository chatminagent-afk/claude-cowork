# Outline Pitch Deck "VIRA Persada" — hasil adjustment dari VIRA.pdf (The Scholars)

**Basis:** VIRA.pdf (31 slide, The Scholars) + blueprint/analisis Persada Cisoka Residence (2026-07-15).
**Status kolom:** KEEP (tidak berubah) / ADJUST (isi disesuaikan, struktur sama) / REPLACE (isi diganti total) / REMOVE (dihapus) / NEW (slide baru).

---

## Ringkasan temuan analisis (kenapa tiap slide berubah)

VIRA.pdf ditulis untuk bisnis **kursus/PMB** (booking les, tutor, invoice per sesi). Tiga sumber ketidaksesuaian utama kalau dipakai apa adanya untuk Persada Cisoka:

1. **Semua mockup chat (slide 10, 11, 13, 15, 19) pakai skenario "booking les Mr. Andi/Ms. Rina"** — tidak ada padanan asli untuk properti karena VIRA-PCR belum live. Screenshot asli tidak bisa direuse; harus jadi **mockup ilustrasi baru** (redraw, bukan screenshot chat sungguhan) yang menunjukkan flow properti: tanya harga unit → tanya KPR → minta jadwal survey → VIRA catat & notify tim lapangan.
2. **Klaim waktu respons "<1 menit" (slide 26) tidak valid** untuk arsitektur yang sudah kita desain. `Wait3` debounce di VIRA (fixed 60 detik) + waktu proses AI (~3-8 detik) + `Wait1` jeda alami sebelum kirim (5-10 detik) = **respons riil ±60-90 detik, bukan di bawah 1 menit**. Ini bukan bug — debounce 60 detik ini SENGAJA ada supaya kalau user kirim 3-4 bubble berturut-turut, VIRA nunggu dan gabung jadi 1 balasan utuh (bukan balas per-bubble yang berantakan). Klaim harus diubah jadi jujur: **"respons dalam hitungan menit, bukan jam/hari"** — tetap radikal lebih cepat dari CS manual, tapi tidak menjanjikan sesuatu yang secara teknis salah.
3. **Automated Invoicing sama sekali tidak relevan** — itu fitur untuk bisnis kursus yang menagih per sesi/paket. Developer perumahan tidak invoice calon pembeli lewat chatbot (transaksi properti pakai jalur legal/notaris terpisah). Dihapus total dari semua slide (fitur, komparasi, harga, ROI).

Selain itu, blueprint Persada Cisoka punya **4 fungsi yang SAMA SEKALI TIDAK ADA di VIRA.pdf** karena tidak dibutuhkan bisnis kursus: Survey Scheduling (pengganti Booking), Call Redirection, Traffic Source Recognition, Delegasi ke Tim Lapangan, dan Summarization/Handover otomatis. Ini yang justru jadi pembeda kuat untuk pitch properti — harus ditonjolkan, bukan disembunyikan di balik struktur lama.

---

## Outline per slide

| # | Slide asli (VIRA.pdf) | Status | Isi baru / adjustment |
|---|---|---|---|
| 1 | Cover "The Future of Customer Service" | ADJUST | Tagline diganti dari "Respon instan, konversi maksimal" → **"Respon cepat, calon pembeli nggak keburu kabur."** (hindari kata "instan" — tidak akurat). Subtitle tambahan: "AI WhatsApp Assistant untuk Persada Cisoka Residence". Presented by Steven Leroy — tetap. |
| 2 | Agenda | ADJUST | Tambah 1 item baru: **"Risiko & Penanganan"** disisipkan sebelum "Implementation" (jadi item 08, geser Implementation ke 09→10 dst). |
| 3 | Quote Wani Sabu (BCA) | KEEP | Kutipan generik soal CS = garda terdepan kepercayaan, relevan lintas industri termasuk properti (bahkan lebih relevan — transaksi besar butuh trust). Tidak diubah. |
| 4 | Pain Points #1 (respon lambat, multi-platform, owner overload, human error) | REPLACE | Ganti konteks kursus → properti:<br>• **Respon Lambat ke Calon Pembeli** — leads properti mahal (iklan IG/FB/Google), telat respon = calon pembeli lanjut ke developer sebelah.<br>• **Multi-Platform Chaos** — IG DM + WA + telepon, leads gampang keselip.<br>• **Owner/Tim Sales Overload** — sales harus handle chat + telepon + antar survey sendiri.<br>• **Human Error Jadwal Survey** — salah catat tanggal/jam survey, lupa follow-up. |
| 5 | Pain Points #2 (biaya admin, manual invoice, lost revenue) | ADJUST | • **Biaya Tinggi Hire Sales/Telemarketer** — tetap relevan (Rp4-6jt/bulan/orang).<br>• ~~Manual Invoice~~ **DIHAPUS**, diganti: **Leads Panas Terlewat** — klien yang sudah tanya DP/KPR/siap survey minggu ini tidak segera ditindaklanjuti karena antrean chat.<br>• **Lost Revenue from No Follow-Up** — tetap, sangat relevan (klien yang belum booking survey lupa di-follow up = leads mati sia-sia). |
| 6 | VIRA title card | KEEP | Tidak berubah. |
| 7 | "WHY?" transisi | KEEP | Tidak berubah. |
| 8 | Core Features (list ✅) | REPLACE | Reuse: WhatsApp Auto-Reply 24/7, FAQ Handling, NLP, Basic Analytics, Google Sheets Sync, Automated Follow Up.<br>Diganti nama: ~~Automated Booking~~ → **Automated Survey Scheduling** (catat jadwal survey ke Sheets, bukan booking les).<br>~~Automated Invoicing~~ **DIHAPUS**.<br>**BARU ditambahkan** (fungsi inti blueprint yang tidak ada di kursus): **Call Redirection**, **Traffic Source Recognition**, **Delegasi Otomatis ke Tim Lapangan**, **Ringkasan Handover ke Admin** (bukan pesan mentah). Karena daftar jadi panjang (~11 item), pertimbangkan split jadi 2 slide: "Core Features" (reuse) + "Fitur Khusus Properti" (baru/pembeda). |
| 9 | "The Flow" transisi | KEEP | Tidak berubah. |
| 10 | Mockup chat: FAQ → booking les → data lengkap → konfirmasi | REPLACE | Mockup baru (ilustrasi, bukan screenshot asli — VIRA-PCR belum live): User tanya unit/harga → VIRA jawab dari data PRODUK → User minta survey → VIRA gali tanggal/jam/unit diminati → keluarkan konfirmasi jadwal. |
| 11 | Screenshot Google Sheets booking + notif admin | REPLACE | Mockup tabel sheet baru: kolom `SURVEY` (No WA, Nama, Tanggal, Jam, Unit Diminati, Status, Sumber Traffic) — sesuai skema §1.3 blueprint. Notif ke **tim lapangan** (bukan admin tunggal), isinya ringkasan hasil handover, bukan pesan mentah. |
| 12 | Invoice otomatis (email + PDF) | REMOVE | Dihapus total — tidak relevan. |
| 13 | Basic Analytics (screenshot sheet counter/intensitas chat) | ADJUST | Sama strukturnya, ganti kolom contoh jadi konteks properti (Nama, Unit Diminati, Sumber Traffic, Counter, dst — bukan nama kursus). |
| 14 | Unknown FAQ (notif admin + input sheet) | KEEP struktur | Ganti contoh pertanyaan dari konteks kursus → properti (mis. "apakah bisa nego harga", "legalitas SHM gimana"). |
| 15 | Automated Follow Up (screenshot WA follow-up les) | REPLACE | Mockup follow-up properti: "Halo Kak, masih berminat lihat-lihat unit di Persada Cisoka? Saya bantu jadwalkan kunjungan yaa" — sesuai template §2.4 blueprint. |
| 15b | **(NEW, disisip setelah 15)** Call Redirection | NEW | Mockup singkat: klien minta nomor yang bisa dihubungi → VIRA balas otomatis + sisipkan nomor admin dari CONFIG (bukan AI mengarang nomor). |
| 15c | **(NEW)** Traffic Source Recognition | NEW | Diagram sederhana: pesan pembuka user dari IG/FB/Google/TikTok terdeteksi otomatis by keyword → tercatat di kolom `lead_source` — dipakai untuk laporan kanal mana yang paling efektif. |
| 15d | **(NEW)** Delegasi ke Tim Lapangan + Ringkasan Handover | NEW | Diagram: begitu jadwal survey terkonfirmasi → sistem bikin ringkasan otomatis (nama, unit, budget, poin penting) → kirim ke WA tim lapangan — tim datang ke lapangan sudah pegang konteks lengkap, bukan cuma nama & nomor. |
| 15e | **(NEW, tambahan usulan — lihat poin 8)** Kirim Brosur & Siteplan Otomatis | NEW | Mockup: user tanya detail unit → VIRA kirim balasan teks singkat + otomatis lampirkan file brosur PDF/siteplan (bukan cuma link, langsung attachment di WA) — dari katalog `LINKS` yang tim Persada bisa update sendiri tanpa sentuh sistem. |
| 16 | "Scale Beyond Limits" transisi | KEEP | Tidak berubah. |
| 17 | Premium Features (list) | ADJUST | Reuse semua: Advanced Insights, Custom Persona, Priority Support, Monthly Persona Update, Global Language Capability, Custom Needs. Deskripsi disesuaikan bahasa (properti, bukan kursus). Global Language tetap relevan (calon pembeli WNA/luar kota). |
| 18 | Advanced Insights (dashboard screenshot) | ADJUST | Sama struktur, ganti label metrik: Total Chat, Total Jadwal Survey, Conversion Rate (chat→survey), Peak Hour, Top Unit Diminati. |
| 19 | Custom Persona + Global Language (mockup 3-bahasa) | ADJUST | Ganti konten chat dari "tanya kursus seni" → "tanya unit/tutor" jadi "tanya unit/KPR". |
| 20 | Comparison table Basic vs Premium | REPLACE (final) | Baris fitur diganti sesuai daftar baru di slide 8 (Survey Scheduling, Call Redirection, Traffic Source Recognition, Delegasi Tim Lapangan, Ringkasan Handover, Media Sending — semua masuk **Basic**, bukan Premium-only, karena ini fungsi inti bukan add-on). ~~Automated Invoicing~~ dan ~~Order Form~~ **dihapus permanen** dari tabel. |
| 21 | "Investment" transisi | KEEP | Tidak berubah. |
| 22 | Tabel harga Basic/Premium/Add-Ons | ADJUST (final) | **Basic: Rp 3.000.000/bulan** (dari 2.499.000). **Premium: Rp 5.000.000/bulan** (dari 4.499.000). **One-Time System Setup & Integration: Rp 3.000.000, dicoret jadi (Free)** (naik dari 1.999.000, tetap gratis di penawaran). **Global Language Capability Add-On: tetap Rp 999.000/bulan** (tidak berubah). Baris fitur ikut perubahan slide 20 (Invoicing & Order Form hilang, fitur baru masuk). |
| 23 | "WHY?" transisi #2 | KEEP | Tidak berubah. |
| 24 | "Advantages & ROI" transisi | KEEP | Tidak berubah. |
| 25 | #1 Time Freedom (2 jam chat + 1 jam invoice = 3 jam/hari) | ADJUST | Hilangkan komponen "1 jam invoice" (tidak ada invoicing). Ganti breakdown: 2 jam/hari balas chat + telepon calon pembeli + 1 jam/hari koordinasi jadwal survey manual = **3 jam/hari** tetap relevan tapi dengan alasan berbeda. Total jam/bulan dialihkan ke: strategi marketing, follow-up leads lama, negosiasi closing — bukan "pengembangan kurikulum". |
| 26 | #2 Zero Leaking Profit ("<1 menit", contoh Rp1jt/prospek) | REPLACE (final, keputusan 2026-07-16) | **Klaim waktu**: "<1 menit" → **"kurang lebih 1 menit"** (jujur sesuai debounce 60 detik + proses).<br>**Angle baru — bukan lagi hitungan Rp/prospek, tapi "kapan pun, siapa pun":**<br><br>**Judul tetap:** Zero Leaking Profit<br>**Subjudul:** Balas Kapan Pun, Bukan Cuma Jam Kerja<br>• Calon pembeli properti nggak selalu chat di jam kerja kantor — banyak yang justru baru sempat mikirin beli rumah atau browsing-browsing lewat tengah malam, sepulang kerja shift, atau pas libur.<br>• VIRA balas kurang lebih 1 menit, 24 jam — baik yang chat siang bolong maupun jam 2 pagi. Nggak ada lagi calon pembeli shift malam yang chat lalu baru dibalas besok siang — keburu dingin, keburu lirik developer sebelah.<br><br>**Kenapa kecepatan ini penting:**<br>• Niat beli rumah punya "jendela minat" yang sempit. Begitu direspons cepat selagi masih semangat, peluang lanjut ke jadwal survey jauh lebih besar dibanding dibalas besok saat minatnya sudah turun.<br>• Rantai dampak: **Respons Lebih Cepat → Survey Lebih Cepat Terjadwal → Closing Lebih Cepat.**<br><br>*Faster Response ->>> More Impact.* (echo tagline slide sebelumnya, konsisten gaya "Bigger Bowl ->>> More Impact") |
| 27 | #3 Scalability without Complexity | KEEP | Argumen generik (chat naik 100→1000/hari, biaya tetap) berlaku sama untuk properti, tidak ada angka spesifik kursus yang perlu diganti. |
| 28 | #4 Brand Trust | ADJUST | Perkuat: untuk keputusan pembelian besar (properti), trust ke sistem respons yang rapi malah LEBIH krusial dibanding kursus — reword sedikit ke arah itu. |
| **29 (NEW)** | **Risiko & Penanganan** | **NEW — disisip sebelum Implementation** | Lihat detail di bawah. |
| 30 | Implementation timeline (Day 1/15/30/31) | ADJUST | Item generik tetap sama strukturnya, sesuaikan istilah: "Membuat Database" → isi tab STATS/SURVEY/PRODUK/FAQ/LINKS/CONFIG; "Testing Workflow" mencakup test flow survey scheduling + delegasi tim lapangan. |
| 31 | 100% Satisfaction Guarantee | KEEP | Tidak berubah. |
| 32 | Closing "Let's Start" | ADJUST | Ganti branding jadi "VIRA untuk Persada Cisoka Residence", kontak Steven tetap sama. |

---

## Detail slide baru: Risiko & Penanganan (item 2 dari permintaan)

Ditulis dengan bahasa awam, jujur, tidak menutupi risiko tapi framing solutif:

**Judul:** "Risiko Teknis & Bagaimana Kami Menanganinya"

**Isi:**
- **Risiko yang mungkin terjadi (kecil, tapi nyata):** sewaktu-waktu server AI atau jalur WhatsApp API bisa mengalami gangguan sementara (down) — ini terjadi pada semua sistem digital, termasuk aplikasi besar sekalipun, dan bukan sesuatu yang bisa dijamin 100% tidak pernah terjadi oleh penyedia manapun.
- **Bagaimana VIRA menangani ini:** sistem dilengkapi **mekanisme deteksi otomatis** — begitu ada error/gangguan yang membuat pesan gagal diproses, notifikasi otomatis langsung terkirim ke Steven secara real-time. Bot tidak akan diam-diam berhenti bekerja tanpa siapa pun tahu.
- **Jalur eskalasi cepat:** kalau terjadi gangguan, Om Sulianto/tim bisa langsung hubungi Steven untuk penanganan cepat — bukan menunggu tiket support berhari-hari.

*(Ini basisnya dari mekanisme "Error Notifier" yang sudah didesain di blueprint — workflow terpisah yang menangkap semua exception dan WA-notify admin/Steven otomatis.)*

---

## Keputusan Final (dikonfirmasi 2026-07-16)

1. Klaim waktu respons → **"kurang lebih 1 menit"**.
2. Slide 26 diganti angle "balas kapan pun, jam berapa pun" + rantai dampak "Respons Lebih Cepat → Survey Lebih Cepat → Closing Lebih Cepat" — copy final sudah masuk ke tabel di atas.
3. Automated Invoicing dihapus permanen dari semua slide.
4. **Setup fee naik jadi Rp 3.000.000** (tetap dicoret jadi Free). **Global Language Add-On tetap Rp 999.000/bulan.**
5. Angka ROI numerik (Rp/prospek) dihapus, diganti narasi kualitatif poin 2 — tidak butuh data tambahan dari Om Sulianto lagi untuk slide ini.
6. Mockup ilustrasi chat WA — dibuatkan (lihat file terpisah/artifact mockup).
7. "Order Form" dihapus permanen dari tabel komparasi.
8. Usulan tambahan dari saya — lihat baris **15e (Kirim Brosur & Siteplan Otomatis)** di atas, ditambahkan sebagai slide spotlight fitur baru karena punya nilai visual kuat dan sudah ada desain teknisnya (lihat `2026-07-15-desain-media-sending.md`). **Belum saya masukkan** (sengaja, karena belum dikonfirmasi ke klien): Reminder Survey H-1 dan Notifikasi Lead Panas dari brainstorm — dua ide ini kuat tapi statusnya masih pertanyaan terbuka ke Om Sulianto, bukan fitur yang sudah disepakati dibangun. Kalau nanti jawabannya "ya", baru ditambah sebagai slide/fitur baru.

---

Lanjut ke: duplicate file Canva VIRA → rename "VIRA Persada" → build ulang slide per outline ini.
