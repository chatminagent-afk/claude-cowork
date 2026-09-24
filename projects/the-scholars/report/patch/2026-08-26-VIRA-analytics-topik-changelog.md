# Changelog — Analytics Topik Bulanan VIRA (WF-A / WF-B / WF-C)

**Tanggal:** 2026-08-26
**Status:** dibangun & lulus QA otomatis — **belum di-import, belum diaktifkan**
**Rencana induk:** [`2026-08-26-rencana-analytics-topik-vira.md`](../../2026-08-26-rencana-analytics-topik-vira.md)
**Taksonomi:** [`2026-08-26-taksonomi-seed-topik.md`](../../2026-08-26-taksonomi-seed-topik.md)

> **Workflow VIRA utama (r6) TIDAK DISENTUH SAMA SEKALI.** Nol node diubah, nol
> connection diubah. Semua di bawah ini adalah workflow baru yang berdiri sendiri.

---

## Berkas yang dihasilkan

| Berkas | Isi |
|---|---|
| `2026-08-26-VIRA-WF-A-topic-harvester.json` | WF-A, 10 node — panen MSG_BUFFER 4x/hari |
| `2026-08-26-VIRA-WF-B-monthly-rollup.json` | WF-B, 4 node — rekap bulanan tanggal 1 |
| `2026-08-26-qa-WF-A-selftest.html` | QA WF-A, 39 pemeriksaan (buka di browser) |
| `2026-08-26-qa-WF-B-selftest.html` | QA WF-B, 32 pemeriksaan (buka di browser) |

Perubahan di proyek dashboard (`../VIRA Dashboard/2026-07-28-production/`):

| Berkas | Perubahan |
|---|---|
| `n8n/src/tenants.js` | +`MONTHLY_SUMMARY` di `tabs`, +blok `monthlySummary`, +`topicLabels` |
| `n8n/src/build-payload.js` | +5 fungsi generik (`vdBuildMonthly` dkk), +wiring di `vdBuildPayload` |
| `n8n/VIRA-Dashboard-API.json` | hasil rebuild (30 node, 273,6 KB) |
| `qa/fixtures/thescholars.json` | +2 baris `MONTHLY_SUMMARY` (sintetis) |
| `qa/fixtures/manifest.json` | +hitungan baris tab baru |
| `qa/preview-monthly.html` | **baru** — pratinjau visual blok bulanan tanpa perlu login |

---

## Hasil QA

| Suite | Hasil |
|---|---|
| QA WF-A (`2026-08-26-qa-WF-A-selftest.html`) | **39 / 39 lulus** |
| QA WF-B (`2026-08-26-qa-WF-B-selftest.html`) | **32 / 32 lulus** |
| Dashboard `qa/selftest.html` | **184 / 184 lulus** (tidak ada regresi) |
| Dashboard `qa/uitest.html` | **94 / 94 lulus** |
| Dashboard `qa/validate_workflow.py` | **24 / 24 lulus** |

Kode Code node **diambil apa adanya dari workflow JSON** oleh generator QA, jadi
yang diuji memang kode yang akan jalan di n8n — bukan salinan yang bisa menyimpang.

Mesin ini tidak punya Node.js, jadi QA dijalankan di browser — mengikuti pola
`qa/selftest.html` di proyek dashboard.

---

## Yang dibangun

### WF-A — `VIRA Topic Harvester`

Cron `0 1,7,13,19 * * *` (Asia/Jakarta). 10 node.

```
Every 6h -> Read State -> Read MSG_BUFFER -> Prepare Batches -> Classify Batch
         -> Aggregate -> Read TOPIC_LOG -> Merge Counts -> Write TOPIC_LOG
         -> Update Watermark
```

- **Watermark** disimpan di tab `ANALYTICS_STATE` (`key = msg_buffer_watermark`),
  bukan di `getWorkflowStaticData` — static data bisa hilang saat workflow disimpan
  ulang, dan itu akan menyebabkan panen ganda tanpa suara.
- **Klasifikasi**: 1 panggilan HTTP ke Anthropic per 40 pesan, model
  `claude-haiku-4-5-20251001`, `temperature: 0`, keluaran JSON array.
- **Nomor WhatsApp tidak pernah dikirim ke AI.** Payload hanya berisi indeks +
  teks pesan; nomornya dijodohkan kembali secara lokal di node `Aggregate`.
  Ada pemeriksaan QA khusus untuk ini.
