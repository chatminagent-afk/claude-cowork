# Planning: Disambiguasi Media (Foto/Video) — VIRA PCR

**Tanggal:** 2026-07-18
**Sumber analisis:** `workflow/VIRA-PCR Main.json` (live export, dibaca subagent Sonnet) + `workflow/PCR_Database.xlsx` sheet LINKS (dibaca subagent Sonnet)
**Status:** MENUNGGU APPROVAL STEVEN — belum ada kode yang diubah

---

## 1. Hasil Crosscheck: BELUM CAPABLE

Pertanyaan: apakah VIRA sudah bisa, saat user minta foto/video, bertanya balik "yang mana yang dimaksud" lalu query LINKS untuk dokumen yang tepat?

**Jawaban: belum.** VIRA saat ini **tidak asal-asalan total** (ada validasi ke LINKS + fallback eskalasi manual ke tim), tapi untuk permintaan ambigu dia **asal kirim baris pertama yang cocok**, tanpa pernah bertanya balik.

### Bukti konkret (skenario gagal nyata dengan data LINKS sekarang)

User kirim: *"minta foto dong"*

1. System prompt malah **mencontohkan key generik**: `"[SEND_MEDIA: foto] Boleh Kak, foto unitnya akan tim kami kirimkan sebentar lagi yaa."` → AI pasang `[SEND_MEDIA: foto]`.
2. `Process All` resolve key `foto`: exact match gagal → fallback **substring match dengan `.find()`** yang berhenti di kecocokan PERTAMA sesuai urutan baris sheet.
3. Baris aktif pertama yang mengandung "foto" = row 3 LINKS: `tipe 36 81 - foto eksterior.jpeg`.
4. **User selalu dikirimi foto eksterior tipe 36/81** — walaupun dia tertarik tipe 30/60 subsidi. Sama untuk *"minta video"* → selalu row 4 (video 36/72–36/81), video subsidi 30/60 (row 6) tidak pernah terkirim lewat jalur ini.

### Akar masalah (3 lapis)

| Lapis | Masalah |
|---|---|
| **System prompt (AI Agent)** | Tidak ada satu kalimat pun yang menyuruh AI klarifikasi dulu bila permintaan media ambigu. Contoh tag justru memakai key generik `foto`/`video`. Padahal AI **sudah punya** daftar katalog LINKS aktif di `data_context` (via `FAQ Retrieve`) — dia tahu opsinya, cuma tidak diperintah membandingkan. |
| **Process All (code)** | Matching `exact → substring .find()` = ambil match pertama. Tidak ada state "ambigu". Hanya biner: ketemu → kirim otomatis; tidak ketemu → `isMediaManual` (eskalasi tim). |
| **Sheet LINKS (data)** | `Nama Link` teks bebas & tidak konsisten (`tipe 36 81 - foto eksterior.jpeg` vs `Contoh unit rumah type 3672 atau type 3681.jpeg` vs `Video tipe 36 72 atau tipe 36 81.mp4`). Tidak ada kolom `Tipe Unit` / `Keyword` yang bisa dicocokkan terstruktur. Row 8 tumpang-tindih dengan row 3 & 5. |

### Pola yang sudah ada dan tinggal ditiru

Alur **SURVEY** sudah punya cetak biru persis untuk ini: hard gate deterministik di `Process All` (`isSurveyIncomplete`) yang **meng-override `cleanOutput`** dengan pertanyaan klarifikasi yang digenerate sistem (bukan mempercayai kalimat AI), satu slot per giliran. Konsisten juga dengan catatan teknis register: *"setiap tag yang ditolak sistem harus MENGUBAH balasan, bukan cuma dibuang."*

---

## 2. Prinsip Desain: Minimal Touch

Klarifikasi menumpang **jalur balasan teks yang sudah ada** (`cleanOutput` → `Wait1` → `Reply Chat Kirimi`). Saat ambigu: `isSendMedia=false` dan `isMediaManual=false`, jadi `IF Send Media` dan `IF Media Manual` tidak terpicu.

**Yang disentuh (3 titik + 1 cek kondisional):**
1. Sheet `LINKS` — data saja, bukan kode
2. Node `AI Agent` — field `systemMessage`, blok `# TAG` bagian SEND_MEDIA saja
3. Node `Process All` — satu blok resolve media saja
4. Node `FAQ Retrieve` — **cek dulu**; ubah hanya kalau kolom baru LINKS tidak ikut terserialisasi ke `data_context`

