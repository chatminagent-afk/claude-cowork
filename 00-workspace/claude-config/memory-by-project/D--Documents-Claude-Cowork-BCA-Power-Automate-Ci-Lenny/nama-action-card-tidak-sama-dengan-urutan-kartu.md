---
name: nama-action-card-tidak-sama-dengan-urutan-kartu
description: Sejak weeklymbicl1.0, Card 1 dibuang tapi action-nya tetap bernama Compose_Card2/Compose_Card3 — "card 1" yang dimaksud Steven = Compose_Card2
metadata:
  type: project
---

Di paket `weeklymbicl*` (pengganti `weeklymbicilennyv7.2`), Card 1 lama sudah dihapus
tapi action yang tersisa **tidak di-rename**. Jadi pemetaannya:

- Steven bilang "card 1" → action `Compose_Card2` / `Post_Card2` (kartu "Bagian 1 dari 2", RELEASE bulan berjalan)
- Steven bilang "card 2" → action `Compose_Card3` / `Post_Card3` (kartu "Bagian 2 dari 2", RELEASE bulan berikutnya)

**Why:** salah petakan = mengedit kartu yang keliru, dan error-nya tidak ketahuan
sampai flow benar-benar dijalankan dan di-post ke Teams.

**How to apply:** sebelum mengedit kartu, konfirmasi lewat TextBlock "Bagian X dari 2"
di dalam ekspresi `Compose_*`, bukan lewat nama action-nya. Kalau suatu saat action
di-rename, hapus memory ini.

Terkait: [[excel-sumber-flow-bukan-file-lokal]]