- **Tidak ada data baru -> node `Prepare Batches` mengembalikan `[]`**, cabang
  berhenti. Tidak ada panggilan AI, tidak ada write. Run kosong = nol biaya.
- Semua node Sheets & HTTP: `retryOnFail`, 3 percobaan, jeda 5 detik.
- `errorWorkflow` diarahkan ke Fallback VIRA Error Email Notifier
  (`ZKsINjA7ZC8c9yRHWp3ud`), sama seperti workflow cleanup.

**Kenapa jam 01:00 (bukan 00:00 atau 02:00).** Cleanup MSG_BUFFER jalan
`0 3 * * *` dengan `RETENTION_MS = 2 jam`, jadi jam 03:00 ia menghapus baris
`ts < 01:00`. Run jam 01:00 menangkap **tepat sampai batas itu** — celah nol.
Kalau dijadwalkan jam 00:00, baris 00:00–01:00 terhapus sebelum sempat dipanen.

### WF-B — `VIRA Monthly Rollup`

Cron `30 0 1 * *` (Asia/Jakarta). 4 node.

- Menentukan bulan sasaran = bulan sebelum bulan berjalan **menurut WIB**.
  Diuji khusus terhadap jebakan zona waktu: 00:30 WIB tanggal 1 = 17:30 UTC
  tanggal 30/31 bulan sebelumnya. Kalau salah, laporan meleset satu bulan penuh.
- **Peringkat dihitung per USER UNIK**, bukan per pesan. Ada pemeriksaan QA
  eksplisit: 1 user yang bertanya 6x harus KALAH dari 2 user yang bertanya 1x.
- `lainnya` (sapaan, ucapan terima kasih, fragmen) **dihitung di total, tapi
  tidak ikut diperingkat**, dan dilaporkan terpisah di kolom `pesan_lainnya`.
- Bulan kosong tetap menulis baris berisi angka nol + catatan, bukan error dan
  bukan baris hilang — supaya dashboard menampilkan "0", bukan kekosongan.

### WF-C — Dashboard

Primitif baru `monthlySummary` di `build-payload.js`, **generik dan
multi-tenant** — tidak ada satu pun string spesifik The Scholars di dalamnya.
Klien berikutnya cukup menambah blok `monthlySummary` di entri tenant-nya.

Frontend `app/` **nol perubahan** (dikonfirmasi oleh gate
`qa/validate_workflow.py` §6 yang menggagalkan build kalau ada kebocoran).

Chart sengaja **tanpa `rangeAware`** → selektor 7/30/90 hari mengabaikannya dan
merender array penuh, sesuai aturan di API contract.

---

## Penyimpangan dari rencana induk — dan alasannya

### 1. `TOPIC_LOG` dapat kolom `row_key`

Rencana: `bulan | user_key | topic | jumlah_pesan | first_ts | last_ts`
Nyatanya: **`row_key` | bulan | user_key | topic | jumlah_pesan | first_ts | last_ts**

Node Google Sheets `appendOrUpdate` hanya bisa mencocokkan **satu kolom**,
sementara kunci logisnya gabungan tiga kolom. `row_key = bulan|user_key|topic`
menjadikannya satu kolom. Tanpa ini, upsert akan menimpa baris yang salah.

### 2. WF-B TIDAK memangkas `TOPIC_LOG`

Rencana menyebut pemangkasan setelah rollup. **Tidak saya kerjakan**, dengan tiga alasan:

1. Volumenya sepele — ~40 user x ~2 topik = ~80 baris/bulan, ~1.000 baris/tahun.
2. Menyimpannya berarti `MONTHLY_SUMMARY` bisa **dihitung ulang** kalau logika
   rollup berubah. Kalau dipangkas, angka lama tidak bisa dikoreksi selamanya.
3. Menghapus baris adalah operasi paling berisiko di sistem ini, dan proyek ini
   punya riwayat pahit di sana.

**Ini tidak melanggar syaratmu "jangan simpan semua chat".** `TOPIC_LOG` tidak
memuat teks percakapan sama sekali — hanya label topik dan angka. Teks pesan
dibuang di node `Aggregate` dan tidak pernah ditulis ke sheet mana pun.

Kalau nanti terasa menumpuk, pemangkasan bisa ditambahkan belakangan.

### 3. Dashboard hanya membaca `MONTHLY_SUMMARY`, bukan `TOPIC_LOG`

