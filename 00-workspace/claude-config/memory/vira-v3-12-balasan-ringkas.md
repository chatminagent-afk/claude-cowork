---
name: vira-v3-12-balasan-ringkas
description: "VIRA Personal v3.12 (2026-09-23) — balasan to the point: prompt + jaring RINGKAS + penangkap fakta; UAT 732/0, eval model asli 5 putaran; LIVE 2026-09-23 12:19 WIB (dicek MCP)"
metadata:
  node_type: memory
  type: project
  originSessionId: 7467153e-4fcc-431f-bf7f-eb7241ff3d80
  modified: 2026-09-23T04:22:35.997Z
---

Dibangun 2026-09-23 dari v3.11 (live = v3.11 identik, dicek via MCP). **LIVE sejak 2026-09-23 ±12:19 WIB** — dicek MCP: 91 node, parameter & koneksi identik dengan file lokal, ID workflow tetap `AC65HeFegHFCFc5aY609u` (Steven menempel node ke workflow lama). Satu-satunya beda: `settings.errorWorkflow` live = `0mp_AdLtInm68RxQUwLqV` (GLOBAL notifier, benar), file lokal masih `P_ECOTzcz99B1siU-BcDW` — patch berikutnya samakan ke `0mp_`.
Berkas: `workflow/_patch_2026-09-23.py` → `2026-09-23-VIRA-Personal-Main-v3.12.json` (91 node), UAT `_uat_2026-09-23.py` 732/0 (generator `_buat_uat_2026-09-23.py`), eval model asli `_eval_2026-09-23.py` → `2026-09-23-hasil-eval-balasan.md`. Panduan: `docs/2026-09-23-panduan-deploy-v3.12.md`.

**Why:** uji Steven 23/09 ("abdul", parfum) — tiap balasan = rangkuman + promosi VIRA + pertanyaan (28–60 kata), dan VIRA menanyakan lagi yang sudah dijawab. Prompt v3.10 sendiri yang mendorongnya ("satu kalimat menanggapi + tambah satu hal dari sisi VIRA").

**Keputusan Steven 2026-09-23:** promosi VIRA hanya kalau ditanya + satu kalimat di tawaran deck; jaring pengaman deterministik di kode DISETUJUI (membalik [[feedback-vira-balasan-ringkas]] "panjang hanya lewat prompt"). Temperature tetap 0.7 ([[vira-temperature-jangan-diturunkan]]).

**How to apply:**
- Eval model asli WAJIB untuk patch perilaku: UAT hijau tapi putaran eval menemukan 6 cacat baru (galian dilewati, minta deck dibalas tawaran, nama usaha "makasih", dll). Butuh workflow `VIRA Eval — Balasan (sementara)` aktif di n8n (DeepSeek key hanya ada di credential n8n, tidak terbaca MCP).
- Blok `PENANGKAP JAWABAN — MULAI/SELESAI` identik di Process All & Rakit Konteks; regex minta-deck di Rakit Konteks disalin dari Process All — UAT V8/V12d memeriksa.
- Jaring RINGKAS: gema → sudah-tahu → satu-tanya → panjang → ekor, lalu tanya-ulang (galian dikecualikan) dan perkenalan; balasan cuma tag → pertanyaan galian. Log event `RINGKAS` di EVENTS.
- Harness V8 di Windows tidak exit sendiri; pakai runner subprocess / `os._exit` sesudah `sys.stdout.flush()`.

**Temuan uji live Steven 2026-09-23 ("Rehan", sewa raket padel) — kandidat v3.13, belum dikerjakan:**
- Jawaban alur "harga dulu, trs klo udah aman baru ke payment" menyalakan `askingPrice` di Preprocess (KATA_HARGA polos, tak ada pengecualian untuk cerita alur) → model membocorkan catatan konteks ("bukan nanya harga VIRA", "yang dia ceritakan") + menyebut harga tanpa ditanya. Jaring RINGKAS tidak jalan karena LEWATI_RINGKAS (Rp/basic/premium); tanya-ulang membuang satu-satunya pertanyaan yang relevan. Giliran berikutnya ("okee") VIRA menanyakan lagi alur yang sudah dijawab.
- `ambilNamaDanUsaha`: "usahaku sewa raket padel" → nama_bisnis (seharusnya industri; JENIS_USAHA/DAGANGAN tak kenal sewa/persewaan). `EKOR` hanya membuang satu kata → industri "persewaan aja".

Terkait: [[vira-v3-11-deck-terkirim]], [[vira-personal-main-tidak-terbaca-mcp]]
