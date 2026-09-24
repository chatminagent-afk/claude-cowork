# Panduan — Pasang Rekomendasi AI (WF-B)

Revisi 5 · 2026-09-06

## ⚡ Urutan singkat

1. Tambah kolom **`ai_insight_json`** di tab `MONTHLY_SUMMARY`
2. Import **`n8n/Monthly-Rollup-WF-B.json`** → ke workflow *Monthly Rollup (WF-B)*
   **yang sudah ada** (jangan bikin workflow baru)
3. Buka node **`Ask Anthropic`** → pilih credential *Anthropic The Scholars*
4. **Execute workflow** manual sekali → cek hasilnya di sheet
5. Aktifkan WF-B
6. Baru import Dashboard API → kartunya muncul

Import WF-B datang dalam keadaan **non-aktif** — sengaja. Aktifkan sendiri
setelah hasil eksekusi manual lo periksa.

---

## ⚠️ Jangan bikin workflow baru

Import ke workflow *Monthly Rollup (WF-B)* yang sudah ada. Kalau di-import
sebagai workflow baru lalu diaktifkan, **ada dua cron menulis baris yang sama**
tiap tanggal 1.

---

## Yang berubah di WF-B

Empat node lama **tidak disentuh sama sekali** — sudah gw verifikasi
byte-per-byte. Cabang AI berdiri sejajar, bukan menyisip:

```
Rollup Bulan Lalu ─┬─→ Write MONTHLY_SUMMARY        (jalur lama, utuh)
                   └─→ Read STATS for Insight
                        → Build Insight Request
                        → Ask Anthropic
                        → Prepare AI Column
                        → Write AI Column
```

Kenapa sejajar: apa pun yang terjadi pada Anthropic — mati, lambat, membalas
ngawur — **baris rekap bulanan tetap tertulis**. Rekap itu sudah jalan sejak
Agustus; menambah rekomendasi tidak boleh membuatnya bergantung pada layanan
luar. Ini pelajaran dari kesalahan gw di Dashboard API kemarin.

`Write AI Column` memakai `appendOrUpdate` yang mencocokkan `bulan`, sama
seperti node aslinya — jadi ia **memperbarui** baris bulan itu, bukan menambah
baris kedua.

**Node `Read STATS for Insight` ditambahkan** supaya saran bisa menyebut hari
("buka kelas hari Rabu"). Sebaran hari tidak ada di `TOPIC_LOG`; harus dari
`Tanggal Chat Terakhir` di STATS. Satu pembacaan sheet per bulan. Pakai
credential yang sama dengan node WF-B lainnya (SA bot, bukan SA dashboard).

---

## Langkah 4: eksekusi manual — apa yang terjadi

`Execute workflow` sekarang (6 Sept) akan memproses **bulan Agustus** — kode
rollup selalu mengambil bulan sebelumnya. Karena penulisannya mencocokkan
`bulan`, baris Agustus yang sudah ada **diperbarui**, bukan diduplikasi. Aman
dijalankan berkali-kali.

Yang harus lo cek setelahnya:

- Tab `MONTHLY_SUMMARY`, baris `2026-08` → kolom `ai_insight_json` terisi JSON
- Node `Ask Anthropic` di execution log → status hijau
- Kalau `ai_insight_json` kosong: buka node `Prepare AI Column` → console log-nya
  menyebut alasannya

Sekalian: setelah eksekusi manual, node Sheets di WF-B sudah "kenal" kolomnya.
Kalau mau import berikutnya bebas ritual, jalankan ini lalu import ulang:

```bash
python n8n/sync_sheets_schema.py
python n8n/build_wfb.py
```

---

## Biaya

**1 panggilan per bulan.** Bukan karena cache atau trik apa pun — cron-nya
memang jalan sebulan sekali. Tidak ada yang perlu diverifikasi.

Kalau bulan itu tidak punya topik sama sekali, `Build Insight Request`
mengembalikan nol item dan node Anthropic **tidak dijalankan** — nol permintaan,
nol biaya.

---

## Pagar yang dipasang

| Keadaan | Yang terjadi |
|---|---|
| Anthropic mati / lambat | Rekap tetap tertulis, kolom AI kosong, kartu tidak tampil |
| Balasan bukan JSON / terpotong | Kolom tidak ditulis sama sekali (bukan setengah jadi) |
| Butir tanpa judul atau aksi | Butir itu dibuang, sisanya tetap dipakai |
| Lebih dari 4 saran | Dipotong 4 |
| Bulan tanpa topik | AI tidak dipanggil |

Prompt-nya melarang mengarang angka, mewajibkan tiap saran menyebut angka
pendukung, dan melarang menyebut hari kalau sebarannya rata.

Data lead **tidak ikut** ke Anthropic — hanya agregat. Ada tes yang memastikan
tidak ada nomor WA maupun nama lead yang bocor ke prompt.

---

## Setelah WF-B beres

Import Dashboard API (`n8n/VIRA-Dashboard-API.json`). Kartu **Rekomendasi dari
Topik** akan muncul di bawah chart topik.

Ketujuh node Sheets-nya sekarang identik byte-per-byte dengan versi yang lo
jalankan, jadi ritual eksekusi–Retry–publish seharusnya tidak perlu lagi.
Kalau node `Append Lead` masih melapor "No columns found", kabari — jangan
diulang sendiri.

---

## Masih menggantung

**Toggle bot belum pernah lo verifikasi.** Coba sekali. Kalau `authentication`
memang penyebab masalah kemarin, kemungkinan besar toggle juga belum pernah
benar-benar jalan sejak Agustus.
