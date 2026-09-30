---
name: miva-v3-18-funnel-fix
description: "MIVA v3.18 + FU v2.4 DIBANGUN 29/09 (DEPLOY 29/09: Main & FU ditempel Steven, sheet 17 sel ditulis 16:22): sapaan tanya bidang, tawaran deck maks 1x/3 balasan, T/P, FAKTA API, [unknown] drop+notif, stiker; UAT 1166/0, FU 235/0, eval 254/255, + lead_source Threads"
metadata:
  type: project
---

Dibangun 29/09 dari evaluasi [[miva-funnel-eval-2026-09-29]] + keputusan Steven. Production TIDAK disentuh (live = Main v3.17, FU v2.3; dicek MCP 29/09 identik file lokal).
File: `workflow/2026-09-29-MIVA-Personal-Main-v3.18.json` (95 node, +IF Pesan Tak Terbaca, +Notify Admin Tak Terbaca), `...-Followup-v2.4.json`, patch `_patch_2026-09-29.py`, UAT `_buat_uat_2026-09-29.py` + `_seksi_uat_AB_2026-09-29.py` -> `_uat_2026-09-29.py` (1166/0, 36 DIGANTI), lead_source Threads di Detect Lead Source + backfill STATS 2 baris, FU `_uat_followup_2026-09-29.py` (235/0), eval `_eval_2026-09-29.py`, sheet 17 sel DITULIS 29/09 16:22 (skrip dihapus atas permintaan Steven; cadangan `2026-09-29-cadangan-sheet-sebelum-v3.18.json`), panduan `docs/2026-09-29-panduan-deploy-v3.18.md`.

Keputusan Steven 29/09: FAQ API unofficial; hanya teks/media diproses, stiker = teks "tidak paham", reaksi & disappearing tidak diproses; notif panas tanpa "Mau"/biaya pihak lain; semua usulan 1-7 disetujui (FAQ saja tidak cukup -> + guard kode).

Fakta teknis penting:
- Kirimi mengirim pesan disappearing & reaksi sebagai teks literal "[unknown]" (bukti MSG_BUFFER), bukan messageType reaction.
- Status deck_requested kini Y / T (tolak, bukan calon) / P (penasaran-ngulik, gugur saat bidang/nama usaha tercatat). FU skip T & P.
- Jeda tawaran pakai static data `tawarDeck[lead]={g,ts}` (ditulis Process All, dibaca Rakit Konteks). Harness eval lama (E.SHIM) TIDAK menyimpan static data -> pakai shim v3.18 di _eval_2026-09-29.py.
- Bug lama ketemu UAT: "bisa jawab stok juga?" sesudah tawaran = setuju deck (setujuPendek tanpa cek tanya) -> diperbaiki.
- Nabil 6285722108932 minta deck 28/09, belum dikirim (backlog).

**How to apply:** patch berikutnya dari v3.18 kalau sudah dideploy (cek MCP). Sesudah deploy wajib UAT manual langkah 8-9 (disappearing/reaksi) karena payload mentah belum pernah dilihat.

**Update 29/09 sore: LIVE.** Dicek MCP: Main updatedAt 16:18 WIB (95 node identik v3.18), FU 16:19 (27 node identik v2.4). Credential tidak terbaca MCP. Sheet 17 sel ditulis 16:22 (dicek langsung). Belum: UAT manual langkah 8-10 (disappearing, reaksi, Threads) di nomor uji.
