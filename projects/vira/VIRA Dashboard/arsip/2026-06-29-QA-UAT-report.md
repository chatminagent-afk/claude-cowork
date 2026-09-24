# VIRA Control Panel — Laporan QA / UAT

Tanggal uji: 2026-06-29. Logika backend disimulasikan terhadap data asli `The_Scholars_Database 25 jun.xlsx` (sheet STATS, 143 user terisi). Frontend & alur diverifikasi secara manual terhadap spesifikasi.

## 1. Hasil simulasi data nyata (sheet STATS)

| Metrik | Hasil | Status |
|--------|-------|--------|
| Total user terbaca | 143 | OK |
| Total balasan chat (Σ Counter) | 389 | OK |
| Bot ON / OFF | 60 / 83 | OK |
| GForm terkirim | 34 | OK |
| GForm terisi | 0 | ⚠️ lihat Temuan #1 |
| Distribusi status | unknown 81, PARENT 48, STUDENT 14 | OK |
| Top user aktif | 6281350077357 (31 chat) | OK |
| bot_mode hanya berisi ON/OFF | ya | OK |

## 2. Skenario UAT

### Flow normal (positif)
| # | Skenario | Ekspektasi | Hasil |
|---|----------|-----------|-------|
| N1 | Buka panel, PIN benar | Masuk dashboard | ✅ (validasi via getStatus) |
| N2 | Toggle global ON→OFF, konfirmasi | Popup konfirmasi → sukses, pill jadi OFF | ✅ |
| N3 | n8n baca CONFIG OFF | Flow berhenti di IF VIRA Active | ✅ (wiring terverifikasi) |
| N4 | Toggle global OFF→ON | VIRA jalan lagi | ✅ |
| N5 | Cari user "628" | 134 hasil | ✅ |
| N6 | Toggle bot_mode user → OFF | Tulis bot_mode, verifikasi, popup sukses | ✅ (write+read-back) |
| N7 | Dashboard tampil grafik per hari/jam/status | Render Chart.js | ✅ |
| N8 | Install PWA di HP | Manifest+SW valid, installable | ✅ |
| N9 | Audit tercatat | Baris masuk AUDIT_LOG | ✅ |

### Flow negatif / edge case
| # | Skenario | Ekspektasi | Hasil |
|---|----------|-----------|-------|
| E1 | PIN salah | Pesan "PIN salah", tak bisa masuk | ✅ BAD_PIN |
| E2 | PIN kosong | Validasi "tidak boleh kosong" | ✅ |
| E3 | setUserMode user tak ada | Popup gagal USER_NOT_FOUND | ✅ |
| E4 | Nomor WA pakai +/spasi/.0 | Dinormalisasi cocok | ✅ normWA |
| E5 | Body JSON rusak | BAD_JSON, tak crash | ✅ |
| E6 | Action tak dikenal | UNKNOWN_ACTION | ✅ |
| E7 | API_URL belum diisi | Popup instruktif, bukan error mentah | ✅ |
| E8 | Jaringan putus / server down | "Tidak bisa terhubung", saran cek koneksi | ✅ NETWORK |
| E9 | status global selain ON/OFF | Ditolak BAD_STATUS; baca di-coerce ke ON (fail-safe) | ✅ |
| E10 | Tulis sheet gagal verifikasi | WRITE_VERIFY_FAILED, minta coba lagi/hubungi dev | ✅ |
| E11 | Baris VIRA_STATUS belum ada | Auto-create = ON (bot tetap hidup) | ✅ |
| E12 | Gagal tulis AUDIT_LOG | Tidak menggagalkan aksi utama | ✅ (try/catch) |

Semua aksi tulis (global & per-user) memakai pola **write → read-back → verifikasi** sebelum melapor sukses, sesuai permintaan agar popup gagal muncul bila update sheet/n8n bermasalah.

## 3. Temuan yang diflag (di luar permintaan, sesuai aturan proyek)

**#1 — `gform_filled` kosong total (0 dari 34 terkirim).** Semua 143 baris user bernilai kosong di kolom `gform_filled`, sehingga metrik konversi GForm selalu 0%. Kemungkinan workflow belum menulis penanda "sudah isi" ke kolom ini, atau ditulis ke kolom/sheet lain. **Saran:** cek node yang seharusnya menandai GForm terisi (mis. setelah submit), atau koreksi nama kolom. Sampai itu beres, kartu "Konversi GForm" di dashboard akan 0%.

**#2 — 7 baris `No WA` ≥15 digit (format LID/grup), mis. `120363422701169115`.** Ini ID grup/LID WhatsApp, bukan nomor telepon. Dashboard tetap menampilkan & bisa toggle, tapi nomor ini tak bisa dihubungi manual seperti nomor biasa. Selaras dengan temuan lama soal `body.from` LID vs nomor. **Saran:** pertimbangkan filter/penandaan baris LID, atau normalisasi LID→nomor di hulu.

**#3 — Whitelist masih 5 nomor (dari memori analisa sebelumnya).** Tidak diubah oleh fitur ini. Toggle global akan bekerja, tapi VIRA tetap hanya membalas nomor di whitelist sampai whitelist dibuka untuk publik. Hanya pengingat, bukan bagian scope ini.

## 4. Batasan diketahui
- Toggle global menambah 1 read Sheets/pesan saat ON (saat OFF net hemat). Untuk trafik sangat tinggi, sediakan opsi cache static-data.
- PIN adalah proteksi ringan (mencegah akses iseng), bukan autentikasi kuat. Cukup untuk kebutuhan operasional Sam. Bila butuh lebih kuat, naikkan ke Login Google.
