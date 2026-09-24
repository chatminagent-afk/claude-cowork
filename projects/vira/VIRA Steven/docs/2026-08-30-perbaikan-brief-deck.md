# Perbaikan alur brief deck — Paket A, B, C, D, E

**Tanggal:** 2026-08-30
**Alasan:** audit isi `sheet/VIRA Database.xlsx` (snapshot 30 Agu) menemukan tiga jalur di mana
informasi prospek hilang atau tidak pernah masuk sebelum sempat dipakai menyusun pitch deck,
plus sejumlah field yang decknya butuh tapi sheet-nya belum punya.

**Status:** semua patch selesai dan **lolos QA statis (57/57, 0 gagal)**.
**UAT perilaku BELUM dijalankan** — nomor WA baru masih terkendala registrasi NIK.
Jangan anggap ini sudah teruji sampai V1–V4 di bawah dicentang.

---

## Berkas

| Berkas | Status |
|---|---|
| `workflow/2026-08-30-VIRA-Personal-Main.json` | **BARU — ini yang diimpor ke n8n** (100 → 102 node) |
| `workflow/2026-08-30-system-prompt-VIRA-Personal.md` | **BARU** — diekstrak dari JSON, hanya untuk dibaca |
| `workflow/_patch_2026-08-30.py` | skrip patch, 22 langkah, gagal-keras kalau pola tidak ketemu |
| `workflow/_qa_2026-08-30.py` | **BARU** — harness QA statis, 57 pemeriksaan |
| `sheet/2026-08-30-import/REQUESTS-header.tsv` | **BARU** — header REQUESTS 43 kolom |
| `sheet/2026-08-30-import/_KAMUS_BRIEF.csv` | **BARU** — kamus field untuk tab `_KAMUS_BRIEF` |
| `workflow/2026-08-28-VIRA-Personal-Main.json` | sumber patch, **tidak diubah** — cadangan untuk balik |
| `workflow/2026-08-15-system-prompt-VIRA-Steven.md` | ditandai KEDALUWARSA di baris pertama, isi lama utuh |

Semua berkas turunan dibuat ulang dari satu skrip. Kalau perlu regenerasi:

```bash
cd "D:/Documents/Claude Cowork/VIRA/VIRA Steven/workflow" && rm -f 2026-08-30-VIRA-Personal-Main.json && python _patch_2026-08-30.py && python _qa_2026-08-30.py
```

---

## PAKET A — hentikan kehilangan data

### A1 — gerbang TINGKAT 1 tidak lagi membuang brief

**Sebelumnya:** kalau `nama_bisnis` / `industri` / `masalah_utama` ada yang kosong, `Process All`
menyetel `isDeckRequest = false` dan **seluruh blok field dibuang**. `deckRejected` cuma masuk
`console.warn`, tidak dipakai node mana pun. Prospek yang sudah menyebut volume chat, budget, dan
deadline tapi belum menyebut nama usahanya → semua itu hilang.

**Sekarang:** gerbang TINGKAT 1 hanya menahan **notifikasi ke HP Steven**. Brief tetap ditulis ke
REQUESTS; kolom `kelengkapan` yang membedakan matang dari mentah. Yang masih dibuang hanya blok
yang benar-benar kosong total.

### A1b/A1c — flag `deckLayak` dipisah dari `isDeckRequest`

Efek samping dari A1, dan ini yang paling mudah kelewat: `isDeckRequest` sekarang `true` juga untuk
brief mentah, padahal ekspresi lama memakai flag itu untuk mengisi `STATS.deck_requested = 'Y'` —
kolom yang **mengeluarkan prospek dari jeda follow-up**. Kalau dibiarkan, orang yang belum pernah
minta deck ikut difollow-up.

Flag baru `deckLayak = isDeckRequest && !deckRejected` dipakai oleh `Update to STATS`,
`Update STATS Brief`, dan `IF Brief Layak`. Keduanya tetap mempertahankan nilai lama kalau
`deckLayak` false, jadi `Y` yang sudah ada tidak pernah terhapus.

### A2 — tidak ada lagi ekspresi yang menyeberangi node `Wait`

**Urutan lama:** `Write REQUESTS → Wait Deck (20s) → Update STATS Brief → Notify Admin Deck`

Dua node di hilir `Wait` membaca `$('Merge Brief')` dan `$('Parse Config')`. Kalau ekspresi lintas
`Wait` gagal resolve, hasilnya **string kosong** dan node HTTP tetap jalan — notifikasi terkirim
tanpa isi, `brief_terisi` tertulis kosong. Tidak ada yang error, jadi tidak ada yang kelihatan.

