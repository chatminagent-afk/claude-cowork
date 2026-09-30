---
name: vira-steven-jalan-di-nomor-pribadi-campuran
description: "Nomor device VIRA Steven (6285155202354) adalah nomor WA bisnis pribadi Steven yang juga dipakai rekan BCA, urusan kerja lain, dan keluarga"
metadata: 
  node_type: memory
  type: project
  originSessionId: 226a5d21-ea40-40ff-b33c-3d5aecf14bc0
  modified: 2026-08-16T17:28:27.255Z
---

Bot VIRA Steven berjalan di device Kirimi `D-XKA2P` pada nomor **6285155202354** — dan
nomor itu **bukan nomor khusus bot**. Itu nomor WhatsApp bisnis pribadi Steven yang juga
dipakai untuk: rekan kerja/nomor kantor BCA, berbagai urusan pekerjaan lain, dan saudara.
Nomor admin penerima notifikasi **6285171701168** adalah HP Steven yang lain.

Yang Steven inginkan: **hanya lead dari iklan Instagram Reels** yang dibalas VIRA. Semua
chat lain (rekan BCA, keluarga, kerjaan non-VIRA) tidak boleh disentuh bot sama sekali.

**Why:** workflow ini diturunkan dari template Persada yang memakai model **blocklist /
default-ALLOW** ("bot ini publik, semua orang boleh masuk") — asumsi itu valid untuk nomor
bot khusus, tapi berbahaya di nomor campuran seperti ini. Risikonya bukan cuma salah balas:
Steven pegawai bank, dan bot AI yang membalas otomatis chat rekan kantor BCA adalah risiko
profesional, bukan sekadar bug kosmetik.

**How to apply:** setiap desain gating nomor untuk VIRA Steven harus **default-DENY**, bukan
default-allow. Jangan pernah mengusulkan solusi yang mengharuskan Steven mengetik manual
nomor-nomor yang mau di-OFF-kan — daftar itu tidak berhingga dan tumbuh terus. Pintu masuk
otomatis satu-satunya yang aman adalah token/kata kunci dari iklan (link `wa.me/...?text=`
di CTWA Instagram), karena hanya lead iklan yang membawanya. Rekomendasi paling tuntas
tetap: nomor terpisah khusus VIRA. Lihat [[vira-steven-aksi-lewat-tag-bukan-tool]] dan
[[kuota-google-sheets-lintas-klien]].
