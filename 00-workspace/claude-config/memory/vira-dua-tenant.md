---
name: vira-dua-tenant
description: VIRA melayani dua klien (The Scholars & Persada) — nama asli tidak boleh muncul di konten, pakai deskripsi generik
metadata:
  type: project
---

VIRA jalan multi-tenant, dua klien produksi (sumber: `VIRA-DASHBOARD/2026-07-28-production/n8n/src/tenants.js`):

| Tenant | Kontak | Bidang | Sebutan di konten |
|---|---|---|---|
| **The Scholars** | Sam | konsultan pendidikan / beasiswa; VIRA = "Sam versi AI" | "klien yang platform edukasi" |
| **Persada** | Om Sulianto | developer properti | "klien yang developer properti" |

**Aturan konten: nama asli kedua klien tidak boleh pernah disebut** — di reels, caption, Threads, maupun screenshot. Selalu pakai deskripsi generik di atas.

Kontras keduanya berguna sebagai bahan cerita "kenapa template nggak jalan": klien edukasi butuh AI yang sabar & ngejelasin pelan (yang chat lagi mikirin keputusan besar), klien properti butuh AI yang cepat ngajak survei & follow up (yang chat lagi bandingin pilihan). Dipakai tanpa nama, ini aman.

Dashboard punya akun demo (`steven`/`sam`/`sulianto`, password `demo`) dengan angka palsu — file `demo/VIRA-Dashboard-DEMO.html` aman dibagikan. Yang JANGAN di-upload: `qa/` dan `docs/` (memuat file password).

Fakta & angka yang aman dipakai: [[vira-fakta-konten]].
