# Panduan Setup — Analytics Topik Bulanan VIRA

**Tanggal:** 2026-08-26
**Untuk:** Steven
**Changelog:** [`2026-08-26-VIRA-analytics-topik-changelog.md`](2026-08-26-VIRA-analytics-topik-changelog.md)

Estimasi **~35 menit**. Tidak ada satu langkah pun yang menyentuh workflow VIRA
utama. Kalau semuanya gagal, bot tetap jalan seperti biasa.

---

## Langkah 1 — Buat 3 tab baru (~10 menit)

Di spreadsheet **`The_Scholars_Database`**
(`1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE`).

Nama tab dan nama kolom **peka huruf besar-kecil** dan harus persis. Salah satu
huruf saja, workflow akan gagal atau menulis ke kolom kosong.

### Tab `ANALYTICS_STATE`
Baris 1:
```
key | value | updated_at
```
Biarkan kosong di bawahnya. WF-A yang akan mengisi barisnya sendiri.

### Tab `TOPIC_LOG`
Baris 1:
```
row_key | bulan | user_key | topic | jumlah_pesan | first_ts | last_ts
```

### Tab `MONTHLY_SUMMARY`
Baris 1:
```
bulan | total_user_unik | total_pesan | top_json | topik_baru_json | pesan_lainnya | topik_terpakai | coverage_note | generated_at
```

> `top_json` akan berisi JSON panjang. Jangan diformat, jangan diberi wrap —
> biarkan sebagai teks biasa.

- [ ] `ANALYTICS_STATE` dibuat
- [ ] `TOPIC_LOG` dibuat
- [ ] `MONTHLY_SUMMARY` dibuat

---

## Langkah 2 — Import WF-A (~5 menit)

- [ ] n8n → Import from File → `report/patch/2026-08-26-VIRA-WF-A-topic-harvester.json`
- [ ] Cek 5 node Google Sheets sudah memakai credential
      **`Google Service Account thescholars`** (harusnya otomatis, ID-nya sama
      dengan yang dipakai bot)
- [ ] Cek node **`Classify Batch`** memakai credential Anthropic
      **`Anthropic Personal`**
- [ ] **JANGAN aktifkan dulu**

> **Soal credential Anthropic.** Node `Classify Batch` memakai HTTP Request
> dengan `predefinedCredentialType: anthropicApi`. Kalau n8n-mu tidak menawarkan
> pilihan itu, ganti ke **Generic Credential Type → Header Auth** dengan header
> `x-api-key` berisi API key Anthropic. Header `anthropic-version: 2023-06-01`
> sudah terpasang dan harus tetap ada.

> **Soal kuota Sheets.** WF-A memakai service account yang sama dengan bot,
> tapi bebannya hanya ~8–12 operasi **per hari** (bandingkan ~650/hari dari
> workflow utama). Kalau nanti SA dashboard sudah dibuat, tinggal ganti
> credential di 5 node itu.

---

## Langkah 3 — Uji manual WF-A ⚠️ SEBELUM diaktifkan (~10 menit)

Ini bagian yang menentukan. Jalankan **Execute Workflow** manual.

### 3.1 Run pertama
- [ ] Klik **Execute Workflow**
- [ ] Buka tab `TOPIC_LOG` → harus muncul baris baru
- [ ] Periksa isi `topic` — masuk akal untuk pesannya? Kalau semuanya `lainnya`,
      berarti klasifikasi gagal (cek output node `Classify Batch`)
- [ ] Buka `ANALYTICS_STATE` → harus ada 1 baris:
      `key = msg_buffer_watermark`, `value` = angka epoch milidetik
- [ ] **Pastikan tidak ada kolom mana pun yang memuat teks chat asli.**
      `TOPIC_LOG` hanya boleh berisi label topik dan angka.

### 3.2 Run kedua — ini yang membuktikan tidak ada hitung ganda
- [ ] Klik **Execute Workflow** lagi, langsung, tanpa menunggu
- [ ] **Harus tidak terjadi apa-apa**: tidak ada baris baru di `TOPIC_LOG`,
      `jumlah_pesan` tidak bertambah, tidak ada panggilan AI

Kalau angkanya bertambah di run kedua, **hentikan** — watermark tidak bekerja
dan datanya akan menggelembung tiap 6 jam.

### 3.3 Baru aktifkan
- [ ] Aktifkan WF-A. Cron `0 1,7,13,19 * * *` WIB.

---

## Langkah 4 — Import & uji WF-B (~10 menit)

- [ ] Import `report/patch/2026-08-26-VIRA-WF-B-monthly-rollup.json`
- [ ] Cek 2 node Sheets punya credential
- [ ] **JANGAN aktifkan dulu**

