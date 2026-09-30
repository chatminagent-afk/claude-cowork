---
name: n8n-referensi-node-mati
description: "Duplikasi/paste workflow n8n menambah sufiks angka ke NAMA NODE tapi tidak ke string $('...') di dalam kode JS — referensi jadi mati diam-diam kalau dibungkus try/catch"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c8117eff-be65-4842-aa66-da4a292d6f00
  modified: 2026-08-21T05:12:13.824Z
---

Saat node di-paste/di-duplikasi ke kanvas n8n yang sudah berisi node, n8n menambahkan sufiks angka
ke **nama node** (`Read FAQ` → `Read FAQ1`) tapi **tidak** menyentuh string literal di dalam kode
JavaScript node lain. Semua `$('Read FAQ')` langsung menunjuk node yang tidak ada.

`$(nama)` **melempar exception** kalau node tidak ditemukan. Kalau panggilannya dibungkus
`try/catch` yang mengembalikan `[]` (pola `grab()` di VIRA PCR), kegagalan jadi **senyap total**:
node "berhasil" jalan, tidak ada error, tapi datanya kosong selamanya.

**Kejadian nyata (2026-08-21):** `FAQ Retrieve1` di VIRA PCR memanggil `grab('Read PRODUK Data')`,
`grab('Read LINKS Data')`, `grab('Read FAQ')` sementara nama aktualnya berakhiran `1`. Akibatnya
`data_context` dan `faq_context` KOSONG untuk **setiap** pesan selama berminggu-minggu, dan model
mengarang harga rumah (Rp 1.150.000.000 untuk unit seharga Rp 409.294.258) ke lead sungguhan.
75 dari 81 node kena sufiks. `Process All1` selamat karena sudah memakai `$('Read LINKS Data1')`.
Kelas bug ini **sudah pernah terjadi** dan diperbaiki 2026-07-19 (entri #8/#9), lalu kembali.

**Why:** JSON valid + workflow jalan tanpa error TIDAK membuktikan referensi antar-node hidup.
Diagnosis yang berhenti di "outputnya kosong, berarti modelnya halu" akan salah menyalahkan LLM
dan menyarankan ganti model — padahal model tidak pernah menerima data sama sekali.

**How to apply:**
1. Setiap kali membaca/mem-patch workflow n8n, audit dulu: kumpulkan semua nama node, lalu
   cocokkan dengan semua string di `$('...')` **dan** pemanggilan helper seperti `grab('...')`.
   Regex `\$\('...'\)` saja TIDAK cukup — helper yang menerima nama lewat variabel akan terlewat;
   cari juga pemanggilan helper-nya per nama.
2. Curigai workflow yang mayoritas nama node-nya berakhiran angka — itu jejak paste/duplikasi.
3. Bandingkan dengan export arsip: kalau versi lama refs-nya valid dan yang live tidak, kerusakan
   masuk lewat duplikasi, bukan lewat edit kode.
4. Saat menulis helper pengambil data, beri **beberapa kandidat nama** (dengan dan tanpa sufiks)
   dan **jangan pernah** telan error diam-diam — minimal `console.error` + flag diagnostik yang
   ikut di-emit, supaya kegagalan berikutnya ketahuan dalam hitungan menit, bukan bulan.

Terkait: [[n8n-json-gaya-byte]], [[pending-changes-register]], [[persada-cisoka-status]],
[[laptop-tanpa-runtime-js]]
