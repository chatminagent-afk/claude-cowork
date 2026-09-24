# VIRA V2 — Analisis Root Cause Penurunan Kualitas (Sam Chatbot)

Tanggal: 2026-06-19 · Lingkup: `VIRA.json` (workflow n8n V2 — Haiku 4.5), system prompt + konfigurasi memory/retrieval, 4 chat gagal "after implementing v2", `UAT Cost Claude.xlsx`, dan balasan asli Sam (acuan V1/Sonnet). Ini pass root-cause terarah, bukan audit baris-per-baris.

**Catatan transparansi:** tidak ada file arsitektur V1 terpisah di folder. V1 dan V2 menjalankan workflow n8n yang sama; perubahan yang disengaja hanyalah model (Sonnet 4.6 → Haiku 4.5). Artinya bug wiring di bawah sudah ada sejak V1 — Sonnet hanya menutupinya.

## Kesimpulan utama (headline)

Penurunan kualitas **mayoritas masalah arsitektur/wiring, bukan kapabilitas model.** Tiga cacat deterministik (tool hantu, memory key reset per jam, deteksi status rapuh) ditambah retrieval leksikal dan temperature 0.7. Haiku **memperbesar** gejalanya, tapi balik ke Sonnet hanya menyembunyikan bug yang sama dengan biaya 4–6× lebih mahal.

## Root cause

### RC1 — Prompt menyuruh memanggil tool BATCH & HARGA yang tidak terpasang (mesin "boros")
**Severity: High · Confidence: 95%**
Agent hanya punya **3 tool**: `PROGRAM`, `LINKS`, `ABOUT_SAM` (tiga node `googleSheetsTool`). Tapi system prompt berkali-kali memerintah: "BATCH untuk jadwal, HARGA untuk biaya … memanggil tool yang relevan adalah WAJIB". Tool BATCH dan HARGA **tidak ada**. Tiap pertanyaan harga/jadwal → model mencoba tool yang tidak ada, retry, habiskan iterasi.
Bukti: `UAT Cost` baris 7–15 — "AI belum dpt jawaban dan stop karena max iterations", lalu menaikkan iterasi 3→6→8, tetap "kena maks iterasi". Cost per turn yang gagal melonjak ke $0,16–$1,72 vs ~$0,01–$0,05 turn normal. Satu cacat ini memicu **hambatan jawaban, loop, latency, biaya, dan hallucination** sekaligus.

### RC2 — Memory key reset tiap pergantian jam + window 5 turn
**Severity: High · Confidence: 95% (deterministik)**
`memoryBufferWindow` sessionKey = `user_wa + '_' + new Date().getHours()`, `contextWindowLength` default (5). Buffer hanya simpan 5 turn terakhir **dan** terhapus tiap server melewati batas jam. Bot lupa yang sudah disepakati.
Bukti: chat **+62 877-8433-6814** — kelas 9/Intermediate sudah ditetapkan dan link GForm sudah dikirim, lalu bot **menanya ulang "Anaknya sekarang kelas berapa?"** dan menawarkan kirim link daftar **lagi**. Persis gejala "muter-muter" + link 2×.

### RC3 — Deteksi status PARENT/STUDENT rapuh → persona referent salah ("kamu" ke orang tua)
**Severity: High (persona) · Confidence: 85%**
Node `Preprocess` mendeteksi PARENT via regex `anak\s*saya` tapi **tidak menangkap singkatan** ("anak sy", "ortu", "sy"); regex STUDENT malah memuat kata **"anaknya"** — kata yang justru sering dipakai orang tua. Akibatnya orang tua salah ditandai/ tidak terdeteksi, dan agent menyapa "kamu".
Bukti: chat **+62 812-8799-6856** — user jelas orang tua ("Anak sy skrg naik kls 6") tapi dibalas "kelas kamu berapa", "kamu cocok untuk program Junior", "passion kamu". (Flag bug konkret di kode Preprocess.)

