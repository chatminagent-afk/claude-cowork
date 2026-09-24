---
name: vira-v3-11-deck-terkirim
description: "VIRA v3.11 (2026-09-22) — VIRA tahu decknya sudah terkirim lewat kolom STATS deck_terkirim_ts + Follow-up v2 berbucket; UAT 551/0 & 204/0, live 2026-09-23"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb57da45-1acc-4523-a82c-c287bd097fa8
  modified: 2026-09-22T06:13:55.928Z
---

Dibangun 2026-09-22. **Live** — Main identik v3.11 & Follow-up v2 aktif (dicek via MCP 2026-09-23). Patch berikutnya: [[vira-v3-12-balasan-ringkas]]. Panduan: `VIRA Steven/docs/2026-09-22-panduan-deploy-v3.11.md`.

**Kolom baru `STATS.deck_terkirim_ts`** (epoch detik, kolom ke-33, paling kanan) ditulis `kirim_deck.py` hanya pada kiriman ke KLIEN. Ini kunci seluruh patch: workflow Main tidak pernah membaca tab REQUESTS, jadi `REQUESTS.deck_dikirim_ts` yang sudah ada tidak bisa dipakai. Dua nama sengaja dibedakan — REQUESTS pakai string WIB (catatan untuk Steven), STATS pakai epoch (dibaca mesin, ikut konvensi `*_ts` lain).

**Why:** sebelum ini VIRA terus bilang briefnya "baru diteruskan" dan decknya "sedang disusun" padahal PDF-nya sudah di tangan prospek, dan tidak tahu caption-nya meminta prospek mengabari condong Basic atau Premium.

**How to apply:**
- Kolom baru di UJUNG STATS ikut terbawa gratis: `Resolve User Row` mengembalikan `userRow: {...row}` dan `Rakit Konteks` membacanya apa adanya → nol perubahan di dua node itu. Semua node Sheets penulis pakai `mappingMode: defineBelow`, jadi kolom yang tidak dipetakan tidak tertimpa.
- v3.11 = v3.10 + sisipan di 3 node (`Rakit Konteks` blok `deck_context`, `AI Agent` bagian `# DECK`, `Process All` gerbang `TAWARAN_DISKUSI`). Murni sisipan — regresi membuktikan tidak ada satu baris v3.10 pun yang hilang, selain satu baris `mintaBicara` yang memang diganti.
- `TAWARAN_DISKUSI` adalah cermin `TAWARAN_DECK`+`SETUJU_PENDEK` yang sudah ada: prospek menjawab "boleh" atas tawaran diskusi tidak memuat satu pun kata di `NIAT_BICARA`, jadi tanpa gerbang ini `matikanBot` tidak pernah true. Dipromosikan jadi `isTalkToAdmin` walau model lupa menulis tagnya.
- **Follow-up v2** (`2026-09-22-VIRA-Personal-Followup-v2.json`, 25 node) di-fork dari Persada 2026-09-16, BUKAN dari file Personal 2026-08-28. Model pakai **DeepSeek** (`tVKwMVPK1fROjH5Z`) — tenant ini tidak punya kredensial Anthropic. Tiga bucket dari kolom: A (belum minta deck), B (sudah minta, deck belum dikirim — **prospeknya tidak dikirimi apa pun**, Steven yang ditegur lewat node `Backlog Deck`), C (deck sudah terkirim).
- Bug yang diperbaiki saat fork: `followup_max` di file lama berarti kebalikannya (0 = nol orang di-follow-up, bukan tanpa batas).
- Follow-up menulis `last_bot_reply` lewat node `Catat Balasan FU` (hanya kalau bukan dry run). Bukan sekadar soal ingatan: `TAWARAN_DECK` dan `TAWARAN_DISKUSI` di Process All membaca kolom itu, jadi tanpa ini "boleh" atas tawaran di follow-up tidak memicu brief maupun handover. `last_reply_ts` sengaja tidak disentuh (acuan jam diam Filter Kandidat).
- `Backlog Deck` sengaja menggantung dari `Read STATS FU`, bukan dari cabang done `Loop Kandidat` — splitInBatches tidak menjalankan cabang done kalau kandidatnya kosong, dan run tanpa kandidat justru yang paling mungkin masih punya backlog.

**Hasil uji:** `_uat_2026-09-22.py` 551/0 (491 di antaranya regresi lama), `_uat_followup_2026-09-22.py` 204/0, `uji_konsistensi.py` 87/0.

Terkait: [[vira-v3-10-nama-usaha-ringkas]], [[feedback-vira-nama-tidak-menyapa]], [[vira-followup-belum-live]], [[vira-personal-main-tidak-terbaca-mcp]]
