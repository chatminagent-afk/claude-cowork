# Panduan Deploy — patch brief deck 2026-08-30

**Ini tambahan, bukan pengganti.** `2026-08-28-panduan-deploy-VIRA-Personal.md` tetap berlaku
untuk kredensial, Kirimi, dashboard, dan cleanup. Yang di sini khusus perubahan brief deck.

**Yang berubah:** REQUESTS 32 → 43 kolom · field AI 27 → 33 · 2 node baru di cabang deck ·
brief setengah jadi tidak lagi dibuang · VIRA boleh menanyakan 2 angka ROI.

**Status QA:** 57 lolos, 0 gagal — **statis saja**. Perilaku belum diuji sama sekali.

---

## 0. File yang sudah disiapkan

| File | Dipakai di |
|---|---|
| `workflow/2026-08-30-VIRA-Personal-Main.json` | langkah C |
| `sheet/2026-08-30-import/REQUESTS-header.tsv` | langkah A |
| `sheet/2026-08-30-import/_KAMUS_BRIEF.csv` | langkah B |
| `workflow/_qa_2026-08-30.py` | jalankan ulang kapan saja untuk cek |
| `docs/2026-08-30-perbaikan-brief-deck.md` | detail teknis + UAT lengkap |

Sumber 28 Agu tidak diubah — masih utuh kalau perlu balik.

---

## A. ⚠️ Tambah 11 kolom di tab REQUESTS

**Ini pemblokir.** `Write REQUESTS` memetakan 8 dari 11 kolom ini. Kalau workflow baru diaktifkan
sebelum header-nya ada, **node Sheets langsung error** dan brief tidak tersimpan sama sekali.

**Caranya:** buka tab REQUESTS, klik sel **AG1** (persis di kanan `status_followup`), ketik 11
header ini berurut ke kanan:

```
kota | jumlah_admin | sudah_pakai_chatbot | integrasi_dibutuhkan | data_tersedia | kutipan_asli | sumber_prospek | brief_jumlah | deck_dikirim_ts | hasil | alasan_kalah
```

**JANGAN import ulang tab REQUESTS** — cukup ketik header, jangan sentuh 32 kolom lama.
Acuan urutan lengkap ada di `REQUESTS-header.tsv`.

**Kenapa ditempel di kanan:** supaya tidak ada kolom lama yang bergeser. Node Sheets memetakan
berdasarkan nama header, jadi urutan tidak berpengaruh ke workflow — yang penting baris lama
tidak rusak.

---

## B. Buat tab `_KAMUS_BRIEF`

Buat tab kosong bernama `_KAMUS_BRIEF`, lalu import `_KAMUS_BRIEF.csv` (**Replace current sheet**).

**Isinya:** 43 baris, satu per kolom REQUESTS — `field`, `tingkat`, `bagian_deck`, `slide`,
`diisi_oleh`, `contoh_isi`, `catatan`.

**Kenapa:** ini jawaban untuk "buka sheet tanpa dokumen, masih ngerti nggak". Sekarang tiap kolom
punya keterangan tingkat penggaliannya, dia mengisi slide berapa, dan diisi AI atau kamu.

---

## C. Import Main baru

1. Import `2026-08-30-VIRA-Personal-Main.json` sebagai workflow baru
2. **Settings → Error Workflow = `VIRA Personal — Error Notifier`** (sama seperti 28 Agu)
3. Set kredensial Sheets di semua node
4. **Jangan aktifkan dulu** — pastikan A sudah beres
5. Nonaktifkan Main lama → baru aktifkan yang baru. **Jangan dua-duanya aktif**, nomornya sama

**Yang baru di cabang deck:** 2 node — `Siapkan Notif Deck` (Code) dan `IF Brief Layak` (IF).
Urutannya sekarang:

```
Write REQUESTS -> Update STATS Brief -> Siapkan Notif Deck -> Wait Deck -> IF Brief Layak -> Notify Admin Deck
```

Kalau di kanvas terlihat beda dari itu, ada yang salah saat import.

---

## D. Rapikan sheet

**Format Plain text:** kolom `no_wa` di REQUESTS dan `No WA` di STATS.
Format → Number → Plain text. Sekarang tersimpan sebagai angka (`6285171701168`) — pencocokan
tetap aman, tapi ekspor ke luar jadi berantakan.

**Hapus baris uji lama** di REQUESTS, STATS, dan EVENTS (semuanya nomormu sendiri, 16–21 Agu).
`ts`-nya masih format lama `"16/8/2026, 11.19.08"`; kalau dicampur baris baru yang formatnya
`"2026-09-01 14:30:00"`, sortir jadi kacau.

