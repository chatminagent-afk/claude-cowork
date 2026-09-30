---
name: retensi-stats-beda-per-klien
description: Aturan retensi/cleanup tab STATS sengaja BERBEDA antara The Scholars dan Persada — jangan disamakan; plus temuan last_reply_ts PCR hanya ditulis di cabang bot_mode ON
metadata:
  type: project
---

Aturan cleanup STATS **sengaja berbeda per klien**. Jangan pernah menyalin logika satu ke yang lain tanpa bertanya.

| | The Scholars (`STATS Cleanup TS`) | Persada (`VIRA-PCR - STATS Purge`) |
|---|---|---|
| Pengecualian | `bot_mode=OFF` + `off_reason != VIRA` dilindungi **permanen** | **tidak ada pengecualian** (keputusan Steven 2026-08-27) |
| Basis umur | nilai terbesar dari `last_reply_ts, buffer_done_ts, timestamp, gform_sent_ts, kelas_anak_ts` + fallback tanggal | `last_reply_ts` saja |
| Baris tanpa jejak waktu | disimpan + dilaporkan | **dihapus** |
| Retensi | 90 hari hardcoded | dari CONFIG `stats_purge_retention_days` (default 90) |
| Dry-run | **tidak ada** | ada (`stats_purge_dry_run`) |
| Cron | `1 0 1 */3 *` | `30 2 1 */3 *` (masih `active:false`) |

**Temuan 2026-09-05 (belum masuk dokumen mana pun):** di PCR, `last_reply_ts` hanya ditulis node `Update to STATS` yang berada di cabang TRUE `IF Bot Mode Active` — persis keterbatasan yang sama seperti The Scholars. Kontak yang di-OFF-kan tidak pernah memperbaruinya. Yang tetap terisi di kedua cabang adalah `buffer_done_ts` (`Mark Buffer Consumed (Bot_Off)` dan `(Regular)`). Dokumen PCR lama menyiratkan "beda dari Persada" seolah Persada aman — itu keliru.

Terkait: [[persada-cisoka-residence]]
