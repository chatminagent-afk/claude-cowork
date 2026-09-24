# Fix: False-Handover saat User Jawab "boleh" atas Tawaran MEDIA — VIRA PCR

**Tanggal:** 2026-07-24
**Target file:** `workflow/production/VIRA-PCR Main V1.4.json` (copy V1.3 + 2 edit prompt) → node `AI Agent`, field `systemMessage`
**Status:** APPLIED ke `Main V1.4.json` (2026-07-24) — versi LEAN (2 rewrite, blok baru dibuang demi hemat token). Sisa: Steven review + import ke n8n live + jalankan QA suite §4.
**Catatan token:** net ~+25 token (rewrite 2 baris existing, bukan blok baru). V1.4 = V1.3 dengan 88 node & 64 koneksi identik, hanya `systemMessage` yang berubah (terverifikasi).
**Terkait:** Pending Waiting Changes #23 (false-handover fallback frasa — beda lapisan, sudah fix di kode) & #25 (entri ini)

---

## 1. Bug yang diamati (transkрip nyata 2026-07-24)

```
VIRA (14:09): ...mau saya kirimkan foto & video unitnya? Tinggal sebut tipe yang kakak minati ya 😊
User (14:42): ya boleh
VIRA (14:45): Baik Kak Ivan, saya sambungkan ke tim marketing kami yaa, mohon ditunggu sebentar.  ← [TALK_TO_ADMIN]
```

User menyetujui tawaran **foto/video**, tapi VIRA malah handoff ke admin. Padahal permintaan media 100% masih scope VIRA (jalur `[SEND_MEDIA]`).

## 2. Akar masalah (dua lapis, keduanya di PROMPT — bukan kode)

Beda dengan #23 (fallback frasa di `Process All` yang meng-override AI). Di sini **AI sendiri** yang memutuskan pasang `[TALK_TO_ADMIN]`. Penyebab:

**Lapis A — tabrakan token "boleh".** Blok `# ESKALASI` menuliskan:
> "[TALK_TO_ADMIN] HANYA dipasang kalau user SENDIRI menyatakan mau (**"boleh"**, "iya mau", "sambungin dong")..."

Kata **"boleh"** di-hardcode sebagai token penerimaan handoff, tanpa syarat "apa yang barusan ditawarkan". Blok `# TAG` memperkuat: *"[TALK_TO_ADMIN] -> ... ATAU mengiyakan tawaranmu (# ESKALASI)"* — model membaca "ya boleh" sebagai "mengiyakan tawaranmu" secara generik. Balasan bug-nya bahkan hampir menyalin contoh verbatim di prompt: *"[TALK_TO_ADMIN] Baik Kak, akan saya sambungkan ke tim marketing kami yaa, mohon ditunggu."* Tidak ada satu pun instruksi yang bilang "boleh atas tawaran foto/video = `[SEND_MEDIA]`".

**Lapis B — sumber ambiguitas: VIRA menawarkan media sebagai pertanyaan ya/tidak.** Tawaran VIRA *"mau saya kirimkan foto & video unitnya?"* adalah pertanyaan ya/tidak untuk aksi — yang justru **dilarang** blok `# LARANGAN` (*"Pertanyaan ya/tidak untuk AKSI ('boleh saya kirim brosurnya?')"*). Pertanyaan ya/tidak inilah yang memancing jawaban telanjang "ya boleh" yang ambigu. Kalau tawaran media selalu berbentuk "mau tipe yang mana", jawaban user otomatis spesifik dan ambiguitasnya hilang di sumbernya.

## 3. Solusi (LEAN — 2 rewrite di systemMessage, tanpa blok baru, tanpa sentuh kode/node)

Prinsip: keputusan tag atas jawaban setuju telanjang ("boleh/iya/mau") harus jadi **fungsi dari apa yang VIRA tawarkan di pesan sebelumnya**. Karena arsitektur VIRA tag-driven tanpa tool, keputusan memang hidup di prompt — TAPI cukup dengan **rewrite 2 baris yang sudah ada**, bukan blok baru (blok besar dibuang demi hemat token; keputusan Steven 2026-07-24).

> **Kenapa bukan fix di kode `Process All`?** Guard kode harus menebak "pesan VIRA sebelumnya = tawaran media" lewat pencocokan frasa — itu persis fallback-frasa yang baru dibuang di register #23. Fix kode = mengulang anti-pattern yang sudah ditinggalkan. Handoff tetap tag-driven dari AI.

### EDIT 1 (Titik 1) — Rewrite kalimat pembuka `# ESKALASI` ← akar utama

