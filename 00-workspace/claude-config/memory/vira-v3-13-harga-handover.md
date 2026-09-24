---
name: vira-v3-13-harga-handover
description: "VIRA Personal v3.13 (2026-09-23) — harga hanya kalau ditanya, jawaban alur bukan tanya harga, sewa X = industri, handover langsung, notif singkat sesudah deck; UAT 885/0 + eval model asli; belum deploy"
metadata:
  node_type: memory
  type: project
  originSessionId: e8202ad0-144f-4558-a086-7f03c65972c1
  modified: 2026-09-23T07:48:25.349Z
---

Dibangun 2026-09-23 dari v3.12 (= live, ID Main tetap `AC65HeFegHFCFc5aY609u`). **Belum di-deploy** — panduan `docs/2026-09-23-panduan-deploy-v3.13.md` (ganti isi workflow live seperti v3.12, ID tetap).
Berkas: `workflow/_patch_2026-09-23b.py` → `2026-09-23-VIRA-Personal-Main-v3.13.json` (91 node, tanpa node baru; md5 `209432822771f95633ddbd6941eef793`); UAT generator `_buat_uat_2026-09-23b.py` → `_uat_2026-09-23b.py` **885/0** (log `2026-09-23-hasil-uat-v3.13.log`); eval `_eval_2026-09-23b.py` → `2026-09-23-hasil-eval-balasan-v3.13.md` (S6 Rehan, S7 handover singkatan). Eval bisa paralel (`--versi --ulang-ke --json`, lalu `--gabung`) dan `--putar-ulang` (rekaman model lewat kode baru, tanpa memanggil model).

**Why:** uji live Steven 23/09 13:22–14:06 ("Rehan", sewa raket padel) di v3.12: jawaban alur "harga dulu, trs…" dibaca tanya harga → VIRA mengutip catatan konteks + sebut Basic/Premium; "usahaku sewa raket padel" jadi nama_bisnis; "basic deh" sesudah deck terkirim → notif BRIEF DECK lengkap lagi; "kpn bs ngmng sm steven?" → tag keluar tapi bot tidak OFF & VIRA tanya "mau aku sambungkan?".

**Keputusan Steven 2026-09-23:** gabung semua ke v3.13; permintaan bicara yang jelas → langsung disambungkan (bot OFF + konfirmasi); sesudah deck terkirim cukup notif singkat "UPDATE PROSPEK" (isian baru / perubahan komersial saja).

**Hasil eval (v3.12 ×1 vs v3.13 ×3):** harga tanpa diminta 1→0; handover singkatan 0/1→3/3; nama usaha 5/6→18/18; STATS Rehan benar 3/3. Temuan eval yang ikut diperbaiki: galian ditempel untuk kolom yang baru terisi; minta deck dibalas tawaran deck; [FACTS nama_bisnis="persewaan"] (FACTS selalu menang) → kini jenis usaha dari model tidak jadi nama.

**How to apply:**
- Preprocess kini membaca `Resolve User Row.last_bot_reply` (try/catch) → `JAWAB_PERTANYAANKU`; keluaran baru `hargaBukanTanya` dipakai jaring HARGA di Process All.
- Nama usaha dagangan: "sewa/persewaan X" huruf kecil = industri; semua kata huruf besar ("Sewa Raket Padel") = nama merek. "rental"/"jasa" sengaja tidak masuk DAGANGAN.
- NIAT_BICARA di Process All & salinannya di Rakit Konteks harus identik (UAT V12d).
- Heredoc bash di mesin ini memakan backslash (`\\b`→`\b`, `\\n`→newline) — edit JS/regex pakai tool Edit, bukan heredoc Python.
- Terbuka: pesan "kpn y bs ngmngnya?" 14:00 tidak pernah masuk MSG_BUFFER — butuh log eksekusi n8n 66435 (panel browser Claude belum login n8n).
- Deferred: model kadang bertanya langkah sesudah prospek menjelaskan alur (dalam konteks lain), dan tawaran deck + satu pertanyaan (2 tanya) lolos karena LEWATI_RINGKAS.

Terkait: [[vira-v3-12-balasan-ringkas]], [[vira-personal-main-tidak-terbaca-mcp]], [[feedback-vira-balasan-ringkas]]
