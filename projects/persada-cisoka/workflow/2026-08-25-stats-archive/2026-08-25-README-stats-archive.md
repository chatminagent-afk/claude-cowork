# STATS Archive & Cleanup — VIRA PCR (tiap 3 bulan)

**Dibuat**: 2026-08-25
**File import**: `2026-08-25-VIRA-PCR-STATS-Archive-3bulan.json`
**Status**: siap import, `active: false` — belum dijadwalkan sampai kamu nyalakan sendiri
**Jadwal**: 1 Jan / 1 Apr / 1 Jul / 1 Okt, **02:00 WIB** (`0 2 1 */3 *`, timezone workflow `Asia/Jakarta`)

Padanan dari `2026-08-19-VIRA-STATS-cleanup-3bulan.json` milik The Scholars, tapi **bukan
salinan** — lihat bagian "Kenapa beda" di bawah.

---

## Kenapa beda dari punya The Scholars

Di The Scholars, STATS isinya state chat. Aturannya sederhana: semua dihapus kecuali
`off_reason = SAM`.

Di PCR, STATS adalah **database lead**. Satu baris membawa 33 kolom milik klien:
`lead_source`, `unit_interest`, `budget_range`, `nama_lengkap`, `lokasi_kerja`,
`survey_date/time/status`, plus state mesin follow-up (`follow_up_count`,
`last_follow_up_ts`). Hapus baris = tiga kerugian sekaligus:

1. Aset klien hilang — data sumber traffic & kualifikasi lead tidak bisa dipulihkan.
2. VIRA menyapa lead lama seperti orang asing, tanya nama dari nol lagi.
3. `follow_up_count` reset ke 0 → lead lama kena rentetan follow-up dari awal.

Karena itu polanya **arsip dulu, baru bersihkan** — bukan hapus-langsung.

---

## Alur (15 node)

```
Schedule → Read CONFIG → Parse Config ARC → Read STATS (all) → Plan archive → IF ada kandidat
                                                                                │
   ┌────────────────────────────────────────────────────────────────────────────┘
   │ true
   ▼
Split rows → Append STATS_ARCHIVE → Collapse → Read STATS_ARCHIVE (verify) → Verify archive
                                                                                │
   ┌────────────────────────────────────────────────────────────────────────────┘
   ▼
Prepare delete blocks → Delete archived blocks → Collapse → Notify Maintenance
                                                              ▲
                                    IF false (tidak ada kandidat) ┘
```

### Tiga pengaman

| Titik gagal | Akibat | Kehilangan data |
|---|---|---|
| Append gagal | berhenti sebelum hapus | **nol** |
| Verifikasi gagal | berhenti sebelum hapus | **nol** |
| Delete gagal | arsip terlanjur berisi duplikat | **nol** |

Urutan ini disengaja. Kalau dibalik (hapus dulu, arsip belakangan), satu kegagalan
append = lead klien hilang permanen.

**Verifikasi bukan "node Append tidak error".** Workflow membaca ulang tab
`STATS_ARCHIVE` dan menghitung baris ber-`periode` run ini. Kurang dari rencana →
`throw` → STATS tidak disentuh sama sekali.

### Cara menghapus

Beda dari The Scholars yang menghapus "baris 2..N" lalu menyalin balik baris yang
dipertahankan ke bawah. Di sini penghapusan memakai **nomor baris yang benar-benar
dibaca run ini**, dikelompokkan jadi blok kontigu, lalu dihapus **dari bawah ke atas**.
Konsekuensinya:

- Lead yang masuk **setelah** node Read tidak pernah ikut terhapus.
- Baris yang tetap tinggal tidak berpindah tempat — tidak ada append-balik, tidak ada
  perubahan urutan.

---

## Aturan: apa yang TETAP tinggal di STATS

Baris diarsipkan **hanya kalau lolos keenam saringan ini**. Kena salah satu → tinggal.

