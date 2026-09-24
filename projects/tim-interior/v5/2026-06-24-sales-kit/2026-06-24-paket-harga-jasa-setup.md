# Paket Harga & Struktur — Jasa Setup + Retainer
### Sistem Manajemen Proyek untuk Studio Desain Interior

> Dokumen internal. Angka di bawah adalah **titik mulai** untuk pasar studio desain interior skala UKM (level harga menengah, biaya server + WhatsApp ditanggung dalam retainer). Sesuaikan dengan biaya riil dan respons pasarmu.

---

## 1. Model bisnis singkat

Kamu **tidak menjual aplikasi** (klien tidak bisa pakai sendiri tanpa setup). Kamu menjual **jasa**: memasangkan sistem siap-pakai + merawatnya tiap bulan.

Karena itu pendapatan punya dua lapis:

- **Setup fee (sekali bayar)** — kompensasi waktu pasang: clone workflow n8n, siapkan Google Sheet, sambungkan WhatsApp, deploy webform, training tim. Sekaligus menyaring klien yang serius.
- **Retainer (bulanan, berulang)** — inilah inti bisnisnya. Menutup biaya operasional (server n8n, device WhatsApp), maintenance, dan support. Recurring = pendapatan yang menumpuk tiap bulan.

**Kenapa ops dibungkus dalam retainer:** studio desain bukan orang teknis. Mereka mau "terima beres" — tidak mau pusing bikin akun server atau bayar layanan WA sendiri. Membungkus biaya ini bikin closing lebih mulus dan menambah marginmu.

---

## 2. Tiga paket

| | **MULAI** | **STUDIO** ⭐ | **SKALA** |
|---|---|---|---|
| **Untuk siapa** | Studio baru / freelancer interior, 1–2 proyek jalan | Studio aktif, beberapa proyek & pekerja | Studio mapan, banyak proyek + butuh kustom |
| **Setup fee (sekali)** | **Rp 2.500.000** | **Rp 4.000.000** | **Rp 6.500.000** |
| **Retainer (per bulan)** | **Rp 350.000** | **Rp 750.000** | **Rp 1.500.000** |
| Proyek aktif | s/d 3 | s/d 15 | Tidak dibatasi |
| Device WhatsApp recap | 1 | 1 | s/d 3 |
| Catat pekerjaan + komplain | ✅ | ✅ | ✅ |
| Dashboard monitoring | ✅ | ✅ | ✅ |
| Generate RAB + checklist | ✅ | ✅ | ✅ |
| Recap WA harian otomatis | ✅ | ✅ | ✅ |
| Kategori RAB kustom | — | ✅ | ✅ |
| Training tim | Video panduan | 1× sesi live (1 jam) | 2× sesi + onboarding |
| Branding di webform | Netral | Nama studio | Logo + warna studio |
| Laporan | — | Rekap bulanan | Rekap + review kuartalan |
| Support | WA, jam kerja | WA prioritas | WA prioritas + respons cepat |
| Biaya server + WA | Termasuk | Termasuk | Termasuk |

⭐ = paket yang didorong sebagai pilihan utama (anchor di tengah).

---

## 3. Apa yang termasuk di "Setup fee"

Sekali bayar di awal, mencakup pekerjaan pasang:

1. Provisioning workflow n8n untuk klien (clone dari template v4/v5).
2. Pembuatan Google Sheet 7-tab + isi data awal (proyek, pekerja, penerima recap).
3. Penyambungan device WhatsApp (kirimi.id) + uji recap harian.
4. Deploy webform (PWA) ke hosting + "Add to Home Screen".
5. Set `TEST_MODE = false` + uji semua flow end-to-end.
6. Training/handover sesuai tier.

**Aturan emas:** jangan mulai kerja teknis sebelum setup fee lunas / DP minimal 50%. Setup itu kerja nyata yang tidak bisa ditarik balik.

---

## 4. Apa yang termasuk di "Retainer"

Berulang tiap bulan, inilah yang membuat sistem tetap hidup:

- Hosting & operasional server n8n (shared, kamu yang kelola).
- Langganan device WhatsApp untuk recap.
- Monitoring agar recap harian & dashboard tetap jalan.
- Perbaikan bila ada error (kuota Google Sheets, webhook, dll).
- Update kecil & permintaan penyesuaian wajar.
- Support sesuai tier.

**Kalau klien berhenti bayar retainer:** recap WA & sinkronisasi berhenti, data tetap milik klien di Sheet mereka. Sampaikan ini transparan sejak awal.

---

## 5. Logika margin (untuk kontrol internal)

Biaya operasional per klien itu **kecil** karena infrastruktur dibagi:

| Komponen | Perkiraan biaya/bulan | Catatan |
|---|---|---|
| VPS n8n (Hostinger) | ~Rp 150.000 total | Dibagi banyak klien → per klien kecil |
| Device WA kirimi.id | ~Rp 50.000–100.000 | Per device |
| Google Workspace | Rp 0 | Tier gratis cukup di awal |

Artinya, di paket **MULAI** (retainer Rp 350.000): setelah dikurangi ~Rp 100.000 biaya WA + porsi server, **margin kotor tetap sehat**. Makin banyak klien berbagi VPS yang sama, makin tinggi marginnya. Inilah kenapa retainer > setup fee dalam jangka panjang.

**Target sederhana:** 10 klien paket STUDIO = Rp 7.500.000/bulan recurring, dengan biaya ops total masih di bawah ~Rp 1.500.000/bulan.

---

## 6. Add-on (opsional, naikkan nilai per klien)

- Migrasi data lama dari Excel/Sheet klien → **Rp 750.000** sekali.
- Device WhatsApp tambahan → **Rp 100.000/bulan** per device.
- Penyesuaian/laporan kustom di luar paket → **Rp 300.000–500.000/jam kerja**.
- Pelatihan tambahan → **Rp 500.000/sesi**.

---

## 7. Syarat & ketentuan ringkas (untuk dicantumkan di penawaran)

- Setup fee dibayar di muka (atau DP 50%, pelunasan saat go-live).
- Retainer ditagih bulanan/3-bulanan di awal periode.
- Kontrak minimum disarankan **3 bulan** agar setup sepadan.
- Data milik klien sepenuhnya; bisa diekspor kapan saja.
- Berhenti berlangganan: layanan otomatis & support berhenti di akhir periode berjalan.

---

## 8. Diskon & taktik closing (pakai secukupnya)

- **Diskon bayar tahunan**: gratis 1–2 bulan retainer bila bayar 12 bulan di muka → mengunci klien & arus kas.
- **Harga early-adopter**: untuk 3–5 klien pertama, potong setup fee dengan syarat boleh dijadikan studi kasus/testimoni.
- **Jangan banting harga retainer** — itu nyawa bisnismu. Lebih baik beri bonus (training/add-on) daripada turunkan retainer.