**Yang TIDAK disentuh:** `IF Send Media`, `Wait Media`, `Download Media`, `Send Media Kirimi`, `IF Media Manual`, `Format Media Notif`, `Notify Media Team`, `Notify Admin Media Error`, seluruh jalur survey/FAQ/debounce, wiring antar-node. **Tidak ada node baru, tidak ada rewiring.**

---

## 3. Langkah-Langkah

### Langkah 1 — Restrukturisasi sheet LINKS (data, tanpa kode)

Standarkan `Nama Link` jadi **key kanonik pendek**, pindahkan nama file panjang ke `Deskripsi`, tambah 2 kolom:

| Nama Link (key) | Tipe | Tipe Unit | Keyword | Status | URL | Caption |
|---|---|---|---|---|---|---|
| `brosur` | image | umum | brosur, price list, pricelist | AKTIF | (tetap) | (tetap) |
| `foto-36-72` | image | 36/72 | foto, eksterior, 3672 | AKTIF | (row 5 lama) | (tetap) |
| `foto-36-81` | image | 36/81 | foto, eksterior, 3681 | AKTIF | (row 3 lama) | (tetap) |
| `foto-30-60` | image | 30/60 | foto, eksterior, subsidi | AKTIF | (row 7 lama) | (tetap) |
| `video-36-72` | video | 36/72 | video, 3672 | AKTIF | (row 4 lama) | (tetap) |
| `video-36-81` | video | 36/81 | video, 3681 | AKTIF | (row 4 lama — URL sama) | (tetap) |
| `video-30-60` | video | 30/60 | video, subsidi | AKTIF | (row 6 lama) | (tetap) |
| `maps` | document | umum | lokasi, maps, alamat | AKTIF | (tetap) | (tetap) |
| `website` | document | umum | website | AKTIF | (tetap) | (tetap) |

Catatan:
- Video 36/72 & 36/81 memang satu file → **dua baris dengan URL sama** supaya matching per tipe unit tetap deterministik. Kode Langkah 3 men-dedup by URL, jadi ini tidak memicu ambiguitas palsu.
- Row 8 lama (`Contoh unit rumah type 3672...`) tumpang-tindih dengan foto per-tipe → usul **hapus / set Status non-aktif** (keputusan Steven).
- URL masih dummy (sudah tercatat di checklist go-live §4) — restrukturisasi ini sekalian dikerjakan saat ganti ke file asli.

### Langkah 2 — Rewrite blok `# TAG` SEND_MEDIA di system prompt AI Agent

Aturan baru (draf final ditulis Opus setelah approval):
1. `<key>` **WAJIB diambil persis** dari daftar LINK/MEDIA AKTIF di DATA TERVERIFIKASI — dilarang mengarang key generik (`foto`, `video` bukan key valid).
2. **Kalau permintaan user ambigu** (minta foto/video tanpa menyebut tipe unit, dan ada >1 kandidat cocok di katalog): **JANGAN pasang tag** — tanya balik SATU pertanyaan yang menyebutkan pilihan tersedia. Contoh: *"Boleh Kak 😊 Mau foto unit yang mana ya — tipe 36/72, 36/81, atau 30/60 subsidi?"*
3. Kalau user sudah spesifik, ATAU cuma ada 1 kandidat cocok, ATAU konteks sudah jelas (mis. `UNIT_INTEREST` di SYSTEM_DATA hanya satu tipe) → langsung pasang tag dengan key spesifik.
4. Kalau media yang diminta memang tidak ada di katalog (mis. "foto interior") → tetap pasang tag dengan key deskriptif → jalur eskalasi manual ke tim tetap bekerja seperti sekarang.
5. Contoh-contoh di blok tag diganti mengikuti key kanonik Langkah 1.

Sekalian cek blok `# LARANGAN` ("pertanyaan ya/tidak untuk aksi") tidak bertabrakan — pertanyaan klarifikasi ini pilihan "yang mana", bukan ya/tidak, tapi wording perlu dipastikan tidak menekan AI untuk skip klarifikasi.

⚠️ Sinkron dengan register entri #3 & #8: system prompt live juga sedang menunggu sync dari doc `2026-07-17-enhanced-system-prompt-vira-pcr.md`. Perubahan blok SEND_MEDIA ini harus diedit **di doc itu juga**, lalu di-apply bareng — jangan sampai dua versi prompt saling menimpa.

