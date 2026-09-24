# STATS Purge — hapus lead yang 3 bulan tidak membalas VIRA

**File import:** `2026-08-27-VIRA-PCR-STATS-Purge-3bulan.json`
**Status:** `active: false` — belum aktif, sengaja. Baca checklist di bawah sebelum menyalakan.
**Dibuat:** 2026-08-27 atas permintaan Steven.

---

## Apa yang dilakukan

Tiap 3 bulan, baca seluruh tab `STATS`, lalu **hapus permanen** setiap baris yang
`last_reply_ts`-nya lebih tua dari 90 hari. Setelah selesai kirim laporan WA ke nomor
maintenance.

### Aturan hapus — satu kriteria, tanpa pengecualian

| Kondisi baris | Hasil |
|---|---|
| `last_reply_ts` < (sekarang − 90 hari) | **DIHAPUS** |
| `last_reply_ts` kosong / bukan angka | **DIHAPUS** (dianggap belum pernah dibalas VIRA) |
| `last_reply_ts` ≥ (sekarang − 90 hari) | tetap tinggal |

Keputusan Steven 2026-08-27: **tidak ada pengecualian.** `bot_mode = OFF`,
`survey_status = SCHEDULED`, `flag_survey = Y`, dan nomor admin/tim sendiri
**semuanya ikut terhapus** kalau `last_reply_ts`-nya sudah lewat ambang.

`last_reply_ts` = kolom **P** di STATS, format **epoch detik**
(`Math.floor(Date.now()/1000)`, ditulis node `Update to STATS` di workflow Main).
Nilai milidetik (>1e12) dinormalkan dulu supaya tidak dibaca sebagai tahun 55.000-an
dan luput dari penghapusan.

### Jadwal

Cron `30 2 1 */3 *` — **02:30 WIB, tanggal 1 Jan / 1 Apr / 1 Jul / 1 Okt.**
Total **4x setahun**. `settings.timezone` = `Asia/Jakarta`.

Jam 02:30 dipilih supaya tidak bertabrakan dengan Archive (02:00) maupun
MSG_BUFFER Cleanup (03:00), dan supaya jaraknya jauh dari menit `:00` tempat
workflow Follow-up (tiap jam) menulis ke STATS.

---

## Alur node

```
Every 3 months 02:30 WIB
 → Read CONFIG PRG          (tab CONFIG, gid 1863977253)
 → Parse Config PRG         (kredensial Kirimi + retention_days + dry_run)
 → Read STATS (all)         (tab STATS, gid 824508993)
 → Plan purge               (hitung baris + bikin blok hapus, urut MENURUN)
 → IF Ada Yang Dihapus
     true  → Split purge blocks → Purge STATS rows → Collapse after purge → Notify Maintenance
     false → Notify Maintenance
```

Semua node Google Sheets: `typeVersion 4.7`, `authentication: serviceAccount`,
credential `QC5aF1HyvTElhC0M — Google Service Account - Persada` (sama dengan
workflow production lain). `errorWorkflow` = `rBsq-mGgHfqfwbz3YmwxI`.

### Kenapa hapus dari bawah ke atas

Nomor baris yang dipakai adalah `row_number` yang **benar-benar terbaca run ini**,
bukan asumsi "baris 2..N" — jadi lead yang masuk setelah node Read tidak ikut kena.
Nomor-nomor itu dikelompokkan jadi blok kontigu lalu diurutkan **menurun**. Menghapus
dari bawah ke atas membuat nomor baris di atasnya tetap valid setelah blok di bawahnya
hilang. Contoh: baris korban `[3,4,5,8,10]` → blok `[{10,1},{8,1},{3,3}]`.

---

## CONFIG yang dipakai

| key | default | fungsi |
|---|---|---|
| `stats_purge_retention_days` | `90` | ambang hari. Di-clamp 7–3650 |
| `stats_purge_dry_run` | kosong = `N` | `Y` = hitung + laporkan saja, sheet **tidak disentuh** |
| `maintenance_phone` | fallback `admin_phone` | tujuan laporan WA |
| `kirimi_user_code` / `kirimi_secret` / `kirimi_device_id` | — | sudah ada, dipakai bersama workflow lain |

Dua key pertama **belum ada** di tab CONFIG. Tidak wajib dibuat — kalau tidak ada,
workflow pakai default (90 hari, bukan dry run). Buat kalau mau ubah ambang atau
mau dry run tanpa menyentuh kode.

---

## Checklist sebelum diaktifkan

1. **Backup tab STATS** — Duplicate sheet. Ini satu-satunya jaring pengaman;
   workflow ini tidak punya arsip.
2. **Import** file JSON ke n8n. Kalau n8n minta konfirmasi kredensial Google,
   pilih `Google Service Account - Persada`.
