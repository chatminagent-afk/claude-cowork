---
name: vira-v3-14-brp
description: "VIRA Personal v3.14 (2026-09-25) — 'Brp' polos = tanya harga (catatan konteks tegas), kata tanya tak pernah jadi nama (penangkap + [FACTS]), tanya-ulang tak bikin balasan buntu saat prospek bertanya; UAT 943/0 + eval asli; belum deploy"
metadata:
  node_type: memory
  type: project
  originSessionId: 3dd12ee3-5c39-4da1-ab11-f7bcc8807576
  modified: 2026-09-25T07:50:07.796Z
---

Dibangun 2026-09-25 dari v3.13 (= live, dibuktikan field `hargaBukanTanya` di output Process All live). **Belum di-deploy** — panduan `VIRA Steven/docs/2026-09-25-panduan-deploy-v3.14.md` (ganti isi workflow live, ID `AC65HeFegHFCFc5aY609u` tetap).
Berkas: `workflow/_patch_2026-09-25.py` → `2026-09-25-VIRA-Personal-Main-v3.14.json` (91 node, 4 berubah: Preprocess, AI Agent, Process All, Rakit Konteks; md5 `7186743b1883cb14d5fe175c88b1fb1b`); regresi S1–S7 ×3 → `2026-09-25-hasil-eval-regresi-v3.14.md` (putar silang 0 beda); UAT `_buat_uat_2026-09-25.py` → `_uat_2026-09-25.py` **943/0** (seksi X = replay insiden Reza, seksi R = bedah vs v3.13); eval `_eval_2026-09-25.py` → `2026-09-25-hasil-eval-brp-v3.14.md` (+ `--putar-ulang`, `--regresi`).

**Why:** live 25/09 prospek iklan IG "Reza" (6285199701359) membalas sapaan nama+usaha dengan "Brp" → terkirim "Salam kenal kak." saja, STATS nama_lengkap = "Brp" (belum dibersihkan — langkah di panduan deploy).

**How to apply:**
- Eval model asli membuktikan: pengecualian di prompt SAJA tidak cukup. Catatan konteks yang ragu ("Sepertinya… Periksa dulu") kalah oleh aturan prompt "satu kata = jawaban" + baris SYSTEM_DATA "pesan prospek adalah tanggapan atas kalimat itu" (3/4 balasan "Itu jawaban untuk pertanyaan nama… atau nanya harga?"). Kasus yang tidak ambigu → catatan konteks TEGAS (10/10 lolos).
- UAT pola "reproduksi dulu": `di_v313()` menjalankan kode versi lama → cek harus mereproduksi output live persis, baru kode baru harus lolos. Eval: giliran 1 dipaksa = teks live persis (`PAKSA_SAPAAN`).
- Desain v3.13 dipertahankan: kalau prospek MENJAWAB, tanya-ulang tetap membuang pertanyaan kembar walau sisanya "Noted kak." (UAT W2/W7/V11b). Pengaman buntu hanya saat PROSPEK_BERTANYA.
- `BUKAN_NAMA_ORANG` ada di blok PENANGKAP (identik 2 node) dan dipakai juga untuk [FACTS nama] (ditolak hanya kalau SEMUA katanya ada di daftar).

Terkait: [[vira-v3-13-harga-handover]], [[vira-personal-main-tidak-terbaca-mcp]], [[feedback-vira-balasan-ringkas]]
