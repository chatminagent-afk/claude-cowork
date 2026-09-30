---
name: vira-ringkasan-jualan
description: "Ringkasan VIRA sebagai produk yang sedang dijual — fungsi, teknis workflow, kapasitas bikin deck otomatis, jumlah klien, harga, dan isu terbuka. Referensi cepat sebelum pitching ke prospek baru."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5da15ae2-881e-4642-8208-b35a803fa6b3
  modified: 2026-09-08T12:46:30.842Z
---

# VIRA — Ringkasan Jualan (per 2026-09-08)
VIRA bukan cuma bot The Scholars — sudah jadi produk yang ditawarkan ke bisnis lain, dengan mesin jualannya sendiri (VIRA Personal).

## Apa itu VIRA
WhatsApp AI Assistant premium 24/7, dijual per-klien (1 bot ter-custom, persona "[Nama klien] versi AI"). Fungsi inti: auto-reply + FAQ, catat aksi utama (booking/survey) + notifikasi tim, analytics dasar (sumber traffic), follow-up otomatis, call redirection. Premium: advanced insights. Nilai tambah di luar bot: dashboard performa lintas klien.

## Sudah berapa klien
- **The Scholars** (Sam) — klien 1, live production. Konsultan pendidikan/beasiswa Singapura. Fase bugfix/reliability, bukan lagi jualan.
- **Persada Cisoka Residence** (Om Sulianto) — klien 2, developer perumahan. Remake dari logika The Scholars + config multi-tenant. Workflow inti sudah dirakit, modul Follow-Up belum.
- **VIRA Personal** — bukan klien berbayar, ini instance Steven sendiri yang jadi mesin jualan (lihat bagian Deck).
- **Total realistis untuk pitching: 2 klien berbayar** (1 live, 1 hampir selesai).

## Teknis / arsitektur
- **n8n** = orchestration engine, 1 workflow WA per klien (webhook masuk → proses → balas)
- **Google Sheets** = database: STATS (state per kontak), FAQ/PROGRAM/ABOUT/LINKS/CONFIG per klien, + REQUESTS (brief prospek)
- **Kirimi** = gateway WA — webhook inbound, kirim media via URL (PDF/gambar, maks 64MB)
- **AI Agent (LLM) + memory manual** — memory bawaan reset tiap deploy, konteks jangka panjang disimpan di kolom sheet
- **Debounce 2 lapis** (~60s) — multi-pesan beruntun digabung jadi satu balasan
- **Identitas user**: nomor WA = primary key, ID internal = backup — tidak pernah fallback ke baris pertama sembarangan
- **Error handling**: workflow error terpisah → notifikasi admin saat gagal silent
- **Retention**: cron cleanup data lama, aturan beda per klien (sengaja)
- **Dashboard multi-tenant**: 1 backend, token per tenant, frontend generik statis, hosting Cloudflare — klien baru = 1 baris config

## Kita bisa bikin deck-nya — pipeline sudah otomatis sampai titik generate
Prospek chat ke VIRA Personal (persona "Steven versi AI") → digali bertahap, 1 pertanyaan per balasan, makin dalam kalau makin terbuka → tiap info baru masuk ke sheet (satu prospek = satu baris yang makin lengkap, data lama tak pernah tertimpa) → Steven dapat notifikasi WA otomatis begitu data minimum lengkap, isinya checklist kelengkapan + status siap-generate → Steven jalankan script generate → keluar PDF ~29 halaman → kalau kalimat mockup kurang pas, Steven tulis naskah sendiri (tersimpan, dipakai lagi di render berikutnya) → review → kirim ke prospek.

**Konsisten by design**: struktur slide dikunci (generator menolak jalan kalau template menyimpang), tanpa elemen acak/LLM saat render (brief sama → PDF identik), tiap render diverifikasi otomatis (jumlah halaman, teks wajib) — mencegah slide diam-diam terpotong.

**Sengaja tidak full-otomatis** — generate tidak terpicu sendiri oleh bot. Deck adalah aset jualan; deck lemah yang cepat terkirim lebih rugi daripada deck bagus yang telat sehari. Steven yang putuskan kapan generate.

**Isi deck** (~52% slide tetap/reusable, 29% teks variabel, 16% mockup chat custom dari kutipan asli prospek): cover, pain points, positioning "Premium 24/7 AI WhatsApp Assistant", 9 fitur inti, 5 slide mockup chat, fitur premium, perbandingan paket, tabel harga, 4 slide ROI (Time Freedom, Zero Leaking Profit, Scalability, Brand Trust), garansi, CTA penutup.

**Contoh harga yang sudah dipakai** (basis, sesuaikan per klien):
- The Scholars: Basic 2.499rb / Premium 4.499rb, setup 1.999rb (digratiskan), garansi 30 hari
- Persada Cisoka: Basic 3.000rb / Premium 5.000rb, setup 3.000rb (digratiskan), garansi tanpa batas, add-on bahasa 999rb/bulan

## Isu terbuka — cek sebelum pakai template ke prospek baru
- Baris setup fee di tabel harga template Persada kemungkinan rusak (label + baris fitur hilang) — verifikasi dulu
- Deck sebut angka add-on, tapi aturan bot melarang bot menyebut angka add-on — belum selaras
- Nomor kontak di slide penutup ada 2 versi berbeda digit — perlu diverifikasi
- Kutipan pihak ketiga di slide awal vs aturan bot yang melarang sebut nama employer Steven — soal konsistensi positioning
- Klaim hasil dalam angka (mis. "kenaikan omzet 20-30%") sudah sengaja dibuang — jangan dimunculkan lagi

## Playbook jualan yang terbukti
Diagnosis dulu sebelum menawarkan (target, masalah paling nyeri, kenapa belum beli). Berani bilang kalau harga/positioning lemah. Jual transformasi/identitas, bukan spesifikasi teknis — fitur → manfaat → identitas.

Tiga prinsip: **(1) Perceived value > harga** — naikkan nilai dulu sebelum sebut angka. **(2) Dengarkan dulu** — pahami target & bahasa mereka sebelum menulis penawaran. **(3) Trust di atas segalanya** — bukti konkret mengalahkan klaim kosong, jangan over-promise.

Urutan yang menjual: pahami target & nyeri → kunci transformasi yang dijual → buka dari masalah mereka (bukan produk) → naikkan perceived value → tanam bukti/trust → hilangkan risiko (garansi, trial) → satu CTA jelas.

Pola add-on yang terbukti closing: free trial dengan tanggal akhir jelas, JANGAN pakai frasa yang menanam kemungkinan gagal ("kalau nggak kepakai"), posisikan sebagai add-on terpisah bukan kenaikan harga utama, sebutkan batasan data di depan, jangan buka dengan harga sebelum value terbangun, sebut angka dev fee lalu bebaskan (bukan langsung "gratis").

Hindari: over-promise, buka dengan harga/fitur sebelum value terbangun, nada memaksa (false scarcity, guilt-trip), materi generik yang tak nembak target spesifik.