| # | Kondisi | Alasan |
|---|---|---|
| 1 | `bot_mode = OFF` | sedang dipegang manusia / tim lapangan |
| 2 | `survey_status = scheduled` | ada jadwal survey aktif |
| 3 | `flag_survey` = Y/YA/YES/TRUE/1/SUDAH/DONE | sudah survey — lead paling berharga |
| 4 | aktivitas terakhir < `stats_archive_idle_days` (default **60** hari) | masih hangat |
| 5 | nomor ada di `admin_phone` / `field_team_phone` / `media_team_phone` | nomor tim sendiri |
| 6 | tidak punya timestamp apa pun | umurnya tak bisa dipastikan → jangan diarsipkan |

Semua perbandingan sudah *trim* + *case-insensitive*, jadi `off`, `OFF`, dan `" Off "`
sama-sama tertangkap.

**"Aktivitas terakhir"** = nilai terbaru dari `last_reply_ts`, `last_follow_up_ts`,
`buffer_done_ts`, `debounce_ts`, `pending_survey_ts`, `unit_interest_ts`,
`budget_range_ts`, `nama_lengkap_ts`, `lokasi_kerja_ts`. Nilai epoch milidetik
dinormalkan ke detik otomatis. Kalau semuanya kosong, dicoba parsing
`Tanggal Chat Terakhir` lalu `Tanggal Chat Pertama` (format `2026-08-21` atau `21/08/2026`).

Baris kategori #6 **dilaporkan terpisah di notifikasi WA** (nomor barisnya disebut)
supaya bisa dicek manual — kalau dibiarkan, baris itu tidak akan pernah bersih.

---

## Setup sebelum diaktifkan

### 1. Buat tab `STATS_ARCHIVE` di `PCR_Database`

> ⚠️ **Jangan ketik headernya manual.** Tiga kolom di STATS punya **spasi di ujung
> nama** — `pending_survey_tanggal `, `pending_survey_jam `, `pending_survey_unit `.
> Spasi itu tidak kelihatan tapi menentukan: node Append memetakan kolom **berdasarkan
> nama persis**. Salah satu spasi hilang → tiga kolom itu kosong di arsip, diam-diam.

Cara aman:

1. Buat tab baru, namanya persis `STATS_ARCHIVE`.
2. Di tab `STATS`: blok **baris 1** (A1:AG1), Copy.
3. Di `STATS_ARCHIVE` klik A1, Paste. Header terbawa apa adanya, spasi ekor ikut.
4. Di sel **AH1** ketik `archived_ts`, di **AI1** ketik `periode`.

Total 35 kolom. Referensi urutan (bukan untuk di-paste): `2026-08-25-header-STATS_ARCHIVE.tsv`.

### 2. Tambah baris di tab `CONFIG`

| key | value | keterangan |
|---|---|---|
| `maintenance_phone` | nomor WA Steven, format `62xxx` tanpa `+`/spasi | tujuan laporan housekeeping. **Kalau dikosongkan, laporan jatuh ke `admin_phone` — yaitu nomor klien.** |
| `stats_archive_idle_days` | `60` | opsional. Batas bawah dipaksa 7 hari, batas atas 3650. |

Kredensial Kirimi tidak perlu disentuh — workflow membacanya dari CONFIG
(`kirimi_user_code` / `kirimi_secret` / `kirimi_device_id`), sesuai keputusan #5 di
`Pending Waiting Changes.md`. **Tidak ada satu pun secret plaintext di file JSON ini.**

### 3. Import & dry run

1. Import JSON ke n8n. Kredensial Google (`QC5aF1HyvTElhC0M`) dan `errorWorkflow`
   (`rBsq-mGgHfqfwbz3YmwxI`) sudah terisi, samakan saja kalau n8n minta konfirmasi.
