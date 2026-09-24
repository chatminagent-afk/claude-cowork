# VIRA Dashboard — production

Dashboard performa & direktori lead untuk bot VIRA. Satu kode, melayani banyak
klien; tiap owner hanya bisa melihat datanya sendiri.

**Status:** siap deploy. QA 257 pemeriksaan, 0 gagal. Belum pernah dijalankan
terhadap instance n8n sungguhan — ada checklist smoke test wajib.

## Lihat dulu tanpa setup apa pun

**`demo/VIRA-Dashboard-DEMO.html` — klik dua kali.** Tanpa server, tanpa n8n,
tanpa internet, tanpa Google service account.

Akun (kata sandi semuanya `demo`):

| Akun | Melihat |
|---|---|
| `steven` | kedua klien, bisa berpindah lewat pemilih di header |
| `sam` | The Scholars saja — pemilih klien tidak muncul |
| `sulianto` | Persada saja |

Semuanya berjalan: chart, filter, pencarian, urut kolom, paginasi, drawer detail,
dan toggle bot_mode lengkap dengan konfirmasi. Yang berubah hanya di dalam
halaman itu — tidak ada yang menyentuh sistem asli.

Angkanya dibuat-buat. Nama kolomnya asli (dibaca dari kedua spreadsheet
produksi), tapi tidak ada satu pun nomor WhatsApp atau nama pelanggan yang nyata,
dan tidak ada kredensial di dalamnya — jadi berkas ini **aman dikirim** ke Sam
atau Om Sulianto untuk minta masukan sebelum integrasi.

Kalau `app/` diubah, rakit ulang:

```bash
python demo/build_demo.py
```

## Mulai dari mana

| Kalau kamu mau… | Buka |
|---|---|
| memasang ini ke produksi | `docs/2026-07-28-DEPLOY-README.md` |
| tahu apa saja yang diuji dan apa yang belum | `docs/2026-07-28-UAT-report.md` |
| baca temuan di luar dashboard + saran | `docs/2026-07-28-konsultasi-rekomendasi.md` |
| mengubah kode | `docs/2026-07-28-API-CONTRACT.md` dulu |
| password owner | `docs/KREDENSIAL-JANGAN-DIBAGIKAN.txt` |

## Isi

```
app/    -> upload folder INI saja ke hosting statis (tanpa build step)
demo/   -> VIRA-Dashboard-DEMO.html, satu berkas, buka langsung. Aman dibagikan.
n8n/    -> src/*.js  = sumber kebenaran kode Code node
           build_workflow.py -> VIRA-Dashboard-API.json (import ke n8n)
qa/     -> test + mock server. JANGAN di-upload.
docs/   -> dokumentasi (memuat file password — JANGAN di-upload)
```

## Perintah

```bash
python n8n/build_workflow.py
```

```bash
python qa/validate_workflow.py
```

```bash
python qa/serve.py
```

Setelah `serve.py` jalan, **dua-duanya** harus menampilkan **SEMUA LOLOS**
sebelum apa pun di-deploy:

- `http://localhost:8099/qa/selftest.html` — fungsi murni & normalisasi data (183)
- `http://localhost:8099/qa/uitest.html` — DOM & event listener (94)

## Dua hal yang paling mudah salah

1. **Jangan edit Code node lewat UI n8n.** Isinya di-generate dari `n8n/src/`;
   editan di UI hilang saat rebuild berikutnya.
2. **Jangan upload `qa/` atau `docs/`** ke hosting. Hanya `app/`.