`TOPIC_LOG` adalah tabel kerja WF-A/WF-B dan terus tumbuh. Dashboard cukup baca
`MONTHLY_SUMMARY` (~12 baris/tahun) — beban API-nya praktis nol.

### 4. `MONTHLY_SUMMARY` punya kolom lebih banyak dari rencana

Tambahan: `topik_baru_json` (label `NEW:` untuk direview bulanan),
`pesan_lainnya`, `topik_terpakai`, `generated_at`.

### 5. Taksonomi 16 topik, bukan 12–15

15 dari analisis data nyata + `ielts_english_test` yang **sengaja dimasukkan
meski nilainya nol** — supaya kalau IELTS ternyata muncul di percakapan lanjutan
(yang tidak terlihat di `Pesan Pertama`), ada angkanya. Ditambah `lainnya`
untuk noise dan prefiks `NEW:` untuk penemuan topik baru.

### 6. Chart jadi "Komposisi Topik", bukan "Top 5 Topik"

Ditemukan saat pratinjau visual: doughnut menghitung persen dari **total irisan**,
sementara tabel menghitung dari **user unik**. Topik yang sama tampil 35,3% di
chart dan 41,9% di tabel — dua-duanya benar, tapi berdampingan terbaca seperti
angka yang bertabrakan.

Judul chart diubah jadi **"Komposisi Topik (5 terbesar)"** supaya persennya
terbaca sebagai porsi, dan angka "% User" yang otoritatif ada di tabel.

### 7. `alwaysOutputData: true` pada semua node read

Ketemu saat pemeriksaan akhir, dan ini akan menggigit tepat di **run pertama**.

Di run pertama, `ANALYTICS_STATE` dan `TOPIC_LOG` masih kosong. Node Google
Sheets yang membaca sheet kosong mengeluarkan **nol item** — dan di n8n, nol item
**menghentikan seluruh rantai di belakangnya tanpa memunculkan error.** WF-A akan
diam seolah sukses, dan tidak ada yang tahu sampai ada yang membuka sheet.

Semua node read di WF-A dan WF-B kini `alwaysOutputData: true`, jadi sheet kosong
mengirim satu item `{}` yang sudah ditangani kodenya. Pola ini sama dengan yang
sudah dipakai r6 di `Read STATS`, `Read User STATS`, `Read MSG_BUFFER`, dll —
alasannya kemungkinan besar persis sama.

Ada tes khusus untuk kondisi ini di kedua suite QA.

---

## Catatan ketergantungan — JANGAN diubah sepihak

> **Jadwal WF-A terikat mati pada cleanup MSG_BUFFER.**
> Cleanup: `0 3 * * *`, `RETENTION_MS = 2 jam`. Run WF-A jam 01:00 yang
> menanggung beban.
> **Kalau cron cleanup diubah atau `RETENTION_MS` dikecilkan, WF-A akan bocor
> diam-diam tanpa memunculkan error.** Ubah keduanya bersamaan, atau jangan
> sama sekali.

---

## Risiko yang diketahui & diterima

| Risiko | Dampak | Sikap |
|---|---|---|
| Blind spot `bot_mode = OFF` | 58% user tidak terekam | Diterima; ditulis apa adanya di `coverage_note` yang tampil di dashboard |
| Pesan non-teks dibuang `Chat Counter` | Undercount | Diterima |
| `Rate Limiter LID` buang >5 pesan/menit tanpa jejak | Undercount kecil | Diterima |
| 1 user ber-`lid` bisa terhitung 2x | Sedikit menggelembungkan user unik | Diterima, belum ada solusi |
| Crash antara `Write TOPIC_LOG` dan `Update Watermark` | `jumlah_pesan` satu user-topik bisa dobel di run berikutnya | Jendelanya satu node; tidak mengubah peringkat top-N secara berarti |
| Label AI meleset | Topik salah kategori | `temperature: 0` + taksonomi eksplisit; batch gagal parse tidak dihitung, dan kalau SEMUA batch gagal watermark tidak dimajukan supaya bisa diulang |

---

## Belum dikerjakan (menunggu tangan Steven)

1. **Buat 3 tab baru** di `The_Scholars_Database` — lihat panduan setup.
2. Import WF-A & WF-B ke n8n, pilih credential, uji manual, baru aktifkan.
3. Deploy dashboard (blocker #1–7 di runbook) — WF-C tidak terlihat sampai ini beres.
4. Optimasi 13 ops workflow utama — **jalur terpisah, belum disentuh sama sekali.**