---

## E. UAT — 4 skenario, jalankan setelah nomor aktif

Detail lengkap + checklist per langkah ada di `2026-08-30-perbaikan-brief-deck.md`.
Ringkasnya:

| | Uji | Yang membuktikan |
|---|---|---|
| **V1** | Chat sebut volume + jam operasional + deadline, **tanpa nama usaha** | Brief mentah **tersimpan**, notif **tidak** terkirim, `deck_requested` tetap kosong |
| **V2** | Lanjutkan sampai sebut nama usaha + industri + masalah | Baris yang sama diperkaya, notif WA **berisi**, `brief_terisi` terisi |
| **V3** | Tanya hal yang sudah dijawab; lalu setuju dibuatkan deck | Bot tidak mengulang; 2 angka ROI ditanya **hanya setelah** setuju, satu per balasan |
| **V4** | Isi kolom `hasil` manual, lalu picu tag lagi | Isian tanganmu **tidak tertimpa** |

**Gerbang paling penting: V1 dan V2.** V1 membuktikan data tidak lagi dibuang, V2 membuktikan
notifikasi tidak lagi kosong. Dua itu inti seluruh patch — kalau keduanya lolos, sisanya kosmetik.

⚠️ **Kalau `brief_terisi` masih kosong di V2:** kolomnya sudah dipastikan ada di STATS, jadi
penyebabnya bukan schema. Langsung buka execution log n8n di node `Update STATS Brief`.

---

## F. Yang berubah di perilaku VIRA — siap-siap

**VIRA sekarang akan menanyakan omzet.** Setelah prospek setuju dibuatkan deck, dia menanyakan
rata-rata nilai satu closing dan prospek per bulan — satu per balasan. Ini disengaja: tanpa dua
angka itu slide ROI di deck selamanya jadi template.

⚠️ **Belum ada jawaban FAQ untuk orang yang defensif soal ini.** Dari 48 baris FAQ, tidak satu
pun menyentuh "kenapa kamu nanya angka penjualan saya". Kalau mau, aku bikinkan.

**VIRA masih belum bisa mengirim file apa pun.** Tab LINKS cuma 2 baris (landing page + IG),
padahal `media/` sudah punya deck PDF, company profile, dan harga-ringkas. Perlu diupload ke
Drive dan ditempel URL-nya ke LINKS.

---

## G. Butuh keputusanmu

- **Enum `hasil`** — aku isi `DEAL / KALAH / NO_RESPONSE / MASIH_JALAN`. Cocok?
- **Kosakata `sumber_prospek`** — sekarang `lead_source` isinya "Organik". Ada nilai lain?
- **File deck 31 slide Scholars + outline Persada** — tidak ada di folder ini. Kalau masih ada,
  aku bisa bikin kerangka deck dari 33 field; tanpa itu cuma jadi tebakan.

---

## Checklist

```
SHEET  (bisa sekarang, tidak menunggu nomor)
[ ] Tambah 11 kolom di REQUESTS mulai sel AG1  <- PEMBLOKIR
[ ] Buat tab _KAMUS_BRIEF -> import _KAMUS_BRIEF.csv (Replace current sheet)
[ ] Format no_wa (REQUESTS) + No WA (STATS) jadi Plain text
[ ] Hapus baris uji 16-21 Agu di REQUESTS / STATS / EVENTS

N8N  (bisa sekarang)
[ ] Import 2026-08-30-VIRA-Personal-Main.json
[ ] Set Error Workflow = VIRA Personal - Error Notifier
[ ] Set kredensial Sheets
[ ] Cek kanvas: Write REQUESTS -> Update STATS Brief -> Siapkan Notif Deck
                -> Wait Deck -> IF Brief Layak -> Notify Admin Deck
[ ] JANGAN aktifkan sampai 4 langkah SHEET beres

MENUNGGU NOMOR
[ ] Isi 5 nilai "ISI MANUAL" di CONFIG
[ ] Nonaktifkan Main lama -> aktifkan Main baru
[ ] UAT V1  (brief mentah tersimpan, notif tidak terkirim)
[ ] UAT V2  (notif berisi, brief_terisi terisi)
[ ] UAT V3  (tidak mengulang, 2B tepat waktu)
[ ] UAT V4  (kolom manual tidak tertimpa)

OPSIONAL
[ ] Upload 3 file media ke Drive -> isi tab LINKS
[ ] Tambah FAQ objection "kenapa nanya omzet"
```

**Verifikasi ulang kapan saja:**

```bash
cd "D:/Documents/Claude Cowork/VIRA/VIRA Steven/workflow" && python _qa_2026-08-30.py
```
