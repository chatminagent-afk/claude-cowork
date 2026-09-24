# Konteks Proyek — Steven (Claude Cowork Workspace)
Ringkasan per 2026-09-08. Dipakai sebagai konteks awal kalau membuka chat/AI baru terkait pekerjaan Steven.

## Tentang Steven
Quality Assurance/Testing Analyst di **BCA (Bank Central Asia, Indonesia)** — kerja utama. Freelance di luar jam kerja untuk **The Scholars** (chatbot WA "VIRA") dan **TIM Interior**. Timezone WIB (Indonesia). Kerja campur Indonesia-Inggris (istilah teknis/sales biasanya tetap Inggris); jangan dipaksa full-Inggris kalau materi sumbernya campur.

## Proyek aktif
| Proyek | Ringkas |
|---|---|
| **VIRA** | WhatsApp AI assistant (n8n + Google Sheets + Kirimi webhook + AI Agent LLM). Sudah jadi produk yang dijual ke bisnis lain, bukan cuma internal The Scholars — detail teknis, pipeline deck, harga, dan jumlah klien ada di ringkasan terpisah "VIRA — Ringkasan Jualan". |
| **BIC 2026 / LUNA** | Entri kompetisi internal BCA (BCA Innovation Competition). LUNA = konsep AI assistant di dalam app myBCA (Learning, Understanding, Navigating, Assisting) — tombol full-moon floating, benefit bertingkat, konfirmasi transaksi via PIN. Deadline submission yang tercatat: 2026-07-10 — **catatan: tanggal itu sudah lewat dari hari ini, jadi kemungkinan sudah selesai/submit atau catatannya belum di-update, perlu dikonfirmasi ulang ke Steven sebelum dipakai sebagai fakta aktif.** |
| **Power Automate — Ci Lenny** | Otomasi buat Ci Lenny (kolega/senior di BCA): (1) Weekly MBI (MyBCA Individu) Projects Report — sumber data SharePoint Excel, output Teams adaptive card; (2) OtomasiStatusUAT — alur status UAT. |
| **TIM Interior** | Klien freelance interior design. Proyek yang tercatat: Rincian Hangtuah (breakdown biaya, Mei 2026). |

## Orang-orang kunci
| Nama | Peran |
|---|---|
| **Sam** | Klien freelance The Scholars (TheScholars.id) — pemilik VIRA; persona bot VIRA = "Sam versi AI" |
| **Ci Lenny** | Kolega/senior di BCA — Steven bikinkan flow Power Automate untuknya |
| **Om Sulianto** | Klien Persada Cisoka Residence — developer perumahan, klien ke-2 VIRA |

## Istilah (glossary singkat)
| Istilah | Arti |
|---|---|
| VIRA | WhatsApp AI assistant — awalnya untuk The Scholars, sekarang produk yang dijual ke klien lain juga |
| LUNA | AI assistant konsep di app myBCA — entri BIC 2026 |
| BIC | BCA Innovation Competition (kompetisi internal tahunan) |
| MBI | MyBCA Individu — kategori proyek di laporan mingguan Power Automate Ci Lenny |
| Kirimi | Gateway/webhook WhatsApp yang dipakai VIRA |
| STATS / MSG_BUFFER | Tab Google Sheets penyimpan state per-kontak VIRA |
| HITL | Human-in-the-loop — titik cek manual di alur VIRA |
| The Scholars | Konsultan pendidikan (program beasiswa Singapura) — klien pertama VIRA |

## Preferensi cara kerja Steven
- Konfirmasi dulu sebelum hapus/timpa/rename file — tunjukkan apa yang berubah sebelum eksekusi
- Kerjaan multi-step: outline rencana → tunggu approval → ringkas tiap langkah besar (bukan cuma di akhir)
- Nama file baru pakai format `YYYY-MM-DD-nama-deskriptif`
- Dokumen analisis/BCA/klien Indonesia ditulis dalam Bahasa Indonesia, mengikuti konvensi yang sudah ada
- Respons singkat dan padat — Steven baca diff/output langsung, tidak perlu banyak rekap

Terkait: lihat file "VIRA — Ringkasan Jualan" untuk detail produk VIRA (teknis, pipeline deck, harga, jumlah klien, playbook jualan).
