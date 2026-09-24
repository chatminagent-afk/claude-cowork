# Panduan Migrasi — 2 Workflow Global

**File import:**
- `2026-08-28-GLOBAL-VIRA-Error-Notifier.json`
- `2026-08-28-GLOBAL-Sheet-Cleanup.json`

Keduanya `active: false` dan tanpa root `id` — import bikin workflow baru, tidak menimpa apa pun.

---

## Yang diganti

| Baru | Menggantikan | Hasil |
|---|---|---|
| GLOBAL - VIRA Error Notifier | VIRA TS Error Notifier<br>VIRA-PCR Error Notifier | 2 → 1 |
| GLOBAL - Sheet Cleanup | VIRA - MSG_BUFFER Cleanup<br>VIRA-PCR - MSG_BUFFER Cleanup<br>VIRA Dashboard - DASH_AUDIT Cleanup | 3 → 1 |

**5 → 2.** Klien ke-3 nanti: 1 entri di `TENANTS` + 1 baris di `WF_MAP` (notifier), 2 baris di `JOBS` (cleanup). Tidak ada workflow baru.

---

## A. Error Notifier

Main workflow **tidak disentuh di tahap 1**. Yang diubah cuma dropdown Settings di workflow satelit.

1. Import → aktifkan → catat ID barunya dari URL.
2. Arahkan ulang `Settings → Error Workflow` ke workflow baru, untuk **satelit dulu**:
   - Topic Harvester (WF-A)
   - Monthly Rollup (WF-B)
   - STATS Cleanup v3
   - Follow-up AI Powered
3. Uji: buka satu satelit → Execute Workflow dengan sengaja bikin gagal (mis. ganti sementara nama tab jadi salah) → pastikan WA masuk dan label tenant-nya benar.
4. Biarkan berjalan 1–2 minggu. Dua notifier lama tetap aktif melayani main workflow.
5. Kalau aman: arahkan `VIRA TS` dan `VIRA PCR AI Powered` ke notifier baru (**dropdown Settings saja, node tidak disentuh**), lalu **nonaktifkan** 2 notifier lama. Jangan dihapus dulu.

**Rollback:** arahkan balik Error Workflow ke notifier lama, aktifkan lagi. Nol perubahan pada node.

---

## B. Sheet Cleanup

1. Import. **Jangan diaktifkan dulu.**
2. Buka node `Read Tab` dan `Delete Rows` → pastikan credential terpilih **"Google Service Account - VIRA Dashboard"** (`5KD9A3Tef1H8UQKk`). Ini SA yang sama yang dipakai DASH_AUDIT Cleanup sekarang untuk kedua spreadsheet, jadi akses hapusnya sudah terbukti — tapi cek visualnya, karena cleanup TS lama pakai SA yang berbeda ("Google Service Account thescholars").
3. Klik **Test manual**. Ini **dry run** — sheet tidak disentuh. Kamu akan dapat WA berisi laporan per job.
4. Cocokkan angkanya: MSG_BUFFER TS harusnya kecil (±3 baris), MSG_BUFFER PCR lebih besar, DASH_AUDIT dua-duanya sesuai isi tab. Kalau ada yang `skipped 0 baris [tidak ada baris data]` padahal tabnya berisi, berarti credential atau nama tab salah — **stop di sini**.
5. Kalau angkanya masuk akal: **nonaktifkan** 3 workflow lama, lalu **aktifkan** yang baru.
6. Besok paginya cek Executions jam 03:00 dan jumlah baris MSG_BUFFER.

**Rollback:** nonaktifkan yang baru, aktifkan lagi 3 yang lama. File lamanya tidak diubah sama sekali.

---

## Dua perubahan perilaku yang disengaja

| | Lama | Baru |
|---|---|---|
| Trigger manual | `Test manual` di DASH_AUDIT Cleanup **langsung wipe produksi** | Dry run. Ubah `MANUAL_DRY_RUN` jadi `false` di node **Mode: Manual** kalau memang mau menghapus. |
| Notifikasi WA | Ketiga cleanup senyap total | Job kuartalan + semua dry run dapat laporan WA. Job harian tetap senyap supaya tidak spam. |

Sisanya identik. Logika penghapusan sudah diuji terhadap port Python dari kedua implementasi lama: **2000/2000 kasus acak cocok untuk MSG_BUFFER, 2000/2000 untuk DASH_AUDIT**, plus kasus batas (sheet kosong, header saja, ts rusak di baris pertama, semua baris masih segar).

Perlu dicatat: `retention_days: 0` untuk DASH_AUDIT **dipertahankan apa adanya** — artinya tetap wipe penuh tiap kuartal, sama seperti sekarang. Kalau mau retensi 90 hari, ubah angka itu di node `Fan Out Jobs`.

---

## Setelah migrasi

`secret` Kirimi sekarang tinggal **2 salinan** (notifier + cleanup), dari sebelumnya 4. Begitu 2 notifier lama dihapus, sisa titik plaintext tinggal: `VIRA TS.json` (5×), `STATS Cleanup v3.json` (1×), dan tab CONFIG PCR. Rotasi secret paling enak dilakukan setelah semua itu beres sekalian.

---

## Belum digabung, sengaja

- `STATS Cleanup v3` + `VIRA-PCR - STATS Purge` — aturan retensinya beda beneran, keduanya sudah lolos QA dan mau dijalankan manual tanggal 1. Gabungkan setelah run Oktober berhasil.
- `Topic Harvester`, `Monthly Rollup`, `Follow-up AI Powered` — tidak punya kembaran di klien lain.
- `Dashboard API` — sudah punya build pipeline sendiri.