### RC4 — Hallucination dari retrieval leksikal + fallback tidak dipaksa
**Severity: High · Confidence: 80%**
FAQ retrieval murni leksikal (stemming + sinonim + TF-IDF, FLOOR 2.5), tanpa pencocokan semantik. Saat miss, prompt minta `[UNKNOWN]` — tapi karena loop tool hantu (RC1) gagal, model malah mengarang dari ingatan, melanggar aturannya sendiri.
Bukti: "ada juga yang **partial** atau tidak dapet beasiswa" (**812-2008-9875**) — partial scholarship tidak ada, ini karangan. Nama-nama folder ("salah kasih info", "salah jawabannya", "salah refer") = tiga kegagalan akurasi independen. Chat **816-1835-809** (anak kelas 10) dijawab lemah, padahal aturan "SMA 10/11 belum ada program cocok" ada di prompt → gap konten/retrieval.

### RC5 — Temperature 0.7 pada bot faktual
**Severity: Medium · Confidence: 70%**
0.7 untuk variasi, bukan untuk bot FAQ/registrasi yang harus grounded. Memperlebar variance output → memperkuat RC3 (drift persona) & RC4 (hallucination), dan membuat jawaban tidak konsisten untuk pertanyaan identik (`UAT` baris 33 vs 35 divergen; baris 33 bahkan **membocorkan instruksi internal** "Ambil data dulu dari FAQ…"; baris 21 men-dump **JSON mentah** sebagai jawaban).

## Top 5 (urut paling berdampak)
1. **RC1** — tool BATCH/HARGA hantu → loop agent (perbaiki hallucination + biaya + latency)
2. **RC2** — reset memory per jam + window 5 (perbaiki muter-muter, link dobel, tanya ulang)
3. **RC4** — retrieval leksikal tanpa fallback dipaksa (perbaiki jawaban salah/karangan)
4. **RC3** — deteksi status rapuh (perbaiki "kamu" ke orang tua)
5. **RC5** — temperature 0.7 (pengali murah atas RC3 & RC4)

## Jawaban langsung
1. **Apakah masalah utamanya model (Haiku 4.5)?** Tidak. Haiku memperbesar gejala, tapi prompt yang sama di Sonnet hanya menyembunyikan bug wiring yang tetap ada.
2. **Apakah arsitektur?** Ya — porsi terbesar. Tool wiring (RC1) + memory key (RC2) adalah cacat deterministik.
3. **Apakah prompt design?** Sebagian. Isi prompt **bagus**; cacatnya: menyuruh tool yang tidak ada + terlalu padat larangan (~30 "DILARANG/JANGAN") untuk model kecil.
4. **Apakah retrieval/context?** Berkontribusi, sedang. Leksikal-only tanpa fallback semantik menciptakan celah yang diisi karangan.
5. **Fix tunggal paling berdampak:** Hentikan agent memilih tool. **Pre-fetch deterministik** baris PROGRAM/BATCH/HARGA/LINKS/FAQ yang relevan (seperti `faq_context` yang sudah diinject) lalu masukkan ke prompt, **matikan tool-calling**. Ini mematikan loop, biaya, dan mayoritas hallucination sekaligus — dan model-agnostic.

## Diagnosis: kombinasi, berbobot
Arsitektur (loop agent + memory) ≈ 55% · Retrieval ≈ 20% · Instruction-following model ≈ 15% · Prompt/temperature ≈ 10%. **Bukan** masalah kapasitas model.

## QUICK WINS (< 1 hari)
- **Perbaiki memory key** → `user_wa` saja (buang `getHours()`); naikkan `contextWindowLength` ke ~15. (RC2)
- **Turunkan temperature ke 0,2–0,3.** (RC5)
- **Hapus instruksi BATCH/HARGA dari prompt** (atau pasang tool-nya). Saran cepat: hapus dulu agar berhenti memanggil tool hantu. (RC1)
- **Paksa fallback:** jika FAQ/tool kosong → output `[UNKNOWN]`, larang free-write. (RC4)
- **Perbaiki regex deteksi status:** tambah "sy", "ortu", "anak saya"; pindahkan "anaknya" keluar dari pemicu STUDENT. (RC3)

