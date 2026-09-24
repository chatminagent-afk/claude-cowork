# Mulai di sini

Semalam saya bangun analytics topik bulanan. **Cukup baca file ini.**
File lain hanya rujukan kalau ada yang mau dicek.

---

## Yang sudah jadi

Tiga workflow n8n baru + satu blok baru di dashboard. **Workflow VIRA utama tidak
disentuh sama sekali** — kalau semuanya gagal, bot tetap jalan normal.

Semua lulus QA otomatis. Tapi **belum pernah jalan di n8n asli** — itu bagianmu.

---

## Yang perlu kamu lakukan

Urutannya penting. Total ~35 menit.

### 1. Buat 3 tab di `The_Scholars_Database` (10 menit)

Nama tab dan kolom **harus persis**, peka huruf besar-kecil.

**`ANALYTICS_STATE`** — baris 1:
```
key | value | updated_at
```

**`TOPIC_LOG`** — baris 1:
```
row_key | bulan | user_key | topic | jumlah_pesan | first_ts | last_ts
```

**`MONTHLY_SUMMARY`** — baris 1:
```
bulan | total_user_unik | total_pesan | top_json | topik_baru_json | pesan_lainnya | topik_terpakai | coverage_note | generated_at
```

Biarkan kosong di bawah header. Workflow yang mengisi.

### 2. Import WF-A, uji manual, baru aktifkan (15 menit)

File: `report/patch/2026-08-26-VIRA-WF-A-topic-harvester.json`

Setelah import, **jangan langsung aktifkan.** Klik **Execute Workflow** manual:

- **Run pertama** → buka `TOPIC_LOG`. Yang wajib dicek:
  - kolom **`row_key` terisi** (bentuknya `2026-08|628xxx|nama_topik`) — **bukan kosong**
  - `topic` masuk akal, `jumlah_pesan` > 0
  - **tidak ada teks chat asli** di kolom mana pun
  - `ANALYTICS_STATE` dapat 1 baris watermark
- **Run kedua**, langsung tanpa jeda → **harus tidak terjadi apa-apa.**
  Tidak ada baris baru, angka tidak bertambah.

> Kalau `row_key` kosong / semua kolom kosong → **berhenti**, kabari saya.
> Kalau di run kedua angkanya bertambah → **berhenti** juga, berarti watermark
> tidak bekerja dan data akan menggelembung tiap 6 jam.

### Kalau sudah terlanjur run versi lama (26 Agustus)

Versi WF-A pertama menulis baris kosong. Sudah diperbaiki, tapi perlu dibereskan:

1. Hapus workflow WF-A yang lama di n8n, import ulang file yang baru
2. Hapus baris kosong di `TOPIC_LOG`
3. **Hapus baris `msg_buffer_watermark` di `ANALYTICS_STATE`** — ini penting.
   Run kemarin sudah memajukan watermark, jadi pesan-pesan itu ditandai "sudah
   dipanen" padahal tidak pernah tercatat. Menghapusnya membuat pesan yang masih
   ada di `MSG_BUFFER` ikut terpanen lagi.
4. Execute manual, ulangi pemeriksaan di atas

Kalau dua-duanya benar → aktifkan.

### 3. Import WF-B, aktifkan (10 menit)

File: `report/patch/2026-08-26-VIRA-WF-B-monthly-rollup.json`

Execute manual sekali. Karena Juli belum ada datanya, dia akan menulis satu baris
berisi angka nol — **itu benar, bukan error.** Lalu aktifkan.

Cara mengujinya dengan data betulan ada di panduan setup, tapi tidak wajib sekarang.

### 4. Dashboard — nanti saja

Blok topiknya sudah siap, tapi baru kelihatan setelah dashboard dideploy.
Itu pekerjaan terpisah, ada runbook-nya sendiri. Tidak menghalangi langkah 1–3.

---

## Kapan hasilnya kelihatan

| Data bulan | Laporan muncul |
|---|---|
| September (parsial, dari hari WF-A aktif) | 1 Oktober |
| Oktober (bulan penuh pertama) | 1 November |

**Makin cepat langkah 2 selesai, makin banyak September yang tertangkap.**
Ini satu-satunya bagian yang punya jam berdetak — sisanya bisa menyusul.

---

## Keputusanmu sudah saya kerjakan

| Keputusan | Hasil |
|---|---|
| Cache 120 detik | ✅ Dibangun jadi **r8**, 24/24 QA lulus. Langkah 5 di bawah. |
| Laporan Sam | ⏸️ Saya diamkan. Ada di `2026-08-26-laporan-baseline-untuk-sam.md`, tunggu kamu review. |
| Update `memory.md` | ✅ Sudah, hanya menambah. |

---

## 5. Patch r8 — hemat 31% operasi Sheets (opsional, terpisah)

File: `report/patch/2026-08-26-VIRA-r8-cache-static-tabs.json`

**Ini menyentuh workflow VIRA utama** — beda dari langkah 1–4 yang tidak menyentuh
apa pun. Kerjakan setelah analytics jalan, jangan barengan.

Isinya: bot mengingat isi 4 tab (FAQ, PROGRAM, ABOUT, LINKS) selama 120 detik,
jadi tidak membacanya ulang tiap pesan. **13 operasi jadi 9.** Sudah termasuk r7
(buang satu pembacaan LINKS yang dobel) — jadi import r8 saja, tidak perlu r7.

Cara ujinya sebelum dipakai:

1. Import, **jangan aktifkan**, matikan dulu workflow VIRA yang lama
2. Kirim pesan tes dari nomormu → bot harus membalas normal
3. Kirim pesan kedua **dalam 2 menit** → masih normal (ini yang pakai cache)
4. Minta link GForm → **link harus tetap terkirim** (ini bagian paling rawan,
   karena saat cache aktif node pembaca LINKS memang dilewati)
5. Tunggu >2 menit, kirim lagi → normal (cache kedaluwarsa, baca ulang)
6. Coba ubah satu baris di tab PROGRAM → dalam 2 menit bot masih pakai data lama,
   setelah itu ikut yang baru. **Itu perilaku yang benar, bukan bug.**

> Kalau langkah 4 gagal, kembalikan ke workflow lama dan kabari saya.

---

## File lain (kalau perlu saja)

| File | Kapan dibuka |
|---|---|
| `report/patch/2026-08-26-VIRA-analytics-topik-panduan-setup.md` | Kalau langkah 1–3 bermasalah |
| `report/patch/2026-08-26-VIRA-analytics-topik-changelog.md` | Kalau mau tahu keputusan teknis & penyimpangan dari rencana |
| `report/patch/2026-08-26-VIRA-analisa-efisiensi-13-ops.md` | Kalau mau tahu kenapa cuma caching yang saya kerjakan, dan apa yang sengaja TIDAK saya sentuh |
| `2026-08-26-taksonomi-seed-topik.md` | Kalau mau lihat data mentah di balik laporan Sam |
| `report/patch/2026-08-26-qa-*.html` | Kalau mau lihat hasil QA (buka di browser) |
