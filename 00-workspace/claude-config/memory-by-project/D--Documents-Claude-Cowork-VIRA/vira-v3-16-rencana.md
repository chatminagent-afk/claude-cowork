---
name: vira-v3-16-rencana
description: "VIRA v3.16 DIBANGUN 27/09 (sapaan tawaran deck, 3 pertanyaan, volume ilustrasi*, FU v2.2) — UAT 1035/0, eval 353/354; menunggu Steven deploy 28/09 + UAT manual"
metadata:
  node_type: memory
  type: project
  originSessionId: dd84563f-97fe-4632-b235-3edfe51f0e6e
  modified: 2026-09-27T14:42:07.838Z
---

Review 2026-09-27 (sesudah v3.15 live 08:42): `VIRA Steven/docs/2026-09-27-review-v3.15-rencana-v3.16.md`, dan panduan ringkasnya sudah dikirim ke WA 6285155202354 lewat API Kirimi. (v3.16 dibangun malam itu juga, lihat Update di bawah.)

Bukti live (sheet, karena layar WA ter-mask: jendelanya dirender `msedgewebview2.exe` dan izinnya ditolak Steven):
- Aldo (2156157472776, lid-only): sudah 11 pesan tapi tidak pernah ditawari deck. Sebabnya `tawaranBoleh()` di Rakit Konteks mensyaratkan `tahu('industri')`, sementara jawabannya masuk `nama_bisnis`.
- Dennis (62818687987): pesan "mau tanya untuk pricing nya" tidak terbaca sebagai tanya harga karena `KATA_HARGA` tidak memuat "pricing". Akibatnya guard RINGKAS memotong jawaban harga, dan kalimat itu tersimpan sebagai `industri`.
- Arjunn: "belum ada usaha..." ikut tersimpan sebagai `industri`.

Keputusan Steven untuk v3.16: opener menawarkan deck + "ngobrol sama Steven", sesudah "iya" langsung tanya bidang, pertanyaan dipangkas jadi 3–4 tanpa jumlah chat, sisanya pakai default. Usulanku: teks opener dikunci kode, 3 pertanyaan (bidang → nama usaha → masalah), dan "iya" sesudah opener jangan sampai terbaca TAWARAN_DISKUSI.

Update 27/09 malam: Steven memutuskan **3 pertanyaan** (bidang → nama usaha → masalah; boleh 5 kalau perlu). FAQ dijawab singkat, lalu kembali ke deck. Follow-up v2.1 siap tempel: `workflow/2026-09-27-VIRA-Personal-Followup-v2.1.json`. Export MCP (`get_workflow_details`) MEMBUANG credential; workflow yang dibangun dari export live wajib dipulihkan credential-nya, dan cek "credential sama dengan live" di atas export MCP selalu lolos semu.

Update 27/09 malam — DIBANGUN (production tidak disentuh): Main `workflow/2026-09-27-VIRA-Personal-Main-v3.16.json` (9 node diubah, 84 identik), patch `_patch_2026-09-27.py`, UAT `_buat_uat_2026-09-27.py` → `_uat_2026-09-27.py` 1035/0 (134 DIGANTI), eval `_eval_2026-09-27.py` 353/354, FU v2.2 `_patch_followup_2026-09-27.py` (UAT 211/0), deck `buat_deck.py` ILUSTRASI_VOLUME=50 (uji 90/0, cadangan *.lama-2026-09-27). Panduan `docs/2026-09-27-panduan-deploy-v3.16.md`.
Pelajaran UAT/eval yang wajib diingat: (1) kalimat sapaan "Kalau mau langsung ngobrol sama Steven, bilang aja ..." terbaca TAWARAN_DISKUSI → "mau tanya dulu" = handover + bot OFF; dikecualikan per kalimat teks sapaan (CONFIG). (2) "tawaran lalu" = kalimat deck + kata menawarkan + tanda tanya (atau disusul "Mau?"), bukan sekadar kata "deck" — "Biar pas di cover decknya, ...?" bukan tawaran. (3) jaring RINGKAS lama memotong contoh konkret; dimatikan di giliran tiga pertanyaan. (4) STATS.deck_requested kini Y/T/lama dari Process All.deck_status; blok brief diam-diam tidak lagi menjadikan Y.

**Why:** Steven merasa v3.15 masih tidak bisa cepat membungkus lead menjadi deck request.

**How to apply:**
- Patch berikutnya dari v3.16 (bukan v3.15). Cek dulu apakah Steven sudah deploy (MCP tidak bisa membaca Main; minta konfirmasi / export).
- Volume kosong di deck = angka ilustrasi 50* (keputusan Steven 27/09), bukan slide dibuang.
- Follow-up live `THuHlao6hdnMtlL01vn_p` berbeda dari file lokal: pengaman WAKTU_LAMPAU tidak ada. Perbaiki dengan menempel v2.2 (dibangun dari live, pasang bersama Main v3.16) atau v2.1; jangan file v2 22/09.
- Gelombang FU pertama jatuh 28–29/09.

Terkait: [[vira-v3-15-tawaran-deck]], [[vira-ads-funnel-eval-2026-09-26]], [[vira-v3-11-deck-terkirim]], [[feedback-deck-field-kosong]]