3. **Run pertama = DRY RUN.** Isi CONFIG `stats_purge_dry_run` = `Y`, klik
   *Execute Workflow* manual, baca laporan WA-nya:
   - `AKAN dihapus : N baris` — masuk akal atau tidak?
   - `last_reply_ts kosong : N` — kalau angka ini besar, artinya banyak lead yang
     belum pernah dibalas VIRA akan ikut hilang. **Periksa dulu.**
   - Daftar 20 nomor pertama yang akan hilang — cek beberapa manual di sheet.
4. Kalau angkanya benar, ubah `stats_purge_dry_run` ke `N` (atau kosongkan), lalu
   aktifkan workflow.
5. **Pastikan `VIRA-PCR - STATS Archive 3bulan` (2026-08-25) tetap NON-AKTIF.**
   Cron-nya di tanggal yang sama. Kalau dua-duanya hidup, dua workflow menghapus
   baris dari STATS di pagi yang sama.

---

## Yang TIDAK dilindungi — baca ini

- **Tidak ada arsip.** Baris yang hilang membawa serta `lead_source`,
  `unit_interest`, `budget_range`, `survey_date`, `flag_survey`, dan
  `follow_up_count`. Tidak bisa dikembalikan kecuali dari backup manual.
- **Lead panas ikut terhapus.** Lead yang sudah survey (`flag_survey = Y`) atau
  punya jadwal survey (`survey_status = SCHEDULED`) tetap dihapus kalau sudah
  90 hari tidak dibalas VIRA. Ini permintaan eksplisit, bukan kelalaian.
- **Baris tanpa `last_reply_ts` ikut terhapus.** Lead hasil impor telemarketer yang
  belum sempat dibalas VIRA akan hilang di run berikutnya. Kalau berubah pikiran,
  ubah `KEEP_WHEN_EMPTY` di baris awal node `Plan purge` jadi `true` — satu kata,
  tidak perlu menyentuh yang lain.
- **Efek samping ke VIRA.** Lead yang barisnya dihapus lalu chat lagi akan dianggap
  user baru: VIRA menyapa dari awal seperti orang asing, dan `follow_up_count`
  balik ke 0 sehingga dia kena rangkaian follow-up dari awal lagi.

### Yang DILINDUNGI

- **Guard skema.** Kalau kolom `No WA` atau `last_reply_ts` tidak ada di sheet yang
  terbaca, workflow `throw` dan **membatalkan seluruh penghapusan**. Ini menjaga
  kalau gid/skema berubah atau workflow salah menunjuk tab — bukan pengecualian
  baris.
- **Peringatan sapu bersih.** Kalau *semua* baris data kena kriteria hapus,
  `console.warn` menyala di log eksekusi (indikasi kolom `last_reply_ts` kemungkinan
  tidak terisi, bukan lead-nya yang memang mati semua).
- **Peringatan kuota.** >40 blok hapus memicu warning — mendekati kuota tulis
  Google Sheets 60/menit. Node Delete sudah `retryOnFail` 3x jeda 5 detik.
- **Notifikasi gagal ≠ hapus gagal.** `Notify Maintenance` pakai
  `onError: continueRegularOutput`, jadi Kirimi down tidak membatalkan penghapusan
  yang sudah beres.

---

## Beda dengan `2026-08-25-VIRA-PCR-STATS-Archive-3bulan.json`

Keduanya jalan 4x setahun dan sama-sama menghapus baris STATS. Pilih **salah satu**.

| | Archive (2026-08-25) | Purge (file ini) |
|---|---|---|
| Ambang default | 60 hari | **90 hari** |
| Dasar "idle" | nilai terbesar dari **9 kolom `_ts`** | **`last_reply_ts` saja** |
| Arsip sebelum hapus | ya, ke tab `STATS_ARCHIVE` + verifikasi baca-ulang | **tidak ada** |
| Pengecualian baris | 5 (bot_mode OFF, survey scheduled, flag_survey Y, nomor tim, tanpa timestamp) | **tidak ada** |
| Baris tanpa timestamp | dilaporkan, tidak dihapus | **dihapus** |
| Jumlah node | 15 + 2 sticky | 10 + 2 sticky |
| Jam | 02:00 WIB | 02:30 WIB |

---

## Verifikasi yang sudah dijalankan

- JSON valid; root key order mengikuti export live n8n
  (`name, nodes, pinData, connections, active, settings, versionId, meta, id, tags`);
  `id` + `versionId` + `meta.instanceId` terisi.
- **0 byte CR** — LF murni, tanpa BOM (421 baris).
- **0 referensi node mati** — dua ekspresi `$('...')` yang dipakai
  (`Parse Config PRG`, `Plan purge`) cocok dengan nama node yang ada.
- Semua target koneksi ada di daftar node; tidak ada dangling.
- **Tree-sitter: 4/4 node Code bebas syntax error.**
- **Simulasi blok hapus: 300/300 kasus acak cocok** — baris yang tersisa persis
  sama dengan yang diharapkan setelah penghapusan bawah→atas.

Belum diuji terhadap sheet sungguhan. Dry run di langkah 3 adalah tes pertamanya.
