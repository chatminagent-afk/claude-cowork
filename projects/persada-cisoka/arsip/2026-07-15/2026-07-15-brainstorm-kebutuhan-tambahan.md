# Brainstorm — Kebutuhan Tambahan untuk Ditanyakan ke Om Sulianto

Ide/use-case tambahan di luar 6 fungsi inti yang sudah disepakati. Dikelompokkan berdasarkan prioritas tanya. Tiap poin ditulis sebagai pertanyaan siap pakai.

---

## Prioritas Tinggi — Berpotensi Mengubah Desain Sistem

1. **Ketersediaan unit real-time.** "Apakah bot perlu tahu unit mana yang masih available (blok/nomor kavling), atau cukup info tipe & harga umum?" — Kalau perlu real-time, harus ada sheet stok yang di-update tim; ini mempengaruhi struktur database dari awal.
2. **Reminder survey H-1 / hari H.** "Mau nggak jadwal survey otomatis diingatkan ke klien H-1 dan pagi hari H?" — Mengurangi no-show, yang biasanya jadi keluhan terbesar tim lapangan. Teknisnya sama dengan follow-up system, murah untuk ditambahkan.
3. **Notifikasi lead panas ke tim.** "Kalau ada klien yang sangat serius (tanya DP, minta hitungan KPR, siap survey minggu ini), mau dinotif langsung ke WA siapa?" — Delegasi bukan cuma untuk yang sudah jadwal, tapi juga untuk yang hampir closing.
4. **Simulasi cicilan KPR otomatis.** "Boleh nggak bot menghitung estimasi cicilan (harga − DP, tenor, bunga bank rekanan) langsung di chat?" — Selling point kuat, tapi butuh persetujuan angka bunga yang boleh dipakai + disclaimer.
5. **Jam operasional bot.** "Bot jalan 24 jam atau ikut jam kerja? Kalau 24 jam, chat tengah malam yang minta telepon dijawab bagaimana?"

## Prioritas Menengah — Nilai Tambah Operasional

6. **Dashboard lead untuk owner.** "Mau nggak ada tampilan ringkas: berapa lead masuk hari ini, dari kanal mana, berapa yang jadwal survey, berapa yang datang?" — VIRA-DASHBOARD The Scholars bisa dipakai ulang dengan penyesuaian.
7. **Pencatatan hasil survey.** "Setelah klien datang survey, hasilnya (jadi nego / mikir / batal) dicatat di mana? Mau bot ikut menagih update status ke tim lapangan?" — Menutup loop funnel dari chat sampai closing.
8. **Follow-up pasca-survey.** "Klien yang sudah survey tapi belum booking, mau di-follow-up otomatis juga? Selang berapa hari, isi pesannya apa?"
9. **Broadcast promo.** "Kalau ada promo baru (subsidi DP, hadiah, kenaikan harga), mau bisa broadcast ke lead lama yang belum closing?" — Perlu cek dukungan API Kirimi + risiko banned WA; wajib opt-out.
10. **Multi-CS / lebih dari satu nomor.** "Nomor WA yang dipasang bot cuma satu? Ada rencana beberapa telemarketer pegang nomor masing-masing?" — Mempengaruhi arsitektur identitas & routing.

## Prioritas Rendah — Tanyakan Kalau Ada Waktu

11. **Bahasa & gaya.** "Klien lebih banyak formal ('Bapak/Ibu') atau santai? Ada istilah lokal Cisoka/Tangerang yang biasa dipakai?"
12. **Konten media lain.** "Selain brosur PDF: ada video walkthrough unit, site plan, atau lokasi Google Maps yang mau bisa dikirim bot?" — Kirim link Maps lokasi itu murah dan hampir pasti berguna untuk survey.
13. **Program referral.** "Ada program referral pembeli lama? Bot perlu bisa jelaskan/mencatat kode referral?"
14. **Kompetitor.** "Kalau klien membandingkan dengan perumahan sebelah, bot boleh menanggapi? Sampai batas mana?"
15. **Legalitas.** "Pertanyaan soal sertifikat (SHM/HGB), IMB/PBG, dan progres pembangunan — boleh dijawab bot dengan jawaban baku, atau selalu dioper ke manusia?"

## Pertanyaan Teknis/Administratif (Wajib Sebelum Mulai Bangun)

16. Nomor WhatsApp yang akan dipakai bot — baru atau nomor CS eksisting? (nomor eksisting = ada riwayat chat, perlu strategi migrasi)
17. Akun Kirimi: pakai akun sendiri Persada Cisoka atau satu akun dikelola Steven? Siapa yang bayar langganan?
18. Google Sheets/akun Google milik siapa yang jadi database? Siapa saja yang boleh akses?
19. Siapa PIC dari sisi Persada Cisoka untuk update data (harga, promo, stok)? Seberapa sering berubah?
20. Ekspektasi go-live kapan, dan siapa yang jadi penguji UAT dari sisi mereka?
