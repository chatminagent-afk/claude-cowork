---
name: stats-kolom-berspasi
description: "3 kolom pending_survey_* di sheet STATS namanya berakhir SPASI; node penulis cocok tapi node pembaca tidak — perbaiki sisi BACA, jangan ubah header sheet"
metadata: 
  node_type: memory
  type: project
  originSessionId: 448502b0-0538-4fb0-86dd-16c90e53394b
  modified: 2026-09-11T08:59:59.227Z
---

Sheet STATS (PCR_Database) punya 3 kolom yang **namanya berakhir spasi**:

```
'pending_survey_tanggal '
'pending_survey_jam '
'pending_survey_unit '
```

`pending_survey_ts` **tidak** berspasi. Sheet SURVEY sudah dicek dan bersih — tidak ada jebakan
serupa di sana.

Akibatnya sebelum patch 2026-09-10: `Update to STATS` **menulis** dengan nama berspasi (cocok dengan
header, jadi datanya masuk), tapi `Cek_user_status` dan `Resolve User Row` **membaca** tanpa spasi →
selalu `undefined` → `PENDING_SURVEY` di prompt selalu `-`. Register slot survey lintas giliran mati
sejak awal tanpa satu pun error.

**Jangan perbaiki dengan menghapus spasi di header sheet.** Yang akan rusak adalah node
**penulis**: mapping kolom `Update to STATS` memakai nama berspasi dan saat ini cocok. Menghapus
spasi menuntut re-map manual 3 kolom di UI n8n, dan ada jendela di mana penulisan gagal.

Perbaikan yang dipakai (V1.5): helper `colPS(obj, base)` di kedua node pembaca — coba nama berspasi
dulu, lalu tanpa spasi. Toleran dua arah, jadi tetap jalan kalau header dibersihkan di kemudian hari.

**Why:** nama kolom sheet adalah kontrak antara sheet dan setiap node yang menyentuhnya. Sisi tulis
dan sisi baca bisa tidak sinkron tanpa gejala apa pun, karena JS mengembalikan `undefined` alih-alih
melempar error.

**How to apply:** sebelum menyentuh node mana pun yang membaca kolom sheet, ambil daftar kolom
otoritatif dari `parameters.columns.schema` yang di-cache node n8n (mis. `Update to STATS`,
`Update STATS Survey`) dan bandingkan dengan setiap akses `row['nama_kolom']` di semua code node —
cetak pakai `repr()` supaya spasi di ujung kelihatan. Jalankan audit itu sebagai bagian QA, bukan
hanya saat curiga.

Terkait: [[n8n-referensi-node-mati]], [[laptop-tanpa-runtime-js]], [[vira-prompt-minim-hardcode]]