**Urutan baru:**
```
Write REQUESTS → Update STATS Brief → Siapkan Notif Deck → Wait Deck → IF Brief Layak → Notify Admin Deck
```

- `Update STATS Brief` sekarang berjalan **sebelum** `Wait`.
- `Siapkan Notif Deck` (node Code baru) mengemas semua yang masih dibutuhkan setelah `Wait`
  (`notif_text`, `deck_layak`, 4 kredensial Kirimi) jadi satu item biasa.
- `Notify Admin Deck` sekarang cuma baca `$json.*`.
- Jeda 20 detik tetap persis sebelum kirim WA ke admin — maksud aslinya tidak berubah.
- `IF Brief Layak` (node IF baru): cabang `false` berhenti diam-diam. Brief tetap tersimpan,
  Steven cuma tidak dikirimi notifikasi untuk brief mentah.

---

## PAKET C — dua angka ROI naik ke tingkat yang boleh ditanya

Desain brief menyebut `nilai_transaksi` + `prospek_per_bulan` sebagai *"dua angka yang bikin slide
ROI bisa dihitung spesifik, bukan template"*. Tapi di system prompt keduanya ada di **TINGKAT 3 —
TIDAK PERNAH kutanyakan**. Terbukti di satu-satunya brief yang pernah masuk: seluruh bagian E (ROI)
dan hampir seluruh bagian F (komersial) kosong. Pola itu akan terulang di setiap prospek.

- **TINGKAT 2B baru** — kedua angka boleh ditanya, **hanya setelah prospek setuju dibuatkan pitch
  deck**. Dibingkai sebagai syarat hitungan, bukan pertanyaan jualan. Satu pertanyaan per balasan
  tetap berlaku, jadi ditanya di dua giliran berbeda. Kalau ditolak, tidak diulang.
- Keduanya keluar dari TINGKAT 3.
- **TINGKAT 1 bukan lagi gerbang emisi tag** — mengikuti A1.
- **Syarat pemicu tag dilonggarkan:** setuju dibuatkan deck, ATAU TINGKAT 1 lengkap, ATAU sudah
  menyebut minimal tiga hal apa pun tentang bisnisnya.
- **Rem baru:** jangan emisikan tag kalau tidak ada informasi baru sejak tag terakhir — supaya
  pelonggaran di atas tidak jadi emisi 33 baris tiap giliran.

---

## PAKET B — 11 kolom baru di REQUESTS

REQUESTS: **32 → 43 kolom**. Field yang diisi AI: **27 → 33**, jadi `kelengkapan` sekarang `n/33`.
Semua kolom baru ditempel di **kanan**; 32 kolom lama tidak bergeser sedikit pun (diverifikasi QA).

### 6 field baru yang diisi AI

| Field | Guna di deck |
|---|---|
| `kutipan_asli` | 3–5 kalimat mentah milik prospek, dipisah ` \| `. Bahan mockup percakapan (slide 8–15) |
| `kota` | Konteks lokal, zona waktu, pengaturan meeting |
| `jumlah_admin` | Angka. Basis hitungan ROI — `siapa_balas_chat` isinya teks bebas, tidak bisa dihitung |
| `sudah_pakai_chatbot` | Menentukan objection mana yang perlu dijawab di deck |
| `integrasi_dibutuhkan` | Scope build + slide implementasi |
| `data_tersedia` | Sudah punya FAQ / price list / katalog? Ini yang menentukan timeline di slide 29 |

Lima yang bawah masuk **TINGKAT 3** (dicatat kalau disebut sendiri, tidak pernah ditanya).

`kutipan_asli` diperlakukan khusus: satu-satunya field yang justru diisi **kutipan mentah** — prompt
lain melarang kutipan mentah. Batas panjangnya dilonggarkan 500 → 900 karakter. Ada larangan
eksplisit memasukkan nomor telepon, alamat, nama orang lain, atau data pribadi ke dalamnya.

### 2 kolom diisi sistem

- `sumber_prospek` — dari mana dia sampai ke VIRA (IG / landing / referral), disalin dari
  `STATS.lead_source`. **Beda dari `sumber_leads`**, yang artinya sumber leads milik bisnis dia.
  Sekali terisi, dipertahankan.
- `brief_jumlah` — versi angka dari `kelengkapan`, supaya bisa disortir. (Ini A3 yang ditunda
  dari sesi lalu.)

