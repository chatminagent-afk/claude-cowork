# Tabel LINKS final — VIRA PCR (disambiguasi media)

**Tanggal:** 2026-07-18
**Sumber URL & Caption:** sheet `LINKS` di `workflow/PCR_Database.xlsx` (dibaca verbatim). URL dipertahankan dari baris lama sesuai planning §Langkah 1.
**Cara pakai:** salin ke sheet `LINKS` (Google Sheets / xlsx). Header WAJIB persis: `Nama Link | Tipe | Tipe Unit | Keyword | Status | URL | Caption | Deskripsi`.

> ⚠️ **URL masih DUMMY** (file contoh dari Steven / placeholder Drive). WAJIB diganti file asli + izin tim sebelum go-live (lihat checklist go-live §4/§6).
> ⚠️ **Row 8 lama** (`Contoh unit rumah type 3672 atau type 3681.jpeg`) **DIHAPUS** — tumpang-tindih dengan foto per-tipe.
> ℹ️ **Video 36/72 & 36/81 = satu file** -> dua baris dengan **URL sama**. Kode Process All men-dedup by URL, jadi tidak memicu ambiguitas palsu.
> ℹ️ Keyword `gambar` ditambahkan ke baris foto (sinonim `foto`) supaya permintaan "minta gambar" ikut terdeteksi seperti "minta foto" (lihat catatan deviasi di laporan akhir).

---

## Tabel (8 baris data)

| Nama Link | Tipe | Tipe Unit | Keyword | Status | URL | Caption | Deskripsi |
|---|---|---|---|---|---|---|---|
| brosur | image | umum | brosur, price list, pricelist | AKTIF | https://drive.google.com/uc?export=download&id=1K3F7Kj3YL199GQUOyspBEE-xFkqgBgYH | Ini brosur Persada Cisoka Residence yaa kak 😊 | Brosur resmi. Host ke Drive (Anyone with link) lalu set AKTIF. |
| foto-36-72 | image | 36/72 | foto, gambar, eksterior, 3672 | AKTIF | https://drive.google.com/uc?export=download&id=19QEUsWCGV_u227mFwCsN2fwVknX6JvUt | Ini foto unit tipe 36/72 di Persada Cisoka Residence kak 😊 | (nama file lama) tipe 36 72 - foto eksterior.jpeg |
| foto-36-81 | image | 36/81 | foto, gambar, eksterior, 3681 | AKTIF | https://drive.google.com/uc?export=download&id=1z20ZYoZ4nXl1X-7K_qq6wMPz3IbWSmRT | Ini foto unit tipe 36/81 di Persada Cisoka Residence kak 😊 | (nama file lama) tipe 36 81 - foto eksterior.jpeg. File dummy 720x1280, link uc publik 2026-07-17. |
| foto-30-60 | image | 30/60 | foto, gambar, eksterior, subsidi | AKTIF | https://drive.google.com/uc?export=download&id=1xT4EmlZ9uN9XEt8_8gsQdmcT4Sd2pWGZ | Ini foto unit tipe 30/60 subsidi di Persada Cisoka Residence kak 😊 | (nama file lama) tipe 30 60 subsidi - foto eksterior.jpeg |
| video-36-72 | video | 36/72 | video, 3672 | AKTIF | https://drive.google.com/uc?export=download&id=1gJPQYKOG4UK4XonHe6GIDYMDctlRtxXC | Ini video unitnya untuk tipe 36/72 atau 36/81 kak, silakan dilihat 😊 | (nama file lama) Video tipe 36 72 atau tipe 36 81.mp4 — satu file untuk 2 tipe (URL sama dg video-36-81). 8,2MB, publik & terkirim via API 2026-07-17. |
| video-36-81 | video | 36/81 | video, 3681 | AKTIF | https://drive.google.com/uc?export=download&id=1gJPQYKOG4UK4XonHe6GIDYMDctlRtxXC | Ini video unitnya untuk tipe 36/72 atau 36/81 kak, silakan dilihat 😊 | (nama file lama) Video tipe 36 72 atau tipe 36 81.mp4 — URL SAMA dengan video-36-72 (dedup by URL di kode). |
| video-30-60 | video | 30/60 | video, subsidi | AKTIF | https://drive.google.com/uc?export=download&id=1PbnT5SqQsSzI4B7dKTQbEj3-5uUZwip8 | Ini video unitnya untuk tipe 30/60 subsidi kak, silakan dilihat 😊 | (nama file lama) tipe 30 60 subsidi - video eksterior.mp4 |
| maps | document | umum | lokasi, maps, alamat | AKTIF | https://maps.app.goo.gl/bjyt4pytMM53KDzRA | Ini titik lokasi Persada Cisoka Residence ya kak 📍 | Link Google Maps dikirim sebagai teks/URL. Minta pin resmi ke tim. |
| website | document | umum | website | AKTIF | https://www.persadacisoka.com | Website resmi Persada Cisoka Residence | Halaman web, bukan file media. AI menyebut URL sbg teks. Jangan diaktifkan sbg attachment. |

---

## Key kanonik (harus konsisten dengan prompt block & logika Process All)

`brosur`, `foto-36-72`, `foto-36-81`, `foto-30-60`, `video-36-72`, `video-36-81`, `video-30-60`, `maps`, `website`.

Konvensi kolom baru:
- **Tipe Unit** — format `NN/NN` (mis. `36/72`) atau `umum`. Dipakai kode untuk menyamakan pola tipe (mis. mediaKey "36 72" -> normalisasi digit "3672" -> cocok `36/72`).
- **Keyword** — comma-separated. Dipakai kode saat exact match `Nama Link` gagal; cocok per-token terhadap mediaKey. Jangan pakai key generik yang bikin ambigu antar-jenis.
