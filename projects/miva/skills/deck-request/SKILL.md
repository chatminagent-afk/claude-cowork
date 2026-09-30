---
name: deck-request
description: Susun pitch deck MIVA dari brief REQUESTS, kirim ke Steven untuk direview, lalu kirim ke klien lewat WhatsApp setelah Steven approve. Pakai kapan pun Steven menyebut ada permintaan deck atau menyebut nomor WA prospek — trigger pada frasa seperti "ada deck request 628xxx", "generate deck", "bikinin deck buat", "cek request baru", "deck buat <nama bisnis>", "kirim decknya ke klien", "revisi decknya", "briefnya kurang apa", atau saat dia meneruskan notifikasi WA dari MIVA (nama lama: VIRA) yang berisi brief prospek. Juga dipakai untuk merevisi deck yang sudah digenerate sebelum dikirim, dan untuk melengkapi brief yang field-nya kosong.
---

# Deck Request — generate, review, kirim

Alur "Claude in the loop": Steven tidak lagi menggenerate deck sendiri. Claude yang menyusun,
mengirim PDF-nya ke Steven untuk direview, dan baru mengirim ke klien setelah Steven bilang kirim.

Semua skrip ada di `D:\Documents\Claude Cowork\MIVA\MIVA Steven\deck`. Jalankan dari folder itu.

## Aturan yang tidak boleh dilanggar

1. **Jangan pernah mengirim ke klien tanpa Steven bilang kirim di percakapan ini.** Tampilkan
   dulu pratinjaunya (nomor tujuan, nama klien, berkas, caption persis), tunggu jawabannya.
   Nomor tujuan diambil dari sheet, jangan pernah dikira-kira sendiri.
2. **Fakta yang tidak diketahui tidak ditebak.** Field brief kosong → slide yang membutuhkannya
   dibuang atau diisi kalimat umum oleh generator. Jangan mengarang isi brief supaya slidenya
   "penuh". Kalau ada field kosong, jalankan prosedur **Field kosong** di bawah.
3. **Tiga field wajib: `nama_bisnis`, `industri`, `masalah_utama`.** Kalau salah satunya kosong,
   `buat_deck.py` berhenti sebelum menulis apa pun (exit 2), dan `kirim_deck.py` menolak kirim ke
   klien. `--lanjut-tanpa <field>` HANYA boleh dipakai setelah Steven, **di percakapan ini**,
   bilang jelas boleh lanjut tanpa field itu — per field, disebut namanya. Izin untuk satu klien
   tidak berlaku untuk klien lain. Jangan pernah menyarankan `--lanjut-tanpa` sebagai jalan pintas.
4. **Usulan isi hanya dari fakta yang sudah tertulis, dan baru ditulis setelah Steven setuju.**
   Lihat prosedur Field kosong.
5. **Kalau `PERIKSA` gagal atau slide wajib kena aturan pembuangan, hentikan** dan laporkan apa
   adanya. Jangan kirim deck yang halamannya tidak sesuai atau yang teksnya terpotong.

## Langkah

**1. Lihat briefnya**

```
python cek_request.py --belum
```

Menampilkan tiap baris REQUESTS yang decknya belum dikirim: nama bisnis, jumlah field terisi,
`status` (siap digenerate / BUTUH KONFIRMASI STEVEN — field wajib kosong), `peringatan`
(field penentu slide yang kosong), dan apakah PDF lokalnya sudah ada. Kalau Steven sudah
menyebut nomornya, langsung ke langkah 2.

**2. Susun decknya**

```
python buat_deck.py --wa 628xxxxxxxxxx --bersih
```

Baca sheet live lewat service account; kalau gagal dia jatuh ke `MIVA Database.xlsx` **dan
mencetak alasannya** — kalau baris `SUMBER` menyebut xlsx, bilang ke Steven, karena datanya
mungkin basi.

Blok `LENGKAP` dicetak paling awal:

| Label | Arti |
|---|---|
| `BLOKIR` | field wajib kosong — generator **berhenti** (`DIHENTIKAN: ...`, exit 2), tidak ada berkas yang ditulis |
| `PERINGATAN` | field penentu slide kosong — deck tetap jadi, tapi ada slide dibuang atau isinya umum |
| `CATATAN` | pelengkap — template memakai kalimat umum |
| `DIIZINKAN` | field wajib yang sudah diizinkan Steven lewat `--lanjut-tanpa` |