2. **Biarkan workflow non-aktif.** Klik *Execute Workflow* manual.
3. Buka output node **`Plan archive`** dan baca:
   - `totalDataRows`, `archiveCount`, `keepCount`
   - `reasons` — pecahan alasan baris yang tinggal
   - `blocks` — blok baris yang akan dihapus
   - `noTsRows` — baris tanpa timestamp yang perlu dicek manual
4. Kalau `archiveCount` terasa terlalu besar, **jangan lanjut** — naikkan
   `stats_archive_idle_days` dulu, jalankan ulang, cek lagi.
5. Puas dengan angkanya → aktifkan scheduler.

> Dry run pertama akan tetap mengeksekusi arsip + hapus sampai selesai. Kalau mau
> benar-benar hanya melihat rencana tanpa menyentuh sheet: nonaktifkan sementara node
> `Split archive rows` (klik kanan → Deactivate), Execute, baca `Plan archive`, lalu
> aktifkan lagi.

### 4. Backup pertama kali

Sebelum run pertama di data live: File → Download → `.xlsx` dari `PCR_Database`, simpan
ke `workflow/arsip/`. Sekali saja, sebagai jaring pengaman terakhir.

---

## Isi notifikasi WA

```
[VIRA-PCR] STATS Archive — 2026-Q3

Diarsipkan   : 148 baris -> tab STATS_ARCHIVE
Sisa di STATS: 37 baris

Yang tetap tinggal:
- Dipegang manusia (bot_mode OFF) : 4
- Jadwal survey aktif (scheduled) : 6
- Sudah survey (flag_survey Y)    : 11
- Masih hangat (< 60 hari)        : 16

PERLU DICEK: 3 baris tanpa timestamp apa pun — umurnya tidak bisa
dipastikan jadi sengaja TIDAK diarsipkan.
Baris: 41(628xxx), 77(-), 92(628yyy)
```

Node `Notify Maintenance` di-set `onError: continueRegularOutput` — Kirimi down tidak
membatalkan arsip yang sudah beres.

---

## Catatan operasional

- **Kuota Google Sheets** 60 tulis/menit/user. Node Delete jalan sekali per blok, sudah
  `retryOnFail` 3× jeda 5 detik. Kalau blok > 40, `Plan archive` menulis peringatan di
  console execution.
- **Jam 02:00 WIB** dipilih karena trafik nol dan satu jam sebelum `MSG_BUFFER Cleanup`
  harian 03:00 — tidak pernah rebutan kuota.
- **Aman dijalankan ulang.** Run kedua di kuartal yang sama tidak menemukan kandidat
  (barisnya sudah pindah) → cabang IF false → cuma kirim notifikasi.
- **Arsip tumbuh terus** di satu tab. Batas spreadsheet Google 10 juta sel; 35 kolom ×
  ribuan baris masih sangat jauh. Kalau suatu saat perlu dipecah per tahun, tinggal
  ganti `sheetName` node Append & Verify jadi ekspresi.
- Workflow ini **tidak menyentuh** tab `SURVEY` dan `EVENTS` — riwayat survey dan event
  log tetap utuh sebagai sumber kebenaran jangka panjang.

## Verifikasi yang sudah dijalankan

- JSON parse OK, 17 node (15 fungsional + 2 sticky note), 0 referensi koneksi
  menggantung, 0 node tak terjangkau.
- Ketujuh Code node lolos parse JavaScript (esprima, wrapped sebagai function body).
- Nol sisa artefak The Scholars (nama, doc ID, gid, kredensial) dan nol secret inline.
- Logika `Plan archive` + penghapusan blok disimulasikan atas 14 baris sintetis yang
  mencakup keenam alasan "tetap tinggal" (termasuk case/spasi campur, epoch milidetik,
  nomor tim ber-`.0`, dan timestamp dari kolom `*_ts` selain `last_reply_ts`):
  blok tersusun menurun `[11..12, 7, 2..3]`, dan baris yang selamat **persis sama**
  dengan daftar yang seharusnya tinggal.
