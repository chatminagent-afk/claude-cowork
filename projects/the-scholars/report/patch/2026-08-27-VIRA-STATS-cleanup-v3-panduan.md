# VIRA — STATS Cleanup v3: lindungi baris OFF + filter umur 90 hari

**Tanggal:** 2026-08-27
**File workflow:** `2026-08-27-VIRA-STATS-cleanup-3bulan-v3.json`
**QA:** `2026-08-27-qa-cleanup-v3.py` — 72 PASS / 0 FAIL
**Menggantikan:** v2 (`2026-08-27-...-v2.json`) dan v1 (`2026-08-19-...json`) — keduanya **belum pernah diaktifkan**

---

## 1. Aturan

Baris **DIPERTAHANKAN** kalau memenuhi salah satu:

1. Header (baris 1) — tidak pernah masuk hitungan.
2. **Dilindungi permanen:** `bot_mode == "OFF"` dan `off_reason` **bukan** `"VIRA"`.
   Tanpa kedaluwarsa, berapa pun umurnya.
3. **Masih hangat:** aktivitas terakhir < **90 hari** lalu.
4. **Tanpa jejak waktu:** tidak ada satu pun kolom timestamp terisi → umur tidak bisa
   dipastikan, jadi tidak disentuh dan dilaporkan di notifikasi WA.

Baris **DIHAPUS** hanya kalau ketiganya benar: tidak dilindungi **DAN** punya jejak waktu
**DAN** jejaknya sudah lewat 90 hari.

### Tabel keputusan

| `bot_mode` | `off_reason` | umur | v2 | v3 |
|---|---|---|---|---|
| `OFF` | `SAM` / kosong / label lain | apa pun | simpan | **simpan** |
| `OFF` | `VIRA` | < 90 hari | hapus | **simpan** |
| `OFF` | `VIRA` | > 90 hari | hapus | **hapus** |
| `ON` / kosong | apa pun | < 90 hari | hapus | **simpan** |
| `ON` / kosong | apa pun | > 90 hari | hapus | **hapus** |
| apa pun (tidak dilindungi) | — | tak diketahui | hapus | **simpan + dilaporkan** |

v3 adalah **superset** dari v2 — tidak ada baris yang dulu selamat lalu jadi terhapus.
Diuji di QA bagian E.

## 2. Kenapa ada filter umur

v2 menghapus baris `bot_mode = ON` tanpa peduli umur. Orang yang baru chat 30 September
ikut hilang saat cleanup 1 Oktober — VIRA lalu menyapanya seperti orang asing, `Counter`
balik ke 0, dan `greeting_sent` ter-reset.

## 3. Kenapa patokannya BUKAN `last_reply_ts` saja

Beda dari Persada. Di workflow utama (r9), `last_reply_ts` **hanya** ditulis node
`Update to STATS`, dan node itu ada di cabang `IF Bot Mode Active = ON`. **Kontak yang
di-OFF-kan tidak pernah memperbaruinya walaupun chat tiap hari.**

Yang menyelamatkan mereka adalah `buffer_done_ts` — ditulis `Delete_Pending_Msg_Bot_Off`,
node buntu di cabang OFF (diverifikasi langsung:
`buffer_done_ts: {{ $('Chat Counter').first().json.process_start_ts }}`).

Coverage di data nyata (snapshot 2026-08-14, 664 baris data):

| kolom | semua baris | khusus baris OFF |
|---|---|---|
| `last_reply_ts` | 54% | **41%** |
| `buffer_done_ts` | 69% | 67% |
| `timestamp` | 73% | 54% |
| `gform_sent_ts` | 37% | 33% |
| `kelas_anak_ts` | 35% | 26% |
| `Tanggal Chat Terakhir` | 73% | 53% |
| **gabungan (max + fallback tanggal)** | **84.5%** | — |

Jadi umur diambil dari **nilai terbesar** `last_reply_ts`, `buffer_done_ts`, `timestamp`,
`gform_sent_ts`, `kelas_anak_ts`, dengan cadangan terakhir parse `Tanggal Chat Terakhir`
lalu `Tanggal Chat Pertama` (format `DD/MM/YYYY`).