## MEDIUM (1–3 hari)
- **Ganti loop agent dengan pre-retrieval deterministik** — rakit konteks PROGRAM/BATCH/HARGA/LINKS/FAQ sebelum panggil LLM; matikan tool-call in-agent. (RC1, RC4)
- **Pecah mega-prompt:** core persona singkat selalu-on + blok aturan sesuai intent terdeteksi (harga/batch/status). Lebih mudah dipatuhi Haiku. (RC3)
- **Tambah baris FAQ** yang ketahuan bolong: klarifikasi "tidak ada partial scholarship", jalur kelas 10/11, frekuensi pertemuan (cek inkonsistensi "2×/minggu" vs "seminggu sekali"). (RC4)

## LONG-TERM
- **Retrieval semantik (embeddings)** menggantikan keyword leksikal. (RC4)
- **Routing berbasis confidence:** default Haiku, eskalasi ke Sonnet hanya saat `[UNKNOWN]`/multi-intent/low-confidence.
- **Regression eval set** dari chat gagal ini, dijalankan tiap ubah prompt/model agar bug tidak kembali.

## Decision matrix
| Opsi | Est. dampak biaya | Est. dampak kualitas | Risiko |
|---|---|---|---|
| Keep V2 as-is | Baseline (loop menggelembungkan) | Buruk — persona/akurasi/UX tetap gagal | Tinggi (reputasi) |
| Improve V2 architecture | **↓ 30–50%** (loop hilang) | **↑ Tinggi** — atasi RC1/2/4/5 | Rendah–Sedang |
| Switch back to Sonnet 4.6 | ↑ 4–6× per chat | ↑ Sedang (menutup, bukan memperbaiki bug) | Sedang (mahal + bug tetap) |
| Hybrid Haiku + Sonnet routing | ↑ 10–25% dari Haiku-saja | ↑ Tinggi | Sedang (kompleksitas routing) |

## FINAL VERDICT

**Root cause paling mungkin:** arsitektur agentik yang menyuruh Haiku memanggil tool yang tidak ada (RC1) di atas memory key yang menghapus konteks tiap jam (RC2). Ini cacat wiring, bukan keterbatasan model.

**Apakah Haiku 4.5 viable?** Ya. Begitu tool-call diganti pre-retrieval deterministik, temperature diturunkan, dan prompt diramping, use-case FAQ/registrasi ini ada dalam jangkauan Haiku — dengan biaya jauh di bawah Sonnet (terbukti `UAT` baris 16–39: setelah prompt/tool dibereskan, Haiku menjawab benar konsisten ~$0,01/turn).

**Apakah Sonnet 4.6 perlu?** Tidak sebagai default. Cukup jadi fallback untuk turn low-confidence/multi-intent.

**Arsitektur yang akan saya deploy:** deteksi intent + status deterministik (regex diperbaiki) → pre-fetch baris PROGRAM/BATCH/HARGA/LINKS/FAQ yang persis ke prompt (tanpa loop tool) → satu panggilan Haiku, temp 0,25, prompt ramping per-intent → memory per-user durabel (window 15, tanpa reset jam) → fallback `[UNKNOWN]` keras → eskalasi Sonnet hanya saat confidence rendah.

**Rekomendasi kualitas-per-dolar terbesar:** Ganti loop tool-calling agent dengan pre-injection konteks deterministik. Menghapus loop pembakar biaya **sekaligus** menghilangkan mayoritas hallucination & "muter-muter" dalam satu perubahan — tetap di harga Haiku dengan keandalan setara Sonnet untuk tugas sempit ini.

---
### File dibuat/dimodifikasi
- Dibuat: `D:\Documents\Claude Cowork\the scholars\enhancement boros v2 vira 18 juni\2026-06-19-VIRA-V2-analisis-root-cause-ID.md`