Ada `BLOKIR` atau `PERINGATAN` → jalankan prosedur **Field kosong** sebelum lanjut ke langkah 3.
Kalau jadi, pastikan keluarannya `Slide: N dari 32` dan `PERIKSA: ... semua teks wajib ada`.

**2b. Naskah percakapan sesuai industri (otomatis, sebelum kirim PDF ke Steven).** Kalau baris
`Naskah` bilang "contoh umum" atau `naskah/<slug>.json` belum ada, tulis `naskah/<slug>.json`
(format & contoh: `naskah/algionet-fiber-by-pt-algio-link-indonesia.json`) dari `industri`,
`masalah_utama`, `kutipan_asli`: 8 gelembung (masuk/keluar bergantian), pertanyaan khas industri
itu. Aturan: balasan MIVA hanya soal PROSES — tanpa harga, stok, ukuran/model tersedia, alamat,
jam buka, atau janji apa pun; nama pelanggan/detail di contoh murni ilustrasi; `_catatan` menyebut
"CONTOH dari Claude <tanggal>". Kalau `pertanyaan_tersering` sudah terisi, pakai itu, jangan
mengarang naskah. Lalu render ulang dan cek `Naskah : naskah/<slug>.json`.

**3. Kirim PDF-nya ke Steven** pakai SendUserFile, dari `deck/keluaran/<slug>.pdf`. Sebutkan
singkat: berapa field brief terisi, field kosong apa saja beserta dampaknya (dari blok `LENGKAP`),
field wajib apa yang diizinkan kosong, dan naskah percakapan slide 9 datang dari mana (barisnya
dicetak generator: `Naskah : ...`).

**4. Revisi kalau diminta.** Yang bisa diubah dan di mana:

| Yang diminta | Ubah di |
|---|---|
| isi brief (nama bisnis, pain point, volume chat, field yang kosong) | kolom REQUESTS — `miva_sheet.tulis_sel("REQUESTS", header, baris, kolom, nilai)`, hanya dengan isi yang sudah disetujui Steven |
| gelembung percakapan slide 9 | tulis tangan di `naskah/<slug>.json` (menang atas `pertanyaan_tersering`) |
| caption WhatsApp | `caption-deck.txt` (`{nama}`, `{nama_bisnis}`) |
| poin custom slide The Scholars / Persada (blok "Yang di-custom") | `template.html` (slide `the-scholars`, `persada-cisoka`) - hanya poin yang Steven sebut |
| urutan/struktur slide | `struktur.lock.json` — hanya kalau Steven memang sengaja mengubah struktur |

Render ulang setelah tiap perubahan, lalu kirim versi barunya ke Steven.

**5. Pratinjau kiriman** (tidak mengirim apa pun):

```
python kirim_deck.py --wa 628xxxxxxxxxx
```

Tampilkan hasilnya ke Steven apa adanya, termasuk blok `LENGKAP`. Skrip menolak jalan kalau PDF
lebih tua dari `update_terakhir` brief, kalau `deck_dikirim_ts` sudah terisi, atau — untuk kiriman
ke klien — kalau ada field wajib kosong yang belum diizinkan (`DIBLOKIR ke klien`).

**6. Kirim.** Hanya setelah Steven menyetujui:

```
python kirim_deck.py --wa 628xxxxxxxxxx --ke-admin --kirim   # ke WA Steven, tidak dicatat ke sheet
python kirim_deck.py --wa 628xxxxxxxxxx --kirim              # ke KLIEN
```

Kalau di langkah 2 Steven sudah mengizinkan field wajib kosong untuk klien ini, kiriman ke klien
butuh `--lanjut-tanpa` yang sama. Yang ke klien otomatis menulis `REQUESTS.deck_dikirim_ts` dan
satu baris EVENTS. Laporkan balasan Kirimi apa adanya — kalau gagal, bilang gagal, jangan diperhalus.

## Field kosong

Dipakai setiap kali blok `LENGKAP` memuat `BLOKIR` atau `PERINGATAN`.

**a. Cari usulan dari fakta yang sudah tertulis.** Sumber yang boleh:
- kolom lain di baris REQUESTS itu — `kutipan_asli`, `catatan`, `pain_points`,
  `alur_setelah_chat`, `pertanyaan_tersering`, `deskripsi_bisnis`, dst.