### 3 kolom diisi Steven manual (Paket E)

`deck_dikirim_ts`, `hasil` (DEAL / KALAH / NO_RESPONSE / MASIH_JALAN), `alasan_kalah`.

Ketiganya **sengaja tidak dipetakan** di `Write REQUESTS` supaya isian tangan tidak pernah ditimpa
workflow. Diverifikasi QA. Tanpa kolom ini tidak ada umpan balik untuk memperbaiki deck maupun bot.

---

## PAKET D — sheet jadi bisa dibaca sendiri

- **Tab `_KAMUS_BRIEF`** — 43 baris, satu per kolom REQUESTS: `field`, `tingkat`, `bagian_deck`,
  `slide`, `diisi_oleh`, `contoh_isi`, `catatan`. Ini yang menjawab "buka sheet tanpa dokumen,
  masih ngerti nggak". QA memaksa isinya selalu sinkron dengan header REQUESTS.
- **Timestamp bisa diurutkan** — `ts` / `update_terakhir` pindah dari `"16/8/2026, 11.19.08"`
  (locale string) ke `"2026-08-30 23:04:11"` WIB. Format lama tidak bisa disortir maupun dihitung
  selisihnya, jadi "berapa lama dari chat pertama sampai brief masuk" mustahil dijawab.
- **Format kolom `no_wa` → Plain text** (langkah manual, ada di checklist deploy). Sekarang
  tersimpan sebagai angka (`6285171701168`); pencocokan tetap aman karena `Merge Brief` memakai
  `digits()`, tapi ekspor ke luar jadi berantakan.

---

## Deploy

**Urutannya mengikat.** Langkah 1 wajib selesai sebelum langkah 3 — `Write REQUESTS` memetakan
8 kolom baru, dan node Google Sheets akan error kalau header-nya belum ada.

1. **Tambahkan 11 kolom di tab REQUESTS**, ditempel di kanan `status_followup`, urut persis:
   `kota`, `jumlah_admin`, `sudah_pakai_chatbot`, `integrasi_dibutuhkan`, `data_tersedia`,
   `kutipan_asli`, `sumber_prospek`, `brief_jumlah`, `deck_dikirim_ts`, `hasil`, `alasan_kalah`.
   Acuan lengkap: `sheet/2026-08-30-import/REQUESTS-header.tsv`.
   **Jangan import ulang tab REQUESTS** — cukup ketik header barunya.
2. **Buat tab kosong `_KAMUS_BRIEF`**, lalu import `_KAMUS_BRIEF.csv` (Replace current sheet).
3. Impor `2026-08-30-VIRA-Personal-Main.json` ke n8n sebagai workflow baru.
4. Set ulang kredensial Google Sheets & Error Workflow.
5. Pastikan `CONFIG` tidak ada lagi nilai `ISI MANUAL` (4 kredensial Kirimi + `bot_wa_number`).
6. Format kolom `no_wa` di REQUESTS & `No WA` di STATS jadi **Plain text**.
7. Hapus baris uji lama di REQUESTS/STATS/EVENTS (nomor Steven sendiri) — `ts`-nya masih format
   lama, akan mengacaukan sortir kalau dicampur baris baru.
8. Nonaktifkan Main lama, aktifkan yang baru. **Jangan dua-duanya aktif** — nomor yang sama.

---

## QA yang sudah dijalankan

```bash
cd "D:/Documents/Claude Cowork/VIRA/VIRA Steven/workflow" && python _qa_2026-08-30.py
```

**57 lolos, 0 gagal, 1 catatan.** Yang diperiksa:

| Kelompok | Isi |
|---|---|
| Integritas workflow | nama node unik, semua koneksi menunjuk node nyata, tidak ada node yatim |
| Sintaks | 29 code node lolos `_cek_js.py` |
| Kabel cabang deck | 8 sambungan berurut + cabang `false` `IF Brief Layak` benar-benar buntu |
| Ekspresi lintas `Wait` | tidak ada `$('NodeLain')` tersisa di hilir `Wait Deck` |
| Keselarasan field | 33 field identik & urut sama di **4 tempat**: `DECK_FIELDS`, `FIELDS`, `LABEL`, blok tag di prompt |
| Kolom REQUESTS | 43 kolom unik; semua yang dipetakan ada di header; 3 kolom manual dipastikan **tidak** dipetakan |
| Kamus | `_KAMUS_BRIEF` menutup 43 kolom, urut sama, tanpa sel kosong, nilai `tingkat` sah |
| Gerbang & flag | `deckLayak` terpapar & dipakai di 3 tempat; `deck_requested` tidak pernah menghapus `Y` lama |
| System prompt | 10 pemeriksaan isi (2B ada, ROI keluar dari T3, rem emisi, aturan & larangan privasi `kutipan_asli`) |
| Sinkron | isi `.md` prompt identik dengan node `AI Agent` di JSON |
| Sheet live | tab yang dirujuk 20 node Sheets semuanya ada; 32 kolom lama tidak bergeser |

