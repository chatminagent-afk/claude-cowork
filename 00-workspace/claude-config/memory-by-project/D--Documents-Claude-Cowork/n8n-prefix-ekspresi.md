---
name: n8n-prefix-ekspresi
description: Nilai parameter n8n yang diawali "=" adalah penanda expression mode — jangan pernah dibuang saat mem-patch workflow JSON
metadata:
  type: project
---

Di berkas ekspor workflow n8n (VIRA), string parameter yang diawali `=` bukan typo —
itu penanda **expression mode**. Di v3.2 ada 158 string seperti itu, termasuk
`AI Agent → parameters.options.systemMessage`, yang isinya memuat 6 ekspresi hidup:
`{{ $json.prospect_context }}`, `brief_context`, `about_context`, `program_context`,
`links_context`, `faq_context`.

Kalau `=` dihapus, field pindah ke fixed mode dan keenam injeksi konteks itu tercetak
mentah sebagai teks — VIRA kehilangan seluruh konteks prospect/brief/about/program/
links/FAQ tanpa error apa pun. UI n8n menyembunyikan prefix ini, jadi memeriksa lewat
UI tidak akan memperlihatkannya.

**Cara pakai:** setiap skrip `_patch_*.py` yang menyentuh systemMessage harus
`assert sp.startswith("=")` sebelum menulis, dan menulis berkas `.md` pendampingnya
dari `sp[1:]` (tanpa `=` — itu bentuk bacanya). Lihat `workflow/_patch_2026-09-06c.py`
sebagai contoh.

Terkait: [[vira-personal-deploy]]