- baris STATS nomor itu (`miva_sheet.baris_dict("STATS")`) — `nama_bisnis`, `industri`,
  `masalah_utama`, `volume_chat`, dan `Nama` (nama akun WhatsApp).

Setiap usulan menyebut sumbernya. Tidak boleh ada fakta baru: nama usaha yang tidak pernah
tertulis di mana pun **tidak bisa diusulkan** — tanyakan. Nama akun WA boleh diajukan sebagai
kandidat nama usaha, dengan catatan "nama akun WA, belum tentu nama usahanya". Menggabungkan
atau merapikan fakta yang ada boleh (misal `deskripsi_bisnis` dari `industri` + `kutipan_asli`);
menambah detail yang tidak ada (harga, jumlah cabang, lokasi, jenis pelanggan) tidak boleh.

**b. Laporkan ke Steven dalam satu tabel**, lalu berhenti dan tunggu jawabannya:

| Field | Tingkat | Dampak ke deck | Usulan (sumber) | Pertanyaan ke prospek |
|---|---|---|---|---|

Pertanyaan ke prospek diambil dari baris `tanya:` keluaran generator. Kolom usulan diisi
"—" kalau tidak ada fakta yang bisa dipakai.

**c. Tawarkan tiga jalan per field:**
1. **Pakai usulan / Steven sebut isinya** → tulis ke REQUESTS persis seperti yang disetujui
   (revisi Steven menang), lalu render ulang.
2. **Tanya prospek dulu** → Steven yang mengirim pertanyaannya, atau MIVA yang menanyakan di
   percakapan berikutnya. Deck ditunda sampai jawabannya masuk ke REQUESTS.
3. **Lanjut tanpa field itu** → untuk field `BLOKIR` butuh izin eksplisit per field, lalu
   render dengan `--lanjut-tanpa <field>`. Untuk `PERINGATAN` cukup Steven bilang lanjut.

Jangan menulis ke sheet, merender, atau mengirim sebelum ada keputusan untuk setiap field
`BLOKIR`. Kalau deck sudah jadi dengan `PERINGATAN`, PDF-nya tetap boleh dikirim ke Steven untuk
review (langkah 3) bersama tabel ini — dia yang memutuskan dilengkapi dulu atau tidak.

## Konteks yang perlu diingat

- Brief masuk otomatis dari workflow n8n `MIVA Personal — Main`: AI Agent mengeluarkan
  `[DECK_REQUEST]` → `Merge Brief` → `Write REQUESTS` → `Notify Admin Deck` kirim WA ke Steven.
  Isi notif itu masih menyebut cara manual lama (`generate-deck.bat`) — abaikan, pakai alur ini.
- Sejak v3.10 (2026-09-18) MIVA menanyakan nama usaha di pesan perkenalan, jadi `nama_bisnis`
  kosong seharusnya jarang. Kalau tetap kosong, itu tanda prospek belum mau menyebutnya.
- Brief tanpa nama bisnis menghasilkan `tanpa-nama-<4 digit akhir no_wa>.pdf`, bukan lagi
  `tanpa-nama.pdf` bersama.
- Kredensial Kirimi dibaca dari tab CONFIG lewat service account. Jangan pernah mencetak
  nilainya ke chat, log, atau file.
- Sumber kebenaran isi deck: `MIVA for Persada Cisoka Residence.pdf`. Harga, timeline, garansi,
  dan keputusan Steven 2026-08-31 ada di `deck/README.md` — baca kalau menyangkut angka. Tabel
  kelengkapan dan alasannya ada di bagian "Gerbang kelengkapan — 2026-09-18" README yang sama.
- Deck ini dokumen yang sudah dipikirkan, chat itu langsung: deck boleh menyebut add-on
  IDR 999.000/bln, bot tetap tidak boleh menyebut harga add-on.
- Slide The Scholars & Persada memakai label "Latar belakang" dan "Goal" plus blok "Yang di-custom untuk <klien>" (2026-09-29). Semua em dash otomatis diganti "-" oleh `buat_deck.py`; jangan tulis em dash di template/naskah/caption.
- Kirim ulang deck yang deck_dikirim_ts-nya sudah terisi butuh `--ulang`, dan hanya kalau Steven memintanya.