**LAMA:**
```
Prinsip: menawarkan bantuan tim BUKAN eskalasi. [TALK_TO_ADMIN] HANYA dipasang kalau user SENDIRI menyatakan mau ("boleh", "iya mau", "sambungin dong"), atau user langsung minta ("saya mau booking", "mau nego"). Tawarkan maks 1x per topik.
```
**BARU (applied):**
```
Prinsip: menawarkan bantuan tim BUKAN eskalasi. Kalau user jawab setuju telanjang ("boleh"/"iya"/"mau"), ikuti tawaran TERAKHIRmu: tawaran foto/video/brosur -> [SEND_MEDIA] (BUKAN [TALK_TO_ADMIN]); survey -> # SURVEY; simulasi -> jawab dari DATA. [TALK_TO_ADMIN] HANYA saat user setuju tawaran menyambungkan ke TIM, atau minta sendiri ("mau booking", "mau nego", "sambungin dong"). Ragu atau kamu menawarkan >1 hal -> klarifikasi 1 pertanyaan, jangan default ke tim. Tawarkan maks 1x per topik.
```

### EDIT 2 (Titik 2) — Scope definisi `[TALK_TO_ADMIN]` di blok `# TAG` (token-neutral)

**LAMA:**
```
... ATAU mengiyakan tawaranmu (# ESKALASI), ATAU ...
```
**BARU (applied):**
```
... ATAU mengiyakan tawaran menyambungkan ke TIM (# ESKALASI, bukan tawaran foto/video/survey/simulasi), ATAU ...
```

### (Opsional, DI-SKIP) — Sumber ambiguitas Lapis B

VIRA menawarkan media pakai ya/tidak ("mau saya kirimkan?") yang memancing "ya boleh". Bisa ditutup dengan menempel ~10 kata ke bullet ya/tidak yang **sudah ada** di `# LARANGAN` (tawaran media proaktif harus menyebut pilihan tipe, bukan ya/tidak). **Di-skip dulu** demi hemat token — pantau setelah live; kalau Titik 1 sudah cukup, tidak perlu.

## 4. QA Test Suite (kriteria lulus — matriks tawaran × jawaban)

Inti bug: jawaban telanjang "boleh" harus dirutекan sesuai tawaran sebelumnya. Wajib lulus SEMUA:

| # | Pesan VIRA sebelumnya | Balasan user | Ekspektasi tag | Ekspektasi balasan |
|---|---|---|---|---|
| 1 ⭐ (bug asli) | "mau saya kirimkan foto & video unitnya? sebut tipe" | "ya boleh" | TIDAK `[TALK_TO_ADMIN]`; TIDAK `[SEND_MEDIA]` (tipe belum jelas) | tanya balik pilihan tipe (36/72, 36/81, 30/60) |
| 2 | "mau saya kirim foto tipe 36/72?" | "boleh" | `[SEND_MEDIA: foto-36-72]` | konfirmasi kirim |
| 3 (regresi POSITIF) | "kalau mau dibantu langsung tim marketing, tinggal bilang yaa" | "boleh" | `[TALK_TO_ADMIN]` | sambungkan ke tim — **harus tetap jalan** |
| 4 | "mau saya bantu hitung simulasi cicilannya?" | "iya mau" | TIDAK `[TALK_TO_ADMIN]` | hitung dari DATA / tanya angka yang kurang |
| 5 | "kapan kira-kira senggang buat survey?" | "boleh, minggu" | `[SCHEDULE_SURVEY]` atau tanya jam; TIDAK `[TALK_TO_ADMIN]` | proses survey |
| 6 | VIRA tawarkan DUA hal: "saya kirim fotonya, atau mau saya sambungkan ke tim?" | "boleh" | TIDAK ada tag | klarifikasi "yang mana dulu" |
| 7 (regresi) | (apa pun) user: "sambungin ke tim dong" | — | `[TALK_TO_ADMIN]` | sambungkan |
| 8 (regresi) | (apa pun) user: "udah DP kok kemarin" | — | `[TALK_TO_ADMIN]` | akui + sambungkan (jalur booking # SURVEY) |
| 9 (regresi) | user minta spesifik: "minta foto subsidi" | — | `[SEND_MEDIA: foto-30-60]` | kirim |
| 10 (sumber) | VIRA proaktif menawarkan media | — | tawaran menyebut tipe, BUKAN ya/tidak | — |

Cara uji: chat manual di n8n live/test dengan model produksi. Kasus #1 & #3 adalah gerbang utama (fix vs regresi). Lulus = #1 tidak handoff DAN #3 tetap handoff.

## 5. Batasan & catatan

- Fix ini **prompt-only**; tidak menyentuh `Process All` maupun node mana pun — aman digabung/terpisah dari patch kode #22/#23.
- Karena arsitektur tanpa-tool, keputusan tetap probabilistik pada model. Robustness datang dari: (a) menghapus instruksi yang bertabrakan, (b) disambiguasi eksplisit-ekshaustif, (c) menutup sumber ambiguitas (EDIT 4), (d) test suite regresi. Kalau setelah live masih ada slip, opsi Lapis-2 (guard kode: suppress `[TALK_TO_ADMIN]` bila pesan VIRA sebelumnya adalah tawaran media/survey dan pesan user jawaban telanjang) bisa dievaluasi — tapi butuh akses pesan-sebelumnya di `Process All` (perubahan lebih besar, di luar scope minim-touch).
- Saat apply: kalau sekalian bikin `Main V1.4`, satukan dengan patch pending lain yang menyentuh systemMessage supaya tidak dua versi prompt saling menimpa.
