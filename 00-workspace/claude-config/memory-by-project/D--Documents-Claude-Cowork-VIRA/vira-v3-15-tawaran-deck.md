---
name: vira-v3-15-tawaran-deck
description: "VIRA v3.15 (26/09) — sapaan tanya bidang saja, bidang diketahui → contoh konkret + tawaran deck, notif LEAD PERLU DIBALAS; LIVE per 2026-09-27 (dicek MCP)"
metadata:
  node_type: memory
  type: project
  originSessionId: 482a6106-463b-4e81-bf4b-8d74b6e30a77
  modified: 2026-09-26T17:11:56.735Z
---

v3.15 dibuat 2026-09-26 dari v3.14 (v3.14 sendiri belum pernah live; live = v3.13). File: `workflow/2026-09-26-VIRA-Personal-Main-v3.15.json`, patch `_patch_2026-09-26.py`, UAT `_uat_2026-09-26.py`, eval `_eval_2026-09-26.py`, panduan `docs/2026-09-26-panduan-deploy-v3.15.md`. BELUM DEPLOY (production tidak disentuh).

**Update 2026-09-27: LIVE.** Dicek via n8n MCP `get_workflow_details`: Main `AC65HeFegHFCFc5aY609u` updatedAt 2026-09-27 08:42 WIB, 93 node — parameter semua node identik dengan file v3.15 (v3.13/v3.14 beda 6 node). Token khas v3.14 (TANYA_HARGA_POLOS, BUKAN_NAMA_ORANG, kataNamaFacts) ikut ada → v3.14 ikut live lewat v3.15. Patch berikutnya dari v3.15.

Keputusan Steven 2026-09-26:
- Sapaan hanya menanyakan BIDANG usaha (nama & nama usaha tidak di awal).
- Waktu balas Steven ke lead = "secepatnya saat sudah available" (bukan "belum bisa pastikan").
- Sidon / 851-7170-1168 = nomor uji Steven, abaikan di analisis lead.

Desain: bidang diketahui → 1 kalimat contoh konkret + tawaran deck + nama usaha di kalimat yang sama (suntingan tangan Steven di prompt live, pola Ziel). Jawaban nama usaha atas tawaran = setuju. Sesudah setuju: nama usaha → masalah → nama (sekali). Notif baru "🔥 LEAD PERLU DIBALAS" (node IF Lead Panas → Notify Admin Lead Panas) saat VIRA menjanjikan tindak lanjut Steven atau lead tanya harga/ratecard; jeda 24 jam per lead per alasan.

Jebakan yang ketemu di UAT: kalimat sapaan "ngobrol **langsung** sama contohnya" terbaca TAWARAN_DISKUSI → "boleh ..." memicu handover + bot OFF. Kalimat perkenalan kini dibuang dari gerbang itu.

Follow-up live (config sheet 26/09): followup_enabled TRUE, dry_run N, interval_hours_a = 72, max_a = 3 → lead yang diam sesudah sapaan baru disapa 3 hari kemudian. Usulan 12 jam / maks 2 belum diterapkan (butuh izin Steven).

Terkait: [[vira-ads-funnel-eval-2026-09-26]], [[vira-v3-14-brp]], [[feedback-deck-field-kosong]]