### Langkah 3 — Guard disambiguasi di `Process All` (defense-in-depth)

Ganti blok resolve media (hanya blok itu). Logika baru:

```
exact match (Nama Link == key)      → 1 hasil  → kirim (seperti sekarang)
substring/keyword match → filter SEMUA kandidat aktif, dedup by URL:
  ├─ 1 kandidat unik   → kirim
  ├─ >1 kandidat unik  → isMediaAmbiguous = true:
  │     • isSendMedia = false, isMediaManual = false
  │     • override cleanOutput dengan pertanyaan pilihan yang
  │       digenerate sistem dari daftar kandidat (pola gate SURVEY —
  │       tag ditolak = balasan berubah, bukan cuma tag dibuang)
  └─ 0 kandidat        → isMediaManual = true (jalur eskalasi existing, tak berubah)
```

- Matching diperluas: cek `Nama Link`, lalu kolom `Keyword` (Langkah 1), plus `Tipe Unit` bila key mengandung pola tipe.
- Ikut konvensi wajib workflow: `.first()` bukan `.item`.
- Field return baru (`isMediaAmbiguous`, `mediaCandidates`) hanya ditambahkan ke object return — tidak mengubah field existing, jadi node hilir tidak terdampak.

### Langkah 4 — Cek serialisasi `FAQ Retrieve` (kondisional)

AI hanya bisa menyebutkan pilihan yang dia "lihat". Cek apakah blok `LINK/MEDIA AKTIF` di `data_context` sudah membawa `Nama Link` + kolom baru (`Tipe Unit`). Kalau sudah cukup → **tidak disentuh**. Kalau belum → tambah 2 kolom itu ke baris serialisasi (perubahan 1-2 baris).

### Langkah 5 — UAT

| # | Skenario | Ekspektasi |
|---|---|---|
| 1 | "minta foto dong" (tanpa konteks tipe) | VIRA tanya balik pilihan tipe; TIDAK ada media terkirim; TIDAK ada notif tim |
| 2 | Lanjutan #1: "yang subsidi" | `[SEND_MEDIA: foto-30-60]` → foto 30/60 terkirim |
| 3 | "minta foto tipe 36/72" (langsung spesifik) | Langsung kirim `foto-36-72`, tanpa tanya balik |
| 4 | "minta video" | Tanya balik (ada video 36/72, 36/81, 30/60) |
| 5 | "ada video yang subsidi?" | Langsung kirim `video-30-60` |
| 6 | "minta foto interior" (tidak ada di katalog) | Eskalasi manual → `Notify Media Team` (jalur existing) |
| 7 | Regresi: "minta brosur" | Langsung kirim brosur (1 kandidat, tanpa tanya balik) |
| 8 | Regresi: alur survey lengkap + chat biasa | Tidak berubah |
| 9 | User dengan `UNIT_INTEREST` satu tipe minta "foto" | Ideal: langsung kirim tipe itu (via aturan prompt #3); minimal: tanya balik |

---

## 4. Pembagian Kerja (sesuai instruksi orkestrasi)

| Peran | Model | Tugas |
|---|---|---|
| Orkestrator | Fable | Analisis, planning ini, review hasil |
| Reader | Sonnet | ✅ Selesai — baca workflow JSON + PCR_Database.xlsx |
| Programmer | Opus | **Setelah approval:** (a) patch blok resolve media `Process All` (find/replace siap paste), (b) teks final blok `# TAG` SEND_MEDIA (untuk node live + doc enhanced prompt), (c) tabel LINKS final siap salin |

## 5. Batasan & Risiko

- **Satu media per giliran** (arsitektur single-tag existing). "Minta foto DAN video 36/72" → AI kirim satu, tawarkan sisanya di giliran berikut. Multi-tag = perubahan lebih besar, di luar scope — masuk register kalau nanti dibutuhkan.
- Perubahan `Nama Link` di LINKS **wajib bareng** update contoh key di system prompt (Langkah 1 & 2 satu paket) — kalau tidak, key lama di prompt tidak akan match.
- `Process All` jalan di setiap pesan → patch harus find/replace blok lokal saja, regresi skenario 8 wajib.
- URL media masih dummy — go-live tetap tergantung checklist §4/§6 (file asli + izin tim).