### Unit campur — penting

Kolom ts di sheet ini **tidak seragam**:

| kolom | unit |
|---|---|
| `last_reply_ts`, `gform_sent_ts`, `kelas_anak_ts` | detik |
| `buffer_done_ts` | milidetik |
| `timestamp` | **campur detik & milidetik antar-baris** |

Karena itu normalisasi dilakukan **per nilai** (`n > 1e12 ? n/1000 : n`), bukan per kolom.

### `KEEP_WHEN_EMPTY` sengaja berbeda dari Persada Purge

Persada Purge memakai `KEEP_WHEN_EMPTY = false` (baris tanpa timestamp dihapus). Di sini
itu berbahaya: di snapshot nyata ada **103 baris tanpa jejak waktu sama sekali, dan 100%
dari baris itu `bot_mode = OFF`** — persis kontak Sam. Di v3 mereka aman lewat dua lapis
sekaligus (lapis 2 perlindungan OFF, dan lapis 4 tanpa-jejak).

## 4. Perubahan arsitektur: salin-lalu-hapus → hapus per blok

v1/v2 memakai "salin baris yang disimpan ke bawah sheet (append), lalu hapus blok
`2..maxRow`". Itu masuk akal ketika yang disimpan cuma segelintir baris SAM.

Dengan filter umur, **mayoritas baris justru dipertahankan** — di data nyata 664 dari 664.
Menyalin ratusan baris lalu menghapus blok raksasa jadi mahal, membakar kuota tulis, dan
menaruh seluruh isi tab dalam risiko tiap run.

v3 memakai pendekatan Persada Archive/Purge: hitung nomor baris yang memang kena, kelompokkan
jadi **blok kontigu**, urutkan **MENURUN**, hapus blok per blok. Baris yang dipertahankan
**tidak pernah disentuh sama sekali**. Urutan menurun wajib — kalau menaik, penghapusan blok
atas menggeser nomor baris blok di bawahnya dan yang terhapus jadi baris yang salah.

### Node

| v2 | v3 |
|---|---|
| `Plan cleanup` | `Plan cleanup` — jsCode diganti total |
| `IF Ada Baris Dipertahankan` | `IF Ada Yang Dihapus` — kondisi jadi `deleteCount > 0` |
| `Split kept rows` | `Split delete blocks` |
| `Append Baris Dipertahankan` | **dibuang** |
| `Prepare delete` | `Collapse to one` |
| `Delete original block` | `Delete STATS rows` — `startIndex/numberToDelete` jadi per-blok |
| `Notify Steven` | pesan jadi `{{ $('Plan cleanup').first().json.report }}` |

9 node → 8 node. Laporan WA sekarang dirangkai di dalam `Plan cleanup` sebagai string
`report`, bukan ekspresi concat panjang di parameter node — lebih mudah diubah dan tidak
gampang salah kutip.

Jalur `false` dari IF tetap menuju `Collapse to one` → notifikasi **selalu** terkirim,
termasuk saat tidak ada yang dihapus.

## 5. Guard

| # | Kondisi | Aksi |
|---|---|---|
| 1 | Kolom `No WA` tak ada | **throw** — tab yang terbaca kemungkinan bukan STATS |
| 2 | Kolom `bot_mode` tak ada | **throw** — tanpa ini tidak ada baris yang terlindungi |
| 3 | Tidak ada satu pun kolom patokan umur | **throw** — semua baris terbaca "tanpa jejak", cleanup mubazir |
| 4 | Kolom `off_reason` tak ada | **peringatan** — semua baris OFF diperlakukan sebagai dilindungi (aman) |

Ditambah: `blockCount > 40` → `console.warn` soal kuota tulis Google Sheets (60/menit).
Tidak ada pembatasan diam-diam; semua yang memenuhi syarat tetap dihapus.

## 6. Dampak di data nyata — TERVALIDASI

