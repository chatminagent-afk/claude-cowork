---
name: excel-sumber-flow-bukan-file-lokal
description: File Excel lokal di folder proyek BUKAN file yang dibaca flow Power Automate — flow membaca copy SharePoint dengan nama berbeda
metadata: 
  node_type: memory
  type: project
  originSessionId: 52626e2e-6813-41c2-a9bd-83aeff9b34db
  modified: 2026-08-19T03:53:12.673Z
---

Flow Weekly MBI Projects Report membaca `/Status UAT dan Imple/Tracking Project MBI.xlsx`
di SharePoint `bcaoffice365.sharepoint.com/sites/Ateam786` (file id `01IN3HZD33YHZVASU6DNGKWMERDX5OO3RZ`),
lewat tabel `TableProjectTesting`, `Table5`, `TableSupport`.

File lokal di folder proyek bernama **`Tracking Project MBI (di luar paketan).xlsx`** — nama
berbeda, jadi jangan diasumsikan identik. Struktur kolomnya cocok dengan yang dipakai flow,
tapi jumlah baris dan isi bisa tertinggal dari yang live.

**Why:** analisis apa pun yang dilakukan atas file lokal (hitung ulang recap, cek isi kolom)
hanya valid sebagai perkiraan. Kesimpulan "kolom X kosong" atau "totalnya N" harus
diverifikasi ulang ke file SharePoint sebelum dipakai untuk keputusan produksi.

**How to apply:** kalau menganalisis data untuk flow ini, sebut eksplisit bahwa angkanya
berasal dari copy lokal dan minta Steven cek silang ke SharePoint. Jangan ubah file lokal
dengan harapan flow ikut berubah.

Terkait: [[flow-mbi-report-v6]]