**Catatan (bukan kegagalan):** 11 kolom REQUESTS harus ditambahkan manual — memang langkah 1 deploy.

### Yang QA statis TIDAK bisa jamin

Harness ini memeriksa struktur, bukan perilaku. Yang tetap harus diuji hidup: apakah AI benar-benar
mengeluarkan tag pada saat yang tepat, apakah Google Sheets menulis ke baris yang benar, apakah
notifikasi WA terkirim berisi, dan apakah 2B tidak terasa menginterogasi. **Tidak ada satu pun dari
itu yang sudah terbukti.**

---

## Checklist UAT (jalankan saat nomor sudah aktif)

Dari nomor uji, empat skenario:

**V1 — brief mentah tetap tersimpan (inti A1)**
Chat yang menyebut volume chat + jam operasional + deadline, **tanpa pernah menyebut nama usaha**.
- [ ] Baris baru muncul di REQUESTS, `nama_bisnis` kosong tapi field lain terisi
- [ ] `kelengkapan` > 0 dan `brief_jumlah` terisi angka yang cocok
- [ ] **Tidak ada** notifikasi WA masuk ke HP Steven
- [ ] `STATS.deck_requested` **tetap kosong** (bukan `Y`)

**V2 — brief matang jalan penuh**
Lanjutkan chat yang sama sampai menyebut nama usaha + industri + masalah utama.
- [ ] Baris REQUESTS yang sama diperkaya, bukan baris baru (cocok `no_wa`)
- [ ] Notifikasi WA masuk **dengan isi lengkap**, bukan pesan kosong
- [ ] `STATS.deck_requested = Y` dan **`STATS.brief_terisi` terisi daftar key**
- [ ] `ts` berformat `2026-09-.. ..:..:..`, dan `update_terakhir` lebih baru dari `ts`
- [ ] `sumber_prospek` terisi mengikuti `STATS.lead_source`

**V3 — bot tidak menanyakan ulang, dan 2B tepat waktu**
- [ ] Bot tidak menanyakan ulang field yang sudah ada di `brief_terisi`
- [ ] Sebelum setuju dibuatkan deck, bot **tidak pernah** menanyakan nilai closing / prospek per bulan
- [ ] Setelah setuju, bot menanyakan keduanya — satu per balasan, di dua giliran berbeda
- [ ] Ditolak sekali → tidak diulang

**V4 — kutipan_asli & kolom manual**
- [ ] `kutipan_asli` terisi kalimat mentah prospek, dipisah ` | `, bukan parafrase
- [ ] Tidak ada nomor telepon / alamat / nama orang lain di dalamnya
- [ ] Isi `hasil` manual di sheet, picu satu tag lagi → **nilai manual itu tidak tertimpa**

**Soal `brief_terisi` yang kosong di data 16 Agu:** QA memastikan kolom `brief_terisi` **sudah ada**
di tab STATS sekarang. Jadi hipotesis "kolomnya belum ada saat tes" hanya berlaku kalau kolom itu
ditambahkan setelah 16 Agu — tidak bisa dipastikan dari snapshot. Kalau V2 masih menunjukkan kolom
itu kosong padahal kolomnya ada, penyebabnya bukan schema: lihat execution log n8n di node
`Update STATS Brief`.

---

## Yang tidak dikerjakan

- **Normalisasi `PROGRAM.Harga`** (campur `3000000` dan `"Gratis"` di satu kolom). Tidak menyentuh
  alur brief deck, dan memisahnya berisiko ke node katalog. Sisakan untuk kalau memang mengganggu.
- **Arsip transkrip percakapan.** `kutipan_asli` menutup kebutuhan deck, tapi percakapan utuh tetap
  hilang setelah `msg_buffer_retention_hours = 2`. Kalau nanti perlu, itu tab baru + job sendiri.
- **Label notifikasi masih `[VIRA Steven]`** padahal tenant sudah bernama VIRA Personal. Kosmetik.
