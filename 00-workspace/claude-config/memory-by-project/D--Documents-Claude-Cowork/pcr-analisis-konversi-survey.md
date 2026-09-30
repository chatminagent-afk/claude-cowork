---
name: pcr-analisis-konversi-survey
description: "Baseline & temuan analisis konversi survey VIRA-PCR (2026-09-18) — angka funnel, kebocoran utama, dan rekomendasi yang belum diputuskan"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9dc8a27d-194a-4bc9-aeaf-2316a9e91107
  modified: 2026-09-18T01:59:04.356Z
---

Analisis 2026-09-18 atas sheet live PCR (627 kontak STATS, 12 flag_survey=Y = 1,9%).

Baseline untuk pembanding nanti:
- Counter=1 (tak pernah balas setelah template iklan): ~20% kohort s/d 23 Ags → ~37% sejak 24 Ags (lompatan, penyebab belum diverifikasi: delivery WA vs perubahan iklan FB).
- 0 konversi di bawah 6 pesan; Y median 10,5 pesan. 9/12 booking tanpa follow-up.
- Follow-up: 513 di-FU → 63 balas → 3 survey. 154 kontak Counter=1 sudah dapat median 7 FU.
- 41 near-miss (survey dibahas/niat datang) vs 12 booked. Bot mengajak survey hanya ~25% dari kontak yang sudah bahas detail (dari ringkasan `konteks`).
- Estimasi tim manusia sendiri: 20–30% chat → janji survey.

Penyebab di workflow yang teridentifikasi: booking wajib tanggal+jam+unit lengkap ("siangan"/"sekarang" gagal), regex `mentionsDateTime` tidak kenal format "21 sep", pending slot TTL 48 jam, pesan pertama = intro + 3 pertanyaan tanpa info, FU AI dilarang angka/file/ajak survey (FU≥6), tier FU tidak reset setelah lead membalas, bot_mode OFF permanen & tak tercatat hasilnya, tidak ada reminder H-1 / status hadir.

Status: rekomendasi disampaikan ke Steven, belum ada keputusan implementasi. Revisi `followup_max` bertentangan dengan keputusan 2026-08-31 — harus diputuskan Steven/klien.

Terkait: [[persada-cisoka-residence]], [[retensi-stats-beda-per-klien]]