### Cara mengujinya tanpa menunggu tanggal 1

WF-B merekap **bulan lalu**. Hari ini Agustus, jadi sasarannya Juli — dan Juli
tidak punya data. Jalankan apa adanya dulu:

- [ ] Execute Workflow → `MONTHLY_SUMMARY` harus dapat 1 baris `bulan = 2026-07`
      dengan angka nol dan catatan "Belum ada data untuk bulan ini."
      Ini perilaku yang benar, bukan error.

Untuk menguji perhitungan yang sesungguhnya:

- [ ] Tambahkan **manual** 3 baris uji di `TOPIC_LOG` (hapus lagi setelah selesai):

| row_key | bulan | user_key | topic | jumlah_pesan | first_ts | last_ts |
|---|---|---|---|---|---|---|
| `2026-07\|TEST1\|biaya_program` | 2026-07 | TEST1 | biaya_program | 6 | 1 | 2 |
| `2026-07\|TEST2\|jadwal_kelas_waktu` | 2026-07 | TEST2 | jadwal_kelas_waktu | 1 | 1 | 2 |
| `2026-07\|TEST3\|jadwal_kelas_waktu` | 2026-07 | TEST3 | jadwal_kelas_waktu | 1 | 1 | 2 |

- [ ] Execute Workflow lagi
- [ ] Baris `2026-07` harus jadi: `total_user_unik = 3`, `total_pesan = 8`, dan
      **`jadwal_kelas_waktu` di peringkat 1** (2 user) mengalahkan
      `biaya_program` (1 user, walau 6 pesan)

Kalau `biaya_program` yang menang, peringkatnya memakai jumlah pesan — salah,
dan angka yang dilihat Sam akan bisa digelembungkan satu orang cerewet.

- [ ] **Hapus 3 baris uji** dari `TOPIC_LOG`
- [ ] Hapus juga baris `2026-07` dari `MONTHLY_SUMMARY`
- [ ] Aktifkan WF-B. Cron `30 0 1 * *` WIB.

---

## Langkah 5 — Dashboard (setelah deploy)

Bagian dashboard sudah dikerjakan dan lulus QA, tapi **baru terlihat setelah
dashboard-nya dideploy** — lihat
[`../../VIRA Dashboard/2026-08-26-runbook-deploy.md`](../../../VIRA%20Dashboard/2026-08-26-runbook-deploy.md).

Yang sudah siap di sana:
- KPI **User Chat Bulan Lalu** dan **Pesan Bulan Lalu**
- Doughnut **Komposisi Topik (5 terbesar) — <Bulan Tahun>**
- Tabel **Peringkat Topik — <Bulan Tahun>** (Topik / User / % User / Pesan)
- Catatan cakupan (blind spot 58%) tampil di bawah tabel

Ingat saat `build_workflow.py` dijalankan ulang: `GOOGLE_CRED_ID` masih
placeholder, dan `HMAC_SECRET` masih perlu dirotasi (Langkah 0 di runbook).

Pratinjau tampilannya tanpa perlu deploy/login:

```bash
python qa/serve.py
```

lalu buka `http://localhost:8099/qa/preview-monthly.html`.

---

## Kalau bermasalah

| Gejala | Penyebab |
|---|---|
| `TOPIC_LOG` tetap kosong setelah run | `MSG_BUFFER` memang kosong (semua user `bot_mode = OFF`, atau memang belum ada chat), atau nama tab salah ketik |
| Semua topik jadi `lainnya` | Node `Classify Batch` gagal — cek responsnya. Kalau 401, credential Anthropic salah |
| `jumlah_pesan` naik terus tiap run | Watermark tidak tersimpan — cek `ANALYTICS_STATE` punya header `key`/`value` persis |
| Workflow error "Semua batch gagal diklasifikasi" | Ini **disengaja**. AI tidak mengembalikan JSON valid; watermark tidak dimajukan supaya bisa diulang. Cek output `Classify Batch`. |
| Baris `TOPIC_LOG` tertimpa/salah | Kolom `row_key` kosong atau tidak jadi matching column |
| Laporan meleset satu bulan | Timezone workflow bukan `Asia/Jakarta` — cek Settings tiap workflow |

---

## Kapan hasilnya bisa dilihat

| Bulan data | Laporan tampil | Catatan |
|---|---|---|
| Agustus 2026 | — | Sudah lewat separuh, data sudah tersapu cleanup |
| September 2026 | 1 Oktober | Parsial — mulai dari tanggal WF-A diaktifkan |
| Oktober 2026 | 1 November | **Bulan penuh pertama** |

Makin cepat WF-A aktif, makin banyak September yang tertangkap. Ini satu-satunya
bagian yang punya jam berdetak — sisanya bisa menyusul.