Node `Plan cleanup` dijalankan manual di n8n (2026-08-27) terhadap sheet live, lalu
hasilnya direkonsiliasi dengan port Python di QA terhadap export
`mock booking/The_Scholars_Database.xlsx` (2026-08-27 16:34, 721 baris data).
**Ke-10 metrik cocok persis, selisih 0:**

```
totalDataRows 721 | keepCount 721 | deleteCount 0 | hasOffReason true
  protSam        66     (OFF + off_reason SAM)
  protBlank     326     (OFF tanpa label)
  protOther       0
  keepHangat    329     (< 90 hari)
  keepTanpaJejak  0
  delOffVira      0
  delNotOff       0
```

**Nol baris dihapus** karena seluruh data berumur 16 Jun – 27 Ags (±72 hari) — belum ada
yang melewati ambang 90 hari. Distribusi umur 329 baris yang tidak dilindungi:

| umur | jumlah |
|---|---|
| 0–30 hari | 140 |
| 31–60 hari | 135 |
| 61–90 hari | 54 |
| > 90 hari | **0** |

`off_reason` di sheet: kosong 648, `SAM` 66, `VIRA` **7**. Ketujuh baris VIRA itu berumur
0,2–6,3 hari — semuanya masih hangat, jadi tidak satu pun kena hapus.

### Proyeksi run berikutnya (berdasarkan data yang ada sekarang saja)

| run | cutoff | hapus |
|---|---|---|
| 2026-10-01 | 2026-07-03 | **76 baris** |
| 2027-01-01 | 2026-10-03 | 329 baris |

Jadi run pertama yang benar-benar menghapus sesuatu adalah **1 Oktober 2026**, sekitar
76 baris. Angka ini belum menghitung baris baru yang masuk sebelum tanggal itu.

Catatan: sheet melaporkan 1515 baris, tapi hanya **721** yang berisi data — sisanya ±794
baris kosong. Baris kosong tidak punya `row_number` dari node Read sehingga tidak ikut
dihitung; v3 juga tidak lagi memadatkannya (v1/v2 memadatkan sebagai efek samping
salin-lalu-hapus). Kalau padding itu mengganggu, rapikan sekali secara manual.

## 7. Sisa risiko

- **Baris OFF tumbuh tanpa batas.** 384 dari 664 baris (58%) sudah OFF dan dilindungi
  selamanya. Filter umur hanya memangkas ekor `ON`, jadi ini memperlambat pertumbuhan,
  bukan membatasinya. Kalau nanti perlu dibatasi: OFF tanpa aktivitas > 12 bulan → arsip
  ke tab `STATS_ARCHIVE` lalu hapus, seperti Persada.
- Beban sebenarnya bukan kapasitas Sheets (batas ~435rb baris di 23 kolom) tapi
  `Read STATS` yang membaca seluruh tab tiap pesan masuk.
- `RETENTION_DAYS = 90` hardcoded di baris awal `Plan cleanup`. Tidak dibaca dari CONFIG
  seperti Persada — workflow ini tidak punya node Read CONFIG dan menambahkannya berarti
  satu API call lagi tiap run.

## 8. Sebelum aktivasi

1. ~~Verifikasi `off_reason`~~ — **SUDAH BERES.** Node `Update row in sheet` di r9 menulis
   `"off_reason": "VIRA"`, dan kolomnya ada di sheet live sebagai **kolom C** (bukan kolom X
   seperti yang direncanakan panduan 2026-08-19 — penyisipan di C menggeser semua kolom
   setelahnya). Tidak berpengaruh ke kode: `Plan cleanup` membaca kolom **berdasarkan nama
   header**, bukan posisi.
2. **`ISI_NOMOR_WA_STEVEN`** di node `Notify Steven` masih placeholder. Node ini
   `onError: continueRegularOutput` — kalau dibiarkan, cleanup tetap jalan tapi laporannya
   hilang diam-diam.
3. ~~Execute Workflow manual dulu~~ — **SUDAH DILAKUKAN** 2026-08-27, hasilnya tervalidasi
   di bagian 6.
4. Pastikan **hanya satu** workflow cleanup STATS yang aktif — v1/v2/v3 memakai cron yang
   sama persis (`1 0 1 */3 *`).
