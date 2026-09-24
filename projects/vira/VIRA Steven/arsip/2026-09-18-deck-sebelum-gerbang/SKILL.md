---
name: deck-request
description: Susun pitch deck VIRA dari brief REQUESTS, kirim ke Steven untuk direview, lalu kirim ke klien lewat WhatsApp setelah Steven approve. Pakai kapan pun Steven menyebut ada permintaan deck atau menyebut nomor WA prospek — trigger pada frasa seperti "ada deck request 628xxx", "generate deck", "bikinin deck buat", "cek request baru", "deck buat <nama bisnis>", "kirim decknya ke klien", "revisi decknya", atau saat dia meneruskan notifikasi WA dari VIRA yang berisi brief prospek. Juga dipakai untuk merevisi deck yang sudah digenerate sebelum dikirim.
---

# Deck Request — generate, review, kirim

Alur "Claude in the loop": Steven tidak lagi menggenerate deck sendiri. Claude yang menyusun,
mengirim PDF-nya ke Steven untuk direview, dan baru mengirim ke klien setelah Steven bilang kirim.

Semua skrip ada di `D:\Documents\Claude Cowork\VIRA\VIRA Steven\deck`. Jalankan dari folder itu.

## Aturan yang tidak boleh dilanggar

1. **Jangan pernah mengirim ke klien tanpa Steven bilang kirim di percakapan ini.** Tampilkan
   dulu pratinjaunya (nomor tujuan, nama klien, berkas, caption persis), tunggu jawabannya.
   Nomor tujuan diambil dari sheet, jangan pernah dikira-kira sendiri.
2. **Angka yang tidak diketahui tidak ditebak.** Field brief kosong → slide yang membutuhkannya
   dibuang oleh generator. Jangan mengarang isi brief supaya slidenya "penuh". Kalau ada field
   penting yang kosong, laporkan ke Steven, jangan diisi sendiri.
3. **Kalau `PERIKSA` gagal atau slide wajib kena aturan pembuangan, hentikan** dan laporkan apa
   adanya. Jangan kirim deck yang halamannya tidak genap 29 atau yang teksnya terpotong.

## Langkah

**1. Lihat briefnya**

```
python cek_request.py --belum
```

Menampilkan tiap baris REQUESTS yang decknya belum dikirim: nama bisnis, jumlah field terisi,
field Tingkat 1 yang masih kosong (`nama_bisnis`, `industri`, `masalah_utama`), dan apakah PDF
lokalnya sudah ada. Kalau Steven sudah menyebut nomornya, langsung ke langkah 2.

**2. Susun decknya**

```
python buat_deck.py --wa 628xxxxxxxxxx --bersih
```

Baca sheet live lewat service account; kalau gagal dia jatuh ke `VIRA Database.xlsx` **dan
mencetak alasannya** — kalau baris `SUMBER` menyebut xlsx, bilang ke Steven, karena datanya
mungkin basi. Pastikan keluarannya `Slide: 29 dari 29` dan `PERIKSA: ... semua teks wajib ada`.

**3. Kirim PDF-nya ke Steven** pakai SendUserFile, dari `deck/keluaran/<slug>.pdf`. Sebutkan
singkat: berapa field brief terisi, field penting apa yang kosong, dan naskah percakapan slide 9
datang dari mana (barisnya dicetak generator: `Naskah : ...`).

**4. Revisi kalau diminta.** Yang bisa diubah dan di mana:

| Yang diminta | Ubah di |
|---|---|
| isi brief (nama bisnis, pain point, volume chat, dll) | kolom REQUESTS — `vira_sheet.tulis_sel("REQUESTS", header, baris, kolom, nilai)` |
| gelembung percakapan slide 9 | tulis tangan di `naskah/<slug>.json` (menang atas `pertanyaan_tersering`) |
| caption WhatsApp | `caption-deck.txt` (`{nama}`, `{nama_bisnis}`) |
| urutan/struktur slide | `struktur.lock.json` — hanya kalau Steven memang sengaja mengubah struktur |

Render ulang setelah tiap perubahan, lalu kirim versi barunya ke Steven.

**5. Pratinjau kiriman** (tidak mengirim apa pun):

```
python kirim_deck.py --wa 628xxxxxxxxxx
```

Tampilkan hasilnya ke Steven apa adanya. Skrip menolak jalan kalau PDF lebih tua dari
`update_terakhir` brief, atau kalau `deck_dikirim_ts` sudah terisi.

**6. Kirim.** Hanya setelah Steven menyetujui:

```
python kirim_deck.py --wa 628xxxxxxxxxx --ke-admin --kirim   # ke WA Steven, tidak dicatat ke sheet
python kirim_deck.py --wa 628xxxxxxxxxx --kirim              # ke KLIEN
```

Yang ke klien otomatis menulis `REQUESTS.deck_dikirim_ts` dan satu baris EVENTS. Laporkan
balasan Kirimi apa adanya — kalau gagal, bilang gagal, jangan diperhalus.

## Konteks yang perlu diingat

- Brief masuk otomatis dari workflow n8n `VIRA Personal — Main`: AI Agent mengeluarkan
  `[DECK_REQUEST]` → `Merge Brief` → `Write REQUESTS` → `Notify Admin Deck` kirim WA ke Steven.
  Isi notif itu masih menyebut cara manual lama (`generate-deck.bat`) — abaikan, pakai alur ini.
- Kredensial Kirimi dibaca dari tab CONFIG lewat service account. Jangan pernah mencetak
  nilainya ke chat, log, atau file.
- Sumber kebenaran isi deck: `VIRA for Persada Cisoka Residence.pdf`. Harga, timeline, garansi,
  dan keputusan Steven 2026-08-31 ada di `deck/README.md` — baca kalau menyangkut angka.
- Deck ini dokumen yang sudah dipikirkan, chat itu langsung: deck boleh menyebut add-on
  IDR 999.000/bln, bot tetap tidak boleh menyebut harga add-on.
